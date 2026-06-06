from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=10, required=True)
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES[:2])  # farmer/buyer only
    state = forms.CharField(max_length=100, required=False)
    district = forms.CharField(max_length=100, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'role', 'state', 'district', 'password1', 'password2']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            if not phone.isdigit() or len(phone) != 10:
                raise forms.ValidationError(
                    "Phone number must be exactly 10 digits. / फ़ोन नंबर ठीक 10 अंकों का होना चाहिए। / फोन नम्बर ठीक १० अंकको हुनुपर्छ।"
                )
        return phone

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '')
        if first_name and not first_name.isalpha():
            raise forms.ValidationError(
                "First name must contain only alphabets. / पहले नाम में केवल अक्षर होने चाहिए। / पहिलो नाममा केवल अक्षरहरू हुनुपर्छ।"
            )
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '')
        if last_name and not last_name.isalpha():
            raise forms.ValidationError(
                "Last name must contain only alphabets. / अंतिम नाम में केवल अक्षर होने चाहिए। / अन्तिम नाममा केवल अक्षरहरू हुनुपर्छ।"
            )
        return last_name

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if username:
            import re
            if not re.search(r'[a-zA-Z]', username):
                raise forms.ValidationError(
                    "Username must contain at least one alphabet character. / यूजरनाम में कम से कम एक अक्षर होना चाहिए। / प्रयोगकर्ता नाममा कम्तिमा एउटा अक्षर हुनुपर्छ।"
                )
        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1', '')
        if password:
            if len(password) < 8:
                raise forms.ValidationError(
                    "Password must be at least 8 characters long. / पासवर्ड कम से कम 8 वर्णों का होना चाहिए। / पासवर्ड कम्तिमा ८ अक्षरको हुनुपर्छ।"
                )
            import re
            if not re.search(r'[a-z]', password):
                raise forms.ValidationError(
                    "Password must contain at least one lowercase letter. / पासवर्ड में कम से कम एक छोटा अक्षर (lowercase) होना चाहिए। / पासवर्डमा कम्तिमा एउटा सानो अक्षर हुनुपर्छ।"
                )
            if not re.search(r'[A-Z]', password):
                raise forms.ValidationError(
                    "Password must contain at least one uppercase letter. / पासवर्ड में कम से कम एक बड़ा अक्षर (uppercase) होना चाहिए। / पासवर्डमा कम्तिमा एउटा ठूलो अक्षर हुनुपर्छ।"
                )
            if not re.search(r'[0-9]', password):
                raise forms.ValidationError(
                    "Password must contain at least one number. / पासवर्ड में कम से कम एक अंक होना चाहिए। / पासवर्डमा कम्तिमा एउटा नम्बर हुनुपर्छ।"
                )
            if not re.search(r'[^a-zA-Z0-9]', password):
                raise forms.ValidationError(
                    "Password must contain at least one special character. / पासवर्ड में कम से कम एक विशेष वर्ण (special character) होना चाहिए। / पासवर्डमा कम्तिमा एउटा विशेष क्यारेक्टर हुनुपर्छ।"
                )
        return password

class LoginForm(AuthenticationForm):
    pass

class ProfileUpdateForm(forms.ModelForm):
    phone = forms.CharField(max_length=10, required=True)
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'state', 'district', 'profile_pic']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'first_name' in self.fields:
            self.fields['first_name'].widget.attrs['oninput'] = "this.value = this.value.replace(/[^a-zA-Z]/g, '')"
        if 'last_name' in self.fields:
            self.fields['last_name'].widget.attrs['oninput'] = "this.value = this.value.replace(/[^a-zA-Z]/g, '')"
        if 'phone' in self.fields:
            self.fields['phone'].widget.attrs['oninput'] = "this.value = this.value.replace(/[^0-9]/g, '')"
            self.fields['phone'].widget.attrs['maxlength'] = "10"

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            if not phone.isdigit() or len(phone) != 10:
                raise forms.ValidationError(
                    "Phone number must be exactly 10 digits. / फ़ोन नंबर ठीक 10 अंकों का होना चाहिए। / फोन नम्बर ठीक १० अंकको हुनुपर्छ।"
                )
        return phone

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '')
        if first_name and not first_name.isalpha():
            raise forms.ValidationError(
                "First name must contain only alphabets. / पहले नाम में केवल अक्षर होने चाहिए। / पहिलो नाममा केवल अक्षरहरू हुनुपर्छ।"
            )
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '')
        if last_name and not last_name.isalpha():
            raise forms.ValidationError(
                "Last name must contain only alphabets. / अंतिम नाम में केवल अक्षर होने चाहिए। / अन्तिम नाममा केवल अक्षरहरू हुनुपर्छ।"
            )
        return last_name

# Apply Bootstrap styling
for field in RegisterForm.base_fields.values():
    if hasattr(field.widget, 'attrs'):
        if field.widget.__class__.__name__ in ['TextInput','EmailInput','NumberInput','PasswordInput']:
            field.widget.attrs['class'] = 'form-control'
        elif field.widget.__class__.__name__ == 'Select':
            field.widget.attrs['class'] = 'form-select'
        elif field.widget.__class__.__name__ == 'Textarea':
            field.widget.attrs['class'] = 'form-control'
for field in ProfileUpdateForm.base_fields.values():
    if hasattr(field.widget, 'attrs'):
        if field.widget.__class__.__name__ in ['TextInput','EmailInput','NumberInput']:
            field.widget.attrs['class'] = 'form-control'
        elif field.widget.__class__.__name__ == 'Textarea':
            field.widget.attrs['class'] = 'form-control'
