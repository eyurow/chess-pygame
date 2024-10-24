
import pandas as pd

col_dict = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8}
num_dict = {value:key for key, value in col_dict.items()}   




def df(_board, compact = True, alpha_cols = False):
    if compact:
        try:
            df = pd.DataFrame.from_dict({k:{kk:kv[0] if kv else None for kk, kv in v.items()} for k, v in _board.items()}, orient = 'columns')
        except TypeError:
            df = pd.DataFrame.from_dict(_board, orient = 'columns')
    else:
        df = pd.DataFrame.from_dict(_board, orient = 'columns')
    if alpha_cols:
        df.columns = [num_dict[x] for x in df.columns]
    return df
    
def mask(_board):
    return {k:{kk:kv if kv else None for kk, kv in v.items()} for k, v in _board.items()}
    
def deep_mask(_board, full = True):
    mask_pieces = []
    if full:
        return {k:{kk:(kv[0], Piece.from_piece(kv[1], mask_pieces)) if kv else None for kk, kv in v.items()} for k, v in _board.items()}, mask_pieces
    else:
        return {k:{kk:Piece.from_piece(kv[1], mask_pieces) if kv else None for kk, kv in v.items()} for k, v in _board.items()}, mask_pieces


def surrounding_cells(cell):
    surround = []
    x = cell[0]
    y = cell[1]
    for c in range(x-1, x+2):
        for r in range(y-1, y+2):
            if (c, r) != cell and c > 0 and c <= 8 and r > 0 and r <= 8:
                surround.append((c, r))
    return surround

def surrounding_pieces(cell, _board, _self = None):
    # get pieces surrounding input cell on board, excludes self if defined (for checking king bump)
    surround = surrounding_cells(cell)
    _surround = []
    for cell in surround:
        if populated(cell, _board) and _board[cell[0]][cell[1]][1] != _self:
            _surround.append(_board[cell[0]][cell[1]][1])
    return _surround


def populated(cell, _board):
    if _board[cell[0]][cell[1]]:
        return True
    else:
        return False
    

def in_check(cell, _board, _alive, _from, as_list = False):
    # generic for cell; piece in_check checker in methods
    enemies = [x for x in _alive if x.team == _from]
    checking = []
    for _piece in enemies:
        if _piece.legal_moves(cell, _board):
            if not as_list:
                return True
            else:
                checking.append(_piece)
    if not as_list:
        return False
    else:
        checking

def puts_in_check(_board, _piece, _move):
    pos = _piece.position
    dm, _pieces = deep_mask(_board, full = True)
    own = dm[pos[0]][pos[1]][1]
    
    king = None
    for piece in _pieces:
        if piece.team == _piece.team and isinstance(piece, King):
            king = piece
    
    if not king:
        return False
            
    if populated(_move, dm):
        _pieces.remove(dm[_move[0]][_move[1]][1])
    dm[pos[0]][pos[1]] = None
    own.position = _move
    own.place(dm)
    return king.in_check(dm, _pieces)
    
    



class Piece:
    def __init__(self, position, team, log = None):
        self.position = position if isinstance(position[0], int) else (col_dict[position[0]], position[1])
        self.team = team
        if not log:
            self.log = [self.position]
        else:
            self.log = log
    
    @property
    def kind(self):
        return type(self).__name__
    @property
    def name(self):
        return f'{self.team.abbrev}{self.kind}'
    @property
    def col(self):
        return self.position[0]
    @property
    def row(self):
        return self.position[1]
    @property
    def board(self):
        return self.team.match.board
    @property
    def match(self):
        return self.team.match
    @property
    def enemy_team(self):
        return self.team.enemy
        
    @staticmethod
    def from_piece(piece):
        tmp = type(piece)
        return tmp(piece.position, piece.team, piece.log[:])
    
    def mask(self, team):
        tmp = type(self)
        return tmp(self.position, team, self.log[:])
    
    def copy(self):
        tmp = type(self)
        return tmp(self.position, self.team, self.log[:])
    
    def place(self):
        self.board[self.position] = self
            
    
    # Movement patterns
    def horiz(self, cell):
        return self.col - cell[0] != 0 and self.row == cell[1]
    def vert(self, cell):
        return self.row - cell[1] != 0 and self.col == cell[0]
    def diag(self, cell):
        return abs(self.row - cell[1]) == abs(self.col - cell[0])
    def knight_jump(self, cell):
        return (abs(self.row - cell[1]) == 1 and abs(self.col - cell[0]) == 2)  \
                or (abs(self.row - cell[1]) == 2 and abs(self.col - cell[0]) == 1)
    
    # checks
    def enemy(self, cell):
        if not self.board(cell):
            return False
        else:
            return self.board(cell).team != self.team
    
    def blocked_path(self, cell):
        if self.horiz(cell):
            if self.col < cell[0]:
                direction = range(1, cell[0] - self.col)
            else:
                direction = range(-(self.col - cell[0]) + 1, 0)[::-1]
                
            for c in direction:
                if self.board(self.col + c, self.row):
                    return True
            return False
        
        elif self.vert(cell):
            if self.row < cell[1]:
                direction = range(1, cell[1] - self.row)
            else:
                direction = range(-(self.row - cell[1]) + 1, 0)[::-1]
                
            for r in direction:
                if self.board(self.col, self.row + r):
                    return True
            return False
        
        elif self.diag(cell):
            if self.col < cell[0]:
                hor_direction = range(1, cell[0] - self.col)
            else:
                hor_direction = range(-(self.col - cell[0]) + 1, 0)[::-1]
                
            if self.row < cell[1]:
                vert_direction = range(1, cell[1] - self.row)
            else:
                vert_direction = range(-(self.row - cell[1]) + 1, 0)[::-1]
            
            increments = [(h, v) for h, v in zip(hor_direction, vert_direction)]
            
            for inc in increments:
                if self.board(self.col + inc[0], self.row + inc[1]):
                    return True
            return False
        
    def surrounding_pieces(self, cell = None):
        # get pieces surrounding input cell on board, excludes self if defined (for checking king bump)
        if cell:
            surround = surrounding_cells(cell)
        else:
            surround = surrounding_cells(self.position)
        _surround = []
        for cell in surround:
            if self.board(cell) and self.board(cell) != self:
                _surround.append(self.board(cell))
        return _surround
        
    def in_check(self, cell = None, as_list = False):
        if cell:
            checking_cell = cell
        else:
            checking_cell = self.position
        enemies = self.enemy_team.alive #[x for x in self.enemy_team.alive]
        checking = []
        for piece in enemies:
            if piece.legal_moves(checking_cell):
                if not as_list:
                    return True
                else:
                    checking.append(piece)
        if not as_list:
            return False
        else:
            return checking
    
    def check_moves(self, as_df = False):
        move_board = {c:{r:self.legal_moves((c, r)) for r in range(1, 9)[::-1]} for c in range(1,9)}
        if as_df:
            return df(move_board)
        else:
            return move_board
                

            
