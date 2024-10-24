import time
import pandas as pd
import pygame
from pygame import Rect
#from AppKit import NSScreen
pygame.font.init()
#import os
#os.environ['SDL_VIDEO_CENTERED'] = '1'

from match import Match

board = {x:{y:None for y in range(1, 9)[::-1]} for x in range(1,9)}

pd.set_option('display.max_columns', 8)



col_dict = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8}
num_dict = {value:key for key, value in col_dict.items()}



#board_alpha_keys = [pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h]
#board_num_keys = [pygame.K_1, pygame.K_2, pygame.K_2, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8]


class SelectionLog:
    def __init__(self, game):
        self.game = game
        self.log = []
        self.full_move_log = []
        
        self.x = 620
        self.y = 400
        self.right_margin = 10
        self.bottom_margin = 5
        
        self.text_left_margin = 3
        self.text_top_margin = 2
        self.line_margin_inc = 3
        self.move_log_line = 490
        self.writing_line = 580
        self.color = (192,192,192)

    
    @property
    def width(self):
        return self.game.WINDOW_WIDTH - self.x - self.right_margin
    @property
    def height(self):
        return self.game.WINDOW_HEIGHT - self.y - self.bottom_margin
    @property
    def FONT(self):
        return self.game.LOG_FONT
    @property
    def match(self):
        return self.game.match
    @property
    def player(self):
        return self.game.player
        
        
    def refresh_full(self):
        self.refresh_move_log()
        self.refresh_select_log()
        self.refresh_write_log(selection = 'piece')
        
    def refresh_move_log(self):
        rect = Rect(self.x, self.y, self.width, self.move_log_line - self.y)
        pygame.draw.rect(self.game.window, self.color, rect)
        
        lines = self.full_move_log[-4:]
        
        l = 0
        for line in lines:
            render = self.FONT.render(line, 1, (34,139,34))
            self.game.window.blit(render, (self.x + self.text_left_margin, 
                                  self.y + self.text_top_margin + (l * (self.line_margin_inc + self.FONT.get_linesize()))))
            l += 1
            
    def refresh_select_log(self):
        rect = Rect(self.x, self.move_log_line, self.width, self.writing_line - self.move_log_line)
        pygame.draw.rect(self.game.window, self.color, rect)
        
        lines = self.log[-4:][::-1]
        
        l = 1
        for line in lines:
            render = self.FONT.render(line, 1, (34,139,34))
            self.game.window.blit(render, (self.x + self.text_left_margin, 
                                  self.writing_line - (l * (self.line_margin_inc + self.FONT.get_linesize()))))
            l += 1    
    
    def refresh_write_log(self, inp = None, selection = None):
        rect = Rect(self.x, self.writing_line, self.width, self.game.WINDOW_HEIGHT - self.writing_line - self.bottom_margin)
        pygame.draw.rect(self.game.window, self.color, rect)
        
        if not inp:
            inp = ''
        
        if not selection:
            return None
        if selection == 'piece':
            text = 'Choose a piece: ' + inp
        elif selection == 'move':
            text = 'Make a move: ' + inp
        text_render = self.FONT.render(text, 1, (34,139,34))
        self.game.window.blit(text_render, (self.x + self.text_left_margin, self.writing_line))
        
        
 
class GameLog:
    def __init__(self, game):
        self.game = game
        self.log = []
        
        self.x = 620
        self.y = 5
        self.right_margin = 10
        self.width = self.game.WINDOW_WIDTH - self.x - self.right_margin
        self.height = 400 - self.y
        
        self.text_left_margin = 3
        self.text_top_margin = 3
        self.line_margin_inc = 3
        self.color = (232,220,202)

    @property
    def FONT(self):
        return self.game.LOG_FONT
    @property
    def match(self):
        return self.game.match
    @property
    def player(self):
        return self.game.player


    def refresh_log(self):
        rect = Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.game.window, self.color, rect)
        
        lines = self.match.log[-17:-1]
        
        l = 0
        for line in lines:
            text = '{}: {} -> {}; {}'.format(line[0],
                                     ''.join(str(x) for x in line[1]), 
                                     ''.join(str(x) for x in line[2]),
                                         line[3])
            render = self.FONT.render(text, 1, (34,139,34))
            self.game.window.blit(render, (self.x + self.text_left_margin, 
                                  self.y + self.text_top_margin + (l * (self.line_margin_inc + self.FONT.get_linesize()))))
            l += 1
            
        for line in self.log:
            render = self.FONT.render(line, 1, (34,139,34))
            self.game.window.blit(render, (self.x + self.text_left_margin, 
                                  self.y + self.text_top_margin + (l * (self.line_margin_inc + self.FONT.get_linesize()))))
            l += 1



