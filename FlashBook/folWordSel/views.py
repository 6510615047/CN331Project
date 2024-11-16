from django.shortcuts import render

def folder_view(request):
    return render(request, 'folder.html')

def word_view(request):
    return render(request, 'word.html')

def select_game_view(request):
    return render(request, 'selGame.html')

# ฟังก์ชันใหม่สำหรับแสดงหน้า timeSet.html
def time_set_view(request):
    return render(request, 'timeSet.html')

# ฟังก์ชันใหม่สำหรับแสดงหน้า modeSet.html
def mode_set_view(request):
    return render(request, 'wordGuessMode.html')
