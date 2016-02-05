# imports 
import argparse
import Queue

positionMapping = {}
traverseLog = open("traverse_log.txt", "w")
nextStateLog = open("next_state.txt", "w")
traceStateLog = open("trace_state.txt", "w")
grid = {}
playerPosition = {}
gameSim = False

def isRaid(playerPosition, player, (i,j)):
    if (i > 0) and playerPosition[(i-1, j)] == player:
        return True
    if (j > 0) and playerPosition[(i, j-1)] == player:
        return True
    if (i < 4) and playerPosition[(i+1, j)] == player:
        return True
    if (j < 4) and playerPosition[(i, j+1)] == player:
        return True
    
    return False
                

def greedyBestFirst(grid, playerPosition, player, oppPlayer):
    
    queue = Queue.PriorityQueue()
    valuePosMap = {}
    for i in range(0, 5):
        for j in range(0, 5):
            playerPosClone = dict(playerPosition)
            if playerPosClone[(i, j)] == '*':
                playerPosClone[(i, j)] = player
                if isRaid(playerPosClone, player, (i,j)):
                    if (i > 0) and playerPosClone[(i-1, j)] == oppPlayer:
                        playerPosClone[(i-1, j)] = player
                    if (j > 0) and playerPosClone[(i, j-1)] == oppPlayer:
                        playerPosClone[(i, j-1)] = player
                    if (i < 4) and playerPosClone[(i+1, j)] == oppPlayer:
                        playerPosClone[(i+1, j)] = player
                    if (j < 4) and playerPosClone[(i, j+1)] == oppPlayer:
                        playerPosClone[(i, j+1)] = player
                
                value = evaluationFunction(grid, playerPosClone, player)
                if -value not in valuePosMap:
                    queue.put(-value)
                    valuePosMap[-value] = (i,j)
    
    highVal = queue.get()
    (nexti, nextj) = valuePosMap[highVal]
    return (nexti, nextj)

def printGrid(playerPosition):
    if gameSim:
        fileHandle = traceStateLog
    else:
        fileHandle = nextStateLog
    for i in range(0, 5):
          fileHandle.write('{}{}{}{}{}\n'.format(playerPosition[(i,0)], playerPosition[(i,1)], playerPosition[(i,2)], playerPosition[(i,3)], playerPosition[(i,4)]))
        #fileHandle.write(playerPosition[(i,0)]+playerPosition[(i,1)]+playerPosition[(i,2)]+playerPosition[(i,3)]+playerPosition[(i,4)])
        #fileHandle.write("\n")
    return

def nextState(playerPosition, player, oppPlayer, (movei, movej)):
    playerPosClone = dict(playerPosition)
    playerPosClone[(movei, movej)] = player
    if isRaid(playerPosClone, player, (movei, movej)):
        if (movei > 0) and playerPosClone[(movei-1, movej)] == oppPlayer:
            playerPosClone[(movei-1, movej)] = player
        if (movej > 0) and playerPosClone[(movei, movej-1)] == oppPlayer:
            playerPosClone[(movei, movej-1)] = player
        if (movei < 4) and playerPosClone[(movei+1, movej)] == oppPlayer:
            playerPosClone[(movei+1, movej)] = player
        if (movej < 4) and playerPosClone[(movei, movej+1)] == oppPlayer:
            playerPosClone[(movei, movej+1)] = player
    return playerPosClone

def miniMaxTraverseLogPrint((i, j), depth, value):
    if gameSim:
        return
    if value == float('inf'):
        valueStr = "Infinity"
    elif value == float('-inf'):
        valueStr = "-Infinity"
    else:
        valueStr = str(value)
    traverseLog.write('{},{},{}\n'.format(positionMapping[(i, j)], depth, valueStr))   

def miniMax(grid, playerPosition, player, oppPlayer, depth):
    
    mainPlayer = player
    bestScore = float('-inf')
    for i in range(0, 5):
        for j in range(0, 5):
            if playerPosition[(i,j)] == '*':
                miniMaxTraverseLogPrint((-1, -1), 0, bestScore)
                playerPosClone = nextState(playerPosition, player, oppPlayer, (i, j))
                score = minValue(grid, playerPosClone, depth, 1, oppPlayer, player, mainPlayer, (i, j))
                miniMaxTraverseLogPrint((i, j), 1, score)
                if score > bestScore:
                    (besti, bestj) = (i,j)
                    bestScore = score 
    
    miniMaxTraverseLogPrint((-1, -1), 0, bestScore)
    return (besti, bestj)

def minValue(grid, playerPosition, depth, myDepth, player, oppPlayer, mainPlayer, (previ, prevj)):
    if cutoff_function(playerPosition, depth, myDepth):
        return evaluationFunction(grid, playerPosition, mainPlayer)
    best_score = float('inf')
    for i in range(0, 5):
        for j in range(0, 5):
            if playerPosition[(i, j)] == '*':
                miniMaxTraverseLogPrint((previ, prevj), myDepth, best_score)
                playerPosClone = nextState(playerPosition, player, oppPlayer, (i,j))
                score = maxValue(grid, playerPosClone, depth, myDepth+1, oppPlayer, player, mainPlayer, (i ,j))
                miniMaxTraverseLogPrint((i, j), myDepth+1, score)
                if score < best_score:
                    (besti, bestj) = (i, j)
                    best_score = score
    return best_score

