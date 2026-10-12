from django.db import models
from django.contrib.auth.models import User
from teams.models import Team, Player, Venue


class Tournament(models.Model):
    """Cricket tournament model."""

    FORMAT_CHOICES = [
        ('league', 'League'),
        ('knockout', 'Knockout'),
        ('league_knockout', 'League + Knockout'),
    ]

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('registration_open', 'Registration Open'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='organized_tournaments')
    location = models.CharField(max_length=200)
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    registration_deadline = models.DateField(null=True, blank=True)
    tournament_format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='league')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='upcoming')
    points_for_win = models.IntegerField(default=2)
    points_for_tie = models.IntegerField(default=1)
    points_for_no_result = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TournamentRegistration(models.Model):
    """Team registration for tournaments."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='registrations')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='tournament_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ['tournament', 'team']

    def __str__(self):
        return f"{self.team.name} - {self.tournament.name}"


class PointsTable(models.Model):
    """Tournament standings / points table."""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='points_table')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='points_entries')
    played = models.IntegerField(default=0)
    won = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    tied = models.IntegerField(default=0)
    no_result = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    net_run_rate = models.FloatField(default=0.0)

    class Meta:
        unique_together = ['tournament', 'team']
        ordering = ['-points', '-net_run_rate']

    def __str__(self):
        return f"{self.team.name} - {self.tournament.name} ({self.points} pts)"

    @property
    def position(self):
        entries = PointsTable.objects.filter(tournament=self.tournament).order_by('-points', '-net_run_rate')
        for i, entry in enumerate(entries, 1):
            if entry.pk == self.pk:
                return i
        return 0
