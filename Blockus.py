#From CMU-112: http://www.cs.cmu.edu/~112/
from cmu_112_graphics import *
import copy 
import math
import random
from tkinter import *
from PIL import Image

#################################################
#Chanaradee Leelamanthep
#################################################

class Heuristics: 
    #The following two tables show the optimal positions for each player. The 
    #higher the number, the better the move is, and vice versa. These tables are 
    #used to calculate the minimax alpha-beta pruning for the 'smartest' AI.
    pieceTableAI = [
        [9, 9, 9, 8, 9, 8, 7, 7, 7, 6, 6, 7, 8, 9],
        [9, 9, 9, 10, 9, 9, 8, 6, 6, 6, 7, 8, 7, 8],
        [9, 9, 9, 10, 8, 7, 7, 6, 6, 5, 5, 8, 7, 7],
        [8, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 7, 7, 6],
        [9, 9, 8, 10, 9, 9, 9, 8, 7, 10, 8, 6, 6, 5],
        [8, 9, 7, 10, 9, 8, 7, 7, 10, 9, 8, 8, 5, 4],
        [7, 8, 7, 10, 8, 7, 8, 10, 8, 6, 7, 5, 6, 4],
        [7, 6, 6, 10, 7, 8, 10, 9, 8, 6, 6, 5, 5, 3],
        [7, 6, 6, 10, 7, 10, 8, 8, 6, 5, 4, 4, 3, 3],
        [6, 6, 5, 9, 10, 9, 6, 6, 5, 3, 3, 2, 2, 2],
        [6, 7, 5, 9, 8, 7, 7, 5, 4, 3, 2, 2, 2, 2],
        [7, 8, 9, 7, 6, 8, 4, 5, 4, 2, 2, 1, 1, 1],
        [8, 7, 7, 7, 6, 5, 6, 5, 3, 2, 2, 1, 1, 1],
        [9, 8, 7, 6, 5, 4, 4, 3, 3, 2, 2, 1, 1, 1]
    ]

    pieceTablePlayer = [
        [1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 6, 7, 8, 9],
        [1, 1, 1, 2, 2, 3, 5, 6, 5, 6, 7, 7, 7, 8],
        [1, 1, 1, 2, 2, 4, 5, 4, 8, 6, 7, 9, 8, 7],
        [2, 2, 2, 2, 3, 4, 5, 7, 7, 8, 9, 5, 7, 6],
        [2, 2, 2, 3, 3, 5, 6, 6, 9, 10, 9, 5, 6, 6],
        [3, 3, 4, 4, 5, 6, 8, 8, 10, 7, 10, 6, 6, 7],
        [3, 5, 5, 6, 6, 8, 9, 10, 8, 7, 10, 6, 6, 7],
        [4, 6, 5, 7, 6, 8, 10, 8, 7, 8, 10, 7, 8, 7],
        [4, 5, 8, 8, 9, 10, 7, 7, 8, 9, 10, 7, 9, 8],
        [5, 6, 6, 8, 10, 7, 8, 9, 9, 9, 10, 8, 9, 9],
        [6, 7, 7, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 8],
        [7, 7, 8, 5, 5, 6, 6, 7, 7, 8, 10, 9, 9, 9],
        [8, 7, 8, 7, 6, 6, 6, 8, 9, 9, 10, 9, 9, 9],
        [9, 8, 7, 6, 6, 7, 7, 7, 8, 9, 8, 9, 9, 9]
    ]

