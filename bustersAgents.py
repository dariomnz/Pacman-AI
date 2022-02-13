from __future__ import print_function
# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from builtins import range
from builtins import object
import time
import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters

class NullGraphics(object):
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs


class BustersAgent(object):
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable
        self.last_score = None
        self.countTicks = 0
        self.last_turn=""


    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True
        
        self.distancer = Distancer(gameState.data.layout, False)

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
            
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        return KeyboardAgent.getAction(self, gameState)

from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys

'''Random PacMan Agent'''
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table
        
    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move
        
class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that has
        not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (according to mazeDistance!).

        To find the mazeDistance between any two positions, use:
          self.distancer.getDistance(pos1, pos2)

        To find the successor position of a position after an action:
          successorPosition = Actions.getSuccessor(position, action)

        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief
        distributions for each of the ghosts that are still alive.  It
        is defined based on (these are implementation details about
        which you need not be concerned):

          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).

          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.
        """
        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]
        return Directions.EAST

class BasicAgentAA(BustersAgent):

    # Este agente no realiza ningun cambio en la q-table, 
    # solo se encarga de ejecutar el pacman de acuerdo a las instrucciones de esta
    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0

        self.actions = {Directions.NORTH:0, Directions.SOUTH:1, Directions.EAST:2, Directions.WEST:3}

        self.q_table = self.readQtable()
        self.epsilon = 0.05 

    def readQtable(self):
        "Read qtable from disc"
        self.table_file = open("qtable.txt", "r+")
        table = self.table_file.readlines()
        q_table = []

        for i, line in enumerate(table):
            row = line.split()
            row = [float(x) for x in row]
            q_table.append(row)

        self.table_file.close()
        return q_table

    # state is a array with 
    # direction_ghost  (norte, sur, este, oeste)
    # distance_ghost  (inmediata, cerca, lejos)
    # direction_pacdot  (norte, sur, este, oeste, none)
    # distance_pacdot (inmediata, cerca, lejos)
    def computePosition(self, state):
        """
        Compute the row of the qtable for a given state.
        """
        return state[0]+state[1]*4+state[2]*12+state[3]*60
    
    def getQValue(self, state, action):

        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        position = self.computePosition(state)
        action_column = self.actions[action]

        return self.q_table[position][action_column]

    def computeValueFromQValues(self, state, gameState):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        legalActions = gameState.getLegalActions(0)
        if len(legalActions)==0:
          return 0
        return max(self.q_table[self.computePosition(state)])
    
    def computeActionFromQValues(self, state, gameState):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        legalActions = gameState.getLegalActions(0)
        if len(legalActions)==0:
          return None
        legalActions.remove(Directions.STOP)
        best_actions = [legalActions[0]]
        best_value = self.getQValue(state, legalActions[0])
        for action in legalActions:
            value = self.getQValue(state, action)
            if value == best_value:
                best_actions.append(action)
            if value > best_value:
                best_actions = [action]
                best_value = value

        return random.choice(best_actions)

    def getActionQtable(self, state, gameState):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
        """

        # Pick Action
        legalActions = gameState.getLegalActions(0)
        legalActions.remove(Directions.STOP)
        action = None

        if len(legalActions) == 0:
             return action

        flip = util.flipCoin(self.epsilon)

        if flip:
            return random.choice(legalActions)
        return self.getPolicy(state, gameState)

    def getPolicy(self, state, gameState):
        "Return the best action in the qtable for a given state"
        return self.computeActionFromQValues(state, gameState)

    def getValue(self, state, gameState):
        "Return the highest q value for a given state"
        return self.computeValueFromQValues(state, gameState)

    def chooseAction(self, gameState):
        # Calcular el state
        # Default action
        self.countActions = self.countActions + 1

        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        pacman_position = gameState.getPacmanPosition()
        ghosts_position = gameState.getGhostPositions()

        num_ghost = 0
        for ghost in  gameState.getLivingGhosts():
            if ghost == True:
                num_ghost += 1
    
        # the target object is a pacdot
        pacdot_position = None
        minDistance = 900000
        pacmanPosition = gameState.getPacmanPosition()
        num_pacdot = 0
        # search the nearest pacdot
        for i in range(gameState.data.layout.width):
            for j in range(gameState.data.layout.height):
                if gameState.hasFood(i, j):
                    num_pacdot +=1
                    foodPosition = i, j
                    distance = self.distancer.getDistance(pacmanPosition, foodPosition)
                    if distance < minDistance:
                        minDistance = distance
                        pacdot_position = foodPosition
        
        object_distances = []

        for ghost_position in ghosts_position:
            object_distances.append(self.distancer.getDistance(pacman_position,ghost_position))

        # Get the min distance in the list
        num_object = None
        index = 0
        final_value = 100000
        for value in object_distances:
            if value and value <= final_value:
                final_value = value
                num_object = index
            index +=1
        near_object_position = ghosts_position[num_object]

        next_distances = {}
        for action in legal:
            next_position = [pacman_position[0],pacman_position[1]]
            if action == Directions.NORTH:
                next_position[1]+=1
                next_distances[Directions.NORTH]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

            elif action == Directions.SOUTH:
                next_position[1]-=1
                next_distances[Directions.SOUTH]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

            elif action == Directions.EAST:
                next_position[0]+=1
                next_distances[Directions.EAST]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

            elif action == Directions.WEST:
                next_position[0]-=1
                next_distances[Directions.WEST]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

        final_direction = None
        min_distance = 100000 
        for _direction, _distance in next_distances.items():
            if _distance < min_distance:
                min_distance = _distance
                final_direction = _direction

        direction_ghost = None
        if final_direction == Directions.NORTH:
            direction_ghost = NORTE
        if final_direction == Directions.SOUTH:
            direction_ghost = SUR
        if final_direction == Directions.EAST:
            direction_ghost = ESTE
        if final_direction == Directions.WEST:
            direction_ghost = OESTE

        # For the ghost distance
        distance_ghost = None
        dis_ghost = object_distances[num_object]
        if object_distances[num_object] == 1:
            distance_ghost = INMEDIATA
        elif object_distances[num_object] == 2:
            distance_ghost = CERCANA
        else:
            distance_ghost = LEJOS


        # For the pacdot direction
        direction_pacdot = None
        if pacdot_position:
            near_object_position = pacdot_position

            next_distances = {}
            for action in legal:
                next_position = [pacman_position[0],pacman_position[1]]
                if action == Directions.NORTH:
                    next_position[1]+=1
                    next_distances[Directions.NORTH]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

                elif action == Directions.SOUTH:
                    next_position[1]-=1
                    next_distances[Directions.SOUTH]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

                elif action == Directions.EAST:
                    next_position[0]+=1
                    next_distances[Directions.EAST]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

                elif action == Directions.WEST:
                    next_position[0]-=1
                    next_distances[Directions.WEST]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

            final_direction = None
            min_distance = 100000 
            for _direction, _distance in next_distances.items():
                if _distance < min_distance:
                    min_distance = _distance
                    final_direction = _direction

            if final_direction == Directions.NORTH:
                direction_pacdot = NORTE
            if final_direction == Directions.SOUTH:
                direction_pacdot = SUR
            if final_direction == Directions.EAST:
                direction_pacdot = ESTE
            if final_direction == Directions.WEST:
                direction_pacdot = OESTE

        else:
            direction_pacdot = NONE

        # Para pacdot distance
        if pacdot_position:
            pacdot_num_distance = self.distancer.getDistance(pacman_position,pacdot_position)
            dis_pacdot = pacdot_num_distance
            distance_pacdot = None
            if pacdot_num_distance == 1:
                distance_pacdot = INMEDIATA
            elif pacdot_num_distance == 2:
                distance_pacdot = CERCANA
            else:
                distance_pacdot = LEJOS
        else:
            distance_pacdot = LEJOS

        state = [direction_ghost,distance_ghost,direction_pacdot,distance_pacdot]
        
        move = self.getActionQtable(state, gameState)
        return move

