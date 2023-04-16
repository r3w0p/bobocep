Examples
********

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


Distributed
===========

TODO


.. raw:: html

    <details>
    <summary><a>Code</a></summary>


.. code:: python

    TODO


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


.. note:: If you want to use the :code:`BoboActionHandlerMultiprocessing`
          action handler, then using :code:`RLock` may cause action execution
          to not work as intended. Therefore, it is recommended that
          you use the :code:`Blocking` and :code:`Multithreading` handlers
          for synchronised action execution.


.. raw:: html

    <details>
    <summary><a>Code</a></summary>


.. code:: python

    from threading import RLock, Thread
    from typing import Tuple, Any, Optional
    from datetime import datetime
    from flask import Flask

    from bobocep.cep.action import BoboAction, BoboActionHandlerMultithreading
    from bobocep.cep.engine.engine import BoboEngine
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
