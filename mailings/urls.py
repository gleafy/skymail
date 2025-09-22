from django.urls import path
from . import views

app_name = "mailings"

urlpatterns = [
    path("recipients/", views.RecipientListView.as_view(), name="recipients_list"),
    path("recipients/add/", views.RecipientCreateView.as_view(), name="recipients_add"),
    path("recipients/<int:pk>/edit/", views.RecipientUpdateView.as_view(), name="recipients_edit"),
    path("recipients/<int:pk>/delete/", views.RecipientDeleteView.as_view(), name="recipients_delete"),
    path("messages/", views.MessageListView.as_view(), name="messages_list"),
    path("messages/add/", views.MessageCreateView.as_view(), name="messages_add"),
    path("messages/<int:pk>/edit/", views.MessageUpdateView.as_view(), name="messages_edit"),
    path("messages/<int:pk>/delete/", views.MessageDeleteView.as_view(), name="messages_delete"),
    path("", views.MailingListView.as_view(), name="mailings_list"),
    path("add/", views.MailingCreateView.as_view(), name="mailings_add"),
    path("<int:pk>/edit/", views.MailingUpdateView.as_view(), name="mailings_edit"),
    path("<int:pk>/delete/", views.MailingDeleteView.as_view(), name="mailings_delete"),
    path("<int:pk>/send/", views.send_mailing_view, name="mailings_send"),
    path("attempts/", views.MailingAttemptListView.as_view(), name="attempts_list"),
    path("reports/", views.MailingReportView.as_view(), name="mailings_report"),
]
