"""
Django command to wait for the database to be available.
"""
import time

from django.db.utils import OperationalError

from psycopg2 import OperationalError as Pyscopg2Error
from django.core.management.base import BaseCommand  # create custom command.


class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *arg, **options):
        """Entry point for command"""

        self.stdout.write('Waiting for database....')
        
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Pyscopg2Error, OperationalError):
                self.stdout.write('Database unavaliable, waiting  1 second....')
                time.sleep(1)
        
        self.stdout.write(self.style.SUCCESS('Database available'))