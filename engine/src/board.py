from abc import ABC, abstractmethod
from typing import List
from .alliance import Alliance

class Tile(ABC):
    def __init__(self, coordinate: int) -> None:
        self._coordinate = coordinate

    def get_coordinate(self) -> int:
        return self._coordinate
    
    @abstractmethod
    def get_piece(self):
        ''' return: Piece or None'''
        pass

    @abstractmethod
    def is_occupied(self) -> bool:
        pass
    
    @staticmethod
    def create_tile(coordinate: int, piece):
        if piece == None:
            return EmptyTile(coordinate)
        return OccupiedTile(coordinate, piece)

class EmptyTile(Tile):
    def __init__(self, coordinate: int) -> None:
        super().__init__(coordinate)

    def get_piece(self):
        return None
    
    def is_occupied(self) -> bool:
        return False
    
    def __str__(self) -> str:
        return '-'
    
class OccupiedTile(Tile):
    def __init__(self, coordinate: int, piece) -> None:
        ''' params: Piece - the piece on tile'''
        super().__init__(coordinate)
        self._piece = piece

    def get_piece(self):
        ''' return: Piece'''
        return self._piece
    
    def is_occupied(self) -> bool:
        return True
    
    def __str__(self) -> str:
        return str(self._piece)

   
class BoardUtils:
    NUMBER_TILES = 64
    NUMBER_TILES_PER_ROW = 8

    FISRT_COLUMN = None
    SECOND_COLUMN = None
    SEVENTH_COLUMN = None
    EIGHTH_COLUMN = None

    EIGHTH_RANK = None
    SEVENTH_RANK = None
    SIXTH_RANK = None
    FIFTH_RANK = None
    FOURTH_RANK = None
    THIRD_RANK = None
    SECOND_RANK = None
    FIRST_RANK = None

    ALGEBREIC_NOTATION = ["a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8",
                          "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
                          "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
                          "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
                          "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
                          "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
                          "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
                          "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"]

    @staticmethod
    def init_row(begin_index: int) -> List[bool]:
        row = [False] * BoardUtils.NUMBER_TILES
        row[begin_index] = True
        begin_index += 1
        while begin_index % BoardUtils.NUMBER_TILES_PER_ROW != 0:
            row[begin_index] = True
            begin_index += 1
        return row

    @staticmethod
    def init_column(column_number: int) -> List[bool]:
        column = [False] * BoardUtils.NUMBER_TILES
        while column_number < BoardUtils.NUMBER_TILES:
            column[column_number] = True
            column_number = column_number + 8
        return column
    
    @staticmethod
    def validate_tile_coordinate(coordinate: int) -> bool:
        return coordinate >= 0 and coordinate < BoardUtils.NUMBER_TILES
    
    @staticmethod
    def init():
        BoardUtils.FISRT_COLUMN = BoardUtils.init_column(0)
        BoardUtils.SECOND_COLUMN = BoardUtils.init_column(1)
        BoardUtils.SEVENTH_COLUMN = BoardUtils.init_column(6)
        BoardUtils.EIGHTH_COLUMN = BoardUtils.init_column(7)

        BoardUtils.EIGHTH_RANK = BoardUtils.init_row(0)
        BoardUtils.SEVENTH_RANK = BoardUtils.init_row(8)
        BoardUtils.SIXTH_RANK = BoardUtils.init_row(16)
        BoardUtils.FIFTH_RANK = BoardUtils.init_row(24)
        BoardUtils.FOURTH_RANK = BoardUtils.init_row(32)
        BoardUtils.THIRD_RANK = BoardUtils.init_row(40)
        BoardUtils.SECOND_RANK = BoardUtils.init_row(48)
        BoardUtils.FIRST_RANK = BoardUtils.init_row(56)

    @staticmethod
    def get_position_at_coordinate(coordinate: int) -> str:
        return BoardUtils.ALGEBREIC_NOTATION[coordinate]
    

class BoardBuilder:
    def __init__(self) -> None:
        self._board_config = {}
        self._next_move_maker = None
        self._enpassant_pawn = None
        
    def set_piece(self, piece):
        self._board_config[piece.get_position()] = piece

    def get_piece(self, coordinate: int):
        return self._board_config.get(coordinate)

    def set_move_maker(self, next_move_maker: Alliance):
        self._next_move_maker = next_move_maker

    def set_enpassant_pawn(self, enpassant_pawn):
        self._enpassant_pawn = enpassant_pawn

    def get_enpassant_pawn(self):
        return self._enpassant_pawn

    def build(self):
        return Board(self)


