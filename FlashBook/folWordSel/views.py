from django.shortcuts import render,redirect
from django.contrib import messages
from homepage.models import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from io import BytesIO
import base64
import json
import random
# Create your views here.

def folder_view(request,noti="Looks like you don't have any folders yet. Let's add one to get started!"):
    user = User.objects.get(user_id=request.session.get('user_id'))
    folders = Folder.objects.filter(user=user)

    return render(request,'folder.html',{'user':user,'folders':folders,'noti':noti})

def word_view(request, folder_id, noti='This folder is empty. Start by adding words!'):
    user = User.objects.get(user_id=request.session.get('user_id'))
    folder = Folder.objects.get(user=user,folder_id=folder_id)
    words = Word.objects.filter(user=user,folder=folder)
    return render(request,'word.html',{'words' : words,'folder':folder,'noti':noti})

def add_folder(request):

    if request.method == 'POST':
        user = User.objects.get(user_id=request.session.get('user_id'))  

        folder_name = request.POST['folder_name']
        
        if Folder.objects.filter(user=user, folder_name=folder_name).exists():
            messages.error(request,"A folder with this name already exists.")
            return redirect('folder') 
        else:

            newFolder = Folder.objects.create(
                user=user,
                folder_name=folder_name
            )
            
            newFolder.save()

    return redirect('folder')

def edit_folder(request,folder_id):

    if request.method == 'POST':
        action = request.POST.get('action')
        user = User.objects.get(user_id=request.session.get('user_id'))  
        actionFolder = Folder.objects.get(user=user,folder_id=folder_id)

        if action == 'edit':

            actionFolder_name = request.POST['folder_name']
            if Folder.objects.filter(user=user,folder_name=actionFolder_name).exists():
                messages.error(request,"A folder with this name already exists.")
                return redirect('folder')
            
            actionFolder.folder_name = actionFolder_name
                    
            actionFolder.save()

        elif action == 'delete':

            actionFolder.delete()

    folders = Folder.objects.filter(user=user)

    return render(request,'folder.html',{'user':user,'folders':folders})

def add_word(request,folder_id):
    
    if request.method == 'POST':
        action = request.POST.get('action')
        user = User.objects.get(user_id=request.session.get('user_id')) 
        folder = Folder.objects.get(user=user,folder_id=folder_id)

        word = request.POST['word_name']

        if Word.objects.filter(user=user, folder=folder,word=word).exists():
                messages.error(request,"Word with this name already exists.")
                return word_view(request,folder_id)

        if action == 'add':
            meaning = request.POST['meaning']
            newWord = Word.objects.create(
                user = user,
                folder = folder,
                word = word,
                meaning = meaning
            )
            newWord.save()
    
    # words = Word.objects.filter(user=user,folder=folder)
    return word_view(request,folder_id)

def edit_word(request,folder_id,word_id):

    if request.method == 'POST':
        action = request.POST.get('action')
        user = User.objects.get(user_id=request.session.get('user_id'))  
        folder = Folder.objects.get(user=user,folder_id=folder_id)

        if action == 'edit':
            word = request.POST['word_name']

            if Word.objects.filter(user=user, folder=folder,word=word).exists():
                messages.error(request,"Word with this name already exists.")
                return word_view(request,folder_id)

            meaning = request.POST['meaning']
            editWord = Word.objects.get(user=user,folder=folder,word_id=word_id)

            editWord.word = word
            editWord.meaning = meaning
                
            editWord.save()
        elif action == 'delete':
            
            deleteWord = Word.objects.get(user=user,folder=folder,word_id=word_id)

            deleteWord.delete()
            Word.reorder_word_ids(deleteWord.user, deleteWord.folder)

    words = Word.objects.filter(user=user,folder=folder)

    return render(request,'word.html',{'words' : words,'folder':folder})

def search_folder(request):
    query = request.GET.get('query', '')
    user = User.objects.get(user_id=request.session.get('user_id'))

    if not query:
        return folder_view(request) 
    else:
        search_results = Folder.objects.filter(folder_name__icontains=query, user=user)

    if search_results:
        return render(request, 'folder.html', {'user': user, 'folders': search_results})
    else:
        error_message = "No folders found matching " + query + ". Try another search term."
        return render(request, 'folder.html', {'user': user, 'folders': search_results, 'noti': error_message})
    
