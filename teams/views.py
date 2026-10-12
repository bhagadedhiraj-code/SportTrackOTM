from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count

from .models import Team, Player, Coach, Venue
from .forms import (
    TeamForm,
    PlayerForm,
    CoachForm,
    VenueForm,
)

from accounts.decorators import (
    admin_required,
    coach_required,
    staff_required,
)

from notifications.models import ActivityLog


# ============================================================
# HOME
# ============================================================

def home(request):
    return render(request, 'home.html')


# ============================================================
# MATCHES
# ============================================================

@login_required
def match_list(request):
    from matches.models import Match

    matches = Match.objects.all().select_related(
        'team1',
        'team2',
        'venue',
        'tournament'
    ).order_by('-date', '-time')

    return render(
        request,
        'matches/match_list.html',
        {
            'matches': matches
        }
    )


@login_required
@staff_required
def add_match(request):
    from matches.forms import MatchForm

    if request.method == 'POST':
        form = MatchForm(request.POST)

        if form.is_valid():
            match = form.save()

            ActivityLog.objects.create(
                user=request.user,
                action='Match Added',
                description=f'Added match: {match.team1} vs {match.team2}'
            )

            messages.success(
                request,
                'Match added successfully.'
            )

            return redirect('match_list')

    else:
        form = MatchForm()

    return render(
        request,
        'matches/match_form.html',
        {
            'form': form,
            'title': 'Add New Match'
        }
    )


@login_required
@staff_required
def update_match_result(request, id):
    from matches.models import Match
    from matches.forms import MatchResultForm

    match = get_object_or_404(Match, id=id)

    if request.method == 'POST':
        form = MatchResultForm(
            request.POST,
            instance=match
        )

        if form.is_valid():
            form.save()

            ActivityLog.objects.create(
                user=request.user,
                action='Match Result Updated',
                description=f'Updated result: {match.team1} vs {match.team2}'
            )

            messages.success(
                request,
                'Match result updated successfully.'
            )

            return redirect('match_list')

    else:
        form = MatchResultForm(instance=match)

    return render(
        request,
        'matches/match_result_form.html',
        {
            'form': form,
            'match': match,
            'title': 'Update Match Result'
        }
    )


# ============================================================
# TOURNAMENTS
# ============================================================

@login_required
def tournament_list(request):
    from .models import Tournament

    tournaments = Tournament.objects.all().order_by(
        '-start_date'
    )

    return render(
        request,
        'teams/tournament_list.html',
        {
            'tournaments': tournaments
        }
    )


@login_required
@staff_required
def add_tournament(request):
    from .models import Tournament
    from .forms import TournamentForm

    if request.method == 'POST':
        form = TournamentForm(request.POST)

        if form.is_valid():
            tournament = form.save()

            ActivityLog.objects.create(
                user=request.user,
                action='Tournament Added',
                description=f'Added tournament: {tournament.name}'
            )

            messages.success(
                request,
                'Tournament added successfully.'
            )

            return redirect('tournament_list')

    else:
        form = TournamentForm()

    return render(
        request,
        'teams/tournament_form.html',
        {
            'form': form,
            'title': 'Add New Tournament'
        }
    )


@login_required
@staff_required
def tournament_edit(request, id):
    from .models import Tournament
    from .forms import TournamentForm

    tournament = get_object_or_404(Tournament, id=id)

    if request.method == 'POST':
        form = TournamentForm(
            request.POST,
            instance=tournament
        )

        if form.is_valid():
            tournament = form.save()

            ActivityLog.objects.create(
                user=request.user,
                action='Tournament Updated',
                description=f'Updated tournament: {tournament.name}'
            )

            messages.success(
                request,
                'Tournament updated successfully.'
            )

            return redirect('tournament_list')
    else:
        form = TournamentForm(instance=tournament)

    return render(
        request,
        'teams/tournament_form.html',
        {
            'form': form,
            'tournament': tournament,
            'title': 'Edit Tournament'
        }
    )


@login_required
@admin_required
def tournament_delete(request, id):
    from .models import Tournament

    tournament = get_object_or_404(Tournament, id=id)

    if request.method == 'POST':
        name = tournament.name
        tournament.delete()

        ActivityLog.objects.create(
            user=request.user,
            action='Tournament Deleted',
            description=f'Deleted tournament: {name}'
        )

        messages.success(
            request,
            f'Tournament "{name}" deleted successfully.'
        )

        return redirect('tournament_list')

    return render(
        request,
        'teams/tournament_confirm_delete.html',
        {
            'tournament': tournament
        }
    )

