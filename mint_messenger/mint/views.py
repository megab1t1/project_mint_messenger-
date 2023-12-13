from os import listdir, remove
from datetime import date, timedelta
from json import loads, dumps
from django.db.models import Q
from copy import deepcopy
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, ListView, UpdateView
from django.http import HttpResponseRedirect
from mint_messenger.settings import LOGOUT_REDIRECT_URL, LOGIN_REDIRECT_URL, MEDIA_ROOT
from PIL import Image
from django.core.mail import send_mail
from random import randint

from .utils import *
from .forms import *
from .serializers import *


global_user_info = {}


class AccountPage(DataMixin, TemplateView, FormView):
    template_name = 'mint/account_page.html'
    form_class = AccountForm
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(LOGOUT_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)

        if request.FILES.get('image', None):
            User.objects.filter(id=self.request.user.id).update(
                image=self.handle_uploaded_file(form.files['image'].file, str(form.files['image']))
            )
        else:
            User.objects.filter(id=self.request.user.id).update(status=form.data['status'])

        return redirect('account')

    def handle_uploaded_file(self, file, filename):
        file_prefix = 1

        try:
            image = User.objects.get(id=self.request.user.id).image
        except:
            image = None

        if image:
            remove(MEDIA_ROOT + '/images/' + str(image))

        while filename in listdir(MEDIA_ROOT + '/images/'):
            if file_prefix == 1:
                filename = filename[:-4] + '_copy' + str(file_prefix) + '.jpg'
            else:
                filename = filename[:-10] + '_copy' + str(file_prefix) + '.jpg'

            file_prefix += 1

        Image.open(file).save(MEDIA_ROOT + '/images/' + filename, format='JPEG')

        return filename

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Аккаунт',
                                      option_selected=1,
                                      user=self.request.user)
        context = dict(list(context.items()) + list(c_def.items()))
        return context


class UserAccountPage(DataMixin, TemplateView):
    template_name = 'mint/user_page.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(LOGOUT_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        user = User.objects.get(id=self.kwargs['user'])
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Аккаунт пользователя ' + user.username,
                                      option_selected=3,
                                      user=user)
        context = dict(list(context.items()) + list(c_def.items()))
        return context


class Chats(DataMixin, ListView):
    model = User
    template_name = 'mint/chats.html'
    context_object_name = 'users'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(LOGOUT_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        users = []

        for user in User.objects.filter(~Q(id=self.request.user.id)):
            friend = user.id in loads(str(User.objects.get(id=self.request.user.id).friends))

            try:
                last_message = Messages.objects.filter(Q(user_to_id=self.request.user.id,
                                                         user_id=user.id) | Q(user_to_id=user.id,
                                                                              user_id=self.request.user.id)).last()
                last_message_date = get_date(last_message.send_time, '%d %b')
            except:
                last_message = None
                last_message_date = None

            users.append({'user': user,
                          'last_message': last_message,
                          'friend': friend,
                          'date': last_message_date})

        return users

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Сообщения',
                                      option_selected=2,
                                      get_url=User.get_absolute_url)
        context = dict(list(context.items()) + list(c_def.items()))
        return context


class Chat(DataMixin, ListView, FormView):
    form_class = SendMessageForm
    model = Messages
    template_name = 'mint/messages.html'
    context_object_name = 'messages'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(LOGOUT_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        messages = []
        user = self.kwargs['user']
        user_id = self.request.user.id
        previous_date = ''

        return get_messages(messages, user, user_id, previous_date)

    def post(self, request, *args, **kwargs):
        form_data = deepcopy(request.POST)
        form_data['user'] = request.user.id
        form_data['user_to'] = self.kwargs['user']
        form = SendMessageForm(form_data)

        if form.is_valid():
            try:
                form.save()
            except:
                form.add_error(None, 'ERROR')

        return HttpResponseRedirect('/chats/' + str(self.kwargs['user']))

    def get_context_data(self, *, object_list=None, **kwargs):
        current_user = User.objects.get(id=self.kwargs['user']).username
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Чат с ' + current_user,
                                      option_selected=2)
        context = dict(list(context.items()) + list(c_def.items()))
        return context


class Friends(DataMixin, ListView):
    model = User
    template_name = 'mint/friends.html'
    context_object_name = 'users'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(LOGOUT_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        users = []
        current_user = User.objects.get(id=self.request.user.id)

        for user in User.objects.filter(~Q(id=self.request.user.id)):
            confirm = user.id in loads(str(current_user.invites))
            invite = self.request.user.id in loads(str(user.invites)) and not confirm
            friend = user.id in loads(str(current_user.friends))

            users.append({
                'user': user,
                'confirm': confirm,
                'invite': invite,
                'friend': friend
            })

        return users

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Друзья',
                                      option_selected=3,
                                      invites=len(User.objects.get(id=self.request.user.id).invites) > 0,
                                      friends=len(User.objects.get(id=self.request.user.id).friends) > 0)
        context = dict(list(context.items()) + list(c_def.items()))
        return context


