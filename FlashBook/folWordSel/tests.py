from django.test import TestCase
from django.urls import reverse

class WebPagesTests(TestCase):

    def test_folder_view(self):
        """Test loading of the folder page"""
        response = self.client.get(reverse("folder"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "folder.html")

    def test_word_view(self):
        """Test loading of the word page"""
        response = self.client.get(reverse('word'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "word.html")

    def test_time_set_view(self):
        """Test loading of the timeSet page"""
        response = self.client.get(reverse('time_set'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Set time")

    def test_select_game_view(self):
        """Test loading of the selectGame page"""
        response = self.client.get(reverse('select_game'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select Game")  # Check that the page contains the phrase "Select Game"

    def test_back_button(self):
        """Test the functionality of the Back button"""
        response = self.client.get(reverse('mode_set'))
        self.assertContains(response, '<button class="back-btn"')  # Check if the Back button is present in modeSet.html
        self.assertContains(response, 'onclick="goBack()"')  # Check if the Back button's onclick uses the goBack() function

    def test_select_game_buttons(self):
        """Test the functionality of the buttons on the selectGame page"""
        response = self.client.get(reverse('select_game'))
        self.assertContains(response, 'timeSet')  # Check if the Flashcard button links to '/folder/timeSet'
        self.assertContains(response, 'modeSet')  # Check if the Wordguess button links to '/folder/modeSet'


