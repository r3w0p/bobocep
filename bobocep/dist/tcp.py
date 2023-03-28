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

from bobocep.cep.engine.decider.decider import BoboDecider, BoboRunTuple
from bobocep.cep.engine.decider.pubsub import BoboDeciderSubscriber
from bobocep.cep.json import BoboJSONableError, BoboJSONable
from bobocep.dist.crypto.crypto import BoboDistributedCrypto
from bobocep.dist.device import BoboDevice, BoboDeviceManager
from bobocep.dist.dist import BoboDistributed, BoboDistributedError, \
    BoboDistributedSystemError, BoboDistributedTimeoutError
from bobocep.dist.pubsub import BoboDistributedSubscriber

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
        json.JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, obj: BoboJSONable):
        """
        :param obj: A JSONable object.
        :return: A JSON string.
        """
        return obj.to_json_str()


class _IncomingJSONDecoder(json.JSONDecoder):
    """
    A JSON decoder for incoming messages.
    """

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, d: dict) -> Dict[str, List[BoboRunTuple]]:
        """
        :param d: An object dict.
        :return: Incoming Decider update information.
        """
        if _KEY_COMPLETED in d:
            d[_KEY_COMPLETED] = [
                BoboRunTuple.from_json_str(rt)
                for rt in d[_KEY_COMPLETED]]

        if _KEY_HALTED in d:
            d[_KEY_HALTED] = [
                BoboRunTuple.from_json_str(rt)
                for rt in d[_KEY_HALTED]]

        if _KEY_UPDATED in d:
            d[_KEY_UPDATED] = [
                BoboRunTuple.from_json_str(rt)
                for rt in d[_KEY_UPDATED]]

        return d