class RegisterPage(FormView):
    form_class = RegisterForm
    template_name = 'mint/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, User.objects.create_user(**form.cleaned_data))

        return HttpResponseRedirect(LOGIN_REDIRECT_URL)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context


class ForgotPassword(FormView):
    form_class = ForgotPasswordForm
    template_name = 'mint/forgot_password.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        verification_code = str()

        for i in range(8):
            verification_code += str(randint(0, 9))

        global global_user_info
        global_user_info['verification_code'] = verification_code

        send_mail(
            'Восстановление пароля',
            'Ваш код для восстановления пароля: ' + verification_code,
            'mint administration',
            [form.data['email']]
        )

        return HttpResponseRedirect(reverse('password_change', kwargs={
            'user': User.objects.get(email=form.data['email']).pk
        }))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Восстановление пароля'
        return context


class PasswordChange(FormView):
    form_class = PasswordChangeForm
    template_name = 'mint/password_change.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(LOGIN_REDIRECT_URL)

        global global_user_info
        global_user_info['password'] = User.objects.get(id=self.kwargs['user']).password

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = User.objects.get(id=self.kwargs['user'])
        user.set_password(form.data['password'])
        user.save()

        global_user_info.clear()

        return redirect('login_page')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Восстановление пароля'
        return context


class EditMessage(DataMixin, UpdateView):
    model = Messages
    pk_url_kwarg = 'message'
    template_name = 'mint/message_edit.html'
    form_class = EditMessageForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(LOGOUT_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def get_messages(self):
        messages = []
        user = self.kwargs['user']
        user_id = self.request.user.id
        previous_date = ''

        return get_messages(messages, user, user_id, previous_date)

    def get_success_url(self):
        return reverse_lazy('messages', kwargs={'user': self.kwargs['user']})

    def get_context_data(self, *, objects_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Чат с ' + User.objects.get(id=self.kwargs['user']).username,
                                      id=self.object.id,
                                      messages=self.get_messages(),
                                      option_selected=2)
        return dict(list(context.items()) + list(c_def.items()))


def send_invite(request, user):
    current_user = User.objects.get(id=user)
    new_invite = dumps([request.user.id])

    if len(current_user.invites) > 0:
        new_invite = dumps(loads(new_invite) + loads(str(current_user.invites)))

    User.objects.filter(id=user).update(invites=new_invite)

    return redirect('friends')


def cancel_invite(request, user):
    current_user = User.objects.get(id=user)
    invites = loads(str(current_user.invites))
    invites.remove(request.user.id)

    User.objects.filter(id=user).update(invites=invites)

    return redirect('friends')


def confirm_invite(request, user):
    current_user = User.objects.get(id=user)
    auth_user = User.objects.get(id=request.user.id)

    new_friend = dumps([auth_user.id])

    if len(current_user.friends) > 0:
        new_friend = dumps(loads(new_friend) + loads(str(current_user.friends)))

    User.objects.filter(id=user).update(friends=new_friend)

    invites = loads(str(auth_user.invites))
    invites.remove(user)

    new_friend = dumps([user])

    if len(auth_user.friends) > 0:
        new_friend = dumps(loads(new_friend) + loads(str(auth_user.friends)))

    User.objects.filter(id=auth_user.id).update(invites=invites, friends=new_friend)

    return redirect('friends')


def remove_friend(request, user):
    current_user = User.objects.get(id=user)
    auth_user = User.objects.get(id=request.user.id)

    friends = loads(str(auth_user.friends))
    friends.remove(current_user.id)

    User.objects.filter(id=auth_user.id).update(friends=friends)

    friends = loads(str(current_user.friends))
    friends.remove(auth_user.id)

    User.objects.filter(id=current_user.id).update(friends=friends)

    return redirect('friends')


def get_date(given_date, date_shape):
    if date.today().strftime('%Y') == given_date.strftime('%Y'):
        if date.today() == given_date.date():
            message_date = 'Today'
        elif date.today() - timedelta(days=1) == given_date.date():
            message_date = 'Yesterday'
        else:
            message_date = given_date.strftime(date_shape)
    else:
        message_date = given_date.strftime(date_shape + ', %Y')

    return message_date


def edit_message(request, message):
    Messages.objects.get(id=message)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def delete_message(request, message):
    Messages.objects.get(id=message).delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def get_messages(messages, user, user_id, previous_date):
    try:
        last_message = Messages.objects.filter(Q(user_to_id=user_id,
                                                 user_id=user) | Q(user_to_id=user,
                                                                   user_id=user_id)).last()
    except:
        last_message = None

    for m in Messages.objects.filter(user_to_id__in=[user, user_id],
                                     user_id__in=[user, user_id]):
        date_var = get_date(m.send_time, '%d %B')
        message_date = date_var if date_var != previous_date else None
        previous_date = date_var

        is_last = True if last_message and m.id == last_message.id else False

        messages.append({'message': m,
                         'send_time': m.send_time,
                         'is_my': m.user_id == user_id,
                         'is_read': m.is_read,
                         'is_last': is_last,
                         'date': message_date})

    Messages.objects.filter(user_to_id=user_id, user_id=user).update(is_read=True)

    return messages
