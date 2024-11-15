from django.shortcuts import render

# Create your views here.

def folder_view(request):
    return render(request,'folder.html')

def word_view(request):
    return render(request,'word.html')

def select_game_view(request):
    return render(request,'selGame.html')