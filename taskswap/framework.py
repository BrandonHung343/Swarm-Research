import pygame 
import numpy as np
import time
import argparse
from agent import *
# sample board: 8x8 board, for letters. 9 agents to populate. First letter is C, then M, then U.
# Ideas: get to the end faster by having the ones near an unassigned goal not change their candidates, 
# since they know for sure it's a good candidate goal since it's unassigned. that will let the propagation 
# of the candidate flow through faster. add a verification bit at the end to make sure it doesn't switch

# Bigger idea: letting chain information flow, if you have the ability to repeat messages along a chain should we propagate them to make clustered decisions

class SwarmMap():
    def __init__(self, numZeros, agentList):
        self.zeros = numZeros
        self.map = track_agents(agentList, numZeros)

    def getDict(self):
        return self.map

    def setDict(self, newDict):
        self.map = newDict



class Sim(pygame.sprite.Sprite):
    def __init__(self, sizeX, sizeY, goals, numAgents):
        pygame.sprite.Sprite.__init__(self)
        self.map = np.zeros(sizeX * sizeY)
        self.xDim = sizeX
        self.yDim = sizeY
        self.size = sizeX * sizeY
        self.agentList = []
        self.cellSize = 50
        self.numZeros = int(np.sqrt(numAgents) / 10) + 1
        # assign goals at random. should be the same as numAgents
        self.assignments = np.random.permutation(goals)
        allLocs = []
        for i in range(sizeX):
            for j in range(sizeY):
                allLocs.append((i, j))
        allLocs = np.random.permutation(allLocs)

        

        # initialize the agents
        for i in range(numAgents):
            A = Agent(loc=allLocs[i], simSize=int(self.cellSize/2), 
                      idNum=i, zeros=self.numZeros, swarmMap=None, allGoals=goals, mapSize=self.xDim, swapGoalProb=0.35, randCandProb=0.05)
            self.agentList.append(A)

        self.swarmMap = SwarmMap(self.numZeros, self.agentList)

        # use the new swarm map to update the agents
        for agent in self.agentList:
            agent.setMap(self.swarmMap)

        sMap = self.swarmMap.getDict()



def track_agents(agentList, zeros):
    newDict = {}
    for agent in agentList:
        x = agent.x
        y = agent.y
        entry = padHash(x, zeros) + padHash(y, zeros)
        newDict[entry] = agent
    return newDict


def render_text(intext, font, canvas, xloc, yloc):
    text = font.render(str(intext), True, (0, 0, 0))
    canvas.blit(text, (xloc, yloc))
    return canvas

def agent_coordinates(agent):
    return int((2*agent.x + 1) * agent.simSize), int((2*agent.y + 1) * agent.simSize)