class Board:
    def __init__(self, builder: BoardBuilder) -> None:
        from .player import WhitePlayer, BlackPlayer
        self._game_board = Board.create_game_board(builder)
        self._white_pieces = self.calculate_active_pieces(Alliance.WHITE)
        self._black_pieces = self.calculate_active_pieces(Alliance.BLACK)
        self._enpassant_pawn = builder.get_enpassant_pawn()
        white_standart_legal_moves = self.calculate_legal_move(self._white_pieces)
        black_standart_legal_moves = self.calculate_legal_move(self._black_pieces)
        self._white_player = WhitePlayer(self, white_standart_legal_moves, black_standart_legal_moves)
        self._black_player = BlackPlayer(self, black_standart_legal_moves, white_standart_legal_moves)
        self._current_player = builder._next_move_maker.choose_player(self._white_player, self._black_player)
    
    def get_tile(self, coordinate: int) -> Tile:
        return self._game_board[coordinate]

    def get_white_player(self):
        return self._white_player
    
    def get_black_player(self):
        return self._black_player
    
    def get_current_player(self):
        return self._current_player
    
    def get_white_piece(self):
        return self._white_pieces
    
    def get_black_piece(self):
        return self._black_pieces
    
    def get_enpassant_pawn(self):
        return self._enpassant_pawn
    
    def calculate_active_pieces(self, alliance: Alliance):
        active_pieces = []
        for tile in self._game_board:
            if tile.is_occupied():
                piece = tile.get_piece()
                if piece.get_alliance() == alliance:
                    active_pieces.append(piece)
        return active_pieces

    def calculate_legal_move(self, pieces):
        '''Calculate legal moves of a set of piece'''
        legal_moves = []
        for piece in pieces:
            legal_moves.extend(piece.calculate_legal_move(self))
        return legal_moves
    
    @staticmethod
    def create_game_board(builder: BoardBuilder) -> List[Tile]:
        tiles = [None] * BoardUtils.NUMBER_TILES
        for i in range(0, BoardUtils.NUMBER_TILES):
            tiles[i] = Tile.create_tile(i, builder.get_piece(i))
        return tiles

    @staticmethod
    def create_standard_board():
        from .piece import Rook, Knight, Bishop, Queen, King, Pawn
        builder = BoardBuilder()

        builder.set_piece(Rook(0, Alliance.BLACK, None))
        builder.set_piece(Knight(1, Alliance.BLACK, None))
        builder.set_piece(Bishop(2, Alliance.BLACK, None))
        builder.set_piece(Queen(3, Alliance.BLACK, None))
        builder.set_piece(King(4, Alliance.BLACK, None, True, True))
        builder.set_piece(Bishop(5, Alliance.BLACK, None))
        builder.set_piece(Knight(6, Alliance.BLACK, None))
        builder.set_piece(Rook(7, Alliance.BLACK, None))
        builder.set_piece(Pawn(8, Alliance.BLACK, None))
        builder.set_piece(Pawn(9, Alliance.BLACK, None))
        builder.set_piece(Pawn(10, Alliance.BLACK, None))
        builder.set_piece(Pawn(11, Alliance.BLACK, None))
        builder.set_piece(Pawn(12, Alliance.BLACK, None))
        builder.set_piece(Pawn(13, Alliance.BLACK, None))
        builder.set_piece(Pawn(14, Alliance.BLACK, None))
        builder.set_piece(Pawn(15, Alliance.BLACK, None))

        builder.set_piece(Pawn(48, Alliance.WHITE, None))
        builder.set_piece(Pawn(49, Alliance.WHITE, None))
        builder.set_piece(Pawn(50, Alliance.WHITE, None))
        builder.set_piece(Pawn(51, Alliance.WHITE, None))
        builder.set_piece(Pawn(52, Alliance.WHITE, None))
        builder.set_piece(Pawn(53, Alliance.WHITE, None))
        builder.set_piece(Pawn(54, Alliance.WHITE, None))
        builder.set_piece(Pawn(55, Alliance.WHITE, None))
        builder.set_piece(Rook(56, Alliance.WHITE, None))
        builder.set_piece(Knight(57, Alliance.WHITE, None))
        builder.set_piece(Bishop(58, Alliance.WHITE, None))
        builder.set_piece(Queen(59, Alliance.WHITE, None))
        builder.set_piece(King(60, Alliance.WHITE, None, True, True))
        builder.set_piece(Bishop(61, Alliance.WHITE, None))
        builder.set_piece(Knight(62, Alliance.WHITE, None))
        builder.set_piece(Rook(63, Alliance.WHITE, None))

        builder.set_move_maker(Alliance.WHITE)
        return builder.build()
    
    def get_all_legal_moves(self):
        ''' Return all legal moves of 2 players'''
        all_legal_moves = []
        all_legal_moves.extend(self._white_player.get_legal_moves())
        all_legal_moves.extend(self._black_player.get_legal_moves())
        return all_legal_moves

    def __str__(self) -> str:
        out_str = ''
        for i in range(0, BoardUtils.NUMBER_TILES):
            tile_text = str(self._game_board[i])
            out_str += '  ' + tile_text
            if i % BoardUtils.NUMBER_TILES_PER_ROW == 7:
                out_str += '\n'
        return out_str
    

