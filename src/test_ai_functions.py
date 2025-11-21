#!/usr/bin/env python3
#
#Comprehensive unit tests for AI functions in HW2_HueristicReal.py
#Tests SearchNode class, utility function, and bestMove function
#unit test helped by ChatGPT

import unittest
import sys
import os
sys.path.append(".")  # Add current directory to path

from AI.HW2_Hueristic_turnin import AIPlayer, SearchNode
from GameState import GameState
from Constants import *
from Move import Move
from Location import Location
from Inventory import Inventory
from Building import Building
from Ant import Ant

class TestSearchNode(unittest.TestCase):
    """Test cases for SearchNode class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.ai_player = AIPlayer(PLAYER_ONE)
        self.game_state = GameState.getBasicState()
        self.sample_move = Move(MOVE_ANT, [(0, 0), (1, 0)])
    
    def test_search_node_initialization(self):
        """Test SearchNode initialization with all parameters."""
        node = SearchNode(
            move=self.sample_move,
            state=self.game_state,
            depth=1,
            parent=None
        )
        
        self.assertEqual(node.move, self.sample_move)
        self.assertEqual(node.state, self.game_state)
        self.assertEqual(node.depth, 1)
        self.assertIsNone(node.parent)
        self.assertIsNone(node.evaluation)  # Should be None until calculated
    
    def test_search_node_with_parent(self):
        """Test SearchNode initialization with parent node."""
        parent_node = SearchNode(
            move=self.sample_move,
            state=self.game_state,
            depth=1,
            parent=None
        )
        
        child_node = SearchNode(
            move=Move(MOVE_ANT, [(1, 0), (2, 0)]),
            state=self.game_state,
            depth=2,
            parent=parent_node
        )
        
        self.assertEqual(child_node.parent, parent_node)
        self.assertEqual(child_node.depth, 2)
    
    def test_calculate_evaluation(self):
        """Test evaluation calculation."""
        node = SearchNode(
            move=self.sample_move,
            state=self.game_state,
            depth=1,
            parent=None
        )
        
        # Calculate evaluation
        evaluation = node.calculate_evaluation(self.ai_player.utility)
        
        # Check that evaluation is set
        self.assertIsNotNone(node.evaluation)
        self.assertEqual(evaluation, node.evaluation)
        
        # Check that evaluation = utility + depth
        expected_utility = self.ai_player.utility(self.game_state)
        expected_evaluation = expected_utility + node.depth
        self.assertAlmostEqual(node.evaluation, expected_evaluation, places=5)
    
    def test_calculate_evaluation_different_depths(self):
        """Test evaluation calculation with different depths."""
        node1 = SearchNode(self.sample_move, self.game_state, 1, None)
        node2 = SearchNode(self.sample_move, self.game_state, 3, None)
        
        eval1 = node1.calculate_evaluation(self.ai_player.utility)
        eval2 = node2.calculate_evaluation(self.ai_player.utility)
        
        # Node with higher depth should have higher evaluation
        self.assertGreater(eval2, eval1)
        self.assertEqual(eval2 - eval1, 2)  # Difference should be exactly 2 (depth difference)
    
    def test_to_dict(self):
        """Test dictionary representation of SearchNode."""
        node = SearchNode(
            move=self.sample_move,
            state=self.game_state,
            depth=2,
            parent=None
        )
        node.calculate_evaluation(self.ai_player.utility)
        
        node_dict = node.to_dict()
        
        self.assertIn('move', node_dict)
        self.assertIn('state', node_dict)
        self.assertIn('depth', node_dict)
        self.assertIn('evaluation', node_dict)
        self.assertIn('parent', node_dict)
        
        self.assertEqual(node_dict['move'], self.sample_move)
        self.assertEqual(node_dict['state'], self.game_state)
        self.assertEqual(node_dict['depth'], 2)
        self.assertEqual(node_dict['evaluation'], node.evaluation)
        self.assertIsNone(node_dict['parent'])
    
    def test_str_representation(self):
        """Test string representation of SearchNode."""
        node = SearchNode(
            move=self.sample_move,
            state=self.game_state,
            depth=1,
            parent=None
        )
        node.calculate_evaluation(self.ai_player.utility)
        
        str_repr = str(node)
        self.assertIn("SearchNode", str_repr)
        self.assertIn("depth=1", str_repr)
        self.assertIn(f"eval={node.evaluation}", str_repr)


class TestUtilityFunction(unittest.TestCase):
    """Test cases for utility function"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.ai_player = AIPlayer(PLAYER_ONE)
        self.game_state = GameState.getBasicState()
    
    def test_utility_basic_state(self):
        """Test utility function with basic game state."""
        utility = self.ai_player.utility(self.game_state)
        
        # Utility should be between 0 and 1
        self.assertGreaterEqual(utility, 0.0)
        self.assertLessEqual(utility, 1.0)
    
    def test_utility_winning_condition(self):
        """Test utility function when player has enough food to win."""
        # Create a state where player has 11+ food (winning condition)
        my_inventory = self.game_state.inventories[PLAYER_ONE]
        my_inventory.foodCount = 11
        
        utility = self.ai_player.utility(self.game_state)
        
        # Should be close to 0.9 (winning condition)
        self.assertGreater(utility, 0.8)
    
    def test_utility_losing_condition(self):
        """Test utility function when player's queen is dead."""
        # Create a state where player's queen is dead
        my_inventory = self.game_state.inventories[PLAYER_ONE]
        my_inventory.ants = []  # Remove all ants including queen
        
        utility = self.ai_player.utility(self.game_state)
        
        # Should be 0 (losing condition)
        self.assertEqual(utility, 0.0)
    
    def test_utility_winning_condition_enemy_queen_dead(self):
        """Test utility function when enemy queen is dead."""
        # Create a state where enemy queen is dead
        enemy_inventory = self.game_state.inventories[PLAYER_TWO]
        enemy_inventory.ants = []  # Remove all ants including queen
        
        utility = self.ai_player.utility(self.game_state)
        
        # Should be 1.0 (winning condition)
        self.assertEqual(utility, 1.0)
    
    def test_utility_food_advantage(self):
        """Test utility function with food advantage."""
        # Create states with different food counts
        state1 = GameState.getBasicState()
        state2 = GameState.getBasicState()
        
        state1.inventories[PLAYER_ONE].foodCount = 5
        state1.inventories[PLAYER_TWO].foodCount = 3
        
        state2.inventories[PLAYER_ONE].foodCount = 3
        state2.inventories[PLAYER_TWO].foodCount = 5
        
        utility1 = self.ai_player.utility(state1)
        utility2 = self.ai_player.utility(state2)
        
        # Player with more food should have higher utility
        self.assertGreater(utility1, utility2)
    
    def test_utility_ant_advantage(self):
        """Test utility function with ant count advantage."""
        # Create states with different ant counts
        state1 = GameState.getBasicState()
        state2 = GameState.getBasicState()
        
        # Add more ants to player in state1
        for i in range(3):
            ant = Ant(PLAYER_ONE, WORKER, (i, 0))
            state1.inventories[PLAYER_ONE].ants.append(ant)
        
        # Add more ants to enemy in state2
        for i in range(3):
            ant = Ant(PLAYER_TWO, WORKER, (i, 9))
            state2.inventories[PLAYER_TWO].ants.append(ant)
        
        utility1 = self.ai_player.utility(state1)
        utility2 = self.ai_player.utility(state2)
        
        # Player with more ants should have higher utility
        self.assertGreater(utility1, utility2)
    
    def test_utility_consistency(self):
        """Test that utility function is consistent for same state."""
        utility1 = self.ai_player.utility(self.game_state)
        utility2 = self.ai_player.utility(self.game_state)
        
        # Same state should give same utility
        self.assertEqual(utility1, utility2)


