"""
Unit tests for AdvancedFantasySimulator

Tests matchup simulation, trade analysis, free agent recommendations, and season projections
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from espn_api.utils.advanced_simulator import AdvancedFantasySimulator


class TestAdvancedFantasySimulator(unittest.TestCase):
    """Test AdvancedFantasySimulator functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock league
        self.league = Mock()
        self.league.year = 2024
        self.league.current_week = 10
        self.league.settings = Mock()
        self.league.settings.playoff_team_count = 6
        self.league.settings.reg_season_count = 14

        # Create mock teams with rosters
        self.teams = self._create_mock_teams(10)
        self.league.teams = self.teams

        # Patch PlayerPerformanceModel to avoid actual training
        with patch('espn_api.utils.advanced_simulator.PlayerPerformanceModel') as mock_ppm:
            mock_model = Mock()
            mock_model.bulk_train.return_value = {}
            mock_model.models = {}
            mock_model.player_states = {}
            mock_ppm.return_value = mock_model

            self.simulator = AdvancedFantasySimulator(
                self.league,
                num_simulations=100,  # Use fewer for testing
                use_gmm=False  # Disable GMM for faster tests
            )

    def _create_mock_player(self, name, position, avg_points, player_id):
        """Create a mock player"""
        player = Mock()
        player.name = name
        player.position = position
        player.playerId = player_id
        player.avg_points = avg_points
        player.projected_avg_points = avg_points * 1.05
        player.lineupSlot = 'STARTER' if 'Starter' in name else 'BE'
        player.stats = {0: {'points': avg_points * 10, 'avg_points': avg_points}}
        return player

    def _create_mock_teams(self, num_teams):
        """Create mock teams with rosters"""
        teams = []
        for i in range(num_teams):
            team = Mock()
            team.team_id = i + 1
            team.team_name = f"Team {i + 1}"
            team.wins = 5
            team.losses = 4
            team.points_for = 1000.0
            team.points_against = 950.0

            # Create roster with starters
            team.roster = [
                self._create_mock_player(f"Starter QB {i}", "QB", 20.0, i * 100 + 1),
                self._create_mock_player(f"Starter RB1 {i}", "RB", 15.0, i * 100 + 2),
                self._create_mock_player(f"Starter RB2 {i}", "RB", 12.0, i * 100 + 3),
                self._create_mock_player(f"Starter WR1 {i}", "WR", 14.0, i * 100 + 4),
                self._create_mock_player(f"Starter WR2 {i}", "WR", 11.0, i * 100 + 5),
                self._create_mock_player(f"Starter TE {i}", "TE", 10.0, i * 100 + 6),
                self._create_mock_player(f"Starter K {i}", "K", 8.0, i * 100 + 7),
                self._create_mock_player(f"Starter DST {i}", "D/ST", 9.0, i * 100 + 8),
                self._create_mock_player(f"Bench RB {i}", "RB", 8.0, i * 100 + 9),
                self._create_mock_player(f"Bench WR {i}", "WR", 7.0, i * 100 + 10),
            ]

            # Create schedule
            team.schedule = list(range(1, 15))  # Opponent IDs for weeks 1-14

            teams.append(team)

        return teams

    def test_simulator_initialization(self):
        """Test simulator initializes correctly"""
        self.assertEqual(self.simulator.league, self.league)
        self.assertEqual(self.simulator.num_simulations, 100)
        self.assertIsNotNone(self.simulator.player_model)

    def test_get_optimal_lineup(self):
        """Test optimal lineup selection"""
        team = self.teams[0]
        lineup = self.simulator._get_optimal_lineup(team.roster)

        # Should have 9 starters (QB, 2RB, 2WR, TE, FLEX, K, DST)
        # Note: Exact count depends on FLEX selection
        self.assertGreater(len(lineup), 7)
        self.assertLessEqual(len(lineup), 9)

        # QB should be in lineup
        qb_names = [p.name for p in lineup if p.position == 'QB']
        self.assertEqual(len(qb_names), 1)

    def test_simulate_roster_score(self):
        """Test roster score simulation"""
        team = self.teams[0]
        score = self.simulator.simulate_roster_score(team)

        # Score should be positive
        self.assertGreater(score, 0)

        # Score should be reasonable (between 50-200 for typical team)
        self.assertGreater(score, 30)
        self.assertLess(score, 250)

    def test_simulate_matchup(self):
        """Test matchup simulation"""
        team1 = self.teams[0]
        team2 = self.teams[1]

        results = self.simulator.simulate_matchup(team1, team2, n_simulations=100)

        # Check result structure
        self.assertIn('team1_win_probability', results)
        self.assertIn('team2_win_probability', results)
        self.assertIn('team1_avg_score', results)
        self.assertIn('team2_avg_score', results)

        # Win probabilities should sum to 100%
        total_prob = results['team1_win_probability'] + results['team2_win_probability']
        self.assertAlmostEqual(total_prob, 100.0, delta=0.1)

        # Each probability should be between 0-100
        self.assertGreaterEqual(results['team1_win_probability'], 0)
        self.assertLessEqual(results['team1_win_probability'], 100)

        # Scores should be reasonable
        self.assertGreater(results['team1_avg_score'], 30)
        self.assertGreater(results['team2_avg_score'], 30)

    def test_calculate_roster_value(self):
        """Test roster value calculation"""
        team = self.teams[0]
        value = self.simulator._calculate_roster_value(team.roster)

        # Value should be positive
        self.assertGreater(value, 0)

        # Should be sum of starter values + 30% bench values
        # Approximate calculation
        expected_value = 20 + 15 + 12 + 14 + 11 + 10 + 8 + 9  # Starters
        expected_value += (8 + 7) * 0.3  # Bench at 30%

        self.assertAlmostEqual(value, expected_value, delta=10)

    def test_analyze_trade_1for1(self):
        """Test 1-for-1 trade analysis"""
        my_team = self.teams[0]
        other_team = self.teams[1]

        my_player = my_team.roster[1]  # RB1
        their_player = other_team.roster[3]  # WR1

        analysis = self.simulator.analyze_trade(
            my_team, other_team,
            [my_player], [their_player],
            weeks_remaining=10
        )

        # Check analysis structure
        self.assertIn('my_value_change', analysis)
        self.assertIn('their_value_change', analysis)
        self.assertIn('asymmetric_advantage', analysis)
        self.assertIn('recommendation', analysis)

        # Recommendation should be ACCEPT or REJECT
        self.assertIn(analysis['recommendation'], ['ACCEPT', 'REJECT'])

    def test_analyze_trade_2for1(self):
        """Test 2-for-1 trade analysis"""
        my_team = self.teams[0]
        other_team = self.teams[1]

        my_players = [my_team.roster[1], my_team.roster[8]]  # RB1 + Bench RB
        their_player = [other_team.roster[3]]  # WR1

        analysis = self.simulator.analyze_trade(
            my_team, other_team,
            my_players, their_player,
            weeks_remaining=10
        )

        self.assertIn('my_value_change', analysis)
        self.assertIn('advantage_margin', analysis)

    def test_asymmetric_advantage_detection(self):
        """Test detection of asymmetric trades"""
        my_team = self.teams[0]
        other_team = self.teams[1]

        # Create scenario where I trade bench for their starter
        my_player = my_team.roster[8]  # Bench RB (8 pts)
        their_player = other_team.roster[1]  # Starter RB1 (15 pts)

        # Temporarily boost my player's value to create asymmetry
        my_player.avg_points = 16.0  # Higher than their starter

        analysis = self.simulator.analyze_trade(
            my_team, other_team,
            [my_player], [their_player]
        )

        # Should show asymmetric advantage for me
        self.assertGreater(analysis['my_value_change'], analysis['their_value_change'])
        self.assertTrue(analysis['asymmetric_advantage'])

    def test_find_trade_opportunities(self):
        """Test finding trade opportunities"""
        my_team = self.teams[0]

        opportunities = self.simulator.find_trade_opportunities(
            my_team,
            min_advantage=1.0,
            max_trades_per_team=2
        )

        # Should return a list
        self.assertIsInstance(opportunities, list)

        # Each opportunity should have required fields
        if opportunities:
            opp = opportunities[0]
            self.assertIn('other_team', opp)
            self.assertIn('give', opp)
            self.assertIn('receive', opp)
            self.assertIn('analysis', opp)

    def test_recommend_free_agents(self):
        """Test free agent recommendations"""
        my_team = self.teams[0]

        # Create mock free agents
        free_agents = [
            self._create_mock_player("FA RB1", "RB", 16.0, 9001),
            self._create_mock_player("FA WR1", "WR", 13.0, 9002),
            self._create_mock_player("FA QB1", "QB", 22.0, 9003),
            self._create_mock_player("FA TE1", "TE", 9.0, 9004),
        ]

        recommendations = self.simulator.recommend_free_agents(
            my_team, free_agents, top_n=5
        )

        # Should return recommendations
        self.assertIsInstance(recommendations, list)

        # Each recommendation should have required fields
        if recommendations:
            rec = recommendations[0]
            self.assertIn('player', rec)
            self.assertIn('value_added', rec)
            self.assertIn('drop_candidate', rec)
            self.assertIn('priority', rec)

            # Priority should be HIGH, MEDIUM, or LOW
            self.assertIn(rec['priority'], ['HIGH', 'MEDIUM', 'LOW'])

    def test_free_agent_value_calculation(self):
        """Test FA value is calculated correctly"""
        my_team = self.teams[0]

        # Create FA better than my worst RB
        fa_rb = self._create_mock_player("FA RB Star", "RB", 18.0, 9005)
        free_agents = [fa_rb]

        recommendations = self.simulator.recommend_free_agents(my_team, free_agents)

        # Should recommend since FA (18 pts) > my worst RB (~8 pts)
        self.assertGreater(len(recommendations), 0)
        self.assertGreater(recommendations[0]['value_added'], 0)

    def test_position_filter_free_agents(self):
        """Test filtering free agents by position"""
        my_team = self.teams[0]

        free_agents = [
            self._create_mock_player("FA RB", "RB", 15.0, 9006),
            self._create_mock_player("FA WR", "WR", 14.0, 9007),
            self._create_mock_player("FA QB", "QB", 21.0, 9008),
        ]

        recommendations = self.simulator.recommend_free_agents(
            my_team, free_agents, positions=['RB']
        )

        # Should only have RB recommendations
        for rec in recommendations:
            self.assertEqual(rec['position'], 'RB')

    def test_simulate_season_rest_of_season(self):
        """Test rest of season simulation"""
        results = self.simulator.simulate_season_rest_of_season()

        # Should have results for all teams
        self.assertEqual(len(results), len(self.teams))

        # Each team should have required fields
        for team_id, team_results in results.items():
            self.assertIn('current_wins', team_results)
            self.assertIn('projected_wins', team_results)
            self.assertIn('playoff_odds', team_results)
            self.assertIn('championship_odds', team_results)

            # Projected wins should be >= current wins
            self.assertGreaterEqual(team_results['projected_wins'], team_results['current_wins'])

            # Odds should be 0-100%
            self.assertGreaterEqual(team_results['playoff_odds'], 0)
            self.assertLessEqual(team_results['playoff_odds'], 100)
            self.assertGreaterEqual(team_results['championship_odds'], 0)
            self.assertLessEqual(team_results['championship_odds'], 100)

    def test_playoff_bracket_simulation(self):
        """Test playoff bracket simulation"""
        playoff_teams = [1, 2, 3, 4, 5, 6]
        champion = self.simulator._simulate_playoff_bracket(playoff_teams)

        # Champion should be one of the playoff teams
        self.assertIn(champion, playoff_teams)

    def test_calculate_player_value(self):
        """Test individual player value calculation"""
        my_team = self.teams[0]

        # Create a star player
        star_player = self._create_mock_player("Star RB", "RB", 25.0, 9999)

        value = self.simulator._calculate_player_value(star_player, my_team)

        # Should add value since 25 > current starter (15)
        self.assertGreater(value, 0)

    def test_get_current_starter(self):
        """Test getting current starter at position"""
        my_team = self.teams[0]

        starter = self.simulator._get_current_starter(my_team, 'QB')

        self.assertIsNotNone(starter)
        self.assertEqual(starter.position, 'QB')

    def test_matchup_variance(self):
        """Test that matchup simulations have realistic variance"""
        team1 = self.teams[0]
        team2 = self.teams[1]

        results = self.simulator.simulate_matchup(team1, team2, n_simulations=100)

        # Standard deviation should be > 0 (variance exists)
        self.assertGreater(results['team1_score_std'], 0)
        self.assertGreater(results['team2_score_std'], 0)

        # Score range should be reasonable
        low, high = results['team1_score_range']
        self.assertLess(low, results['team1_avg_score'])
        self.assertGreater(high, results['team1_avg_score'])

    def test_weekly_score_consistency(self):
        """Test that scores are consistent across simulations"""
        team = self.teams[0]

        scores = [self.simulator.simulate_roster_score(team) for _ in range(10)]

        # Mean should be relatively stable
        mean_score = np.mean(scores)
        self.assertGreater(mean_score, 50)
        self.assertLess(mean_score, 150)

        # Should have some variance
        std_score = np.std(scores)
        self.assertGreater(std_score, 1)

    def test_trade_weeks_remaining_impact(self):
        """Test that weeks remaining affects trade value calculation"""
        my_team = self.teams[0]
        other_team = self.teams[1]

        my_player = my_team.roster[1]
        their_player = other_team.roster[3]

        # Analysis with many weeks remaining
        analysis_long = self.simulator.analyze_trade(
            my_team, other_team,
            [my_player], [their_player],
            weeks_remaining=10
        )

        # Analysis with few weeks remaining
        analysis_short = self.simulator.analyze_trade(
            my_team, other_team,
            [my_player], [their_player],
            weeks_remaining=2
        )

        # Points added per week should differ based on weeks remaining
        # (though total value change is the same)
        if analysis_long['my_value_change'] != 0:
            ratio = analysis_long['projected_points_added_per_week'] / analysis_short['projected_points_added_per_week']
            self.assertAlmostEqual(ratio, 10.0 / 2.0, delta=0.1)


class TestSimulatorEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_empty_roster(self):
        """Test handling of empty roster"""
        league = Mock()
        league.year = 2024
        league.current_week = 1
        league.teams = []
        league.settings = Mock()
        league.settings.playoff_team_count = 6
        league.settings.reg_season_count = 14

        with patch('espn_api.utils.advanced_simulator.PlayerPerformanceModel'):
            simulator = AdvancedFantasySimulator(league, num_simulations=10, use_gmm=False)

            team = Mock()
            team.roster = []
            team.team_id = 1

            # Should handle gracefully
            score = simulator.simulate_roster_score(team)
            self.assertEqual(score, 0)

    def test_single_simulation(self):
        """Test simulator works with single simulation"""
        league = Mock()
        league.year = 2024
        league.current_week = 1
        league.teams = []
        league.settings = Mock()
        league.settings.playoff_team_count = 6

        with patch('espn_api.utils.advanced_simulator.PlayerPerformanceModel'):
            simulator = AdvancedFantasySimulator(league, num_simulations=1, use_gmm=False)
            self.assertEqual(simulator.num_simulations, 1)


if __name__ == '__main__':
    unittest.main()
