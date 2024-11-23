from django.shortcuts import render
from homepage.models import User, Highscore, Folder, Word
from random import choice

def word_guess_view(request, folder_id):
    user = User.objects.get(user=request.user)
    folder = Folder.objects.get(user=user, folder_id=folder_id)
    words = Word.objects.filter(user=user, folder=folder)

    guesses = request.session.get('guesses', [])
    
    if 'word_id' not in request.session: #choose word for new session
        word = choice(words)
        request.session['word_id'] = word.id
        guesses = [] # makes guess characlist empty for new sesion
        request.session['guesses'] = guesses # update session guess detail
    else:
        word = Word.objects.get(id=request.session['word_id'])

    meaning = word.meaning

    score = request.session.get('score', 6)  # Default score is 6

    # Process guess
    if request.method == "POST" and 'guess' in request.POST:
        guesses, score = process_guess(request, word, guesses, score) #Process guess everytime that add input
        request.session['guesses'] = guesses
        request.session['score'] = score
    
    display_word = get_display_word(word, guesses) # Call display_word method

    # Check if the game is over
    game_end = False
    message = ""
    
    if "_" not in display_word:  # If no blanks, the word is fully guessed
        game_end = True
        message = "Congratulations! You guessed the word!"
    elif score == 0:  # If the score is 0, the game is over
        game_end = True
        message = f"You lost! The word was '{word.word}'."

    if game_end:
        # Update or create highscore at the end of the game
        update_highscore(user, folder, score)
        #reser session
        request.session.pop('word_id', None)
        request.session.pop('guesses', None)
        request.session.pop('score', None)

    hearts_range = range(score)

    # Prepare the context for the template
    context = {
        'highscore': Highscore.objects.filter(user=user, folder=folder, game_id=2).order_by('-play_time').first(),
        'display_word': display_word,
        'game_end': game_end,
        'message': message,
        'guesses': guesses,
        'score': score,
        'user': user,
        'word': word,
        'meaning': meaning,
        'folder': folder,
        'hearts_range': hearts_range,
    }

    print(meaning)
    print(word)
    
    return render(request, 'wordguess/wordGuess.html', context) #render site with parameter from context

def process_guess(request, word, guesses, score):
    guess = request.POST.get('guess', '').lower()  # Get the guess and convert it to lowercase
    if guess and len(guess) == 1 and guess.isalpha():  # Check if there's an guess input and length = 1
        if guess not in guesses:  # Only process the guess if it's a new character
            guesses.append(guess)
            request.session['guesses'] = guesses  # Save the guesses list back to the session

            # Check if the guess is incorrect, decrease score
            if guess not in word.word.lower():
                score -= 1
    print(guess)
    return guesses, score

def update_highscore(user, folder, score):
    highscore = Highscore.objects.filter(
        user=user,
        folder=folder,
        game_id=2  # Assuming game ID for word guess is 2
    ).order_by('-play_time').first()  # Get the most recent highscore

    if highscore:
        highscore.score = score
        highscore.save()  # Update the highscore
    else:
        # Create new highscore if it doesn't exist
        Highscore.objects.create(
            user=user,
            folder=folder,
            game_id=2,
            score=score,
            play_time=1  # First play time
        )

def get_display_word(word, guesses):
    return " ".join([char if char in guesses else "_" for char in word.word])  # Display _ _ _ _ _ ...












