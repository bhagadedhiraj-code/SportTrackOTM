from django.db import models
from django.contrib.auth.models import User


class Coach(models.Model):
    """Cricket coach model."""

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coach_profile'
    )

    name = models.CharField(max_length=100)

    profile_photo = models.ImageField(
        upload_to='coaches/',
        blank=True,
        null=True
    )

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    experience = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. 10 years"
    )

    specialization = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. Batting Coach, Bowling Coach"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ],
        default='active'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Coaches"


class Team(models.Model):
    """Cricket team model."""

    name = models.CharField(max_length=100)

    logo = models.ImageField(
        upload_to='teams/',
        blank=True,
        null=True
    )

    coach = models.ForeignKey(
        Coach,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teams'
    )

    city = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    established_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ],
        default='active'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def player_count(self):
        return self.players.count()

    @property
    def active_players(self):
        return self.players.filter(status='active')


class Player(models.Model):
    """Cricket player model."""

    PLAYING_ROLE_CHOICES = [
        ('batsman', 'Batsman'),
        ('bowler', 'Bowler'),
        ('all_rounder', 'All-rounder'),
        ('wicket_keeper', 'Wicket-keeper'),
    ]

    BATTING_STYLE_CHOICES = [
        ('right_hand', 'Right Hand'),
        ('left_hand', 'Left Hand'),
    ]

    BOWLING_STYLE_CHOICES = [
        ('right_arm_fast', 'Right-arm Fast'),
        ('left_arm_fast', 'Left-arm Fast'),
        ('right_arm_medium', 'Right-arm Medium'),
        ('left_arm_medium', 'Left-arm Medium'),
        ('right_arm_spin', 'Right-arm Spin'),
        ('left_arm_spin', 'Left-arm Spin'),
        ('none', 'None'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='player_profile'
    )

    name = models.CharField(max_length=100)

    profile_photo = models.ImageField(
        upload_to='players/',
        blank=True,
        null=True
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='players'
    )

    date_of_birth = models.DateField(null=True, blank=True)
    jersey_number = models.IntegerField(null=True, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    playing_role = models.CharField(
        max_length=20,
        choices=PLAYING_ROLE_CHOICES,
        default='batsman'
    )

    batting_style = models.CharField(
        max_length=20,
        choices=BATTING_STYLE_CHOICES,
        default='right_hand'
    )

    bowling_style = models.CharField(
        max_length=25,
        choices=BOWLING_STYLE_CHOICES,
        default='none'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('injured', 'Injured'),
        ],
        default='active'
    )

    join_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def age(self):
        if self.date_of_birth:
            from datetime import date

            today = date.today()

            return (
                today.year
                - self.date_of_birth.year
                - (
                    (today.month, today.day)
                    < (
                        self.date_of_birth.month,
                        self.date_of_birth.day
                    )
                )
            )

        return None


class Venue(models.Model):
    """Cricket venue model."""

    PITCH_TYPE_CHOICES = [
        ('turf', 'Turf'),
        ('natural_turf', 'Natural Turf'),
        ('artificial_turf', 'Artificial Turf'),
        ('cement', 'Cement'),
        ('matting', 'Matting'),
        ('clay', 'Clay'),
        ('hybrid', 'Hybrid'),
    ]

    name = models.CharField(max_length=200)

    address = models.TextField(blank=True)

    city = models.CharField(max_length=100)

    capacity = models.IntegerField(
        null=True,
        blank=True
    )

    pitch_type = models.CharField(
        max_length=20,
        choices=PITCH_TYPE_CHOICES,
        default='turf'
    )

    is_available = models.BooleanField(default=True)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.name}, {self.city}"


class Tournament(models.Model):
    """Cricket tournament model."""

    FORMAT_CHOICES = [
        ('t20', 'T20'),
        ('odi', 'ODI'),
        ('test', 'Test'),
    ]

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('registration', 'Registration Open'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)

    location = models.CharField(
        max_length=200,
        blank=True
    )

    start_date = models.DateField()

    end_date = models.DateField()

    registration_deadline = models.DateField(
        null=True,
        blank=True
    )

    tournament_format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        default='t20'
    )

    description = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name