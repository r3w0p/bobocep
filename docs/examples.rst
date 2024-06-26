========
Examples
========

Simple
======

This example demonstrates setting up a simple, non-distributed :code:`BoboCEP`
instance with a single pattern:
:code:`1`, followed by :code:`2`, followed by :code:`3`.
The engine runs on a separate thread, and a :code:`for` loop adds numbers
:code:`0` to :code:`4` to the data stream in 1-second intervals.
When the pattern is fulfilled, an instance of the custom action
:code:`BoboActionPrint` prints :code:`"Hello 123!"`.


.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>


.. code:: python

    from threading import Thread
    from time import sleep
    from typing import Tuple, Any

    from bobocep.cep.action import BoboAction, BoboActionHandlerMultithreading
    from bobocep.cep.event import BoboEventComplex
    from bobocep.cep.phenom import BoboPatternBuilder, BoboPhenomenon, BoboPattern
    from bobocep.setup import BoboSetupSimple


    class BoboActionPrint(BoboAction):
        """An action that prints a string to stdout."""

        def __init__(self, name: str, message: str):
            """
            :param name: The name of the action.
            :param message: The message to print to stdout.
            """
            super().__init__(name)

            self._message: str = message

        def execute(self, event: BoboEventComplex) -> Tuple[bool, Any]:
            """
            :param event: The complex event generated when my_pattern was
                satisfied with data: 1, 2, 3.

            :return: Whether action execution was successful, followed by
                any additional data (or None).
            """
            print(self._message)

            return True, self._message


    if __name__ == '__main__':
        # A simple pattern to test BoboCEP.
        #
        # The pattern is called "my_pattern" and consists of three predicates.
        # The first predicate checks if an event has data equal to 1.
        # This must be followed by another event with data equal to 2.
        # Finally, a third event must follow with data equal to 3.
        #
        # If three events are input into the BoboCEP system in this order,
        # the pattern is fulfilled and a complex event is generated.
        my_pattern: BoboPattern = BoboPatternBuilder("my_pattern") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by(lambda e, h: int(e.data) == 2) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        # The pattern must be associated with a phenomenon which explains what
        # the pattern is trying to model / represent / observe.
        #
        # This phenomenon is called "my_phenomenon".
        #
        # When any of its patterns are fulfilled, its action, BoboActionPrint,
        # will be executed. This action will print a message to stdout.
        my_phenomenon = BoboPhenomenon(
            name="my_phenomenon",
            patterns=[my_pattern],
            action=BoboActionPrint(
                name="my_action",
                message="Hello 123!")
        )

        # The convenience class BoboSetupSimple is used to make BoboCEP setup
        # much simpler. The list of phenomena needs to be provided and an
        # action handler. The handler allows for five actions to be executed
        # concurrently over five threads.
        engine = BoboSetupSimple(
            phenomena=[my_phenomenon],
            handler=BoboActionHandlerMultithreading(threads=5)
        ).generate()

        # BoboCEP is started on a separate thread so that we can pass data to it
        # on the current thread.
        thread_engine = Thread(target=lambda: engine.run())
        thread_engine.start()

        # Data from 0 to 4 are passed to BoboCEP.
        # When 1, 2, 3 are sent, the output will show the action's message.
        for data in range(0, 5):
            print(data)
            engine.receiver.add_data(data)
            sleep(1)

        # The engine and its thread are closed.
        engine.close()
        thread_engine.join()


.. raw:: html

    </details>
    </br>


Advanced
========

This example shows you how to set up :code:`BoboCEP` without
relying on the :code:`BoboSetup` classes.

It is the same example as :ref:`examples:Simple` above, but with the
subsystems of :code:`BoboEngine` manually assembled.


.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>


