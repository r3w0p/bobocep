import unittest

from bobocep.decider.versions.run_version import RunVersion


class TestRunVersion(unittest.TestCase):

    def test_list_to_version(self):
        strlist = ['abc', 'def']

        self.assertListEqual(strlist,
                             RunVersion.list_to_version(strlist)._levels)

    def test_list_to_version_str(self):
        strlist = ['abc', 'def']

        self.assertEqual('abc.def',
                         RunVersion.list_to_version_str(strlist))

    def test_str_to_version(self):
        strlist = ['abc', 'def']
        strver = 'abc.def'

        self.assertListEqual(strlist,
                             RunVersion.str_to_version(strver)._levels)

    def test_constructor_no_existing(self):
        version = RunVersion()
        self.assertListEqual([], version._levels)

    def test_constructor_existing(self):
        existing = RunVersion()
        existing.add_level('abc')

        version = RunVersion(parent_version=existing)
        self.assertListEqual([['abc']], version._levels)

    def test_add_level(self):
        version = RunVersion()

        version.add_level('abc')
        self.assertListEqual([['abc']], version._levels)

        version.add_level('def')
        self.assertListEqual([['abc'], ['def']], version._levels)

    def test_increment_level(self):
        version = RunVersion()

        with self.assertRaises(RuntimeError):
            version.increment_level('abc')

        version.add_level('abc')
        version.increment_level('def')

        self.assertListEqual([['abc', 'def']], version._levels)

        version.add_level('ghi')
        version.increment_level('jkl')

        self.assertListEqual([['abc', 'def'], ['ghi', 'jkl']], version._levels)

    def test_size(self):
        version = RunVersion()

        version.add_level('abc')
        self.assertEqual(1, version.size())

        version.add_level('def')
        self.assertEqual(2, version.size())

        version.increment_level('ghi')
        self.assertEqual(2, version.size())

    def test_size_level(self):
        version = RunVersion()

        version.add_level('abc')
        self.assertEqual(1, version.size_level(0))
        self.assertEqual(1, version.size_level())

        version.add_level('def')
        self.assertEqual(1, version.size_level(1))
        self.assertEqual(1, version.size_level())

        version.increment_level('ghi')
        self.assertEqual(2, version.size_level(1))
        self.assertEqual(2, version.size_level())

    def test_clear_all_levels(self):
        version = RunVersion()

        version.add_level('abc')
        version.add_level('def')
        version.add_level('ghi')

        self.assertEqual(3, version.size())

        version.remove_all_levels()
        self.assertEqual(0, version.size())

    def test_get_version_as_list(self):
        version = RunVersion()

        self.assertListEqual([],
                             version.get_version_as_list())

        version.add_level('abc')

        self.assertListEqual(['abc'],
                             version.get_version_as_list())

        version.add_level('def')

        self.assertListEqual(['abc', 'def'],
                             version.get_version_as_list())

        version.increment_level('ghi')

        self.assertListEqual(['abc', 'ghi'],
                             version.get_version_as_list())

    def test_get_version_as_str(self):
        version = RunVersion()

        self.assertEqual('',
                         version.get_version_as_str())

        version.add_level('abc')

        self.assertEqual('abc',
                         version.get_version_as_str())

        version.add_level('def')

        self.assertEqual('abc.def',
                         version.get_version_as_str())

        version.increment_level('ghi')

        self.assertEqual('abc.ghi',
                         version.get_version_as_str())

    def test_get_previous_version_as_list(self):
        version = RunVersion()

        # No levels or increments exist yet
        with self.assertRaises(RuntimeError):
            version.get_previous_version_as_list(
                decrease_level=0,
                decrease_incr=0
            )

        # Add levels and increments
        version.add_level('abc')
        version.add_level('def')
        version.increment_level('ghi')

        # Check current version is correct
        self.assertListEqual(['abc', 'ghi'],
                             version.get_version_as_list())

        # Go back one increment
        self.assertListEqual(['abc', 'def'],
                             version.get_previous_version_as_list(
                                 decrease_level=0,
                                 decrease_incr=1
                             ))

        # No more previous increments in current level
        with self.assertRaises(RuntimeError):
            version.get_previous_version_as_list(
                decrease_level=0,
                decrease_incr=2
            )

        # Go back one level
        self.assertListEqual(['abc'],
                             version.get_previous_version_as_list(
                                 decrease_level=1,
                                 decrease_incr=0
                             ))

        # No more previous increments in previous level
        with self.assertRaises(RuntimeError):
            version.get_previous_version_as_list(
                decrease_level=1,
                decrease_incr=1
            )

        # No more previous levels
        with self.assertRaises(RuntimeError):
            version.get_previous_version_as_list(
                decrease_level=2,
                decrease_incr=0
            )

    def test_get_previous_version_as_str(self):
        version = RunVersion()

        # No levels or increments exist yet
        self.assertEqual("", version.get_previous_version_as_str(
            decrease_level=0,
            decrease_incr=0))

        # Add levels and increments
        version.add_level('abc')
        version.add_level('def')
        version.increment_level('ghi')

        # Check current version is correct
        self.assertEqual('abc.ghi',
                         version.get_version_as_str())

        # Go back one increment
        self.assertEqual('abc.def',
                         version.get_previous_version_as_str(
                             decrease_level=0,
                             decrease_incr=1
                         ))

        # No more previous increments in current level
        self.assertIsNone(version.get_previous_version_as_str(decrease_level=0,
                                                              decrease_incr=2))

        # Go back one level
        self.assertEqual('abc',
                         version.get_previous_version_as_str(
                             decrease_level=1,
                             decrease_incr=0
                         ))

        # No more previous increments in previous level
        self.assertIsNone(version.get_previous_version_as_str(decrease_level=1,
                                                              decrease_incr=1))

        # No more previous levels
        self.assertIsNone(version.get_previous_version_as_str(decrease_level=2,
                                                              decrease_incr=0))
