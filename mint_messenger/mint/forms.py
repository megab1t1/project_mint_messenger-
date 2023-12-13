from django import forms
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError

from .models import *


class SendMessageForm(forms.ModelForm):
    class Meta:
        model = Messages
        fields = ['message', 'user', 'user_to']
        widgets = {
            'message': forms.TextInput(attrs={'autofocus': True,
                                              'class': 'input_field',
                                              'autocomplete': 'off',
                                              'placeholder': 'write something...',
                                              'title': ''})
        }

    def __init__(self, *args, **kwargs):
        super(SendMessageForm, self).__init__(*args, **kwargs)
        self.fields['message'].label = ''


class EditMessageForm(forms.ModelForm):
    class Meta:
        model = Messages
        fields = ['message']
        widgets = {
            'message': forms.TextInput(attrs={'autofocus': True,
                                              'class': 'input_field',
                                              'autocomplete': 'off',
                                              'placeholder': 'write something...',
                                              'title': ''})
        }

    def __init__(self, *args, **kwargs):
        super(EditMessageForm, self).__init__(*args, **kwargs)
        self.fields['message'].label = ''


class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        help_texts = {
            'username': None
        }
        widgets = {
            'username': forms.TextInput(attrs={'autofocus': True,
                                               'autocomplete': 'off',
                                               'placeholder': 'имя пользователя',
                                               'title': '',
                                               'class': 'form_field'}),

            'password': forms.TextInput(attrs={'autocomplete': 'off',
                                               'placeholder': 'пароль',
                                               'title': '',
                                               'class': 'form_field'}),

            'email': forms.TextInput(attrs={'autocomplete': 'off',
                                            'placeholder': 'email',
                                            'title': '',
                                            'class': 'form_field'})
        }

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = ''
        self.fields['password'].label = ''
        self.fields['email'].label = ''


class AccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['image', 'status']


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'autofocus': True,
                                                                            'autocomplete': 'off',
                                                                            'placeholder': 'email',
                                                                            'title': '',
                                                                            'class': 'form_field'}))

    def __init__(self, *args, **kwargs):
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = ''

    def clean(self):
        if self.cleaned_data['email'] not in [user.email for user in User.objects.all()]:
            raise ValidationError('Пользователя с таким email не найдено')


class PasswordChangeForm(forms.Form):
    verification_code = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off',
                                                                      'placeholder': 'код подтверждения',
                                                                      'title': '',
                                                                      'class': 'form_field'}))

    password = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off',
                                                             'placeholder': 'новый пароль',
                                                             'title': '',
                                                             'class': 'form_field'}))

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['verification_code'].label = ''
        self.fields['password'].label = ''

    def clean(self):
        from .views import global_user_info

        if global_user_info['verification_code'] != self.cleaned_data['verification_code']:
            raise ValidationError('Неверный код подтверждения')
        if check_password(self.cleaned_data['password'], global_user_info['password']):
            raise ValidationError('Новый пароль не может совпадать со старым')
