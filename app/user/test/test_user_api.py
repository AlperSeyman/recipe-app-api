"""
Test for user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**kwargs):
    """Create and return new user."""
    User = get_user_model()
    user = User.objects.create_user(**kwargs)
    return user

class PublicUserApiTest(TestCase): # unauthenticated requests (registering a new user.)
    """Test the public features of the user API"""
    """Test the parts of the API that do NOT need a Token.
       Anyone on the internet can access these functions"""

    def setUp(self):
        """Create a fresh 'Fake Browser' (client) for every test."""
        self.client = APIClient()

    def  test_create_user_succes(self):
        """Test creating a user is successfull."""
        """Test the 'Registration' process.
        Check if a stranger can successfully create a new account.
        Check: 1. Status is 201. 2. Password is encrypted. 3. Password is hidden"""
        payload = {
            'email':'test@example.com',
            'password':'testpass123',
            'name':'Test User Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        """Test that two people cannot use the same email.
           If we try to create a user with an email that is already in the database,
           the system must return a 400 Error."""
        payload = {
            'email':'test@example.com',
            'password':'testpass123',
            'name': 'Test User Name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test error returned if password less than 5 char."""
        """Test the security rule for password length.
           If a user tries to use a very short password (like 'pw'),
           the Serializer must stop them and return a 400 Error."""
        payload = {
            'email':'test@example.com',
            'password':'pw',
            'name': 'Test User Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generrates token for valid credentials."""
        """Test the 'Login' process.
           When a user sends the correct Email and Password,
           does the system give them a secret Token (key)?"""
        user_details = {
            'name' : 'Test Name',
            'email' : 'test@example.com',
            'password' : 'test-user-password123',
        }
        create_user(**user_details)

        payload = {
            'email' : user_details['email'],
            'password' : user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        """Test that wrong passwords are rejected.
           If a user exists but provides the WRONG password,
           they must NOT get a token and must receive a 400 Error."""
        create_user(email='test@example.com', password='goodpass')

        payload = {
            'email' : 'test@example.com',
            'password' : 'badpass',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        """Test that empty passwords are rejected.
           If the user forgets to type a password, the system should not process the login."""
        payload = {'email':'test@example.com', 'password':''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        """Test the security 'Lock' on the Profile page.
           Try to visit the private 'Me' URL without being logged in.
           The system must return 401 Unauthorized (Access Denied)."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):

    def setUp(self):
        """It creates a real user in test database"""
        self.user = create_user(
            email='email@example.com',
            password='pass1234',
            name='Test Name',
        )
        """Opens a new, empty browser window for the test to use"""
        self.client = APIClient()
        """You are now logged in as the user we just created."""
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieve profile for logged in user."""
        res=self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'name':self.user.name, 'email':self.user.email,})

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the 'me' endpoint"""
        res=self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {
            'name':'Updated Name',
            'password':'newpassword1234',
        }
        res=self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)