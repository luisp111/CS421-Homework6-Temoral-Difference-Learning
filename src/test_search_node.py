#!/usr/bin/env python3
"""
Comprehensive test script for SearchNode functionality.
"""

import unittest
import sys
sys.path.append(".")  # Add current directory to path

from AI.HW2_HueristicReal import AIPlayer, SearchNode
from GameState import GameState
from Constants import *
from Move import Move

class TestSearchNodeComprehensive(unittest.TestCase):
    """Comprehensive test cases for SearchNode class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.ai_player = AIPlayer(PLAYER_ONE)
        self.game_state = GameState.getBasicState()
        self.sample_move = Move(MOVE_ANT, [(0, 0), (1, 0)])
    
    def test_search_node_creation(self):
        """Test SearchNode creation and basic properties."""
        print("Testing SearchNode creation...")
        
        search_node = SearchNode(
            move=self.sample_move,
            state=self.game_state,
            depth=1,
            parent=None
        )
        
        # Test basic properties
        self.assertEqual(search_node.move, self.sample_move)
        self.assertEqual(search_node.state, self.game_state)
        self.assertEqual(search_node.depth, 1)
        self.assertIsNone(search_node.parent)
        self.assertIsNone(search_node.evaluation)  # Should be None until calculated
        
        print(f"✓ SearchNode created successfully")
        print(f"  Move: {search_node.move}")
        print(f"  Depth: {search_node.depth}")
        print(f"  Parent: {search_node.parent}")
    
    def test_evaluation_calculation(self):
        """Test evaluation calculation functionality."""
        print("\nTesting evaluation calculation...")
        
        search_node = SearchNode(
            move=self.sample_move,
            state=self.game_state,
            depth=1,
            parent=None
        )
        
        # Calculate evaluation
        evaluation = search_node.calculate_evaluation(self.ai_player.utility)
        
        # Test evaluation properties
        self.assertIsNotNone(evaluation)
        self.assertIsNotNone(search_node.evaluation)
        self.assertEqual(evaluation, search_node.evaluation)
        
        # Test evaluation formula: utility + depth
        expected_utility = self.ai_player.utility(self.game_state)
        expected_evaluation = expected_utility + search_node.depth
        self.assertAlmostEqual(evaluation, expected_evaluation, places=5)
        
        print(f"✓ Evaluation calculated: {evaluation:.4f}")
        print(f"  Utility: {expected_utility:.4f}")
        print(f"  Depth: {search_node.depth}")
        print(f"  Total: {expected_utility + search_node.depth:.4f}")
    
    def test_different_depths(self):
        """Test SearchNode with different depths."""
        print("\nTesting different depths...")
        
        depths = [1, 2, 3, 5]
        evaluations = []
        
        for depth in depths:
            node = SearchNode(self.sample_move, self.game_state, depth, None)
            evaluation = node.calculate_evaluation(self.ai_player.utility)
            evaluations.append(evaluation)
            
            print(f"  Depth {depth}: Evaluation {evaluation:.4f}")
        
        # Higher depth should give higher evaluation
        for i in range(1, len(evaluations)):
            self.assertGreater(evaluations[i], evaluations[i-1])
            # Difference should be equal to depth difference
            expected_diff = depths[i] - depths[i-1]
            self.assertEqual(evaluations[i] - evaluations[i-1], expected_diff)
        
        print("✓ Depth scaling works correctly")
    
    def test_parent_child_relationship(self):
        """Test parent-child relationships between SearchNodes."""
        print("\nTesting parent-child relationships...")
        
        # Create parent node
        parent_node = SearchNode(
            move=self.sample_move,
            state=self.game_state,
            depth=1,
            parent=None
        )
        parent_node.calculate_evaluation(self.ai_player.utility)
        
        # Create child node
        child_move = Move(MOVE_ANT, [(1, 0), (2, 0)])
        child_node = SearchNode(
            move=child_move,
            state=self.game_state,
            depth=2,
            parent=parent_node
        )
        child_node.calculate_evaluation(self.ai_player.utility)
        
        # Test relationships
        self.assertEqual(child_node.parent, parent_node)
        self.assertGreater(child_node.depth, parent_node.depth)
        self.assertGreater(child_node.evaluation, parent_node.evaluation)
        
        print(f"✓ Parent-child relationship established")
        print(f"  Parent depth: {parent_node.depth}, evaluation: {parent_node.evaluation:.4f}")
        print(f"  Child depth: {child_node.depth}, evaluation: {child_node.evaluation:.4f}")
    
    def test_dictionary_representation(self):
        """Test dictionary representation of SearchNode."""
        print("\nTesting dictionary representation...")
        
        search_node = SearchNode(
            move=self.sample_move,
            state=self.game_state,
            depth=2,
            parent=None
        )
        search_node.calculate_evaluation(self.ai_player.utility)
        
        node_dict = search_node.to_dict()
        
        # Test dictionary contents
        self.assertIn('move', node_dict)
        self.assertIn('state', node_dict)
        self.assertIn('depth', node_dict)
        self.assertIn('evaluation', node_dict)
        self.assertIn('parent', node_dict)
        
        # Test dictionary values
        self.assertEqual(node_dict['move'], self.sample_move)
        self.assertEqual(node_dict['state'], self.game_state)
        self.assertEqual(node_dict['depth'], 2)
        self.assertEqual(node_dict['evaluation'], search_node.evaluation)
        self.assertIsNone(node_dict['parent'])
        
        print("✓ Dictionary representation:")
        for key, value in node_dict.items():
            if key == 'state':
                print(f"  {key}: GameState object")
            elif key == 'parent':
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
    
    def test_string_representation(self):
        """Test string representation of SearchNode."""
        print("\nTesting string representation...")
        
        search_node = SearchNode(
            move=self.sample_move,
            state=self.game_state,
            depth=1,
            parent=None
        )
        search_node.calculate_evaluation(self.ai_player.utility)
        
        str_repr = str(search_node)
        
        # Test string contents
        self.assertIn("SearchNode", str_repr)
        self.assertIn("depth=1", str_repr)
        self.assertIn(f"eval={search_node.evaluation}", str_repr)
        
        print(f"✓ String representation: {str_repr}")
    
    def test_create_search_node_helper(self):
        """Test the create_search_node helper method."""
        print("\nTesting create_search_node helper...")
        
        search_node = self.ai_player.create_search_node(
            move=self.sample_move,
            state=self.game_state,
            depth=1
        )
        
        # Test that evaluation is automatically calculated
        self.assertIsNotNone(search_node.evaluation)
        self.assertIsInstance(search_node, SearchNode)
        
        print(f"✓ Helper method works: evaluation = {search_node.evaluation:.4f}")
    
    def test_evaluation_consistency(self):
        """Test that evaluation is consistent for same parameters."""
        print("\nTesting evaluation consistency...")
        
        # Create two identical nodes
        node1 = SearchNode(self.sample_move, self.game_state, 1, None)
        node2 = SearchNode(self.sample_move, self.game_state, 1, None)
        
        eval1 = node1.calculate_evaluation(self.ai_player.utility)
        eval2 = node2.calculate_evaluation(self.ai_player.utility)
        
        # Should be identical
        self.assertEqual(eval1, eval2)
        
        print(f"✓ Evaluation consistency: {eval1:.4f} == {eval2:.4f}")

def run_search_node_tests():
    """Run SearchNode tests with detailed output."""
    print("Running SearchNode Comprehensive Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestSearchNodeComprehensive))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
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

def test_search_node_demo():
    """Demonstration of SearchNode usage."""
    print("SearchNode Usage Demonstration")
    print("=" * 50)
    
    # Create AI player
    ai_player = AIPlayer(PLAYER_ONE)
    
    # Get a basic game state
    current_state = GameState.getBasicState()
    print(f"Current state utility: {ai_player.utility(current_state):.3f}")
    print()
    
    # Create a sample move
    sample_move = Move(MOVE_ANT, [(0, 0), (1, 0)])
    
    # Create search nodes for different depths
    print("Creating SearchNodes for different depths:")
    for depth in [1, 2, 3]:
        search_node = ai_player.create_search_node(
        move=sample_move,
        state=current_state,
            depth=depth
        )
        print(f"  Depth {depth}: Evaluation {search_node.evaluation:.4f}")
    
    print("\nSearchNode demonstration completed!")
    print("The SearchNode class provides all required components:")
    print("  ✓ Move that would be taken")
    print("  ✓ State that would be reached")
    print("  ✓ Depth from current state")
    print("  ✓ Evaluation (utility + depth)")
    print("  ✓ Parent reference (for Part B)")

if __name__ == "__main__":
    # Run comprehensive tests
    success = run_search_node_tests()
    
    if success:
        print("\n" + "=" * 60)
        print("All tests passed! Running demonstration...")
        test_search_node_demo()
    
    sys.exit(0 if success else 1)
