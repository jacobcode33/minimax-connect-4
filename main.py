import pygame as pg, time, random, math, copy

w,h = 8,8
screenw, screenh = 50*(1+w),50*(2+h)
pg.init()
screen = pg.display.set_mode((screenw,screenh))

board = []
for col in range(h):
    row = [0]*w
    board.append(row)

def drawboard(board,w,h):
    for y in range(h):
        for x in range(w):
            if board[y][x] == 0:
                pg.draw.circle(screen, (200,200,200), ((x+1)*50,(y+1)*50), 20)
            elif board[y][x] == 1:
                pg.draw.circle(screen, (200,0,0), ((x+1)*50,(y+1)*50), 20)
            elif board[y][x] == 2:
                pg.draw.circle(screen, (0,0,200), ((x+1)*50,(y+1)*50), 20)

def isquit():
    ev = pg.event.get()
    for event in ev:
        if event.type == pg.QUIT:
            return True
    return False

def place(state,turn,x): #assumes the input is legal
    for y in range(h):
        if state[-y-1][x] == 0:
            state[-y-1][x] = turn
            return state

def hplace(board):
    x1,y1 = pg.mouse.get_pos()
    for x2 in range(w):
        for y2 in range(h):
            x3 = (x2+1)*50
            y3 = (y2+1)*50
            dis = math.sqrt((x1-x3)**2+(y1-y3)**2)
            if dis <= 20:
                if board[0][x2] == 0: # if theres at least the top one free in that column
                    return x2
    return False

def getadjacent(board,team):
    def gethor(board,team):
        most = 0
        for y in range(h):
            run = 0
            for x in range(w):
                if board[y][x] == team:
                    run += 1
                    if run > most:
                        most = run
                else:
                    run = 0
        return most

    def getver(board,team):
        most = 0
        for x in range(w):
            last = None
            run = 0
            for y in range(h):
                if board[y][x] == team:
                    run += 1
                    if run > most:
                        most = run
                else:
                    run = 0
        return most

    def getdia1(board,team):
        maxdiag = 0
        for x in range (h):
            for y in range (w):
                k = 0
                while (x+k < h and y+k < w and board[x+k][y+k] == team):
                    k+=1
                    if (k > maxdiag):
                        maxdiag = k
        return maxdiag

    def getdia2(board,team):
        maxdiag = 0
        for x in range (w):
            for y in range (h):
                k = 0
                while (x-k >= 0 and y+k < w and board[x-k][y+k] == team):
                    k+=1
                    if (k > maxdiag):
                        maxdiag = k
        return maxdiag
        
    runs = [gethor(board,team),getver(board,team),getdia1(board,team),getdia2(board,team)]
    return runs

def aichoose(board,team):
    global depth
    def getscore(state):
        def gethor(board,team):
            points = 0
            for y in range(h):
                prun = 0
                rrun = 0
                for x in range(w):
                    if board[y][x] == team: # if its your piece
                        prun += 1
                        rrun += 1
                    elif board[y][x] == 0: # if its empty
                        prun += 1
                    else: # if its their piece
                        if prun >= 4:
                            points += rrun**2
                        prun = 0
                        rrun = 0
                if prun >= 4:
                    if rrun >=4:
                        return 9999999 # return large number if a state has a winner
                    points += rrun**2
            return points

        def getver(board,team):
            points = 0
            for x in range(w):
                prun = 0
                rrun = 0
                for y in range(h):
                    if board[y][x] == team: # if its your piece
                        prun += 1
                        rrun += 1
                    elif board[y][x] == 0: # if its empty
                        prun += 1
                    else: # if its their piece
                        if prun >= 4:
                            points += rrun**2
                        prun = 0
                        rrun = 0
                if prun >= 4:
                    if rrun >=4:
                        return 9999999 # return large number if a state has a winner
                    points += rrun**2
            return points

        def getdia1(board,team):
            points = 0
            used = []
            for x in range (h):
                for y in range (w):
                    k = 0
                    rrun = 0
                    while (x+k < h and y+k < w and (board[x+k][y+k] == team or board[x+k][y+k] == 0) and (x+k,y+k) not in used):
                        if board[x+k][y+k] == team:
                            used.append((x+k,y+k))
                            rrun += 1
                        k+=1
                    if k >= 4:
                        if rrun >=4:
                            return 9999999 # return large number if a state has a winner
                        points+=rrun**2
            return points
                    
        def getdia2(board,team):
            points = 0
            used = []
            for x in range (h):
                for y in range (w):
                    k = 0
                    rrun = 0
                    while (x-k >= 0 and y+k < w and (board[x-k][y+k] == team or board[x-k][y+k] == 0) and (x-k,y+k) not in used):
                        if board[x-k][y+k] == team:
                            used.append((x-k,y+k))
                            rrun += 1
                        k+=1
                    if k >= 4:
                        if rrun >=4:
                            return 9999999 # return large number if a state has a winner
                        points+=rrun**2
            return points
        
        total = (gethor(state,2)+getver(state,2)+getdia1(state,2)+getdia2(state,2)) - (gethor(state,1)+getver(state,1)+getdia1(state,1)+getdia2(state,1))
        if team == 1: total *= 1

        return total
        

    def recurse(state,count):
        global progress
        if count == depth-2:
            progress += 1/64
            pg.draw.rect(screen, (50,255,50), (35,50*h+50,progress*(50*w-20),30))
            pg.display.update()

        score = getscore(state)
        if count != depth and abs(score) > 999999: # if a winning state is found simply return that score as game will terminate at this state
            return score-count

        if count == 0: # if its the final state
            return score # simply return the score of this state

        else: # if it is a middle state
            who = count%2 + 1
            states = []
            for x in range(w): # for all the possible choices which can be made
                if state[0][x] == 0:
                    new = place(copy.deepcopy(state),who,x) # create new board state
                    states.append(recurse(new,count-1)) # create list of scores of the child states
                else:
                    if who == 2:
                        states.append(-999999999) # if its an illegal move score is the worst move possible this means that you will never choose it
                    else:
                        states.append(999999999)
            if depth % 2 == 0 or True: # maybe not right
                if count == depth:
                    return states.index(min(states))
                if who % 2 == 0:
                    return max(states)
                else:
                    return min(states)
    return recurse(copy.deepcopy(board),depth)

players = 1 # currently ai vs ai not work
turn = 1
last = False
winner = 0
depth = 4
while not isquit() and winner == 0:
    screen.fill((0,0,0))
    drawboard(board,w,h)
    
    if turn <= players:
        if pg.mouse.get_pressed()[0] == 1 and not last:
            slot = hplace(board)
            if type(slot) == int:
                state = copy.deepcopy(board)
                board = place(state,turn,slot)
                turn = (turn % 2) + 1
        last = pg.mouse.get_pressed()[0] != 0
    
    else:
        state = copy.deepcopy(board)
        progress = 0
        board = place(state,turn,aichoose(state,turn))
        turn = (turn % 2) + 1

    for t in range(2):
        if max(getadjacent(board,t+1)) >= 4:
            winner = t+1



    pg.display.update()
print("winner =", winner)
while not isquit():
    drawboard(board,w,h)
    pg.display.update()