.. code:: python

    from threading import Thread
    from time import sleep
    from typing import Tuple, Any

    from bobocep.cep.action import BoboAction, BoboActionHandlerMultithreading
    from bobocep.cep.engine import BoboEngine
    from bobocep.cep.engine.decider import BoboDecider
    from bobocep.cep.engine.forwarder import BoboForwarder
    from bobocep.cep.engine.producer import BoboProducer
    from bobocep.cep.engine.receiver import BoboReceiver
    from bobocep.cep.engine.receiver.validator import BoboValidatorAll
    from bobocep.cep.event import BoboEventComplex
    from bobocep.cep.gen import BoboGenEventIDUnique, BoboGenTimestampEpoch, \
        BoboGenEventTime
    from bobocep.cep.phenom import BoboPatternBuilder, BoboPhenomenon, BoboPattern


    class BoboActionPrint(BoboAction):
        """An action that prints a string to stdout."""

        def __init__(self, name: str, message: str):
            """
            :param name: The name of the action.
            :param message: The message to print to stdout.
            """
            super().__init__(name)

            self._message: str = message

        def execute(self, event: BoboEventComplex) -> Tuple[bool, Any]:
            """
            :param event: The complex event generated when my_pattern was
                satisfied with data: 1, 2, 3.

            :return: Whether action execution was successful, followed by
                any additional data (or None).
            """
            print(self._message)

            return True, self._message


    if __name__ == '__main__':
        # A simple pattern to test BoboCEP.
        #
        # The pattern is called "my_pattern" and consists of three predicates.
        # The first predicate checks if an event has data equal to 1.
        # This must be followed by another event with data equal to 2.
        # Finally, a third event must follow with data equal to 3.
        #
        # If three events are input into the BoboCEP system in this order,
        # the pattern is fulfilled and a complex event is generated.
        my_pattern: BoboPattern = BoboPatternBuilder("my_pattern") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by(lambda e, h: int(e.data) == 2) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        # The pattern must be associated with a phenomenon which explains what
        # the pattern is trying to model / represent / observe.
        #
        # This phenomenon is called "my_phenomenon".
        #
        # When any of its patterns are fulfilled, its action, BoboActionPrint,
        # will be executed. This action will print a message to stdout.
        my_phenomenon = BoboPhenomenon(
            name="my_phenomenon",
            patterns=[my_pattern],
            action=BoboActionPrint(
                name="my_action",
                message="Hello 123!")
        )

        # The list of all phenomena under consideration by BoboCEP
        phenomena = [my_phenomenon]

        # Custom URN to prefix before event IDs
        urn = "urn:bobocep:"

        # Accept all data types
        validator = BoboValidatorAll()

        # Unique event ID with custom URN prefixed
        gen_event_id = BoboGenEventIDUnique(urn)

        # Unique run ID with custom URN prefixed
        gen_run_id = BoboGenEventIDUnique(urn)

        # Timestamp is the time since the epoch
        gen_timestamp = BoboGenTimestampEpoch()

        # Generate simple event every second and add to Receiver data stream
        gen_event = BoboGenEventTime(millis=1000)

        # Action handler that can process five actions concurrently
        handler = BoboActionHandlerMultithreading(threads=5)

        # Create Receiver, where data are first entered into BoboCEP
        receiver = BoboReceiver(
            validator=validator,
            gen_event_id=gen_event_id,
            gen_timestamp=gen_timestamp,
            gen_event=gen_event)

        # Create Decider, where data are compared against pattern instances (runs)
        decider = BoboDecider(
            phenomena=phenomena,
            gen_event_id=gen_event_id,
            gen_run_id=gen_run_id)

        # Create Producer, where complex event are generated
        producer = BoboProducer(
            phenomena=phenomena,
            gen_event_id=gen_event_id,
            gen_timestamp=gen_timestamp)

        # Create Forwarder, where actions are executed and action events generated
        forwarder = BoboForwarder(
            phenomena=phenomena,
            handler=handler,
            gen_event_id=gen_event_id,
            gen_timestamp=gen_timestamp)

        # Create Engine, which operates the subsystems above
        engine = BoboEngine(
            receiver=receiver,
            decider=decider,
            producer=producer,
            forwarder=forwarder)

        # BoboCEP is started on a separate thread so that we can pass data to it
        # on the current thread.
        thread_engine = Thread(target=lambda: engine.run())
        thread_engine.start()

        # Data from 0 to 4 are passed to BoboCEP.
        # When 1, 2, 3 are sent, the output will show the action's message.
        for data in range(0, 5):
            print(data)
            engine.receiver.add_data(data)
            sleep(1)

        # The engine and its thread are closed.
        engine.close()
        thread_engine.join()


If you want to include distributed processing to the above, then
add these additional imports:


.. code:: python

    from typing import List
    from bobocep.dist import BoboDistributedTCP, BoboDevice
    from bobocep.dist.crypto import BoboDistributedCryptoAES


Then, add the following, just after creating the :code:`BoboEngine` instance.


.. code:: python

    # Create Device list and AES key accordingly
    devices: List[BoboDevice] = ...
    aes_key: str = ...

    # Generate Distributed TCP instance
    distributed: BoboDistributedTCP = BoboDistributedTCP(
        urn=urn,
        decider=engine.decider,
        devices=devices,
        crypto=BoboDistributedCryptoAES(aes_key=aes_key))

    # Subscribe Decider to Distributed, and vice versa
    engine.decider.subscribe(distributed)
    distributed.subscribe(engine.decider)


