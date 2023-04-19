# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Distributed `BoboCEP` via TCP.
"""

import json
import logging
import socket
import time
from queue import Queue
from threading import Thread, RLock
from typing import Dict, Tuple, Optional, List

from bobocep.bobocep import BoboJSONableError, BoboJSONable
from bobocep.cep.engine.decider.pubsub import BoboDeciderSubscriber, \
    BoboDeciderPublisher
from bobocep.cep.engine.decider.runserial import BoboRunSerial
from bobocep.dist.crypto.crypto import BoboDistributedCrypto
from bobocep.dist.device import BoboDevice
from bobocep.dist.devman import BoboDeviceManager
from bobocep.dist.dist import BoboDistributedJSONDecodeError, \
    BoboDistributed, BoboDistributedError, BoboDistributedSystemError, \
    BoboDistributedTimeoutError
from bobocep.dist.pubsub import BoboDistributedSubscriber, \
    BoboDistributedPublisher

_KEY_COMPLETED = "completed"
_KEY_HALTED = "halted"
_KEY_UPDATED = "updated"

_TYPE_SYNC = 0
_TYPE_PING = 1
_TYPE_RESYNC = 2

_FLAG_RESET = 1

_EXC_CLOSED = "distributed is closed"
_EXC_RUNNING = "distributed is already running"
_EXC_NOT_RUNNING = "distributed is not running"


class _OutgoingJSONEncoder(json.JSONEncoder):
    """
    JSON encoder for outgoing messages.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor for encoding outgoing data into JSON.

        :param args: Arguments.
        :param kwargs: Keyword arguments.
        """
        json.JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, obj: BoboJSONable):
        """
        :param obj: A JSONable object.
        :return: A JSON string.
        """
        try:
            return obj.to_json_str()

        except (KeyError, RecursionError, TypeError, ValueError) as e:
            raise BoboDistributedJSONDecodeError(
                "Failed to encode outgoing data. "
                "Ensure all types are JSONable. "
                "Error: {}".format(e))


class _IncomingJSONDecoder(json.JSONDecoder):
    """
    A JSON decoder for incoming messages.
    """

    def __init__(self):
        """
        Constructor for decoding incoming JSON data.
        """

        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, d: dict) -> Dict[str, List[BoboRunSerial]]:
        """
        :param d: An object dict.
        :return: Incoming Decider update information.
        """

        try:
            if _KEY_COMPLETED in d:
                d[_KEY_COMPLETED] = [
                    BoboRunSerial.from_json_str(rt)
                    for rt in d[_KEY_COMPLETED]]

            if _KEY_HALTED in d:
                d[_KEY_HALTED] = [
                    BoboRunSerial.from_json_str(rt)
                    for rt in d[_KEY_HALTED]]

            if _KEY_UPDATED in d:
                d[_KEY_UPDATED] = [
                    BoboRunSerial.from_json_str(rt)
                    for rt in d[_KEY_UPDATED]]

            return d

        except (KeyError, RecursionError, TypeError, ValueError) as e:
            # json.JSONDecodeError is a subclass of ValueError
            raise BoboDistributedJSONDecodeError(
                "Failed to decode incoming data. "
                "Ensure all types are JSONable."
                "Error: {}".format(e))


class BoboDistributedTCP(BoboDistributed,
                         BoboDistributedPublisher,
                         BoboDeciderSubscriber):
    """
    An implementation of distributed BoboCEP that uses TCP for data
    transmission across the network.
    """

    def __init__(self,
                 urn: str,
                 decider: BoboDeciderPublisher,
                 devices: List[BoboDevice],
                 crypto: BoboDistributedCrypto,
                 max_size_incoming: int = 0,
                 max_size_outgoing: int = 0,
                 period_ping: int = 30,
                 period_resync: int = 60,
                 attempt_stash: int = 5,
                 attempt_ping: int = 5,
                 attempt_resync: int = 10,
                 max_listen: int = 3,
                 timeout_accept: int = 3,
                 timeout_connect: int = 3,
                 timeout_send: int = 3,
                 timeout_receive: int = 3,
                 recv_bytes: int = 2048,
                 flag_reset: bool = True):
        """
        :param urn: A URN that is unique across devices in the network.
        :param decider: The Decider used in the local engine.
        :param devices: Devices in the network (including this device).
        :param crypto: Encryption to use for message exchange.
        :param max_size_incoming: Max queue size for incoming data.
            Default: 0 (unbounded).
        :param max_size_outgoing: Max queue size for outgoing data.
            Default: 0 (unbounded).
        :param period_ping: Period of inactivity from another device
            to warrant pinging the device, in seconds.
            Default: 30.
        :param period_resync: Period of inactivity from another device
            to warrant resyncing with the device, in seconds.
            Default: 60.
        :param attempt_stash: How frequently to attempt to send the sync stash
            if the stash is not empty.
        :param attempt_ping: How frequently to ping another device
            if it is within the ping period, in seconds.
            Default: 10.
        :param attempt_resync: How frequently to resync with another device
            if it is within the resync period, in seconds.
            Default: 10.
        :param max_listen: Max number of incoming connections to listen for
            at a given time, in seconds.
            Default: 3.
        :param timeout_accept: Timeout for accepting a new incoming
            connection, in seconds.
            Default: 3.
        :param timeout_connect: Timeout for connecting to a client
            when sending data, in seconds.
            Default: 3.
        :param timeout_send: Timeout for sending data, in seconds.
            Default: 3.
        :param timeout_receive: Timeout for receiving data, in seconds.
            Default: 3.
        :param recv_bytes: Number of bytes to receive at a time when receiving
            data.
            Default: 2048.
        :param flag_reset: If `True`, the RESET flag is set to indicate to
            external devices that it should reset its data on this device,
            which will trigger a resync.
        """
        super().__init__()

        # Lock used for local updates to and from the decider
        self._lock_local: RLock = RLock()
        # Lock used when sending and receiving remote messages
        self._lock_in_out: RLock = RLock()

        self._closed: bool = False
        self._running: bool = False
        self._thread_closed: bool = False
        self._subscribers: List[BoboDistributedSubscriber] = []

        self._urn: str = urn
        self._decider: BoboDeciderPublisher = decider
        self._devices: Dict[str, BoboDeviceManager] = {}
        self._crypto: BoboDistributedCrypto = crypto

        self._period_ping: int = period_ping
        self._period_resync: int = period_resync
        self._attempt_stash: int = attempt_stash
        self._attempt_ping: int = attempt_ping
        self._attempt_resync: int = attempt_resync

        # Check devices for duplicate URNs
        for d in devices:
            if d.urn in self._devices:
                raise BoboDistributedError(
                    "Duplicate device URN: {}".format(d.urn))

            self._devices[d.urn] = BoboDeviceManager(
                device=d,
                flag_reset=flag_reset)

        # Ensure at least two devices are listed, one of which is this device
        if (len(self._devices.keys()) < 2) or (urn not in self._devices):
            raise BoboDistributedError(
                "Devices list must contain at least 2 devices, one of which"
                " is this device ({}), found: {}"
                .format(urn, list(self._devices.keys())))

        self._max_listen: int = max_listen
        self._timeout_accept: int = timeout_accept
        self._timeout_connect: int = timeout_connect
        self._timeout_send: int = timeout_send
        self._timeout_receive: int = timeout_receive
        self._recv_bytes: int = recv_bytes

        self._thread_incoming: Thread = Thread(target=self._tcp_incoming)
        self._thread_outgoing: Thread = Thread(target=self._tcp_outgoing)

        self._queue_incoming: Queue[Dict[str, List[BoboRunSerial]]] = \
            Queue(maxsize=max_size_incoming)
        self._queue_outgoing: Queue[Dict[str, List[BoboRunSerial]]] = \
            Queue(maxsize=max_size_outgoing)

    def run(self) -> None:
        """
        Runs the distributed instance.
        """
        with self._lock_local:
            if self._closed:
                raise BoboDistributedError(_EXC_CLOSED)

            if self._running:
                raise BoboDistributedError(_EXC_RUNNING)

            self._thread_incoming.start()
            self._thread_outgoing.start()

            self._running = True

        while True:
            with self._lock_local:
                if self._closed:
                    self._running = False
                    break
                self._update()

    def subscribe(self, subscriber: BoboDistributedSubscriber) -> None:
        """
        :param subscriber: Subscriber to the distributed instance.
        """
        with self._lock_local:
            if subscriber not in self._subscribers:
                self._subscribers.append(subscriber)

    def _update(self) -> None:
        """
        Processes data in the incoming queue and passes them to subscribers.
        """
        # Take incoming data and pass to decider
        while not self._queue_incoming.empty():
            incoming: Dict[str, List[BoboRunSerial]] = \
                self._queue_incoming.get_nowait()

            completed: List[BoboRunSerial] = incoming[_KEY_COMPLETED]
            halted: List[BoboRunSerial] = incoming[_KEY_HALTED]
            updated: List[BoboRunSerial] = incoming[_KEY_UPDATED]

            logging.debug("{} Sending incoming queue data to subscribers"
                          .format(self._urn))

            if (
                    len(completed) > 0 or
                    len(halted) > 0 or
                    len(updated) > 0
            ):
                for subscriber in self._subscribers:
                    subscriber.on_distributed_update(
                        completed=completed,
                        halted=halted,
                        updated=updated)

    def on_decider_update(
            self,
            completed: List[BoboRunSerial],
            halted: List[BoboRunSerial],
            updated: List[BoboRunSerial],
            local: bool
    ) -> None:
        """
        :param completed: Locally completed runs.
        :param halted: Locally halted runs.
        :param updated: Locally updated runs.
        :param local: `True` if the Decider update occurred locally;
            `False` if the update occurred on a remote (distributed) instance.
        """
        with self._lock_local:
            if self._closed:
                raise BoboDistributedError(_EXC_CLOSED)

            if not self._running:
                raise BoboDistributedError(_EXC_NOT_RUNNING)

            # Prevents Decider from passing distributed data back
            if not local:
                return

            logging.debug("{} Adding local Decider changes "
                          "to outgoing queue".format(self._urn))

            # Take changes to decider and pass to outgoing

            outgoing: Dict[str, List[BoboRunSerial]] = {
                _KEY_COMPLETED: completed,
                _KEY_HALTED: halted,
                _KEY_UPDATED: updated
            }

            if not self._queue_outgoing.full():
                self._queue_outgoing.put_nowait(outgoing)

            else:
                errmsg = "Outgoing queue is full."
                logging.critical(errmsg)
                raise BoboDistributedSystemError(errmsg)

    @staticmethod
    def _now() -> int:
        """
        :return: The current time in seconds since epoch.
        """
        return int(time.time())

    def _tcp_outgoing(self):
        """
        Executed within a thread. It sends internal Decider state updates,
        stored in the outgoing queue, to external `BoboCEP` instances.
        """

        while True:
            with self._lock_in_out:
                # Thread has been marked to close
                if self._thread_closed:
                    return

                outlist: List[Tuple[BoboDeviceManager, int]] = []
                now: int = self._now()

                # Determine what to send to each device...
                for d in self._devices.values():
                    # Ignore self...
                    if d.urn == self._urn:
                        continue

                    comms_range: int = (now - d.last_comms)
                    attempt_range: int = (now - d.last_attempt)
                    queue_empty: bool = self._queue_outgoing.empty()

                    # If device is within the "RESYNC Period"...
                    if comms_range >= self._period_resync:
                        # ...and due to attempt another RESYNC...
                        if attempt_range >= self._attempt_resync:
                            outlist.append((d, _TYPE_RESYNC))

                    # If device is within the "PING Period"
                    # and there is nothing to SYNC...
                    elif comms_range >= self._period_ping and (
                            queue_empty and
                            d.size_stash() == 0
                    ):
                        # ...and due to attempt another PING...
                        if attempt_range >= self._attempt_ping:
                            outlist.append((d, _TYPE_PING))

                    # If device is within the "SYNC Period"
                    # or "PING Period" with something left to SYNC...
                    else:
                        # ...and there is data in the queue or
                        # data in the device's stash that is due to send...
                        if (not queue_empty) or (
                                d.size_stash() > 0 and
                                attempt_range >= self._attempt_stash
                        ):
                            outlist.append((d, _TYPE_SYNC))

            # Compiled SYNC data for sending to all devices
            cache_sync: Optional[Dict[str, List[BoboRunSerial]]] = None

            for d, msg_type in outlist:
                # Set flags
                msg_flags: int = 0

                if d.flag_reset:
                    msg_flags += _FLAG_RESET

                if msg_type == _TYPE_RESYNC:
                    # Stash contents not needed when in RESYNC Period
                    d.clear_stash()

                    # Collect and cache a snapshot of Decider
                    snapshot = self._decider.snapshot()
                    msg_json_resync = self._outgoing_to_json({
                        _KEY_COMPLETED: snapshot[0],
                        _KEY_HALTED: snapshot[1],
                        _KEY_UPDATED: snapshot[2]
                    })

                    # Send snapshot to remote
                    err: int = self._tcp_send(
                        d, msg_type, msg_flags, msg_json_resync)

                    # Update last comms on success
                    now = self._now()

                    if err == 0:
                        logging.debug("{} Resync SUCCESS: {}"
                                      .format(self._urn, d.urn))
                        d.last_comms = now

                        if (msg_flags & _FLAG_RESET) == _FLAG_RESET:
                            d.flag_reset = False

                    else:
                        logging.error(
                            "{} Resync FAILURE: {} (code {})"
                            .format(self._urn, d.urn, err))

                    d.last_attempt = now

                elif msg_type == _TYPE_PING:
                    # Send ping
                    err: int = self._tcp_send(d, msg_type, msg_flags, "{}")

                    # Update last comms on success
                    now = self._now()

                    if err == 0:
                        logging.debug("{} Ping SUCCESS: {}"
                                      .format(self._urn, d.urn))
                        d.last_comms = now

                        if (msg_flags & _FLAG_RESET) == _FLAG_RESET:
                            d.flag_reset = False

                    else:
                        logging.error(
                            "{} Ping FAILURE: {} (code {})"
                            .format(self._urn, d.urn, err))

                    d.last_attempt = now

                elif msg_type == _TYPE_SYNC:
                    # Get SYNC data to send (cached for all devices to use)
                    if cache_sync is None:
                        if not self._queue_outgoing.empty():
                            cache_sync = self._queue_outgoing.get_nowait()
                        else:
                            cache_sync = {
                                _KEY_COMPLETED: [],
                                _KEY_HALTED: [],
                                _KEY_UPDATED: []
                            }

                    # Get device's stash of unsent data
                    stash_c, stash_h, stash_u = d.stash()

                    # Add stash to new data to send
                    send_sync: Dict[str, List[BoboRunSerial]] = {
                        _KEY_COMPLETED:
                            cache_sync[_KEY_COMPLETED] + stash_c,
                        _KEY_HALTED:
                            cache_sync[_KEY_HALTED] + stash_h,
                        _KEY_UPDATED:
                            cache_sync[_KEY_UPDATED] + stash_u
                    }

                    # Send JSON sync
                    msg_json_sync: str = self._outgoing_to_json(send_sync)
                    err: int = self._tcp_send(
                        d, msg_type, msg_flags, msg_json_sync)

                    now = self._now()
                    if err == 0:
                        logging.debug("{} Sync SUCCESS: {}"
                                      .format(self._urn, d.urn))

                        # Update last comms on success and clear stash
                        d.clear_stash()
                        d.last_comms = now

                        if (msg_flags & _FLAG_RESET) == _FLAG_RESET:
                            d.flag_reset = False
                    else:
                        logging.error("{} Sync FAILURE: {} (code {})"
                                      .format(self._urn, d.urn, err))

                        # Append stash with cache_sync on error
                        d.append_stash(
                            completed=cache_sync[_KEY_COMPLETED],
                            halted=cache_sync[_KEY_HALTED],
                            updated=cache_sync[_KEY_UPDATED])

                    d.last_attempt = now

    def _tcp_send(self, d: BoboDeviceManager, msg_type: int,
                  msg_flags: int, msg_str: str) -> int:
        """
        Sends data via TCP.

        :param d: The device to send data to.
        :param msg_type: Message type.
        :param msg_flags: Message flags.
        :param msg_str: The data to send.
        :return: 0 for success; 1 for timeout error; 2 for system error.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            logging.debug("{} Sending to: {} ({}:{})"
                          .format(self._urn, d.urn, d.addr, d.port))

            s.settimeout(self._timeout_connect)
            s.connect((d.addr, d.port))
            s.settimeout(None)

            mydev = self._devices[self._urn]

            msg_str = "{} {} {} {} {}".format(
                mydev.urn,
                mydev.id_key,
                msg_type,
                msg_flags,
                msg_str)

            msg_bytes = self._crypto.encrypt(msg_str)

            s.settimeout(self._timeout_send)
            s.sendall(msg_bytes)
            s.settimeout(None)

            return 0

        except TimeoutError:
            # Raised when a system function timed out at the system level.
            return 1

        except OSError:
            # Raised when a system function returns a system-related error.
            return 2

        finally:
            s.close()

    def _tcp_incoming(self) -> None:
        """
        Executed within a thread. It accepts outside connections and stores
        their data in the incoming queue, if valid.
        """

        mydev = self._devices[self._urn]

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((mydev.addr, mydev.port))

        # queue requests before refusing outside connections
        s.listen(self._max_listen)

        try:
            while True:
                with self._lock_in_out:
                    if self._thread_closed:
                        return

                try:
                    s.settimeout(self._timeout_accept)

                    client_s, client_origin = s.accept()
                    client_addr = client_origin[0]
                    client_port = client_origin[1]

                    s.settimeout(None)
                    client_accepted = int(time.time())

                    logging.debug("{} Incoming client: {}:{}"
                                  .format(self._urn, client_addr, client_port))

                    self._tcp_incoming_handle_client(
                        client_s, client_addr, client_accepted)

                except (BoboDistributedSystemError,
                        BoboDistributedTimeoutError) as e:
                    # From _tcp_incoming_handle_client
                    logging.error("{} {}: {}"
                                  .format(self._urn, e.__class__.__name__, e))

                except socket.timeout:
                    # From s.accept()
                    # Timeout is added here so that the thread can react to
                    # _thread_closed=True when no data received for a while
                    pass

                except Exception as e:
                    # From other
                    logging.error("{} {}: {}"
                                  .format(self._urn, e.__class__.__name__, e))
        finally:
            s.close()

    def _tcp_incoming_handle_client(
            self, client_s, client_addr, client_accepted: int) -> None:
        """
        Handles an incoming client request.
        :param client_s: The client socket.
        :param client_addr: The client address.
        :param client_accepted: The time when the client request was accepted.
        """
        try:
            all_bytes = bytearray()

            while True:
                now = int(time.time())
                elapse = (now - client_accepted)

                if elapse >= self._timeout_receive:
                    raise BoboDistributedTimeoutError(
                        "Message timeout ({} seconds)"
                        .format(elapse))

                bytes_msg = client_s.recv(self._recv_bytes)
                all_bytes.extend(bytes_msg)

                # If bytes received so far are at least the minimum length
                # and end with the expected end bytes.
                if (
                        len(bytes_msg) >= self._crypto.min_length() and
                        bytes_msg[-len(self._crypto.end_bytes()):]
                        == self._crypto.end_bytes()
                ):

                    try:
                        plaintext = self._crypto.decrypt(all_bytes)
                    except ValueError as e:
                        raise BoboDistributedSystemError(
                            "Failed to unwrap incoming message (bytes: {})"
                            .format(e))

                    pt_urn, pt_id, pt_type, pt_flags, pt_json = \
                        self._split_plaintext(plaintext)

                    logging.debug(
                        "{} Incoming: urn={}, type={}, flags={}"
                        .format(self._urn, pt_urn, pt_type, pt_flags))

                    # Check if URN is NOT a recognised device
                    if pt_urn not in self._devices:
                        raise BoboDistributedSystemError(
                            "Unknown device URN '{}'.".format(pt_urn))

                    device: BoboDeviceManager = self._devices[pt_urn]

                    # Check if ID key DOES NOT MATCH expected key for URN
                    if pt_id != device.id_key:
                        raise BoboDistributedSystemError(
                            "Invalid ID key for URN '{}'".format(device.urn))

                    # Update address if remote address has changed
                    if client_addr != device.addr:
                        logging.debug(
                            "{} Device {} addr update: from '{}' to '{}'"
                            .format(self._urn,
                                    device.urn, device.addr, client_addr))
                        device.addr = client_addr

                    if pt_type == _TYPE_SYNC or pt_type == _TYPE_RESYNC:
                        incoming = self._incoming_from_json(pt_json)

                        logging.debug("{} Data from {}: {}"
                                      .format(self._urn, pt_urn, incoming))

                        # Add incoming data to queue
                        if not self._queue_incoming.full():
                            self._queue_incoming.put_nowait(incoming)
                        else:
                            errmsg = "Incoming queue is full."
                            logging.critical(errmsg)
                            raise BoboDistributedSystemError(errmsg)

                    # (Nothing to do on PING; it exists for outgoing.)
                    if pt_type == _TYPE_PING:
                        logging.debug("{} Pinged by: {}"
                                      .format(self._urn, pt_urn))

                    if (pt_flags & _FLAG_RESET) == _FLAG_RESET:
                        # Clears comms for device to trigger RESYNC
                        logging.debug("{} Reset for: {}"
                                      .format(self._urn, pt_urn))
                        device.clear_last()

                    break
        finally:
            client_s.close()

    def _split_plaintext(self, plaintext: str) \
            -> Tuple[str, str, int, int, str]:
        """
        :param plaintext: The string to split.
        :return: Tuple containing: URN, ID, type, flags, and JSON message.
        """
        ix_delim = []

        for i, c in enumerate(plaintext):
            if c == ' ':
                ix_delim.append(i)

            if len(ix_delim) == 4:
                break

        if len(ix_delim) != 4:
            raise BoboDistributedError(
                "Invalid plaintext message: {}".format(plaintext))

        # pt_urn, pt_id,, pt_type, pt_flags, pt_json
        return (
            plaintext[:ix_delim[0]],
            plaintext[ix_delim[0] + 1:ix_delim[1]],
            int(plaintext[ix_delim[1] + 1:ix_delim[2]]),
            int(plaintext[ix_delim[2] + 1:ix_delim[3]]),
            plaintext[ix_delim[3] + 1:]
        )

    def _incoming_from_json(
            self, msg_str: str) -> Dict[str, List[BoboRunSerial]]:
        """
        :param msg_str: Incoming JSON string.
        :return: Incoming Decider update information.
        """
        try:
            return json.loads(msg_str, cls=_IncomingJSONDecoder)

        except (BoboJSONableError, TypeError) as e:
            raise BoboDistributedSystemError(
                "Failed to parse incoming JSON: {}".format(e))

    def _outgoing_to_json(
            self, msg: Dict[str, List[BoboRunSerial]]) -> str:
        """
        :param msg: Outgoing Decider update information.
        :return: Outgoing JSON string.
        """
        try:
            return json.dumps(msg, cls=_OutgoingJSONEncoder)

        except (BoboJSONableError, TypeError) as e:
            raise BoboDistributedSystemError(
                "Failed to generate outgoing JSON: {}".format(e))

    def join(self) -> None:
        """
        Joins with the incoming and outgoing threads.
        """
        with self._lock_local:
            self._thread_incoming.join()
            self._thread_outgoing.join()

    def close(self) -> None:
        """
        Closes the distributed instance.
        """
        with self._lock_local:
            if self._closed:
                return

            try:
                logging.debug("{} Close distributed".format(self._urn))

                with self._lock_in_out:
                    self._thread_closed = True

            finally:
                self._closed = True

    def is_closed(self) -> bool:
        """
        :return: `True` if distributed is closed; `False` otherwise.
        """
        with self._lock_local:
            return self._closed

    def size_incoming(self) -> int:
        """
        :return: Size of incoming queue.
        """
        with self._lock_local:
            return self._queue_incoming.qsize()

    def size_outgoing(self) -> int:
        """
        :return: Size of outgoing queue
        """
        with self._lock_local:
            return self._queue_outgoing.qsize()