NORTE = 0
SUR = 1
ESTE = 2
OESTE = 3
NONE = 4
INMEDIATA = 0
CERCANA = 1
LEJOS = 2

class QLearningAgent(BustersAgent):
    
    def __init__(self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True,
    epsilon = 0.05,alpha = 0,discount=0.9,tickLimit=0,entrenamiento=0):
        super().__init__(index, inference, ghostAgents, observeEnable, elapseTimeEnable)
        
        self.epsilon = float(epsilon)   # Cuanto mayor, mayor la probabilidad de coger un valor aleatorio
        self.alpha = float(alpha)      # Ratio de aprendizaje
        self.discount = float(discount)   # factor de discount

        self.tickLimit=float(tickLimit)
        self.entrenamiento = float(entrenamiento)


    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0

        self.actions = {Directions.NORTH:0, Directions.SOUTH:1, Directions.EAST:2, Directions.WEST:3}
        
        self.q_table = self.readQtable()

        self.last_state = None
        self.last_move = None
        
        self.last_num_ghost = None
        self.last_num_pacdot = None


        # state is a array with 
        # direction_ghost  (norte, sur, este, oeste)
        # distance_ghost  (inmediata, cerca, lejos)
        # direction_pacdot  (norte, sur, este, oeste, none)
        # distance_pacdot (inmediata, cerca, lejos)
    
    def readQtable(self):
        "Read qtable from disc"
        self.table_file = open("qtable.txt", "r+")
        table = self.table_file.readlines()
        q_table = []

        for i, line in enumerate(table):
            row = line.split()
            row = [float(x) for x in row]
            q_table.append(row)

        return q_table

    def writeQtable(self):
        "Write qtable to disc"
        self.table_file.seek(0)
        self.table_file.truncate()
        for line in self.q_table:
            for item in line:
                self.table_file.write(str(item)+" ")
            self.table_file.write("\n")
        self.table_file.close()
    
    def __del__(self):
        "Destructor. Invokation at the end of each episode"
        self.writeQtable()

    
    # state is a array with 
    # direction_ghost  (norte, sur, este, oeste)
    # distance_ghost  (inmediata, cerca, lejos)
    # direction_pacdot  (norte, sur, este, oeste, none)
    # distance_pacdot (inmediata, cerca, lejos)
    def computePosition(self, state):
        """
        Compute the row of the qtable for a given state.
        """
        return state[0]+state[1]*4+state[2]*12+state[3]*60
    
    def getQValue(self, state, action):

        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        position = self.computePosition(state)
        action_column = self.actions[action]

        return self.q_table[position][action_column]

    def computeValueFromQValues(self, state, gameState):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        legalActions = gameState.getLegalActions(0)
        if len(legalActions)==0:
          return 0
        return max(self.q_table[self.computePosition(state)])
    
    def computeActionFromQValues(self, state, gameState):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        legalActions = gameState.getLegalActions(0)
        if len(legalActions)==0:
          return None
        legalActions.remove(Directions.STOP)
        best_actions = [legalActions[0]]
        best_value = self.getQValue(state, legalActions[0])
        for action in legalActions:
            value = self.getQValue(state, action)
            if value == best_value:
                best_actions.append(action)
            if value > best_value:
                best_actions = [action]
                best_value = value

        return random.choice(best_actions)

    def getActionQtable(self, state, gameState):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
        """
        # Pick Action
        legalActions = gameState.getLegalActions(0)
        legalActions.remove(Directions.STOP)
        action = None

        if len(legalActions) == 0:
             return action

        flip = util.flipCoin(self.epsilon)

        if flip:
            return random.choice(legalActions)
        return self.getPolicy(state, gameState)

    def update(self, state, action, nextState, reward,gameState):
        """
        The parent class calls this to observe a
        state = action => nextState and reward transition.
        You should do your Q-Value update here

        Good Terminal state -> reward 1
        Bad Terminal state -> reward -1
        Otherwise -> reward 0

        Q-Learning update:

        if terminal_state:
        Q(state,action) <- (1-self.alpha) Q(state,action) + self.alpha * (r + 0)
        else:
        Q(state,action) <- (1-self.alpha) Q(state,action) + self.alpha * (r + self.discount * max a' Q(nextState, a'))

        """
        # TRACE for transition and position to update. Comment the following lines if you do not want to see that trace
        if self.entrenamiento == 0:
            print("Update Q-table with transition: ", state, action, nextState, reward)
        position = self.computePosition(state)
        action_column = self.actions[action]
    
        if self.entrenamiento == 0:
            print("Corresponding Q-table cell to update:", position, action_column)
        position = self.computePosition(state)
        
        
        "*** YOUR CODE HERE ***"
        self.q_table[position][action_column] = (1-self.alpha) * self.getQValue(state,action) + self.alpha * (reward + self.discount * self.computeValueFromQValues(nextState,gameState))
        # TRACE for updated q-table. Comment the following lines if you do not want to see that trace
        # print("Q-table:")
        # self.printQtable()

    def getPolicy(self, state, gameState):
        "Return the best action in the qtable for a given state"
        return self.computeActionFromQValues(state, gameState)

    def getValue(self, state, gameState):
        "Return the highest q value for a given state"
        return self.computeValueFromQValues(state, gameState)

    def chooseAction(self, gameState):
        # Si tarda mucho termina
        self.countActions = self.countActions + 1
        if self.tickLimit != 0 and self.countActions > self.tickLimit:
            quit()

        # Calcular el state
         # Default action
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        pacman_position = gameState.getPacmanPosition()
        ghosts_position = gameState.getGhostPositions()

        num_ghost = 0
        for ghost in  gameState.getLivingGhosts():
            if ghost == True:
                num_ghost += 1
    
        # the target object is a pacdot
        pacdot_position = None
        minDistance = 900000
        pacmanPosition = gameState.getPacmanPosition()
        num_pacdot = 0
        # search the nearest pacdot
        for i in range(gameState.data.layout.width):
            for j in range(gameState.data.layout.height):
                if gameState.hasFood(i, j):
                    num_pacdot +=1
                    foodPosition = i, j
                    distance = self.distancer.getDistance(pacmanPosition, foodPosition)
                    if distance < minDistance:
                        minDistance = distance
                        pacdot_position = foodPosition
        
        object_distances = []

        for ghost_position in ghosts_position:
            object_distances.append(self.distancer.getDistance(pacman_position,ghost_position))

        # Get the min distance in the list
        num_object = None
        index = 0
        final_value = 100000
        for value in object_distances:
            if value and value <= final_value:
                final_value = value
                num_object = index
            index +=1
        near_object_position = ghosts_position[num_object]

        next_distances = {}
        for action in legal:
            next_position = [pacman_position[0],pacman_position[1]]
            if action == Directions.NORTH:
                next_position[1]+=1
                next_distances[Directions.NORTH]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

            elif action == Directions.SOUTH:
                next_position[1]-=1
                next_distances[Directions.SOUTH]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

            elif action == Directions.EAST:
                next_position[0]+=1
                next_distances[Directions.EAST]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

            elif action == Directions.WEST:
                next_position[0]-=1
                next_distances[Directions.WEST]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

        final_direction = None
        min_distance = 100000 
        for _direction, _distance in next_distances.items():
            if _distance < min_distance:
                min_distance = _distance
                final_direction = _direction

        direction_ghost = None
        if final_direction == Directions.NORTH:
            direction_ghost = NORTE
        if final_direction == Directions.SOUTH:
            direction_ghost = SUR
        if final_direction == Directions.EAST:
            direction_ghost = ESTE
        if final_direction == Directions.WEST:
            direction_ghost = OESTE

        # For the ghost distance
        distance_ghost = None
        dis_ghost = object_distances[num_object]
        if object_distances[num_object] == 1:
            distance_ghost = INMEDIATA
        elif object_distances[num_object] == 2:
            distance_ghost = CERCANA
        else:
            distance_ghost = LEJOS


        # For the pacdot direction
        
        direction_pacdot = None
        if pacdot_position:
            near_object_position = pacdot_position

            next_distances = {}
            for action in legal:
                next_position = [pacman_position[0],pacman_position[1]]
                if action == Directions.NORTH:
                    next_position[1]+=1
                    next_distances[Directions.NORTH]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

                elif action == Directions.SOUTH:
                    next_position[1]-=1
                    next_distances[Directions.SOUTH]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

                elif action == Directions.EAST:
                    next_position[0]+=1
                    next_distances[Directions.EAST]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

                elif action == Directions.WEST:
                    next_position[0]-=1
                    next_distances[Directions.WEST]=self.distancer.getDistance(tuple(next_position),tuple(near_object_position))

            final_direction = None
            min_distance = 100000 
            for _direction, _distance in next_distances.items():
                if _distance < min_distance:
                    min_distance = _distance
                    final_direction = _direction

            if final_direction == Directions.NORTH:
                direction_pacdot = NORTE
            if final_direction == Directions.SOUTH:
                direction_pacdot = SUR
            if final_direction == Directions.EAST:
                direction_pacdot = ESTE
            if final_direction == Directions.WEST:
                direction_pacdot = OESTE

        else:
            direction_pacdot = NONE

        # Para pacdot distance
        if pacdot_position:
            pacdot_num_distance = self.distancer.getDistance(pacman_position,pacdot_position)
            dis_pacdot = pacdot_num_distance
            distance_pacdot = None
            if pacdot_num_distance == 1:
                distance_pacdot = INMEDIATA
            elif pacdot_num_distance == 2:
                distance_pacdot = CERCANA
            else:
                distance_pacdot = LEJOS
        else:
            distance_pacdot = LEJOS


        state = [direction_ghost,distance_ghost,direction_pacdot,distance_pacdot]
        
        move = self.getActionQtable(state, gameState)

        if self.last_state != None and self.last_move != None:
            # Calcular la recompensa
            reward = 0
            if self.last_num_ghost > num_ghost:
                # Cuando se come un fantasma
                reward += 50
            
            if self.last_num_pacdot > num_pacdot:
                # Cuando se come un pacdot
                reward += 100


            # state is a array with 
            # direction_ghost  (norte, sur, este, oeste)
            # distance_ghost  (inmediata, cerca, lejos)
            # direction_pacdot  (norte, sur, este, oeste, none)
            # distance_pacdot (inmediata, cerca, lejos)
            self.update(self.last_state,self.last_move,state,reward,gameState)
            # self.writeQtable()
        self.last_state = state
        self.last_move = move
        self.last_num_ghost = num_ghost
        self.last_num_pacdot = num_pacdot

        return move

