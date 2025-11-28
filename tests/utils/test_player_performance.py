"""
Unit tests for PlayerPerformanceModel

Tests GMM training, caching, prediction, and state detection
"""

import unittest
import os
import shutil
import tempfile
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from espn_api.utils.player_performance import PlayerPerformanceModel


class TestPlayerPerformanceModel(unittest.TestCase):
    """Test PlayerPerformanceModel functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary cache directory
        self.cache_dir = tempfile.mkdtemp()
        self.model = PlayerPerformanceModel(n_components=3, cache_dir=self.cache_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary cache directory
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)

    def _create_mock_player(self, player_id, weekly_scores):
        """Create a mock player with stats"""
        player = Mock()
        player.playerId = player_id
        player.name = f"Test Player {player_id}"
        player.position = "WR"
        player.avg_points = np.mean(weekly_scores) if weekly_scores else 0
        player.projected_avg_points = player.avg_points * 1.1

        # Create stats dict with weekly scores
        player.stats = {0: {'points': sum(weekly_scores), 'avg_points': player.avg_points}}
        for week, score in enumerate(weekly_scores, 1):
            player.stats[week] = {
                'points': score,
                'projected_points': score * 1.1,
                'breakdown': {},
                'avg_points': score
            }

        return player

    def test_model_initialization(self):
        """Test model initializes correctly"""
        self.assertEqual(self.model.n_components, 3)
        self.assertEqual(self.model.cache_dir, self.cache_dir)
        self.assertEqual(len(self.model.models), 0)
        self.assertEqual(len(self.model.player_states), 0)

    def test_cache_path_generation(self):
        """Test cache path generation"""
        path = self.model._get_cache_path(12345, 2024)
        expected = os.path.join(self.cache_dir, 'player_12345_2024.pkl')
        self.assertEqual(path, expected)

    def test_train_model_insufficient_data(self):
        """Test training with insufficient data returns None"""
        # Player with only 3 weeks (need 5)
        player = self._create_mock_player(1, [10.0, 12.0, 8.0])
        result = self.model.train_model(player, 2024)
        self.assertIsNone(result)

    def test_train_model_success(self):
        """Test successful model training"""
        # Player with 10 weeks of data
        weekly_scores = [15.2, 18.3, 12.1, 20.5, 14.8, 16.9, 11.2, 19.4, 17.1, 13.6]
        player = self._create_mock_player(1, weekly_scores)

        model = self.model.train_model(player, 2024)

        self.assertIsNotNone(model)
        self.assertIn(1, self.model.models)
        self.assertIn(1, self.model.player_states)

    def test_player_state_detection(self):
        """Test player state (hot/normal/cold) detection"""
        # Player trending hot (recent scores higher than average)
        weekly_scores = [10.0, 11.0, 12.0, 13.0, 14.0, 18.0, 19.0, 20.0]
        player = self._create_mock_player(2, weekly_scores)

        self.model.train_model(player, 2024)

        state = self.model.player_states[2]
        self.assertIn('current_state', state)
        self.assertEqual(state['current_state'], 'hot')
        self.assertEqual(len(state['recent_scores']), 3)

    def test_cold_streak_detection(self):
        """Test cold streak detection"""
        # Player trending cold (recent scores lower than average)
        weekly_scores = [20.0, 19.0, 18.0, 17.0, 16.0, 12.0, 10.0, 8.0]
        player = self._create_mock_player(3, weekly_scores)

        self.model.train_model(player, 2024)

        state = self.model.player_states[3]
        self.assertEqual(state['current_state'], 'cold')

    def test_caching_saves_model(self):
        """Test that model is saved to cache"""
        weekly_scores = [15.0, 16.0, 14.0, 17.0, 15.5, 16.5, 14.5, 15.8]
        player = self._create_mock_player(4, weekly_scores)

        self.model.train_model(player, 2024)

        cache_path = self.model._get_cache_path(4, 2024)
        self.assertTrue(os.path.exists(cache_path))

    def test_caching_loads_model(self):
        """Test that cached model is loaded"""
        weekly_scores = [15.0, 16.0, 14.0, 17.0, 15.5, 16.5, 14.5, 15.8]
        player = self._create_mock_player(5, weekly_scores)

        # Train and cache
        self.model.train_model(player, 2024)
        original_state = self.model.player_states[5].copy()

        # Create new model instance and load from cache
        new_model = PlayerPerformanceModel(cache_dir=self.cache_dir)
        new_model.train_model(player, 2024, force_retrain=False)

        # Should have loaded from cache
        self.assertIn(5, new_model.models)
        self.assertEqual(new_model.player_states[5]['season_avg'], original_state['season_avg'])

    def test_predict_performance_without_model(self):
        """Test prediction falls back to normal distribution without model"""
        player = self._create_mock_player(6, [15.0])
        player.avg_points = 15.0
        player.projected_avg_points = 16.5

        predictions = self.model.predict_performance(player, n_samples=100)

        self.assertEqual(len(predictions), 100)
        self.assertTrue(np.all(predictions >= 0))  # All predictions non-negative
        # Mean should be around projected average (within 20%)
        self.assertAlmostEqual(np.mean(predictions), 16.5, delta=5.0)

    def test_predict_performance_with_model(self):
        """Test prediction using trained GMM"""
        weekly_scores = [15.0, 16.0, 14.0, 17.0, 15.5, 16.5, 14.5, 15.8]
        player = self._create_mock_player(7, weekly_scores)

        self.model.train_model(player, 2024)
        predictions = self.model.predict_performance(player, n_samples=1000)

        self.assertEqual(len(predictions), 1000)
        self.assertTrue(np.all(predictions >= 0))
        # Mean should be close to season average
        self.assertAlmostEqual(np.mean(predictions), np.mean(weekly_scores), delta=2.0)

    def test_predict_with_state_bias(self):
        """Test that state bias affects predictions"""
        # Hot streak player
        weekly_scores = [10.0, 11.0, 12.0, 13.0, 14.0, 18.0, 19.0, 20.0]
        player = self._create_mock_player(8, weekly_scores)

        self.model.train_model(player, 2024)

        # Predictions with state bias should trend higher
        biased_preds = self.model.predict_performance(player, n_samples=1000, use_state_bias=True)
        unbiased_preds = self.model.predict_performance(player, n_samples=1000, use_state_bias=False)

        # Biased predictions should have higher mean (hot streak)
        self.assertGreater(np.mean(biased_preds), np.mean(unbiased_preds))

    def test_get_player_variance(self):
        """Test getting player variance"""
        weekly_scores = [15.0, 20.0, 10.0, 18.0, 12.0, 16.0, 14.0, 17.0]
        player = self._create_mock_player(9, weekly_scores)

        self.model.train_model(player, 2024)
        variance = self.model.get_player_variance(player)

        expected_std = np.std(weekly_scores)
        self.assertAlmostEqual(variance, expected_std, delta=1.0)

    def test_get_player_variance_no_model(self):
        """Test variance fallback without model"""
        player = self._create_mock_player(10, [])
        player.avg_points = 15.0

        variance = self.model.get_player_variance(player)

        # Should be approximately 25% of mean
        self.assertAlmostEqual(variance, 15.0 * 0.25, delta=1.0)

    def test_bulk_train(self):
        """Test bulk training multiple players"""
        players = [
            self._create_mock_player(11, [15.0, 16.0, 14.0, 17.0, 15.5, 16.5]),
            self._create_mock_player(12, [10.0, 11.0, 10.5, 11.5, 10.0, 11.0]),
            self._create_mock_player(13, [5.0, 6.0]),  # Insufficient data
        ]

        results = self.model.bulk_train(players, 2024)

        self.assertTrue(results[11])  # Should succeed
        self.assertTrue(results[12])  # Should succeed
        self.assertFalse(results[13])  # Should fail (insufficient data)

    def test_force_retrain(self):
        """Test force retrain ignores cache"""
        weekly_scores = [15.0, 16.0, 14.0, 17.0, 15.5, 16.5, 14.5, 15.8]
        player = self._create_mock_player(14, weekly_scores)

        # Train and cache
        self.model.train_model(player, 2024)
        cache_path = self.model._get_cache_path(14, 2024)
        original_mtime = os.path.getmtime(cache_path)

        # Wait a bit and force retrain
        import time
        time.sleep(0.1)
        self.model.train_model(player, 2024, force_retrain=True)

        new_mtime = os.path.getmtime(cache_path)
        self.assertGreater(new_mtime, original_mtime)

    def test_non_negative_predictions(self):
        """Test that predictions are always non-negative"""
        # Player with low scores (could generate negative predictions)
        weekly_scores = [2.0, 3.0, 1.5, 2.5, 2.0, 1.0, 2.2, 1.8]
        player = self._create_mock_player(15, weekly_scores)

        self.model.train_model(player, 2024)
        predictions = self.model.predict_performance(player, n_samples=1000)

        # All predictions should be >= 0
        self.assertTrue(np.all(predictions >= 0))

    def test_get_player_state(self):
        """Test getting player state info"""
        weekly_scores = [15.0, 16.0, 14.0, 17.0, 15.5, 16.5, 14.5, 15.8]
        player = self._create_mock_player(16, weekly_scores)

        self.model.train_model(player, 2024)
        state = self.model.get_player_state(player)

        self.assertIn('season_avg', state)
        self.assertIn('season_std', state)
        self.assertIn('current_state', state)
        self.assertIn('recent_scores', state)

    def test_component_reduction_with_few_weeks(self):
        """Test that components are reduced for players with limited data"""
        # 5 weeks - should use fewer components
        weekly_scores = [15.0, 16.0, 14.0, 17.0, 15.5]
        player = self._create_mock_player(17, weekly_scores)

        model = self.model.train_model(player, 2024)

        # Should have reduced number of components (not 3)
        self.assertIsNotNone(model)
        self.assertLessEqual(model.n_components, 2)


if __name__ == '__main__':
    unittest.main()
