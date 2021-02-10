# TODO: if you can't move to a square that decreases cost because that neighbor wants that goal.
#  Try: if there is a square you can move to which decreases your cost, then pick that cost instead of random
#  Try: if the candidate goal is your goal, repick a candidate goal. Broadcast out a different candidate goal if you are at your goal already to 
#  neighbors
#  Try: if there's a candidate goal with 0 hops, go to it
# TODO: Fix the repicker to propagate to neighbors as well; all neighbors should be picking a random once the hole is filled
import numpy as np

def padHash(num, zeros):
    num = str(num)
    pad = zeros - len(num)
    return '0' * pad + num


def rand():
    return np.random.rand()


def cost(pos, goal):
    return np.abs(goal[0] - pos[0]) + np.abs(goal[1] - pos[1])


def priority(posA, posB):
    aX = posA[0]
    aY = posA[1]
    bX = posB[0]
    bY = posB[1]

    if aX == bX:
        return True if aY > bY else False
    return True if aX > bX else False

class Node():
    def __init__(self, parent=None, pos=None, g=0, h=0):
        self.parent = parent
        self.pos = pos
        self.g = g
        self.h = h
        self.f = self.g+self.h

    def __eq__(self, other):
        return self.pos == other.pos


class Agent():
    def __init__(self, loc, simSize, idNum, zeros, swarmMap, allGoals, mapSize, swapGoalProb, randCandProb):
        self.x = loc[0]
        self.y = loc[1]
        self.simSize = simSize
        self.mapSize= mapSize
        self.id = idNum
        self.nx = None
        self.ny = None
        self.hop = 20000 # ideally should be infinite
        self.fontSize = 12
        self.freq = 10 # 10 hz
        # self.neighborGoals = []
        self.numZeros = zeros
        self.map = swarmMap
        self.nextStep = None
        self.allGoals = allGoals
        self.goal = self.allGoals[np.random.choice(len(self.allGoals))]
        self.candidate = self.allGoals[np.random.choice(len(self.allGoals))]
        self.swapProb = swapGoalProb
        self.randProb = randCandProb
        print(self.goal)
        print(self.candidate)
        print(self.x)
        print(self.y)

    #TODO: Fix A* to not have the dumb bug where it can't move around something. 
    def astar(self, through=False, oid=0):
        # print(cost(self.goal, self.pos()))
        openList = [Node(None, self.pos(), 0, cost(self.goal, self.pos()))]
        closedList = []

        endNode = Node(None, self.goal)
        curNode = openList[0]
        # print("startf", curNode.f)
        curInd = 0

        if self.pos() == self.goal:
            return [curNode.pos]

        while len(openList) > 0:
            curNode.f = 1000000
            for index, node in enumerate(openList):
                if node.f < curNode.f:
                    curNode = node
                    curInd = index
                # print("Olist", node.pos)

            openList.pop(curInd)
            closedList.append(curNode)

            if curNode == endNode:
                path = []
                curStep = curNode
                while curStep is not None:
                    path.append(curStep.pos)
                    curStep = curStep.parent
                return path[::-1]

            neighbors = self.get_neighbors(curNode.pos)
            # print(neighbors)
            print('curnode', curNode.pos)
            print("Endat", endNode.pos)

            for node in neighbors:
                skip = False
                
                checkNode = self.lookup_agent(node)
                if not through:
                    if checkNode is not None:
                        continue
                else:
                    if checkNode is not None and checkNode.id != oid:
                        continue

                # print("node", node)

                newNode = Node(curNode, node, curNode.g+1, cost(node, self.goal))

                for oNode in openList:
                    if newNode == oNode and oNode.f < newNode.f:
                        skip = True

                for cNode in closedList:
                    if newNode == cNode and cNode.f <= newNode.f:
                        skip = True
                
                if not skip:
                    openList.append(newNode)

            closedList.append(curNode)
            input('step')


    def astar_cost(self, through=None, oid=0):
        goalPath = self.astar(through, oid)
        return len(goalPath) - 1

    def swap_goals(self, other):
        tmpGoal = self.goal
        self.goal = other.goal
        other.goal = tmpGoal


    def get_neighbors(self, pos=None):
        if pos is None:
            a = self.x
            b = self.y
        else:
            a = pos[0]
            b = pos[1]
        neighbors = np.random.permutation([(a, b+1), (a, b-1), (a+1, b), (a-1, b)])
        i = 0 
        goodNeighbors = []
        for x, y in neighbors:
            if x >= 0 and x < self.mapSize and y >= 0 and y < self.mapSize:
                goodNeighbors.append((x, y))
            i += 1

        return goodNeighbors


    def cmp(self, other):
        if self.x == other[0]:
            return True if self.y > other[1] else False
        return True if self.x > other[0] else False

    def isEq(self, other):
        return self.id == other.id


    def setMap(self, map):
        self.map = map

    def pos(self):
        return (self.x, self.y)


    def setPos(self):
        self.x = self.nextStep[0]
        self.y = self.nextStep[1]


    def goal(self):
        return self.goal


    def setGoal(self, newGoal):
        self.goal = newGoal

    def message(self):
        taken = False
        if self.candidate == self.goal and self.pos() == self.goal:
            self.candidate = self.allGoals[np.random.choice(len(self.allGoals))]
            self.hop = 1000000
            taken = True

        return (self.pos(), self.nextStep, self.goal, self.candidate, self.hop, taken)

    def lookup_agent(self, n):
        swarmDict = self.map.getDict()
        hashkey = padHash(n[0], self.numZeros) + padHash(n[1], self.numZeros)
        if hashkey in swarmDict:
            # print('Hash', hashkey)
            return swarmDict[hashkey]
        return None


    def broadcast_and_collect(self, neighbors):
        swarmDict = self.map.getDict()
        
        for n in neighbors:
            hashkey = padHash(n[0], self.numZeros) + padHash(n[1], self.numZeros)
            if hashkey in swarmDict:
                neigh = swarmDict[hashkey]
                if neigh.goal == self.goal:
                    return True, neigh

        return False, None


    def new_goal_selector(self, msgs, neighbors):
        # if we share a goal, then randomly break the tie by usually choosing our candidate goal
        for msg in msgs:
            if self.goal == msg[2]:
                if not self.cmp(msg[0]):
                    if rand() > self.randProb:
                        self.goal = self.candidate
                    else:
                        self.goal = self.allGoals[np.random.choice(len(self.allGoals))]
                # print('same Goal')
           # print('Msg', msg)

            nAgent = self.lookup_agent(msg[0])
            if nAgent is None:
                continue

            # compares the costs of the swapped and non-swapped configs, and swaps if necessary
            # nowCost = self.astar_cost() + nAgent.astar_cost()
            # print('nowCost', nowCost)
            # self.swap_goals(nAgent)
            
            #  # cost(self.pos(), self.goal) + cost(msg[0], msg[2])
            # swapCost = self.astar_cost(True, nAgent.id) + nAgent.astar_cost(True, self.id)

            # print('swapCost', swapCost)
            

            # if swapCost >= nowCost:
            #     self.swap_goals(nAgent)
            #     print("no swap")

            nowCost = cost(self.pos(), self.goal) + cost(nAgent.pos(), nAgent.goal)
            swapCost = cost(self.pos(), nAgent.goal) + cost(nAgent.pos(), self.goal)

            if swapCost < nowCost:
                self.swap_goals(nAgent)
            elif swapCost == nowCost:
                if rand() <= self.swapProb:
                    self.swap_goals(nAgent)


    def receive_msgs(self, neighbors):
        swarmDict = self.map.getDict()
        # randomly selects an order of people to broadcast to
        msgs = []
        for n in neighbors:
            hashkey = padHash(n[0], self.numZeros) + padHash(n[1], self.numZeros)
            if hashkey in swarmDict:
                msgs.append(swarmDict[hashkey].message())
        return msgs

    # if you are at a goal and waiting, you want to prioritize your candidate first
    def motion_planner(self, neighbors, msgs):
        wait = False

        # TODO: replace with A*
        for n in neighbors:
            # print(n)
            if cost(n, self.goal) < cost(self.pos(), self.goal):
                self.nextStep = n

        if len(msgs) > 0:
            minHop = 1000000
            msgGoals = []
            repick = False
            minMsg = None
            for msg in msgs:
                if msg[4] < minHop:
                    minHop = msg[4]
                    minMsg = msg
                    repick = msg[5]
                    diff = True
                msgGoals.append(msg[2])
                
                # if an agent is at our waypoint is occupied
                if self.nextStep == msg[0]:
                    wait = True
                    # print('wait')
                elif self.nextStep == msg[1] and not priority(self.pos(), msg[0]):
                    wait = True
                    # print('wait')
                elif self.goal == self.pos():
                    wait = True

            
            if minMsg is not None:
                self.hop = minHop + 1
                self.candidate = minMsg[3]

        for n in neighbors:
            if n in self.allGoals and self.lookup_agent(n) is None:
                self.candidate = n 
                self.hop = 0
                break

        if self.pos() == self.goal:
            return 1

        if not wait:
            self.setPos()

        if repick: # put repick 
            self.hop = 1000000
            self.candidate = self.allGoals[np.random.choice(len(self.allGoals))]
            
            

        return 0


    def step(self):
        # randomly selects an order of people to broadcast to
        neighbors = self.get_neighbors()
        # save one copy of the swarm map at the start of the loop
        
        # check adjacent tiles for messages
        msgs = self.receive_msgs(neighbors)

        if len(msgs) > 0:
            # TODO: changes the checkAgents to be the agents instead of the goals. that way we can set the goals for the swap
            # TODO: for a small number, color coding will help explain it better 
            self.new_goal_selector(msgs, neighbors)

        return self.motion_planner(neighbors, msgs)






        


