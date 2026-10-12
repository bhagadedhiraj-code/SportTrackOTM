from django.db import models
from django.contrib.auth.models import User
from teams.models import Team, Player, Venue, Tournament


class Match(models.Model):

    FORMAT_CHOICES = [
        ("t10", "T10"),
        ("t20", "T20"),
        ("odi", "ODI"),
        ("test", "Test"),
        ("custom", "Custom"),
    ]

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("live", "Live"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("abandoned", "Abandoned"),
    ]

    TOSS_DECISION_CHOICES = [
        ("bat", "Bat"),
        ("bowl", "Bowl"),
    ]

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches",
    )

    team1 = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="home_matches",
    )

    team2 = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="away_matches",
    )

    venue = models.ForeignKey(
        Venue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches",
    )

    date = models.DateField()
    time = models.TimeField()

    match_format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        default="t20",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="scheduled",
    )

    toss_winner = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="toss_wins",
    )

    toss_decision = models.CharField(
        max_length=10,
        choices=TOSS_DECISION_CHOICES,
        blank=True,
    )

    # SCORE
    team1_score = models.IntegerField(default=0)
    team1_wickets = models.IntegerField(default=0)
    team1_overs = models.FloatField(default=0)

    team2_score = models.IntegerField(default=0)
    team2_wickets = models.IntegerField(default=0)
    team2_overs = models.FloatField(default=0)

    winner = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="match_wins",
    )

    result = models.CharField(
        max_length=255,
        blank=True,
        help_text="Example: Pune Warriors won by 5 wickets",
    )

    player_of_match = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="motm_awards",
    )

    match_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Matches"
        ordering = ["-date", "-time"]

    def __str__(self):
        return f"{self.team1} vs {self.team2}"


class Innings(models.Model):

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="innings",
    )

    batting_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="batting_innings",
    )

    bowling_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="bowling_innings",
    )

    innings_number = models.IntegerField(default=1)
    runs = models.IntegerField(default=0)
    wickets = models.IntegerField(default=0)
    overs = models.FloatField(default=0)
    extras = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.match} - Innings {self.innings_number}"


class BattingScore(models.Model):

    innings = models.ForeignKey(
        Innings,
        on_delete=models.CASCADE,
        related_name="batting_scores",
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="batting_scores",
    )

    runs = models.IntegerField(default=0)
    balls = models.IntegerField(default=0)
    fours = models.IntegerField(default=0)
    sixes = models.IntegerField(default=0)
    is_out = models.BooleanField(default=False)

    how_out = models.CharField(
        max_length=100,
        blank=True,
    )

    def __str__(self):
        return f"{self.player} - {self.runs} runs"


class BowlingScore(models.Model):

    innings = models.ForeignKey(
        Innings,
        on_delete=models.CASCADE,
        related_name="bowling_scores",
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="bowling_scores",
    )

    overs = models.FloatField(default=0)
    maidens = models.IntegerField(default=0)
    runs_conceded = models.IntegerField(default=0)
    wickets = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.player} - {self.wickets} wickets"


class PlayerMatchPerformance(models.Model):

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="performances",
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="match_performances",
    )

    catches = models.IntegerField(default=0)
    run_outs = models.IntegerField(default=0)
    stumpings = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.player} - {self.match}"