class Board:
    def __init__(self, game):
        self.game = game
        self.img = None
        self.coord_dict = None
        self.cell_x = 68
        self.cell_y = 66
        self.cell_w = 59.5
        self.cell_h = 59
        
    @property
    def window(self):
        return self.game.window
    @property
    def FONT(self):
        return self.game.BOARD_FONT
        
    def generate_coordinates(self):
        coord_dict = {}
        for c in range(8):
            for r in range(8):
                coord_dict[(c + 1, 8 - r)] = (self.cell_x + (c * self.cell_w), self.cell_y + (r * self.cell_h))
        self.coord_dict = coord_dict

    def generate_board(self):
        if self.img:
            board = self.img
        else:
            board = pygame.image.load('board3.png')
            w = board.get_width()
            h = board.get_height()
            board = pygame.transform.scale(board, ((w/h) * self.game.WINDOW_HEIGHT, self.game.WINDOW_HEIGHT))
            self.img = board

        self.window.blit(board, (0,0))
    
    def generate_lettering(self):
        c_margin = 79
        r_margin = 490
        for k, v in col_dict.items():
            c_text = self.FONT.render(k, 1, (38,7,5))
            self.window.blit(c_text, (c_margin, 3))
            self.window.blit(c_text, (c_margin, 557))
            c_margin += 60
            
            r_text = self.FONT.render(str(v), 1, (37,7,5))
            self.window.blit(r_text, (12, r_margin))
            self.window.blit(r_text, (573, r_margin))
            r_margin += -60
        
    def generate_pieces(self, pieces):
        for piece in pieces:
            img = pygame.transform.scale_by(pygame.image.load(f'{piece.team.name[0].lower()}_{piece.kind.lower()}.png'), (2/3.2))
            img.set_colorkey((209, 139, 71))
            self.window.blit(img, (70 + ((piece.col - 1)*59.5), 475 - ((piece.row - 1)*59)))



