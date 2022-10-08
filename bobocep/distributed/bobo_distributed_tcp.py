# Copyright (c) 2019-2022 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import socket
from threading import Thread, RLock
from typing import List
from bobocep.distributed.bobo_distributed import BoboDistributed
from queue import Queue
import time

from bobocep.distributed.bobo_device_tuple import \
    BoboDeviceTuple
from bobocep.distributed.bobo_distributed_error import BoboDistributedError
from bobocep.distributed.bobo_distributed_timeout_error import \
    BoboDistributedTimeoutError
from bobocep.cep.engine.decider.bobo_decider_run import BoboDeciderRunTuple
from bobocep.cep.event.bobo_event import BoboEvent
from bobocep.cep.event.bobo_event_action import BoboEventAction
from bobocep.cep.event.bobo_event_complex import BoboEventComplex
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class BoboDistributedTCP(BoboDistributed):

    _EXC_CLOSED = "object is closed"
    _EXC_RUNNING = "object is running"
    _EXC_NOT_RUNNING = "object is not running"

    _UTF_8 = "UTF-8"
    _TIMEOUT_ACCEPT = 5
    _PAD_MODULO = 16
    _START_WORD = "BOBO"

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
        self._closed: bool = False
        self._running: bool = False

        self._devices = {}

        for d in devices:
            if d.urn in self._devices:
                raise BoboDistributedError(
                    "duplicate device URN {}".format(d.urn))
            self._devices[d.urn] = d

        if urn not in self._devices:
            raise BoboDistributedError(
                "URN not found in devices: {}".format(urn))

        if len(pad_char) != 1:
            raise BoboDistributedError(
                "pad_char must have a length of 1: '{}' has a length of {}"
                .format(pad_char, len(pad_char)))

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

        self._thread_lock: RLock = RLock()
        self._thread_closed: bool = False

        self._thread_incoming: Thread = Thread(target=self._tcp_incoming)
        self._thread_outgoing: Thread = Thread(target=self._tcp_outgoing)

        self._queue_incoming: Queue = Queue(maxsize=max_size_incoming)
        self._queue_outgoing: Queue = Queue(maxsize=max_size_outgoing)

    def _process(self):
        while self._running:
            # TODO
            time.sleep(5)

    def run(self):
        with self._lock:
            if self._closed:
                raise BoboDistributedError(self._EXC_CLOSED)

            if self._running:
                raise BoboDistributedError(self._EXC_RUNNING)

            self._thread_incoming.start()
            self._thread_outgoing.start()

            self._running = True
            self._process()

    def _msg_wrap(self, msg: str) -> bytes:
        nonce = get_random_bytes(self._nonce_length)
        cipher = AES.new(self._aes_key, AES.MODE_GCM,
                         nonce=nonce, mac_len=self._mac_length)

        mydev = self._devices[self._urn]
        msg = "{} {} {} {}".format(
            self._START_WORD, mydev.urn, mydev.id_key, msg)

        len_msg = len(msg)
        if len_msg % self._PAD_MODULO != 0:
            msg = msg + (self._pad_char *
                         (self._PAD_MODULO - len_msg % self._PAD_MODULO))

        ciphertext, mac = cipher.encrypt_and_digest(msg.encode(self._UTF_8))

        # Append nonce and mac
        ciphertext_nonce_tag = bytearray(ciphertext)
        ciphertext_nonce_tag.extend(nonce)
        ciphertext_nonce_tag.extend(mac)
        ciphertext_nonce_tag = bytes(ciphertext_nonce_tag)

        return ciphertext_nonce_tag

    def _msg_unwrap(self, msg_bytes: bytes) -> str:
        nonce = msg_bytes[-(self._nonce_length + self._mac_length):
                          -self._mac_length]
        mac = msg_bytes[-self._nonce_length:]

        ciphertext = msg_bytes[:-(self._nonce_length + self._mac_length)]

        cipher = AES.new(self._aes_key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, mac) \
            .decode(self._UTF_8) \
            .rstrip(self._pad_char)

        return plaintext

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

                if len(bytes_msg) >= self._msg_min_length:
                    plaintext = self._msg_unwrap(all_bytes)

                    if plaintext.startswith(self._START_WORD):
                        print(plaintext)
                        break

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

                    addr_known = any(client_addr[0] == othdev.addr
                                     for othdev in self._devices.values())

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

            time.sleep(1)

    def join(self):
        with self._lock:
            if self._closed:
                raise BoboDistributedError(self._EXC_CLOSED)

            if not self._running:
                raise BoboDistributedError(self._EXC_NOT_RUNNING)

            self._thread_incoming.join()
            self._thread_outgoing.join()

    def close(self):
        with self._lock:
            if self._closed:
                raise BoboDistributedError(self._EXC_CLOSED)

            self._closed = True

            with self._thread_lock:
                print("Closing threads")
                self._thread_closed = True

    def is_closed(self) -> bool:
        with self._lock:
            return self._closed

    def on_receiver_event(self, event: BoboEvent):
        """"""

    def on_decider_run_changes(
            self,
            halted_complete: List[BoboDeciderRunTuple],
            halted_incomplete: List[BoboDeciderRunTuple],
            updated: List[BoboDeciderRunTuple]):
        """"""

    def on_producer_complex_event(self, event: BoboEventComplex):
        """"""

    def on_forwarder_action_event(self, event: BoboEventAction):
        """"""