class PlayBlokus(Mode):                
    def gameDimensions(mode): 
        #the board for blokus 2v2 is 14x14 
        rows, cols, cellSize, margin = 14, 14, 20, 20*10
        scaleRow, scaleCol = 5, 5
        rowAdjustment = 22
        player = 2
        return (rows, cols, cellSize, margin, scaleRow, scaleCol,rowAdjustment,\
            player)

    def appStarted(mode):
        mode.rows, mode.cols, mode.cellSize, mode.margin, mode.scaleRow, \
            mode.scaleCol, mode.rowAdjustment, mode.players = mode.gameDimensions()
        mode.emptyColor = "gray86"
        mode.board = [([mode.emptyColor]*mode.cols) for rows in range(mode.rows)]
        mode.isGameOver = False
        mode.pieces = mode.createPieces("RosyBrown1")
        mode.piecesTwo = mode.createPieces("PaleTurquoise1")
        mode.turn = 0
        mode.isMousePressed = False
        mode.mouseX, mode.mouseY = -1, -1
        mode.mouseXRelease, mode.mouseYRelease = -1, -1
        mode.isClickingNewPiece = False
        mode.clickedPiece = [([False])*5 for rows in range(5)]
        mode.turnPlayer = ""
        mode.prevPage = "multiplayer"
        mode.player1Points, mode.player2Points = 0, 0
        #PHOTO FROM https://www.stickpng.com/
        hintUrl = "https://tinyurl.com/wqf6qtg"
        mode.hint = mode.loadImage(hintUrl)
        mode.hint = mode.scaleImage(mode.hint, 1/13)
        mode.player1HasMoves = True
        mode.player2HasMoves = True
    
    def checkGameStatus(mode):
        #If there are no possible moves left for both players, the game is over.
        #This will change to a game over state. 
        if not mode.possibleMovesP1(mode.board, mode.pieces, "RosyBrown1") and \
            not mode.possibleMovesP2(mode.board, mode.piecesTwo, "PaleTurquoise1"):
            mode.isGameOver = True
            return
    
    def mousePressed(mode, event):
        mode.isMousePressed = True
        mode.mouseX, mode.mouseY = event.x, event.y
        #If the back button is clicked, it will take the player back to the previous page
        if mode.height//100 <= event.x <= mode.height//100 + mode.height//100 * 9 and \
            -mode.height//200 + mode.height - mode.height //100 * 9 <= event.y <= -mode.height//200 + mode.height:
            mode.app.setActiveMode(mode.app.localP)
        #If the question mark is clicked, it will take the player to the help page
        elif mode.height//34 <= event.y <= mode.height//17 and \
            mode.width - mode.height//20 - 10 <= event.x <= mode.width - mode.height//20 + 10:
                mode.app.setActiveMode(mode.app.helpMode)
        if not mode.isGameOver:
            mode.isMousePressed = True
            #If the lightbulb/hint photo is clicked, a hint move is played on 
            # behalf of the player.
            mode.mouseX, mode.mouseY = event.x, event.y
            hintWidth, hintHeight = mode.hint.size
            if mode.app.width - mode.app.width//8 - hintWidth//2 <= event.x <= mode.app.width - mode.app.width//8 + hintWidth//2 \
                and mode.app.height//2 - hintHeight//2 <= event.y <= mode.app.height//2 + hintHeight//2:
                if mode.turn % 2 == 0:
                    pPieces = mode.possibleMovesP1(mode.board, mode.pieces, "RosyBrown1")
                    mode.getHint(pPieces, "RosyBrown1", mode.pieces)
                else:
                    pPieces = mode.possibleMovesP2(mode.board, mode.piecesTwo, "PaleTurquoise1")
                    mode.getHint(pPieces, "PaleTurquoise1", mode.piecesTwo)

    def mouseDragged(mode, event):
        mode.mouseXRelease, mode.mouseYRelease = event.x, event.y

    def mouseReleased(mode, event):
        mode.mouseXRelease, mode.mouseYRelease = event.x, event.y
        mode.isMouseTouchingPiece()
        mode.isMousePressed = False
        mode.checkGameStatus()
        if mode.turn % 2 == 0:
            if not mode.possibleMovesP1(mode.board, mode.pieces, "RosyBrown1"):
                mode.player1HasMoves = False
        else:
            if not mode.possibleMovesP2(mode.board, mode.piecesTwo, "PaleTurquoise1"):
                mode.player2HasMoves = False

    def drawNoMoreMove(mode, canvas):  
        if not mode.player1HasMoves:
            canvas.create_text(mode.app.width//2, mode.app.height//2 + mode.app.height//5 + 15, 
            text = "NO MORE MOVES FOR PLAYER 1")
        if not mode.player2HasMoves:
            canvas.create_text(mode.app.width//2, mode.app.height//2 - mode.app.height//5 - 15, 
            text = f"NO MORE MOVES FOR PLAYER 2")

    def keyPressed(mode, event):
        if event.key == "r":
            mode.isGameOver = False
            mode.app.playLocal = PlayBlokus()
            mode.app.setActiveMode(mode.app.playLocal)
        elif event.key == "Up":
            mode.clickedPiece = mode.flipUpDown(mode.clickedPiece)
        elif event.key == "Right":
            mode.clickedPiece = mode.flipSideways(mode.clickedPiece)
        elif event.key == "Down":
            mode.clickedPiece = mode.rotate(mode.clickedPiece)
        elif event.key == "h":
            if mode.turn % 2 == 0:
                pPieces = mode.possibleMovesP1(mode.board, mode.pieces, "RosyBrown1")
                mode.getHint(pPieces, "RosyBrown1", mode.pieces)
            else:
                pPieces = mode.possibleMovesP2(mode.board, mode.piecesTwo, "PaleTurquoise1")
                mode.getHint(pPieces, "PaleTurquoise1", mode.piecesTwo)

    def drawHint(mode, canvas):
        canvas.create_text(mode.app.width//2, mode.app.height - mode.app.height//50, 
        text = "CLICK THE LIGHTBULB OR PRESS H FOR HINTS!")
 
    def getHint(mode, pieces, color, dict):
        #After all the possible moves for a player is generated, the hint chooses the
        #piece with the most points. The piece's current information is updated here. 
        if pieces == []:
            mode.turn += 1
            return
        piece = mode.findLargestPossiblePiece(pieces)
        row, col, hintPiece, origPiece = piece
        mode.updateBoard(mode.board, row, col, hintPiece, color)
        for elem in dict:
            row, col, color, shape, hasMoved, isClicked = dict[elem]
            if shape == origPiece:
                dict[elem] = row, col, color, shape, True, isClicked
                continue
        mode.turn += 1

    def findLargestPossiblePiece(mode, pieces):
        if pieces == []:
            return
        maxScore = 0
        maxPiece = None
        index = 0
        while index < len(pieces) and maxScore < 5:
            pieceScore = 0
            piece = pieces[index]
            row, col, shape, origShape = piece
            for r in range(len(shape)):
                for c in range(len(shape[r])):
                    if shape[r][c]:
                        pieceScore += 1
            if pieceScore > maxScore:
                maxScore = pieceScore
                maxPiece = piece
            index += 1
        return maxPiece
        
    def drawBoard(mode, canvas):
        for row in range(mode.rows):
            for col in range(mode.cols):
                mode.drawCell(canvas, row, col, mode.board[row][col])

    def drawPieces(mode, canvas):
        mode.drawPieceByColor(canvas, mode.pieces, 0)
        mode.drawPieceByColor(canvas,mode.piecesTwo, mode.rowAdjustment)

    def drawPieceByColor(mode, canvas, dictPlayer,rowAdjustment):
        for elem in dictPlayer:
            row, col, color, shape, hasMoved, isClicked = dictPlayer[elem]
            if hasMoved:
                continue
            for r in range(len(shape)):
                for c in range(len(shape[0])):
                    if shape[r][c]:
                        mode.drawCellPieces(canvas, row+ r-rowAdjustment,\
                            col + c, color)

    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "antique white")
        mode.drawBoard(canvas)
        mode.drawPieces(canvas)
        mode.drawHelpButton(canvas)
        mode.drawNoMoreMove(canvas)
        if mode.turn % 2 == 0:
            color = "RosyBrown1"
        else:
            color = "PaleTurquoise1"
        mode.drawClickedPiece(canvas, color)
        mode.drawPrevScreen(canvas)
        mode.drawScore(canvas)
        mode.drawTurn(canvas)
        #DRAW HINT ICON
        canvas.create_image(mode.app.width - mode.app.width//8, mode.app.height//2, image = ImageTk.PhotoImage(mode.hint))
        mode.drawHint(canvas)
        #Display the scoreboard once the game is over
        if mode.isGameOver:
            font = f"helvetica {mode.app.width//20} bold"
            canvas.create_rectangle(0, mode.app.height//2 - mode.app.height//2, mode.app.width, mode.app.height//2 - mode.app.height//2, fill = "antique white")
            canvas.create_text(mode.app.width//2, mode.app.height//5, text = "GAME OVER", fill = "BLACK", font= font)
            text = "PLAYERS TIED!!!"
            if mode.player1Points > mode.player2Points:
                text = f"""
       PLAYER 1 WON\n
        Player 1: {mode.player1Points}
        Player 2: {mode.player2Points}

        Press r to restart
                """
            elif mode.player1Points < mode.player2Points:
                text = f"""
       PLAYER 2 WON\n
        Player 2: {mode.player2Points}
        Player 1: {mode.player1Points}

        Press r to restart
                """
            canvas.create_text(mode.app.width//2, mode.app.height//2, text = text, fill = "black", font = font)

    def drawScore(mode, canvas):
        #Draws a box around the player with the higher score
        if mode.player1Points > mode.player2Points:
            canvas.create_rectangle(mode.app.width - mode.app.width//5 - 40, mode.app.height//5 * 2 - 20,
            mode.app.width - mode.app.width//5 + 70, mode.app.height//5 * 2 )
        elif mode.player2Points > mode.player1Points:
            canvas.create_rectangle(mode.app.width - mode.app.width//5 - 40, mode.app.height//5 * 2,
            mode.app.width - mode.app.width//5 + 70, mode.app.height//5 * 2 + 20)
        canvas.create_text(mode.app.width - mode.app.width //5, mode.app.height//5*2 - 30, text = "SCORE", 
            font = "helvetica 20 bold")
        canvas.create_text(mode.app.width - mode.app.width //5, mode.app.height//5*2, text = f"""
        PLAYER ONE: {mode.player1Points}
        PLAYER TWO: {mode.player2Points}
        """)

    def drawPrevScreen(mode, canvas):
        fontSize = int(mode.width//60)
        font = f"helvetica {fontSize}"
        #DRAW BACK TO PREVIOUS PAGE BUTTON
        canvas.create_oval(mode.height//100, -mode.height//200 + mode.height - mode.height //100 * 9, mode.height//100 + mode.height//100 * 9 , -mode.height//200 + mode.height, fill = "red")
        canvas.create_text(mode.height//20,  mode.height - mode.height //170 * 9, text = f"  BACK\n{mode.prevPage}", font = font)
    
    def drawCell(mode, canvas, row, col, color):
        canvas.create_rectangle(mode.margin + (col)*mode.cellSize,
            mode.margin + (row)*mode.cellSize,
            mode.margin + (col + 1)*mode.cellSize,
            mode.margin + (row + 1)*mode.cellSize, fill = color, width = 1)

    def drawCellPieces(mode, canvas, row, col, color):
        if color == "RosyBrown1":
            canvas.create_rectangle(mode.margin//2 + (col)*mode.cellSize,
            mode.margin//2 + (row + 1)*mode.cellSize,
            mode.margin//2 + (col + 1)*mode.cellSize,
            mode.margin//2 + (row + 2)*mode.cellSize, fill = color, width = 2)
        else:
            canvas.create_rectangle(mode.margin//2 + (col)*mode.cellSize,
            mode.margin//2 + (row)*mode.cellSize,
            mode.margin//2 + (col + 1)*mode.cellSize,
            mode.margin//2 + (row + 1)*mode.cellSize, fill = color, width = 2)                                           

    def drawClickedPiece(mode, canvas, color):
        for r in range(len(mode.clickedPiece)):
            for c in range(len(mode.clickedPiece[r])):
                if mode.clickedPiece[r][c]:
                    mode.drawClickedCell(canvas, r, c, color)
                
    def drawClickedCell(mode, canvas, row, col, color):
        canvas.create_rectangle(mode.margin//2 + (col)*mode.cellSize,
            mode.height//2 + (row)*mode.cellSize,
            mode.margin//2 + (col + 1)*mode.cellSize,
            mode.height//2 + (row + 1)*mode.cellSize, fill = color, width = 2) 

    def drawHelpButton(mode, canvas):
        fontSize = int(mode.width//20)
        font = f"helvetica {fontSize} bold"
        canvas.create_text(mode.width - mode.height//20,  mode.height//20, text = "?", font = font )

    def drawTurn(mode, canvas):
        #Specifies whose turn it is to place the piece
        canvas.create_text(mode.app.width//5, mode.app.height//3, text = f"Player {mode.turn%mode.players + 1}'s turn")
    
    def createPieces(mode, color):
        pieces = dict()
        p1 = [[True]]
        optionsP1 = []
        pieces[1] = (25, 16, color, p1, False, False)
        p2 = [[True, False],[True, False]]
        pieces[2] = (24, 9, color, p2, False, False)
        p3 = [[True,True,True]]
        pieces[3] = (24, 23, color, p3, False, False)
        p4 = [[True,True,True,True]]
        pieces[4] = (25, 0, color, p4, False, False)
        p5 = [[True,True,True,True,True]]
        pieces[5] = (19, 0, color, p5, False, False)
        p6 = [[True,False],
              [True,True]]
        pieces[6] = (24, 21, color, p6, False, False)
        p7 = [[True,False,False],
              [True,True,True]]
        pieces[7] = (24, 5, color, p7, False, False)
        p8 = [[True,True,True,True],
              [True,False,False,False]]
        pieces[8] = (19, 22, color, p8, False, False)
        p9 = [[True,False,False],
              [True,False,False],
              [True,True,True]]
        pieces[9] = (19, 11, color, p9, False, False)
        p10 = [[True,False,False],
               [True,True,False],
               [False,True,True]]
        pieces[10] = (21, 9, color, p10, False, False)
        p11 = [[False,True,False],
               [True,True,True]]
        pieces[11] = (24, 11, color, p11, False, False)
        p12 = [[True,True,True],
               [False,True,False],
               [False,True,False]]
        pieces[12] = (19, 14, color, p12, False, False)
        p13 = [[False,True,False,False],
               [True,True,True,True]]
        pieces[13] = (21, 0, color, p13, False, False)
        p14 = [[True, False],
               [True, True],
               [False, True]]
        pieces[14] = (21, 25, color, p14, False, False)
        p15 = [[False,True,True,True],
               [True,True,False,False]]
        pieces[15] = (19, 6, color, p15, False, False)
        p16 = [[True,False,False],
               [True,True,True],
               [False,False,True]]
        pieces[16] = (21, 5, color, p16, False, False)
        p17 = [[True,True],
               [True,True]]
        pieces[17] = (24, 18, color, p17, False, False)
        p18 = [[True,False],
               [True,True],
               [True,True]]
        pieces[18] = (22, 14, color, p18, False, False)
        p19 = [[True,True,True],
               [True,False,True]]
        pieces[19] = (19, 18, color, p19, False, False)
        p20 = [[False,False,True],
               [True,True,True],
               [False,True,False]]
        pieces[20] = (21, 21, color, p20, False, False)
        p21 = [[False,True,False],
               [True,True,True],
               [False,True,False]]
        pieces[21] = (21, 16, color, p21, False, False)
        return pieces    
    
    def getAllOrientations(mode, piece):
        pieces = []
        for i in range(4):
            newPiece = mode.rotate(piece)
            newPieceCopy = copy.deepcopy(newPiece)
            newPieceCopy2 = copy.deepcopy(newPiece)
            pieceUpDown = mode.flipUpDown(newPieceCopy)
            pieceSide = mode.flipSideways(newPieceCopy2)
            pieces += [newPiece, pieceUpDown, pieceSide]
            piece = newPiece
        return pieces
    
    def getRangeCoordinates(mode, x, y, c, r):
        return (x + c * mode.cellSize, y + r * mode.cellSize)
                
    def isMouseTouchingPiece(mode):
        if mode.isMousePressed:
            if mode.turn % mode.players == 0: 
                mode.turnPlayer = "PINK"
                if not mode.possibleMovesP1(mode.board, mode.pieces, "RosyBrown1"):
                    mode.player1HasMoves = False
                    print("NO MORE MOVES FOR PLAYER 1")
                    mode.turn += 1
                    return
                #Checks to see if a piece is clicked - loops through all the pieces and
                #their entire piece 
                for elem in mode.pieces:
                    row, col, color, piece, hasMoved, isClicked = mode.pieces[elem]
                    if color == "RosyBrown1":
                        tempRow = row + 1
                    x = mode.margin//2 + col * mode.cellSize
                    y = mode.margin//2 + tempRow * mode.cellSize
                    xClickedPiece = mode.margin//2 + 0* mode.cellSize
                    yClickedPiece = mode.margin//2 + 12*mode.cellSize
                    lstOrientations = mode.getAllOrientations(piece)
                    if mode.clickedPiece in lstOrientations:
                        piece = mode.clickedPiece
                    for r in range(len(piece)):
                        for c in range(len(piece[r])):
                            if not piece[r][c]:
                                continue
                            else:
                                xPrime = x + c*mode.cellSize
                                yPrime = y + r*mode.cellSize
                                xPrimeTwo = xClickedPiece + c*mode.cellSize
                                yPrimeTwo = yClickedPiece + r*mode.cellSize
                            #Checks to see if the piece at the original position is moved/will be moved
                            if not hasMoved and ((xPrime <= mode.mouseX <= xPrime + mode.cellSize \
                                and yPrime <= mode.mouseY <= yPrime + mode.cellSize)):
                                mode.clickedPiece = piece
                                mode.pieces[elem] = row, col, color, piece, hasMoved, True
                                newRow = int((mode.mouseYRelease - (mode.margin//2))/mode.cellSize)
                                newCol = int((mode.mouseXRelease - (mode.margin//2))/mode.cellSize)
                                boardRow, boardCol = newRow - mode.scaleRow, newCol - mode.scaleCol
                                if mode.isFirstMove(mode.board, color):
                                    if color == "RosyBrown1":
                                        if piece[0][0] != True or boardRow - r!= 0 or boardCol - c != 0:
                                            return
                                        else: 
                                            mode.pieces[elem]= newRow, newCol, color, piece, True, False
                                            mode.updateBoard(mode.board,boardRow-r, boardCol-c, piece, "RosyBrown1")
                                            mode.turn += 1
                                            mode.resetClickedPiece() 
                                else:
                                    mode.placePiece(boardRow, boardCol, newRow, newCol, r, c, elem, piece, color)
                            #Checks to see if the clicked piece (drawn to the left of the board) can be moved 
                            elif not hasMoved and  (xPrimeTwo <= mode.mouseX <= xPrimeTwo + mode.cellSize and \
                                yPrimeTwo <= mode.mouseY <= yPrimeTwo + mode.cellSize):
                                lstOrientations = mode.getAllOrientations(piece)
                                if mode.clickedPiece not in lstOrientations:
                                    continue
                                mode.pieces[elem] = row, col, color, piece, hasMoved, True
                                newRow = int((mode.mouseYRelease - (mode.margin//2))/mode.cellSize)
                                newCol = int((mode.mouseXRelease - (mode.margin//2))/mode.cellSize)
                                boardRow, boardCol = newRow - mode.scaleRow, newCol - mode.scaleCol
                                #The piece has to start at the corner
                                if mode.isFirstMove(mode.board, color):
                                    if color == "RosyBrown1":
                                        if piece[0][0] != True or boardRow - r!= 0 or boardCol - c != 0:
                                            return
                                        else: 
                                            mode.pieces[elem]= newRow, newCol, color, piece, True, False
                                            mode.updateBoard(mode.board,boardRow-r, boardCol-c, mode.clickedPiece, "RosyBrown1")
                                            mode.turn += 1
                                            mode.resetClickedPiece() 
                                else:
                                    mode.placePiece(boardRow, boardCol, newRow, newCol, r, c, elem, mode.clickedPiece, color)
            elif mode.turn % mode.players == 1: 
                mode.turnPlayer = "PaleTurquoise1"
                if not mode.possibleMovesP2(mode.board, mode.piecesTwo, "PaleTurquoise1"):
                    mode.player2HasMoves = False
                    print("NO MORE MOVES FOR PLAYER 2")
                    mode.turn += 1
                    return
                #Checks to see if a piece is clicked - loops through all the pieces and
                #their entire piece 
                for elem in mode.piecesTwo:
                    row, col, color, piece, hasMoved, isClicked = mode.piecesTwo[elem]
                    row -= mode.rowAdjustment
                    x = mode.margin//2 + col * mode.cellSize
                    y = mode.margin//2 + row * mode.cellSize
                    xClickedPiece = mode.margin//2 + 0* mode.cellSize
                    yClickedPiece = mode.margin//2 + 12*mode.cellSize
                    lstOrientations = mode.getAllOrientations(piece)
                    if mode.clickedPiece in lstOrientations:
                        piece = mode.clickedPiece
                    for r in range(len(piece)):
                        for c in range(len(piece[r])):
                            if not piece[r][c]:
                                continue
                            else:
                                xPrime = x + c*mode.cellSize
                                yPrime = y + r*mode.cellSize
                                xPrimeTwo = xClickedPiece + c*mode.cellSize
                                yPrimeTwo = yClickedPiece + r*mode.cellSize
                            #Checks to see if the piece at the original position is moved/will be moved
                            if not hasMoved and ((xPrime <= mode.mouseX <= \
                                xPrime + mode.cellSize and yPrime <= mode.mouseY \
                                <= yPrime + mode.cellSize)):
                                mode.clickedPiece = piece
                                newRow = int((mode.mouseYRelease - (mode.margin//2))/mode.cellSize)
                                newCol = int((mode.mouseXRelease - (mode.margin//2))/mode.cellSize)
                                #mode.piecesTwo[elem] = newRow, newCol, color, piece, hasMoved, True
                                boardRow, boardCol = newRow - mode.scaleRow, newCol - mode.scaleCol
                                if mode.isFirstMove(mode.board, color):
                                    if color == "PaleTurquoise1":
                                        if piece[len(piece)-1][len(piece[0])-1] != True or boardRow-r+(len(piece)-1)!=len(mode.board)-1 \
                                            or boardCol-c+len(piece[0])-1 != len(mode.board[0])-1:
                                            return
                                        else: 
                                            mode.piecesTwo[elem]= newRow, newCol, color, piece, True, False
                                            mode.updateBoard(mode.board,boardRow-r, boardCol-c, piece, "PaleTurquoise1")
                                            mode.turn += 1
                                            mode.resetClickedPiece() 
                                else:
                                    mode.placePiece(boardRow, boardCol, newRow, newCol, r, c, elem, piece, color)
                            #Checks to see if the clicked piece (drawn to the left of the board) can be moved 
                            elif not hasMoved and (xPrimeTwo <= mode.mouseX <= \
                                xPrimeTwo + mode.cellSize and yPrimeTwo <= mode.mouseY \
                                <= yPrimeTwo + mode.cellSize):
                                lstOrientations = mode.getAllOrientations(piece)
                                if mode.clickedPiece not in lstOrientations:
                                    continue
                                mode.piecesTwo[elem] = row, col, color, piece, hasMoved, True
                                newRow = int((mode.mouseYRelease - (mode.margin//2))/mode.cellSize)
                                newCol = int((mode.mouseXRelease - (mode.margin//2))/mode.cellSize)
                                boardRow, boardCol = newRow - mode.scaleRow, newCol - mode.scaleCol
                                #The piece has to start at a corner
                                mode.isClickingNewPiece = True
                                if mode.isFirstMove(mode.board, color):
                                    if color == "PaleTurquoise1":
                                        if piece[len(piece)-1][len(piece[0])-1] != True or boardRow-r+(len(piece)-1)!=len(mode.board)-1 \
                                            or boardCol-c+len(piece[0])-1 != len(mode.board[0])-1:           
                                            return
                                        else: 
                                            mode.piecesTwo[elem]= newRow, newCol, color, piece, True, False
                                            mode.updateBoard(mode.board,boardRow-r, boardCol-c, mode.clickedPiece, "PaleTurquoise1")
                                            mode.turn += 1
                                            mode.resetClickedPiece() 
                                else:
                                    mode.placePiece(boardRow, boardCol, newRow, newCol, r, c, elem, mode.clickedPiece, color)
                                              
    def updateBoard(mode, board, row, col, piece, color):
        #THe board is updated every time a piece is placed
        for r in range(len(piece)):
            for c in range(len(piece[0])):
                if mode.isInBound(board, row + r, col + c) and piece[r][c]:
                    board[row + r][col + c] = color
        mode.player1Points = mode.score(mode.board,"RosyBrown1")
        mode.player2Points = mode.score(mode.board,"PaleTurquoise1")
        
    def isFirstMove(mode, board, color):
        #If there is no piece of that color on the board, then it's the color's
        #first move
        for r in range(len(board)):
            for c in range(len(board)):
                if board[r][c] == color: 
                    return False
        return True

    def isInBound(mode, board, row, col):
        #check if each block is in the bound
        return 0 <= row < len(board) and 0 <= col < len(board[0])

    def isLegalMove(mode, board, row, col, piece, color):
        #This checks all four directions of a piece. If that location is valid 
        # (not adjacent to the same color and in bounds), the piece can be placed. 
        # However, if there is another color on that spot, it is not a legal move. 
        directions = [(+1,0),(-1,0),(0,+1),(0,-1)]
        for r in range(len(piece)):
            for c in range(len(piece[0])):
                if piece[r][c]:
                    for horDir, verDir in directions:
                        if not mode.isInBound(board,(row+r+verDir),(col+c+horDir)):
                            continue
                        if board[row+r+verDir][col+c+horDir] == color:
                            return False
        return True

    def hasDiagonal(mode, board, row, col, piece, color):
        #Checks if the new piece is connected to the previous pieces (checks all
        # four corners)
        directions = [(-1,-1),(-1,+1),(+1,-1),(+1,+1)]
        for r in range(len(piece)):
            for c in range(len(piece[0])):
                if piece[r][c]:
                    for horDir, verDir in directions:
                        if not mode.isInBound(board,(row+r+verDir),(col+c+horDir)):
                            pass
                        elif board[row+r+verDir][col+c+horDir] == color:
                            return True
        return False

    def isPlaceable(mode, board, newRow, newCol, piece):
        #The moved piece is within the bounds
        for r in range(len(piece)):
            for c in range(len(piece[0])):
                if piece[r][c]:
                    if newRow + r < 0 or newRow + r >= len(board) or \
                        newCol + c < 0 or newCol + c >= len(board[0]):
                        return False
                    if not board[newRow + r][newCol + c] == "gray86":
                        return False
        return True

    def placePiece(mode, boardRow, boardCol, newRow, newCol, r, c, elem, piece, color):
        #Checks all the conditions that make a move legal. If it is legal, the
        #move is taken.
        if mode.isPlaceable(mode.board,boardRow-r,boardCol-c,piece) and\
                mode.isLegalMove(mode.board,boardRow-r,boardCol-c,piece,color)\
                and mode.hasDiagonal(mode.board,boardRow-r,boardCol-c,piece,color):
            if mode.turn % 2 == 0:
                mode.pieces[elem] = newRow, newCol, color, piece, True, False
            elif mode.turn % 2 == 1:
                mode.piecesTwo[elem] = newRow-r, newCol-c, color, piece, True, False
            mode.updateBoard(mode.board, boardRow-r, boardCol-c, piece, color) 
            mode.turn += 1
            mode.resetClickedPiece() 
            
    def flipUpDown(mode, piece):
        copyPiece = [([False]*len(piece[0])) for r in range(len(piece))]
        for r in range(len(piece)):
            for c in range(len(piece[0])):
                flipRow = abs(len(piece)-1-r)
                copyPiece[flipRow][c] = piece[r][c]
        return copyPiece
      
    def flipSideways(mode, piece):
        copyPiece = [([False]*len(piece[0])) for r in range(len(piece))]
        for r in range(len(piece)):
            for c in range(len(piece[0])):
                flipCol = abs(len(piece[0])-1-c)
                copyPiece[r][flipCol] = piece[r][c]
        return copyPiece

    def rotate(mode, piece):
        copyPiece = [([False]*len(piece)) for r in range(len(piece[0]))]
        for r in range(len(copyPiece[0])):
            for c in range(len(copyPiece)):
                copyPiece[c][r] = piece[r][len(piece[0])-c-1]
        return copyPiece

    def score(mode, board, color):
        score = 0
        for r in range(len(board)):
            for c in range(len(board[0])):
                if board[r][c] == color:
                    score += 1
        return score

    def updatePieceMoved(mode, pieceDict, pieceCopy):
        for elem in pieceDict:
            row, col, color, shape, hasMoved, isClicked = pieceDict[elem]
            if len(shape) != len(pieceCopy) or len(shape[0]) != len(pieceCopy[0]): 
                continue
            isSameShape = True
            for i in range(len(shape)):
                for j in range(len(shape[0])):
                    if shape[i][j] != pieceCopy[i][j]:
                        isSameShape = False
            if(isSameShape):
                pieceDict[elem] = row, col, color, shape, True
                break

    def possibleMovesP1(mode, board,piece, color):
        L = []
        for elem in piece:
            row, col, color, shape, hasMoved, isClicked = piece[elem]
            if hasMoved: 
                continue
            else: 
                lstPiece = mode.getAllOrientations(shape)
                for shapeCopy in lstPiece:
                    for r in range(len(board)):
                        for c in range(len(board[r])):
                            if mode.isFirstMove(board, color):
                                if shapeCopy[0][0] and r == 0 and c == 0:
                                    L += [(r,c,shapeCopy,shape)]
                            elif mode.isPlaceable(board, r,c, shapeCopy) and \
                                mode.isLegalMove(board,r, c, shapeCopy, color) and \
                                mode.hasDiagonal(board,r,c, shapeCopy, color):
                                L += [(r,c,shapeCopy,shape)]
        return L

    def possibleMovesP2(mode,board,piece, color):
        L = []
        for elem in piece:
            row, col, color, shape, hasMoved, isClicked = piece[elem]
            if hasMoved: 
                continue
            else: 
                lstPiece = mode.getAllOrientations(shape)
                for shapeCopy in lstPiece:
                    for r in range(len(board)):
                        for c in range(len(board[r])):
                            if mode.isFirstMove(board, color):
                                if shapeCopy[len(shapeCopy)-1][len(shapeCopy[0])-1] and \
                                    r+len(shapeCopy) == len(board) and \
                                    c+len(shapeCopy[0])== len(board[0]):
                                    L += [(r,c,shapeCopy,shape)]
                            elif mode.isPlaceable(board, r,c, shapeCopy) and \
                                    mode.isLegalMove(board,r, c, shapeCopy, color) and \
                                    mode.hasDiagonal(board,r,c, shapeCopy, color):
                                L += [(r,c,shapeCopy,shape)]
        return L  

    def resetClickedPiece(mode):
        mode.clickedPiece = []
        mode.isClickingNewPiece = False

class PlayBlokusEasyAI(PlayBlokus):
    def appStarted(mode):
        super().appStarted()
        mode.prevPage = "    AI"

    def mousePressed(mode, event):
        mode.isMousePressed = True
        mode.mouseX, mode.mouseY = event.x, event.y
        #If the back button is clicked, it will take the player back to the previous page
        if mode.height//100 <= event.x <= mode.height//100 + mode.height//100 * 9 and \
            -mode.height//200 + mode.height - mode.height //100 * 9 <= event.y <= -mode.height//200 + mode.height:
            mode.app.setActiveMode(mode.app.ai)
        #If the question mark is clicked, it will take the player to the help page
        elif mode.height//34 <= event.y <= mode.height//17 and \
            mode.width - mode.height//20 - 10 <= event.x <= mode.width - mode.height//20 + 10:
                mode.app.setActiveMode(mode.app.helpMode)
        if not mode.isGameOver:
            mode.isMousePressed = True
            #If the lightbulb/hint photo is clicked, a hint move is played on 
            # behalf of the player.
            mode.mouseX, mode.mouseY = event.x, event.y
            hintWidth, hintHeight = mode.hint.size
            if mode.app.width - mode.app.width//8 - hintWidth//2 <= event.x <= mode.app.width - mode.app.width//8 + hintWidth//2 \
                and mode.app.height//2 - hintHeight//2 <= event.y <= mode.app.height//2 + hintHeight//2:
                if mode.turn % 2 == 0:
                    pPieces = mode.possibleMovesP1(mode.board, mode.pieces, "RosyBrown1")
                    mode.getHint(pPieces, "RosyBrown1", mode.pieces)
                    mode.aiPiece()
    
    def keyPressed(mode, event):
        if event.key == "r":
            mode.app.easyAI = PlayBlokusEasyAI()
            mode.app.setActiveMode(mode.app.easyAI)
        elif event.key == "Up":
            mode.clickedPiece = mode.flipUpDown(mode.clickedPiece)
        elif event.key == "Right":
            mode.clickedPiece = mode.flipSideways(mode.clickedPiece)
        elif event.key == "Down":
            mode.clickedPiece = mode.rotate(mode.clickedPiece)
        elif event.key == "h":
            pPieces = mode.possibleMovesP1(mode.board, mode.pieces, "RosyBrown1")
            mode.getHint(pPieces, "RosyBrown1", mode.pieces)
            mode.aiPiece()

    def isMouseTouchingPiece(mode):
        if mode.isMousePressed:
            if mode.turn % mode.players == 0: 
                mode.turnPlayer = "PINK"
                if not mode.possibleMovesP1(mode.board, mode.pieces, "RosyBrown1"):
                    print("NO MORE MOVES FOR PLAYER 1")
                    mode.player1HasMoves = False
                    mode.turn += 1
                    return
                for elem in mode.pieces:
                    row, col, color, piece, hasMoved, isClicked = mode.pieces[elem]
                    rowTemp = row + 1
                    x = mode.margin//2 + col * mode.cellSize
                    y = mode.margin//2 + rowTemp * mode.cellSize
                    xClickedPiece = mode.margin//2 + 0* mode.cellSize
                    yClickedPiece = mode.margin//2 + 12*mode.cellSize
                    lstOrientations = mode.getAllOrientations(piece)
                    if mode.clickedPiece in lstOrientations:
                        piece = mode.clickedPiece
                    for r in range(len(piece)):
                        for c in range(len(piece[r])):
                            if not piece[r][c]:
                                continue
                            else:
                                xPrime = x + c*mode.cellSize
                                yPrime = y + r*mode.cellSize
                                xPrimeTwo = xClickedPiece + c*mode.cellSize
                                yPrimeTwo = yClickedPiece + r*mode.cellSize
                            #Checks to see if the piece at the original position is moved/will be moved
                            if not hasMoved and ((xPrime <= mode.mouseX <= xPrime + mode.cellSize \
                                and yPrime <= mode.mouseY <= yPrime + mode.cellSize)):
                                mode.clickedPiece = piece
                                mode.pieces[elem] = row, col, color, piece, hasMoved, True
                                newRow = int((mode.mouseYRelease - (mode.margin//2))/mode.cellSize)
                                newCol = int((mode.mouseXRelease - (mode.margin//2))/mode.cellSize)
                                boardRow, boardCol = newRow - mode.scaleRow, newCol - mode.scaleCol
                                if mode.isFirstMove(mode.board, color):
                                    if color == "RosyBrown1":
                                        if piece[0][0] != True or boardRow - r!= 0 or boardCol - c != 0:
                                            return
                                        else: 
                                            mode.pieces[elem]= newRow, newCol, color, piece, True, False
                                            mode.updateBoard(mode.board,boardRow-r, boardCol-c, piece, "RosyBrown1")
                                            mode.turn += 1
                                            mode.resetClickedPiece()
                                            mode.aiPiece()
                                            return
                                else:
                                    if abs(mode.mouseX - mode.mouseXRelease) < mode.cellSize and \
                                        abs(mode.mouseY - mode.mouseYRelease) < mode.cellSize:
                                        pass
                                    else:
                                        mode.placePiece(boardRow, boardCol, newRow, newCol, r, c, elem, piece, color)
                                        mode.aiPiece()
                                        #mode.turn += 1
                                        return
                            #Checks to see if the clicked piece (drawn to the left of the board) can be moved 
                            elif not hasMoved and (xPrimeTwo <= mode.mouseX <= xPrimeTwo + mode.cellSize and \
                                yPrimeTwo <= mode.mouseY <= yPrimeTwo + mode.cellSize):
                                lstOrientations = mode.getAllOrientations(piece)
                                if mode.clickedPiece not in lstOrientations:
                                    continue
                                mode.pieces[elem] = row, col, color, piece, hasMoved, True
                                newRow = int((mode.mouseYRelease - (mode.margin//2))/mode.cellSize)
                                newCol = int((mode.mouseXRelease - (mode.margin//2))/mode.cellSize)
                                boardRow, boardCol = newRow - mode.scaleRow, newCol - mode.scaleCol
                                if mode.isFirstMove(mode.board, color):
                                    if color == "RosyBrown1":
                                        if piece[0][0] != True or boardRow - r!= 0 or boardCol - c != 0:
                                            return
                                        else: 
                                            mode.pieces[elem]= newRow, newCol, color, piece, True, False
                                            mode.updateBoard(mode.board, boardRow-r, boardCol-c, piece, "RosyBrown1")
                                            mode.turn += 1 
                                            mode.resetClickedPiece() 
                                            #Finds the best move for the AI
                                            mode.aiPiece()
                                            return
                                elif mode.isPlaceable(mode.board, boardRow - r, boardCol - c, piece) and \
                                mode.isLegalMove(mode.board, boardRow - r, boardCol - c, piece, color) and \
                                mode.hasDiagonal(mode.board, boardRow - r, boardCol - c, piece, color):
                                    mode.pieces[elem] =newRow,newCol,color,piece,True, False
                                    mode.updateBoard(mode.board, boardRow-r, boardCol-c, piece, "RosyBrown1") 
                                    mode.turn += 1
                                    mode.resetClickedPiece() 
                                    mode.aiPiece()
                                    return
                    
                                    
    def aiPiece(mode):
        #After generating all the possible moves, a random piece is selected
        print("AI's turn...", end = " ")
        moves = mode.possibleMovesP2(mode.board, mode.piecesTwo, "PaleTurquoise1")
        if moves == []:
            return
        move = random.choice(moves)
        print("Done!!!")
        #Updating the piece information -> piece has been moved
        rowMove, colMove, pieceCopy, shapeOrig = move
        mode.updateBoard(mode.board, rowMove, colMove, pieceCopy, "PaleTurquoise1")
        for elem in mode.piecesTwo:
            row, col, color, shape, hasMoved, isClicked = mode.piecesTwo[elem]
            if len(shape) != len(shapeOrig) or len(shape[0]) != len(shapeOrig[0]): 
                continue
            isSameShape = True
            for i in range(len(shape)):
                for j in range(len(shape[0])):
                    if shape[i][j] != shapeOrig[i][j]:
                        isSameShape = False
            if(isSameShape):
                mode.piecesTwo[elem] = rowMove, colMove, color, shapeOrig, True, False
                break
        mode.turn += 1

class PlayBlokusAI2(PlayBlokusEasyAI):
    def keyPressed(mode, event):
        if event.key == "r":
            mode.app.playAI = PlayBlokusAI2()
            mode.app.setActiveMode(mode.app.playAI)
            return
        super().keyPressed(event)

    def possibleMovesP1(mode, board,piece, color):
        L = []
        for elem in piece:
            row, col, color, shape, hasMoved, isClicked = piece[elem]
            if hasMoved: 
                continue
            else: 
                for r in range(len(board)):
                    for c in range(len(board[r])):
                        if mode.isFirstMove(board, color):
                            if shape[0][0] and r == 0 and c == 0:
                                L += [(r,c,shape,shape)]
                        elif mode.isPlaceable(board, r,c, shape) and \
                            mode.isLegalMove(board,r, c, shape, color) and \
                            mode.hasDiagonal(board,r,c, shape, color):
                            L += [(r,c,shape,shape)]
        return L
    
    def possibleMovesP2(mode,board,piece,color):
        L = []
        for elem in piece:
            row, col, color, shape, hasMoved, isClicked = piece[elem]
            if hasMoved: 
                continue
            else: 
                for r in range(len(board)):
                    for c in range(len(board[r])):
                        if mode.isFirstMove(board, color):
                            if shape[len(shape)-1][len(shape[0])-1] and \
                                r+len(shape) == len(board) and \
                                c+len(shape[0])== len(board[0]):
                                L += [(r,c,shape,shape)]
                        elif mode.isPlaceable(board, r,c, shape) and \
                                mode.isLegalMove(board,r, c, shape, color) and \
                                mode.hasDiagonal(board,r,c, shape, color):
                            L += [(r,c,shape,shape)]
        return L 

    def allPossibleMoves(mode, board, pieces, color):
        L = []
        for elem in pieces:
            row, col, color, shape, hasMoved, isClicked = pieces[elem]
            if hasMoved: 
                continue
            else: 
                lstPiece = mode.getAllOrientations(shape)
                for shapeCopy in lstPiece:
                    for r in range(len(board)):
                        for c in range(len(board[r])):
                            if mode.isPlaceable(board, r,c, shapeCopy) and \
                                    mode.isLegalMove(board,r, c, shapeCopy, color) and \
                                    mode.hasDiagonal(board,r,c, shapeCopy, color):
                                L += [(r,c,shapeCopy,shape)]
        return L  

    def aiPiece(mode):
        print("AI's turn...", end = " ")
        move, score = mode.miniMax(mode.board, mode.pieces,mode.piecesTwo, 2, "PaleTurquoise1")
        if move == None:
            rotatedMoves = mode.allPossibleMoves(mode.board, mode.piecesTwo, "PaleTurquoise1")
            if rotatedMoves == []:
                print("AI RAN OUT OF MOVES")
                mode.turn += 1
                return
            else:
                move = mode.findLargestPossiblePiece(rotatedMoves)
        print("Done!!!")
        rowMove, colMove, pieceCopy, shapeOrig = move                                            
        mode.updateBoard(mode.board, rowMove, colMove, pieceCopy, "PaleTurquoise1")
        for elem in mode.piecesTwo:
            row, col, color, shape, hasMoved, clickedPiece = mode.piecesTwo[elem]
            if len(shape) != len(pieceCopy) or len(shape[0])!= len(pieceCopy[0]): 
                continue
            isSameShape = True
            for i in range(len(shape)):
                for j in range(len(shape[0])):
                    if shape[i][j] != pieceCopy[i][j]:
                        isSameShape = False
            if(isSameShape):
                mode.piecesTwo[elem] = rowMove, colMove, color, shape, True, True
                break
        mode.turn += 1

    def miniMaxPoints(mode, board):
        #minimax is based of the AI trying to maximize its points and minimize the
        #player's points. Increased difference between the two means that the 
        #AI is more 'advantageous'
        return mode.score(board, "PaleTurquoise1") - mode.score(board, "RosyBrown1")

    def miniMax(mode,board,piece1,piece2, depth, player):
        #Inspiration from https://towardsdatascience.com/create-ai-for-your-own-board-\
        # game-from-scratch-miniMax-part-2-517e1c1e3362
        if depth == 0:
            return (None, mode.miniMaxPoints(board))
        else: 
            if player == "PaleTurquoise1":
                moves = mode.possibleMovesP2(board, piece2, "PaleTurquoise1")
                maxPoints = -math.inf
                maxMove = None
                for move in moves: 
                    board2 = copy.deepcopy(board)
                    copyPiece2 = copy.deepcopy(piece2)
                    row, col, piece, pieceC = move
                    mode.updateBoard(board2, row, col, piece, "PaleTurquoise1")
                    mode.updatePieceMoved(copyPiece2, piece)
                    a, b = mode.miniMax(board2,piece1,copyPiece2, depth -1, "RosyBrown1")
                    if b > maxPoints: 
                        maxPoints = b
                        maxMove = move
                return maxMove, maxPoints
            elif player == "RosyBrown1":
                moves = mode.possibleMovesP1(board,piece1, player)
                minPoints = math.inf
                minMove = None                
                for move in moves:
                    board1 = copy.deepcopy(board)
                    copyPiece1 = copy.deepcopy(piece1)
                    row, col, piece, pieceC = move
                    mode.updateBoard(board1, row, col, piece, "RosyBrown1")
                    mode.updatePieceMoved(copyPiece1, piece)
                    a, b = mode.miniMax(board1,copyPiece1,piece2, depth - 1, "PaleTurquoise1")
                    if b < minPoints:
                        minPoints = b
                        minMove = move
                return minMove, minPoints

class PlayBlokusAIABP2(PlayBlokusAI2):
    def mousePressed(mode, event):
        super().mousePressed(event)

    def keyPressed(mode, event):
        if event.key == "r":
            mode.app.playAIABP = PlayBlokusAIABP2()
            mode.app.setActiveMode(mode.app.playAIABP)
            return
        super().keyPressed(event)

    def aiPiece(mode):
        print("AI's turn...", end = " ")
        move, score = mode.miniMax(mode.board, mode.pieces,mode.piecesTwo,2,"PaleTurquoise1",-math.inf, math.inf)
        if move == None:
            rotatedMoves = mode.allPossibleMoves(mode.board, mode.piecesTwo, "PaleTurquoise1")
            if rotatedMoves == []:
                print("AI RAN OUT OF MOVES")
                mode.turn += 1
                return
            else:
                move = mode.findLargestPossiblePiece(rotatedMoves)
                print('added', mode.turn)
        print("Done!!!")
        rowMove, colMove, pieceCopy, pieceOrig = move                                            
        mode.updateBoard(mode.board, rowMove, colMove, pieceCopy, "PaleTurquoise1")
        for elem in mode.piecesTwo:
            row, col, color, shape, hasMoved, clickedPiece = mode.piecesTwo[elem]
            if len(shape) != len(pieceCopy) or len(shape[0])!= len(pieceCopy[0]): 
                continue
            isSameShape = True
            for i in range(len(shape)):
                for j in range(len(shape[0])):
                    if shape[i][j] != pieceCopy[i][j]:
                        isSameShape = False
            if(isSameShape):
                mode.piecesTwo[elem] = rowMove, colMove, color, shape, True, True
                break
        mode.turn += 1
        print('added', mode.turn)

    def miniMax(mode,board,piece1,piece2, depth, player, alpha, beta):
        #Inspiration from https://towardsdatascience.com/create-ai-for-your-own-board-\
        # game-from-scratch-miniMax-part-2-517e1c1e3362
        if depth == 0:
            return (None, mode.miniMaxPointsAB(board))
        else: 
            if player == "PaleTurquoise1":
                moves = mode.possibleMovesP2(board,piece2, "PaleTurquoise1")
                maxPoints = -math.inf
                maxMove = None
                for move in moves: 
                    board2 = copy.deepcopy(board)
                    copyPiece2 = copy.deepcopy(piece2)
                    row, col, piece, pieceC = move
                    mode.updateBoard(board2, row, col, piece, "PaleTurquoise1")
                    mode.updatePieceMoved(copyPiece2, piece)
                    a, b = mode.miniMax(board2,piece1,copyPiece2, depth -1, "RosyBrown1", alpha, beta)
                    if b > maxPoints: 
                        maxPoints = b
                        maxMove = move
                    if maxPoints >= beta:
                        return maxMove, maxPoints
                    else:
                        alpha = max(alpha, maxPoints)
                return maxMove, maxPoints
            elif player == "RosyBrown1":
                moves = mode.possibleMovesP1(board,piece1, player)
                minPoints = math.inf
                minMove = None                
                for move in moves:
                    board1 = copy.deepcopy(board)
                    copyPiece1 = copy.deepcopy(piece1)
                    row, col, piece, pieceC = move
                    mode.updateBoard(board1, row, col, piece, "RosyBrown1")
                    mode.updatePieceMoved(copyPiece1, piece)
                    a, b = mode.miniMax(board1,copyPiece1,piece2, depth - 1, "PaleTurquoise1", alpha, beta)
                    if b < minPoints:
                        minPoints = b
                        minMove = move
                    if minPoints <= alpha:
                        return minMove, minPoints
                    else:
                        beta = min(beta, minPoints)
                return minMove, minPoints
    
    def scoreAB(mode, board, color):
        #ALPHA BETA SCORE based on the table in heuristics
        #The AI will try to place the pieces in the most advantageous spots
        score = 0
        if color == "PaleTurquoise1":
            scoreBoard = Heuristics.pieceTableAI
        elif color == "RosyBrown1":
            scoreBoard = Heuristics.pieceTablePlayer
        for r in range(len(board)):
            for c in range(len(board[0])):
                if board[r][c] == color:
                    score += scoreBoard[r][c]
        return score

    def miniMaxPointsAB(mode, board):
        #Difference between the scores based on the heuristics table
        return mode.scoreAB(board, "PaleTurquoise1") - mode.scoreAB(board, "RosyBrown1")

class PlayBlokus4(PlayBlokus):
    def appStarted(mode):
        super().appStarted()
        mode.piecesThree = mode.createPieces("PaleGreen1")
        mode.piecesFour = mode.createPieces("LightGoldenrod1")
        mode.prevPage = "multiplayer"
        mode.player3Points = 0
        mode.player4Points = 0
        mode.player3HasMoves = True
        mode.player4HasMoves = True
        mode.players = 4 

    def gameDimensions(mode): 
        rows, cols, cellSize, margin, scaleRow, scaleCol = 20, 20, 15, 200, 7, 7
        rowAdjustment, players = 32, 4
        return (rows, cols, cellSize, margin, scaleRow, scaleCol, rowAdjustment, players)
    
    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "antique white")
        mode.drawBoard(canvas)
        mode.drawPieces(canvas)
        mode.drawHelpButton(canvas)
        mode.drawTurn(canvas)
        if mode.turn % mode.players < 2 and (mode.turn % mode.players) % 2 == 0:
            color = "RosyBrown1"
        elif mode.turn % mode.players < 2 and (mode.turn % mode.players) % 2 == 1:
            color = "PaleTurquoise1"
        elif mode.turn % mode.players == 0:
            color = "PaleGreen1"
        else:
            color = "LightGoldenrod1"
        mode.drawClickedPiece(canvas, color)
        mode.drawPrevScreen(canvas)
        mode.drawScore(canvas)
        canvas.create_image(mode.app.width - mode.app.width//8, mode.app.height//2, image = ImageTk.PhotoImage(mode.hint))
        mode.drawHint(canvas)
        mode.drawNoMoreMove(canvas)
        mode.drawGameOver(canvas)

    def drawGameOver(mode, canvas):
        if mode.isGameOver:
            font = f"helvetica {mode.app.width//20} bold"
            canvas.create_rectangle(mode.app.width//2 - mode.app.width//5, mode.app.height//3 - mode.app.height//5, mode.app.width//2 +  mode.app.width//5, mode.app.height//4, fill = "salmon")
            canvas.create_text(mode.app.width//2, mode.app.height//5, text = "GAME OVER", fill = "BLACK", font= font)
            playerScores = set([(mode.player1Points,"Player 1"),(mode.player2Points,"Player 2"),
            (mode.player3Points,"Player 3"), (mode.player4Points,"Player 4")])
            highestScore = sorted(playerScores, reverse = True)
            s = "\n\n"
            for elem in highestScore:
                sc, pl = elem
                s = s + "      " + pl + ": "+ str(sc) + "\n"
            text = s + "\n  Press r to restart"
            canvas.create_text(mode.app.width//2, mode.app.height//2, text = text, fill = "black", font = font)
    
    def keyPressed(mode, event):
        if event.key == "r":
            mode.app.playLocal4 = PlayBlokus4()
            mode.app.setActiveMode(mode.app.playLocal4)
        elif event.key == "Up":
            mode.clickedPiece = mode.flipUpDown(mode.clickedPiece)
        elif event.key == "Right":
            mode.clickedPiece = mode.flipSideways(mode.clickedPiece)
        elif event.key == "Down":
            mode.clickedPiece = mode.rotate(mode.clickedPiece)
        #Get hints for the player
        elif event.key == "h":
            if mode.turn % mode.players < 2 and (mode.turn % mode.players) % 2 == 0:
                pieces = mode.possibleMovesP1(mode.board, mode.pieces, "RosyBrown1")
                if pieces == []:
                    mode.turn += 1
                    return
                piece = mode.findLargestPossiblePiece(pieces)
                row, col, hintPiece, origPiece = piece
                mode.updateBoard(mode.board, row, col, hintPiece, "RosyBrown1")
                for elem in mode.pieces:
                    row, col, color, shape, hasMoved, isClicked = mode.pieces[elem]
                    if shape == origPiece:
                        mode.pieces[elem] = row, col, color, shape, True, isClicked
                        continue
                mode.turn += 1
            elif mode.turn % mode.players < 2 and (mode.turn % mode.players) % 2 == 1:
                pieces = mode.possibleMovesP2(mode.board, mode.piecesTwo, "PaleTurquoise1")
                if pieces == []:
                    mode.turn += 1
                    return
                piece = mode.findLargestPossiblePiece(pieces)
                row, col, hintPiece, origPiece = piece
                mode.updateBoard(mode.board, row, col, hintPiece, "PaleTurquoise1")
                for elem in mode.piecesTwo:
                    row, col, color, shape, hasMoved, isClicked = mode.piecesTwo[elem]
                    if shape == origPiece:
                        mode.piecesTwo[elem] = row, col, color, shape, True, isClicked
                        continue
                mode.turn += 1
            elif (mode.turn % mode.players) % 2 == 0:
                pieces = mode.possibleMovesP3(mode.board, mode.piecesThree, "PaleGreen1")
                if pieces == []:
                    mode.turn += 1
                    return
                piece = mode.findLargestPossiblePiece(pieces)
                row, col, hintPiece, origPiece = piece
                mode.updateBoard(mode.board, row, col, hintPiece, "PaleGreen1")
                for elem in mode.piecesThree:
                    row, col, color, shape, hasMoved, isClicked = mode.piecesThree[elem]
                    if shape == origPiece:
                        mode.piecesThree[elem] = row, col, color, shape, True, isClicked
                        continue
                mode.turn += 1
            else:
                pieces = mode.possibleMovesP4(mode.board, mode.piecesFour, "LightGoldenrod1")
                if pieces == []:
                    mode.turn += 1
                    return
                piece = mode.findLargestPossiblePiece(pieces)
                row, col, hintPiece, origPiece = piece
                mode.updateBoard(mode.board, row, col, hintPiece, "LightGoldenrod1")
                for elem in mode.piecesFour:
                    row, col, color, shape, hasMoved, isClicked = mode.piecesFour[elem]
                    if shape == origPiece:
                        mode.piecesFour[elem] = row, col, color, shape, True, isClicked
                        continue
                mode.turn += 1

    def mousePressed(mode, event):
        #Clicking the hint button
        hintWidth, hintHeight = mode.hint.size
        if mode.app.width - mode.app.width//8 - hintWidth//2 <= event.x <= mode.app.width - mode.app.width//8 + hintWidth//2 \
            and mode.app.height//2 - hintHeight//2 <= event.y <= mode.app.height//2 + hintHeight//2:
            if mode.turn % mode.players < 2 and (mode.turn % mode.players) % 2 == 0:  
                pPieces = mode.possibleMovesP1(mode.board, mode.pieces, "RosyBrown1")
                mode.getHint(pPieces, "RosyBrown1", mode.pieces)
            elif mode.turn % mode.players < 2 and (mode.turn % mode.players) % 2 == 1:
                pPieces = mode.possibleMovesP2(mode.board, mode.piecesTwo, "PaleTurquoise1")
                mode.getHint(pPieces, "PaleTurquoise1", mode.piecesTwo)
            elif mode.turn % mode.players % 2 == 0:
                pPieces = mode.possibleMovesP3(mode.board, mode.piecesThree, "PaleGreen1")
                mode.getHint(pPieces, "PaleGreen1", mode.piecesThree)
            else:
                pPieces = mode.possibleMovesP4(mode.board, mode.piecesFour, "LightGoldenrod1")
                mode.getHint(pPieces, "LightGoldenrod1", mode.piecesFour)
        #Clicking the help button
        elif mode.height//34 <= event.y <= mode.height//17 and \
            mode.width - mode.height//20 - 10 <= event.x <= mode.width - mode.height//20 + 10:
            mode.app.setActiveMode(mode.app.helpMode)
        super().mousePressed(event)

    def createPieces(mode, color):
        #row, col, cellSize, margin, lst, hasMoved
        pieces = dict()
        p1 = [[True]]
        optionsP1 = []
        pieces[1] = (35, 16, color, p1, False, False)
        p2 = [[True, False],[True, False]]
        pieces[2] = (34, 9, color, p2, False, False)
        p3 = [[True,True,True]]
        pieces[3] = (34, 23, color, p3, False, False)
        p4 = [[True,True,True,True]]
        pieces[4] = (35, 0, color, p4, False, False)
        p5 = [[True,True,True,True,True]]
        pieces[5] = (29, 0, color, p5, False, False)
        p6 = [[True,False],
              [True,True]]
        pieces[6] = (34, 21, color, p6, False, False)
        p7 = [[True,False,False],
              [True,True,True]]
        pieces[7] = (34, 5, color, p7, False, False)
        p8 = [[True,True,True,True],
              [True,False,False,False]]
        pieces[8] = (29, 22, color, p8, False, False)
        p9 = [[True,False,False],
              [True,False,False],
              [True,True,True]]
        pieces[9] = (29, 11, color, p9, False, False)
        p10 = [[True,False,False],
               [True,True,False],
               [False,True,True]]
        pieces[10] = (31, 9, color, p10, False, False)
        p11 = [[False,True,False],
               [True,True,True]]
        pieces[11] = (34, 11, color, p11, False, False)
        p12 = [[True,True,True],
               [False,True,False],
               [False,True,False]]
        pieces[12] = (29, 14, color, p12, False, False)
        p13 = [[False,True,False,False],
               [True,True,True,True]]
        pieces[13] = (31, 0, color, p13, False, False)
        p14 = [[True, False],
               [True, True],
               [False, True]]
        pieces[14] = (31, 25, color, p14, False, False)
        p15 = [[False,True,True,True],
               [True,True,False,False]]
        pieces[15] = (29, 6, color, p15, False, False)
        p16 = [[True,False,False],
               [True,True,True],
               [False,False,True]]
        pieces[16] = (31, 5, color, p16, False, False)
        p17 = [[True,True],
               [True,True]]
        pieces[17] = (34, 18, color, p17, False, False)
        p18 = [[True,False],
               [True,True],
               [True,True]]
        pieces[18] = (32, 14, color, p18, False, False)
        p19 = [[True,True,True],
               [True,False,True]]
        pieces[19] = (29, 18, color, p19, False, False)
        p20 = [[False,False,True],
               [True,True,True],
               [False,True,False]]
        pieces[20] = (31, 21, color, p20, False, False)
        p21 = [[False,True,False],
               [True,True,True],
               [False,True,False]]
        pieces[21] = (31, 16, color, p21, False, False)
        return pieces
    
    def isMouseTouchingPiece(mode):
        if mode.isMousePressed:
            #PLAYER 1's TURN
            if mode.turn % mode.players < 2 and (mode.turn % mode.players) % 2 == 0: 
                if not mode.possibleMovesP1(mode.board, mode.pieces, "RosyBrown1"):
                    mode.player1HasMoves = False
                    mode.turn += 1
                    return
                for elem in mode.pieces:
                    row, col, color, piece, hasMoved, isClicked = mode.pieces[elem]
                    tempCol = col + 3
                    x = mode.margin//2 + tempCol * mode.cellSize
                    y = mode.margin//2 + row * mode.cellSize
                    for r in range(len(piece)):
                        for c in range(len(piece[r])):
                            if not piece[r][c]:
                                continue
                            else:
                                xPrime = x + c*mode.cellSize
                                yPrime = y + r*mode.cellSize
                            if not hasMoved and xPrime <= mode.mouseX <= \
                                xPrime + mode.cellSize and yPrime <= mode.mouseY \
                                <= yPrime + mode.cellSize:
                                newRow = int((mode.mouseYRelease - (mode.margin//2))/mode.cellSize)
                                newCol = int((mode.mouseXRelease - (mode.margin//2))/mode.cellSize)
                                boardRow, boardCol = newRow - mode.scaleRow, newCol - mode.scaleCol
                                #has to start at a corner
                                if mode.isFirstMove(mode.board, color):
                                    if color == "RosyBrown1":
                                        if piece[0][0] != True or boardRow - r!= 0 or boardCol - c != 0:
                                            return
                                        else: 
                                            mode.pieces[elem]= newRow, newCol, color, piece, True, False
                                            mode.updateBoard(mode.board,boardRow-r, boardCol-c, piece, "RosyBrown1")
                                            mode.turn += 1
                                else:
                                    mode.placePiece(boardRow, boardCol, newRow, newCol, r, c, elem, piece, color)
            #Player 2's Turn
            elif mode.turn % mode.players < 2 and (mode.turn % mode.players) % 2 == 1:
                if not mode.possibleMovesP2(mode.board, mode.pieces, "PaleTurquoise1"):
                    mode.player2HasMoves = False
                    mode.turn += 1
                    return
                for elem in mode.piecesTwo:
                    row, col, color, piece, hasMoved, isClicked = mode.piecesTwo[elem]
                    row -= mode.rowAdjustment
                    tempCol = col + 3
                    x = mode.margin//2 + tempCol * mode.cellSize
                    y = mode.margin//2 + row * mode.cellSize
                    for r in range(len(piece)):
                        for c in range(len(piece[r])):
                            if not piece[r][c]:
                                continue
                            else:
                                xPrime = x + c*mode.cellSize
                                yPrime = y + r*mode.cellSize
                            if not hasMoved and xPrime <= mode.mouseX <= xPrime + \
                                mode.cellSize and yPrime <= mode.mouseY <= yPrime + mode.cellSize:
                                newRow = int((mode.mouseYRelease - (mode.margin//2))/mode.cellSize)
                                newCol = int((mode.mouseXRelease - (mode.margin//2))/mode.cellSize)
                                boardRow, boardCol = newRow - mode.scaleRow, newCol - mode.scaleCol
                                
                        #has to start at the corner
                        ##########################
                                if mode.isFirstMove(mode.board, color):
                                    if color == "PaleTurquoise1":
                                        if piece[0][len(piece[0])-1] != True or boardRow - r != 0 \
                                            or boardCol-c+len(piece[0])-1 != len(mode.board[0])-1:
                                            return
                                        else: 
                                            mode.piecesTwo[elem]= newRow, newCol, color, piece, True, False
                                            mode.updateBoard(mode.board, boardRow-r, boardCol-c, piece, "PaleTurquoise1")
                                            mode.turn += 1
                                else:
                                    mode.placePiece(boardRow, boardCol, newRow, newCol, r, c, elem, piece, color)
            #Player 3's turn
            elif (mode.turn % mode.players) % 2 == 0: 
                if not mode.possibleMovesP3(mode.board, mode.piecesThree, "PaleGreen1"):
                    mode.player3HasMoves = False
                    mode.turn += 1
                    return
                for elem in mode.piecesThree:
                    row, col, color, piece, hasMoved, isClicked = mode.piecesThree[elem]
                    tempCol = col + 3
                    x = mode.margin//2 + tempCol * mode.cellSize
                    y = mode.margin//2 + row * mode.cellSize
                    for r in range(len(piece)):
                        for c in range(len(piece[r])):
                            if not piece[r][c]:
                                continue
                            else:
                                xPrime = x + c*mode.cellSize
                                yPrime = y + r*mode.cellSize
                            if not hasMoved and xPrime <= mode.mouseX <= \
                                xPrime + mode.cellSize and yPrime <= mode.mouseY \
                                <= yPrime + mode.cellSize:
                                newRow = int((mode.mouseYRelease - (mode.margin//2))/mode.cellSize)
                                newCol = int((mode.mouseXRelease - (mode.margin//2))/mode.cellSize)
                                boardRow, boardCol = newRow - mode.scaleRow, newCol - mode.scaleCol
                                #has to start at a corner
                                if mode.isFirstMove(mode.board, color):
                                    if color == "PaleGreen1":
                                        if piece[len(piece)-1][len(piece[0])-1] != True or boardRow-r+(len(piece)-1)!=len(mode.board)-1 \
                                            or boardCol-c+len(piece[0])-1 != len(mode.board[0])-1:
                                            return
                                        else: 
                                            mode.piecesThree[elem]= newRow, newCol, color, piece, True, False
                                            mode.updateBoard(mode.board,boardRow-r, boardCol-c, piece, "PaleGreen1")
                                            mode.turn += 1
                                else:
                                    mode.placePiece(boardRow, boardCol, newRow, newCol, r, c, elem, piece, color)
            #Player 4's turn
            elif (mode.turn % mode.players) % 2 == 1:
                if not mode.possibleMovesP4(mode.board, mode.piecesFour, "LightGoldenrod1"):
                    mode.player4HasMoves = False
                    mode.turn += 1
                    return
                for elem in mode.piecesFour:
                    row, col, color, piece, hasMoved, isClicked = mode.piecesFour[elem]
                    row -= mode.rowAdjustment
                    tempCol = col + 3
                    x = mode.margin//2 + tempCol * mode.cellSize
                    y = mode.margin//2 + row * mode.cellSize
                    for r in range(len(piece)):
                        for c in range(len(piece[r])):
                            if not piece[r][c]:
                                continue
                            else:
                                xPrime = x + c*mode.cellSize
                                yPrime = y + r*mode.cellSize
                            if not hasMoved and xPrime <= mode.mouseX <= xPrime + \
                                mode.cellSize and yPrime <= mode.mouseY <= yPrime + mode.cellSize:
                                newRow = int((mode.mouseYRelease - (mode.margin//2))/mode.cellSize)
                                newCol = int((mode.mouseXRelease - (mode.margin//2))/mode.cellSize)
                                boardRow, boardCol = newRow - mode.scaleRow, newCol - mode.scaleCol
                                #has to start at a corner
                                if mode.isFirstMove(mode.board, color):
                                    if color == "LightGoldenrod1":
                                        if piece[len(piece)-1][0] != True or boardRow-r+(len(piece)-1)!=len(mode.board)-1 \
                                            or boardCol - c != 0:
                                            return
                                        else: 
                                            mode.piecesFour[elem]= newRow, newCol, color, piece, True, False
                                            mode.updateBoard(mode.board, boardRow-r, boardCol-c, piece, "LightGoldenrod1")
                                            mode.turn += 1
                                else:
                                    mode.placePiece(boardRow, boardCol, newRow, newCol, r, c, elem, piece, color)        
    
    def placePiece(mode, boardRow, boardCol, newRow, newCol, r, c, elem, piece, color):
        if mode.isPlaceable(mode.board,boardRow-r,boardCol-c,piece) and\
                mode.isLegalMove(mode.board,boardRow-r,boardCol-c,piece,color)\
                and mode.hasDiagonal(mode.board,boardRow-r,boardCol-c,piece,color):
            if mode.turn % mode.players < 2 and (mode.turn % mode.players) % 2 == 0:
                mode.pieces[elem] = newRow, newCol, color, piece, True, False
            elif mode.turn % mode.players < 2 and (mode.turn % mode.players) % 2 == 1:
                mode.piecesTwo[elem] = newRow-r, newCol-c, color, piece, True, False
            elif mode.turn % 2 == 0:
                mode.piecesThree[elem] = newRow, newCol, color, piece, True, False
            elif mode.turn % 2 == 1:
                mode.piecesFour[elem] = newRow-r, newCol-c, color, piece, True, False
            mode.updateBoard(mode.board, boardRow-r, boardCol-c, piece, color) 
            mode.turn += 1
            return 

    def drawCellPieces(mode, canvas, row, col, color):
        canvas.create_rectangle(mode.margin//2 + (col + 3)*mode.cellSize,
            mode.margin//2 + (row)*mode.cellSize,
            mode.margin//2 + (col + 1 + 3)*mode.cellSize,
            mode.margin//2 + (row + 1)*mode.cellSize, fill = color, width = 2)  

    def drawScore(mode, canvas):
        canvas.create_text(mode.app.width - mode.app.width //6, mode.app.height//5*2 - 50, text = "SCORE", 
            font = "helvetica 20 bold")
        canvas.create_text(mode.app.width - mode.app.width //6, mode.app.height//5*2, text = f"""
        PLAYER ONE: {mode.player1Points}
        PLAYER TWO: {mode.player2Points}
        PLAYER THREE: {mode.player3Points}
        PLAYER FOUR: {mode.player4Points}
        """)   
    
    def possibleMovesP2(mode, board, piece, color):
        L = []
        for elem in piece:
            row, col, color, shape, hasMoved, isClicked = piece[elem]
            if hasMoved: 
                continue
            else:
                lstPiece = mode.getAllOrientations(shape)
                for shapeCopy in lstPiece: 
                    for r in range(len(board)):
                        for c in range(len(board[r])):
                            if mode.isFirstMove(board, color):
                                if shape[0][len(shape[0])-1] and r == 0 and c+len(shape)== len(board[0]):
                                    L += [(r,c,shapeCopy,shape)]
                            elif mode.isPlaceable(board, r,c, shapeCopy) and mode.isLegalMove(board,r, c, shapeCopy, color) and \
                            mode.hasDiagonal(board,r,c, shapeCopy, color):
                                L += [(r,c,shapeCopy,shape)]
        return L

    def possibleMovesP3(mode, board,piece, color):
        L = []
        for elem in piece:
            row, col, color, shape, hasMoved, isClicked = piece[elem]
            if hasMoved: 
                continue
            else: 
                lstPiece = mode.getAllOrientations(shape)
                for shapeCopy in lstPiece: 
                    for r in range(len(board)):
                        for c in range(len(board[r])):
                            if mode.isFirstMove(board, color):
                                if shapeCopy[len(shapeCopy)-1][len(shapeCopy[0])-1] and r+len(shapeCopy) == len(board) and \
                                    c+len(shapeCopy[0])== len(board[0]):
                                    L += [(r,c,shapeCopy,shape)]
                            elif mode.isPlaceable(board, r, c, shapeCopy) and \
                                mode.isLegalMove(board,r, c, shapeCopy, color) and \
                                mode.hasDiagonal(board, r, c, shapeCopy, color):
                                L += [(r,c,shapeCopy,shape)]
        return L

    def possibleMovesP4(mode, board,piece, color):
        L = []
        for elem in piece:
            row, col, color, shape, hasMoved, isClicked = piece[elem]
            if hasMoved: 
                continue
            else:
                lstPiece = mode.getAllOrientations(shape)
                for shapeCopy in lstPiece:  
                    for r in range(len(board)):
                        for c in range(len(board[r])):
                            if mode.isFirstMove(board, color):
                                if shapeCopy[len(shapeCopy)-1][0] and r+len(shapeCopy) == len(board) and c == 0:
                                    L += [(r,c,shapeCopy,shape)]
                            elif mode.isPlaceable(board, r, c, shapeCopy) and \
                                    mode.isLegalMove(board, r, c, shapeCopy, color) and \
                                    mode.hasDiagonal(board,r, c, shapeCopy, color):
                                L += [(r,c,shapeCopy,shape)]
        return L  

    def drawPieces(mode, canvas):
        if mode.turn % mode.players < 2:
            super().drawPieces(canvas)
        else: 
           mode.drawPieceByColor(canvas, mode.piecesThree, 0)
           mode.drawPieceByColor(canvas,mode.piecesFour, mode.rowAdjustment) 

    def mouseReleased(mode, event):
        mode.mouseXRelease, mode.mouseYRelease = event.x, event.y
        mode.isMouseTouchingPiece()
        mode.isMousePressed = False
        if not mode.possibleMovesP1(mode.board, mode.pieces, "RosyBrown1") and \
            not mode.possibleMovesP2(mode.board, mode.piecesTwo, "PaleTurquoise1") and \
            not mode.possibleMovesP3(mode.board, mode.piecesThree, "PaleGreen1") and \
            not mode.possibleMovesP4(mode.board, mode.piecesFour, "LightGoldenrod1"):
            mode.isGameOver = True
            return

        if mode.turn % mode.players < 2 and (mode.turn % mode.players) % 2 == 0:
            if not mode.possibleMovesP1(mode.board, mode.pieces, "RosyBrown1"):
                mode.player1HasMoves = False
                print("NO MORE MOVES FOR PLAYER 1")
        elif mode.turn % mode.players % 2 == 0:
            if not mode.possibleMovesP3(mode.board, mode.piecesThree, "PaleGreen1"):
                mode.player3HasMoves = False
                print("NO MORE MOVES FOR PLAYER 3")
        if mode.turn % mode.players < 2 and (mode.turn%mode.players) % 2 == 1:
            if not mode.possibleMovesP2(mode.board, mode.piecesTwo, "PaleTurquoise1"):
                mode.player2HasMoves = False
                print("NO MORE MOVES FOR PLAYER 2")
        else:
            if not mode.possibleMovesP4(mode.board, mode.piecesFour, "LightGoldenrod1"):
                mode.player4HasMoves = False
                print("NO MORE MOVES FOR PLAYER 4")

    def checkGameStatus(mode):
        if not mode.possibleMovesP1(mode.board, mode.pieces, "RosyBrown1") and \
            not mode.possibleMovesP2(mode.board, mode.piecesTwo, "PaleTurquoise1") and\
            not mode.possibleMovesP3(mode.board, mode.piecesThree, "PaleGreen1") and \
            not mode.possibleMovesP4(mode.board, mode.piecesFour, "LightGoldenrod1"):
            mode.isGameOver = True
            return
    
    def updateBoard(mode, board, row, col, piece, color):
        super().updateBoard(board, row, col, piece, color)
        mode.player3Points = mode.score(mode.board,"PaleGreen1")
        mode.player4Points = mode.score(mode.board,"LightGoldenrod1")
    
    def drawNoMoreMove(mode, canvas): 
        if mode.turn % mode.players < 2:
            if not mode.player1HasMoves:
                canvas.create_text(mode.app.width//2 + 10, mode.app.height//2 + mode.app.height//5 + 35, 
                text = "NO MORE MOVES FOR PLAYER 1")
            if not mode.player2HasMoves:
                canvas.create_text(mode.app.width//2 + 10, mode.app.height//2 - mode.app.height//5 - 15, 
                text = f"NO MORE MOVES FOR PLAYER 2")
        else:
            if not mode.player3HasMoves:
                canvas.create_text(mode.app.width//2 + 10, mode.app.height//2 + mode.app.height//5 + 35, 
                text = "NO MORE MOVES FOR PLAYER 3")
            if not mode.player4HasMoves:
                canvas.create_text(mode.app.width//2 + 10, mode.app.height//2 - mode.app.height//5 - 15, 
                text = f"NO MORE MOVES FOR PLAYER 4")
    
class SplashScreenMode(Mode):
    #players get to choose whether they want to play against local players or
    #the computer
    def appStarted(mode):
        mode.margin = mode.width//4
        mode.board = mode.blokusTitle()
        mode.cellSize = int((mode.width - mode.margin*2)/len(mode.board[0]))

    def blokusTitle(mode):
        board = [
            [True, True, True, False, False, True, False, False, False, True, True, True, False, True, True, True, False, True, False, False, True, False, True, False, True, False, True, True, True],
            [True, False, True, False, False, True, False, False, False, True, False, True, False, True, False, False, False, True, False, True, True, False, True, False, True, False, True, False, False],
            [True, False, True, False, False, True, False, False, False, True, False, True, False, True, False, False, False, True, True, True, False, False, True, False, True, False, True, False, False],
            [True, True, True, True, False, True, False, False, False, True, False, True, False, True, False, False, False, True, True, False, False, False, True, False, True, False, True, True, True],
            [True, False, False, True, False, True, False, False, False, True, False, True, False, True, False, False, False, True, True, True, False, False, True, False, True, False, False, False, True],
            [True, False, False, True, False, True, False, False, False, True, False, True, False, True, False, False, False, True, False, True, True, False, True, False, True, False, False, False, True],
            [True, True, True, True, False, True, True, True, False, True, True, True, False, True, True, True, False, True, False, False, True, False, True, True, True, False, True, True, True]
        ]
        return board

    def playTitle(mode):
        play = [
            [True, True, True, False, True, False, False, False, True, True, True, False, True, False, True],
            [True, False, True, False, True, False, False, False, True, False, True, False, True, False, True],
            [True, False, True, False, True, False, False, False, True, False, True, False, True, False, True],
            [True, True, True, False, True, False, False, False, True, True, True, False, True, True, True],
            [True, False, False, False, True, False, False, False, True, False, True, False, False, True, False],
            [True, False, False, False, True, False, False, False, True, False, True, False, False, True, False],
            [True, False, False, False, True, True, True, False, True, False, True, False, False, True, False]
        ]
        return play

    def helpTitle(mode):
        help = [
            [True, False, True, False, True, True, True, False, True, False, False, False, True, True, True],
            [True, False, True, False, True, False, False, False, True, False, False, False, True, False, True],
            [True, False, True, False, True, False, False, False, True, False, False, False, True, False, True],
            [True, True, True, False, True, True, True, False, True, False, False, False, True, True, True],
            [True, False, True, False, True, False, False, False, True, False, False, False, True, False, False],
            [True, False, True, False, True, False, False, False, True, False, False, False, True, False, False],
            [True, False, True, False, True, True, True, False, True, True, True, False, True, False, False]
        ]
        return help

    def drawBlokus(mode, canvas):
        for row in range(len(mode.board)):
            for col in range(len(mode.board[row])):
                if mode.board[row][col]:
                    mode.drawCell(canvas, row, col + 2, mode.board[row][col], mode.margin, mode.cellSize)

    def drawCell(mode, canvas, row, col, color, margin, cellSize):
        canvas.create_rectangle(margin + (col)*cellSize,
            margin + (row)*cellSize,
            margin + (col + 1) * cellSize,
            margin + (row + 1) * cellSize, fill = "black", width = 1)

    def drawPlay(mode, canvas):
        title = mode.playTitle()
        for row in range(len(title)):
            for col in range(len(title[row])):
                if title[row][col]:
                    mode.drawCell(canvas, row + 8, col, title[row][col], mode.width//5*2, mode.cellSize*0.9)
    
    def drawHelp(mode, canvas):
        title = mode.helpTitle()
        for row in range(len(title)):
            for col in range(len(title[row])):
                if title[row][col]:
                    mode.drawCell(canvas, row + 18, col, title[row][col], mode.width//5*2, mode.cellSize*0.9)

    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "antique white")
        mode.drawBlokus(canvas)
        mode.drawPlay(canvas)
        mode.drawHelp(canvas)
        
    def mousePressed(mode, event):
        if mode.width//5*2  <= event.x <= mode.width//5*2 + mode.cellSize*15 \
            and mode.width//5*2 + 7*mode.cellSize <= event.y <= mode.width//5*2 + 14*mode.cellSize:
            mode.app.setActiveMode(mode.app.chooseMode)
        elif mode.width//5*2  <= event.x <= mode.width//5*2 + mode.cellSize*15 \
            and mode.width//5*2 + 15*mode.cellSize <= event.y <= mode.width//5*2 + 22*mode.cellSize:
            mode.app.setActiveMode(mode.app.helpMode)
        
class ChooseMode(Mode):
    def appStarted(mode):
        mode.text = "CHOOSE YOUR MODE"
        mode.prevPage = "home"
    
    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "antique white")
        font = f"helvetica {mode.width//15} bold"
        canvas.create_text(mode.width//2, mode.height//5, text=mode.text, font=font)
        canvas.create_text(mode.width//2, mode.height//5*2, text = """Press UP key for LOCAL GAME\n
      Press DOWN Key for AI\n
      or CLICK THE BUTTONS""", font = f"helvetica {mode.width//22}")
        #Button for arrows
        canvas.create_rectangle(mode.width//2 - mode.width//10, mode.height//2 + mode.height//10, mode.width//2 + mode.width//10, mode.height//2 + mode.height//10 + mode.height//8, fill = "white")
        canvas.create_text(mode.width//2, mode.height//2 + mode.height//6, text = "/\\", font = f"helvetica {mode.width//10}")
        canvas.create_rectangle(mode.width//2 - mode.width//10, mode.height//2 + mode.height//9 + mode.height//8, mode.width//2 + mode.width//10, mode.height//2 + mode.height//9 + mode.height//4, fill = "white")
        canvas.create_text(mode.width//2, mode.height//2 + mode.height//4 + mode.height//20, text = "\\/", font = f"helvetica {mode.width//10}")
        #DRAW BACK TO SPLASHSCREEN BUTTON
        canvas.create_oval(mode.height//100, -mode.height//200 + mode.height - mode.height //100 * 9, mode.height//100 + mode.height//100 * 9 , -mode.height//200 + mode.height, fill = "red")
        canvas.create_text(mode.height//20,  mode.height - mode.height //170 * 9, text = f"BACK\n{mode.prevPage}")
    
    def mousePressed(mode, event):
        if mode.width//2 - mode.width//10 <= event.x <= mode.width//2 + mode.width//10 and \
            mode.height//2 + mode.height//10 <= event.y <= mode.height//2 + mode.height//10 + mode.height//8:
            mode.app.setActiveMode(mode.app.localP) 
        elif mode.width//2 - mode.width//10 <= event.x <= mode.width//2 + mode.width//10 and \
            mode.height//2 + mode.height//9 <= event.y <= mode.height//2 + mode.height//9 + mode.height//4:
            mode.app.setActiveMode(mode.app.ai)
        elif mode.height//100 <= event.x <= mode.height//100 + mode.height//100 * 9 and \
            -mode.height//200 + mode.height - mode.height //100 * 9 <= event.y <= -mode.height//200 + mode.height:
            mode.app.setActiveMode(mode.app.splashScreenMode)
        elif mode.height//34 <= event.y <= mode.height//17 and \
            mode.width - mode.height//20 - 10 <= event.x <= mode.width - mode.height//20 + 10:
            mode.app.setActiveMode(mode.app.helpMode)

    def keyPressed(mode, event):
        if event.key == "Up":
            mode.app.setActiveMode(mode.app.localP) 
        elif event.key == "Down":
            mode.app.setActiveMode(mode.app.ai)
                
class LocalPlayerSplash(Mode):
    def appStarted(mode):
        mode.text = "MULTIPLAYER"
        mode.prevPage = "choose"
        #Photo from https://www.iconfinder.com/
        twoPlayerUrl = "https://cdn3.iconfinder.com/data/icons/ui-2-glyph/64/people-512.png"
        mode.twoPlayers = mode.loadImage(twoPlayerUrl)
        mode.twoPlayers = mode.scaleImage(mode.twoPlayers, 1/5)
        mode.twoPWidth, mode.twoPHeight = mode.twoPlayers.size
        mode.twoPlayersFlipped = mode.twoPlayers.transpose(Image.FLIP_LEFT_RIGHT)
        
    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "antique white")
        fontSize = int(mode.width//10)
        font = f"helvetica {fontSize} bold"
        canvas.create_text(mode.width//2, mode.height//4, text=mode.text, font=font)
        #DRAW BACK TO PREVIOUS PAGE BUTTON
        canvas.create_oval(mode.height//100, -mode.height//200 + mode.height - mode.height //100 * 9, mode.height//100 + mode.height//100 * 9 , -mode.height//200 + mode.height, fill = "red")
        canvas.create_text(mode.height//20,  mode.height - mode.height //170 * 9, text = f" BACK\n{mode.prevPage}")
        canvas.create_text(mode.width//2, mode.height//3, text = "Click on the icon or press 2 for 2v2 and 4 for 4v4")
        #TWO PLAYERS ICON
        canvas.create_image(mode.app.width//3, mode.app.height//2, image = ImageTk.PhotoImage(mode.twoPlayers))
        canvas.create_text(mode.app.width//2 + mode.app.width//7, mode.app.height//2, text = "2v2", font = font)
        #FOUR PLAYERS ICON
        canvas.create_image(mode.app.width//3 - mode.twoPWidth//2, mode.app.height//2 + mode.app.height//5, image = ImageTk.PhotoImage(mode.twoPlayers))
        canvas.create_image(mode.app.width//3 + mode.twoPWidth//5, mode.app.height//2 + mode.app.height//5, image = ImageTk.PhotoImage(mode.twoPlayersFlipped))
        canvas.create_text(mode.app.width//2 + mode.app.width//7, mode.app.height//2 + mode.app.height//5, text = "4v4", font = font)

    def mousePressed(mode, event):
        if mode.height//100 <= event.x <= mode.height//100 + mode.height//100 * 9 and \
            -mode.height//200 + mode.height - mode.height //100 * 9 <= event.y <= -mode.height//200 + mode.height:
            mode.app.setActiveMode(mode.app.chooseMode)
        elif mode.app.width//3 - mode.twoPWidth//2 <= event.x <= mode.app.width//2 + mode.twoPWidth//2 and \
            mode.app.height//2 - mode.twoPHeight//2 <= event.y <= mode.app.height//2 + mode.twoPHeight//2:
            mode.app.setActiveMode(mode.app.playLocal)
        elif mode.app.width//3 - (mode.twoPWidth//2)*2 <= event.x <= mode.app.width//3 + mode.twoPWidth//5 + mode.twoPWidth and \
            mode.app.height//2 + mode.app.height//5 - mode.twoPHeight//2 <= event.y <= mode.app.height//2 + mode.app.height//5 + mode.twoPHeight//2:
            mode.app.setActiveMode(mode.app.playLocal4)
        elif mode.height//34 <= event.y <= mode.height//17 and \
            mode.width - mode.height//20 - 10 <= event.x <= mode.width - mode.height//20 + 10:
            mode.app.setActiveMode(mode.app.helpMode)
            
    def keyPressed(mode, event):
        if event.key == "2":
            mode.app.setActiveMode(mode.app.playLocal)
        elif event.key == "4":
            mode.app.setActiveMode(mode.app.playLocal4)

class AISplash(Mode):
    def appStarted(mode):
        mode.text = "AI"
        mode.prevPage = "home"
    
    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "antique white")
        fontSize = int(mode.width//5)
        font = f"helvetica {fontSize} bold"
        fontTwo = f"helvetica {fontSize}"
        canvas.create_text(mode.width//2, mode.height//4, text=mode.text, font=font, fill = "black")
        canvas.create_text(mode.width//2, mode.height//5*2, text = "Press right, left, or up key or click the buttons to choose the difficulty level!")
        canvas.create_rectangle(mode.width//2 - mode.width//4, mode.height//2 - mode.height//30, mode.width//2 + mode.width//4, mode.height//2+mode.height//6, fill = "LightGoldenRod1", width = 3)
        canvas.create_rectangle(mode.width//2 + mode.width//12, mode.height//2 - mode.height//30, mode.width//2 + mode.width//4, mode.height//2+mode.height//6, fill = "coral1", width = 3)
        canvas.create_rectangle(mode.width//2 - mode.width//4, mode.height//2 - mode.height//30, mode.width//2 - mode.width//12, mode.height//2+mode.height//6, fill = "SeaGreen1", width = 3)
        canvas.create_text(mode.width//2, mode.height//2 + mode.height//15, text = "< ^ >", font = fontTwo)
        #DRAW BACK TO SPLASHSCREEN BUTTON
        canvas.create_oval(mode.height//100, -mode.height//200 + mode.height - mode.height //100 * 9, mode.height//100 + mode.height//100 * 9 , -mode.height//200 + mode.height, fill = "red")
        canvas.create_text(mode.height//20,  mode.height - mode.height //170 * 9, text = f"BACK\n{mode.prevPage}")
        mode.drawHelpButton(canvas)

    def drawHelpButton(mode, canvas):
        fontSize = int(mode.width//20)
        font = f"helvetica {fontSize} bold"
        canvas.create_text(mode.width - mode.height//20,  mode.height//20, text = "?", font = font )  

    def mousePressed(mode, event):
        if mode.height//2 <= event.y <= mode.height//2 + mode.height//6:
            if mode.width//2 - mode.width//4 <= event. x <= mode.width//2 - mode.width//12:
                mode.app.setActiveMode(mode.app.easyAI)
            elif mode.width//2 + mode.width//12 <= event.x <= mode.width//2 + mode.width//4:
                mode.app.setActiveMode(mode.app.playAIABP)
            elif mode.width//2-mode.width//4 <= event.x <= mode.width//2 + mode.width//4:
                mode.app.setActiveMode(mode.app.playAI)
        elif mode.height//100 <= event.x <= mode.height//100 + mode.height//100 * 9 and \
            -mode.height//200 + mode.height - mode.height //100 * 9 <= event.y <= -mode.height//200 + mode.height:
            mode.app.setActiveMode(mode.app.splashScreenMode)
        elif mode.height//34 <= event.y <= mode.height//17 and \
            mode.width - mode.height//20 - 10 <= event.x <= mode.width - mode.height//20 + 10:
            mode.app.setActiveMode(mode.app.helpMode)

    def keyPressed(mode, event):
        if event.key == "Right": 
            mode.app.setActiveMode(mode.app.playAIABP)
        elif event.key == "Up":
            mode.app.setActiveMode(mode.app.playAI)
        elif event.key == "Left":
            mode.app.setActiveMode(mode.app.easyAI)

class HowToPlayMode(Mode):
    def appStarted(mode):
        mode.title = "INSTRUCTIONS"
        mode.text = """
                The goal of Blokus is for each player to establish their 
                territories and block other players from expanding their 
                territories. Each player takes a turn to make their move, 
                and everyone has to connect their pieces diagonally (none
                of the player's pieces can be adjacent to another). The 
                score of this game is determined by how many blocks the 
                player is able to piece on the board. 

                To move the piece, drag the piece from the piece board directly
                to the board. For the mini boards, the players can rotate 
                their pieces freely, which can be done by clicking the piece, 
                waiting for it to show up to the left of the board, and pressing 
                arrows to transform it. Clicking the up arrow will flip the 
                clicked piece vertically; clicking the right arrow will flip the 
                clicked piece horizontally; clicking the down arrow will rotate 
                the piece. 

                For this game, if a player is stuck and does not know which
                move to place next, he can click the 'h' key or press the 
                hint button (light bulb) for help. If no possible moves 
                remain, then the player's turn is skipped until none of 
                the players have a possible move. After that, the final 
                score is calculated. Bear in mind that the last man standing 
                may not be the winner although that is often the case. Once 
                the game is over (or whenever the users feel like it), the 
                users can press 'r' to restart the game. If something is not
                right, try clicking 'h' or the screen. Players can always 
                refer back to this page by clicking the question mark on 
                the top right corner. Good luck, and may the best conqueror win!
                 
        """

    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "antique white")
        fontSize = int(mode.width//10)
        font = f"helvetica {fontSize} bold"
        canvas.create_text(mode.width//2, mode.height//6, text=mode.title, font = font)
        canvas.create_text(mode.width//5*3, mode.height//5*3, text=mode.text)
        mode.drawKey(canvas)
        
    def drawKey(mode, canvas):
        #UP
        font = f"helvetica {mode.app.width//15} bold"
        canvas.create_rectangle(mode.app.width//10, mode.app.height - mode.app.height//3 + 10, \
            mode.app.width//5, mode.app.height - mode.app.height//3 + mode.app.width//10 + 10, fill = "white")
        midXUp = (mode.app.width//10 + mode.app.width//5)//2
        midYUp = (mode.app.height - mode.app.height//3 + 10 + mode.app.height - mode.app.height//3 + mode.app.width//10 + 10)//2
        canvas.create_text(midXUp, midYUp, text = "/\\", font = font)
        #DOWN
        canvas.create_rectangle(mode.app.width//10, mode.app.height - mode.app.height//5, \
            mode.app.width//5, mode.app.height - mode.app.height//10, fill = "white")
        midXDown = (mode.app.width//10 + mode.app.width//5)//2
        midYDown = (mode.app.height - mode.app.height//5 + mode.app.height - mode.app.height//10)//2
        canvas.create_text(midXDown, midYDown, text = "\\/", font = font)
        #RIGHT
        canvas.create_rectangle(mode.app.width//10*2 + 10, mode.app.height - mode.app.height//5, \
            mode.app.width//10*3 + 10, mode.app.height - mode.app.height//5 + mode.app.width//10, fill = "white")
        midXRight = (mode.app.width//10*2 + 10 + mode.app.width//10*3 + 10)//2
        midYRight = (mode.app.height - mode.app.height//5 + mode.app.height - mode.app.height//5 + mode.app.width//10)//2
        canvas.create_text(midXRight, midYRight, text = ">", font = font)

    def mousePressed(mode, event):
        mode.app.setActiveMode(mode.app.splashScreenMode)

class MyModalApp(ModalApp):
    def appStarted(app):
        app.splashScreenMode = SplashScreenMode()
        app.chooseMode = ChooseMode()
        app.localP = LocalPlayerSplash()
        app.ai = AISplash()
        app.playLocal4 = PlayBlokus4()
        app.playLocal = PlayBlokus()
        app.easyAI = PlayBlokusEasyAI()
        app.playAI = PlayBlokusAI2()
        app.playAIABP = PlayBlokusAIABP2()
        app.setActiveMode(app.splashScreenMode)
        app.helpMode = HowToPlayMode()

app = MyModalApp(width=680, height=680)