# ============================================================
# TEAMS
# ============================================================

@login_required
def team_list(request):
    teams = Team.objects.all().select_related('coach')

    search = request.GET.get('search', '')

    if search:
        teams = teams.filter(
            Q(name__icontains=search) |
            Q(city__icontains=search)
        )

    status_filter = request.GET.get('status', '')

    if status_filter:
        teams = teams.filter(
            status=status_filter
        )

    return render(
        request,
        'teams/team_list.html',
        {
            'teams': teams,
            'search': search,
            'status_filter': status_filter
        }
    )


@login_required
def team_detail(request, id):
    team = get_object_or_404(
        Team,
        id=id
    )

    players = team.players.all()

    from matches.models import Match

    upcoming = Match.objects.filter(
        Q(team1=team) | Q(team2=team),
        status='scheduled'
    ).order_by('date')[:5]

    recent = Match.objects.filter(
        Q(team1=team) | Q(team2=team),
        status='completed'
    ).order_by('-date')[:5]

    from tournaments.models import TournamentRegistration

    tournament_regs = TournamentRegistration.objects.filter(
        team=team,
        status='approved'
    )

    return render(
        request,
        'teams/team_detail.html',
        {
            'team': team,
            'players': players,
            'upcoming_matches': upcoming,
            'recent_results': recent,
            'tournament_regs': tournament_regs
        }
    )


@login_required
@staff_required
def add_team(request):

    if request.method == 'POST':
        form = TeamForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            team = form.save()

            ActivityLog.objects.create(
                user=request.user,
                action='Team Created',
                description=f'Created team: {team.name}'
            )

            messages.success(
                request,
                f'Team "{team.name}" created successfully.'
            )

            return redirect('team_list')

    else:
        form = TeamForm()

    return render(
        request,
        'teams/team_form.html',
        {
            'form': form,
            'title': 'Add New Team'
        }
    )


@login_required
@staff_required
def edit_team(request, id):
    team = get_object_or_404(
        Team,
        id=id
    )

    if (
        hasattr(request.user, 'profile')
        and request.user.profile.role == 'coach'
    ):
        if not (
            hasattr(request.user, 'coach_profile')
            and team in request.user.coach_profile.teams.all()
        ):
            messages.error(
                request,
                'You can only edit your own team.'
            )

            return redirect('team_list')

    if request.method == 'POST':
        form = TeamForm(
            request.POST,
            request.FILES,
            instance=team
        )

        if form.is_valid():
            form.save()

            ActivityLog.objects.create(
                user=request.user,
                action='Team Updated',
                description=f'Updated team: {team.name}'
            )

            messages.success(
                request,
                f'Team "{team.name}" updated successfully.'
            )

            return redirect(
                'team_detail',
                id=team.id
            )

    else:
        form = TeamForm(
            instance=team
        )

    return render(
        request,
        'teams/team_form.html',
        {
            'form': form,
            'title': f'Edit Team: {team.name}',
            'team': team
        }
    )


@login_required
@admin_required
def delete_team(request, id):
    team = get_object_or_404(
        Team,
        id=id
    )

    if request.method == 'POST':
        name = team.name

        team.delete()

        ActivityLog.objects.create(
            user=request.user,
            action='Team Deleted',
            description=f'Deleted team: {name}'
        )

        messages.success(
            request,
            f'Team "{name}" deleted successfully.'
        )

        return redirect('team_list')

    return render(
        request,
        'teams/team_confirm_delete.html',
        {
            'team': team
        }
    )


# ============================================================
# PLAYERS
# ============================================================

@login_required
def player_list(request):
    players = Player.objects.all().select_related(
        'team'
    )

    search = request.GET.get(
        'search',
        ''
    )

    if search:
        players = players.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search)
        )

    team_filter = request.GET.get(
        'team',
        ''
    )

    if team_filter:
        players = players.filter(
            team_id=team_filter
        )

    role_filter = request.GET.get(
        'role',
        ''
    )

    if role_filter:
        players = players.filter(
            playing_role=role_filter
        )

    teams = Team.objects.all()

    return render(
        request,
        'teams/player_list.html',
        {
            'players': players,
            'search': search,
            'teams': teams,
            'team_filter': team_filter,
            'role_filter': role_filter
        }
    )


