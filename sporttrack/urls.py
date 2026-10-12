from django.contrib import admin
from django.urls import path, include

from teams.views import (
    home,

    # Teams
    team_list,
    team_detail,
    add_team,
    edit_team,
    delete_team,

    # Players
    player_list,
    player_detail,
    add_player,
    edit_player,
    delete_player,

    # Coaches
    coach_list,
    coach_detail,
    add_coach,
    edit_coach,
    delete_coach,

    # Venues
    venue_list,
    add_venue,
    edit_venue,
    delete_venue,

    # Matches
    match_list,
    add_match,
    update_match_result,

    # Tournaments
    tournament_list,
    add_tournament,
    tournament_edit,
    tournament_delete,
)


urlpatterns = [

    # =========================
    # ADMIN
    # =========================
    path("admin/", admin.site.urls),

    # =========================
    # ACCOUNTS
    # =========================
    
    path("accounts/", include("accounts.urls")),

    # =========================
    # HOME
    # =========================
    path("", home, name="home"),

    # =========================
    # TEAMS
    # =========================
    path("teams/", team_list, name="team_list"),
    path("teams/<int:id>/", team_detail, name="team_detail"),
    path("teams/add/", add_team, name="add_team"),
    path("teams/edit/<int:id>/", edit_team, name="edit_team"),
    path("teams/delete/<int:id>/", delete_team, name="delete_team"),

    # =========================
    # PLAYERS
    # =========================
    path("teams/players/", player_list, name="player_list"),
    path("teams/players/add/", add_player, name="add_player"),
    path("teams/players/<int:id>/", player_detail, name="player_detail"),
    path("teams/players/edit/<int:id>/", edit_player, name="edit_player"),
    path("teams/players/delete/<int:id>/", delete_player, name="delete_player"),

    # =========================
    # COACHES
    # =========================
    path("teams/coaches/", coach_list, name="coach_list"),
    path("teams/coaches/add/", add_coach, name="add_coach"),
    path("teams/coaches/<int:id>/", coach_detail, name="coach_detail"),
    path("teams/coaches/edit/<int:id>/", edit_coach, name="edit_coach"),
    path("teams/coaches/delete/<int:id>/", delete_coach, name="delete_coach"),

    # =========================
    # VENUES
    # =========================
    path("teams/venues/", venue_list, name="venue_list"),
    path("teams/venues/add/", add_venue, name="add_venue"),
    path("teams/venues/edit/<int:id>/", edit_venue, name="edit_venue"),
    path("teams/venues/delete/<int:id>/", delete_venue, name="delete_venue"),

    # =========================
    # MATCHES
    # =========================
    path("teams/matches/", match_list, name="match_list"),
    path("teams/matches/add/", add_match, name="add_match"),
    path(
        "teams/matches/<int:id>/result/",
        update_match_result,
        name="update_match_result",
    ),

    # =========================
    # TOURNAMENTS
    # =========================
    path("teams/tournaments/", tournament_list, name="tournament_list"),
    path("teams/tournaments/add/", add_tournament, name="add_tournament"),
    path(
        "teams/tournaments/edit/<int:id>/",
        tournament_edit,
        name="tournament_edit",
    ),
    path(
        "teams/tournaments/delete/<int:id>/",
        tournament_delete,
        name="tournament_delete",
    ),
]