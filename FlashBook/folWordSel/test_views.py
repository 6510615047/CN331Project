from django.test import TestCase, Client
from django.contrib.auth.models import User as UserBuiltIn
from homepage.models import *
from django.urls import reverse
import base64
from datetime import date
import json

class FolderTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(
            user_id=1,
            user='testuser',
            fname='Test',
            lname='User',
            email='testuser@example.com',
            password='testpassword'
        )

        self.user_built_in = UserBuiltIn.objects.create_user(
            username='testuser',
            password='testpassword',
            first_name='Test',
            last_name='User',
            email='testuser@example.com'
        )

        self.client = Client()
        
        login_url = reverse('login')
        response = self.client.get(login_url)
        csrf_token = response.cookies['csrftoken'].value
        
        response = self.client.post(
            login_url,
            {   
                'csrfmiddlewaretoken': csrf_token,
                'username': 'testuser',
                'password': 'testpassword'
            }
        )

        # Create initial folders for the user
        self.folder1 = Folder.objects.create(user=self.user, folder_name='Folder1')
        self.folder2 = Folder.objects.create(user=self.user, folder_name='Folder2')


    def test_folder_view(self):

        response = self.client.get(reverse('folder'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Folder1')
        self.assertTemplateUsed(response, 'folder.html')

    def test_add_folder(self):
        response = self.client.post(reverse('add_folder'), {'folder_name': 'NewFolder'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('folder'))
        self.assertTrue(Folder.objects.filter(user=self.user, folder_name='NewFolder').exists())

    def test_add_duplicate_folder(self):
        """Test adding a duplicate folder."""
        response = self.client.post(reverse('add_folder'), {'folder_name': 'Folder1'})
        self.assertRedirects(response, reverse('folder'))
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('A folder with this name already exists.' in str(m) for m in messages))

    def test_edit_folder(self):
        """Test editing an existing folder."""
        response = self.client.post(reverse('edit_folder', args=[self.folder1.folder_id]), {
            'action': 'edit',
            'folder_name': 'UpdatedFolder'
        })
        self.assertEqual(Folder.objects.get(user=self.user,folder_id=self.folder1.folder_id).folder_name, 'UpdatedFolder')
    
    def test_edit_duplicate_name_folder(self):
        """Test editing an existing folder."""
        response = self.client.post(reverse('edit_folder', args=[self.folder1.folder_id]), {
            'action': 'edit',
            'folder_name': 'Folder2'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('folder'))

    def test_delete_folder(self):
        """Test deleting an existing folder."""
        response = self.client.post(reverse('edit_folder', args=[self.folder1.folder_id]), {'action': 'delete'})
        self.assertFalse(Folder.objects.filter(user=self.user,folder_id=self.folder1.folder_id).exists())

    def test_folder_search_success(self):
        """Test searching for a folder."""
        response = self.client.get(reverse('search_folder') + '?query=Folder1')
        self.assertContains(response, 'Folder1')
        self.assertNotContains(response, 'Folder2')

    def test_folder_search_failure(self):
        """Test searching for a folder."""
        response = self.client.get(reverse('search_folder') + '?query=Folder3')
        self.assertNotContains(response, 'Folder1')
        self.assertNotContains(response, 'Folder2')

    def test_folder_search_empty(self):
        """Test searching for a folder."""
        response = self.client.get(reverse('search_folder') + '?query=')
        self.assertContains(response, 'Folder1')
        self.assertContains(response, 'Folder2')

class WordTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(
            user_id=1,
            user='testuser',
            fname='Test',
            lname='User',
            email='testuser@example.com',
            password='testpassword'
        )

        self.user_built_in = UserBuiltIn.objects.create_user(
            username='testuser',
            password='testpassword',
            first_name='Test',
            last_name='User',
            email='testuser@example.com'
        )

        self.client = Client()
        
        login_url = reverse('login')

        # Get the CSRF token first by making a GET request
        response = self.client.get(login_url)
        csrf_token = response.cookies['csrftoken'].value  # Extract the CSRF token

        # Now submit the POST request with the CSRF token
        response = self.client.post(
            login_url,
            {   
                'csrfmiddlewaretoken': csrf_token,
                'username': 'testuser',
                'password': 'testpassword'
            }
        )

        # Create initial folders and words
        self.folder = Folder.objects.create(user=self.user, folder_name='Folder')

        self.word1 = Word.objects.create(user=self.user, folder=self.folder,word='testword1',meaning='testmeaning1')
        self.word2 = Word.objects.create(user=self.user, folder=self.folder,word='testword2',meaning='testmeaning2')

    def test_word_view(self):
        response = self.client.get(reverse('word', args=[self.folder.folder_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testword1')
        self.assertContains(response, 'testword2')
        self.assertTemplateUsed(response, 'word.html')

    def test_add_word(self):
        response = self.client.post(reverse('add_word', args=[self.folder.folder_id]), {
            'action': 'add',
            'word_name': 'NewWord',
            'meaning': 'NewMeaning'
        })
        self.assertTrue(Word.objects.filter(user=self.user,folder=self.folder, word='NewWord').exists())

    def test_add_duplicate_word(self):
        response = self.client.post(reverse('add_word', args=[self.folder.folder_id]), {
            'action': 'add',
            'word_name': 'testword1',
            'meaning': 'testmeaning1'
        })
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('Word with this name already exists.' in str(m) for m in messages))

    def test_edit_word(self):
        response = self.client.post(reverse('edit_word', args=[self.folder.folder_id, self.word1.word_id]), {
            'action': 'edit',
            'word_name': 'testword3',
            'meaning': 'testmeaning3'
        })
        word = Word.objects.get(word_id=self.word1.word_id)
        self.assertEqual(word.word, 'testword3')
        self.assertEqual(word.meaning, 'testmeaning3')

    def test_edit_duplicate_name_word(self):
        response = self.client.post(reverse('edit_word', args=[self.folder.folder_id, self.word1.word_id]), {
            'action': 'edit',
            'word_name': 'testword2',
            'meaning': 'testmeaning2'
        })
        self.assertEqual(response.status_code, 200)

    def test_delete_word(self):
        """Test deleting a word in a folder."""
        response = self.client.post(reverse('edit_word', args=[self.folder.folder_id, self.word1.word_id]), {
            'action': 'delete'
        })
        self.assertFalse(Word.objects.filter(user=self.user,folder=self.folder,word=self.word1.word).exists())

    def test_search_word_success(self):
        """Test searching for a word."""
        response = self.client.get(reverse('search_word', args=[self.folder.folder_id]) + '?query=testword1')
        self.assertContains(response, 'testword1')
        self.assertNotContains(response, 'testword2')

    def test_search_word_failure(self):
        """Test searching for a word."""
        response = self.client.get(reverse('search_word', args=[self.folder.folder_id]) + '?query=testword3')
        self.assertNotContains(response, 'testword1')
        self.assertNotContains(response, 'testword2')

    def test_search_word_empty(self):
        """Test searching for a word."""
        response = self.client.get(reverse('search_word', args=[self.folder.folder_id]) + '?query=')
        self.assertContains(response, 'testword1')
        self.assertContains(response, 'testword2')

    def test_time_set_view(self):
        """Test loading of the timeSet page"""
        response = self.client.get(reverse('time_set', args=[self.folder.folder_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Set time")

    def test_select_game_view(self):
        """Test loading of the selectGame page"""
        response = self.client.get(reverse('select_game', args=[self.folder.folder_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select Game")  # Check that the page contains the phrase "Select Game"

    def test_back_button(self):
        """Test the functionality of the Back button"""
        response = self.client.get(reverse('mode_set', args=[self.folder.folder_id]))
        self.assertContains(response, '<button class="back-btn"')  # Check if the Back button is present in modeSet.html
        self.assertContains(response, 'onclick="goBack()"')  # Check if the Back button's onclick uses the goBack() function

    def test_select_game_buttons(self):
        """Test the functionality of the buttons on the selectGame page"""
        response = self.client.get(reverse('select_game', args=[self.folder.folder_id]))
        self.assertContains(response, 'timeSet')  # Check if the Flashcard button links to '/folder/timeSet'
        self.assertContains(response, 'modeSet')  # Check if the Wordguess button links to '/folder/modeSet'

class ScoreViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(
            user_id=1,
            user='testuser',
            fname='Test',
            lname='User',
            email='testuser@example.com',
            password='testpassword'
        )

        self.user_built_in = UserBuiltIn.objects.create_user(
            username='testuser',
            password='testpassword',
            first_name='Test',
            last_name='User',
            email='testuser@example.com'
        )

        self.client = Client()
        
        login_url = reverse('login')

        # Get the CSRF token first by making a GET request
        response = self.client.get(login_url)
        csrf_token = response.cookies['csrftoken'].value  # Extract the CSRF token

        # Now submit the POST request with the CSRF token
        response = self.client.post(
            login_url,
            {   
                'csrfmiddlewaretoken': csrf_token,
                'username': 'testuser',
                'password': 'testpassword'
            }
        )

        # Create test folders
        self.folder1 = Folder.objects.create(user=self.user, folder_name="Folder 1")
        self.folder2 = Folder.objects.create(user=self.user, folder_name="Folder 2")

        # Create test scores for different games
        self.game_1_score_1 = Highscore.objects.create(
            user=self.user, folder=self.folder1, game_id=1, play_time=1, score=100
        )
        self.game_1_score_2 = Highscore.objects.create(
            user=self.user, folder=self.folder1, game_id=1, play_time=2, score=150
        )

        self.game_2_score = Highscore.objects.create(
            user=self.user, folder=self.folder2, game_id=2, play_time=1, score=200
        )

        self.game_3_score = Highscore.objects.create(
            user=self.user, folder=self.folder2, game_id=3, play_time=1, score=250
        )

    def test_score_view_no_query(self):
        """Test the score view with no search query."""
        response = self.client.get(reverse('score'))
        self.assertEqual(response.status_code, 200)

        # Check if the graph is present in the response context
        self.assertIn('graph', response.context)
        self.assertIn('folders', response.context)
        self.assertEqual(len(response.context['folders']), 2)  # return both folders

        # Validate the graph data
        graph_data = response.context['graph']
        self.assertIsNotNone(graph_data)
        self.assertTrue(base64.b64decode(graph_data))  # Validate base64 data
        self.assertTrue(isinstance(graph_data, str))

    def test_score_view_with_query(self):
        """Test the score view with a search query."""
        response = self.client.get(reverse('score'), {'query': 'Folder 1'})
        self.assertEqual(response.status_code, 200)

        # Check filtered folders
        self.assertIn('folders', response.context)
        self.assertEqual(len(response.context['folders']), 1)  # Only "Folder 1" should match
        self.assertEqual(response.context['folders'][0].folder_name, "Folder 1")
        self.assertIsNotNone(response.context['graph'])

    def test_score_view_no_matching_query(self):
        """Test the score view with a query that doesn't match any folders."""
        response = self.client.get(reverse('score'), {'query': 'Nonexistent'})
        self.assertEqual(response.status_code, 200)

        # Check notification message
        self.assertIn('noti', response.context)
        self.assertEqual(
            response.context['noti'], "No scores found matching Nonexistent. Try another search term."
        )

        # Check folders returned
        self.assertIn('folders', response.context)
        self.assertEqual(len(response.context['folders']), 2)  # Should return all folders
        self.assertIsNotNone(response.context['graph'])

    def test_score_view_no_folders(self):
        """Test the score view when no folders exist."""
        Folder.objects.all().delete()  # Delete all folders

        response = self.client.get(reverse('score'))
        self.assertEqual(response.status_code, 200)

        # # Check that no graphs are returned
        self.assertNotIn('graph', response.context)
        self.assertNotIn('folders', response.context)

    def test_graph_generation(self):
        """Test graph generation with sample data."""
        response = self.client.get(reverse('score'))
        self.assertEqual(response.status_code, 200)

        # Check that graph is properly generated
        graph_data = response.context['graph']
        # Base64-encoded PNG files often start with this header
        self.assertTrue(graph_data.startswith('iVBORw0')) 
