from django import forms
from .models import Match
from teams.models import Tournament


class MatchForm(forms.ModelForm):

    tournament = forms.ModelChoiceField(
        queryset=Tournament.objects.all(),
        required=False,
        empty_label="Select Tournament",
    )

    class Meta:
        model = Match

        fields = [
            "tournament",
            "team1",
            "team2",
            "venue",
            "date",
            "time",
            "match_format",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
        }


class MatchResultForm(forms.ModelForm):

    class Meta:
        model = Match

        fields = [
            "team1_score",
            "team1_wickets",
            "team1_overs",
            "team2_score",
            "team2_wickets",
            "team2_overs",
            "winner",
            "result",
            "player_of_match",
            "match_notes",
        ]

        widgets = {
            "team1_score": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "team1_wickets": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 10}
            ),
            "team1_overs": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "step": "0.1"}
            ),
            "team2_score": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "team2_wickets": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 10}
            ),
            "team2_overs": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "step": "0.1"}
            ),
            "result": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Pune Warriors won by 5 wickets",
                }
            ),
            "match_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Additional match notes",
                }
            ),
        }