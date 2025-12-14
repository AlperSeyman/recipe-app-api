"""
Test for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model  # Return the active User model (default or custom).


class ModelTest(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is sucessful."""
        User = get_user_model()
        email = "test@example.com"
        password = "testpass123"
        user = User.objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password)) # Removed the password variable from the check

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'test2@example.com'], # Changed to lowercase 'test2' for correct normalization
            ['TEST3@EXAMPLE.COM', 'test3@example.com'], # Changed to lowercase 'test3' for correct normalization
            ['test4@example.com', 'test4@example.com'],
        ]
        for email, expected_email in sample_emails:
            User = get_user_model()
            user = User.objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser"""
        User = get_user_model()
        email = "admin@example.com" # Changed email to avoid potential conflict with previous tests
        password = "testpass123"
        user = User.objects.create_superuser(
            email=email,
            password=password,
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        # Added a check for is_staff, which is part of superuser creation
        self.assertTrue(user.is_staff)