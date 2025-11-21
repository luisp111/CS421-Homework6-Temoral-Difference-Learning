# -*- coding: latin-1 -*-
import random
import sys
sys.path.append("..")  # so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *


##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "Booger")
        # The coordinates of the agent's food and tunnel will be stored in these
        # variables (see getMove() below)
        self.myFood = None
        self.myTunnel = None
    
    ##
    #getPlacement 
    #
    # The agent uses a hardcoded arrangement for phase 1 to provide maximum
    # protection to the queen.  Enemy food is placed randomly.
    #
    def getPlacement(self, currentState):
        self.myFood = None
        self.myTunnel = None
        if currentState.phase == SETUP_PHASE_1:
            return [(0,0), (5, 1), 
                    (0,3), (1,2), (2,1), (3,0), \
                    (0,2), (1,1), (2,0), \
                    (0,1), (1,0) ];
        elif currentState.phase == SETUP_PHASE_2:
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:            
            return None  #should never happen
    
    ##
    #getMove
    #
    # This agent simply gathers food as fast as it can with its worker.  It
    # never attacks and never builds more ants.  The queen is never moved.
    #
    ##
    def getMove(self, currentState):
        #asciiPrintState(currentState)
        #Useful pointers
        myInv = getCurrPlayerInventory(currentState)
        me = currentState.whoseTurn

        # The first time this method is called, the food and tunnel locations
        # need to be recorded in their respective instance variables
        if self.myTunnel is None:
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        if self.myFood is None:
            foods = getConstrList(currentState, None, (FOOD,))
            self.myFood = foods[0]
            # Find the food closest to the tunnel
            best_dist_so_far = 1000  # i.e., infinity
            for food in foods:
                dist = stepsToReach(currentState, self.myTunnel.coords, food.coords)
                if dist < best_dist_so_far:
                    self.myFood = food
                    best_dist_so_far = dist

        # If I don't have a worker, give up. QQ
        num_ants = len(myInv.ants)
        if num_ants == 1:
            return Move(END, None, None)

        # If the worker has already moved, we're done
        worker_list = getAntList(currentState, me, (WORKER,))
        if len(worker_list) < 1:
            return Move(END, None, None)
        else:
            my_worker = worker_list[0]
            if my_worker.hasMoved:
                return Move(END, None, None)

        # If the queen is on the anthill move her
        my_queen = myInv.getQueen()
        if my_queen.coords == myInv.getAnthill().coords:
            return Move(MOVE_ANT, [myInv.getQueen().coords, (1, 0)], None)

        # If the queen hasn't moved, have her move in place so she will attack
        if not my_queen.hasMoved:
            return Move(MOVE_ANT, [my_queen.coords], None)

        # If I have the food and the anthill is unoccupied then make a drone
        if myInv.foodCount > 2:
            if getAntAt(currentState, myInv.getAnthill().coords) is None:
                return Move(BUILD, [myInv.getAnthill().coords], DRONE)

        # Move all my drones towards the enemy
        my_drones = getAntList(currentState, me, (DRONE,))
        for drone in my_drones:
            if not drone.hasMoved:
                drone_x = drone.coords[0]
                drone_y = drone.coords[1]
                if drone_y < 9:
                    drone_y += 1
                else:
                    drone_x += 1
                if (drone_x, drone_y) in listReachableAdjacent(currentState, drone.coords, 3):
                    return Move(MOVE_ANT, [drone.coords, (drone_x, drone_y)], None)
                else:
                    return Move(MOVE_ANT, [drone.coords], None)
                    
        # If the worker has food, move toward tunnel
        if my_worker.carrying:
            path = createPathToward(currentState, my_worker.coords,
                                    self.myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
            return Move(MOVE_ANT, path, None)
            
        # If the worker has no food, move toward food
        else:
            path = createPathToward(currentState, my_worker.coords,
                                    self.myFood.coords, UNIT_STATS[WORKER][MOVEMENT])
            return Move(MOVE_ANT, path, None)
                              
    
    ##
    #getAttack
    #
    # This agent never attacks
    #
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[0]  # don't care
        
    ##
    # registerWin
    #
    # This agent doesn't learn
    #
    def registerWin(self, hasWon):
        # method template, not implemented
        pass
