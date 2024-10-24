import pandas as pd
from pieces import King, Queen, Rook, Knight, Bishop, Pawn

col_dict = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8}
num_dict = {value:key for key, value in col_dict.items()}   

pd.set_option('display.max_columns', 8)

def horiz(c, cell):
    return c[0] - cell[0] != 0 and c[1] == cell[1]
def vert(c, cell):
    return c[1] - cell[1] != 0 and c[0] == cell[0]
def diag(c, cell):
    return abs(c[1] - cell[1]) == abs(c[0] - cell[0])
def knight_jump(c, cell):
    return (abs(c[1] - cell[1]) == 1 and abs(c[0] - cell[0]) == 2)  \
            or (abs(c[1]- cell[1]) == 2 and abs(c[0]- cell[0]) == 1)



class Match:
    def __init__(self):
        self.board = Board(self)
        self.teams = [Team('White', self), Team('Black', self)]
        self.log = []
        self.turn = None
        
    def __getitem__(self, team):
        if team.name == 'White':
            return self.white
        elif team.name == 'Black':
            return self.black
    
    @property
    def white(self):
        return self.teams[0]
    @property
    def black(self):
        return self.teams[1]
    
    
    def generate_pieces(self):
        self.white.pieces.append(King((5,1), self.white))
        self.black.pieces.append(King((5,8), self.black))
        for col in range(1,9):
            self.white.pieces.append(Pawn((num_dict[col],2), self.white))
            self.black.pieces.append(Pawn((num_dict[col],7), self.black))
        for col in [1,8]:
            self.white.pieces.append(Rook((num_dict[col],1), self.white))
            self.black.pieces.append(Rook((num_dict[col],8), self.black))
        for col in [2,7]:
            self.white.pieces.append(Knight((num_dict[col],1), self.white))
            self.black.pieces.append(Knight((num_dict[col],8), self.black))
        for col in [3,6]:
            self.white.pieces.append(Bishop((num_dict[col],1), self.white))
            self.black.pieces.append(Bishop((num_dict[col],8), self.black))                
        self.white.pieces.append(Queen((4,1), self.white))
        self.black.pieces.append(Queen((4,8), self.black))
        
    def generate_test(self): #TODO delete
        self.white.pieces.append(King((4,1), self.white))
        self.white.pieces.append(Rook((8,1), self.white))
        self.black.pieces.append(King((4,8), self.black))
        self.black.pieces.append(Pawn((2,2), self.black))
        #self.black.pieces.append(Queen((4,8), self.black))
            
    def set_pieces(self):
        for team in self.teams:
            for piece in team.pieces:
                piece.place()
    
    def new_game(self, test = True): #TODO: turnoff test
        if test:
            self.generate_test()
        else:
            self.generate_pieces()
        self.set_pieces()
        for team in self.teams:
            team.alive = team.pieces[:]
        self.turn = 1
            
    def mask(self):
        mask = Match()
        mask.white.pieces = [piece.mask(mask.white) for piece in self.white.alive]
        mask.black.pieces = [piece.mask(mask.black) for piece in self.black.alive]
        mask.set_pieces()
        for team in mask.teams:
            team.alive = team.pieces[:]
        return mask
            
    
    
    def move(self, piece_pos, cell):
        piece = self.board(piece_pos)
        if self.board(cell):
            self.board(cell).team.alive.remove(self.board(cell))
        # TODO: check en passant
        self.board[piece.position] = None
        piece.position = cell
        piece.place()
        piece.log.append(piece.position)
        
    def check_move(self, piece_pos, move):
        piece_text = num_dict[piece_pos[0]].lower() + str(piece_pos[1])
        cell_text = num_dict[move[0]].lower() + str(move[1])
        
        piece = self.board(piece_pos)
        if not piece.legal_moves(move):
            return f'{piece_text} -> {cell_text}: Illegal Move'
        elif piece.team.reveals_check(piece, move):
            return f'{piece_text} -> {cell_text}: Cannot put your king into check'
        elif piece.team.leaves_in_check(piece_pos, move):
            return f'{piece_text} -> {cell_text}: Cannot leave your king in check'
        else:
            return True
        
        
    def check_moves(self, team):
        for piece in team.alive:
            for c in range(1, 9):
                for r in range(1, 9):
                    if piece.legal_moves((c,r)) and not team.reveals_check(piece, (c,r)) and not team.leaves_in_check(piece, (c,r)):
                        return True
            if piece.kind == 'King':
                if piece.legal_castle((piece.col, 1)) or piece.legal_castle((piece.col, 8)):
                    return True
        return False
    

        
