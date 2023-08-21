from django import forms
from django.contrib.auth.models import User
from models import Customer

class CheckoutForm(forms.ModelForm):
    #only for guest
    name = forms.CharField(max_length=20, label='name')
    email = forms.EmailField(max_length=30, label='email')

    #only if cart has non-digital item(s)
    address = forms.CharField(max_length=100, label='address')
    city = forms.CharField(max_length=20, label='city')
    state = forms.CharField(max_length=15, label='state')
    zipcode = forms.CharField(max_length=10, label='zipcode')

    total = forms.FloatField(label='total')

    class Meta:
        model = Customer
        fields = (
            'name',
            'email'
        )
    
    #validate form data
    def clean(self):
        super(CheckoutForm, self).clean()

        user = User
        if not user.is_authenticated:
            name = self.cleaned_data.get('name')
            if not name:
                self.add_error('name', 'Please fill in name')
            
            email = self.cleaned_data.get('email')
            if not email:
                self.add_error('email', 'Please fill in email')

        address = self.cleaned_data.get('address')
        if not address:
            self.add_error('address', 'Please fill in address')

        city = self.cleaned_data.get('city')
        if not city:
            self.add_error('city', 'Please fill in city')
            
        state = self.cleaned_data.get('state')
        if not state:
            self.add_error('state', 'Please fill in state')
            
        zipcode = self.cleaned_data.get('zipcode')
        if not zipcode:
            self.add_error('zipcode', 'Please fill in zipcode')

        return self.cleaned_data