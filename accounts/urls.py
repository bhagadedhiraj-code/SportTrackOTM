from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("coach-dashboard/", views.coach_dashboard, name="coach_dashboard"),
    path("player-dashboard/", views.player_dashboard, name="player_dashboard"),
    path("organizer-dashboard/", views.organizer_dashboard, name="organizer_dashboard"),

    path("profile/", views.profile_view, name="profile"),

    path("users/", views.user_list, name="user_list"),
    path("users/add/", views.user_create, name="user_create"),
    path(
        "users/<int:user_id>/toggle/",
        views.user_toggle_status,
        name="user_toggle_status",
    ),
    path(
        "users/<int:user_id>/delete/",
        views.user_delete,
        name="user_delete",
    ),

    path("activity-log/", views.activity_log_view, name="activity_log"),
]