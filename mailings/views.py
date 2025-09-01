from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Count, Q
from django.urls import reverse_lazy
from .models import Recipient, Message, Mailing, MailingAttempt
from .forms import RecipientForm, MessageForm, MailingForm
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.http import HttpResponseForbidden
import logging

logger = logging.getLogger(__name__)


def is_manager(user):
    return user.groups.filter(name="Managers").exists()


@cache_page(60)
def home(request):
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(status=Mailing.STATUS_RUNNING).count()
    unique_recipients = Recipient.objects.count()
    return render(
        request,
        "home.html",
        {"total_mailings": total_mailings, "active_mailings": active_mailings, "unique_recipients": unique_recipients},
    )


class OwnerFilteredMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated and is_manager(self.request.user):
            return qs  # Менеджеры видят все объекты
        if self.request.user.is_authenticated:
            return qs.filter(owner=self.request.user)
        return qs.none()

    def dispatch(self, request, *args, **kwargs):
        if is_manager(request.user) and request.method not in ['GET', 'HEAD']:
            return HttpResponseForbidden("Managers can only view objects")
        return super().dispatch(request, *args, **kwargs)


class RecipientListView(OwnerFilteredMixin, ListView):
    model = Recipient
    template_name = "mailings/recipient_list.html"


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailings/recipient_form.html"
    success_url = reverse_lazy("mailings:recipients_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(OwnerFilteredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailings/recipient_form.html"
    success_url = reverse_lazy("mailings:recipients_list")


class RecipientDeleteView(OwnerFilteredMixin, DeleteView):
    model = Recipient
    template_name = "mailings/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailings:recipients_list")


class MessageListView(OwnerFilteredMixin, ListView):
    model = Message
    template_name = "mailings/message_list.html"


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:messages_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(OwnerFilteredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailings/message_form.html"
    success_url = reverse_lazy("mailings:messages_list")

class MessageDeleteView(OwnerFilteredMixin, DeleteView):
    model = Message
    template_name = "mailings/message_confirm_delete.html"
    success_url = reverse_lazy("mailings:messages_list")


class MailingListView(OwnerFilteredMixin, ListView):
    model = Mailing
    template_name = "mailings/mailing_list.html"


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:mailings_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(OwnerFilteredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:mailings_list")


class MailingDeleteView(OwnerFilteredMixin, DeleteView):
    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:mailings_list")


@login_required
def send_mailing_view(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if not (mailing.owner == request.user or is_manager(request.user)):
        return redirect("mailings:mailings_list")
    recipients = list(mailing.recipients.values_list("email", flat=True))
    try:
        subject = mailing.message.subject
        body = mailing.message.body
        sent = send_mail(subject, body, settings.SERVER_EMAIL or None, recipients)
        status = MailingAttempt.STATUS_SUCCESS if sent else MailingAttempt.STATUS_FAILED
        response = f"sent_count={sent}"
    except Exception as e:
        status = MailingAttempt.STATUS_FAILED
        response = str(e)
    MailingAttempt.objects.create(mailing=mailing, status=status, response=response)
    mailing.status = Mailing.STATUS_RUNNING if status == MailingAttempt.STATUS_SUCCESS else mailing.status
    mailing.save()
    return redirect("mailings:mailings_list")


class MailingAttemptListView(ListView):
    model = MailingAttempt
    template_name = "mailings/attempt_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated and is_manager(self.request.user):
            return qs
        if self.request.user.is_authenticated:
            return qs.filter(mailing__owner=self.request.user)
        return qs.none()


class MailingReportView(OwnerFilteredMixin, ListView):
    model = Mailing
    template_name = "mailings/mailing_report.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(
            success_count=Count("attempts", filter=Q(attempts__status=MailingAttempt.STATUS_SUCCESS)),
            fail_count=Count("attempts", filter=Q(attempts__status=MailingAttempt.STATUS_FAILED)),
        )