def render_agents(agentList, canvas):
    for agent in agentList:
        agentX, agentY = agent_coordinates(agent)
        pygame.draw.circle(canvas, (255, 0, 0), (agentX, agentY), agent.simSize-2)
        font = pygame.font.Font(None, agent.fontSize)
        canvas = render_text(agent.goal, font, canvas, agentX-agent.simSize+agent.fontSize//2, agentY-agent.fontSize//2)
        canvas = render_text(agent.id, font, canvas, agentX, agentY-agent.fontSize//2)
        canvas = render_text(agent.candidate, font, canvas, agentX+agent.simSize//2-agent.fontSize//2, agentY-agent.fontSize//2)
    return canvas


def render_all(canvas, sim, screen):
    canvas.fill((255, 255, 255))
    cSize = sim.cellSize
    xStart = 0
    xEnd = cSize * sim.xDim
    for row in range(sim.yDim):
        pygame.draw.line(canvas, (0, 0, 0), (xStart, row * cSize), (xEnd, row * cSize), 3)
    yStart = 0
    yEnd = cSize * sim.yDim
    for col in range(sim.xDim):
        pygame.draw.line(canvas, (0, 0, 0), (col * cSize, yStart), (col * cSize, yEnd), 3)
        # print('sup')
    

    canvas = render_agents(sim.agentList, canvas)
    # drawer.draw(canvas)
    screen.blit(canvas, [0, 0])
    pygame.display.flip()

def main():
    # goals = [(2, 1), (3, 1), (4, 1), (1, 2), (1, 3), (1, 4), (2, 5), (3, 5), (4, 5)] # c
    # goals = [(1, 2), (1, 3), (1, 4), (2, 3), (3, 4), (4, 3), (5, 2), (5, 3), (5, 4)] # m
    # goals = [(2, 2), (2, 3), (2, 4), (2, 1), (3, 4), (4, 4), (4, 2), (4, 3), (4, 1)] # u

    # goals = [(1, 2), (2, 2), (3, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, 4), (3, 4), (3, 5),
    #           (3, 6), (2, 6), (5, 2), (6, 2), (7, 2), (5, 3), (5, 4), (6, 4), (7, 4), 
    #           (7, 3), (7, 5), (6, 6), (5, 6), (7, 6)] # 69


    goals = [(2, 1), (3, 1), (4, 1), (1, 2), (1, 3), (1, 4), (2, 5), (3, 5), (4, 5), (6, 2), (6, 3), (6, 4), 
             (6, 1), (10, 1), (6, 5), (10, 5), (7, 3), (8, 4), (9, 3), (10, 2), (10, 3), (10, 4), (12, 2), 
             (12, 3), (12, 4), (12, 1), (15, 4), (15, 2), (15, 3), (15, 1), (15, 5), (12, 5), (13, 5), (14, 5)] # cmu
    print(len(goals))

    # goals = [(3, 2), (4, 3), (5, 2), (2, 3), (6, 3), (2, 4), (6, 4), (3, 5), (5, 5), (4, 6), (3, 3), (5, 3), (3, 4), (4, 4), (5, 4), (4, 5)] # heart
    parser = argparse.ArgumentParser()
    parser.add_argument('--xDim', type=int, default=1)
    parser.add_argument('--yDim', type=int, default=1)
    parser.add_argument('--numAgents', type=int, default=0)
    args = parser.parse_args()

    assert(len(goals) == args.numAgents)
    # initialize simulation
    sim = Sim(args.xDim, args.yDim, goals, args.numAgents)
    # initialize canvas
    pygame.display.init()
    pygame.font.init()

    screen = pygame.display.set_mode((sim.xDim * sim.cellSize, sim.yDim * sim.cellSize))
    canvas = pygame.Surface(screen.get_size())
    canvas = canvas.convert()

    # Bad test case: implement A* and come back to this
    # sim.agentList[0].goal = (1, 1)
    # sim.agentList[0].x = 1
    # sim.agentList[0].y = 1
    # sim.agentList[0].candidate = (1, 0)

    # sim.agentList[2].goal = (2, 0)
    # sim.agentList[2].x = 0
    # sim.agentList[2].y = 1
    # sim.agentList[2].candidate = (1, 0)

    # sim.agentList[3].goal = (0, 0)
    # sim.agentList[3].x = 0
    # sim.agentList[3].y = 0
    # sim.agentList[3].candidate = (1, 0)

    # sim.agentList[1].goal = (1, 0)
    # sim.agentList[1].x = 1
    # sim.agentList[1].y = 2
    # sim.agentList[1].candidate = (1, 1)

    

    render_all(canvas, sim, screen)
    atGoal = 0
    time.sleep(1)
    # for agent in sim.agentList:
    #     print("Astar", agent.astar())
    #     sim.swarmMap = SwarmMap(sim.numZeros, sim.agentList)
    #     for agent in sim.agentList:
    #         agent.setMap(sim.swarmMap)


    s = time.time()
    # Main code block
    while atGoal < len(goals):
        atGoal = 0
        time.sleep(1)
        for agent in sim.agentList:
            atGoal += agent.step()
            sim.swarmMap = SwarmMap(sim.numZeros, sim.agentList)
            for agent in sim.agentList:
                agent.setMap(sim.swarmMap)

            render_all(canvas, sim, screen)
    b = time.time()
    time.sleep(3)
    print("time %.3f" % (b - s))
        





if __name__ == '__main__':
    main()
    













    

