from copy import copy
from typing import List


class RunVersion:
    """
    The current version of a run, using the identification scheme of the
    Shared Versioned Match Buffer, as proposed by Agrawal et al. (2008)
    in their paper "Efficient Pattern Matching over Event Streams".

    :param parent_version: The parent version. If provided, the new version
                           will copy the parent version's levels.
                           Defaults to None.
    :type parent_version: RunVersion
    """

    _DELIMITER = "."

    def __init__(self, parent_version: 'RunVersion' = None) -> None:
        super().__init__()

        self._levels = [] if parent_version is None \
            else copy(parent_version._levels)

    @staticmethod
    def list_to_version(version_list: List[str]) -> 'RunVersion':
        """
        Converts a list of strings into a RunVersion instance, where each
        string of the list becomes a level in the RunVersion instance, in list
        order.

        :param version_list: A list of strings.
        :type version_list: List[str]

        :return: A new RunVersion instance.
        """

        run = RunVersion()
        run._levels = version_list
        return run

    @staticmethod
    def list_to_version_str(str_list: List[str]) -> str:
        """
        Converts a list of strings into a valid version string by joining
        each string in the list by the delimeter ".".

        :param str_list: A list of strings.
        :type str_list: List[str]

        :return: A valid version string.
        """

        return RunVersion._DELIMITER.join(str_list)

    @staticmethod
    def str_to_version(version_str: str) -> 'RunVersion':
        """
        Converts a version string into a RunVersion instance by splitting the
        string by the delimiter "." and making each split a level in the new
        instance.

        :param version_str: The version string.
        :type version_str: str

        :return: A new RunVersion instance.
        """

        run = RunVersion()
        run._levels = version_str.split(RunVersion._DELIMITER)
        return run

    def add_level(self, level: str) -> None:
        """
        Adds a new level to the version.

        :param level: The level name.
        :type level: str
        """

        self._levels.append([level])

    def increment_level(self, increment: str) -> None:
        """
        Increments the current level.

        :param increment: The increment name.
        :type increment: str

        :raises RuntimeError: Attempting to increment when there are no levels.
        """

        if len(self._levels) == 0:
            raise RuntimeError("Cannot increment. No levels found.")

        self._levels[-1].append(increment)

    def size(self) -> int:
        """
        :return: The number of levels.
        """

        return len(self._levels)

    def size_level(self, index: int = -1):
        """
        :param index: The index of the level, defaults to the latest level.
        :type index: int, optional

        :return: The number of increments in at a given level.
        """

        return len(self._levels[index])

    def remove_all_levels(self) -> None:
        """
        Removes all levels from the version.
        """

        self._levels = []

    def get_version_as_list(self) -> List[str]:
        """
        :return: The latest version as a list of strings, where each string
                 is the latest increment of the given level.
        """

        return [level[-1] for level in self._levels]

    def get_version_as_str(self) -> str:
        """
        :return: The latest version as a string, where each level is the latest
                 increment of the given level, separated with the delimeter
                 ".", for example, "a.b.c".
                 If there are no levels, it returns an empty string.
        """

        if len(self._levels) == 0:
            return ""

        return RunVersion._DELIMITER.join(
            [level[-1] for level in self._levels])

    def get_previous_version_as_list(self,
                                     decrease_level: int,
                                     decrease_incr: int) -> List[str]:
        """
        Gets a previous version of the run version as a list of strings.

        :param decrease_level: How many levels to decrease by.
                               For example, if there are 5 levels, a
                               decrease_level of 2 will go back to level 3.
        :type decrease_level: int

        :param decrease_incr: How many increments of a level to decrease by.
        :type decrease_incr: int

        :raises RuntimeError: Decreasing beyond the number of levels.
        :raises RuntimeError: Decreasing beyond the number of increments in
                              the chosen level.

        :return: The previous version as a list.
        """

        index_level = len(self._levels) - decrease_level - 1

        if not (0 <= index_level < len(self._levels)):
            raise RuntimeError("Level decrease is greater than the number of "
                               "levels. Version has {} levels, decrease is {}."
                               .format(len(self._levels), decrease_level))

        index_incr = len(self._levels[index_level]) - decrease_incr - 1

        if not (0 <= index_incr < len(self._levels[index_level])):
            raise RuntimeError("Increment decrease is greater than the number "
                               "of increments in level {}. "
                               "Level has {} increments, decrease is {}."
                               .format(index_level + 1,
                                       len(self._levels[index_level]),
                                       decrease_incr))

        version = [level[-1] for level in self._levels[:index_level]]
        version.append(self._levels[index_level][index_incr])

        return version

    def get_previous_version_as_str(self,
                                    decrease_level: int,
                                    decrease_incr: int,
                                    default=None) -> str:
        """
        Gets a previous version of the run version as a string, delimited by
        ".".

        :param decrease_level: How many levels to decrease by.
                               For example, if there are 5 levels, a
                               decrease_level of 2 will go back to level 3.
        :type decrease_level: int

        :param decrease_incr: How many increments of a level to decrease by.
        :type decrease_incr: int

        :param default: The default value to return if a version string fails
                        to be generated, defaults to None.
        :type default: any, optional

        :return: The previous version as a string delimited by ".".
                 If there are no levels, it returns an empty string.
        """

        if len(self._levels) == 0:
            return ""

        try:
            return RunVersion._DELIMITER.join(
                self.get_previous_version_as_list(decrease_level,
                                                  decrease_incr))
        except RuntimeError:
            return default
