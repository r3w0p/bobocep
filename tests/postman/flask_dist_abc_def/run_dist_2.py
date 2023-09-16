# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

import logging
from datetime import datetime
from threading import Thread, RLock
from typing import Tuple, Any

from flask import Flask

from bobocep.cep.action import BoboAction, BoboActionHandlerMultithreading
from bobocep.cep.engine import BoboEngine
from bobocep.cep.event import BoboEventComplex
from bobocep.cep.phenom import BoboPatternBuilder, BoboPhenomenon, BoboPattern
from bobocep.dist import BoboDevice
from bobocep.setup import BoboSetupSimpleDistributed

app = Flask(__name__)
engine: BoboEngine


# A Flask interface that enables string data to be passed via a GET request.
# For example: 127.0.0.1:9090/data/int/hello
@app.route("/data/str/<my_str>", methods=['GET'])
def data_str(my_str):
    global engine
    engine.receiver.add_data(str(my_str))
    return str(my_str)


# A Flask interface at index that returns the current time in ISO8601 format.
@app.route("/", methods=['GET'])
def index():
    return datetime.now().isoformat()


class BoboActionCounter(BoboAction):
    """
    An action that keeps count of how many times it has been executed,
    and prints the count to stdout each time.

    Note: using RLock with BoboActionHandlerMultiprocessing causes problems,
    so BoboActionHandlerMultithreading is used instead.
    """

    def __init__(self, name: str = "action_counter"):
        """
        :param name: The name of the action.
        """
        super().__init__(name)
        self._lock: RLock = RLock()
        self._count: int = 0

    def execute(self, event: BoboEventComplex) -> Tuple[bool, Any]:
        """
        :param event: The generated complex event.

        :return: Success, and current count.
        """
        with self._lock:
            self._count += 1
            print("{} {}: {}".format(self._name, self._count, event.event_id))

            return True, None


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)

    # A simple pattern: "d" followed by "e" followed by "f".
    # Halt on "h".
    my_pattern: BoboPattern = BoboPatternBuilder("my_pattern") \
        .followed_by(lambda e, h: str(e.data) == "d") \
        .followed_by(lambda e, h: str(e.data) == "e") \
        .followed_by(lambda e, h: str(e.data) == "f") \
        .haltcondition(lambda e, h: str(e.data) == "h") \
        .generate()

    # When the pattern is fulfilled, its action, BoboActionCounter,
    # increments its internal counter and prints a message to stdout.
    my_phenomenon = BoboPhenomenon(
        name="my_phenomenon",
        patterns=[my_pattern],
        action=BoboActionCounter()
    )

    # A list of the devices that are to be part of your distributed BoboCEP
    # network. This list should contain yourself and all other external
    # BoboCEP instances.
    # - URNs are required to be unique for each device.
    # - ID keys are expected to be kept secret, and are used for identifying
    #   devices even if their addr / port were to change over time.
    devices = [
        # This is some other BoboCEP instance on the network.
        BoboDevice(
            addr="127.0.0.1",
            port=8081,
            urn="urn:bobocep:device:1",
            id_key="id_key_device_1"
        ),
        # This is you.
        BoboDevice(
            addr="127.0.0.1",
            port=8082,
            urn="urn:bobocep:device:2",
            id_key="id_key_device_2"
        )
    ]

    # The convenience class BoboSetupSimpleDistributed is used to make
    # distributed BoboCEP setup much simpler.
    # - The URN needs to match the URN for the devices representing you
    #   in the devices list.
    # - The AES, as with device ID keys, is expected to be kept secret.
    #   Each BoboCEP instance in the distributed network needs to have the
    #   same AES key to be able to encrypt and decrypt messages.
    engine, dist = BoboSetupSimpleDistributed(
        phenomena=[my_phenomenon],
        handler=BoboActionHandlerMultithreading(threads=5),
        urn="urn:bobocep:device:2",
        devices=devices,
        aes_key="1234567890ABCDEF"
    ).generate()

    # BoboCEP engine and distributed component are run on separate threads.
    thread_engine = Thread(target=lambda: engine.run())
    thread_dist = Thread(target=lambda: dist.run())

    # Start both threads.
    thread_engine.start()
    thread_dist.start()

    # The Flask server is started.
    app.run(
        host="0.0.0.0",
        port=9090,
        debug=True,
        use_reloader=False)
