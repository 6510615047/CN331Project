from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm
from django.contrib.messages import get_messages

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
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Please correct the error below.')
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
        self.assertRedirects(response, '/')

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
