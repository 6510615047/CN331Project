# tests/test_views.py
from django.test import TestCase
from django.urls import reverse
from homepage.models import User, Folder, Word, Highscore
from flashcard.views import next_word

class FlashcardViewsTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create(
            user="wern", fname="Wern", lname="Test", email="wern@example.com"
        )
        # Create a folder for the user
        self.folder = Folder.objects.create(
            user=self.user, folder_name="Test Folder", folder_id=1
        )
        # Create some words for the flashcards
        Word.objects.create(user=self.user, folder=self.folder, word_id=1, word="Test", meaning="A test word")
        Word.objects.create(user=self.user, folder=self.folder, word_id=2, word="Example", meaning="An example word")
        
        # Create a highscore for the user and folder
        Highscore.objects.create(user=self.user, folder=self.folder, game_id=1, score=0, play_time=1)

    def test_flashcard_view(self):
        """Test the flashcard view returns the correct word and score"""
        response = self.client.get(reverse('flashcard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test")  # Check if word is displayed
        self.assertContains(response, "Score")  # Check if score is displayed

    def test_correct_answer_view(self):
        """Test that the score is incremented when the correct answer is selected"""
        response = self.client.get(reverse('correct_answer'))
        self.assertEqual(response.status_code, 302)  # Should redirect to flashcard page
        # Fetch the updated highscore
        highscore = Highscore.objects.get(user=self.user, folder=self.folder, game_id=1)
        self.assertEqual(highscore.score, 1)  # Score should be incremented by 1

    def test_wrong_answer_view(self):
        """Test that the score is not changed when the wrong answer is selected"""
        response = self.client.get(reverse('wrong_answer'))
        self.assertEqual(response.status_code, 302)  # Should redirect to flashcard page
        # Fetch the updated highscore
        highscore = Highscore.objects.get(user=self.user, folder=self.folder, game_id=1)
        self.assertEqual(highscore.score, 0)  # Score should remain the same

    def test_next_word_view(self):
        """Test that the next word is shown when the next word button is pressed"""
        response = self.client.get(reverse('next_word'))
        self.assertEqual(response.status_code, 302)  # Should redirect to flashcard page
        
        # Check if the next word is set correctly in the session
        self.assertEqual(self.client.session.get('current_word_id'), 2)

    def test_no_next_word_view(self):
        # Set up the current_word_id in the session
        session = self.client.session
        session['current_word_id'] = 2  # Set to the last word's word_id
        session.save()  # Save the session

        # Simulate a request to the 'next_word' view
        response = self.client.get(reverse('next_word'))

        # Verify the response
        self.assertEqual(response.status_code, 302)  # Expect a redirect (to 'flashcard')
        self.assertEqual(self.client.session['current_word_id'], 1)  # Should cycle back to the first word

    def test_finish_view(self):
        """Test the finish page"""
        response = self.client.get(reverse('finish'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finish.html')  # Check if finish template is used
    

