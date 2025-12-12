"""
Test custom Django management commands.
"""

from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# Use @patch to replace the real Command.check method with a Mock object.
# This gives control over the database connection status during the test.
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTest(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_read(self, mocked_check):
        """Test waiting for database if database is ready."""
        # Tell the fake check function to immediately return True (Success).
        mocked_check.return_value = True

        # Run the command. It will get True and exit instantly.
        call_command('wait_for_db')

        # Check that the command called the fake check function exactly once
        # with the correct database arguments, proving it finished efficiently.
        mocked_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patch_sleep, mocked_check):
        """Test waiting for database when getting OperationalError."""
        mocked_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(mocked_check.call_count, 6)

        mocked_check.assert_called_with(databases=['default'])
