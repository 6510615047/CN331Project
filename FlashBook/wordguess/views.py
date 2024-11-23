from django.shortcuts import render
from homepage.models import User, Highscore, Folder, Word
from random import choice,sample

def word_guess_view(request, folder_id):
    username = request.user
    user = User.objects.get(user=username)
    folder = Folder.objects.get(user=user, folder_id=folder_id)
    words = Word.objects.filter(user=user, folder=folder)
    difficulty = request.GET.get('difficulty', 'normal') #default=normal

    guesses = request.session.get('guesses', [])
    
    if 'word_id' not in request.session: #choose word for new session
        word = choice(words)
        request.session['word_id'] = word.word_id
        guesses = [] # makes guess characlist empty for new sesion

        if difficulty == "easy":
            prefill_count = max(1, len(word.word) // 2)  # Prefill ~50%
            guesses = sample(list(set(word.word.lower())), prefill_count)
        elif difficulty == "normal":
            prefill_count = max(1, len(word.word) // 4)  # Prefill ~25%
            guesses = sample(list(set(word.word.lower())), prefill_count)
        elif difficulty == "hard":
            guesses = []  # No prefilled characters
            request.session['score'] = 4  # Reduce initial score for hard mode

        request.session['guesses'] = guesses # update session guess detail
    else:
        word = Word.objects.get(
        word_id=request.session['word_id'],
        user=user,
        folder=folder
        )
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
        #reset session
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
    print(user)
    print(folder)
    print(word)
    

    return render(request, 'wordguess/wordGuess.html', context) #render site with parameter from context

def process_guess(request, word, guesses, score):
    guess = request.POST.get('guess','').lower()  # Get the guess and convert it to lowercase
    word_lower = word.word.lower()

    if guess and len(guess) == 1 and guess.isalnum():  # Check if there's an guess input (alphanumeric)length = 1
        if guess not in guesses:  # Only process the guess if it's a new character
            guesses.append(guess)
            request.session['guesses'] = guesses  # Save the guesses list back to the session

            # Check if the guess is incorrect, decrease score
            if guess not in word_lower:
                score -= 1

    print(guesses)
    print(word_lower)
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
    word_lower = word.word.lower()
    return " ".join([char if char in guesses else "_" for char in word_lower])  # Display _ _ _ _ _ ...












