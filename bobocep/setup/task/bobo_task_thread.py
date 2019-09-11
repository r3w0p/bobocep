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
        self._cancel_event = Event()

    def run(self):
        """Runs the thread."""

        try:
            if (not self._cancel_event.is_set()) and \
                    (not self._task.is_cancelled()):
                self._task.setup()

                # thread has been cancelled if True
                while not self._cancel_event.wait(self._delay):
                    # task has been cancelled if True
                    if not self._task.is_cancelled():
                        self._task.loop()
                    else:
                        break
        except Exception:
            pass
        finally:
            try:
                self._task.cancel()
            except Exception:
                pass
            self._cancel_event.set()

    def is_cancelled(self) -> bool:
        """
        :return: True if thread is cancelled, False otherwise.
        """

        return self._cancel_event.is_set()

    def cancel(self):
        """Cancels the thread."""

        self._cancel_event.set()