.. raw:: html

    </details>
    </br>


Distributed
===========

The :code:`BoboSetupSimpleDistributed` class uses TCP for decentralised
message-passing, and requires AES encryption to encrypt all traffic
between :code:`BoboCEP` instances.

- The AES key that you choose must be 16, 24, or 32 bytes long
  for AES-128, AES-192, or AES-256 encryption, respectively.

Distributed works by defining a list of :code:`BoboDevice` representing
all :code:`BoboCEP` instances (including yourself) that will synchronise
together, and providing each device with a unique URN and an ID key
to identify the events generated by a device and identify exchanged messages
from that device, respectively.


.. warning::
    The ID keys that you use for devices, and the AES key, are expected
    to be kept secret and **not** hard-coded into your software.
    The example below is for demonstration purposes only.


Similar to the :ref:`examples:Simple` example above, there is a single pattern
that expects :code:`a`, followed by :code:`b`, followed by :code:`c`, with
an additional haltcondition :code:`h` that will halt any partially-completed
run for this pattern.


.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>


Firstly, run the following code as :code:`dist_1.py`. This will represent
device :code:`urn:bobocep:device:1`.

.. code:: python

    import logging
    from threading import Thread, RLock
    from typing import Tuple, Any

    from flask import Flask

    from bobocep.cep.action import BoboAction, BoboActionHandlerMultithreading
    from bobocep.cep.engine import BoboEngine
    from bobocep.cep.event import BoboEventComplex
    from bobocep.cep.phenom import BoboPatternBuilder, BoboPhenomenon, BoboPattern
    from bobocep.dist import BoboDevice
    from bobocep.setup import BoboSetupSimpleDistributed

    app = Flask(__name__)  # v2.2.3
    engine: BoboEngine


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

        # A simple pattern: "a" followed by "b" followed by "c".
        # Halt on "h".
        my_pattern: BoboPattern = BoboPatternBuilder("my_pattern") \
            .followed_by(lambda e, h: str(e.data) == "a") \
            .followed_by(lambda e, h: str(e.data) == "b") \
            .followed_by(lambda e, h: str(e.data) == "c") \
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
            # This is Device 1 (you).
            BoboDevice(
                addr="127.0.0.1",
                port=8081,
                urn="urn:bobocep:device:1",
                id_key="id_key_device_1"
            ),
            # This is Device 2.
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
            urn="urn:bobocep:device:1",
            devices=devices,
            aes_key="1234567890ABCDEF"
        ).generate()

        # BoboCEP engine and distributed component are run on separate threads.
        thread_engine = Thread(target=lambda: engine.run())
        thread_dist = Thread(target=lambda: dist.run())

        # Start both threads.
        thread_engine.start()
        thread_dist.start()


Then, run the following code as :code:`dist_2.py`. This will represent
device :code:`urn:bobocep:device:2`. This code also has an additional
:code:`for` loop that will generate data for :code:`device:2`
to consume. If you watch the outlog logs, you should see state synchronisation
between both devices.


.. code:: python

    import logging
    import time
    from threading import Thread, RLock
    from typing import Tuple, Any

    from flask import Flask

    from bobocep.cep.action import BoboAction, BoboActionHandlerMultithreading
    from bobocep.cep.engine import BoboEngine
    from bobocep.cep.event import BoboEventComplex
    from bobocep.cep.phenom import BoboPatternBuilder, BoboPhenomenon, BoboPattern
    from bobocep.dist import BoboDevice
    from bobocep.setup import BoboSetupSimpleDistributed

    app = Flask(__name__)  # v2.2.3
    engine: BoboEngine


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

        # A simple pattern: "a" followed by "b" followed by "c".
        # Halt on "h".
        my_pattern: BoboPattern = BoboPatternBuilder("my_pattern") \
            .followed_by(lambda e, h: str(e.data) == "a") \
            .followed_by(lambda e, h: str(e.data) == "b") \
            .followed_by(lambda e, h: str(e.data) == "c") \
            .haltcondition(lambda e, h: str(e.data) == "h") \
            .generate()

        my_phenomenon = BoboPhenomenon(
            name="my_phenomenon",
            patterns=[my_pattern],
            action=BoboActionCounter()
        )

        devices = [
            # This is Device 1.
            BoboDevice(
                addr="127.0.0.1",
                port=8081,
                urn="urn:bobocep:device:1",
                id_key="id_key_device_1"
            ),
            # This is Device 2 (you).
            BoboDevice(
                addr="127.0.0.1",
                port=8082,
                urn="urn:bobocep:device:2",
                id_key="id_key_device_2"
            )
        ]

        # Distributed for Device 2.
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

        time.sleep(5)

        # Additional code to generate "a", "b", "c" five times.
        for _ in range(5):
            for data in ["a", "b", "c"]:
                engine.receiver.add_data(data)
                time.sleep(3)


