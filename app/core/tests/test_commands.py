"""
Test custom Django management commands.
"""

# used to create fake objects (Mocks)
from unittest.mock import patch 

from psycopg2 import OperationalError as Pyscopg2Error

# Executes custom management command
from django.core.management import call_command

# The error the command is looking for 
from django.db.utils import OperationalError

# Base class for tests that don't need a real database
from django.test import SimpleTestCase  

# use @patch to replace the real Command class with a Mock object
# control over the database connection status during the test
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTest(SimpleTestCase):
    """Test commands."""
    
    # The 'mocked_check' parameter receives the fake object created by @patch
    def test_wait_for_db_read(self, mocked_check):
        """Test waiting for database if database is ready."""
        
        # tell the fake check function to immediately return True (Success).
        mocked_check.return_value = True
        
        # it will get True and exit instantly.
        call_command('wait_for_db')
        
        # Check that the command called the fake check function exactly once 
        # with the correct database arguments, proving it finished efficiently.
        mocked_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patch_sleep, mocked_check):
        """Test waiting for database when getting OperationalError."""
        
        mocked_check.side_effect = [Pyscopg2Error] * 2 + [OperationalError] * 3 + [True]
        
        call_command('wait_for_db')
        
        self.assertEqual(mocked_check.call_count, 6)
        mocked_check.assert_called_with(databases=['default'])