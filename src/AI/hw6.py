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
        self.gamma = 0.9 # discount factor
        self.epsilon = 0.3  # exploration rate
        
        # State utilities dictionary
        self.state_utilities = {}
        
        # Track last visited state for online TD updates
        self.last_state_category = None
        self.last_reward = None
        
        # Filename for saving/loading weights (path relative to project src directory)
        # This makes it independent of the current working directory.
        self.weights_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "weights.txt")
        
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
        
        # Feature 5: my queen alive
        has_queen = any(ant.type == QUEEN for ant in my_inv.ants)
        
        # Feature 6: enemy queen alive
        enemy_has_queen = any(ant.type == QUEEN for ant in enemy_inv.ants)
        
        # Feature 7: number of my workers
        num_workers = len([ant for ant in my_inv.ants if ant.type == WORKER])
        worker_bucket = min(num_workers, 3)
        
        # Feature 8: is any worker carrying food
        worker_carrying = any(ant.carrying for ant in my_inv.ants if ant.type == WORKER)
        
        # Feature 9: food advantage bucket (bounded difference)
        food_advantage = max(min(my_food - enemy_food, 5), -5)
        
        # Feature 10: enemy threat near my queen (bool)
        my_queen = my_inv.getQueen()
        enemy_threat = False
        if my_queen is not None:
            for ant in enemy_inv.ants:
                if approxDist(ant.coords, my_queen.coords) <= 2:
                    enemy_threat = True
                    break
        
        # Return tuple
        category = (
            food_bucket,
            ant_bucket,
            enemy_food_bucket,
            enemy_ant_bucket,
            has_queen,
            enemy_has_queen,
            worker_bucket,
            worker_carrying,
            food_advantage,
            enemy_threat
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
        #Shaping reward that encourages food collection, keeping workers alive,
        #and protecting the queen. Terminal rewards are handled separately at
        #the end of the game using the hasWon flag.
    
        winner = getWinner(currentState)
        if winner == self.playerId:
            return 1.0
        if winner == 1 - self.playerId:
            return -1.0
        
        me = self.playerId
        enemy = 1 - me
        my_inv = currentState.inventories[me]
        enemy_inv = currentState.inventories[enemy]
        
        reward = -0.01  # baseline time penalty
        
        # Reward holding a food advantage
        food_advantage = my_inv.foodCount - enemy_inv.foodCount
        reward += 0.02 * food_advantage
        
        # Encourage building/maintaining workers and carrying food
        workers = [ant for ant in my_inv.ants if ant.type == WORKER]
        if not workers:
            reward -= 0.05
        if any(worker.carrying for worker in workers):
            reward += 0.05
        
        # Penalize letting the enemy threaten our queen
        my_queen = my_inv.getQueen()
        if my_queen is not None:
            if any(approxDist(ant.coords, my_queen.coords) <= 1 for ant in enemy_inv.ants):
                reward -= 0.1
        
        return reward


    def _apply_td_update(self, next_state_category):
        #Perform a TD(0) update using the last recorded state/reward and the
        #estimated value of the next state.
        if self.last_state_category is None or self.last_reward is None:
            return
        
        current_utility = self.get_utility(self.last_state_category)
        next_utility = self.get_utility(next_state_category)
        td_target = self.last_reward + self.gamma * next_utility
        td_error = td_target - current_utility
        new_utility = current_utility + self.alpha * td_error
        self.update_utility(self.last_state_category, new_utility)
    
    
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
        
        # Update previous state's utility estimate with the new information
        self._apply_td_update(current_category)
        
        # Remember this state for the next update
        self.last_state_category = current_category
        self.last_reward = current_reward
        
        # Epsilon-greedy exploration
        if random.random() < self.epsilon:
            # Explore: random move
            selected_move = moves[random.randint(0, len(moves) - 1)]
        else:
            # Exploit: choose move leading to highest utility state
            best_move = None
            best_utility = float('-inf')
            
            for move in moves:
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
        if numAnts >= 3:
            # Prefer non-build moves when we already have enough ants
            non_build_moves = [m for m in moves if m.moveType != BUILD]
            if non_build_moves:
                selected_move = random.choice(non_build_moves)
        
        return selected_move
    
    
    def predict_state(self, currentState, move):
        """
        Predict the next state resulting from taking the given move.
        Uses the helper from AIPlayerUtils which returns a fast-cloned
        next state with updated inventories.
        """
        return getNextState(currentState, move)
    
    
    ## Attack Selection
    # Attack a random enemy
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]
    
    
    ## TD Learning Update at End of Game
    def registerWin(self, hasWon):
        #Called at end of game. Apply the final TD update with the terminal
        #reward and persist learned utilities.
        print(f"Game ended. Result: {'WIN' if hasWon else 'LOSS'}")
        
        final_reward = 1.0 if hasWon else -1.0
        
        if self.last_state_category is not None:
            total_reward = (self.last_reward if self.last_reward is not None else 0.0) + final_reward
            current_utility = self.get_utility(self.last_state_category)
            td_error = total_reward - current_utility
            new_utility = current_utility + self.alpha * td_error
            self.update_utility(self.last_state_category, new_utility)
        
        # Save utilities after each game
        self.save_utilities()
        
        # Reset TD tracking for next game
        self.last_state_category = None
        self.last_reward = None
        
        print(f"Total states learned: {len(self.state_utilities)}")