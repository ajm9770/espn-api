"""
Tests for injury status filtering in free agent recommendations
"""

import unittest
from unittest.mock import Mock
from espn_api.utils.advanced_simulator import AdvancedFantasySimulator


class TestInjuryFiltering(unittest.TestCase):
    """Test that injured players are filtered from free agent recommendations"""

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

        # Create mock team
        self.my_team = Mock()
        self.my_team.team_id = 1
        self.my_team.roster = [
            self._create_mock_player("Starter RB", "RB", 15.0, 1),
            self._create_mock_player("Bench RB", "RB", 8.0, 2)
        ]

        # Create simulator without GMM
        from unittest.mock import patch
        with patch('espn_api.utils.advanced_simulator.PlayerPerformanceModel'):
            self.simulator = AdvancedFantasySimulator(
                self.league,
                num_simulations=100,
                use_gmm=False
            )

    def _create_mock_player(self, name, position, avg_points, player_id, injury_status=None):
        """Create a mock player with optional injury status"""
        player = Mock()
        player.name = name
        player.position = position
        player.playerId = player_id
        player.avg_points = avg_points
        player.projected_avg_points = avg_points * 1.05
        player.injuryStatus = injury_status
        player.injury_status = injury_status  # Both attributes
        player.stats = {0: {'points': avg_points * 10, 'avg_points': avg_points}}
        return player

    def test_filters_out_players(self):
        """Test that OUT players are filtered"""
        # Create free agents with various injury statuses
        free_agents = [
            self._create_mock_player("Healthy RB", "RB", 12.0, 101, "ACTIVE"),
            self._create_mock_player("Out RB", "RB", 14.0, 102, "OUT"),
            self._create_mock_player("Normal RB", "RB", 11.0, 103, "NORMAL"),
        ]

        # Get recommendations
        recommendations = self.simulator.recommend_free_agents(
            self.my_team,
            free_agents,
            exclude_injured=True
        )

        # Should only recommend healthy players (ACTIVE and NORMAL)
        self.assertEqual(len(recommendations), 2)
        healthy_names = [r['player'].name for r in recommendations]
        self.assertIn("Healthy RB", healthy_names)
        self.assertIn("Normal RB", healthy_names)

    def test_filters_questionable_players(self):
        """Test that QUESTIONABLE players are filtered"""
        free_agents = [
            self._create_mock_player("Healthy RB", "RB", 12.0, 101, "ACTIVE"),
            self._create_mock_player("Q RB", "RB", 14.0, 102, "QUESTIONABLE"),
        ]

        recommendations = self.simulator.recommend_free_agents(
            self.my_team,
            free_agents,
            exclude_injured=True
        )

        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['player'].name, "Healthy RB")

    def test_filters_doubtful_players(self):
        """Test that DOUBTFUL players are filtered"""
        free_agents = [
            self._create_mock_player("Healthy RB", "RB", 12.0, 101, "ACTIVE"),
            self._create_mock_player("D RB", "RB", 14.0, 102, "DOUBTFUL"),
        ]

        recommendations = self.simulator.recommend_free_agents(
            self.my_team,
            free_agents,
            exclude_injured=True
        )

        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['player'].name, "Healthy RB")

    def test_filters_ir_players(self):
        """Test that INJURY_RESERVE players are filtered"""
        free_agents = [
            self._create_mock_player("Healthy RB", "RB", 12.0, 101, "ACTIVE"),
            self._create_mock_player("IR RB", "RB", 14.0, 102, "INJURY_RESERVE"),
        ]

        recommendations = self.simulator.recommend_free_agents(
            self.my_team,
            free_agents,
            exclude_injured=True
        )

        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['player'].name, "Healthy RB")

    def test_filters_suspended_players(self):
        """Test that suspended players are filtered"""
        free_agents = [
            self._create_mock_player("Healthy RB", "RB", 12.0, 101, "ACTIVE"),
            self._create_mock_player("Suspended RB", "RB", 14.0, 102, "SUSPENSION"),
        ]

        recommendations = self.simulator.recommend_free_agents(
            self.my_team,
            free_agents,
            exclude_injured=True
        )

        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['player'].name, "Healthy RB")

    def test_case_insensitive_filtering(self):
        """Test that injury status filtering is case-insensitive"""
        free_agents = [
            self._create_mock_player("Healthy RB", "RB", 12.0, 101, "active"),  # lowercase
            self._create_mock_player("out RB", "RB", 14.0, 102, "out"),  # lowercase
            self._create_mock_player("Out RB", "RB", 14.0, 103, "Out"),  # mixed case
        ]

        recommendations = self.simulator.recommend_free_agents(
            self.my_team,
            free_agents,
            exclude_injured=True
        )

        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['player'].name, "Healthy RB")

    def test_exclude_injured_false_includes_all(self):
        """Test that exclude_injured=False includes injured players"""
        free_agents = [
            self._create_mock_player("Healthy RB", "RB", 12.0, 101, "ACTIVE"),
            self._create_mock_player("Out RB", "RB", 14.0, 102, "OUT"),
            self._create_mock_player("Q RB", "RB", 13.0, 103, "QUESTIONABLE"),
        ]

        recommendations = self.simulator.recommend_free_agents(
            self.my_team,
            free_agents,
            exclude_injured=False  # Include injured
        )

        # Should include all 3 players
        self.assertEqual(len(recommendations), 3)

    def test_healthy_players_not_filtered(self):
        """Test that players without injury status are not filtered"""
        free_agents = [
            self._create_mock_player("Active RB", "RB", 12.0, 101, "ACTIVE"),
            self._create_mock_player("Normal RB", "RB", 11.0, 102, "NORMAL"),
            self._create_mock_player("None RB", "RB", 10.0, 103, None),
        ]

        recommendations = self.simulator.recommend_free_agents(
            self.my_team,
            free_agents,
            exclude_injured=True
        )

        # All healthy players should be included
        self.assertEqual(len(recommendations), 3)

    def test_mixed_injury_statuses(self):
        """Test filtering with mixed injury statuses"""
        free_agents = [
            self._create_mock_player("Active 1", "RB", 12.0, 101, "ACTIVE"),
            self._create_mock_player("Out", "RB", 15.0, 102, "OUT"),
            self._create_mock_player("Normal 1", "RB", 11.0, 103, "NORMAL"),
            self._create_mock_player("Q", "RB", 14.0, 104, "QUESTIONABLE"),
            self._create_mock_player("Active 2", "RB", 10.0, 105, "ACTIVE"),
            self._create_mock_player("D", "RB", 13.0, 106, "DOUBTFUL"),
            self._create_mock_player("IR", "RB", 16.0, 107, "INJURY_RESERVE"),
        ]

        recommendations = self.simulator.recommend_free_agents(
            self.my_team,
            free_agents,
            exclude_injured=True
        )

        # Should only get the 3 healthy players
        self.assertEqual(len(recommendations), 3)
        healthy_names = [r['player'].name for r in recommendations]
        self.assertIn("Active 1", healthy_names)
        self.assertIn("Normal 1", healthy_names)
        self.assertIn("Active 2", healthy_names)

    def test_injury_filtering_preserves_value_ranking(self):
        """Test that filtering doesn't affect value-based ranking"""
        free_agents = [
            self._create_mock_player("Low Value", "RB", 9.0, 101, "ACTIVE"),
            self._create_mock_player("Injured High", "RB", 20.0, 102, "OUT"),
            self._create_mock_player("High Value", "RB", 18.0, 103, "NORMAL"),
            self._create_mock_player("Medium Value", "RB", 12.0, 104, "ACTIVE"),
        ]

        recommendations = self.simulator.recommend_free_agents(
            self.my_team,
            free_agents,
            top_n=3,
            exclude_injured=True
        )

        # Should be ranked by value: High (18), Medium (12), Low (9)
        # Injured High (20) should be excluded
        self.assertEqual(len(recommendations), 3)
        self.assertEqual(recommendations[0]['player'].name, "High Value")
        self.assertEqual(recommendations[1]['player'].name, "Medium Value")
        self.assertEqual(recommendations[2]['player'].name, "Low Value")


if __name__ == '__main__':
    unittest.main()
