from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from django.core.mail import send_mail
from django.conf import settings

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        # Отправка письма с логином (пароль не отправляем!)
        send_mail(
            subject='Регистрация на сайте',
            message=f'Здравствуйте, {user.username}!\nВы успешно зарегистрированы.\nВаш логин: {user.username}',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            recipient_list=[user.email],
            fail_silently=True,
        )
        return response

# Create your views here.
