from abc import ABC, abstractmethod
from threading import RLock


class BoboTask(ABC):
    """A task that is scheduled to repeat indefinitely until cancelled.

    :param active: Whether task should start in an active state,
                   defaults to True.
    :type active: bool, optional
    """

    def __init__(self, active: bool = True) -> None:
        super().__init__()

        self._is_active = active
        self._is_cancelled = False
        self._is_setup = False
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

    def activate(self) -> None:
        """Activates task."""

        with self._lock:
            self._is_active = True

    def deactivate(self) -> None:
        """Deactivates task."""

        with self._lock:
            self._is_active = False

    def is_active(self) -> bool:
        """
        :return: True if the task is current active, False otherwise.
        """

        with self._lock:
            return self._is_active

    def cancel(self) -> None:
        """Cancel the task."""

        with self._lock:
            if not self._is_cancelled:
                self._cancel()
                self._is_cancelled = True

    def is_cancelled(self) -> bool:
        """
        :return: True if the task has been cancelled, False otherwise.
        """

        with self._lock:
            return self._is_cancelled

    def setup(self) -> None:
        """Perform initial setup. It can only be performed once, and must be
        performed before loop functionality can occur.

        :raises RuntimeError: Task has already been cancelled.
        :raises RuntimeError: Setup has already been performed.
        :raises RuntimeError: Exception raised during setup.
        """

        with self._lock:
            if self._is_cancelled:
                raise RuntimeError("Task has already been cancelled.")

            if self._is_setup:
                raise RuntimeError("Setup has already been performed.")

            try:
                self._setup()
            except Exception as e:
                raise RuntimeError("Exception raised during setup: {}."
                                   .format(e))
            self._is_setup = True

    def is_setup(self) -> bool:
        """
        :return: True if task has successfully set up, False otherwise.
        """

        with self._lock:
            return self._is_setup

    def loop(self) -> None:
        """Perform primary task loop. The task must not be cancelled, and
        setup must have already occurred.

        :raises RuntimeError: Task has already been cancelled.
        :raises RuntimeError: Setup must be performed before using loop.
        :raises RuntimeError: Exception raised during loop.
        """

        with self._lock:
            if self._is_cancelled:
                raise RuntimeError("Task has already been cancelled.")

            if not self._is_setup:
                raise RuntimeError(
                    "Setup must be performed before using loop.")

            if self._is_active:
                try:
                    self._loop()
                except Exception as e:
                    raise RuntimeError("Exception raised during loop: {}."
                                       .format(e))
