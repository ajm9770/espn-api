import numpy as np
from typing import List, Dict, Optional
from ..base_league import BaseLeague

class MonteCarloSimulator:
    def __init__(self, league: BaseLeague, num_simulations: int = 1000, preseason: bool = False):
        """Initialize Monte Carlo simulator for season predictions
        
        Args:
            league: League instance to simulate
            num_simulations: Number of season simulations to run
            preseason: If True, use preseason projections and simulate entire season
        """
        self.league = league
        self.num_simulations = num_simulations
        self.preseason = preseason
        self.teams = league.teams
        self.schedule = self._get_schedule()
        self.team_ratings = self._get_team_ratings()
        self.draft_rankings = {}  # Store draft rankings if in preseason
        
    def _get_schedule(self) -> List[Dict]:
        """Get schedule based on whether it's preseason or mid-season"""
        schedule = []
        start_week = 1 if self.preseason else self.league.current_week
        
        for team in self.teams:
            for matchup in team.schedule:
                if matchup.week >= start_week:
                    schedule.append({
                        'week': matchup.week,
                        'team1_id': team.team_id,
                        'team2_id': matchup.away_team.team_id if matchup.away_team else matchup.home_team.team_id
                    })
        # Remove duplicates since each matchup appears twice
        unique_schedule = []
        seen = set()
        for game in schedule:
            game_key = (game['week'], tuple(sorted([game['team1_id'], game['team2_id']])))
            if game_key not in seen:
                unique_schedule.append(game)
                seen.add(game_key)
        return unique_schedule

    def _get_team_ratings(self) -> Dict[int, Dict]:
        """Get team ratings based on projections and past performance"""
        ratings = {}
        for team in self.teams:
            if self.preseason:
                # Use ESPN preseason projections
                projected_points = self._get_preseason_projection(team)
                # Higher variance in preseason
                std_dev = projected_points * 0.2  # 20% variance in preseason
            else:
                # Use current season performance and projections
                projected_points = team.projected_points if hasattr(team, 'projected_points') else team.points_for
                std_dev = np.std([m.points_for for m in team.schedule if m.points_for is not None]) if team.schedule else projected_points * 0.15
            
            ratings[team.team_id] = {
                'mean': projected_points,
                'std': std_dev,
                'roster_value': self._calculate_roster_value(team)
            }
        return ratings
        
    def _get_preseason_projection(self, team) -> float:
        """Get preseason projection for a team based on roster"""
        total_projection = 0
        for player in team.roster:
            # Get player's ESPN projection
            projection = getattr(player, 'projected_points', 0)
            if projection == 0:
                # Fallback to last season's points per game
                projection = getattr(player, 'points_per_game', 0) * self.league.settings.reg_season_count
            total_projection += projection
        return total_projection

    def _calculate_roster_value(self, team) -> float:
        """Calculate overall roster value considering depth and positional importance"""
        value = 0
        position_weights = {
            'QB': 1.2,
            'RB': 1.1,
            'WR': 1.1,
            'TE': 0.8,
            'K': 0.5,
            'D/ST': 0.7
        }
        
        for player in team.roster:
            pos = player.position
            # Get player's projected points
            points = getattr(player, 'projected_points', 0)
            if points == 0:
                points = getattr(player, 'points_per_game', 0) * self.league.settings.reg_season_count
            
            # Apply position weight
            value += points * position_weights.get(pos, 1.0)
        
        return value

    def analyze_draft_strategy(self) -> Dict[str, List[Dict]]:
        """Analyze different draft strategies through simulation
        
        Returns:
            Dict mapping strategy name to list of successful draft picks
        """
        if not self.preseason:
            raise ValueError("Draft strategy analysis only available in preseason mode")
            
        strategies = {
            'Zero RB': {'RB': 0.1, 'WR': 0.4, 'TE': 0.2, 'QB': 0.2, 'K': 0.05, 'D/ST': 0.05},
            'RB Heavy': {'RB': 0.4, 'WR': 0.2, 'TE': 0.1, 'QB': 0.2, 'K': 0.05, 'D/ST': 0.05},
            'Balanced': {'RB': 0.25, 'WR': 0.25, 'TE': 0.15, 'QB': 0.25, 'K': 0.05, 'D/ST': 0.05},
        }
        
        results = {strategy: [] for strategy in strategies}
        
        for strategy, weights in strategies.items():
            # Simulate seasons with this strategy
            championship_rosters = []
            for _ in range(self.num_simulations // 10):  # Fewer sims for draft analysis
                # Modify team ratings based on strategy weights
                modified_ratings = self._apply_strategy_weights(weights)
                season_result = self._simulate_season_with_ratings(modified_ratings)
                
                # Record championship roster composition
                champ_id = self.simulate_playoffs([t[0] for t in season_result[:self.league.settings.playoff_team_count]])
                champ_roster = [p for p in self.league.get_team_data(champ_id).roster]
                championship_rosters.append(champ_roster)
            
            # Analyze successful roster compositions
            results[strategy] = self._analyze_championship_rosters(championship_rosters)
            
        return results

    def _apply_strategy_weights(self, weights: Dict[str, float]) -> Dict[int, Dict]:
        """Apply strategy weights to team ratings"""
        modified_ratings = self.team_ratings.copy()
        for team_id in modified_ratings:
            team = next(t for t in self.teams if t.team_id == team_id)
            
            # Adjust team rating based on roster composition matching strategy
            roster_comp = self._get_roster_composition(team)
            strategy_match = sum(weights[pos] * pct for pos, pct in roster_comp.items())
            
            modified_ratings[team_id]['mean'] *= strategy_match
            
        return modified_ratings

    def _get_roster_composition(self, team) -> Dict[str, float]:
        """Get roster composition percentages by position"""
        composition = {'QB': 0, 'RB': 0, 'WR': 0, 'TE': 0, 'K': 0, 'D/ST': 0}
        total_value = 0
        
        for player in team.roster:
            pos = player.position
            value = getattr(player, 'projected_points', 0)
            if value == 0:
                value = getattr(player, 'points_per_game', 0) * self.league.settings.reg_season_count
                
            composition[pos] = composition.get(pos, 0) + value
            total_value += value
            
        # Convert to percentages
        if total_value > 0:
            for pos in composition:
                composition[pos] /= total_value
                
        return composition

    def _analyze_championship_rosters(self, rosters: List[List]) -> List[Dict]:
        """Analyze common characteristics of championship rosters"""
        analysis = []
        
        for roster in rosters:
            # Analyze roster composition
            comp = self._get_roster_composition({'roster': roster})
            
            # Analyze star power (number of top performers)
            star_players = len([p for p in roster if getattr(p, 'projected_points', 0) > 
                              np.mean([getattr(p2, 'projected_points', 0) for p2 in roster]) + 
                              np.std([getattr(p2, 'projected_points', 0) for p2 in roster])])
            
            analysis.append({
                'composition': comp,
                'star_players': star_players,
                'total_projection': sum(getattr(p, 'projected_points', 0) for p in roster)
            })
            
        return analysis

    def get_optimal_moves(self, team_id: int, free_agents: List = None) -> List[Dict]:
        """Get recommended roster moves based on simulation results
        
        Args:
            team_id: Team to get recommendations for
            free_agents: List of available free agents (optional)
            
        Returns:
            List of recommended moves with expected value impact
        """
        team = next(t for t in self.teams if t.team_id == team_id)
        current_value = self.team_ratings[team_id]['roster_value']
        
        recommendations = []
        
        # Analyze potential trades
        for other_team in self.teams:
            if other_team.team_id == team_id:
                continue
                
            # Find valuable trade targets
            for player in other_team.roster:
                # Calculate value added by this player
                value_added = self._calculate_player_value(player, team)
                if value_added > 0:
                    recommendations.append({
                        'type': 'trade',
                        'player': player,
                        'target_team': other_team.team_name,
                        'value_added': value_added,
                        'priority': 'high' if value_added > current_value * 0.1 else 'medium'
                    })
        
        # Analyze free agents if provided
        if free_agents:
            for player in free_agents:
                value_added = self._calculate_player_value(player, team)
                if value_added > 0:
                    recommendations.append({
                        'type': 'add',
                        'player': player,
                        'value_added': value_added,
                        'priority': 'high' if value_added > current_value * 0.05 else 'medium'
                    })
        
        # Sort by value added
        recommendations.sort(key=lambda x: x['value_added'], reverse=True)
        return recommendations[:5]  # Return top 5 recommendations

    def _calculate_player_value(self, player, team) -> float:
        """Calculate the value a player would add to a team"""
        pos = player.position
        current_starter = self._get_current_starter(team, pos)
        
        player_projection = getattr(player, 'projected_points', 0)
        if player_projection == 0:
            player_projection = getattr(player, 'points_per_game', 0) * self.league.settings.reg_season_count
            
        starter_projection = getattr(current_starter, 'projected_points', 0)
        if starter_projection == 0:
            starter_projection = getattr(current_starter, 'points_per_game', 0) * self.league.settings.reg_season_count
            
        return player_projection - starter_projection

    def _get_current_starter(self, team, position: str):
        """Get current starter at position"""
        pos_players = [p for p in team.roster if p.position == position]
        if not pos_players:
            return None
        return max(pos_players, key=lambda p: getattr(p, 'projected_points', 0) or getattr(p, 'points_per_game', 0))

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
