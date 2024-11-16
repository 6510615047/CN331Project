from django.test import TestCase 
from django.urls import reverse
from homepage.models import User, Highscore, Folder
from unittest.mock import patch
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
from django.contrib.auth.hashers import check_password
import random

class WordGuessTests(TestCase):

    def setUp(self):
        # Create test user
        self.user = User.objects.create(user='testuser', fname='Test', lname='User', email='testuser@example.com')

        # Set password using the set_password method
        self.user.set_password('testpassword')

        # Ensure that the password has been hashed (this checks the set_password method functionality)
        self.assertNotEqual(self.user.password, 'testpassword')  # The password should not be plain text

        # Save the user object
        self.user.save()

        # Ensure the user is saved in the database
        saved_user = User.objects.get(user='testuser')
        self.assertEqual(saved_user.user, 'testuser')  # Ensure the user data is saved correctly

        # Verify that the password was hashed in the database
        self.assertTrue(check_password('testpassword', saved_user.password))  # Check password directly using check_password

        # Log the user in
        self.client.login(username='testuser', password='testpassword')

    @patch('random.choice')
    def test_word_guess_view_initialization(self, mock_random_choice):
        # Mock the word selection
        mock_random_choice.return_value = {"word": "python", "meaning": "a programming language"}
        
        # Send a GET request to initialize the game
        response = self.client.get(reverse('word_guess'))
        
        # Ensure the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check if word_data is in session
        self.assertIn('word_data', response.client.session)
        self.assertEqual(response.client.session['word_data']['word'], "python")

    def test_word_guess_view_post_guess(self):
        # Set initial session data for the test
        self.client.session['word_data'] = {"word": "python", "meaning": "a programming language"}
        self.client.session['guesses'] = ['p', 'y']
        self.client.session['incorrect_guesses'] = ['z']
        
        # Send a POST request with a guess
        response = self.client.post(reverse('word_guess'), {'guess': 't'})
        
        # Check if the guess has been added to the session
        self.assertIn('t', response.client.session['guesses'])
        self.assertEqual(response.status_code, 200)

    def test_word_guess_view_game_reset(self):
        # Set initial session data
        self.client.session['word_data'] = {"word": "python", "meaning": "a programming language"}
        
        # Simulate game reset by sending a POST request with the reset flag
        response = self.client.post(reverse('word_guess'), {'reset': 'true'})
        
        # Check if session is flushed
        self.assertNotIn('word_data', response.client.session)
        self.assertEqual(response.status_code, 302)  # Expect a redirect after reset

    def test_user_creation_on_first_visit(self):
        # Ensure that the user does not exist before the test
        user_count = User.objects.count()
        
        # Trigger the word_guess_view and ensure no new user is created
        response = self.client.get(reverse('word_guess'))
        
        # Check that the user count has not changed, since the user already exists
        self.assertEqual(User.objects.count(), user_count)  # No new user should be created
        
        # Fetch the user from the database
        user = User.objects.get(user='testuser')

        # Check if the password is correct using Django's check_password function
        self.assertTrue(check_password('testpassword', user.password))  # Check password directly

class GameScoresViewTests(TestCase):

    def setUp(self):
        # Create test user and folder
        self.user = User.objects.create(user='testuser', fname='Test', lname='User', email='testuser@example.com')
        self.user.set_password('testpassword')
        self.user.save()
        
        self.folder = Folder.objects.create(user=self.user, folder_name="WordGuess")
        
        # Create highscore data for the test user
        self.highscore = Highscore.objects.create(user=self.user, score=100, game_id=2, folder=self.folder)
        
        # Log the user in
        self.client.login(username='testuser', password='testpassword')  # Corrected login

    def test_game_scores_view_authenticated(self):
        # Send GET request to the game_scores_view
        response = self.client.get(reverse('game_scores', args=[2]))
        
        # Ensure the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check if the scores are present in the response context
        self.assertIn('scores', response.context)
        
        # Check if the score matches the expected value
        self.assertEqual(response.context['scores'][0].score, self.highscore.score)

    def test_multiple_scores_per_user(self):
        # Create another score for the user
        another_folder = Folder.objects.create(user=self.user, folder_name="Flashcards")
        another_highscore = Highscore.objects.create(user=self.user, score=150, game_id=2, folder=another_folder)
        
        response = self.client.get(reverse('game_scores', args=[2]))
        
        # Ensure both scores are in the context
        self.assertIn(self.highscore, response.context['scores'])
        self.assertIn(another_highscore, response.context['scores'])
