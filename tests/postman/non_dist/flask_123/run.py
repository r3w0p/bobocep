# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

from datetime import datetime
from threading import RLock, Thread
from typing import Tuple, Any

from flask import Flask

from bobocep.cep.action import BoboAction, BoboActionHandlerMultithreading
from bobocep.cep.engine import BoboEngine
from bobocep.cep.event import BoboEventComplex
from bobocep.cep.phenom import BoboPattern, BoboPatternBuilder, \
    BoboPhenomenon
from bobocep.setup import BoboSetupSimple

app = Flask(__name__)  # v2.2.3
engine: BoboEngine


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