def maxValue(grid, playerPosition, depth, myDepth, player, oppPlayer, mainPlayer, (previ, prevj)):
    if cutoff_function(playerPosition, depth, myDepth):
        return evaluationFunction(grid, playerPosition, mainPlayer)
    best_score = float('-inf')
    for i in range(0, 5):
        for j in range(0, 5):
            if playerPosition[(i, j)] == '*':
                miniMaxTraverseLogPrint((previ, prevj), myDepth, best_score)
                playerPosClone = nextState(playerPosition, player, oppPlayer, (i,j))
                score = minValue(grid, playerPosClone, depth, myDepth+1, oppPlayer, player, mainPlayer, (i, j))
                miniMaxTraverseLogPrint((i, j), myDepth+1, score)
                if score > best_score:
                    (besti, bestj) = (i, j)
                    best_score = score
    return best_score

def cutoff_function(playerPosition, depth, myDepth):
    if myDepth >= depth:
        return True
    for i in range(0, 5):
        for j in range(0, 5):
            if playerPosition[(i,j)] == '*':
                return False
    
    return True

def alphaBetaTraverseLogPrint((i, j), depth, value, alpha, beta):
    if gameSim:
        return
    if alpha == float('inf'):
        alphaStr = "Infinity"
    elif alpha == float('-inf'):
        alphaStr = "-Infinity"
    else:
        alphaStr = str(alpha)
    if beta == float('inf'):
        betaStr = "Infinity"
    elif beta == float('-inf'):
        betaStr = "-Infinity"
    else:
        betaStr = str(beta)
    if value == float('inf'):
        valueStr = "Infinity"
    elif value == float('-inf'):
        valueStr = "-Infinity"
    else:
        valueStr = str(value)
    traverseLog.write('{},{},{},{},{}\n'.format(positionMapping[(i, j)], depth, valueStr, alphaStr, betaStr))

def alphaBetaPruning(grid, playerPosition, player, oppPlayer, depth):
    (nexti, nextj), score = maxValueAlphaBeta(grid, playerPosition, player, oppPlayer, player, depth, 0, float('-inf'), float('inf'), -1, -1)
    return (nexti, nextj)

def maxValueAlphaBeta(grid, playerPosition, player, oppPlayer, mainPlayer, depth, myDepth, alpha, beta, previ, prevj):
    if cutoff_function(playerPosition, depth, myDepth):
        value = evaluationFunction(grid, playerPosition, mainPlayer)
        alphaBetaTraverseLogPrint((previ, prevj), myDepth, value, alpha, beta)
        return (-1, -1), value
    best_score = float('-inf')
    for i in range(0, 5):
        for j in range(0, 5):
            if playerPosition[(i, j)] == '*':
                alphaBetaTraverseLogPrint((previ, prevj), myDepth, best_score, alpha, beta)
                playerPosClone = nextState(playerPosition, player, oppPlayer, (i,j))
                _, score = minValueAlphaBeta(grid, playerPosClone, oppPlayer, player, mainPlayer, depth, myDepth+1, alpha, beta, i, j)
                if score > best_score:
                    (besti, bestj) = (i, j)
                    best_score = score
                if best_score >= beta:
                    alphaBetaTraverseLogPrint((previ, prevj), myDepth, best_score, alpha, beta)
                    return (besti, bestj), best_score
                if alpha < best_score:
                    alpha = best_score
    alphaBetaTraverseLogPrint((previ, prevj), myDepth, best_score, alpha, beta)
    return (besti, bestj), best_score

def minValueAlphaBeta(grid, playerPosition, player, oppPlayer, mainPlayer, depth, myDepth, alpha, beta, previ, prevj):
    if cutoff_function(playerPosition, depth, myDepth):
        value = evaluationFunction(grid, playerPosition, mainPlayer)
        alphaBetaTraverseLogPrint((previ, prevj), myDepth, value, alpha, beta)
        return (-1, -1), value
    best_score = float('inf')
    for i in range(0, 5):
        for j in range(0, 5):
            if playerPosition[(i, j)] == '*':
                alphaBetaTraverseLogPrint((previ, prevj), myDepth, best_score, alpha, beta)
                playerPosClone = nextState(playerPosition, player, oppPlayer, (i,j))
                _, score = maxValueAlphaBeta(grid, playerPosClone, oppPlayer, player, mainPlayer, depth, myDepth+1, alpha, beta, i, j)
                if score < best_score:
                    (besti, bestj) = (i, j)
                    best_score = score
                if best_score <= alpha:
                    alphaBetaTraverseLogPrint((previ, prevj), myDepth, best_score, alpha, beta)
                    return (besti, bestj), best_score
                if beta > best_score:
                    beta = best_score
    alphaBetaTraverseLogPrint((previ, prevj), myDepth, best_score, alpha, beta)
    return (besti, bestj), best_score

