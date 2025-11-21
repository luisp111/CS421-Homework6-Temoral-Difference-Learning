#!/usr/bin/env python3
#Focused unit tests for the utility function


import unittest
import sys
sys.path.append(".")

from AI.HW2_HueristicReal import AIPlayer
from GameState import GameState
from Constants import *
from Ant import Ant

class TestUtilityFunctionFocused(unittest.TestCase):
    #Focused test cases for utility function#
    
    def setUp(self):
        #Set up test fixtures before each test method.
        self.ai_player = AIPlayer(PLAYER_ONE)
        self.game_state = GameState.getBasicState()
    
    def test_utility_basic_functionality(self):
        #Test basic utility function behavior.
        utility = self.ai_player.utility(self.game_state)
        
        # Basic constraints
        self.assertIsInstance(utility, float)
        self.assertGreaterEqual(utility, 0.0)
        self.assertLessEqual(utility, 1.0)
        
        print(f"Basic utility value: {utility:.4f}")
    
    def test_utility_food_scoring(self):
        #Test utility function food scoring mechanism.
        # Test with different food counts
        test_cases = [
            (0, 0, "Equal food"),
            (5, 3, "Player advantage"),
            (3, 5, "Enemy advantage"),
            (11, 0, "Player winning condition"),
            (0, 11, "Enemy winning condition")
        ]
        
        for player_food, enemy_food, description in test_cases:
            with self.subTest(description=description):
                state = GameState.getBasicState()
                state.inventories[PLAYER_ONE].foodCount = player_food
                state.inventories[PLAYER_TWO].foodCount = enemy_food
                
                utility = self.ai_player.utility(state)
                print(f"{description}: Player={player_food}, Enemy={enemy_food}, Utility={utility:.4f}")
                
                # Basic validation
                self.assertGreaterEqual(utility, 0.0)
                self.assertLessEqual(utility, 1.0)
    
    def test_utility_queen_status(self):
        #Test utility function queen status handling.
        # Test with both queens alive
        state = GameState.getBasicState()
        utility_both_alive = self.ai_player.utility(state)
        
        # Test with player queen dead
        state.inventories[PLAYER_ONE].ants = []
        utility_player_dead = self.ai_player.utility(state)
        
        # Test with enemy queen dead
        state = GameState.getBasicState()
        state.inventories[PLAYER_TWO].ants = []
        utility_enemy_dead = self.ai_player.utility(state)
        
        print(f"Both queens alive: {utility_both_alive:.4f}")
        print(f"Player queen dead: {utility_player_dead:.4f}")
        print(f"Enemy queen dead: {utility_enemy_dead:.4f}")
        
        # Player queen dead should give lowest utility
        self.assertEqual(utility_player_dead, 0.0)
        
        # Enemy queen dead should give highest utility
        self.assertEqual(utility_enemy_dead, 1.0)
    
    def test_utility_ant_count_scoring(self):
        #Test utility function ant count scoring.
        state = GameState.getBasicState()
        
        # Add different numbers of ants
        for i in range(3):
            worker = Ant(PLAYER_ONE, WORKER, (i, 0))
            state.inventories[PLAYER_ONE].ants.append(worker)
        
        for i in range(2):
            worker = Ant(PLAYER_TWO, WORKER, (i, 9))
            state.inventories[PLAYER_TWO].ants.append(worker)
        
        utility = self.ai_player.utility(state)
        print(f"Utility with 3 player ants, 2 enemy ants: {utility:.4f}")
        
        # Should be reasonable value
        self.assertGreater(utility, 0.0)
        self.assertLess(utility, 1.0)
    
    def test_utility_attacker_scoring(self):
        """Test utility function attacker ant scoring."""
        state = GameState.getBasicState()
        
        # Add attacker ants
        soldier = Ant(PLAYER_ONE, SOLDIER, (0, 0))
        state.inventories[PLAYER_ONE].ants.append(soldier)
        
        utility = self.ai_player.utility(state)
        print(f"Utility with player soldier: {utility:.4f}")
        
        # Should be valid
        self.assertGreaterEqual(utility, 0.0)
        self.assertLessEqual(utility, 1.0)
    
    def test_utility_worker_carrying_food(self):
        """Test utility function with workers carrying food."""
        state = GameState.getBasicState()
        
        # Create a worker carrying food
        worker = Ant(PLAYER_ONE, WORKER, (0, 0))
        worker.carrying = True
        state.inventories[PLAYER_ONE].ants.append(worker)
        
        utility = self.ai_player.utility(state)
        print(f"Utility with carrying worker: {utility:.4f}")
        
        # Should be valid
        self.assertGreaterEqual(utility, 0.0)
        self.assertLessEqual(utility, 1.0)
    
    def test_utility_consistency(self):
        """Test utility function consistency."""
        # Same state should give same utility
        utility1 = self.ai_player.utility(self.game_state)
        utility2 = self.ai_player.utility(self.game_state)
        
        self.assertEqual(utility1, utility2)
        print(f"Consistency test passed: {utility1:.4f} == {utility2:.4f}")
    
    def test_utility_edge_cases(self):
        """Test utility function edge cases."""
        # Test with very high food count
        state = GameState.getBasicState()
        state.inventories[PLAYER_ONE].foodCount = 100
        utility_high_food = self.ai_player.utility(state)
        
        # Test with negative food (if possible)
        state.inventories[PLAYER_ONE].foodCount = -1
        utility_negative_food = self.ai_player.utility(state)
        
        print(f"High food utility: {utility_high_food:.4f}")
        print(f"Negative food utility: {utility_negative_food:.4f}")
        
        # Both should be valid
        self.assertGreaterEqual(utility_high_food, 0.0)
        self.assertLessEqual(utility_high_food, 1.0)
        self.assertGreaterEqual(utility_negative_food, 0.0)
        self.assertLessEqual(utility_negative_food, 1.0)

def run_utility_tests():
    """Run utility function tests with detailed output."""
    print("Running Utility Function Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestUtilityFunctionFocused))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_utility_tests()
    sys.exit(0 if success else 1)