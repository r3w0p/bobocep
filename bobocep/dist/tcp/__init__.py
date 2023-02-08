# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
Distributed complex event processing via TCP.
"""

import json
import logging
import socket
import time
from queue import Queue
from threading import Thread, RLock
from typing import List, Dict, Tuple

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from bobocep.cep import BoboJSONableError, BoboJSONable
from bobocep.cep.engine.task.decider import BoboRunTuple
from bobocep.cep.engine.task.decider.pubsub import BoboDeciderSubscriber
from bobocep.dist import BoboDistributed, BoboDeviceTuple, \
    BoboDistributedError, BoboDistributedSystemError, \
    BoboDistributedTimeoutError

_KEY_COMPLETED = "completed"
_KEY_HALTED = "halted"
_KEY_UPDATED = "updated"


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
    Data are encrypted using AES-128, 192, or 256 encryption.
    """

    _EXC_CLOSED = "distributed is closed"
    _EXC_RUNNING = "distributed is already running"
    _EXC_NOT_RUNNING = "distributed is not running"

    _UTF_8 = "UTF-8"
    _PAD_MODULO = 16
    _START_STR = "BOBO"
    _END_BYTES = "BOBO".encode(_UTF_8)
    _LEN_END_BYTES = len(_END_BYTES)

    _BYTES_AES_128 = 16
    _BYTES_AES_192 = 24
    _BYTES_AES_256 = 32

    def __init__(self,
                 urn: str,
                 devices: List[BoboDeviceTuple],
                 aes_key: str,
                 max_size_incoming: int,
                 max_size_outgoing: int,
                 listen_queue: int = 5,
                 timeout_accept: int = 5,
                 timeout_connect: int = 5,
                 timeout_send: int = 5,
                 timeout_receive: int = 5,
                 recv_bytes: int = 2048,
                 pad_char: str = '\0',
                 nonce_length: int = 16,
                 mac_length: int = 16):
        super().__init__()
        self._lock: RLock = RLock()
        self._thread_lock: RLock = RLock()

        self._closed: bool = False
        self._running: bool = False
        self._thread_closed: bool = False

        self._urn: str = urn
        self._devices: Dict[str, BoboDeviceTuple] = {}

        for d in devices:
            if d.urn in self._devices:
                raise BoboDistributedError(
                    "duplicate device URN {}".format(d.urn))
            self._devices[d.urn] = d

        if len(self._devices.keys()) == 0 or \
                (len(self._devices.keys()) == 1 and urn in self._devices):
            raise BoboDistributedError(
                "must provide at least one other device")

        if urn not in self._devices:
            raise BoboDistributedError(
                "URN not found in devices: {}".format(urn))

        if len(pad_char) != 1:
            raise BoboDistributedError(
                "pad_char must have a length of 1: '{}' has a length of {}"
                .format(pad_char, len(pad_char)))

        num_bytes_aes_key = len(aes_key)

        if (num_bytes_aes_key != self._BYTES_AES_128 and
                num_bytes_aes_key != self._BYTES_AES_192 and
                num_bytes_aes_key != self._BYTES_AES_256):
            raise BoboDistributedError(
                "AES key must be 16, 24, or 32 bytes long "
                "(respectively for AES-128, AES-192, or AES-256): "
                "'{}' has {} bytes.".format(aes_key, len(aes_key)))

        self._aes_key: bytes = aes_key.encode(self._UTF_8)
        self._listen_queue: int = listen_queue
        self._timeout_accept: int = timeout_accept
        self._timeout_connect: int = timeout_connect
        self._timeout_send: int = timeout_send
        self._timeout_receive: int = timeout_receive

        self._recv_bytes: int = recv_bytes
        self._pad_char: str = pad_char
        self._nonce_length: int = nonce_length
        self._mac_length: int = mac_length

        self._msg_min_length: int = \
            self._PAD_MODULO + nonce_length + mac_length

        self._thread_incoming: Thread = Thread(target=self._tcp_incoming)
        self._thread_outgoing: Thread = Thread(target=self._tcp_outgoing)

        self._queue_incoming: Queue[Dict[str, List[BoboRunTuple]]] = \
            Queue(maxsize=max_size_incoming)
        self._queue_outgoing: Queue[Dict[str, List[BoboRunTuple]]] = \
            Queue(maxsize=max_size_outgoing)

    def run(self) -> None:
        with self._lock:
            if self._closed:
                raise BoboDistributedError(self._EXC_CLOSED)

            if self._running:
                raise BoboDistributedError(self._EXC_RUNNING)

            self._thread_incoming.start()
            self._thread_outgoing.start()

            self._running = True

        while True:
            with self._lock:
                if self._closed:
                    self._running = False
                    break
                self._update()

    def _update(self):
        # Take incoming data and pass to decider
        while not self._queue_incoming.empty():
            incoming: Dict[str, List[BoboRunTuple]] = \
                self._queue_incoming.get_nowait()

            logging.debug("_update: processing incoming")

            completed: List[BoboRunTuple] = incoming[_KEY_COMPLETED]
            halted: List[BoboRunTuple] = incoming[_KEY_HALTED]
            updated: List[BoboRunTuple] = incoming[_KEY_UPDATED]

            logging.debug("_update: sending to subscribers")

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
        with self._lock:
            if self._closed:
                raise BoboDistributedError(self._EXC_CLOSED)

            if not self._running:
                raise BoboDistributedError(self._EXC_NOT_RUNNING)

            logging.debug("on_decider_update: packaging")

            outgoing: Dict[str, List[BoboRunTuple]] = {
                _KEY_COMPLETED: completed,
                _KEY_HALTED: halted,
                _KEY_UPDATED: updated
            }

            if not self._queue_outgoing.full():
                logging.debug("on_decider_update: adding to queue")
                self._queue_outgoing.put_nowait(outgoing)

            else:
                raise BoboDistributedSystemError(
                    "Outgoing queue is full.")

    def _tcp_incoming(self) -> None:
        """
        Executed within a thread. It accepts outside connections and stores
        their data in the incoming queue, if valid.
        """

        mydev = self._devices[self._urn]

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((mydev.addr, mydev.port))

        # queue requests before refusing outside connections
        s.listen(self._listen_queue)

        with s:
            while True:
                with self._thread_lock:
                    if self._thread_closed:
                        return

                try:
                    s.settimeout(self._timeout_accept)
                    client_s, client_addr = s.accept()
                    s.settimeout(None)
                    client_accepted = int(time.time())

                    logging.debug("New client: {} ({})"
                                  .format(client_addr, client_accepted))

                    addr_known = any(client_addr[0] == d.addr
                                     for d in self._devices.values())

                    if addr_known:
                        self._tcp_incoming_handle_client(
                            client_s, client_addr, client_accepted)

                except (BoboDistributedSystemError,
                        BoboDistributedTimeoutError) as e:
                    # From _tcp_incoming_handle_client
                    msg = "Incoming {}: {}".format(e.__class__.__name__, e)
                    logging.error(msg)
                    raise BoboDistributedSystemError(msg)

                except socket.timeout:
                    # From s.accept()
                    # Timeout is added here so that the thread can react to
                    # _thread_closed=True when no data received for a while
                    logging.debug("Incoming socket timeout (ignoring)")

                except Exception as e:
                    # From other
                    msg = "Incoming {}: {}".format(e.__class__.__name__, e)
                    logging.error(msg)
                    raise BoboDistributedSystemError(msg)

    def _tcp_outgoing(self):
        """
        Executed within a thread. It sends internal Decider state updates,
        stored in the outgoing queue, to external `BoboCEP` instances.
        """

        # TODO handling failures to send data
        #  - invalid device data e.g. (static) addr, urn, key
        #  - inability to connect to external device (n times)

        while True:
            with self._thread_lock:
                if self._thread_closed:
                    return

                if self._queue_outgoing.empty():
                    continue

                try:
                    msg: str = self._outgoing_to_json(
                        self._queue_outgoing.get_nowait())

                except (BoboJSONableError, TypeError) as e:
                    raise BoboDistributedSystemError(
                        "Outgoing {}: {}".format(e.__class__.__name__, e))

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            with s:
                try:
                    for d_urn in self._devices.keys():
                        with self._thread_lock:
                            if self._thread_closed:
                                return

                        # Ignore self...
                        if d_urn == self._urn:
                            continue

                        d = self._devices[d_urn]

                        logging.debug("Outgoing: {} ({}:{})",
                                      d.urn, d.addr, d.port)

                        s.settimeout(self._timeout_connect)
                        s.connect((d.addr, d.port))
                        s.settimeout(None)

                        msg_bytes = self._msg_wrap(msg)

                        s.settimeout(self._timeout_send)
                        s.sendall(msg_bytes)
                        s.settimeout(None)

                except TimeoutError as e:
                    # Raised when a system function timed out at
                    # the system level
                    raise BoboDistributedTimeoutError(
                        "Outgoing {}: {}".format(e.__class__.__name__, e))

                except OSError as e:
                    # This exception is raised when a system function
                    # returns a system-related error.
                    raise BoboDistributedSystemError(
                        "Outgoing {}: {}".format(e.__class__.__name__, e))

    def _tcp_incoming_handle_client(
            self, client_s, client_addr, client_accepted) -> None:
        """
        Handles an incoming client request.
        :param client_s: The client socket.
        :param client_addr: The client address of origin.
        :param client_accepted: The time when the client request was accepted.
        """
        with client_s:
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

                if len(bytes_msg) >= self._msg_min_length and \
                        bytes_msg[-len(self._END_BYTES):] == self._END_BYTES:

                    try:
                        plaintext = self._msg_unwrap(all_bytes)
                    except ValueError as e:
                        raise BoboDistributedTimeoutError(
                            "Failed to unwrap incoming message bytes:", e)

                    pt_bobo, pt_urn, pt_id, pt_json = self._split_plaintext(
                        plaintext)

                    # Check if message has expected starting string
                    if pt_bobo != self._START_STR:
                        raise BoboDistributedSystemError(
                            "Invalid start message '{}': expected '{}'."
                            .format(pt_bobo, self._START_STR))

                    # Check if URN is a recognised device
                    if pt_urn not in self._devices:
                        raise BoboDistributedSystemError(
                            "Unknown device URN '{}'.".format(pt_urn))

                    device: BoboDeviceTuple = self._devices[pt_urn]

                    # Check if ID key matches expected key for URN
                    if pt_id != device.id_key:
                        raise BoboDistributedSystemError(
                            "Invalid ID key for URN '{}'".format(device.urn))

                    # Update address if remote address has changed
                    if client_addr[0] != device.addr:
                        self._devices[pt_urn].addr = client_addr[0]

                    # TODO change pt_json to pt_str, where pt_str could be
                    #  "PING" for heartbeat messages?
                    #  if so, do not add message to incoming queue

                    try:
                        incoming = self._incoming_from_json(pt_json)

                    except (BoboJSONableError, TypeError) as e:
                        raise BoboDistributedSystemError(
                            "Unable to build incoming message from JSON:", e)

                    # Add incoming data to queue
                    if not self._queue_incoming.full():
                        self._queue_incoming.put_nowait(incoming)
                    else:
                        raise BoboDistributedSystemError(
                            "Incoming queue is full.")

                    break

    def _incoming_from_json(
            self, msg_str: str) -> Dict[str, List[BoboRunTuple]]:
        """
        :param msg_str: Incoming JSON string.
        :return: Incoming Decider update information.
        """
        msg = json.loads(msg_str, cls=_IncomingJSONDecoder)
        return msg

    def _outgoing_to_json(
            self, msg: Dict[str, List[BoboRunTuple]]) -> str:
        """
        :param msg: Outgoing Decider update information.
        :return: Outgoing JSON string.
        """
        return json.dumps(msg, cls=_OutgoingJSONEncoder)

    def _msg_wrap(self, msg: str) -> bytes:
        """
        :param msg: Wraps JSON string in other data for transit.
        :return: The bytes to transmit.
        """
        nonce = get_random_bytes(self._nonce_length)
        cipher = AES.new(self._aes_key, AES.MODE_GCM,
                         nonce=nonce, mac_len=self._mac_length)

        mydev = self._devices[self._urn]
        msg = "{} {} {} {}".format(
            self._START_STR, mydev.urn, mydev.id_key, msg)

        len_msg = len(msg)
        if len_msg % self._PAD_MODULO != 0:
            msg = msg + (self._pad_char *
                         (self._PAD_MODULO - len_msg % self._PAD_MODULO))

        ciphertext, mac = cipher.encrypt_and_digest(  # type: ignore
            msg.encode(self._UTF_8))

        # Append nonce, mac, end bytes
        ciphertext_bytes = bytearray(ciphertext)
        ciphertext_bytes.extend(nonce)
        ciphertext_bytes.extend(mac)
        ciphertext_bytes.extend(self._END_BYTES)

        return ciphertext_bytes

    def _msg_unwrap(self, msg_bytes: bytes) -> str:
        """
        :param msg_bytes: Incoming bytes.
        :return: Incoming JSON string with other data from transit.
        """
        nonce = msg_bytes[
                -(self._LEN_END_BYTES + self._mac_length + self._nonce_length):
                -(self._LEN_END_BYTES + self._mac_length)]
        mac = msg_bytes[
              -(self._LEN_END_BYTES + self._nonce_length):
              -self._LEN_END_BYTES]

        ciphertext = msg_bytes[:-(
                self._LEN_END_BYTES +
                self._mac_length +
                self._nonce_length)]

        cipher = AES.new(self._aes_key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(  # type: ignore
            ciphertext, mac).decode(
            self._UTF_8).rstrip(self._pad_char)

        return plaintext

    def _split_plaintext(self, plaintext: str) -> Tuple[str, str, str, str]:
        """
        :param plaintext: The string to split.
        :return: Incoming start text, URN, ID, and JSON string.
        """
        ix_delim = []

        for i, c in enumerate(plaintext):
            if c == ' ':
                ix_delim.append(i)

            if len(ix_delim) == 3:
                break

        if len(ix_delim) != 3:
            raise BoboDistributedSystemError("Invalid plaintext message.")

        # pt_bobo, pt_urn, pt_id, pt_json
        return plaintext[:ix_delim[0]], \
               plaintext[ix_delim[0] + 1:ix_delim[1]], \
               plaintext[ix_delim[1] + 1:ix_delim[2]], \
               plaintext[ix_delim[2] + 1:]

    def join(self):
        with self._lock:
            self._thread_incoming.join()
            self._thread_outgoing.join()

    def close(self):
        with self._lock:
            if self._closed:
                raise BoboDistributedError(self._EXC_CLOSED)

            logging.debug("Closing distributed: {}".format(self._urn))
            self._closed = True

            with self._thread_lock:
                self._thread_closed = True

    def is_closed(self) -> bool:
        with self._lock:
            return self._closed

    def size_incoming(self) -> int:
        with self._lock:
            return self._queue_incoming.qsize()

    def size_outgoing(self) -> int:
        with self._lock:
            return self._queue_outgoing.qsize()