class TestBestMoveFunction(unittest.TestCase):
    """Test cases for bestMove function"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.ai_player = AIPlayer(PLAYER_ONE)
        self.game_state = GameState.getBasicState()
    
    def test_best_move_empty_list(self):
        """Test bestMove with empty list."""
        result = self.ai_player.bestMove([])
        self.assertIsNone(result)
    
    def test_best_move_single_node(self):
        """Test bestMove with single node."""
        move = Move(MOVE_ANT, [(0, 0), (1, 0)])
        node = self.ai_player.create_search_node(move, self.game_state, depth=1)
        
        result = self.ai_player.bestMove([node])
        self.assertEqual(result, node)
    
    def test_best_move_multiple_nodes(self):
        """Test bestMove with multiple nodes."""
        # Create nodes with different evaluations
        move1 = Move(MOVE_ANT, [(0, 0), (1, 0)])
        move2 = Move(MOVE_ANT, [(1, 0), (2, 0)])
        move3 = Move(MOVE_ANT, [(2, 0), (3, 0)])
        
        node1 = self.ai_player.create_search_node(move1, self.game_state, depth=1)
        node2 = self.ai_player.create_search_node(move2, self.game_state, depth=2)
        node3 = self.ai_player.create_search_node(move3, self.game_state, depth=3)
        
        nodes = [node1, node2, node3]
        result = self.ai_player.bestMove(nodes)
        
        # Should return the node with highest evaluation
        self.assertIsNotNone(result)
        self.assertIn(result, nodes)
        
        # Verify it's actually the best
        max_eval = max(node.evaluation for node in nodes)
        self.assertEqual(result.evaluation, max_eval)
    
    def test_best_move_tie_breaking(self):
        """Test bestMove when multiple nodes have same evaluation."""
        # Create nodes with same evaluation by using same depth and state
        move1 = Move(MOVE_ANT, [(0, 0), (1, 0)])
        move2 = Move(MOVE_ANT, [(1, 0), (2, 0)])
        
        node1 = self.ai_player.create_search_node(move1, self.game_state, depth=1)
        node2 = self.ai_player.create_search_node(move2, self.game_state, depth=1)
        
        nodes = [node1, node2]
        result = self.ai_player.bestMove(nodes)
        
        # Should return one of the nodes (max() behavior with ties)
        self.assertIsNotNone(result)
        self.assertIn(result, nodes)
        self.assertEqual(result.evaluation, node1.evaluation)
        self.assertEqual(result.evaluation, node2.evaluation)
    
    def test_best_move_different_depths(self):
        """Test bestMove with nodes of different depths."""
        move1 = Move(MOVE_ANT, [(0, 0), (1, 0)])
        move2 = Move(MOVE_ANT, [(1, 0), (2, 0)])
        
        # Create nodes with different depths
        node1 = self.ai_player.create_search_node(move1, self.game_state, depth=1)
        node2 = self.ai_player.create_search_node(move2, self.game_state, depth=5)
        
        nodes = [node1, node2]
        result = self.ai_player.bestMove(nodes)
        
        # Node with higher depth should have higher evaluation
        self.assertEqual(result, node2)
        self.assertGreater(node2.evaluation, node1.evaluation)


class TestAIPlayerIntegration(unittest.TestCase):
    """Integration tests for AIPlayer methods"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.ai_player = AIPlayer(PLAYER_ONE)
        self.game_state = GameState.getBasicState()
    
    def test_create_search_node(self):
        """Test create_search_node helper method."""
        move = Move(MOVE_ANT, [(0, 0), (1, 0)])
        node = self.ai_player.create_search_node(move, self.game_state, depth=2)
        
        self.assertIsInstance(node, SearchNode)
        self.assertEqual(node.move, move)
        self.assertEqual(node.state, self.game_state)
        self.assertEqual(node.depth, 2)
        self.assertIsNotNone(node.evaluation)  # Should be calculated automatically
    
    def test_create_search_node_with_parent(self):
        """Test create_search_node with parent node."""
        parent_move = Move(MOVE_ANT, [(0, 0), (1, 0)])
        parent_node = self.ai_player.create_search_node(parent_move, self.game_state, depth=1)
        
        child_move = Move(MOVE_ANT, [(1, 0), (2, 0)])
        child_node = self.ai_player.create_search_node(child_move, self.game_state, depth=2, parent=parent_node)
        
        self.assertEqual(child_node.parent, parent_node)
        self.assertEqual(child_node.depth, 2)
    
    def test_utility_function_edge_cases(self):
        """Test utility function with edge cases."""
        # Test with very high food count
        state = GameState.getBasicState()
        state.inventories[PLAYER_ONE].foodCount = 50
        utility = self.ai_player.utility(state)
        self.assertGreaterEqual(utility, 0.8)  # Should be high
        
        # Test with zero food
        state.inventories[PLAYER_ONE].foodCount = 0
        state.inventories[PLAYER_TWO].foodCount = 0
        utility = self.ai_player.utility(state)
        self.assertGreaterEqual(utility, 0.0)  # Should be valid
        
        # Test with negative food (if possible)
        state.inventories[PLAYER_ONE].foodCount = -1
        utility = self.ai_player.utility(state)
        self.assertGreaterEqual(utility, 0.0)  # Should handle gracefully


def run_tests():
    """Run all tests and display results."""
    print("Running AI Functions Unit Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestSearchNode))
    test_suite.addTest(unittest.makeSuite(TestUtilityFunction))
    test_suite.addTest(unittest.makeSuite(TestBestMoveFunction))
    test_suite.addTest(unittest.makeSuite(TestAIPlayerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