class Pawn(Piece):
    def __init__(self, position, team, log = None):
        super().__init__(position, team, log)
        
    def legal_moves(self, cell):
        if (self.team.name == 'White' and cell[1] <= self.row) or (self.team.name == 'Black' and cell[1] >= self.row):
            return False # can only move forward
        
        # if cell diag1 and has enemy or in en passant
        elif self.diag(cell) and abs(self.col - cell[0]) == 1 and abs(self.row - cell[1]) == 1:
            if self.enemy(cell):
                return True
            elif self.enemy((cell[0], self.row)) and self.board(cell[0], self.row).kind == 'Pawn' \
                    and len(self.board(cell[0], self.row).log == 2) and abs(self.board(cell[0],self.row).log[1][1]-self.board(cell[0],self.row).log[1][0]) == 2: # TODO: and enemy pawn moved two spaces on first turn
                return True
            else: 
                return False
                
        # vertical movement and move number
        elif self.vert(cell):
            if abs(self.row - cell[1]) > 2:
                return False # move too far
            elif self.board(cell):
                return False # can only capture diagonally
            elif abs(self.row - cell[1]) <= 2:
                if len(self.log) > 1 and abs(self.row - cell[1]) == 2:
                    return False
                elif abs(self.row - cell[1]) == 2 and self.blocked_path(cell):
                    return False
                else:
                    return True
                
        else:
            return False
            

class Knight(Piece):
    def __init__(self, position, team, log = None):
        super().__init__(position, team, log)
        
    def legal_moves(self, cell):
        if not self.knight_jump(cell):
            return False
        elif (not self.board(cell)) or self.enemy(cell):
            return True
        else:
            return False
        
class Bishop(Piece):
    def __init__(self, position, team, log = None):
        super().__init__(position, team, log)
        
    def legal_moves(self, cell):
        if not self.diag(cell):
            return False
        elif not self.blocked_path(cell) and ((not self.board(cell)) or self.enemy(cell)):
            return True
        else:
            return False
        
class Rook(Piece):
    def __init__(self, position, team, log = None):
        super().__init__(position, team, log)
        
    def legal_moves(self, cell):
        if not (self.horiz(cell) or self.vert(cell)):
            return False
        elif not self.blocked_path(cell) and ((not self.board(cell)) or self.enemy(cell)):
            return True
        # TODO: Castling
        else:
            return False
                
class Queen(Piece):
    def __init__(self, position, team, log = None):
        super().__init__(position, team, log)
        
    def legal_moves(self, cell):
        if not (self.horiz(cell) or self.vert(cell) or self.diag(cell)):
            return False
        elif not self.blocked_path(cell) and ((not self.board(cell)) or self.enemy(cell)):
            return True
        else:
            return False
                
class King(Piece):
    def __init__(self, position, team, log = None):
        super().__init__(position, team, log)
        
    def legal_moves(self, cell):
        if abs(self.row - cell[1]) > 1 or abs(self.col - cell[0]) > 1: # regular movement
            # TODO: castling
            return False
        elif (not self.board(cell)) or self.enemy(cell):
            if any([piece.kind == 'King' for piece in self.surrounding_pieces(cell) if piece != self]): # can't bump another king
                return False
            else:
                return True
        else:
            return False
        
    def legal_castle(self, cell):
        if len(self.log) > 1 or self.in_check():
            print('Cannot castle if king has already moved or king is in check')
            return False #can't castle after king has moved or castle while in check
        
        if self.col < cell[0]:
            rook_cell = (8, self.row)
            direction = range(1, rook_cell[0] - self.col)
        else:
            rook_cell = (1, self.row)
            direction = range(-(self.col - rook_cell[0]) + 1, 0)[::-1]
            
        if self.board(rook_cell) and self.board(rook_cell).team == self.team \
                and self.board(rook_cell).kind == 'Rook' and len(self.board(rook_cell).log) == 1: # Check unmoved rook in corner
            
            for c in direction:
                if self.board(self.col + c, self.row): # no pieces between king and rook
                    return 'Cannot castle through pieces'
                if abs(c) <= 2:
                    if self.in_check((self.position[0] + c, self.position[1])): # king isn't moving through check  #TODO: rewrite this in_check func
                        return 'Cannot castle through checked squares'
            return True

        else:
            return 'Cannot castle this side - requires unmoved rook in corner and cannot move through check'
        
        
