import numpy as np
from typing import List, Dict, Optional
from ..base_league import BaseLeague

class MonteCarloSimulator:
    def __init__(self, league: BaseLeague, num_simulations: int = 1000):
        """Initialize Monte Carlo simulator for season predictions
        
        Args:
            league: League instance to simulate
            num_simulations: Number of season simulations to run
        """
        self.league = league
        self.num_simulations = num_simulations
        self.teams = league.teams
        self.schedule = self._get_remaining_schedule()
        self.team_ratings = self._get_team_ratings()
        
    def _get_remaining_schedule(self) -> List[Dict]:
        """Get remaining schedule from league"""
        schedule = []
        for team in self.teams:
            for matchup in team.schedule:
                if matchup.week >= self.league.current_week:
                    schedule.append({
                        'week': matchup.week,
                        'team1_id': team.team_id,
                        'team2_id': matchup.away_team.team_id if matchup.away_team else matchup.home_team.team_id
                    })
        # Remove duplicates since each matchup appears twice
        unique_schedule = []
        seen = set()
        for game in schedule:
            game_key = tuple(sorted([game['team1_id'], game['team2_id']]))
            if game_key not in seen:
                unique_schedule.append(game)
                seen.add(game_key)
        return unique_schedule

    def _get_team_ratings(self) -> Dict[int, float]:
        """Get team ratings based on projections and past performance"""
        ratings = {}
        for team in self.teams:
            # Use team's projected points as base rating
            # Add some variance based on past performance
            projected_points = team.projected_points if hasattr(team, 'projected_points') else team.points_for
            std_dev = np.std([m.points_for for m in team.schedule if m.points_for is not None]) if team.schedule else 10
            ratings[team.team_id] = {
                'mean': projected_points,
                'std': std_dev
            }
        return ratings

    def simulate_game(self, team1_id: int, team2_id: int) -> int:
        """Simulate a single game between two teams
        
        Returns:
            1 if team1 wins, 2 if team2 wins
        """
        team1_score = np.random.normal(
            self.team_ratings[team1_id]['mean'],
            self.team_ratings[team1_id]['std']
        )
        team2_score = np.random.normal(
            self.team_ratings[team2_id]['mean'],
            self.team_ratings[team2_id]['std']
        )
        return 1 if team1_score > team2_score else 2

    def simulate_season(self) -> Dict[int, Dict]:
        """Simulate one complete season
        
        Returns:
            Dict mapping team_id to wins and playoff probability
        """
        wins = {team.team_id: team.wins for team in self.teams}
        
        # Simulate remaining games
        for game in self.schedule:
            winner = self.simulate_game(game['team1_id'], game['team2_id'])
            if winner == 1:
                wins[game['team1_id']] += 1
            else:
                wins[game['team2_id']] += 1
                
        return wins

    def run_simulations(self) -> Dict[int, Dict]:
        """Run multiple season simulations
        
        Returns:
            Dict mapping team_id to:
                - avg_wins: Average number of wins
                - playoff_odds: Percentage of simulations making playoffs
                - division_odds: Percentage of simulations winning division
                - championship_odds: Percentage of simulations winning championship
        """
        results = {team.team_id: {
            'wins': 0,
            'playoffs': 0,
            'division': 0,
            'championship': 0
        } for team in self.teams}
        
        for _ in range(self.num_simulations):
            season = self.simulate_season()
            
            # Sort teams by wins for playoff determination
            sorted_teams = sorted(
                season.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Record wins
            for team_id, wins in season.items():
                results[team_id]['wins'] += wins
            
            # Record playoff berths (top N teams)
            playoff_teams = sorted_teams[:self.league.settings.playoff_team_count]
            for team_id, _ in playoff_teams:
                results[team_id]['playoffs'] += 1
            
            # Simulate playoffs for championship odds
            if len(playoff_teams) >= 2:
                champ_id = self.simulate_playoffs([t[0] for t in playoff_teams])
                results[champ_id]['championship'] += 1
        
        # Convert totals to averages/percentages
        for team_id in results:
            results[team_id]['avg_wins'] = results[team_id]['wins'] / self.num_simulations
            results[team_id]['playoff_odds'] = results[team_id]['playoffs'] / self.num_simulations * 100
            results[team_id]['championship_odds'] = results[team_id]['championship'] / self.num_simulations * 100
            
        return results

    def simulate_playoffs(self, playoff_teams: List[int]) -> int:
        """Simulate playoff bracket to determine champion
        
        Args:
            playoff_teams: List of team IDs in playoff seeding order
        
        Returns:
            team_id of champion
        """
        teams = playoff_teams.copy()
        
        while len(teams) > 1:
            winners = []
            # Simulate matchups (1v8, 2v7, etc)
            for i in range(0, len(teams), 2):
                if i + 1 >= len(teams):
                    winners.append(teams[i])
                    continue
                winner = self.simulate_game(teams[i], teams[i+1])
                winners.append(teams[i] if winner == 1 else teams[i+1])
            teams = winners
            
        return teams[0]
