from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy
from .forms import RegisterForm
from .models import User
from django.core.mail import send_mail

def manager_required(view_func):
    decorated_view_func = user_passes_test(
        lambda u: u.is_authenticated and u.groups.filter(name='Managers').exists(),
        login_url='/'
    )
    return decorated_view_func(view_func)

@manager_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'users/user_list.html', {'users': users})

@manager_required
def toggle_user_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    return redirect('user_list')

@manager_required
def disable_mailing(request, pk):
    from mailings.models import Mailing
    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.status = Mailing.STATUS_FINISHED
    mailing.save()
    return redirect('mailings:mailings_list')

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            subject = "Activate your account"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = request.build_absolute_uri(reverse("activate", args=(uid, token)))
            message = f"Activate: {link}"
            send_mail(subject, message, None, [user.email])
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect("/")
    return render(request, "users/activation_invalid.html")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "avatar", "phone", "country")


class ProfileView(DetailView):
    model = User
    template_name = "users/profile.html"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "users/profile_form.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user
