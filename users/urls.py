from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import ProfileView, ProfileUpdateView

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("activate/<uidb64>/<token>/", views.activate_view, name="activate"),
    path("login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(template_name="users/password_reset_form.html"),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/toggle/', views.toggle_user_active, name='toggle_user_active'),
    path('mailings/<int:pk>/disable/', views.disable_mailing, name='disable_mailing'),
]
