from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm
from django.contrib.messages import get_messages
from .models import User as User_model
from .models import Folder, Word, Highscore
from homepage.models import User as CustomUser
from django.test import SimpleTestCase
from homepage.views import homepage, about, register, login_views, logout_views, profile_view
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User as AuthUser

class RegisterLoginTests(TestCase):
    # เตรียมข้อมูลสำหรับทดสอบ
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.homepage_url = reverse('homepage')
        self.about_url = reverse('about')
        self.admin_url = '/admin/'
        self.user_credentials = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        self.admin_credentials = {
            'username': 'adminuser',
            'password': 'adminpassword123',
            'is_staff': True
        }
        self.user = User.objects.create_user(**self.user_credentials)
        self.admin_user = User.objects.create_user(**self.admin_credentials)

        self.user_model = User_model.objects.create(
            user_id=1,
            user='testuser',
            fname='Test',
            lname='User',
            email='testuser@example.com',
            password='testpassword123'
        )

    # ทดสอบหน้า homepage เพื่อให้แน่ใจว่าสามารถโหลดได้สำเร็จและใช้ template ที่ถูกต้อง
    def test_homepage_view(self):
        response = self.client.get(self.homepage_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')

    # ทดสอบหน้า about เพื่อให้แน่ใจว่าสามารถโหลดได้สำเร็จและใช้ template ที่ถูกต้อง
    def test_about_view(self):
        response = self.client.get(self.about_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')

    # ทดสอบหน้า register ด้วยการส่ง GET request เพื่อให้แน่ใจว่าแบบฟอร์มการลงทะเบียนโหลดได้สำเร็จ
    def test_register_view_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIsInstance(response.context['form'], RegisterForm)

    # ทดสอบหน้า register ด้วยการส่งข้อมูล POST ที่ถูกต้อง (happy path)
    def test_register_view_post_valid(self):
        valid_data = {
            'username': 'newuser',
            'fname': 'New',
            'lname': 'User',
            'email': 'newuser@example.com',
            'birthdate': '2000-01-01',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
        response = self.client.post(self.register_url, data=valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    # ทดสอบหน้า register ด้วยการส่งข้อมูล POST ที่ไม่ถูกต้อง (sad path)
    def test_register_view_post_invalid(self):
        invalid_data = {
            'username': '',  # Username จำเป็นแต่ไม่มีการกรอกข้อมูล
            'fname': 'New',
            'lname': 'User',
            'email': 'invalidemail',  # รูปแบบอีเมลไม่ถูกต้อง
            'birthdate': '2000-01-01',
            'password1': 'newpassword123',
            'password2': 'differentpassword'  # รหัสผ่านไม่ตรงกัน
        }
        response = self.client.post(self.register_url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertFalse(User.objects.filter(username='').exists())

    # ทดสอบหน้า login ด้วยการส่ง GET request เพื่อให้แน่ใจว่าแบบฟอร์มการล็อกอินโหลดได้สำเร็จ
    def test_login_view_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIsInstance(response.context['form'], LoginForm)

    # ทดสอบหน้า login ด้วยการส่งข้อมูล POST ที่ถูกต้อง (happy path)
    def test_login_view_post_valid(self):
        response = self.client.post(self.login_url, data=self.user_credentials)
        self.assertEqual(response.status_code, 302)

    # ทดสอบหน้า login ด้วยการส่งข้อมูล POST ที่ไม่ถูกต้อง (sad path)
    def test_login_view_post_invalid(self):
        invalid_credentials = {
            'username': 'wronguser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data=invalid_credentials)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    # ทดสอบหน้า logout เพื่อให้แน่ใจว่าผู้ใช้สามารถล็อกเอาต์และเปลี่ยนเส้นทางไปยังหน้าล็อกอินได้
    def test_logout_view(self):
        self.client.login(**self.user_credentials)
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)

    # ทดสอบการเข้าถึงหน้า admin เมื่อผู้ใช้ที่ล็อกอินเป็น admin
    def test_admin_login(self):
        self.client.login(username='adminuser', password='adminpassword123')
        response = self.client.post(self.login_url, data=self.admin_credentials)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.admin_url)

    # ทดสอบการเข้าถึงหน้า homepage โดยไม่ได้ล็อกอิน
    def test_homepage_view_without_login(self):
        response = self.client.get(self.homepage_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')

    def test_str_user_method(self):
        expected_str = f"{self.user_model.user}"
        self.assertEqual(str(self.user_model), expected_str)

    def test_str_folder_method(self):
        folder = Folder.objects.create(user=self.user_model, folder_name="Test Folder")
        expected_str = f"Folder 1 for User {self.user_model.user}"
        self.assertEqual(str(folder), expected_str)

    def test_str_word_method(self):
        folder = Folder.objects.create(user=self.user_model, folder_name="Test Folder")
        word = Word.objects.create(user=self.user_model, folder=folder, word="Test", meaning="This is a test.")
        expected_str = f"Word 1 in Folder {folder.folder_id} for User {self.user_model.user}"
        self.assertEqual(str(word), expected_str)

    def test_highscore_str_method(self):
        folder = Folder.objects.create(user=self.user_model, folder_name="Test Folder")
        highscore = Highscore.objects.create(user=self.user_model, folder=folder, game_id=1, play_time=1, score=0)
        expected_str = f"{self.user.username} - Folder {folder.folder_id} - Game {highscore.game_id} - Play {highscore.play_time} - Score: {highscore.score}"
        # Check if the string representation matches
        self.assertEqual(str(highscore), expected_str)


class TestUrls(SimpleTestCase):

    def test_homepage_url_resolves(self):
        url = reverse('homepage')
        self.assertEqual(resolve(url).func, homepage)

    def test_about_url_resolves(self):
        url = reverse('about')
        self.assertEqual(resolve(url).func, about)

    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func, register)

    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func, login_views)

    def test_logout_url_resolves(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func, logout_views)

    def test_profile_url_resolves(self):
        url = reverse('profile')
        self.assertEqual(resolve(url).func, profile_view)

    # ทดสอบ URL สำหรับ password reset views
    def test_password_reset_url_resolves(self):
        url = reverse('password_reset')
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetView)

    def test_password_reset_done_url_resolves(self):
        url = reverse('password_reset_done')
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetDoneView)

    def test_password_reset_confirm_url_resolves(self):
        # จำลองค่า uidb64 และ token เพื่อสร้าง URL ที่สมบูรณ์
        url = reverse('password_reset_confirm', kwargs={'uidb64': 'abcd', 'token': '12345'})
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetConfirmView)

    def test_password_reset_complete_url_resolves(self):
        url = reverse('password_reset_complete')
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetCompleteView)

