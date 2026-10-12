from django.db import models
from django.contrib.auth.models import User
from teams.models import Team, Player, Venue, Coach


class TrainingSession(models.Model):
    """Training session model."""

    TYPE_CHOICES = [
        ('batting', 'Batting Practice'),
        ('bowling', 'Bowling Practice'),
        ('fielding', 'Fielding Practice'),
        ('fitness', 'Fitness Training'),
        ('match_simulation', 'Match Simulation'),
        ('net_practice', 'Net Practice'),
        ('general', 'General Training'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='training_sessions')
    coach = models.ForeignKey(Coach, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True)
    training_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.team.name} - {self.get_training_type_display()} ({self.date})"


class Attendance(models.Model):
    """Player attendance for training sessions."""

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]

    training_session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='attendance_records')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ['training_session', 'player']

    def __str__(self):
        return f"{self.player.name} - {self.get_status_display()}"