def search_word(request,folder_id):
    query = request.GET.get('query', '')
    user = User.objects.get(user_id=request.session.get('user_id'))
    folder = Folder.objects.get(user=user,folder_id=folder_id)

    if not query:
        return word_view(request,folder_id) 
    else:
        search_results = Word.objects.filter(word__icontains=query, user=user,folder=folder)

    if search_results:
        return render(request, 'word.html', {'user': user, 'folder': folder, 'words' : search_results})
    else:
        error_message = "No words found matching " + query + ". Try another search term."
        return render(request, 'word.html', {'user': user, 'folder': folder, 'words' : search_results, 'noti':error_message})

def select_game_view(request,folder_id):
    return render(request, 'selGame.html',{'folder_id':folder_id})

# ฟังก์ชันใหม่สำหรับแสดงหน้า timeSet.html
def time_set_view(request,folder_id):
    return render(request, 'timeSet.html',{'folder_id':folder_id})

# ฟังก์ชันใหม่สำหรับแสดงหน้า modeSet.html
def mode_set_view(request,folder_id):
    return render(request, 'wordGuessMode.html',{'folder_id':folder_id})

def score(request):
    user = User.objects.get(user_id=request.session.get('user_id'))
    noti = None
    query = request.GET.get('query', None)

    game_1_scores = Highscore.objects.filter(user=user, game_id=1)
    game_2_scores = Highscore.objects.filter(user=user, game_id=2)
    # game_3_scores = Highscore.objects.filter(user=user, game_id=3)

    if query:
        folders = Folder.objects.filter(user=user, folder_name__icontains=query)  # กรองตาม query

        if not folders:
            folders = Folder.objects.filter(user=user)
            noti = "No scores found matching " + query + ". Try another search term."
        
    else:
        folders = Folder.objects.filter(user=user)
        if not folders:
            return render(request, 'score.html',{'user': user})

    fig, axs = plt.subplots(len(folders), 3, figsize=(15, len(folders) * 5))

    # ถ้ามีแค่ 1 folder ก็จะเป็นแค่ 1 แถว
    if len(folders) == 1:
        axs = [axs]

    for i, folder in enumerate(folders):
        # กรองข้อมูลของแต่ละ folder สำหรับเกมแต่ละเกม
        folder_game_1_scores = game_1_scores.filter(folder=folder)[:20]  # กรองตาม folder และจำกัดจำนวน
        folder_game_2_scores = game_2_scores.filter(folder=folder)[:20]
        # folder_game_3_scores = game_3_scores.filter(folder=folder)[:20]

        # สร้างกราฟสำหรับเกม 1
        folder_game_1_play_times = [score.play_time for score in folder_game_1_scores]
        folder_game_1_scores_values = [score.score for score in folder_game_1_scores]
        axs[i][0].plot(folder_game_1_play_times, folder_game_1_scores_values, marker='o', linestyle='-', color='b')
        axs[i][0].set(xlabel='Play Time', ylabel='Score', title=f'Game Flashcard: Folder {folder.folder_name}')
        axs[i][0].xaxis.set_major_locator(MaxNLocator(integer=True))  # แสดงค่าจำนวนเต็มบนแกน x
        axs[i][0].yaxis.set_major_locator(MaxNLocator(integer=True))  # แสดงค่าจำนวนเต็มบนแกน y
        axs[i][0].grid(False)

        # สร้างกราฟสำหรับเกม 2
        folder_game_2_play_times = [score.play_time for score in folder_game_2_scores]
        folder_game_2_scores_values = [score.score for score in folder_game_2_scores]
        axs[i][1].plot(folder_game_2_play_times, folder_game_2_scores_values, marker='o', linestyle='-', color='g')
        axs[i][1].set(xlabel='Play Time', ylabel='Score', title=f'Game Wordguess: Folder {folder.folder_name}')
        axs[i][1].xaxis.set_major_locator(MaxNLocator(integer=True))  # แสดงค่าจำนวนเต็มบนแกน x
        axs[i][1].yaxis.set_major_locator(MaxNLocator(integer=True))  # แสดงค่าจำนวนเต็มบนแกน y
        axs[i][1].grid(False)

        # สร้างกราฟสำหรับเกม 3
        # folder_game_3_play_times = [score.play_time for score in folder_game_3_scores]
        # folder_game_3_scores_values = [score.score for score in folder_game_3_scores]
        # axs[i][2].plot(folder_game_3_play_times, folder_game_3_scores_values, marker='o', linestyle='-', color='r')
        # axs[i][2].set(xlabel='Play Time', ylabel='Score', title=f'Game Flashcard multiple choice: Folder {folder.folder_name}')
        # axs[i][2].xaxis.set_major_locator(MaxNLocator(integer=True))  # แสดงค่าจำนวนเต็มบนแกน x
        # axs[i][2].yaxis.set_major_locator(MaxNLocator(integer=True))  # แสดงค่าจำนวนเต็มบนแกน y
        # axs[i][2].grid(True)

    # ปรับแต่งการจัด layout เพื่อให้กราฟไม่ทับซ้อน
    plt.tight_layout(pad=2.0)  # เพิ่มช่องว่างระหว่างกราฟ

    # บันทึกกราฟลงใน buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # แปลงกราฟเป็น base64
    graph_data = base64.b64encode(buf.getvalue()).decode('utf-8')

    # ส่งข้อมูลกราฟไปยัง template
    return render(request, 'score.html', {
        'user': user,
        'graph': graph_data,
        'folders': folders,
        'noti' : noti  # ส่งข้อมูล folder ไปยัง template
    })

