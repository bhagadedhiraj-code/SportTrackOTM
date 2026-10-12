from django.db import models
from django.contrib.auth.models import User
from teams.models import Team
from tournaments.models import Tournament


class Announcement(models.Model):
    """Announcements from admin, coach, or organizer."""

    TARGET_CHOICES = [
        ('all', 'All Users'),
        ('players', 'All Players'),
        ('coaches', 'All Coaches'),
        ('team', 'Specific Team'),
        ('tournament', 'Tournament Participants'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    target = models.CharField(max_length=20, choices=TARGET_CHOICES, default='all')
    target_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    target_tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Notification(models.Model):
    """User notifications."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.CharField(max_length=500)
    notification_type = models.CharField(max_length=50, default='info')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class ActivityLog(models.Model):
    """Audit trail for important actions."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action = models.CharField(max_length=100)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action} ({self.timestamp})"
