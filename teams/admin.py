from django.contrib import admin
from .models import Team, Player, Tournament
from matches.models import Match
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(Tournament)