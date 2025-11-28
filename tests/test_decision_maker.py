"""
Integration tests for Fantasy Decision Maker CLI

Tests the main application functionality end-to-end
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fantasy_decision_maker import FantasyDecisionMaker


class TestFantasyDecisionMaker(unittest.TestCase):
    """Integration tests for FantasyDecisionMaker class"""

    @patch('fantasy_decision_maker.League')
    @patch('fantasy_decision_maker.AdvancedFantasySimulator')
    def setUp(self, mock_simulator, mock_league):
        """Set up test fixtures with mocked dependencies"""
        # Mock league
        self.mock_league_class = mock_league
        league_instance = Mock()
        league_instance.teams = self._create_mock_teams()
        league_instance.current_week = 10
        league_instance.settings = Mock()
        league_instance.settings.playoff_team_count = 6
        mock_league.return_value = league_instance

        # Mock simulator
        self.mock_simulator_class = mock_simulator
        simulator_instance = Mock()
        mock_simulator.return_value = simulator_instance

        # Create decision maker instance
        self.dm = FantasyDecisionMaker(
            league_id=123456,
            team_id=1,
            year=2024,
            num_simulations=100
        )

    def _create_mock_teams(self):
        """Create mock teams for testing"""
        teams = []
        for i in range(10):
            team = Mock()
            team.team_id = i + 1
            team.team_name = f"Team {i + 1}"
            team.wins = 5 + i % 3
            team.losses = 4 - i % 3
            team.points_for = 1000 + i * 50
            team.schedule = list(range(1, 15))
            team.roster = []
            teams.append(team)
        return teams

    def test_initialization(self):
        """Test decision maker initializes correctly"""
        self.assertEqual(self.dm.league_id, 123456)
        self.assertEqual(self.dm.team_id, 1)
        self.assertEqual(self.dm.year, 2024)
        self.assertIsNotNone(self.dm.league)
        self.assertIsNotNone(self.dm.my_team)
        self.assertIsNotNone(self.dm.simulator)

    def test_find_my_team(self):
        """Test finding user's team"""
        self.assertEqual(self.dm.my_team.team_id, 1)
        self.assertEqual(self.dm.my_team.team_name, "Team 1")

    @patch('fantasy_decision_maker.League')
    @patch('fantasy_decision_maker.AdvancedFantasySimulator')
    def test_invalid_team_id_raises_error(self, mock_sim, mock_league):
        """Test that invalid team ID raises ValueError"""
        league_instance = Mock()
        league_instance.teams = self._create_mock_teams()
        mock_league.return_value = league_instance

        with self.assertRaises(ValueError):
            FantasyDecisionMaker(
                league_id=123456,
                team_id=999,  # Invalid team ID
                year=2024
            )

    def test_analyze_current_matchup(self):
        """Test matchup analysis"""
        # Mock simulator results
        self.dm.simulator.simulate_matchup.return_value = {
            'team1_win_probability': 65.5,
            'team2_win_probability': 34.5,
            'team1_avg_score': 118.3,
            'team1_score_std': 15.2,
            'team1_score_range': (98.5, 137.8),
            'team2_avg_score': 109.7,
            'team2_score_std': 18.3,
            'team2_score_range': (86.2, 133.4)
        }

        # Should not raise exception
        try:
            self.dm.analyze_current_matchup()
        except Exception as e:
            self.fail(f"analyze_current_matchup raised {e}")

    def test_analyze_free_agents(self):
        """Test free agent analysis"""
        # Mock free agents
        fa1 = Mock()
        fa1.name = "Free Agent 1"
        fa1.position = "RB"

        self.dm.league.free_agents.return_value = [fa1]

        # Mock recommendations
        self.dm.simulator.recommend_free_agents.return_value = [{
            'player': fa1,
            'position': 'RB',
            'value_added': 4.2,
            'drop_candidate': 'Bench Player',
            'fa_projected_avg': 12.3,
            'drop_projected_avg': 8.1,
            'priority': 'HIGH',
            'ownership_pct': 45.2
        }]

        # Should not raise exception
        try:
            self.dm.analyze_free_agents(top_n=5)
        except Exception as e:
            self.fail(f"analyze_free_agents raised {e}")

    def test_analyze_trades(self):
        """Test trade analysis"""
        # Mock trade opportunities
        my_player = Mock()
        my_player.name = "My Player"
        their_player = Mock()
        their_player.name = "Their Player"

        self.dm.simulator.find_trade_opportunities.return_value = [{
            'other_team': 'Team 2',
            'give': ['My Player'],
            'receive': ['Their Player'],
            'analysis': {
                'my_value_change': 8.3,
                'their_value_change': 1.2,
                'advantage_margin': 7.1,
                'projected_points_added_per_week': 0.8,
                'recommendation': 'ACCEPT',
                'confidence': 78,
                'asymmetric_advantage': True
            }
        }]

        # Should not raise exception
        try:
            self.dm.analyze_trades(max_opportunities=5)
        except Exception as e:
            self.fail(f"analyze_trades raised {e}")

    def test_analyze_season_outlook(self):
        """Test season outlook analysis"""
        # Mock season projections
        results = {}
        for team in self.dm.league.teams:
            results[team.team_id] = {
                'current_wins': team.wins,
                'projected_wins': team.wins + 3.5,
                'playoff_odds': 65.5,
                'championship_odds': 12.3
            }

        self.dm.simulator.simulate_season_rest_of_season.return_value = results

        # Should not raise exception
        try:
            self.dm.analyze_season_outlook()
        except Exception as e:
            self.fail(f"analyze_season_outlook raised {e}")

    @patch('builtins.open', create=True)
    def test_generate_weekly_report(self, mock_open):
        """Test weekly report generation"""
        # Mock all analysis methods
        self.dm.simulator.simulate_matchup.return_value = {
            'team1_win_probability': 60.0,
            'team2_win_probability': 40.0,
            'team1_avg_score': 115.0,
            'team1_score_std': 12.0,
            'team1_score_range': (95.0, 135.0),
            'team2_avg_score': 110.0,
            'team2_score_std': 14.0,
            'team2_score_range': (90.0, 130.0)
        }

        self.dm.league.free_agents.return_value = []
        self.dm.simulator.recommend_free_agents.return_value = []
        self.dm.simulator.find_trade_opportunities.return_value = []

        results = {}
        for team in self.dm.league.teams:
            results[team.team_id] = {
                'current_wins': 5,
                'projected_wins': 8.5,
                'playoff_odds': 60.0,
                'championship_odds': 10.0
            }
        self.dm.simulator.simulate_season_rest_of_season.return_value = results

        # Should not raise exception
        try:
            self.dm.generate_weekly_report()
        except Exception as e:
            self.fail(f"generate_weekly_report raised {e}")


