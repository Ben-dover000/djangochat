from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    name = models.CharField(max_length=23)
    slug = models.SlugField(unique=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='owned_rooms',
        on_delete=models.CASCADE
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='rooms',
        blank=True
    )
    is_private = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.owner.username}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)

class Invitation(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    invited_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )
    accepted = models.BooleanField(null=True)   # None = pending, True = accepted, False = rejected
    viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('room', 'invited_user', 'accepted')

    def accept(self):
        # Only process if pending
        if self.accepted is None:
            # Delete any other accepted invitations for this user/room
            Invitation.objects.filter(
                room=self.room,
                invited_user=self.invited_user,
                accepted=True
            ).exclude(id=self.id).delete()

            self.accepted = True
            self.viewed = True
            self.save()

            # Add user to participants
            self.room.participants.add(self.invited_user)

            # Create system message
            Message.objects.create(
                room=self.room,
                user=self.invited_user,
                content=f"{self.invited_user.username} aceitou o convite! Diz olá."
            )

    def reject(self):
        if self.accepted is None:
            self.accepted = False
            self.viewed = True
            self.save()
            Message.objects.create(
                room=self.room,
                user=self.invited_user,
                content=f"{self.invited_user.username} rejeitou o convite :(."
            )