class Move:
    def __init__(self, board: Board, moved_piece, destination_coordinate: int) -> None:
        self._board = board
        self._moved_piece = moved_piece
        self._destination_coordinate = destination_coordinate
        self._is_first_move = moved_piece.is_first_move() #TODO: why don't delete this ?

    def __eq__(self, __value: object) -> bool:
        if __value is None:
            return False
        if not isinstance(__value, Move):
            return False
        return self._destination_coordinate == __value._destination_coordinate and \
               self._moved_piece == __value._moved_piece
               # self._moved_piece.get_position() == __value._moved_piece.get_position()
    
    def __hash__(self) -> int:
        result = self._destination_coordinate * 31
        result = result * 31 + hash(self._moved_piece)
        result = result * 31 + self._moved_piece.get_position()
        return result

    def get_board(self) -> Board:
        return self._board
    
    def get_current_coordinate(self) -> int:
        return self._moved_piece.get_position()
    
    def get_destination_coordinate(self) -> int:
        return self._destination_coordinate
    
    def get_moved_piece(self):
        return self._moved_piece
    
    def execute(self) -> Board:
        ''' Return new Board instance after this move is executed '''
        builder = BoardBuilder()
        for piece in self._board.get_current_player().get_active_pieces():
            if not piece == self._moved_piece:
                builder.set_piece(piece)
        for piece in self._board.get_current_player().get_opponent().get_active_pieces():
            builder.set_piece(piece)
        builder.set_piece(self._moved_piece.move(self))
        builder.set_move_maker(self._board.get_current_player().get_opponent().get_alliance())
        return builder.build()

    def is_attack(self) -> bool:
        return False
    
    def get_attacked_piece(self):
        return None
    
    def is_castling_move(self) -> bool:
        return False

    def __str__(self) -> str:
        return str(self._moved_piece) + ' : ' + BoardUtils.get_position_at_coordinate(self._moved_piece.get_position()) + \
        ' --> ' + BoardUtils.get_position_at_coordinate(self._destination_coordinate)
    

class MajorMove(Move):
    def __init__(self, board: Board, moved_piece, destination_coordinate: int) -> None:
        super().__init__(board, moved_piece, destination_coordinate)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, MajorMove) and super().__eq__(__value)
    

class AttackMove(Move):
    def __init__(self, board: Board, moved_piece, destination_coordinate: int, attacked_piece) -> None:
        super().__init__(board, moved_piece, destination_coordinate)
        self._attacked_piece = attacked_piece

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, AttackMove) and \
               self._attacked_piece == __value._attacked_piece and \
               super().__eq__(__value)
    
    def __hash__(self) -> int:
        return super().__hash__() + hash(self._attacked_piece)

    def get_attacked_piece(self):
        return self._attacked_piece
    
    def is_attack(self) -> bool:
        return True
    

class MajorAttackMove(AttackMove):
    def __init__(self, board: Board, moved_piece, destination_coordinate: int, attacked_piece) -> None:
        super().__init__(board, moved_piece, destination_coordinate, attacked_piece)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, MajorAttackMove) and super().__eq__(__value)

    
class PawnMove(Move):
    def __init__(self, board: Board, moved_piece, destination_coordinate: int) -> None:
        super().__init__(board, moved_piece, destination_coordinate)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PawnMove) and super().__eq__(__value)


class PawnJump(Move):
    def __init__(self, board: Board, moved_piece, destination_coordinate: int) -> None:
        super().__init__(board, moved_piece, destination_coordinate)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PawnJump) and super().__eq__(__value)

    def execute(self) -> Board:
        ''' Return new Board instance after this move is executed '''
        builder = BoardBuilder()
        for piece in self._board.get_current_player().get_active_pieces():
            if not piece == self._moved_piece:
                builder.set_piece(piece)
        for piece in self._board.get_current_player().get_opponent().get_active_pieces():
            builder.set_piece(piece)
        pawn_moved = self._moved_piece.move(self)
        builder.set_piece(pawn_moved)
        builder.set_enpassant_pawn(pawn_moved)
        builder.set_move_maker(self._board.get_current_player().get_opponent().get_alliance())  
        return builder.build()



class PawnAttackMove(AttackMove):
    def __init__(self, board: Board, moved_piece, destination_coordinate: int, attacked_piece) -> None:
        super().__init__(board, moved_piece, destination_coordinate, attacked_piece)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PawnAttackMove) and super().__eq__(__value)


