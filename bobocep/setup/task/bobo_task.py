from abc import abstractmethod
from threading import RLock


class BoboTask:
    """A task that is scheduled to repeat indefinitely until cancelled."""

    def __init__(self) -> None:
        super().__init__()

        self._setup_done = False
        self._cancelled = False
        self._lock = RLock()

    @abstractmethod
    def _setup(self) -> None:
        """"""

    @abstractmethod
    def _loop(self) -> None:
        """"""

    @abstractmethod
    def _cancel(self) -> None:
        """"""

    def setup(self) -> None:
        """Perform initial setup. It can only be performed once, and must be
        performed before loop functionality can occur.

        :raises RuntimeError: Task has already been cancelled.
        :raises RuntimeError: Setup has already been performed.
        :raises RuntimeError: Exception raised during setup.
        """

        with self._lock:
            if self._cancelled:
                raise RuntimeError("Task has already been cancelled.")

            if self._setup_done:
                raise RuntimeError("Setup has already been performed.")

            try:
                self._setup()
            except Exception as e:
                raise RuntimeError("Exception raised during setup: {}."
                                   .format(e))
            self._setup_done = True

    def loop(self) -> None:
        """Perform primary task loop. The task must not be cancelled, and
        setup must have already occurred.

        :raises RuntimeError: Task has already been cancelled.
        :raises RuntimeError: Setup must be performed before using loop.
        :raises RuntimeError: Exception raised during loop.
        """

        with self._lock:
            if self._cancelled:
                raise RuntimeError("Task has already been cancelled.")

            if not self._setup_done:
                raise RuntimeError(
                    "Setup must be performed before using loop.")

            try:
                self._loop()
            except Exception as e:
                raise RuntimeError("Exception raised during loop: {}."
                                   .format(e))

    def cancel(self) -> None:
        """Cancel the task. This will prevent setup and loop from being
        called.

        :raises RuntimeError: Task has already been cancelled.
        :raises RuntimeError: Exception raised during cancel.
        """

        with self._lock:
            if self._cancelled:
                raise RuntimeError("Task has already been cancelled.")

            try:
                self._cancel()
            except Exception as e:
                raise RuntimeError("Exception raised during cancel: {}."
                                   .format(e))

            self._cancelled = True

    def is_cancelled(self) -> bool:
        """
        :return: True if the task has been cancelled, False otherwise.
        """

        with self._lock:
            return self._cancelled
