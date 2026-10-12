from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta

from .models import UserProfile
from .forms import LoginForm, RegisterForm, ProfileForm, UserCreateForm
from .decorators import admin_required, role_required

from teams.models import Team, Player, Coach, Venue
from matches.models import Match
from tournaments.models import Tournament, TournamentRegistration
from training.models import TrainingSession, Attendance
from notifications.models import Notification, ActivityLog, Announcement

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request, "accounts/dashboard.html")


@login_required
def admin_dashboard(request):
    return render(request, "accounts/admin_dashboard.html")


@login_required
def coach_dashboard(request):
    return render(request, "accounts/coach_dashboard.html")


@login_required
def player_dashboard(request):
    return render(request, "accounts/player_dashboard.html")
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                if hasattr(user, 'profile') and not user.profile.is_active_account:
                    messages.error(request, 'Your account has been deactivated. Contact admin.')
                    return render(request, 'accounts/login.html', {'form': form})
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role='player')
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to SportTrackOTM.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    """Route to appropriate dashboard based on role."""
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    if hasattr(request.user, 'profile'):
        role = request.user.profile.role
        if role == 'admin':
            return redirect('admin_dashboard')
        elif role == 'coach':
            return redirect('coach_dashboard')
        elif role == 'player':
            return redirect('player_dashboard')
        elif role == 'organizer':
            return redirect('organizer_dashboard')
    return redirect('admin_dashboard')


@login_required
@admin_required
def admin_dashboard(request):
    today = timezone.now().date()
    context = {
        'total_teams': Team.objects.count(),
        'total_players': Player.objects.count(),
        'total_coaches': Coach.objects.count(),
        'total_tournaments': Tournament.objects.count(),
        'upcoming_matches': Match.objects.filter(status='scheduled', date__gte=today).count(),
        'completed_matches': Match.objects.filter(status='completed').count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_venues': Venue.objects.count(),
        'recent_activities': ActivityLog.objects.all()[:10],
        'upcoming_matches_list': Match.objects.filter(status='scheduled', date__gte=today).order_by('date')[:5],
        'recent_results': Match.objects.filter(status='completed').order_by('-date')[:5],
        # Chart data
        'teams_by_city': list(Team.objects.values('city').annotate(count=Count('id')).order_by('-count')[:10]),
        'players_by_role': list(Player.objects.values('playing_role').annotate(count=Count('id'))),
        'matches_by_status': list(Match.objects.values('status').annotate(count=Count('id'))),
        'tournaments_by_status': list(Tournament.objects.values('status').annotate(count=Count('id'))),
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def coach_dashboard(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role in ['coach', 'admin'])):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    today = timezone.now().date()
    # Get coach's team(s)
    my_teams = Team.objects.none()
    if hasattr(request.user, 'coach_profile'):
        my_teams = request.user.coach_profile.teams.all()
    elif request.user.is_superuser:
        my_teams = Team.objects.all()

    team_ids = my_teams.values_list('id', flat=True)
    my_players = Player.objects.filter(team_id__in=team_ids)

    context = {
        'my_teams': my_teams,
        'my_team': my_teams.first(),
        'total_players': my_players.count(),
        'upcoming_matches': Match.objects.filter(
            Q(team1_id__in=team_ids) | Q(team2_id__in=team_ids),
            status='scheduled', date__gte=today
        ).order_by('date')[:5],
        'recent_results': Match.objects.filter(
            Q(team1_id__in=team_ids) | Q(team2_id__in=team_ids),
            status='completed'
        ).order_by('-date')[:5],
        'training_sessions': TrainingSession.objects.filter(team_id__in=team_ids, date__gte=today).order_by('date')[:5],
        'my_players': my_players,
    }
    return render(request, 'accounts/coach_dashboard.html', context)


@login_required
def player_dashboard(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role in ['player', 'admin'])):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    today = timezone.now().date()
    player = None
    my_team = None
    if hasattr(request.user, 'player_profile'):
        player = request.user.player_profile
        my_team = player.team

    context = {
        'player': player,
        'my_team': my_team,
    }

    if my_team:
        context['teammates'] = Player.objects.filter(team=my_team).exclude(id=player.id if player else 0)
        context['upcoming_matches'] = Match.objects.filter(
            Q(team1=my_team) | Q(team2=my_team),
            status='scheduled', date__gte=today
        ).order_by('date')[:5]
        context['recent_results'] = Match.objects.filter(
            Q(team1=my_team) | Q(team2=my_team),
            status='completed'
        ).order_by('-date')[:5]
        context['training_sessions'] = TrainingSession.objects.filter(team=my_team, date__gte=today).order_by('date')[:5]

    context['notifications'] = Notification.objects.filter(user=request.user, is_read=False)[:5]
    return render(request, 'accounts/player_dashboard.html', context)


@login_required
def organizer_dashboard(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role in ['organizer', 'admin'])):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    today = timezone.now().date()
    my_tournaments = Tournament.objects.all()
    if not request.user.is_superuser and hasattr(request.user, 'profile') and request.user.profile.role == 'organizer':
        my_tournaments = Tournament.objects.filter(organizer=request.user)

    context = {
        'active_tournaments': my_tournaments.filter(status__in=['ongoing', 'registration_open']),
        'all_tournaments': my_tournaments,
        'total_tournaments': my_tournaments.count(),
        'upcoming_matches': Match.objects.filter(status='scheduled', date__gte=today, tournament__in=my_tournaments).order_by('date')[:5],
        'completed_matches': Match.objects.filter(status='completed', tournament__in=my_tournaments).order_by('-date')[:5],
        'pending_registrations': TournamentRegistration.objects.filter(tournament__in=my_tournaments, status='pending'),
        'venues': Venue.objects.all(),
    }
    return render(request, 'accounts/organizer_dashboard.html', context)


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'admin' if request.user.is_superuser else 'player'})
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


# ============ User Management (Admin) ============

@login_required
@admin_required
def user_list(request):
    users = User.objects.all().select_related('profile').order_by('-date_joined')
    search = request.GET.get('search', '')
    if search:
        users = users.filter(Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search))
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(profile__role=role_filter)
    return render(request, 'accounts/user_list.html', {'users': users, 'search': search, 'role_filter': role_filter})


@login_required
@admin_required
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                phone=form.cleaned_data.get('phone', '')
            )
            ActivityLog.objects.create(user=request.user, action='User Created', description=f'Created user: {user.username} with role: {form.cleaned_data["role"]}')
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('user_list')
    else:
        form = UserCreateForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create User'})


@login_required
@admin_required
def user_toggle_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('user_list')
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.is_active_account = not profile.is_active_account
    profile.save()
    user.is_active = profile.is_active_account
    user.save()
    status = 'activated' if profile.is_active_account else 'deactivated'
    ActivityLog.objects.create(user=request.user, action=f'User {status.title()}', description=f'{status.title()} user: {user.username}')
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('user_list')


@login_required
@admin_required
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('user_list')
    if request.method == 'POST':
        username = user.username
        user.delete()
        ActivityLog.objects.create(user=request.user, action='User Deleted', description=f'Deleted user: {username}')
        messages.success(request, f'User {username} has been deleted.')
        return redirect('user_list')
    return render(request, 'accounts/user_confirm_delete.html', {'target_user': user})


@login_required
@admin_required
def activity_log_view(request):
    logs = ActivityLog.objects.all()[:100]
    return render(request, 'notifications/activity_log.html', {'logs': logs})
