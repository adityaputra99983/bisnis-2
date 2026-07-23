from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'email@contoh.com'
    }))
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Nama Depan'
    }))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Nama Belakang'
    }))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': '+62xxx'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Pilih username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Buat password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ulangi password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'customer',
                    'phone': self.cleaned_data.get('phone', ''),
                }
            )
        return user


class HealerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'email@contoh.com'
    }))
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Nama Depan'
    }))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Nama Belakang'
    }))
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': '+62xxx'
    }))
    healer_name = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Nama profesional Anda'
    }))
    address = forms.CharField(required=True, widget=forms.Textarea(attrs={
        'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat praktek'
    }))
    experience_years = forms.IntegerField(min_value=0, required=True, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': '0'
    }))
    bio = forms.CharField(required=True, widget=forms.Textarea(attrs={
        'class': 'form-control', 'rows': 3, 'placeholder': 'Ceritakan tentang pengalaman dan keahlian Anda...'
    }))
    specializations = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Reiki, Chakra Healing, Sound Healing'
    }))
    price_idr = forms.IntegerField(min_value=0, required=True, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': '500000'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Pilih username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Buat password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ulangi password'})

    def save(self, commit=True):
        from healers.models import Healer
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'healer',
                    'phone': self.cleaned_data.get('phone', ''),
                    'bio': self.cleaned_data.get('bio', ''),
                }
            )
            slug = self.cleaned_data['healer_name'].lower().replace(' ', '-')
            Healer.objects.get_or_create(
                user=user,
                defaults={
                    'name': self.cleaned_data['healer_name'],
                    'slug': slug,
                    'bio': self.cleaned_data['bio'],
                    'experience_years': self.cleaned_data['experience_years'],
                    'phone': self.cleaned_data['phone'],
                    'email': user.email,
                    'address': self.cleaned_data['address'],
                    'price_idr': self.cleaned_data['price_idr'],
                    'specializations': self.cleaned_data['specializations'],
                }
            )
        return user


class UserEditForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'bio']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