class PawnPromotionMove(Move):
    def __init__(self, wrapped_move: Move) -> None:
        self._wrapped_move = wrapped_move
        self._promoted_pawn = wrapped_move.get_moved_piece()
        super().__init__(wrapped_move.get_board(), wrapped_move.get_moved_piece(), wrapped_move.get_destination_coordinate())
    
    def __hash__(self) -> int:
        return hash(self._wrapped_move) + hash(self._promoted_pawn)
    
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PawnPromotionMove) and super().__eq__(__value)
    
    def execute(self) -> Board:
        ''' Return new Board instance after this move is executed '''
        pawn_moved_board = self._wrapped_move.execute()
        builder = BoardBuilder()
        for piece in pawn_moved_board.get_current_player().get_opponent().get_active_pieces():
            if not piece == self._promoted_pawn:
                builder.set_piece(piece)
        for piece in pawn_moved_board.get_current_player().get_active_pieces():
            builder.set_piece(piece)
        builder.set_piece(self._promoted_pawn.get_promotion_piece().move())
        builder.set_move_maker(self._board.get_current_player().get_alliance())
        return builder.build()
    
    def is_attack(self) -> bool:
        return self._wrapped_move.is_attack()
    
    def get_attacked_piece(self):
        return self._wrapped_move.get_attacked_piece()
    

class PawnEnpassantAttackMove(PawnAttackMove):
    def __init__(self, board: Board, moved_piece, destination_coordinate: int, attacked_piece) -> None:
        super().__init__(board, moved_piece, destination_coordinate, attacked_piece)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PawnEnpassantAttackMove) and super().__eq__(__value)
    
    def execute(self) -> Board:
        ''' Return new Board instance after this move is executed '''
        builder = BoardBuilder()
        for piece in self._board.get_current_player().get_active_pieces():
            if not piece == self._moved_piece:
                builder.set_piece(piece)
        for piece in self._board.get_current_player().get_opponent().get_active_pieces():
            if not piece == self._attacked_piece:
                builder.set_piece(piece)
        builder.set_piece(self._moved_piece.move(self))
        builder.set_move_maker(self._board.get_current_player().get_opponent().get_alliance())
        return builder.build()
    
class CastleMove(Move):
    def __init__(self, board: Board, moved_piece, destination_coordinate: int,
                 castle_rook, castle_rook_start: int, castle_rook_destination: int) -> None:
        self._castle_rook = castle_rook
        self._castle_rook_start = castle_rook_start
        self._castle_rook_destination = castle_rook_destination
        super().__init__(board, moved_piece, destination_coordinate)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, CastleMove) and \
               self._castle_rook == __value._castle_rook and \
               super().__eq__(__value)
    
    def __hash__(self) -> int:
        result = super.__hash__() * 31
        result = result * 31 + hash(self._castle_rook)
        result = result * 31 + self._castle_rook_destination
        return result

    def is_castling_move(self) -> bool:
        return True
    
    def execute(self) -> Board:
        from .piece import Rook
        ''' Return new Board instance after this move is executed '''
        builder = BoardBuilder()
        for piece in self._board.get_current_player().get_active_pieces():
            if not piece == self._moved_piece and not piece == self._castle_rook:
                builder.set_piece(piece)
        for piece in self._board.get_current_player().get_opponent().get_active_pieces():
            builder.set_piece(piece)
        builder.set_piece(self._moved_piece.move())
        builder.set_piece(Rook(self._castle_rook_destination, self._castle_rook.get_alliance(), False))
        builder.set_move_maker(self._board.get_current_player().get_opponent().get_alliance())
        return builder.build()
    
class KingSideCastleMove(CastleMove):
    def __init__(self, board: Board, moved_piece, destination_coordinate: int, 
                 castle_rook, castle_rook_start: int, castle_rook_destination: int) -> None:
        super().__init__(board, moved_piece, destination_coordinate, 
                         castle_rook, castle_rook_start, castle_rook_destination)
        
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, KingSideCastleMove) and super().__eq__(__value)
    
    def __str__(self) -> str:
        return '0-0'


class QueenSideCastleMove(CastleMove):
    def __init__(self, board: Board, moved_piece, destination_coordinate: int, 
                 castle_rook, castle_rook_start: int, castle_rook_destination: int) -> None:
        super().__init__(board, moved_piece, destination_coordinate, 
                         castle_rook, castle_rook_start, castle_rook_destination)
        
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, QueenSideCastleMove) and super().__eq__(__value)
    
    def __str__(self) -> str:
        return '0-0-0'

class MoveFactory:
    @staticmethod
    def create_move(board: Board, current_coordinate: int, destination_coordinate: int) -> Move:
        for move in board.get_all_legal_moves():
            if move.get_current_coordinate() == current_coordinate and \
               move.get_destination_coordinate() == destination_coordinate:
                return move


