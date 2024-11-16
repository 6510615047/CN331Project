from django.shortcuts import render, redirect
from homepage.models import User, Highscore, Folder
from .models import WordGuessGame
from django.contrib.auth.decorators import login_required
import random

# Define a list of words and their meanings (replace with your actual word list)
WORDS = [
    {"word": "python", "meaning": "ภาษาโปรแกรมมิ่งยอดนิยม"},
    {"word": "django", "meaning": "เฟรมเวิร์คสำหรับสร้างเว็บในภาษา Python"}
    # Add more words as needed
]

# @login_required
def word_guess_view(request):
    print("Word Guess View is running...")
    # Manually create or get a user for testing
    user, created = User.objects.get_or_create(user='testuser', defaults={'password': 'testpassword'})
    if created:
        user.set_password('testpassword')
        user.save()
    
    request.user = user  # Simulate a logged-in user

    # Fetch or create a game session for the current user
    game, created = WordGuessGame.objects.get_or_create(user=request.user, game_status='in_progress')

    if request.method == "POST" and 'reset' in request.POST:
        request.session.flush()  # Clears session data
        return redirect('word_guess')  # Restart the game

    # Initialize session variables if this is the first visit or after a reset
    if 'word_data' not in request.session:
        selected_word = random.choice(WORDS)
        request.session['word_data'] = selected_word
        request.session['guesses'] = []  # Guessed letters
        request.session['incorrect_guesses'] = []  # Incorrect guesses

    word_data = request.session['word_data']
    word = word_data["word"]  # Get the word
    meaning = word_data["meaning"]  # Get the Thai meaning
    guesses = request.session['guesses']
    incorrect_guesses = request.session['incorrect_guesses']

    # Handle form submission
    if request.method == "POST":
        guess = request.POST.get('guess', '').lower()
        if guess and guess not in guesses:
            guesses.append(guess)
            if guess not in word:
                incorrect_guesses.append(guess)
        request.session['guesses'] = guesses
        request.session['incorrect_guesses'] = incorrect_guesses

    # Generate the display word (e.g., "_ y _ _ _ n" for "python")
    display_word = " ".join([char if char in guesses else "_" for char in word])

    game_id = 2  # 2 for Word Guess Game
    folder, _ = Folder.objects.get_or_create(user=request.user, folder_name="WordGuess")

    # Check win or lose condition
    game_over = False
    message = ""
    max_incorrect_guesses = 6  # Allow 6 incorrect guesses
    hearts_left = max_incorrect_guesses - len(incorrect_guesses)

    if "_" not in display_word:
        game_over = True
        message = "Congratulations! You guessed the word!"
    elif hearts_left == 0:  # No hearts left
        game_over = True
        message = f"You lost! The word was '{word}'."

    # Create the range for hearts
    hearts_range = range(hearts_left)

    context = {
        'display_word': display_word,
        'incorrect_guesses': incorrect_guesses,
        'hearts_range': hearts_range,
        'game_over': game_over,
        'message': message,
        'word_meaning': meaning,  # Pass the Thai meaning
    }

    return render(request, 'wordguess/wordGuess.html', context)

def game_scores_view(request, game_id):
    # Simulate logged-in user for testing
    user, _ = User.objects.get_or_create(user='testuser')
    request.user = user
    
    # Assuming you want to filter Highscore by game_id and user
    scores = Highscore.objects.filter(user=request.user, game_id=game_id)

    return render(request, 'wordguess/game_scores.html', {
        'scores': scores,
        'game_id': game_id,
    })
