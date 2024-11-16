from django.test import TestCase 
from django.urls import reverse
from homepage.models import User, Highscore, Folder
from unittest.mock import patch
from wordguess.models import WordGuessGame
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
import random

class WordGuessViewTests(TestCase):

    def setUp(self):
        # Manually create the user (no need for create_user)
        self.user = User.objects.create(user='testuser', fname='Test', lname='User', email='testuser@example.com')
        self.user.set_password('testpassword')
        self.user.save()  # Save the user object to the database

        # Directly assign the user to the request
        self.client.force_login(self.user)  # Using force_login to bypass the login page

    def test_word_guess_view_authenticated(self):
        # Make a GET request to the word guess view
        response = self.client.get(reverse('word_guess'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Test if the session data is initialized correctly
        self.assertIn('word_data', response.context)
        self.assertIn('guesses', response.context)
        self.assertIn('incorrect_guesses', response.context)

    def test_word_guess_view_win_condition(self):
        # Make a POST request with a correct guess
        selected_word = random.choice([{"word": "python", "meaning": "ภาษาโปรแกรมมิ่งยอดนิยม"},
                                      {"word": "django", "meaning": "เฟรมเวิร์คสำหรับสร้างเว็บในภาษา Python"}])
        self.client.session['word_data'] = selected_word
        self.client.session['guesses'] = ['p', 'y', 't', 'h', 'o', 'n']

        response = self.client.post(reverse('word_guess'), {'guess': 'p'})
        
        # Check that the game is over and the win message appears
        self.assertContains(response, 'Congratulations! You guessed the word!')

    def test_word_guess_view_lose_condition(self):
        # Make a POST request with an incorrect guess
        selected_word = random.choice([{"word": "python", "meaning": "ภาษาโปรแกรมมิ่งยอดนิยม"},
                                      {"word": "django", "meaning": "เฟรมเวิร์คสำหรับสร้างเว็บในภาษา Python"}])
        self.client.session['word_data'] = selected_word
        self.client.session['incorrect_guesses'] = ['z', 'x', 'c', 'v', 'b', 'n']

        response = self.client.post(reverse('word_guess'), {'guess': 'p'})
        
        # Check that the game is over and the lose message appears
        self.assertContains(response, f"You lost! The word was '{selected_word['word']}'.")
        

class GameScoresViewTests(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create(user='testuser', fname='Test', lname='User', email='testuser@example.com')
        self.user.set_password('testpassword')
        self.user.save()

        # Create a Folder instance for the test user
        self.folder = Folder.objects.create(
            user=self.user,
            folder_name="Test Folder",  # Ensure folder_name is provided as it's required
        )

        # Create a Highscore instance for the user and game_id 2
        self.highscore = Highscore.objects.create(
            user=self.user,
            score=100,
            game_id=2,
            folder=self.folder,
        )

    @patch('homepage.views.Highscore.objects.filter')  # Patch the filter method
    def test_game_scores_view_authenticated(self, mock_filter):
        # Mock the filter to return the Highscore instance we created
        mock_filter.return_value = [self.highscore]

        # Log in as the test user
        self.client.login(user='testuser', password='testpassword')

        # Send a GET request to the game scores view
        response = self.client.get(reverse('game_scores', args=[2]))

        # Assert that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the scores are present in the response context
        self.assertIn('scores', response.context)

        # Ensure the score in the context matches the mocked score
        self.assertEqual(response.context['scores'][0].score, self.highscore.score)