class TestDecisionMakerHelpers(unittest.TestCase):
    """Test helper functions and edge cases"""

    @patch('fantasy_decision_maker.League')
    @patch('fantasy_decision_maker.AdvancedFantasySimulator')
    def test_private_league_initialization(self, mock_sim, mock_league):
        """Test initialization with private league credentials"""
        league_instance = Mock()
        league_instance.teams = [Mock()]
        league_instance.teams[0].team_id = 1
        league_instance.current_week = 10
        league_instance.settings = Mock()
        league_instance.settings.playoff_team_count = 6
        mock_league.return_value = league_instance

        dm = FantasyDecisionMaker(
            league_id=123456,
            team_id=1,
            year=2024,
            swid="{test-swid}",
            espn_s2="test-espn-s2"
        )

        # League should be initialized with credentials
        mock_league.assert_called_with(
            league_id=123456,
            year=2024,
            espn_s2="test-espn-s2",
            swid="{test-swid}"
        )

    @patch('fantasy_decision_maker.League')
    @patch('fantasy_decision_maker.AdvancedFantasySimulator')
    def test_custom_cache_dir(self, mock_sim, mock_league):
        """Test custom cache directory"""
        league_instance = Mock()
        league_instance.teams = [Mock()]
        league_instance.teams[0].team_id = 1
        league_instance.current_week = 10
        league_instance.settings = Mock()
        league_instance.settings.playoff_team_count = 6
        mock_league.return_value = league_instance

        custom_cache = '/tmp/custom_cache'
        dm = FantasyDecisionMaker(
            league_id=123456,
            team_id=1,
            year=2024,
            cache_dir=custom_cache
        )

        self.assertEqual(dm.cache_dir, custom_cache)

    @patch('fantasy_decision_maker.League')
    @patch('fantasy_decision_maker.AdvancedFantasySimulator')
    def test_custom_simulations(self, mock_sim, mock_league):
        """Test custom number of simulations"""
        league_instance = Mock()
        league_instance.teams = [Mock()]
        league_instance.teams[0].team_id = 1
        league_instance.current_week = 10
        league_instance.settings = Mock()
        league_instance.settings.playoff_team_count = 6
        mock_league.return_value = league_instance

        dm = FantasyDecisionMaker(
            league_id=123456,
            team_id=1,
            year=2024,
            num_simulations=50000
        )

        self.assertEqual(dm.num_simulations, 50000)


if __name__ == '__main__':
    unittest.main()
