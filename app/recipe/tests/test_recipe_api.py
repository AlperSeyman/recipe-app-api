"""
Test for recipe APIs.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse('recipe:recipe-list')

def create_recipe(user, **kwargs):
    """Create and return a sample recipe"""
    default = {
        'title':'Sample recipe title',
        'time_minutes':22,
        'price':Decimal('5.50'),
        'description':'Sample description',
        'link':'https://example.com/recipe.pdf'
    }
    default.update(kwargs)

    recipe = Recipe.objects.create(user=user,**default)
    return recipe

class PublicRecipeAPITest(TestCase):
    """Test unauthenticated API request."""

    def setUp(self):
        """Opens a new, empty browser window for the test to use"""
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