class Game:
    def __init__(self):
        self.match = None
        self.player = None
        self.WINDOW_WIDTH = 1000
        self.WINDOW_HEIGHT = 600
        self.BOARD_FONT = pygame.font.SysFont('copperplate', bold = True, size = 40)
        self.LOG_FONT = pygame.font.SysFont('helvetica', size = 14)
        self.window = None
        self.board = Board(self)
        self.game_log = GameLog(self)
        self.selection_log = SelectionLog(self)
        
    def set_window(self):
        self.window = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))            
    
    def receive_input(self, selection = 'piece', inp = ''):
        selected = False
        #pygame.event.clear()
        
        while not selected:
            update = False
            event = pygame.event.wait(timeout = 60000)
            
            if event.type == pygame.NOEVENT:
                return 'Timeout'
            elif event.type == pygame.QUIT:
                return 'quit'
            
            elif event.type == pygame.TEXTINPUT:
                text = event.text
                inp = inp + text
                self.selection_log.refresh_write_log(inp, selection)
                update = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                inp = inp[:-1]
                self.selection_log.refresh_write_log(inp, selection)
                update = True
                
            elif event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
                selected = self.validate_input(inp, selection)
                if not selected:
                    inp = ''
                update = True
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.board.coord_dict:
                    self.board.generate_coordinates()
                
                if event.pos[0] >= self.board.cell_x and event.pos[0] <= self.board.cell_x + (self.board.cell_w * 8) \
                        and event.pos[1] >= self.board.cell_y and event.pos[1] <= self.board.cell_y + (self.board.cell_h * 8): # click within board bounds
                    
                    reverse_coord = {v:k for k,v in self.board.coord_dict.items()}
                    for k in reverse_coord.keys():
                        if event.pos[0] >= k[0] and event.pos[0] <= k[0] + self.board.cell_w  \
                                and event.pos[1] >= k[1] and event.pos[1] <= k[1] + self.board.cell_y:
                                    
                            cell = reverse_coord[k]
                            selected = self.validate_input(f'{num_dict[cell[0]]}{cell[1]}', selection)
                            if not selected:
                                inp = ''
                            update = True

            if update: 
                pygame.display.update()
            
                
        return selected
    
    def validate_input(self, inp, selection):
        #TODO: castling
        if selection == 'piece':
            if not self.check_piece_selection(inp): # adds selection response to log
                piece = False
            else:
                self.selection_log.log = [f'Selected Piece: {inp}']
                piece = (col_dict[inp[0].upper()], int(inp[1]))
        elif selection == 'move':
            if not self.check_move_selection(inp): # adds move response to log
                piece = False
            else:
                self.selection_log.log = []
                piece = (col_dict[inp[0].upper()], int(inp[1]))
        
        self.selection_log.refresh_select_log()
        if (selection == 'piece' and piece) or (selection == 'move' and not piece):
            self.selection_log.refresh_write_log(selection = 'move')
        elif (selection == 'move' and piece) or (selection == 'piece' and not piece):
            self.selection_log.refresh_write_log(selection = 'piece')
            
        return piece
    
    def check_piece_selection(self, cell_input):
        try:  
            cell = (col_dict[cell_input[0].upper()], int(cell_input[1]))
        except:
            self.selection_log.log.append(f'{cell_input}: Select cell like so - a6 or f3')
            return False
        
        if cell[0] not in range(1,9) or cell[1] not in range(1,9):
            self.selection_log.log.append(f'{cell_input}: Invalid selection - Columns (left to right) A-H or 1-8; Rows (top to bottom) 8-1')
            return False
        elif not self.match.board(cell):
            self.selection_log.log.append(f'{cell_input}: Choose a square with a piece')
            return False
        elif self.match.board(cell).team != self.player:
            self.selection_log.log.append(f'{cell_input}: Pick a piece on your team')
            return False
        else:
            return True 
        
    def check_move_selection(self, move_input):
        try:  
            cell = (col_dict[move_input[0].upper()], int(move_input[1]))
        except:
            self.selection_log.log.append(f'{move_input}: Select cell like so - a6 or f3')
            return False
        
        if cell[0] not in range(1,9) or cell[1] not in range(1,9):
            self.selection_log.log.append(f'{move_input}: Invalid selection - Columns (left to right) A-H or 1-8; Rows (top to bottom) 8-1')
            return False
        elif self.match.board(cell) and self.match.board(cell).team == self.player and not self.match.board(cell).kind == 'Rook':
            self.selection_log.log.append(f'{move_input}: Already occupied by your team')
            return False
        else:
            return True 

        
        
    def play(self):
        self.match = Match() 
        match = self.match
        match.new_game(test = False)
        
        pygame.init()
        self.set_window()
        
        run = True
        quitt = False
        while run:
            
            ## Start Turn            
            if len(match.log) == 0:
                self.player = match.white
            else:
                self.game_log.log = ['',
                                     'Last Move',
                                     '{}: {} -> {}; {}'.format(match.log[-1][0],
                                      ''.join(str(x) for x in match.log[-1][1]), 
                                      ''.join(str(x) for x in match.log[-1][2]),
                                          match.log[-1][3]),
                                     ''
                                     ]
                
            self.game_log.log.append(f'Turn: {match.turn}')
            self.game_log.log.append(f'{self.player.name} move')
            
            # In Check
            if self.player.king.in_check():
                self.game_log.log.append(f'{self.player.name} is in check')
            
            
            self.selection_log.full_move_log = []
            pieces = match.white.alive + match.black.alive
            self.board.generate_board()
            self.board.generate_lettering()
            self.board.generate_pieces(pieces)
            self.game_log.refresh_log()
            self.selection_log.refresh_full()
            pygame.display.update()
            
            
            ## Piece Selection
            legal_move = False
            legal_castle = False
            while not legal_move:
                pygame.display.update()
                piece = self.receive_input('piece')
                
                if piece == 'quit':
                    quitt = True
                    break
                elif piece == 'Timeout':
                    continue
                
                elif isinstance(piece, tuple):
                    move = self.receive_input('move')
                    
                    if move == 'quit':
                        quitt = True
                        break
                    elif move == 'Timeout':
                        continue
                    
                    elif isinstance(move, tuple):
                        legal = match.check_move(piece, move)
                        if legal == True:
                            legal_move = True
                        else:  
                            if piece == self.player.king.position and self.player.king.horiz(move)        \
                                        and self.player.king.col in [4,5] and self.player.king.row in [1,8]     \
                                        and (abs(self.player.king.col - move[0]) == 2 or move[0] in [1,8]): #Castle
                                legal_castle = self.player.king.legal_castle(move)
                                if legal_castle == True:
                                    legal_move = True
                                else:
                                    self.selection_log.full_move_log.append(legal_castle)
                                    self.selection_log.refresh_move_log()
                                    
                            self.selection_log.full_move_log.append(legal)
                            self.selection_log.refresh_move_log()        
            if quitt:
                break
                
            ## Move and match log
            piece_name = match.board(piece).name
            
            if legal_castle == True:
                self.player.castle(move) 
                match.log.append((piece_name, (num_dict[piece[0]], piece[1]), (num_dict[move[0]], move[1]), 'Castle'))
            else:
                if match.board(move):
                    match.log.append((piece_name, (num_dict[piece[0]], piece[1]), (num_dict[move[0]], move[1]), f'{match.board(move).name} Captured'))
                else:
                    match.log.append((piece_name, (num_dict[piece[0]], piece[1]), (num_dict[move[0]], move[1]), ''))
                match.move(piece, move)
            
            
            ## End Turn
            # Pawn Queening
            for piece in self.player.alive:
                if ((piece.row == 8 and self.player.name == 'White') or (piece.row == 1 and self.player.name == 'Black')) and piece.kind == 'Pawn':
                    match.log[-1] = (match.log[-1][0], match.log[-1][1], match.log[-1][2], 'Promoted to Queen')
                    self.player.queen_pawn(piece)
            
            # Check Enemy Moves
            if not self.player.enemy.check_moves():
                if self.player.enemy.king.in_check():
                    self.game_log.log.append(f'{self.player.enemy.name} is in checkmate; {self.player.name} wins!')
                else:
                    self.game_log.log.append(f'{self.player.enemy.name} has no moves; {self.player.name} wins!')
                run = False
                continue
            
            # Player Switch and Turn Count
            if self.player == match.black:
                match.turn += 1
            self.player = match.white if self.player.name == 'Black' else match.black
            
            #self.selection_log.full_move_log = []
            
        pygame.quit()
        
        return match, self.selection_log, self.game_log
    
    




if __name__ == '__main__':
    game = Game()
    game.play()