def check_in(request):
    user = User.objects.get(user_id=request.session.get('user_id'))
    user.check_in()
    return redirect('folder')

def reward(request):
    user = User.objects.get(user_id=request.session.get('user_id'))
    return render(request,'reward.html',{'user':user})

def redeem_reward(request,reward_id):
    user = User.objects.get(user_id=request.session.get('user_id'))

    title_available = ['Letter Seeker','Word Explorer','Rookie Linguist','Sentence Spinner','Riddle Solver','Master of Meaning','Word Wizard','Word God','Linguistic Overlord']
    title_costs = [10, 20, 50, 80, 100, 150, 200, 300, 500]

    card_color_available = ['#FF5733','#5BC0EB','#28A745','#FFC107','#D1A1D3','#F06292','linear-gradient(45deg, #F06292, #9C27B0)','linear-gradient(45deg, #5BC0EB, #28A745)','linear-gradient(45deg, #FFC107, #FF7043)']
    card_color_costs = [100,100,100,100,100,100,300,300,300]

    colors = [
        "#D3D3D3", "#F0F0F0", "#8B8B8B", "#B0B0B0", "#A9A9A9", 
        "#FF8C00", "#FF6347", "#FFD700", "#87CEFA", "#98FB98",
        "#FF69B4", "#00BFFF", "#32CD32", "#FF4500", "#9932CC",
        "#FF1493", "#8A2BE2", "#7FFF00", "#FF6347", "#00CED1"
    ]
    
    gradients = [
        "linear-gradient(45deg, #D3D3D3, #F0F0F0)", "linear-gradient(45deg, #FF8C00, #FF6347)",
        "linear-gradient(45deg, #FFD700, #98FB98)", "linear-gradient(45deg, #87CEFA, #FFD700)",
        "linear-gradient(45deg, #FF69B4, #FF4500)", "linear-gradient(45deg, #00BFFF, #32CD32)",
        "linear-gradient(45deg, #9932CC, #FF69B4)", "linear-gradient(45deg, #FF4500, #00BFFF)"
    ]
    
    lucky_chest = colors + gradients
    weights = [3] * len(colors) + [1] * len(gradients)

    message = 'Redeem Success!'

    title_ava = user.get_title_ava()  # แปลง JSON string เป็น list
    card_color_ava = user.get_card_color_ava()  # แปลง JSON string เป็น list

    if(reward_id == 0):
        user.credits += 10
        user.day_streak_left -= 3

    elif(reward_id == 999):
        user.hint_ava += 1
        user.credits -= 50

    elif reward_id >= 1 and reward_id <= 9:
        title = title_available[reward_id - 1]
        cost = title_costs[reward_id - 1]

        if title not in title_ava:
            title_ava.append(title)  # เพิ่ม title ที่ได้จาก reward_id

        user.credits -= cost

    elif reward_id >= 10 and reward_id <= 18:
        card_color = card_color_available[reward_id - 10]
        cost = card_color_costs[reward_id - 10]

        if card_color not in card_color_ava:
            card_color_ava.append(card_color)
        
        user.credits -= cost

    elif(reward_id == 50):
        card_color = random.choices(lucky_chest, weights=weights, k=1)[0]
        if card_color not in card_color_ava:
            message = f'You have got {card_color}. Congratulations! A new card color has been added.'
            card_color_ava.append(card_color)
        else:
            message = f'You have got {card_color}. You already have this color.'
        
        user.credits -= 150

    else:
        error_message = 'Invalid reward_id!'
        return render(request,'reward.html',{'user':user,'noti':error_message}) 
    
    user.save()
    return render(request,'reward.html',{'user':user,'noti':message}) 
