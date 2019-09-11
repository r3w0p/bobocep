import unittest
from time import sleep

from bobocep.setup.task.bobo_task import BoboTask
from bobocep.setup.task.bobo_task_thread import BoboTaskThread

DELAY = 0.1
DELAY_WAIT = 0.5


class StubBoboTask(BoboTask):

    def __init__(self,
                 active: bool,
                 exception_setup: bool = False,
                 exception_loop: bool = False,
                 exception_cancel: bool = False) -> None:
        super().__init__(active=active)

        self.stub_setup = False
        self.stub_loop = False
        self.stub_cancel = False

        self.exception_setup = exception_setup
        self.exception_loop = exception_loop
        self.exception_cancel = exception_cancel

    def _setup(self) -> None:
        self.stub_setup = True

        if self.exception_setup:
            raise RuntimeError

    def _loop(self) -> None:
        self.stub_loop = True

        if self.exception_loop:
            raise RuntimeError

    def _cancel(self) -> None:
        self.stub_cancel = True

        if self.exception_cancel:
            raise RuntimeError


class TestBoboTaskThread(unittest.TestCase):

    def test_start_then_thread_cancel(self):
        task = StubBoboTask(active=True)
        thread = BoboTaskThread(task=task, delay=DELAY)

        thread.start()
        sleep(DELAY_WAIT)
        self.assertFalse(thread.is_cancelled())

        thread.cancel()
        sleep(DELAY_WAIT)
        self.assertTrue(thread.is_cancelled())

    def test_start_then_task_cancel(self):
        task = StubBoboTask(active=True)
        thread = BoboTaskThread(task=task, delay=DELAY)

        thread.start()
        sleep(DELAY_WAIT)
        self.assertFalse(thread.is_cancelled())

        task.cancel()
        sleep(DELAY_WAIT)
        self.assertTrue(thread.is_cancelled())

    def test_thread_cancelled_before_start(self):
        task = StubBoboTask(active=True)
        thread = BoboTaskThread(task=task, delay=DELAY)
        thread.cancel()

        thread.start()
        self.assertTrue(thread.is_cancelled())

    def test_task_cancelled_before_start(self):
        task = StubBoboTask(active=True)
        thread = BoboTaskThread(task=task, delay=DELAY)
        task.cancel()

        thread.start()
        self.assertTrue(thread.is_cancelled())

    def test_task_setup_exception(self):
        task = StubBoboTask(active=True, exception_setup=True)
        thread = BoboTaskThread(task=task, delay=DELAY)

        thread.start()
        sleep(DELAY_WAIT)
        self.assertTrue(thread.is_cancelled())

    def test_task_loop_exception(self):
        task = StubBoboTask(active=True, exception_loop=True)
        thread = BoboTaskThread(task=task, delay=DELAY)

        thread.start()
        sleep(DELAY_WAIT)
        self.assertTrue(thread.is_cancelled())

    def test_task_cancel_exception(self):
        task = StubBoboTask(active=True, exception_cancel=True)
        thread = BoboTaskThread(task=task, delay=DELAY)

        thread.start()
        sleep(DELAY_WAIT)
        thread.cancel()
        sleep(DELAY_WAIT)
        self.assertTrue(thread.is_cancelled())
