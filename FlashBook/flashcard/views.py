from django.shortcuts import render, redirect
from homepage.models import User, Folder, Highscore,Word

# Create your views here.

def flashcard(request):
    user = User.objects.get(user="wern")
    folder = Folder.objects.filter(user=user)
    
    # Retrieve the current word ID from the session, default to 1
    current_word_id = request.session.get('current_word_id', 1)
    
    # Retrieve the current word based on the word_id
    word = Word.objects.filter(user=user, folder__in=folder, word_id=current_word_id).first()
    
    # Get or create Highscore entry for the user and folder
    highscore, created = Highscore.objects.get_or_create(
        user=user,
        folder=folder.first(),
        game_id=1,
        defaults={'score': 0, 'play_time': 1}
    )

    # Check if the user wants to see the meaning
    show_meaning = request.session.get('show_meaning', False)

    # Prepare the context
    context = {
        'highscore': highscore,
        'user': user,
        'word': word.word if word and not show_meaning else word.meaning if word else None,
        'show_meaning': show_meaning,
    }

    return render(request, 'flashcard.html', context)


def correct_answer(request):
    # Retrieve the test user
    user = User.objects.get(user="wern")
    folder = Folder.objects.get(user=user)

    # Retrieve or create Highscore for the user and folder
    highscore, created = Highscore.objects.get_or_create(
        user=user,
        folder=folder,
        game_id=1,
        defaults={'score': 0}
    )
    
    # Increment score
    highscore.score += 1
    highscore.save()

    # Set the session to show the meaning after either "correct" or "wrong"
    request.session['show_meaning'] = True

    # Redirect to flashcard page
    return redirect('flashcard')

def wrong_answer(request):
    # Retrieve the test user
    user = User.objects.get(user="wern")
    folder = Folder.objects.get(user=user)

    # Retrieve or create Highscore for the user and folder
    highscore, created = Highscore.objects.get_or_create(
        user=user,
        folder=folder,
        game_id=1,
        defaults={'score': 0}
    )

    # Decrement score (optional)
    highscore.score -= 0
    highscore.save()

    # Set the session to show the meaning after either "correct" or "wrong"
    request.session['show_meaning'] = True

    # Redirect to flashcard page
    return redirect('flashcard')

def next_word(request):
    user = User.objects.get(user="wern")
    folder = Folder.objects.get(user=user)
    
    # Get the current word from session or default to word_id 1
    current_word = request.session.get('current_word_id', 1)
    
    # Retrieve the next word based on the current word_id
    next_word = Word.objects.filter(user=user, folder=folder, word_id=current_word + 1).first()
    
    # If there's no next word, we cycle back to the first word or handle it differently
    if not next_word:
        # Cycle back to the first word if needed
        next_word = Word.objects.filter(user=user, folder=folder, word_id=1).first()
        
        # Reset score to 0 if no next word (i.e., end of words or cycle back)
        highscore, created = Highscore.objects.get_or_create(
            user=user,
            folder=folder,
            game_id=1,
            defaults={'score': 0}  # Initialize score to 0 if it's the end
        )
        highscore.score = 0
        highscore.save()

        # Reset session variables and show the finish screen
        request.session['current_word_id'] = next_word.word_id if next_word else current_word
        request.session['show_meaning'] = False
        
        return redirect('finish')
    
    # Set the current word in the session for the next call
    request.session['current_word_id'] = next_word.word_id if next_word else current_word
    
    # Reset session to show the word, not the meaning, after moving to the next word
    request.session['show_meaning'] = False
    
    return redirect('flashcard')

def finish(request):
    return render(request,'finish.html')



