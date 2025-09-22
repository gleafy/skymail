from django.db import models
from django.conf import settings


class Recipient(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipients")

    def __str__(self):
        return self.email

    class Meta:
        permissions = [("view_all_recipients", "Can view all recipients")]


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages")

    def __str__(self):
        return self.subject

    class Meta:
        permissions = [("view_all_messages", "Can view all messages")]


class Mailing(models.Model):
    STATUS_CREATED = "created"
    STATUS_RUNNING = "running"
    STATUS_FINISHED = "finished"
    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_RUNNING, "Запущена"),
        (STATUS_FINISHED, "Завершена"),
    ]
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="mailings")
    recipients = models.ManyToManyField(Recipient, related_name="mailings")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mailings")

    def __str__(self):
        return f"Mailing {self.pk} {self.status}"

    class Meta:
        permissions = [("view_all_mailings", "Can view all mailings")]


class MailingAttempt(models.Model):
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Успешно"),
        (STATUS_FAILED, "Не успешно"),
    ]
    at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    response = models.TextField(blank=True)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name="attempts")

    def __str__(self):
        return f"Attempt {self.pk} for {self.mailing_id}"
