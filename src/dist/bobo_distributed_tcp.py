# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import json
import socket
import time
from queue import Queue
from threading import Thread, RLock
from typing import List, Dict, Tuple

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from src.cep.engine.decider.bobo_decider_run_tuple import BoboDeciderRunTuple
from src.cep.event.bobo_event import BoboEvent
from src.cep.event.bobo_event_action import BoboEventAction
from src.cep.event.bobo_event_complex import BoboEventComplex
from src.dist.bobo_device_tuple import \
    BoboDeviceTuple
from src.dist.bobo_distributed import BoboDistributed
from src.dist.bobo_distributed_error import BoboDistributedError
from src.dist.bobo_distributed_system_error import \
    BoboDistributedSystemError
from src.dist.bobo_distributed_timeout_error import \
    BoboDistributedTimeoutError


class BoboDistributedTCP(BoboDistributed):
    _EXC_CLOSED = "object is closed"
    _EXC_RUNNING = "object is running"
    _EXC_NOT_RUNNING = "object is not running"

    _UTF_8 = "UTF-8"
    _TIMEOUT_ACCEPT = 5
    _TIMEOUT_CONNECT = 5
    _TIMEOUT_SEND = 5
    _PAD_MODULO = 16
    _START_MSG = "BOBO"
    _END_BYTES = "BOBO".encode("UTF-8")
    _LEN_END_BYTES = len(_END_BYTES)

    _BYTES_AES_128 = 16
    _BYTES_AES_192 = 24
    _BYTES_AES_256 = 32

    _KEY_HALTED_COMPLETE = "halted_complete"
    _KEY_HALTED_INCOMPLETE = "halted_incomplete"
    _KEY_UPDATED = "updated"

    def __init__(self,
                 urn: str,
                 devices: List[BoboDeviceTuple],
                 aes_key: str,
                 max_size_incoming: int,
                 max_size_outgoing: int,
                 listen: int = 5,
                 timeout_receive: int = 5,
                 recv_bytes: int = 1024,
                 pad_char: str = '\0',
                 nonce_length: int = 16,
                 mac_length: int = 16):
        super().__init__()
        self._lock: RLock = RLock()
        self._thread_lock: RLock = RLock()

        self._closed: bool = False
        self._running: bool = False
        self._thread_closed: bool = False

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
                "AES key must be 16, 24 or 32 bytes long "
                "(respectively for AES-128, AES-192 or AES-256): "
                "'{}' has {} bytes.".format(aes_key, len(aes_key)))

        self._urn: str = urn
        self._aes_key: bytes = aes_key.encode(self._UTF_8)
        self._listen: int = listen
        self._timeout_receive: int = timeout_receive
        self._recv_bytes: int = recv_bytes
        self._pad_char: str = pad_char
        self._nonce_length: int = nonce_length
        self._mac_length: int = mac_length
        self._msg_min_length: int = \
            self._PAD_MODULO + nonce_length + mac_length

        self._thread_incoming: Thread = Thread(target=self._tcp_incoming)
        self._thread_outgoing: Thread = Thread(target=self._tcp_outgoing)

        self._queue_incoming: Queue[Dict] = Queue(maxsize=max_size_incoming)
        self._queue_outgoing: Queue[Dict] = Queue(maxsize=max_size_outgoing)

    def run(self):
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

    def join(self):
        with self._lock:
            self._thread_incoming.join()
            self._thread_outgoing.join()

    def close(self):
        with self._lock:
            if self._closed:
                raise BoboDistributedError(self._EXC_CLOSED)

            self._closed = True

            with self._thread_lock:
                self._thread_closed = True

    def is_closed(self) -> bool:
        with self._lock:
            return self._closed

    def on_decider_update(
            self,
            halted_complete: List[BoboDeciderRunTuple],
            halted_incomplete: List[BoboDeciderRunTuple],
            updated: List[BoboDeciderRunTuple]):
        with self._lock:
            if self._closed:
                raise BoboDistributedError(self._EXC_CLOSED)

            if not self._running:
                raise BoboDistributedError(self._EXC_NOT_RUNNING)

            # TODO BoboJsonable error handling
            self._queue_outgoing.put_nowait({
                self._KEY_HALTED_COMPLETE: [
                    hc.to_dict() for hc in halted_complete],
                self._KEY_HALTED_INCOMPLETE: [
                    hi.to_dict() for hi in halted_incomplete],
                self._KEY_UPDATED: [
                    upd.to_dict() for upd in updated]
            })

    def size_incoming(self) -> int:
        with self._lock:
            return self._queue_incoming.qsize()

    def size_outgoing(self) -> int:
        with self._lock:
            return self._queue_outgoing.qsize()

    def _update(self):
        # TODO implementation
        pass

    def _tcp_incoming(self):
        mydev = self._devices[self._urn]

        print("Creating socket...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Connecting to: {}:{}".format(mydev.addr, mydev.port))
        s.bind((mydev.addr, mydev.port))

        print("Listening...")
        # queue up as many as 5 connect requests (the normal max)
        # before refusing outside connections
        s.listen(self._listen)

        with s:
            while True:
                with self._thread_lock:
                    if self._thread_closed:
                        return

                try:
                    s.settimeout(self._TIMEOUT_ACCEPT)
                    client_s, client_addr = s.accept()
                    s.settimeout(None)
                    client_accepted = int(time.time())

                    addr_known = any(client_addr[0] == d.addr
                                     for d in self._devices.values())

                    if addr_known:
                        self._tcp_incoming_handle_client(
                            client_s, client_addr, client_accepted)

                except BoboDistributedTimeoutError as e:
                    # From _tcp_incoming_handle_client
                    print("Incoming {}: {}".format(e.__class__.__name__, e))

                except TimeoutError:
                    # From accept
                    # Timeout is added here so that the thread can react to
                    # _thread_closed=True when no data has been received
                    # in a while
                    pass

                except Exception as e:
                    # From other
                    print("Incoming {}: {}".format(e.__class__.__name__, e))

    def _tcp_outgoing(self):
        while True:
            with self._thread_lock:
                if self._thread_closed:
                    return

                if self._queue_outgoing.empty():
                    continue

                try:
                    msg = json.dumps(self._queue_outgoing.get_nowait())

                except TypeError as e:
                    print("Outgoing {}: {}".format(e.__class__.__name__, e))

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

                        s.settimeout(self._TIMEOUT_CONNECT)
                        s.connect((d.addr, d.port))
                        s.settimeout(None)

                        # TODO handle wrap exception(s)
                        msg_bytes = self._msg_wrap(msg)
                        # print(len(msg_bytes))

                        s.settimeout(self._TIMEOUT_SEND)
                        s.sendall(msg_bytes)
                        s.settimeout(None)

                        # print("Sent: {}".format(msg))

                except TimeoutError as e:
                    # Raised when a system function timed out at
                    # the system level
                    print("Outgoing {}: {}".format(e.__class__.__name__, e))
                    raise BoboDistributedTimeoutError(str(e))

                except OSError as e:
                    # This exception is raised when a system function
                    # returns a system-related error.
                    print("Outgoing {}: {}".format(e.__class__.__name__, e))
                    raise BoboDistributedSystemError(str(e))

    def _tcp_incoming_handle_client(
            self, client_s, client_addr, client_accepted):
        print("Connection from: {}".format(client_addr))

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
                    # TODO handle unwrap exception(s)
                    #  e.g. "ValueError: MAC check failed"
                    plaintext = self._msg_unwrap(all_bytes)

                    # TODO handle split exception(s)
                    pt_bobo, pt_urn, pt_id, pt_json = self._split_plaintext(
                        plaintext)

                    if pt_bobo != self._START_MSG:
                        raise BoboDistributedSystemError(
                            "Invalid start message '{}': expected '{}'."
                            .format(pt_bobo, self._START_MSG))

                    # TODO if urn
                    # TODO if id

                    # TODO json exception(s)
                    ljsn = json.loads(pt_json)

                    # TODO exceptions for full queues...?
                    #  i think i did this elsewhere...
                    self._queue_incoming.put_nowait(ljsn)

    def _split_plaintext(self, plaintext: str) -> Tuple[str, str, str, str]:
        ix_delim = []

        for i, c in enumerate(plaintext):
            if c == ' ':
                ix_delim.append(i)

            if len(ix_delim) == 3:
                break

        if len(ix_delim) != 3:
            raise BoboDistributedSystemError("Invalid plaintext message.")

        return plaintext[:ix_delim[0]],\
               plaintext[ix_delim[0]:ix_delim[1]], \
               plaintext[ix_delim[1]:ix_delim[2]], \
               plaintext[ix_delim[2]:]

    def _msg_wrap(self, msg: str) -> bytes:
        nonce = get_random_bytes(self._nonce_length)
        cipher = AES.new(self._aes_key, AES.MODE_GCM,
                         nonce=nonce, mac_len=self._mac_length)

        mydev = self._devices[self._urn]
        msg = "{} {} {} {}".format(
            self._START_MSG, mydev.urn, mydev.id_key, msg)

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
        nonce = msg_bytes[
                -(self._LEN_END_BYTES + self._mac_length + self._nonce_length):
                -(self._LEN_END_BYTES + self._mac_length)]
        mac = msg_bytes[
              -(self._LEN_END_BYTES + self._nonce_length):-self._LEN_END_BYTES]

        ciphertext = msg_bytes[:-(
                    self._LEN_END_BYTES +
                    self._mac_length +
                    self._nonce_length)]

        cipher = AES.new(self._aes_key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(  # type: ignore
            ciphertext, mac).decode(
            self._UTF_8).rstrip(self._pad_char)

        return plaintext

    def on_receiver_update(self, event: BoboEvent):
        """"""

    def on_producer_update(self, event: BoboEventComplex):
        """"""

    def on_forwarder_update(self, event: BoboEventAction):
        """"""
