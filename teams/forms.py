from django import forms
from .models import Team, Player, Coach, Venue, Tournament


class TeamForm(forms.ModelForm):

    class Meta:
        model = Team
        fields = [
            "name",
            "logo",
            "coach",
            "city",
            "description",
            "established_date",
            "status",
        ]

        widgets = {
            "established_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Enter team details"
                }
            ),
        }


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = [
            "user",
            "name",
            "profile_photo",
            "team",
            "date_of_birth",
            "jersey_number",
            "email",
            "phone",
            "playing_role",
            "batting_style",
            "bowling_style",
            "status",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


class CoachForm(forms.ModelForm):

    class Meta:
        model = Coach
        fields = [
            "user",
            "name",
            "profile_photo",
            "email",
            "phone",
            "experience",
            "specialization",
            "status",
        ]

        widgets = {
            "experience": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Enter coaching experience"
                }
            ),
        }


class VenueForm(forms.ModelForm):

    class Meta:
        model = Venue
        fields = [
            "name",
            "address",
            "city",
            "capacity",
            "pitch_type",
            "is_available",
            "description",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Enter venue details"
                }
            ),
        }


class TournamentForm(forms.ModelForm):

    class Meta:
        model = Tournament
        fields = [
            "name",
            "location",
            "start_date",
            "end_date",
            "registration_deadline",
            "tournament_format",
            "description",
            "status",
        ]

        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "registration_deadline": forms.DateInput(
                attrs={"type": "date"}
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Enter tournament details"
                }
            ),
        }