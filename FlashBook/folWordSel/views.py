from django.shortcuts import render,redirect
from django.contrib import messages
from homepage.models import *
# Create your views here.

# user = User.objects.get(user_id=request.session.get('user_id'))

def folder_view(request):
    user = User.objects.get(user_id=1)
    folders = Folder.objects.filter(user=user)
    return render(request,'folder.html',{'user':user,'folders' : folders})

def word_view(request, folder_id):
    user = User.objects.get(user_id=1)
    folder = Folder.objects.get(user=user,folder_id=folder_id)
    words = Word.objects.filter(user=user,folder=folder)
    return render(request,'word.html',{'words' : words,'folder':folder})

def select_game_view(request,folder_id):
    return render(request,'selGame.html')

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

        if action == 'edit':
            meaning = request.POST['meaning']
            newWord = Word.objects.create(
                user = user,
                folder = folder,
                word = word,
                meaning = meaning
            )
        elif action == 'auto_meaning':
            newWord = Word.objects.create(
                user = user,
                folder = folder,
                word = word,
            )

        newWord.save()
    words = Word.objects.filter(user=user,folder=folder)
    return render(request,'word.html',{'words' : words,'folder':folder})

def edit_word(request,folder_id,word_id):

    if request.method == 'POST':
        action = request.POST.get('action')
        user = User.objects.get(user_id=1)  
        folder = Folder.objects.get(user=user,folder_id=folder_id)

        if action == 'edit':
            word = request.POST['word_name']
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

    return render(request, 'folder.html', {'user': user, 'folders': search_results})


