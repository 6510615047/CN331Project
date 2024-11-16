from django.test import TestCase, Client
from django.contrib.auth.models import User
from homepage.models import *
from django.urls import reverse

class FolderTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(
            user_id=1, 
            user='testuser',
            fname='testfname',
            lname='testlname', 
            password='testpassword',
            email='testemail@test.com'
        )

        self.client = Client()

        # Create initial folders and words
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
            fname='testfname',
            lname='testlname', 
            password='testpassword',
            email='testemail@test.com'
        )

        self.client = Client()

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
        self.assertFalse(Word.objects.filter(word_id=self.word1.word_id).exists())

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