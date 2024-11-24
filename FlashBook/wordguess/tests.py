from django.test import TestCase, Client
from homepage.models import User, Folder, Word, Highscore
from django.contrib.auth.models import User as UserBuiltIn
from django.urls import reverse

class WordGuessViewTests(TestCase):
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

        # Create a folder for the user
        self.folder = Folder.objects.create(user=self.user, folder_name='Folder1')
        
        # Create some words for the flashcards
        self.word1 = Word.objects.create(user=self.user, folder=self.folder,word='TESTWORD1',meaning='testmeaning1')
        self.word2 = Word.objects.create(user=self.user, folder=self.folder,word='TESTword2',meaning='testmeaning2')
        self.word2 = Word.objects.create(user=self.user, folder=self.folder,word='testword3',meaning='testmeaning3')
        
        # Create a highscore for the user and folder
        self.highscore = Highscore.objects.create(user=self.user, folder=self.folder, game_id=2, score=0, play_time=1)

    def test_initial_easy_mode(self):
        response = self.client.get(reverse('wordguess', args=[self.folder.folder_id]), {'difficulty': 'easy'})
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        word = Word.objects.get(word_id=session['word_id'])
        guesses = session['guesses']
        self.assertGreaterEqual(len(guesses), len(word.word) // 2)
        self.assertEqual(session['hearts_left'], 6)

    def test_initial_normal_mode(self):
        response = self.client.get(reverse('wordguess', args=[self.folder.folder_id]), {'difficulty': 'normal'})
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        word = Word.objects.get(word_id=session['word_id'])
        guesses = session['guesses']
        self.assertGreaterEqual(len(guesses), len(word.word) // 4)
        self.assertEqual(session['hearts_left'], 6)

    def test_initial_hard_mode(self):
        response = self.client.get(reverse('wordguess', args=[self.folder.folder_id]), {'difficulty': 'hard'})
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertEqual(len(session['guesses']), 0)
        self.assertEqual(session['hearts_left'], 4)

    def test_correct_guess(self):
        response = self.client.get(reverse('wordguess', args=[self.folder.folder_id]))
        session = self.client.session
        word = Word.objects.get(word_id=session['word_id'])
        correct_letter = word.word[0].lower()

        response = self.client.post(reverse('wordguess', args=[self.folder.folder_id]), {'guess': correct_letter})
        session = self.client.session
        self.assertEqual(response.status_code, 200)
        self.assertIn(correct_letter, session['guesses'])
        self.assertEqual(session['hearts_left'], 6)

    def test_incorrect_guess(self):
        response = self.client.get(reverse('wordguess', args=[self.folder.folder_id]))
        session = self.client.session
        word = Word.objects.get(word_id=session['word_id'])
        incorrect_letter = 'z'
        while incorrect_letter in word.word.lower():
            incorrect_letter = chr(ord(incorrect_letter) + 1)

        response = self.client.post(reverse('wordguess', args=[self.folder.folder_id]), {'guess': incorrect_letter})
        session = self.client.session
        self.assertEqual(response.status_code, 200)
        self.assertIn(incorrect_letter, session['guesses'])
        self.assertEqual(session['hearts_left'], 5)

    def test_game_end_success(self):
        response = self.client.get(reverse('wordguess', args=[self.folder.folder_id]))
        session = self.client.session
        hearts_left = session.get('hearts_left', 6)
        word = Word.objects.get(word_id=session['word_id'])
        highscore = Highscore.objects.filter(user=self.user, folder=self.folder, game_id=2).first()
        guesses = session.get('guesses',[])
        display_word = response.context.get('display_word')

        while hearts_left > 0 and "_" in display_word:  # "_ in word.word" checks if there are blanks
            # Pick a valid letter (adjust the logic as needed)
            for char in "abcdefghijklmnopqrstuvwxyz0123456789":
                if char not in guesses:
                    guesses.append(char)  # Add guess
                    break
            
            # Update session with new guess
            session['guesses'] = guesses
            session.save()  # Save session explicitly

            # Post the guess and get response
            response = self.client.post(reverse('wordguess', args=[self.folder.folder_id]), {'guess': guesses[-1]})

            # Re-fetch session variables
            session = self.client.session
            hearts_left = session.get('hearts_left', 6)
            display_word = response.context.get('display_word')

        session = self.client.session
        game_end = session.get('game_end')
        print(f"Game End Status: {game_end}")  # Debugging line
        print(f"Remaining Hearts: {session.get('hearts_left')}") 
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(session.get('word_id'))
        self.assertContains(response, "Congratulations! You guessed the word!")
        self.assertEqual(highscore.score, 1)

    def test_game_end_failure(self):
        response = self.client.get(reverse('wordguess', args=[self.folder.folder_id]))
        session = self.client.session
        hearts_left = session.get('hearts_left', 6)
        word = Word.objects.get(word_id=session['word_id'])
        highscore = Highscore.objects.filter(user=self.user, folder=self.folder, game_id=2).first()
        guesses = session.get('guesses',[])
        display_word = response.context.get('display_word')

        while hearts_left > 0 and "_" in display_word:  # "_ in word.word" checks if there are blanks
            # Pick a valid letter (adjust the logic as needed)
            for char in "abcdefghijklmnopqrstuvwxyz0123456789":
                if char not in guesses:
                    guesses.append(char)  # Add guess
                    break
            
            # Update session with new guess
            session['guesses'] = guesses
            session.save()  # Save session explicitly

            # Post the guess and get response
            response = self.client.post(reverse('wordguess', args=[self.folder.folder_id]), {'guess': guesses[-1]})

            # Re-fetch session variables
            session = self.client.session
            hearts_left = session.get('hearts_left', 6)
            display_word = response.context.get('display_word')
        
        session = self.client.session
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(session.get('word_id'))
        self.assertContains(response, "You lost!")
        self.assertEqual(highscore.score, 0)

