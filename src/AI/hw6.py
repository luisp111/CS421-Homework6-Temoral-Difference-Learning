import random
import sys
import json
import os
sys.path.append("..")
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *


class AIPlayer(Player):
    
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "TD_Learner")
        
        # TD Learning parameters
        self.alpha = 0.1  # learning rate
        self.gamma = 0.9  # discount factor
        self.epsilon = 0.1  # exploration rate
        
        # State utilities dictionary
        self.state_utilities = {}
        
        # Episode history for TD updates
        self.episode_history = []  # list of (state_category, reward) tuples
        
        # Filename for saving/loading weights
        self.weights_file = "./weights.txt"
        
        # Load existing utilities if file exists
        self.load_utilities()
    
    
    ## State Categorization
    def categorize_state(self, currentState):
        me = currentState.whoseTurn
        enemy = 1 - me
        
        # Get inventories
        my_inv = currentState.inventories[me]
        enemy_inv = currentState.inventories[enemy]
        
        # Feature 1 food count
        my_food = my_inv.foodCount
        food_bucket = min(my_food // 2, 5)  # 0-2, 3-4, 5-6, 7-8, 9-10, 11+
        
        # Feature 2 number of my ants
        num_my_ants = len(my_inv.ants)
        ant_bucket = min(num_my_ants // 2, 4)  # 0-1, 2-3, 4-5, 6-7, 8+
        
        # Feature 3 enemy food count 
        enemy_food = enemy_inv.foodCount
        enemy_food_bucket = min(enemy_food // 2, 5)
        
        # Feature 4 number of enemy ants 
        num_enemy_ants = len(enemy_inv.ants)
        enemy_ant_bucket = min(num_enemy_ants // 2, 4)
        
        # Feature 5
        has_queen = any(ant.type == QUEEN for ant in my_inv.ants)
        
        # Feature 6
        enemy_has_queen = any(ant.type == QUEEN for ant in enemy_inv.ants)
        
        # Return tuple
        category = (
            food_bucket,
            ant_bucket,
            enemy_food_bucket,
            enemy_ant_bucket,
            has_queen,
            enemy_has_queen
        )
        
        return category
    
    
    ## Utility Management
    def get_utility(self, state_category):
        if state_category not in self.state_utilities:
            self.state_utilities[state_category] = 0.0  # initial utility
        return self.state_utilities[state_category]
    
    
    def update_utility(self, state_category, new_utility):
        self.state_utilities[state_category] = new_utility
    
    
    ## Reward Function
    def get_reward(self, currentState):
        winner = getWinner(currentState)
        
        if winner == self.playerId:
            return 1.0  # Win
        elif winner == 1 - self.playerId:
            return -1.0  # Loss
        else:
            return -0.01  # Small penalty for each turn
    
    
    ## Save/Load Utilities
    def save_utilities(self):
        """Save state utilities to file."""
        try:
            # Convert tuple keys to strings for JSON serialization
            serializable_utilities = {str(k): v for k, v in self.state_utilities.items()}
            with open(self.weights_file, 'w') as f:
                json.dump(serializable_utilities, f)
            print(f"Saved {len(self.state_utilities)} state utilities to {self.weights_file}")
        except Exception as e:
            print(f"Error saving utilities: {e}")
    
    
    def load_utilities(self):
        """Load state utilities from file if it exists."""
        if os.path.exists(self.weights_file):
            try:
                with open(self.weights_file, 'r') as f:
                    loaded = json.load(f)
                # Convert string keys back to tuples
                self.state_utilities = {eval(k): v for k, v in loaded.items()}
                print(f"Loaded {len(self.state_utilities)} state utilities from {self.weights_file}")
            except Exception as e:
                print(f"Error loading utilities: {e}")
                self.state_utilities = {}
        else:
            print(f"No weights file found. Starting with fresh utilities.")
            self.state_utilities = {}
    
    
    ## Placement
    def getPlacement(self, currentState):
        numToPlace = 0
        if currentState.phase == SETUP_PHASE_1:
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    x = random.randint(0, 9)
                    y = random.randint(0, 3)
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    x = random.randint(0, 9)
                    y = random.randint(6, 9)
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]
    
    
    ## Move Selection with TD Learning
    # Move using epsilon-greedy strategy
    def getMove(self, currentState):
        moves = listAllLegalMoves(currentState)
        
        # Get current state category and record it
        current_category = self.categorize_state(currentState)
        current_reward = self.get_reward(currentState)
        self.episode_history.append((current_category, current_reward))
        
        # Epsilon-greedy exploration
        if random.random() < self.epsilon:
            # Explore: random move
            selected_move = moves[random.randint(0, len(moves) - 1)]
        else:
            # Exploit: choose move leading to highest utility state
            best_move = None
            best_utility = float('-inf')
            
            for move in moves:
                # Predict next state (you may need to implement this)
                # For now, we'll use a simplified approach
                next_state = self.predict_state(currentState, move)
                next_category = self.categorize_state(next_state)
                next_utility = self.get_utility(next_category)
                
                # Track best move
                if next_utility > best_utility:
                    best_utility = next_utility
                    best_move = move
                elif next_utility == best_utility and random.random() < 0.5:
                    # Break ties randomly
                    best_move = move
            
            selected_move = best_move if best_move else moves[0]
        
        # Don't build if we have 3+ ants (simple heuristic)
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        while Move.moveType == BUILD and numAnts >= 3 and len(moves) > 1:
            selected_move = moves[random.randint(0, len(moves) - 1)]
        
        return selected_move
    
    
    def predict_state(self, currentState, move):
        return currentState
    
    
    ## Attack Selection
    # Attack a random enemy
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]
    
    
    ## TD Learning Update at End of Game
    def registerWin(self, hasWon):
        """
        Called at end of game. Update utilities using TD learning.
        """
        print(f"Game ended. Result: {'WIN' if hasWon else 'LOSS'}")
        
        # Perform TD updates backward through episode
        for i in range(len(self.episode_history) - 1):
            state_cat, reward = self.episode_history[i]
            next_state_cat, next_reward = self.episode_history[i + 1]
            
            # TD Update: U(s) = U(s) + α[R + γ*U(s') - U(s)]
            current_utility = self.get_utility(state_cat)
            next_utility = self.get_utility(next_state_cat)
            
            td_target = reward + self.gamma * next_utility
            td_error = td_target - current_utility
            new_utility = current_utility + self.alpha * td_error
            
            self.update_utility(state_cat, new_utility)
        
        # Handle final state (terminal state has no next state)
        if self.episode_history:
            final_state_cat, final_reward = self.episode_history[-1]
            current_utility = self.get_utility(final_state_cat)
            new_utility = current_utility + self.alpha * (final_reward - current_utility)
            self.update_utility(final_state_cat, new_utility)
        
        # Save utilities after each game
        self.save_utilities()
        
        # Clear episode history for next game
        self.episode_history = []
        
        print(f"Total states learned: {len(self.state_utilities)}")