from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Match, Innings, BattingScore, BowlingScore, PlayerMatchPerformance
from .forms import MatchForm, MatchResultForm, InningsForm
from teams.models import Team, Player
from tournaments.models import Tournament, PointsTable
from accounts.decorators import staff_required, admin_required, organizer_required
from notifications.models import ActivityLog, Notification


@login_required
def match_list(request):
    matches = Match.objects.all().select_related('team1', 'team2', 'venue', 'tournament', 'winner')
    search = request.GET.get('search', '')
    if search:
        matches = matches.filter(Q(team1__name__icontains=search) | Q(team2__name__icontains=search))
    status_filter = request.GET.get('status', '')
    if status_filter:
        matches = matches.filter(status=status_filter)
    tournament_filter = request.GET.get('tournament', '')
    if tournament_filter:
        matches = matches.filter(tournament_id=tournament_filter)
    tournaments = Tournament.objects.all()
    return render(request, 'matches/match_list.html', {
        'matches': matches, 'search': search, 'status_filter': status_filter,
        'tournament_filter': tournament_filter, 'tournaments': tournaments
    })


@login_required
def match_detail(request, id):
    match = get_object_or_404(Match, id=id)
    innings = Innings.objects.filter(match=match).order_by('innings_number')
    innings_data = []
    for inn in innings:
        batting_scores = BattingScore.objects.filter(innings=inn).select_related('player')
        bowling_scores = BowlingScore.objects.filter(innings=inn).select_related('player')
        innings_data.append({
            'innings': inn,
            'batting_scores': batting_scores,
            'bowling_scores': bowling_scores,
        })
    return render(request, 'matches/match_detail.html', {
        'match': match, 'innings_data': innings_data,
    })


@login_required
@staff_required
def match_create(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save(commit=False)
            match.status = 'scheduled'
            match.save()
            ActivityLog.objects.create(user=request.user, action='Match Scheduled', description=f'Scheduled: {match.team1} vs {match.team2}')
            # Create notifications
            msg = f'New match scheduled: {match.team1} vs {match.team2} on {match.date}'
            for user in set(list(Player.objects.filter(team__in=[match.team1, match.team2]).values_list('user', flat=True)) + [match.team1.coach.user.id if match.team1.coach and match.team1.coach.user else None, match.team2.coach.user.id if match.team2.coach and match.team2.coach.user else None]):
                if user:
                    Notification.objects.create(user_id=user, title='New Match Scheduled', message=msg, link=f'/matches/{match.id}/')
            messages.success(request, 'Match scheduled successfully.')
            return redirect('match_list')
    else:
        form = MatchForm()
    return render(request, 'matches/match_form.html', {'form': form, 'title': 'Schedule New Match'})


@login_required
@staff_required
def match_update_result(request, id):
    match = get_object_or_404(Match, id=id)
    if request.method == 'POST':
        form = MatchResultForm(request.POST, instance=match)
        if form.is_valid():
            match = form.save(commit=False)
            match.status = 'completed'
            match.save()
            # Update points table if tournament match
            if match.tournament:
                _update_points_table(match)
            ActivityLog.objects.create(user=request.user, action='Match Result Updated', description=f'Result: {match.team1} vs {match.team2} - {match.result}')
            messages.success(request, 'Match result updated successfully.')
            return redirect('match_detail', id=match.id)
    else:
        form = MatchResultForm(instance=match)
        form.fields['toss_winner'].queryset = Team.objects.filter(id__in=[match.team1_id, match.team2_id])
        form.fields['winner'].queryset = Team.objects.filter(id__in=[match.team1_id, match.team2_id])
        form.fields['player_of_match'].queryset = Player.objects.filter(team__in=[match.team1, match.team2])
    return render(request, 'matches/match_result_form.html', {'form': form, 'match': match})


def _update_points_table(match):
    """Update points table when a match result is entered."""
    tournament = match.tournament
    if not tournament:
        return
    for team in [match.team1, match.team2]:
        entry, _ = PointsTable.objects.get_or_create(tournament=tournament, team=team)
    # Recalculate from all completed matches
    for entry in PointsTable.objects.filter(tournament=tournament):
        team = entry.team
        team_matches = Match.objects.filter(
            tournament=tournament, status='completed'
        ).filter(Q(team1=team) | Q(team2=team))
        entry.played = team_matches.count()
        entry.won = team_matches.filter(winner=team).count()
        entry.tied = team_matches.filter(result__icontains='tie').count()
        entry.no_result = team_matches.filter(status='abandoned').count()
        entry.lost = entry.played - entry.won - entry.tied - entry.no_result
        entry.points = (entry.won * tournament.points_for_win +
                       entry.tied * tournament.points_for_tie +
                       entry.no_result * tournament.points_for_no_result)
        # Calculate NRR
        batting_innings = Innings.objects.filter(match__in=team_matches, batting_team=team)
        bowling_innings = Innings.objects.filter(match__in=team_matches, bowling_team=team)
        total_runs_scored = sum(i.runs for i in batting_innings)
        total_overs_faced = sum(i.overs for i in batting_innings) or 1
        total_runs_conceded = sum(i.runs for i in bowling_innings)
        total_overs_bowled = sum(i.overs for i in bowling_innings) or 1
        entry.net_run_rate = round((total_runs_scored / total_overs_faced) - (total_runs_conceded / total_overs_bowled), 3)
        entry.save()


@login_required
@staff_required
def add_innings(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        form = InningsForm(request.POST)
        if form.is_valid():
            innings = form.save(commit=False)
            innings.match = match
            existing = Innings.objects.filter(match=match).count()
            innings.innings_number = existing + 1
            innings.save()
            messages.success(request, f'Innings {innings.innings_number} added successfully.')
            return redirect('match_detail', id=match.id)
    else:
        form = InningsForm()
        form.fields['batting_team'].queryset = Team.objects.filter(id__in=[match.team1_id, match.team2_id])
        form.fields['bowling_team'].queryset = Team.objects.filter(id__in=[match.team1_id, match.team2_id])
    return render(request, 'matches/innings_form.html', {'form': form, 'match': match})


@login_required
@admin_required
def delete_match(request, id):
    match = get_object_or_404(Match, id=id)
    if request.method == 'POST':
        desc = str(match)
        match.delete()
        ActivityLog.objects.create(user=request.user, action='Match Deleted', description=f'Deleted match: {desc}')
        messages.success(request, 'Match deleted successfully.')
        return redirect('match_list')
    return render(request, 'matches/match_confirm_delete.html', {'match': match})
