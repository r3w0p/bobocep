import unittest

from bobocep.setup.task.bobo_task import BoboTask


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


class TestBoboTask(unittest.TestCase):

    def test_activate_deactivate(self):
        self.assertTrue(StubBoboTask(active=True).is_active())

        task = StubBoboTask(active=False)
        self.assertFalse(task.is_active())
        task.activate()
        self.assertTrue(task.is_active())
        task.deactivate()
        self.assertFalse(task.is_active())

    def test_setup(self):
        task = StubBoboTask(active=True)
        self.assertFalse(task.is_setup())

        task.setup()
        self.assertTrue(task.is_setup())

    def test_setup_failure_cancelled(self):
        task = StubBoboTask(active=True)
        task.cancel()

        with self.assertRaises(RuntimeError):
            task.setup()

        self.assertFalse(task.is_setup())

    def test_setup_failure_already_setup(self):
        task = StubBoboTask(active=True)
        task.setup()

        with self.assertRaises(RuntimeError):
            task.setup()

        self.assertTrue(task.is_setup())

    def test_setup_failure_exception(self):
        task = StubBoboTask(active=True,
                            exception_setup=True)

        with self.assertRaises(RuntimeError):
            task.setup()

        self.assertFalse(task.is_setup())

    def test_loop(self):
        task = StubBoboTask(active=True)
        task.setup()

        task.loop()
        self.assertTrue(task.stub_loop)

    def test_loop_failure_cancelled(self):
        task = StubBoboTask(active=True)
        task.setup()
        task.cancel()

        with self.assertRaises(RuntimeError):
            task.loop()

        self.assertFalse(task.stub_loop)

    def test_loop_failure_not_setup(self):
        task = StubBoboTask(active=True)

        with self.assertRaises(RuntimeError):
            task.loop()

        self.assertFalse(task.stub_loop)

    def test_loop_failure_exception(self):
        task = StubBoboTask(active=True,
                            exception_loop=True)
        task.setup()

        with self.assertRaises(RuntimeError):
            task.loop()

        self.assertTrue(task.stub_loop)

    def test_loop_inactive_active(self):
        task = StubBoboTask(active=False)
        task.setup()

        task.loop()
        self.assertFalse(task.stub_loop)

        task.activate()
        task.loop()
        self.assertTrue(task.stub_loop)

    def test_cancel(self):
        task = StubBoboTask(active=True)
        self.assertFalse(task.is_cancelled())

        task.cancel()
        self.assertTrue(task.is_cancelled())

    def test_cancel_failure_exception(self):
        task = StubBoboTask(active=True,
                            exception_cancel=True)

        with self.assertRaises(RuntimeError):
            task.cancel()

        self.assertFalse(task.is_cancelled())
        self.assertTrue(task.stub_cancel)
