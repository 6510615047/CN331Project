from django.shortcuts import render, redirect
from homepage.models import User, Highscore, Folder
from django.db.models import Min,Max
import random
WORDS = [
    {"word": "python", "meaning": "ภาษาโปรแกรมมิ่งยอดนิยม"},
    {"word": "django", "meaning": "เฟรมเวิร์คสำหรับสร้างเว็บในภาษา Python"}
    
]

def word_guess_view(request,folder_id):
    username = request.user
    user = User.objects.get(user=username)
    folder = Folder.objects.get(user=user,folder_id=folder_id)
    max_play_time = Highscore.objects.filter(user=user, folder=folder,game_id=1).aggregate(Max('play_time'))['play_time__max']

    if request.method == "POST" and 'reset' in request.POST:
        request.session.flush()  
        return redirect('word_guess')
    
    if 'word_data' not in request.session:
        selected_word = random.choice(WORDS)
        request.session['word_data'] = selected_word
        request.session['guesses'] = []  
        request.session['incorrect_guesses'] = []  

    word_data = request.session['word_data']
    word = word_data["word"]  
    meaning = word_data["meaning"]  
    guesses = request.session['guesses']
    incorrect_guesses = request.session['incorrect_guesses']

    if request.method == "POST":
        guess = request.POST.get('guess', '').lower()
        if guess and guess not in guesses:
            guesses.append(guess)
            if guess not in word:
                incorrect_guesses.append(guess)
        request.session['guesses'] = guesses
        request.session['incorrect_guesses'] = incorrect_guesses
    
    display_word = " ".join([char if char in guesses else "_" for char in word])

    game_id = 2  
    folder, _ = Folder.objects.get_or_create(user=request.user, folder_name="WordGuess")

    
    game_over = False
    message = ""
    max_incorrect_guesses = 6  
    hearts_left = max_incorrect_guesses - len(incorrect_guesses)

    if "_" not in display_word:
        game_over = True
        message = "Congratulations! You guessed the word!"
    elif hearts_left == 0:  
        game_over = True
        message = f"You lost! The word was '{word}'."

    
    if game_over:
        folder, _ = Folder.objects.get_or_create(user=request.user, folder_name="WordGuess")

        Highscore.objects.update_or_create(
            user=request.user,
            folder=folder,  
            game_id=game_id,
            defaults={'score': hearts_left, 'play_time': 1}  
        )

    hearts_range = range(hearts_left)

    context = {
        'display_word': display_word,
        'incorrect_guesses': incorrect_guesses,
        'hearts_range': hearts_range,
        'game_over': game_over,
        'message': message,
        'word_meaning': meaning,
    }

    return render(request, 'wordguess/wordGuess.html', context)

def game_scores_view(request,game_id,folder_id):
    
    username = request.user
    user = User.objects.get(user=username)
    folder = Folder.objects.get(user=user,folder_id=folder_id)
    scores = Highscore.objects.filter(user=request.user, game_id=game_id)

    return render(request, 'wordguess/wordGuess.html', {
        'scores': scores, 
        'game_id': game_id,
    })

