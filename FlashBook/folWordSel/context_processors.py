from datetime import date
from homepage.models import User

def check_in_today(request):
    # ตรวจสอบว่าผู้ใช้ล็อกอินหรือยัง
    if request.session.get('user_id'):
        user = User.objects.get(user_id=request.session.get('user_id'))
        today = date.today()
        print(today)
        print(user.last_check_in)
        # ตรวจสอบว่า user ได้เช็คอินในวันนี้หรือไม่
        is_checked_in_today = user.last_check_in == today
        return {'is_checked_in_today': is_checked_in_today,'user': user}
    return {'is_checked_in_today': False,'user': user}