def evaluationFunction(grid, playerPosition, player):
    myValue = 0
    oppValue = 0
    for i in range(0, 5):
        for j in range(0, 5):
            if playerPosition[(i, j)] == player:
                myValue = myValue + grid[(i, j)]
            elif playerPosition[(i, j)] != '*':
                oppValue = oppValue + grid[(i, j)]
    return myValue - oppValue

def createPositionMapping():
    positionMapping[(-1, -1)] = "root"
    for i in range(0, 5):
        positionMapping[(i,0)] = "A"+str(i+1)
        positionMapping[(i,1)] = "B"+str(i+1)
        positionMapping[(i,2)] = "C"+str(i+1)
        positionMapping[(i,3)] = "D"+str(i+1)
        positionMapping[(i,4)] = "E"+str(i+1)

def gridNotFilled(playerPosition):
    for i in range(0,5):
        for j in range(0,5):
            if playerPosition[(i,j)] == "*":
                return True
    return False

def swap(one, two):
    return two, one

def nextMoveForPlayer(playerPosition, player, algo, depth, oppPlayer):
    if algo == 1:
        (nexti, nextj) = greedyBestFirst(grid, playerPosition, player, oppPlayer)
    elif algo == 2:
        (nexti, nextj) = miniMax(grid, playerPosition, player, oppPlayer, depth)            
    elif algo == 3:
        (nexti, nextj) = alphaBetaPruning(grid, playerPosition, player, oppPlayer, depth)
    return (nexti, nextj)

def gameSimulation(dataLines):
    playerOne = dataLines[1][0:1]
    algoOne = int(dataLines[2][:-1])
    depthOne = int(dataLines[3][:-1])
    playerTwo = dataLines[4][0:1]
    algoTwo = int(dataLines[5][:-1])
    depthTwo = int(dataLines[6][:-1])
    for i in range(0,5):
        val = dataLines[i+7][:-1].split()
        for j in range(0,5):
            grid[i,j] = int(val[j])
    playerPosition = {}
    for i in range(0,5):
        val = dataLines[i+12]
        for j in range(0,5):
            playerPosition[i,j] = val[j]
    while gridNotFilled(playerPosition):
        (nexti, nextj) = nextMoveForPlayer(playerPosition, playerOne, algoOne, depthOne, playerTwo)
        playerPosition = nextState(playerPosition, playerOne, playerTwo, (nexti, nextj))
        printGrid(playerPosition)
        algoOne, algoTwo = swap(algoOne, algoTwo)
        depthOne, depthTwo = swap(depthOne, depthTwo)
        playerOne, playerTwo = swap(playerOne, playerTwo)
    
    traceStateLog.seek(0,2)
    nsize = traceStateLog.tell()
    traceStateLog.truncate(nsize-1)

# main
if __name__ == "__main__":

    createPositionMapping()
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', required=True)
    args = parser.parse_args()
    inFile = args.i
    inF = open(inFile, 'r')
    dataLines = inF.readlines()
    algo = int(dataLines[0][:-1])
    if algo == 4:
        gameSim = True
        gameSimulation(dataLines)
    else:
        player = dataLines[1][0:1]
        depth = int(dataLines[2][:-1])
        for i in range(0,5):
            val = dataLines[i+3][:-1].split()
            for j in range(0,5):
                grid[i,j] = int(val[j])
        
        for i in range(0,5):
            val = dataLines[i+8]
            for j in range(0,5):
                playerPosition[i,j] = val[j]
        inF.close()
        if player == 'X':
            oppPlayer = 'O'
        else:
            oppPlayer = 'X'
        
        if algo == 1:
            (nexti, nextj) = greedyBestFirst(grid, playerPosition, player, oppPlayer)
            playerPosition = nextState(playerPosition, player, oppPlayer, (nexti, nextj))
            printGrid(playerPosition)
        elif algo == 2:
            traverseLog.write("Node,Depth,Value\n")
            (nexti, nextj) = miniMax(grid, playerPosition, player, oppPlayer, depth)            
            playerPosition = nextState(playerPosition, player, oppPlayer, (nexti, nextj))
            printGrid(playerPosition)
            traverseLog.seek(0,2)
            size = traverseLog.tell()
            traverseLog.truncate(size-1)
        elif algo == 3:
            traverseLog.write("Node,Depth,Value,Alpha,Beta\n")
            (nexti, nextj) = alphaBetaPruning(grid, playerPosition, player, oppPlayer, depth)
            playerPosition = nextState(playerPosition, player, oppPlayer, (nexti, nextj))
            printGrid(playerPosition)
            traverseLog.seek(0,2)
            size = traverseLog.tell()
            traverseLog.truncate(size-1)
        nextStateLog.seek(0,2)
        nsize = nextStateLog.tell()
        nextStateLog.truncate(nsize-1)
    traverseLog.close()
    nextStateLog.close()
    traceStateLog.close()
