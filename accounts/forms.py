from django import forms
from django.contrib.auth.models import User

class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(max_length=40, label='first_name')
    last_name = forms.CharField(max_length=40, label='last_name')
    email = forms.EmailField(max_length=30, label='email')
    username = forms.CharField(max_length=20, label='username')
    password = forms.CharField(max_length=20, label='password')

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'username',
            'password'
        )
        
    def clean(self):
        super(SignUpForm, self).clean()
    
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            self.add_error('first_name', 'Please fill in first name')
        elif len(first_name) <= 2:
            self.add_error('first_name', 'First name must be at least two characters long')

        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            self.add_error('last_name', 'Please fill in last name')
        elif len(last_name) <= 2:
            self.add_error('last_name', 'Last name must be at least two characters long')

        email = self.cleaned_data.get('email')
        if not email:
            self.add_error('email', 'Please fill in email')
        elif User.objects.filter(email=email).exists():
            self.add_error('email', 'Email already in use')

        username = self.cleaned_data.get('username')
        if not username:
            self.add_error('username', 'Please fill in username')
        elif len(username) <= 3:
            self.add_error('username', 'Username must be at least 3 characters long')
            
        password = self.cleaned_data.get('password')
        if not password:
            self.add_error('password', 'Please fill in password')
        elif len(password) <= 7:
            self.add_error('password', 'Password must be at least 8 characters long')

        return self.cleaned_data
                
class SignInForm(forms.Form):
    username = forms.CharField(max_length=20, label='username')
    password = forms.CharField(max_length=20, label='password')

class ChangePasswordForm(forms.ModelForm):
    password = forms.CharField(max_length=20, label='password')

    class Meta:
        model = User
        fields = ('password',)
    
    def clean (self):
        super(ChangePasswordForm, self).clean()

        password = self.cleaned_data.get('password')
        if not password:
            self.add_error('password', 'Please fill in password')
        elif len(password) <=7 :
            self.add_error('password', 'Password must be at least 8 characters long')

        return self.cleaned_data

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(max_length=30, label='email')