@login_required
def player_detail(request, id):
    player = get_object_or_404(
        Player,
        id=id
    )

    from matches.models import (
        BattingScore,
        BowlingScore,
        PlayerMatchPerformance
    )

    batting_stats = BattingScore.objects.filter(
        player=player
    )

    bowling_stats = BowlingScore.objects.filter(
        player=player
    )

    fielding_stats = PlayerMatchPerformance.objects.filter(
        player=player
    )

    total_runs = sum(
        b.runs for b in batting_stats
    )

    total_balls = sum(
        b.balls for b in batting_stats
    )

    total_fours = sum(
        b.fours for b in batting_stats
    )

    total_sixes = sum(
        b.sixes for b in batting_stats
    )

    batting_innings = batting_stats.count()

    highest_score = max(
        (b.runs for b in batting_stats),
        default=0
    )

    avg = (
        round(
            total_runs / batting_innings,
            2
        )
        if batting_innings > 0
        else 0
    )

    sr = (
        round(
            (total_runs / total_balls) * 100,
            2
        )
        if total_balls > 0
        else 0
    )

    total_overs = sum(
        b.overs for b in bowling_stats
    )

    total_wickets = sum(
        b.wickets for b in bowling_stats
    )

    total_runs_conceded = sum(
        b.runs_conceded
        for b in bowling_stats
    )

    total_maidens = sum(
        b.maidens
        for b in bowling_stats
    )

    bowling_innings = bowling_stats.count()

    best_bowling = '0/0'

    if bowling_stats.exists():
        best = max(
            bowling_stats,
            key=lambda b: (
                b.wickets,
                -b.runs_conceded
            )
        )

        best_bowling = (
            f'{best.wickets}/'
            f'{best.runs_conceded}'
        )

    economy = (
        round(
            total_runs_conceded / total_overs,
            2
        )
        if total_overs > 0
        else 0
    )

    total_catches = sum(
        f.catches for f in fielding_stats
    )

    total_runouts = sum(
        f.run_outs for f in fielding_stats
    )

    total_stumpings = sum(
        f.stumpings for f in fielding_stats
    )

    from matches.models import Match

    motm_count = Match.objects.filter(
        player_of_match=player
    ).count()

    from training.models import Attendance

    attendance_records = Attendance.objects.filter(
        player=player
    )

    total_sessions = attendance_records.count()

    present_count = (
        attendance_records.filter(
            status='present'
        ).count()
        +
        attendance_records.filter(
            status='late'
        ).count()
    )

    attendance_pct = (
        round(
            (present_count / total_sessions) * 100,
            1
        )
        if total_sessions > 0
        else 0
    )

    context = {
        'player': player,

        'batting': {
            'innings': batting_innings,
            'runs': total_runs,
            'highest': highest_score,
            'average': avg,
            'strike_rate': sr,
            'fours': total_fours,
            'sixes': total_sixes
        },

        'bowling': {
            'innings': bowling_innings,
            'overs': total_overs,
            'wickets': total_wickets,
            'runs_conceded': total_runs_conceded,
            'maidens': total_maidens,
            'best': best_bowling,
            'economy': economy
        },

        'fielding': {
            'catches': total_catches,
            'run_outs': total_runouts,
            'stumpings': total_stumpings
        },

        'motm_count': motm_count,
        'attendance_pct': attendance_pct,
    }

    return render(
        request,
        'teams/player_detail.html',
        context
    )


@login_required
@staff_required
def add_player(request):

    if request.method == 'POST':
        form = PlayerForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            player = form.save()

            ActivityLog.objects.create(
                user=request.user,
                action='Player Added',
                description=f'Added player: {player.name}'
            )

            messages.success(
                request,
                f'Player "{player.name}" added successfully.'
            )

            return redirect(
                'player_list'
            )

    else:
        form = PlayerForm()

    if (
        hasattr(request.user, 'profile')
        and request.user.profile.role == 'coach'
        and hasattr(request.user, 'coach_profile')
    ):
        form.fields['team'].queryset = (
            request.user.coach_profile.teams.all()
        )

    return render(
        request,
        'teams/player_form.html',
        {
            'form': form,
            'title': 'Add New Player'
        }
    )


@login_required
@staff_required
def edit_player(request, id):
    player = get_object_or_404(
        Player,
        id=id
    )

    if request.method == 'POST':
        form = PlayerForm(
            request.POST,
            request.FILES,
            instance=player
        )

        if form.is_valid():
            form.save()

            ActivityLog.objects.create(
                user=request.user,
                action='Player Updated',
                description=f'Updated player: {player.name}'
            )

            messages.success(
                request,
                f'Player "{player.name}" updated successfully.'
            )

            return redirect(
                'player_detail',
                id=player.id
            )

    else:
        form = PlayerForm(
            instance=player
        )

    return render(
        request,
        'teams/player_form.html',
        {
            'form': form,
            'title': f'Edit Player: {player.name}',
            'player': player
        }
    )


