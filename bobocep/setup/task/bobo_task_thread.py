from threading import Thread, Event

from bobocep.setup.task.bobo_task import BoboTask


class BoboTaskThread(Thread):
    """
    A thread to run BoboTask instances. It runs the setup task once, and
    then runs the loop task continually until the thread is cancelled.
    There is a delay between each loop.

    :param task: The task to perform.
    :type task: BoboTask

    :param delay: The delay between loops.
    :type delay: float
    """

    def __init__(self,
                 task: BoboTask,
                 delay: float):
        Thread.__init__(self)

        self._task = task
        self._delay = delay
        self._cancel = Event()

    def run(self):
        """Runs the task.

        :raises RuntimeError: Exception raised during task execution.
        """

        try:
            if not self._cancel.is_set():
                self._task.setup()

                # THREAD has been cancelled if False
                while not self._cancel.wait(self._delay):
                    self._task.loop()

                self._task.cancel()
        except Exception as e:
            raise RuntimeError("Exception raised during task execution: {}."
                               .format(e))

    def cancel(self):
        """Cancels the task."""

        self._cancel.set()
