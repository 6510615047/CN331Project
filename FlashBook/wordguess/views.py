from django.shortcuts import render, redirect 
from django.contrib.auth.models import User
from .models import WordGuessGame
import random

WORDS = ["python", "django", "hangman", "programming", "flashbook"]

def word_guess_view(request):
    # Simulate an authenticated user (you can replace this with a real user during testing)
    if not request.user.is_authenticated:
        user, created = User.objects.get_or_create(username='testuser', defaults={'password': 'testpassword'})
        if created:
            user.set_password('testpassword')
            user.save()
        request.user = user  # Manually assign the user to the request object

    # Ensure user is logged in
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login page if not authenticated

    # Fetch or create a game session for the current user
    game, created = WordGuessGame.objects.get_or_create(user=request.user, game_status='in_progress')

    if request.method == "POST" and 'reset' in request.POST:
        request.session.flush()  # Clears session data
        return redirect('word_guess')  # Redirect to the same page to restart the game

    # Initialize session variables if this is the first visit or after a reset
    if 'word' not in request.session:
        request.session['word'] = random.choice(WORDS)  # Random word
        request.session['guesses'] = []  # Guessed letters
        request.session['incorrect_guesses'] = []  # Incorrect guesses

    word = request.session['word']
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

    # Check win or lose condition
    game_over = False
    message = ""
    max_incorrect_guesses = 6  # Allow 6 incorrect guesses before game over
    hearts_left = max_incorrect_guesses - len(incorrect_guesses)

    if "_" not in display_word:
        game_over = True
        message = "Congratulations! You guessed the word!"
    elif hearts_left == 0:  # No hearts left (max incorrect guesses reached)
        game_over = True
        message = f"You lost! The word was '{word}'."

    # Create the range for hearts based on incorrect guesses
    hearts_range = range(hearts_left)

    context = {
        'display_word': display_word,
        'incorrect_guesses': incorrect_guesses,
        'hearts_range': hearts_range,  # Range for hearts to display remaining hearts
        'game_over': game_over,
        'message': message,
    }

    return render(request, 'wordGuess.html', context)