class Team:
    def __init__(self, name, match):
        self.name = name
        self.match = match
        self.pieces = []
        self.alive = []
        
    @property
    def abbrev(self):
        return f'{self.name[:2]}.'
    @property
    def king(self):
        return self.alive[0]
    @property
    def enemy(self):
        return self.match.white if self.name == 'Black' else self.match.black
    @property
    def board(self):
        return self.match.board
    
    def castle(self, rook):
        king = self.king
        if king.col < rook[0]:
            _rook = self.board(8, king.row)
            n_king = (7, king.row)
            n_rook = (6, king.row)
        else:
            _rook = self.board(1, king.row)
            n_king = (3, king.row)
            n_rook = (4, king.row)
            
        self.board[king.position] = None
        self.board[_rook.position] = None
        king.position = n_king
        _rook.position = n_rook
        king.place()
        _rook.place()
        king.log.append(king.position)
        _rook.log.append(_rook.position)
        
    def queen_pawn(self, pawn):
        queen = Queen(pawn.position, self, pawn.log[:])
        self.alive.remove(pawn)
        self.alive.append(queen)
        queen.place()
        
        
    def reveals_check(self, piece, cell):
        king = self.king

        if piece.horiz(king.position) and cell[1] != piece.row: # if moving off horizontal plane with king
            if king.col < piece.col:
                direction = range(piece.col + 1, 9)
            else:
                direction = range(1, piece.col)[::-1]
            for c in direction:
                if self.board(c, piece.row) and self.board(c, piece.row).team == self.enemy and self.board(c, piece.row).kind in ['Queen','Rook']:
                    return True

        elif piece.vert(king.position) and cell[0] != piece.col:
            if king.row < piece.row:
                direction = range(piece.row + 1, 9)
            else:
                direction = range(1, piece.row)[::-1]
            for r in direction:
                if self.board(piece.col, r) and self.board(piece.col, r).team == self.enemy and self.board(piece.col, r).kind in ['Queen','Rook']:
                    return True
                
        elif piece.diag(king.position) and not diag(cell, king.position):
            if king.col < piece.col:
                h_direction = range(piece.col + 1, 9)
            else:
                h_direction = range(1, piece.col)[::-1]
            if king.row < piece.row:
                v_direction = range(piece.row + 1, 9)
            else:
                v_direction = range(1, piece.row)[::-1]
            for c, r in zip(h_direction, v_direction):
                if self.board(c, r) and self.board(c, r).team == self.enemy and self.board(c, r).kind in ['Queen','Bishop']:
                    return True
                
        return False
    
    def leaves_in_check(self, piece_pos, move):
        mask = self.match.mask()
        own = mask.board(piece_pos)
                
        if mask.board(move):
            mask.board(move).team.alive.remove(mask.board(move))
        # TODO: Castling
        mask.board[piece_pos] = None
        own.position = move
        own.place()
        return mask[self].king.in_check()
    
    def check_moves(self):
        for piece in self.alive:
            for c in range(1, 9):
                for r in range(1, 9):
                    if piece.legal_moves((c,r)) and not self.reveals_check(piece, (c,r)) and not self.leaves_in_check(piece.position, (c,r)):
                        return True
            if piece.kind == 'King':
                if piece.legal_castle((piece.col, 1)) or piece.legal_castle((piece.col, 8)):
                    return True
        return False
            
        

class Board(dict):
    def __init__(self, match):
        super().__init__()
        self.match = match
        self.update({x:{y:None for y in range(1, 9)[::-1]} for x in range(1,9)})
    
    @property
    def df(self, alpha_cols = False):
        df = pd.DataFrame.from_dict({k:{kk:f'{kv.team.abbrev}{kv.kind}' if kv else None for kk, kv in v.items()} for k, v in self.items()}, orient = 'columns')
        if alpha_cols:
            df.columns = [num_dict[x] for x in df.columns]
        return df
    
    @property
    def display(self):
        df = pd.DataFrame.from_dict({k:{kk:f'{kv.team.abbrev}{kv.kind}' if kv else None for kk, kv in v.items()} for k, v in self.items()}, orient = 'columns')
        df.columns = [num_dict[x] for x in df.columns]
        return df
    
    def __call__(self, col, row = None):
        if row:
            return self[col][row]
        elif isinstance(col, tuple):
            return self[col[0]][col[1]]
        else:
            raise ValueError('Must define a col and row or tuple of (col, row)')
    
    def __setitem__(self, col, row, value = None):
        if value:
            self[col][row] = value
        elif isinstance(col, tuple):
            self[col[0]][col[1]] = row
        else:
            raise ValueError('Must define a col and row or tuple of (col, row)')


