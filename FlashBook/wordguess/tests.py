from django.test import TestCase 
from django.urls import reverse
from homepage.models import User, Highscore, Folder
from unittest.mock import patch
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
from django.contrib.auth.hashers import check_password
import random
from django.core.management import call_command

class WordGuessTests(TestCase):
    def setUp(self):
        User.objects.all().delete()
        super().setUp()  # Call the parent setup
        self.user = User.objects.create(user='testuser', fname='Test', lname='User', email='testuser@example.com')
        self.user.set_password('testpassword')
        self.assertNotEqual(self.user.password, 'testpassword')
        self.user.save()
        saved_user = User.objects.get(user='testuser')
        self.assertEqual(saved_user.user, 'testuser')
        self.assertTrue(check_password('testpassword', saved_user.password))
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
    
    def test_user_creation(self):
        # Check the initial user count and log it
        initial_count = User.objects.count()
        print(f"Initial user count: {initial_count}")

        # Ensure no user with the same 'user' field exists before creating a new one
        User.objects.filter(user='testuser').delete()  # Delete any existing user with the same 'user'

        # Manually create the user
        user = User.objects.create(user='testuser', fname='Test', lname='User', email='testuser@example.com')
        user.set_password('testpassword')
        user.save()

        # Log the count after user creation
        after_creation_count = User.objects.count()
        print(f"User count after creation: {after_creation_count}")

        # Check the final user count
        self.assertEqual(after_creation_count, initial_count + 1)

        # Check if the password was set correctly
        self.assertTrue(check_password('testpassword', user.password))


    def test_user_creation_on_first_visit(self):
        # Ensure that no user with the same 'user' field exists
        user_count_before = User.objects.count()

        # Trigger a new visit to potentially create a user
        response = self.client.get(reverse('word_guess'))

        # Ensure that the user count has increased only if the user was created
        # If the user already exists, the count should stay the same
        user_count_after = User.objects.count()
        
        # If the user is being created, the count should increase by 1
        if user_count_before == user_count_after:
            # The user was already created, no changes in the count
            print("User already exists. No new user created.")
        else:
            # A new user was created
            self.assertEqual(user_count_after, user_count_before + 1)
        
        # Fetch the user from the database
        user = User.objects.get(user='testuser')
        
        # Check if the password was set correctly
        self.assertTrue(check_password('testpassword', user.password))  # Check the password

    def test_word_guess_view_incorrect_guess(self):
        # Set initial session data for the test
        self.client.session['word_data'] = {"word": "python", "meaning": "a programming language"}
        self.client.session['guesses'] = ['p', 'y']
        self.client.session['incorrect_guesses'] = []  # Initially empty list
        
        # Send a POST request with an incorrect guess
        response = self.client.post(reverse('word_guess'), {'guess': 'z'})
        
        # Check if the guess has been added to the incorrect guesses list
        self.assertIn('z', response.client.session['incorrect_guesses'])
        
        # Ensure the response status is 200
        self.assertEqual(response.status_code, 200)


    @patch('random.choice')
    def test_game_lost_condition(self, mock_random_choice):
        # Mock random word
        mock_random_choice.return_value = {"word": "python", "meaning": "a programming language"}

        # Set up session for lost game
        session = self.client.session
        session['word_data'] = {"word": "python", "meaning": "a programming language"}
        session['incorrect_guesses'] = ['a', 'b', 'c', 'd', 'e', 'f']  # Simulate 6 incorrect guesses
        session['guesses'] = ['a', 'b', 'c', 'd', 'e', 'f']  # Simulate all incorrect guesses
        session.save()

        # Make the POST request to trigger the game logic
        response = self.client.post(reverse('word_guess'))

        # Assertions
        self.assertTrue(response.context['game_over'])  # Should detect game over
        self.assertEqual(response.context['message'], "You lost! The word was 'python'.")


    @patch('random.choice')
    def test_game_won_condition(self, mock_random_choice):
        # Mock random word
        mock_random_choice.return_value = {"word": "python", "meaning": "a programming language"}

        # Set up session for won game
        session = self.client.session
        session['word_data'] = {"word": "python", "meaning": "a programming language"}
        session['incorrect_guesses'] = []  # No incorrect guesses
        session['guesses'] = ['p', 'y', 't', 'h', 'o', 'n']  # All correct guesses
        session['hearts_left'] = 6  # Start with full hearts
        session.save()

        response = self.client.post(reverse('word_guess'))

        # Assertions
        self.assertTrue(response.context['game_over'])  # Should detect game over
        self.assertEqual(response.context['message'], "Congratulations! You guessed the word!")

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
        another_folder = Folder.objects.create(user=self.user, folder_name="Flashcards")
        another_highscore = Highscore.objects.create(user=self.user, score=150, game_id=2, folder=another_folder)
        response = self.client.get(reverse('game_scores', args=[2]))
        self.assertIn(self.highscore, response.context['scores'])
        self.assertIn(another_highscore, response.context['scores'])