class TestProfileView(TestCase):
    def setUp(self):
        self.client = Client()
        self.auth_user = AuthUser.objects.create_user(username='testuser', password='testpassword')
        self.custom_user = User_model.objects.create(user_id=self.auth_user.id, user='testuser', fname='Test', lname='User', email='testuser@example.com')
        self.profile_url = reverse('profile')

    # ทดสอบการอัปเดตข้อมูลสำเร็จ
    def test_profile_view_success(self):
        self.client.login(username='testuser', password='testpassword')
        data = {
            'user': 'newusername',
            'fname': 'NewFirstName',
            'lname': 'NewLastName',
            'title': 'NewTitle',
            'card_color': '#123456',
            'email': 'newemail@example.com',
            'current_password': 'testpassword',
            'new_password': 'newpassword'
        }

        response = self.client.post(self.profile_url, data)

        # Fetch updated data
        self.custom_user.refresh_from_db()
        self.auth_user.refresh_from_db()

        # Assert the updates were successful
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertEqual(self.custom_user.user, 'newusername')
        self.assertEqual(self.custom_user.fname, 'NewFirstName')
        self.assertEqual(self.custom_user.lname, 'NewLastName')
        self.assertEqual(self.custom_user.title, 'NewTitle')
        self.assertEqual(self.custom_user.card_color, '#123456')
        self.assertEqual(self.custom_user.email, 'newemail@example.com')
        self.assertEqual(self.auth_user.username, 'newusername')
        self.assertTrue(self.auth_user.check_password('newpassword'))

    # ทดสอบกรณีผู้ใช้ไม่พบในระบบ
    def test_profile_view_user_not_found(self):
        self.client.login(username='nonexistent', password='testpassword')
        response = self.client.get(self.profile_url)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)  # Redirect to login if user not found

    # ทดสอบกรณีชื่อผู้ใช้ใหม่ซ้ำกับผู้ใช้อื่น
    def test_profile_view_username_exists(self):
        another_user = AuthUser.objects.create_user(username='existinguser', password='password123')
        User_model.objects.create(user_id=another_user.id, user='existinguser', fname='Another', lname='User', email='existinguser@example.com')

        self.client.login(username='testuser', password='testpassword')
        data = {
            'user': 'existinguser',
            'fname': 'NewFirstName',
            'lname': 'NewLastName',
            'title': 'NewTitle',
            'card_color': '#123456',
            'email': 'newemail@example.com',
            'current_password': 'testpassword',
            'new_password': 'newpassword'
        }

        response = self.client.post(self.profile_url, data)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)  # Redirect after error

    # ทดสอบกรณีรหัสผ่านปัจจุบันไม่ถูกต้อง
    def test_profile_view_incorrect_current_password(self):
        self.client.login(username='testuser', password='testpassword')
        data = {
            'user': 'newusername',
            'fname': 'NewFirstName',
            'lname': 'NewLastName',
            'title': 'NewTitle',
            'card_color': '#123456',
            'email': 'newemail@example.com',
            'current_password': 'wrongpassword',
            'new_password': 'newpassword'
        }

        response = self.client.post(self.profile_url, data)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)  # Redirect after error

    # ทดสอบการอัปเดตข้อมูลโดยไม่มีการเปลี่ยนรหัสผ่าน
    def test_profile_view_no_password_change(self):
        self.client.login(username='testuser', password='testpassword')
        data = {
            'user': 'newusername',
            'fname': 'NewFirstName',
            'lname': 'NewLastName',
            'title': 'NewTitle',
            'card_color': '#123456',
            'email': 'newemail@example.com'
        }

        response = self.client.post(self.profile_url, data)

        # Fetch updated data
        self.custom_user.refresh_from_db()
        self.auth_user.refresh_from_db()

        # Assert the updates were successful
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertEqual(self.custom_user.user, 'newusername')
        self.assertEqual(self.custom_user.fname, 'NewFirstName')
        self.assertEqual(self.custom_user.lname, 'NewLastName')
        self.assertEqual(self.custom_user.title, 'NewTitle')
        self.assertEqual(self.custom_user.card_color, '#123456')
        self.assertEqual(self.custom_user.email, 'newemail@example.com')
        self.assertEqual(self.auth_user.username, 'newusername')
        self.assertEqual(self.auth_user.email, 'newemail@example.com')