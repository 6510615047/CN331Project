from django.shortcuts import render, redirect
import random
from homepage.models import User, Folder, Highscore,Word
from django.db.models import Min,Max
from itertools import groupby

# Create your views here.

def flashcard_choice(request,folder_id):
    username = request.user
    user = User.objects.get(user=username)
    folder = Folder.objects.get(user=user,folder_id=folder_id)
    min_word_id = Word.objects.filter(user=user, folder=folder).aggregate(Min('word_id'))['word_id__min']

    max_play_time = Highscore.objects.filter(user=user, folder=folder,game_id=3).aggregate(Max('play_time'))['play_time__max']

    default_word_id = min_word_id if min_word_id is not None else 1

    currentWordId = request.session.get('currentWordId', default_word_id)
    request.session['currentWordId'] = currentWordId
    
    current_word = Word.objects.filter(user=user, folder=folder, word_id=currentWordId).first()

    # Check if answers have already been stored in the session
    if request.session.get('is_first_visit', True):
        # User's first visit
        answers = [current_word.meaning]
        all_incorrect_answers = Word.objects.filter(user=user, folder=folder).exclude(meaning=current_word.meaning).order_by('?')
        unique_incorrect_answers = []
        for key, group in groupby(all_incorrect_answers, key=lambda x: x.meaning):
            unique_incorrect_answers.append(next(group))

        unique_incorrect_answers = unique_incorrect_answers[:3]
        incorrect_answers = [incorrect.meaning for incorrect in unique_incorrect_answers]
        answers += incorrect_answers
        random.shuffle(answers)

        # Store answers in session to prevent reshuffling
        request.session['answers'] = answers
        request.session['is_first_visit'] = False  # Set flag to False after first visit

    else:
        # User's subsequent visit
        currentWord = request.session.get('currentWordId')
        nextWord = Word.objects.filter(user=user, folder=folder, word_id=currentWord + 1).first()
        if not nextWord:
            # Clear session variables when the game finishes
            del request.session['currentWordId']
            del request.session['is_first_visit']
            return redirect('finish_choice', folder_id=folder.folder_id) 

        current_word = nextWord
        request.session['currentWordId'] = currentWord + 1

        answers = [current_word.meaning]
        all_incorrect_answers = Word.objects.filter(user=user, folder=folder).exclude(meaning=current_word.meaning).order_by('?')
        unique_incorrect_answers = []
        for key, group in groupby(all_incorrect_answers, key=lambda x: x.meaning):
            unique_incorrect_answers.append(next(group))

        unique_incorrect_answers = unique_incorrect_answers[:3]
        incorrect_answers = [incorrect.meaning for incorrect in unique_incorrect_answers]
        answers += incorrect_answers
        random.shuffle(answers)

    referrer = request.META.get('HTTP_REFERER', None)
    if referrer and "flashcardChoice" in referrer:
        highscore = Highscore.objects.get(
            user=user,
            folder=folder,
            game_id=3,
            play_time = max_play_time
        )
    else:
        highscore = Highscore.objects.create(
            user=user,
            folder=folder,
            game_id=3,
            score = 0
        )
        request.session['answered'] = False

    play_time = highscore.play_time

    pop_up_message_correct = request.session.pop('pop_up_message_correct', None)
    context = {
        'highscore': highscore,
        'user': user,
        'word': current_word.word,
        'folder':folder,
        'play_time':play_time,
        'answers':answers,
        'pop_up_message_correct': pop_up_message_correct,
        'correct_answer':current_word.meaning  # use for check_answer
    }

    return render (request,'flashcardChoice.html',context)

def check_answer(request,folder_id,play_time):
    username = request.user
    user = User.objects.get(user=username)
    folder = Folder.objects.get(user=user,folder_id=folder_id)

    highscore = Highscore.objects.get(
        user=user,
        folder=folder,
        game_id=3,
        play_time=play_time
    )

    if request.method == 'POST':
        selected_answer = request.POST.get('selected_answer')
        correct_answer=request.POST.get('correct_answer')
        if selected_answer==correct_answer:
            highscore.score += 1
            highscore.save()
            pop_up_message_correct = True
        else:
            pop_up_message_correct = False

        # Store the result in the session
        request.session['pop_up_message_correct'] = pop_up_message_correct

        # Store whether the answer was correct or not in the session for the next request
        request.session['answered'] = True if selected_answer == correct_answer else False

        # Redirect to the flashcard page (even if the answer is wrong)
        return redirect('flashcard_choice', folder_id=folder.folder_id)

def finishChoice(request, folder_id):
    username = request.user
    user = User.objects.get(user=username)
    folder = Folder.objects.get(user=user, folder_id=folder_id)

    highscore = Highscore.objects.filter(user=user, folder=folder, game_id=3).order_by('-play_time').first()

    pop_up_message_correct = request.session.get('pop_up_message_correct', None)
    context = {
        'highscore': highscore,
        'pop_up_message_correct': pop_up_message_correct,
    }

    request.session.pop('pop_up_message_correct', None)
    return render(request, 'finishChoice.html', context)






    