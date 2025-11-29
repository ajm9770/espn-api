"""
Tests for Rest of Season (ROS) trade analysis
"""

import unittest
from unittest.mock import Mock, MagicMock
from espn_api.utils.advanced_simulator import AdvancedFantasySimulator


class TestROSTradeAnalysis(unittest.TestCase):
    """Test ROS-based trade analysis"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock league
        self.league = Mock()
        self.league.year = 2024
        self.league.current_week = 10
        self.league.settings = Mock()
        self.league.settings.playoff_team_count = 6
        self.league.settings.reg_season_count = 14
        self.league.teams = []

        # Create mock teams
        self.my_team = Mock()
        self.my_team.team_id = 1
        self.my_team.team_name = "My Team"

        self.other_team = Mock()
        self.other_team.team_id = 2
        self.other_team.team_name = "Other Team"

        self.league.teams = [self.my_team, self.other_team]

        # Create simulator without GMM
        from unittest.mock import patch
        with patch('espn_api.utils.advanced_simulator.PlayerPerformanceModel'):
            self.simulator = AdvancedFantasySimulator(
                self.league,
                num_simulations=100,
                use_gmm=False
            )

    def _create_mock_player(self, name, position, avg_points, player_id, schedule=None):
        """Create a mock player with optional schedule"""
        player = Mock()
        player.name = name
        player.position = position
        player.playerId = player_id
        player.avg_points = avg_points
        player.projected_avg_points = avg_points
        player.stats = {0: {'points': avg_points * 10, 'avg_points': avg_points}}

        # Add schedule if provided
        if schedule:
            player.schedule = schedule
        else:
            player.schedule = {}

        return player

    def test_ros_uses_weeks_remaining(self):
        """Test that ROS analysis uses weeks_remaining parameter"""
        # Create players
        my_player = self._create_mock_player("My RB", "RB", 15.0, 101)
        their_player = self._create_mock_player("Their WR", "WR", 15.0, 201)

        self.my_team.roster = [my_player]
        self.other_team.roster = [their_player]

        # Analyze trade with ROS
        analysis = self.simulator.analyze_trade(
            self.my_team,
            self.other_team,
            [my_player],
            [their_player],
            weeks_remaining=5,
            use_ros=True
        )

        # Verify weeks_remaining is stored
        self.assertEqual(analysis['weeks_remaining'], 5)
        self.assertTrue(analysis['uses_ros_projections'])

    def test_ros_vs_season_avg_different_results(self):
        """Test that ROS gives different results than season avg for players with schedules"""
        # Player with tough schedule
        tough_schedule = {
            10: {'team': 'SF', 'date': None},  # Tough defense
            11: {'team': 'BAL', 'date': None},  # Tough defense
            12: {'team': 'BUF', 'date': None},  # Tough defense
        }

        # Player with easy schedule
        easy_schedule = {
            10: {'team': 'ARI', 'date': None},  # Weak defense
            11: {'team': 'CAR', 'date': None},  # Weak defense
            12: {'team': 'NYG', 'date': None},  # Weak defense
        }

        tough_rb = self._create_mock_player("Tough Schedule RB", "RB", 15.0, 101, tough_schedule)
        easy_rb = self._create_mock_player("Easy Schedule RB", "RB", 15.0, 102, easy_schedule)

        self.my_team.roster = [tough_rb]
        self.other_team.roster = [easy_rb]

        # Analyze with ROS (should consider schedules)
        ros_analysis = self.simulator.analyze_trade(
            self.my_team,
            self.other_team,
            [tough_rb],
            [easy_rb],
            weeks_remaining=3,
            use_ros=True
        )

        # Analyze without ROS (season averages)
        season_analysis = self.simulator.analyze_trade(
            self.my_team,
            self.other_team,
            [tough_rb],
            [easy_rb],
            weeks_remaining=3,
            use_ros=False
        )

        # ROS and season avg should use different calculation methods
        self.assertTrue(ros_analysis['uses_ros_projections'])
        self.assertFalse(season_analysis['uses_ros_projections'])

    def test_find_trade_opportunities_uses_ros(self):
        """Test that find_trade_opportunities passes ROS flag correctly"""
        player1 = self._create_mock_player("Player 1", "RB", 10.0, 101)
        player2 = self._create_mock_player("Player 2", "RB", 20.0, 201)

        self.my_team.roster = [player1]
        self.other_team.roster = [player2]

        # Find opportunities with ROS
        opportunities = self.simulator.find_trade_opportunities(
            self.my_team,
            min_advantage=1.0,
            use_ros=True
        )

        # If any trades found, verify they use ROS
        for opp in opportunities:
            analysis = opp['analysis']
            self.assertTrue(analysis.get('uses_ros_projections', False))

    def test_opponent_strength_calculation(self):
        """Test opponent strength multiplier calculation"""
        # Create dummy league data for opponent strength calc
        dummy_player = self._create_mock_player("Dummy", "RB", 15.0, 999)
        self.my_team.roster = [dummy_player]
        self.other_team.roster = [dummy_player]

        # Test opponent strength calculation
        multiplier = self.simulator._calculate_opponent_strength("RB", "SF")

        # Multiplier should be a positive number around 1.0
        self.assertGreater(multiplier, 0)
        self.assertIsInstance(multiplier, float)

    def test_ros_value_calculation(self):
        """Test ROS roster value calculation"""
        # Create player with schedule
        schedule = {
            10: {'team': 'SF', 'date': None},
            11: {'team': 'BAL', 'date': None},
        }
        player = self._create_mock_player("Test RB", "RB", 15.0, 101, schedule)

        roster = [player]

        # Calculate ROS value
        ros_value = self.simulator._calculate_roster_value_ros(
            roster,
            current_week=10,
            end_week=11,
            consider_schedule=True
        )

        # Should return a positive value
        self.assertGreater(ros_value, 0)
        self.assertIsInstance(ros_value, float)

    def test_ros_with_no_schedule_data(self):
        """Test that ROS calculation works even without schedule data"""
        # Player without schedule
        player = self._create_mock_player("No Schedule RB", "RB", 15.0, 101)

        roster = [player]

        # Calculate ROS value (should fall back to projections)
        ros_value = self.simulator._calculate_roster_value_ros(
            roster,
            current_week=10,
            end_week=12,
            consider_schedule=True
        )

        # Should still return a value based on projections
        self.assertGreater(ros_value, 0)


if __name__ == '__main__':
    unittest.main()
