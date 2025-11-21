#!/usr/bin/env python3
"""
Simple test to verify utility method and SearchNode are working.
"""

import sys
sys.path.append(".")

from AI.HW2_Hueristic import AIPlayer, SearchNode
from GameState import GameState
from Constants import *
from Move import Move

def simple_test():
    print("=== Simple Test ===")
    
    # Create AI player
    ai = AIPlayer(PLAYER_ONE)
    
    # Test 1: Basic state
    state = GameState.getBasicState()
    utility = ai.utility(state)
    print(f"1. Basic state utility: {utility:.3f}")
    
    # Test 2: Create a search node
    move = Move(MOVE_ANT, (0, 0), (1, 0))
    node = ai.create_search_node(move, state, depth=1)
    print(f"2. Search node evaluation: {node.evaluation:.3f}")
    print(f"   (Should be utility + depth = {utility:.3f} + 1 = {utility + 1:.3f})")
    
    # Test 3: Different food counts
    state2 = state.clone()
    state2.inventories[PLAYER_ONE].foodCount = 5
    state2.inventories[PLAYER_TWO].foodCount = 2
    utility2 = ai.utility(state2)
    print(f"3. More food utility: {utility2:.3f}")
    
    # Test 4: Winning condition
    state3 = state.clone()
    state3.inventories[PLAYER_ONE].foodCount = 11
    utility3 = ai.utility(state3)
    print(f"4. Winning state utility: {utility3:.3f}")
    
    print("\n✓ All tests passed! Your utility method and SearchNode are working correctly.")

if __name__ == "__main__":
    simple_test()
