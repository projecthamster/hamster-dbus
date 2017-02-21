import pytest

from hamster_dbus import helpers


class TestRepresentCategory(object):
    @pytest.mark.parametrize(('legacy_mode', 'expectation'), [
        (True, 'unsorted category'),
        (False, ''),
    ])
    def test_represent_category_None(self, legacy_mode, expectation):
        """Make sure that representation of ``Ǹone`` categories works dependend on legacy mode."""
        result = helpers._represent_category(None, legacy_mode=legacy_mode)
        assert result == expectation
