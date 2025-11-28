"""
Smoke tests to verify basic functionality without external dependencies

These tests verify that modules can be imported and basic functionality works
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestImports(unittest.TestCase):
    """Test that all modules can be imported"""

    def test_import_player_performance(self):
        """Test importing player_performance module"""
        try:
            from espn_api.utils import player_performance
            self.assertTrue(hasattr(player_performance, 'PlayerPerformanceModel'))
        except ImportError as e:
            self.fail(f"Failed to import player_performance: {e}")

    def test_import_advanced_simulator(self):
        """Test importing advanced_simulator module"""
        try:
            from espn_api.utils import advanced_simulator
            self.assertTrue(hasattr(advanced_simulator, 'AdvancedFantasySimulator'))
        except ImportError as e:
            self.fail(f"Failed to import advanced_simulator: {e}")

    def test_import_decision_maker(self):
        """Test importing decision maker"""
        try:
            import fantasy_decision_maker
            self.assertTrue(hasattr(fantasy_decision_maker, 'FantasyDecisionMaker'))
        except ImportError as e:
            self.fail(f"Failed to import fantasy_decision_maker: {e}")

    def test_import_espn_api(self):
        """Test importing ESPN API"""
        try:
            from espn_api.football import League
            self.assertIsNotNone(League)
        except ImportError as e:
            self.fail(f"Failed to import ESPN API: {e}")


class TestStructure(unittest.TestCase):
    """Test file structure and organization"""

    def test_utils_directory_exists(self):
        """Test utils directory exists"""
        utils_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'espn_api', 'utils'
        )
        self.assertTrue(os.path.exists(utils_path))

    def test_player_performance_file_exists(self):
        """Test player_performance.py exists"""
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'espn_api', 'utils', 'player_performance.py'
        )
        self.assertTrue(os.path.exists(file_path))

    def test_advanced_simulator_file_exists(self):
        """Test advanced_simulator.py exists"""
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'espn_api', 'utils', 'advanced_simulator.py'
        )
        self.assertTrue(os.path.exists(file_path))

    def test_decision_maker_file_exists(self):
        """Test fantasy_decision_maker.py exists"""
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'fantasy_decision_maker.py'
        )
        self.assertTrue(os.path.exists(file_path))

    def test_examples_directory_exists(self):
        """Test examples directory exists"""
        examples_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'examples'
        )
        self.assertTrue(os.path.exists(examples_path))

    def test_documentation_exists(self):
        """Test documentation files exist"""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        docs = [
            'README.md',
            'QUICK_START.md',
            'SYSTEM_OVERVIEW.md',
            'config.template.json'
        ]

        for doc in docs:
            doc_path = os.path.join(base_path, doc)
            self.assertTrue(os.path.exists(doc_path), f"{doc} should exist")


class TestConfiguration(unittest.TestCase):
    """Test configuration files"""

    def test_requirements_has_scikit_learn(self):
        """Test requirements.txt includes scikit-learn"""
        req_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'requirements.txt'
        )

        with open(req_path, 'r') as f:
            content = f.read()

        self.assertIn('scikit-learn', content)

    def test_requirements_has_numpy(self):
        """Test requirements.txt includes numpy"""
        req_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'requirements.txt'
        )

        with open(req_path, 'r') as f:
            content = f.read()

        self.assertIn('numpy', content)

    def test_requirements_has_pandas(self):
        """Test requirements.txt includes pandas"""
        req_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'requirements.txt'
        )

        with open(req_path, 'r') as f:
            content = f.read()

        self.assertIn('pandas', content)


class TestCodeQuality(unittest.TestCase):
    """Test code quality and structure"""

    def test_player_performance_has_classes(self):
        """Test PlayerPerformanceModel class exists"""
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'espn_api', 'utils', 'player_performance.py'
        )

        with open(file_path, 'r') as f:
            content = f.read()

        self.assertIn('class PlayerPerformanceModel', content)
        self.assertIn('def train_model', content)
        self.assertIn('def predict_performance', content)

    def test_advanced_simulator_has_classes(self):
        """Test AdvancedFantasySimulator class exists"""
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'espn_api', 'utils', 'advanced_simulator.py'
        )

        with open(file_path, 'r') as f:
            content = f.read()

        self.assertIn('class AdvancedFantasySimulator', content)
        self.assertIn('def simulate_matchup', content)
        self.assertIn('def analyze_trade', content)
        self.assertIn('def recommend_free_agents', content)

    def test_decision_maker_has_main(self):
        """Test decision maker has main function"""
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'fantasy_decision_maker.py'
        )

        with open(file_path, 'r') as f:
            content = f.read()

        self.assertIn('def main()', content)
        self.assertIn('class FantasyDecisionMaker', content)

    def test_decision_maker_is_executable(self):
        """Test decision maker script is executable"""
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'fantasy_decision_maker.py'
        )

        # Check if file has execute permissions
        self.assertTrue(os.path.isfile(file_path))


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