.. raw:: html

    </details>
    </br>


Flask
=====

Similar to the :ref:`examples:Simple` example above, there is a single pattern
that expects :code:`1`, followed by :code:`2`, followed by :code:`3`.
However, these values must, instead, be provided via GET requests using
a `Flask <https://flask.palletsprojects.com/>`_ server.

This can be accomplished with three separate calls, as follows:

- :code:`http://127.0.0.1:8080/data/int/1`
- :code:`http://127.0.0.1:8080/data/int/2`
- :code:`http://127.0.0.1:8080/data/int/3`

Each time the phenomenon's pattern is fulfilled, it increments its internal
counter and prints a message to stdout, displaying its action name, the current
counter value, and the ID of the complex event that was generated. For example:
:code:`action_counter 1: 1681645446_0`.


.. warning::
    If you want to use the :code:`BoboActionHandlerMultiprocessing`
    action handler, then using :code:`RLock` may cause action execution
    to not work as intended. Therefore, it is recommended that
    you use the :code:`Blocking` and :code:`Multithreading` handlers
    for synchronised action execution.


.. raw:: html

    <details>
    <summary><a>Code</a></summary>
    </br>


.. code:: python

    from threading import RLock, Thread
    from typing import Tuple, Any, Optional
    from datetime import datetime
    from flask import Flask

    from bobocep.cep.action import BoboAction, BoboActionHandlerMultithreading
    from bobocep.cep.engine import BoboEngine
    from bobocep.cep.event import BoboEventComplex
    from bobocep.cep.phenom import BoboPattern, BoboPatternBuilder, \
        BoboPhenomenon
    from bobocep.setup import BoboSetupSimple

    app = Flask(__name__)  # v2.2.3
    engine: Optional[BoboEngine] = None


    # A Flask interface that enables integer data to be passed via a GET request.
    # For example: 127.0.0.1/data/int/6
    @app.route("/data/int/<my_int>", methods=['GET'])
    def data_int(my_int):
        global engine
        engine.receiver.add_data(int(my_int))
        return str(int(my_int))


    # A Flask interface at index that returns the current time in ISO8601 format.
    @app.route("/", methods=['GET'])
    def index():
        return datetime.now().isoformat()


    class BoboActionCounter(BoboAction):
        """
        An action that keeps count of how many times it has been executed,
        and prints the count to stdout each time.
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
        # A simple pattern to test BoboCEP.
        #
        # The pattern is called "my_pattern" and consists of three predicates.
        # The first predicate checks if an event has data equal to 1.
        # This must be followed by another event with data equal to 2.
        # Finally, a third event must follow with data equal to 3.
        #
        # If three events are input into the BoboCEP system in this order,
        # the pattern is fulfilled and a complex event is generated.
        my_pattern: BoboPattern = BoboPatternBuilder("my_pattern") \
            .followed_by(lambda e, h: int(e.data) == 1) \
            .followed_by(lambda e, h: int(e.data) == 2) \
            .followed_by(lambda e, h: int(e.data) == 3) \
            .generate()

        # The pattern must be associated with a phenomenon which explains what
        # the pattern is trying to model / represent / observe.
        #
        # This phenomenon is called "my_phenomenon".
        #
        # When any of its patterns are fulfilled, its action, BoboActionCounter,
        # increments its internal counter and prints a message to stdout.
        my_phenomenon = BoboPhenomenon(
            name="my_phenomenon",
            patterns=[my_pattern],
            action=BoboActionCounter()
        )

        # The convenience class BoboSetupSimple is used to make BoboCEP setup
        # much simpler. The list of phenomena needs to be provided and an
        # action handler. The handler allows for five actions to be executed
        # concurrently over five threads.
        engine = BoboSetupSimple(
            phenomena=[my_phenomenon],
            handler=BoboActionHandlerMultithreading(threads=5)
        ).generate()

        # BoboCEP is started on a separate thread so that we can pass data to it
        # via Flask interface calls.
        thread_engine = Thread(target=lambda: engine.run())
        thread_engine.start()

        # The Flask server is started.
        app.run(
            host="0.0.0.0",
            port=8080,
            debug=True,
            use_reloader=False)


.. raw:: html

    </details>
    </br>