@login_required
@admin_required
def delete_player(request, id):
    player = get_object_or_404(
        Player,
        id=id
    )

    if request.method == 'POST':
        name = player.name

        player.delete()

        ActivityLog.objects.create(
            user=request.user,
            action='Player Deleted',
            description=f'Deleted player: {name}'
        )

        messages.success(
            request,
            f'Player "{name}" deleted successfully.'
        )

        return redirect(
            'player_list'
        )

    return render(
        request,
        'teams/player_confirm_delete.html',
        {
            'player': player
        }
    )


# ============================================================
# COACHES
# ============================================================

@login_required
@admin_required
def coach_list(request):
    coaches = Coach.objects.all()

    return render(
        request,
        'teams/coach_list.html',
        {
            'coaches': coaches
        }
    )


@login_required
@admin_required
def coach_detail(request, id):
    coach = get_object_or_404(
        Coach,
        id=id
    )

    teams = coach.teams.all()

    return render(
        request,
        'teams/coach_detail.html',
        {
            'coach': coach,
            'teams': teams
        }
    )


@login_required
@admin_required
def add_coach(request):

    if request.method == 'POST':
        form = CoachForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            coach = form.save()

            ActivityLog.objects.create(
                user=request.user,
                action='Coach Added',
                description=f'Added coach: {coach.name}'
            )

            messages.success(
                request,
                f'Coach "{coach.name}" added successfully.'
            )

            return redirect(
                'coach_list'
            )

    else:
        form = CoachForm()

    return render(
        request,
        'teams/coach_form.html',
        {
            'form': form,
            'title': 'Add New Coach'
        }
    )


@login_required
@admin_required
def edit_coach(request, id):
    coach = get_object_or_404(
        Coach,
        id=id
    )

    if request.method == 'POST':
        form = CoachForm(
            request.POST,
            request.FILES,
            instance=coach
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                f'Coach "{coach.name}" updated successfully.'
            )

            return redirect(
                'coach_list'
            )

    else:
        form = CoachForm(
            instance=coach
        )

    return render(
        request,
        'teams/coach_form.html',
        {
            'form': form,
            'title': f'Edit Coach: {coach.name}',
            'coach': coach
        }
    )


@login_required
@admin_required
def delete_coach(request, id):
    coach = get_object_or_404(
        Coach,
        id=id
    )

    if request.method == 'POST':
        name = coach.name

        coach.delete()

        messages.success(
            request,
            f'Coach "{name}" deleted successfully.'
        )

        return redirect(
            'coach_list'
        )

    return render(
        request,
        'teams/coach_confirm_delete.html',
        {
            'coach': coach
        }
    )


# ============================================================
# VENUES
# ============================================================

@login_required
@staff_required
def venue_list(request):
    venues = Venue.objects.all()

    return render(
        request,
        'teams/venue_list.html',
        {
            'venues': venues
        }
    )


@login_required
@admin_required
def add_venue(request):

    if request.method == 'POST':
        form = VenueForm(request.POST)

        if form.is_valid():
            venue = form.save()

            ActivityLog.objects.create(
                user=request.user,
                action='Venue Added',
                description=f'Added venue: {venue.name}'
            )

            messages.success(
                request,
                f'Venue "{venue.name}" added successfully.'
            )

            return redirect(
                'venue_list'
            )

    else:
        form = VenueForm()

    return render(
        request,
        'teams/venue_form.html',
        {
            'form': form,
            'title': 'Add New Venue'
        }
    )


@login_required
@admin_required
def edit_venue(request, id):
    venue = get_object_or_404(
        Venue,
        id=id
    )

    if request.method == 'POST':
        form = VenueForm(
            request.POST,
            instance=venue
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                f'Venue "{venue.name}" updated successfully.'
            )

            return redirect(
                'venue_list'
            )

    else:
        form = VenueForm(
            instance=venue
        )

    return render(
        request,
        'teams/venue_form.html',
        {
            'form': form,
            'title': f'Edit Venue: {venue.name}',
            'venue': venue
        }
    )


@login_required
@admin_required
def delete_venue(request, id):
    venue = get_object_or_404(
        Venue,
        id=id
    )

    if request.method == 'POST':
        name = venue.name

        venue.delete()

        messages.success(
            request,
            f'Venue "{name}" deleted successfully.'
        )

        return redirect(
            'venue_list'
        )

    return render(
        request,
        'teams/venue_confirm_delete.html',
        {
            'venue': venue
        }
    )       