class BoboDistributedTCP(BoboDistributed, BoboDeciderSubscriber):
    """
    An implementation of distributed BoboCEP that uses TCP for data
    transmission across the network.
    """

    def __init__(self,
                 urn: str,
                 decider: BoboDecider,
                 devices: List[BoboDevice],
                 crypto: BoboDistributedCrypto,
                 max_size_incoming: int = 0,
                 max_size_outgoing: int = 0,
                 period_ping: int = 30,
                 period_resync: int = 60,
                 attempt_ping: int = 10,
                 attempt_resync: int = 10,
                 max_listen: int = 3,
                 timeout_accept: int = 3,
                 timeout_connect: int = 3,
                 timeout_send: int = 3,
                 timeout_receive: int = 3,
                 recv_bytes: int = 2048,
                 subscribe: bool = True,
                 flag_reset: bool = True):
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
        self._decider: BoboDecider = decider
        self._devices: Dict[str, BoboDeviceManager] = {}
        self._crypto: BoboDistributedCrypto = crypto

        self._period_ping: int = period_ping
        self._period_resync: int = period_resync
        self._attempt_ping: int = attempt_ping
        self._attempt_resync: int = attempt_resync

        # Subscribe distributed and decider to each other
        if subscribe:
            self.subscribe(self._decider)
            self._decider.subscribe(self)

        # Check devices for duplicate URNs
        for d in devices:
            if d.urn in self._devices:
                raise BoboDistributedError(
                    "Duplicate device URN: {}".format(d.urn))

            self._devices[d.urn] = BoboDeviceManager(
                device=d,
                flag_reset=flag_reset)

        # Ensure at least one device is listed
        # Ensure that, if only one device is listed, it is itself
        if (
                len(self._devices.keys()) == 0 or
                (len(self._devices.keys()) == 1 and urn in self._devices)
        ):
            raise BoboDistributedError(
                "Devices must provide at least one other device")

        # Check that itself is in the device list
        if urn not in self._devices:
            raise BoboDistributedError(
                "URN not found in devices: {}".format(urn))

        self._max_listen: int = max_listen
        self._timeout_accept: int = timeout_accept
        self._timeout_connect: int = timeout_connect
        self._timeout_send: int = timeout_send
        self._timeout_receive: int = timeout_receive
        self._recv_bytes: int = recv_bytes

        self._thread_incoming: Thread = Thread(target=self._tcp_incoming)
        self._thread_outgoing: Thread = Thread(target=self._tcp_outgoing)

        self._queue_incoming: Queue[Dict[str, List[BoboRunTuple]]] = \
            Queue(maxsize=max_size_incoming)
        self._queue_outgoing: Queue[Dict[str, List[BoboRunTuple]]] = \
            Queue(maxsize=max_size_outgoing)

    def run(self) -> None:
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

    def subscribe(self, subscriber: BoboDistributedSubscriber):
        with self._lock_local:
            if subscriber not in self._subscribers:
                self._subscribers.append(subscriber)

    def _update(self):
        # Take incoming data and pass to decider
        while not self._queue_incoming.empty():
            logging.debug("{} _update fetching data from incoming queue"
                          .format(self._urn))

            incoming: Dict[str, List[BoboRunTuple]] = \
                self._queue_incoming.get_nowait()

            completed: List[BoboRunTuple] = incoming[_KEY_COMPLETED]
            halted: List[BoboRunTuple] = incoming[_KEY_HALTED]
            updated: List[BoboRunTuple] = incoming[_KEY_UPDATED]

            logging.debug("{} _update sending data to subscribers"
                          .format(self._urn))

            for subscriber in self._subscribers:
                subscriber.on_distributed_update(
                    completed=completed,
                    halted=halted,
                    updated=updated)

    def on_decider_update(
            self,
            completed: List[BoboRunTuple],
            halted: List[BoboRunTuple],
            updated: List[BoboRunTuple]):
        with self._lock_local:
            if self._closed:
                raise BoboDistributedError(_EXC_CLOSED)

            if not self._running:
                raise BoboDistributedError(_EXC_NOT_RUNNING)

            logging.debug("{} on_decider_update adding local Decider changes "
                          "to outgoing queue".format(self._urn))

            # Take changes to decider and pass to outgoing

            outgoing: Dict[str, List[BoboRunTuple]] = {
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

                    # If device is within the "Resync Period"...
                    if (now - d.last_comms) >= self._period_resync:
                        # ...and due to attempt another resync...
                        if (now - d.last_attempt) > self._attempt_resync:
                            outlist.append((d, _TYPE_RESYNC))

                    # If device is within the "Ping Period"
                    # and there is otherwise nothing to sync...
                    elif (
                            (now - d.last_comms) >= self._period_ping and
                            self._queue_outgoing.empty()
                    ):
                        # ...and due to attempt another ping...
                        if (now - d.last_attempt) > self._attempt_ping:
                            outlist.append((d, _TYPE_PING))

                    # If device is within the "OK Period"...
                    else:
                        # ...and there is something to sync...
                        if not self._queue_outgoing.empty():
                            outlist.append((d, _TYPE_SYNC))

            # Used to share data across multiple devices
            cache_resync_str: Optional[str] = None
            cache_sync_dict: Optional[Dict[str, List[BoboRunTuple]]] = None

            for d, msg_type in outlist:
                # Set flags
                msg_flags: int = 0

                if d.flag_reset:
                    msg_flags += _FLAG_RESET

                if msg_type == _TYPE_RESYNC:
                    # Stash contents not needed when sending resync
                    d.clear_stash()

                    # Collect and cache a snapshot of decider
                    if cache_resync_str is None:
                        snapshot = self._decider.snapshot()
                        cache_resync_str = self._outgoing_to_json({
                            _KEY_COMPLETED: snapshot[0],
                            _KEY_HALTED: snapshot[1],
                            _KEY_UPDATED: snapshot[2]
                        })

                    # Send snapshot to remote
                    err: int = self._tcp_send(
                        d, msg_type, msg_flags, cache_resync_str)

                    # Update last comms on success
                    now = self._now()

                    if err == 0:
                        logging.debug("{} _tcp_outgoing resync success with {}"
                                      .format(self._urn, d.urn))
                        d.last_comms = now

                        if (msg_flags & _FLAG_RESET) == _FLAG_RESET:
                            d.flag_reset = False

                    else:
                        logging.error(
                            "{} _tcp_outgoing resync FAILURE with {} (code {})"
                            .format(self._urn, d.urn, err))

                    d.last_attempt = now

                elif msg_type == _TYPE_PING:
                    # Send ping
                    err: int = self._tcp_send(d, msg_type, msg_flags, "{}")

                    # Update last comms on success
                    now = self._now()

                    if err == 0:
                        logging.debug("{} _tcp_outgoing ping success with {}"
                                      .format(self._urn, d.urn))
                        d.last_comms = now

                        if (msg_flags & _FLAG_RESET) == _FLAG_RESET:
                            d.flag_reset = False

                    else:
                        logging.error(
                            "{} _tcp_outgoing ping FAILURE with {} (code {})"
                            .format(self._urn, d.urn, err))

                    d.last_attempt = now

                elif msg_type == _TYPE_SYNC:
                    # Get data from queue
                    if cache_sync_dict is None:
                        cache_sync_dict = self._queue_outgoing.get_nowait()

                    # Get device's stash of unsent data
                    stash_c, stash_h, stash_u = d.stash()

                    # Add stash to new data to send
                    send_sync: Dict[str, List[BoboRunTuple]] = {
                        _KEY_COMPLETED:
                            cache_sync_dict[_KEY_COMPLETED] + stash_c,
                        _KEY_HALTED:
                            cache_sync_dict[_KEY_HALTED] + stash_h,
                        _KEY_UPDATED:
                            cache_sync_dict[_KEY_UPDATED] + stash_u
                    }

                    # Send JSON sync
                    msg_json_sync: str = self._outgoing_to_json(send_sync)
                    err: int = self._tcp_send(
                        d, msg_type, msg_flags, msg_json_sync)

                    now = self._now()
                    if err == 0:
                        logging.debug("{} _tcp_outgoing sync success with {}"
                                      .format(self._urn, d.urn))

                        # Update last comms on success and clear stash
                        d.clear_stash()
                        d.last_comms = now

                        if (msg_flags & _FLAG_RESET) == _FLAG_RESET:
                            d.flag_reset = False
                    else:
                        logging.error(
                            "{} _tcp_outgoing sync FAILURE with {} (code {})"
                            .format(self._urn, d.urn, err))

                        # Append stash with cache_sync on error
                        d.append_stash(
                            completed=cache_sync_dict[_KEY_COMPLETED],
                            halted=cache_sync_dict[_KEY_HALTED],
                            updated=cache_sync_dict[_KEY_UPDATED])

                    d.last_attempt = now

    def _tcp_send(self, d: BoboDeviceManager, msg_type: int,
                  msg_flags: int, msg_str: str) -> int:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            logging.debug("{} _tcp_send sending to {} at {}:{}"
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

                    logging.debug("{} _tcp_incoming incoming client: {}:{}"
                                  .format(self._urn, client_addr, client_port))

                    self._tcp_incoming_handle_client(
                        client_s, client_addr, client_accepted)

                except (BoboDistributedSystemError,
                        BoboDistributedTimeoutError) as e:
                    # From _tcp_incoming_handle_client
                    logging.error("{} _tcp_incoming {}: {}"
                                  .format(self._urn, e.__class__.__name__, e))

                except socket.timeout:
                    # From s.accept()
                    # Timeout is added here so that the thread can react to
                    # _thread_closed=True when no data received for a while
                    logging.debug("{} _tcp_incoming socket timeout (ignoring)"
                                  .format(self._urn))

                except Exception as e:
                    # From other
                    logging.error("{} _tcp_incoming {}: {}"
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
                        "message timeout ({} seconds)"
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
                        raise BoboDistributedTimeoutError(
                            "Failed to unwrap incoming message bytes: {}"
                            .format(e))

                    pt_urn, pt_id, pt_type, pt_flags, pt_json = \
                        self._split_plaintext(plaintext)

                    logging.debug(
                        "{} _tcp_incoming_handle_client plaintext: {}"
                        .format(self._urn, pt_urn))

                    # Check if URN is a recognised device
                    if pt_urn not in self._devices:
                        raise BoboDistributedSystemError(
                            "Unknown device URN '{}'.".format(pt_urn))

                    device: BoboDeviceManager = self._devices[pt_urn]

                    # Check if ID key matches expected key for URN
                    if pt_id != device.id_key:
                        raise BoboDistributedSystemError(
                            "Invalid ID key for URN '{}'".format(device.urn))

                    # Update address if remote address has changed
                    if client_addr != device.addr:
                        logging.debug(
                            "{} _tcp_incoming_handle_client device {} "
                            "address update: from '{}' to '{}'"
                            .format(self._urn,
                                    device.urn, device.addr, client_addr))
                        device.addr = client_addr

                    if pt_type == _TYPE_SYNC or _TYPE_RESYNC:
                        incoming = self._incoming_from_json(pt_json)

                        # Add incoming data to queue
                        if not self._queue_incoming.full():
                            self._queue_incoming.put_nowait(incoming)
                        else:
                            errmsg = "Incoming queue is full."
                            logging.critical(errmsg)
                            raise BoboDistributedSystemError(errmsg)

                    # (Nothing to do on PING; it exists for outgoing.)

                    if (pt_flags & _FLAG_RESET) == _FLAG_RESET:
                        # Resets comms for device to trigger RESYNC
                        device.reset_last()

                    break
        finally:
            client_s.close()

    def _split_plaintext(self, plaintext: str) \
            -> Tuple[str, str, int, int, str]:
        """
        :param plaintext: The string to split.
        :return: Tuple containing: URN, ID, type, flags, and JSON message
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
            self, msg_str: str) -> Dict[str, List[BoboRunTuple]]:
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
            self, msg: Dict[str, List[BoboRunTuple]]) -> str:
        """
        :param msg: Outgoing Decider update information.
        :return: Outgoing JSON string.
        """
        try:
            return json.dumps(msg, cls=_OutgoingJSONEncoder)

        except (BoboJSONableError, TypeError) as e:
            raise BoboDistributedSystemError(
                "Failed to generate outgoing JSON: {}".format(e))

    def join(self):
        with self._lock_local:
            self._thread_incoming.join()
            self._thread_outgoing.join()

    def close(self):
        with self._lock_local:
            if self._closed:
                raise BoboDistributedError(_EXC_CLOSED)

            logging.debug("{} close distributed".format(self._urn))
            self._closed = True

            with self._lock_in_out:
                self._thread_closed = True

    def is_closed(self) -> bool:
        with self._lock_local:
            return self._closed

    def size_incoming(self) -> int:
        with self._lock_local:
            return self._queue_incoming.qsize()

    def size_outgoing(self) -> int:
        with self._lock_local:
            return self._queue_outgoing.qsize()
