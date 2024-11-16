from django.shortcuts import render,redirect
from django.contrib import messages
from homepage.models import *
# Create your views here.

# user = User.objects.get(user_id=request.session.get('user_id'))

def folder_view(request,noti="Looks like you don't have any folders yet. Let's add one to get started!"):
    user = User.objects.get(user_id=1)
    folders = Folder.objects.filter(user=user)
    return render(request,'folder.html',{'user':user,'folders':folders,'noti':noti})

def word_view(request, folder_id, noti='This folder is empty. Start by adding words!'):
    user = User.objects.get(user_id=1)
    folder = Folder.objects.get(user=user,folder_id=folder_id)
    words = Word.objects.filter(user=user,folder=folder)
    return render(request,'word.html',{'words' : words,'folder':folder,'noti':noti})

def add_folder(request):

    if request.method == 'POST':
        user = User.objects.get(user_id=1)  

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
        user = User.objects.get(user_id=1)  
        actionFolder = Folder.objects.get(user=user,folder_id=folder_id)

        if action == 'edit':

            actionFolder_name = request.POST['folder_name']
            print(actionFolder_name)
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
        user = User.objects.get(user_id=1)  
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
        user = User.objects.get(user_id=1)  
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

    words = Word.objects.filter(user=user,folder=folder)

    return render(request,'word.html',{'words' : words,'folder':folder})

def search_folder(request):
    query = request.GET.get('query', '')
    user = User.objects.get(user_id=1)

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
    user = User.objects.get(user_id=1)
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
    return render(request, 'selGame.html')

# ฟังก์ชันใหม่สำหรับแสดงหน้า timeSet.html
def time_set_view(request):
    return render(request, 'timeSet.html')

# ฟังก์ชันใหม่สำหรับแสดงหน้า modeSet.html
def mode_set_view(request):
    return render(request, 'wordGuessMode.html')

