from django.test import TestCase
from accounts.forms import RegisterForm, ProfileUpdateForm

class RegisterFormTest(TestCase):
    def test_valid_form(self):
        # A fully valid form submission
        data = {
            'username': 'farmer123',
            'email': 'farmer@example.com',
            'first_name': 'Ram',
            'last_name': 'Singh',
            'phone': '9876543210',
            'role': 'farmer',
            'state': 'Bihar',
            'district': 'Patna',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        form = RegisterForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_invalid_names(self):
        # Names containing numbers should be rejected
        data = {
            'username': 'buyer456',
            'email': 'buyer@example.com',
            'first_name': 'Ram123', # Invalid
            'last_name': 'Singh',
            'phone': '9876543210',
            'role': 'buyer',
            'state': 'Bihar',
            'district': 'Patna',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

        # Names containing special characters should be rejected
        data['first_name'] = 'Ram'
        data['last_name'] = 'Singh-Sharma' # Invalid (only alphabets, no dash)
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

    def test_username_validation(self):
        # Username must contain at least one alphabet character, numbers are optional.
        # 1. Letters only (valid)
        data = {
            'username': 'farmeronly',
            'email': 'farmer@example.com',
            'first_name': 'Ram',
            'last_name': 'Singh',
            'phone': '9876543210',
            'role': 'farmer',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        form = RegisterForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())

        # 2. Numbers only (invalid)
        data['username'] = '12345678'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_phone_validation(self):
        # 1. Too short (9 digits)
        data = {
            'username': 'farmer123',
            'email': 'farmer@example.com',
            'first_name': 'Ram',
            'last_name': 'Singh',
            'phone': '987654321', # 9 digits
            'role': 'farmer',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

        # 2. Too long (11 digits)
        data['phone'] = '98765432101'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

        # 3. Containing non-digits
        data['phone'] = '987654321a'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

        # 4. Valid (exactly 10 digits)
        data['phone'] = '9876543210'
        form = RegisterForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_password_strength(self):
        # Base valid data
        base_data = {
            'username': 'buyer456',
            'email': 'buyer@example.com',
            'first_name': 'Ram',
            'last_name': 'Singh',
            'role': 'buyer',
            'phone': '9876543210',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }

        # 1. Too short
        data = base_data.copy()
        data['password1'] = 'Pass1!'
        data['password2'] = 'Pass1!'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

        # 2. No lowercase
        data = base_data.copy()
        data['password1'] = 'SECUREPASS123!'
        data['password2'] = 'SECUREPASS123!'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

        # 3. No uppercase
        data = base_data.copy()
        data['password1'] = 'securepass123!'
        data['password2'] = 'securepass123!'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

        # 4. No number
        data = base_data.copy()
        data['password1'] = 'SecurePass!'
        data['password2'] = 'SecurePass!'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

        # 5. No special char
        data = base_data.copy()
        data['password1'] = 'SecurePass123'
        data['password2'] = 'SecurePass123'
        form = RegisterForm(data=data)
        self.assertIn('password1', form.errors)

    def test_register_view(self):
        from django.urls import reverse
        # Test GET request
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request
        data = {
            'username': 'buyer999',
            'email': 'buyer999@example.com',
            'first_name': 'Ram',
            'last_name': 'Singh',
            'phone': '9876543210',
            'role': 'buyer',
            'state': 'Delhi',
            'district': 'New Delhi',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = self.client.post(reverse('register'), data=data)
        # Print status and errors if any to debug
        print("\n=== REGISTER VIEW TEST OUTPUT ===")
        print("STATUS:", response.status_code)
        if response.status_code == 200:
            print("ERRORS:", response.context['form'].errors.as_json())
        print("=================================\n")
        self.assertEqual(response.status_code, 302)

    def test_login_register_redirects_for_authenticated_users(self):
        from django.urls import reverse
        from accounts.models import CustomUser
        user = CustomUser.objects.create_user(
            username='authuser1', password='Password123!', email='auth@example.com', phone='9876543210'
        )
        self.client.login(username='authuser1', password='Password123!')
        
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, reverse('dashboard'))
        
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('dashboard'))

class ProfileUpdateFormTest(TestCase):
    def test_valid_profile_update(self):
        # Valid names
        data = {
            'first_name': 'Ram',
            'last_name': 'Singh',
            'email': 'ram@example.com',
            'phone': '9876543210',
        }
        form = ProfileUpdateForm(data=data)
        # Note: ProfileUpdateForm might have some fields that are required by the model/widget,
        # but let's check validation errors specifically for the names.
        self.assertNotIn('first_name', form.errors)
        self.assertNotIn('last_name', form.errors)

    def test_invalid_profile_update_names(self):
        # Invalid names
        data = {
            'first_name': 'Ram123',
            'last_name': 'Singh@',
            'email': 'ram@example.com',
            'phone': '9876543210',
        }
        form = ProfileUpdateForm(data=data)
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)

    def test_profile_phone_validation(self):
        # 1. Too short
        data = {
            'first_name': 'Ram',
            'last_name': 'Singh',
            'email': 'ram@example.com',
            'phone': '987654321',
        }
        form = ProfileUpdateForm(data=data)
        self.assertIn('phone', form.errors)

        # 2. Too long
        data['phone'] = '98765432101'
        form = ProfileUpdateForm(data=data)
        self.assertIn('phone', form.errors)

        # 3. Valid
        data['phone'] = '9876543210'
        form = ProfileUpdateForm(data=data)
        self.assertNotIn('phone', form.errors)
