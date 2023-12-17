from abc import ABC, abstractmethod
from enum import Enum
from typing import List
from .board import *

class PieceType(Enum):
    PAWN = 'P'
    KNIGHT = 'N'
    BISHOP = 'B'
    ROOK = 'R'
    QUEEN = 'Q'
    KING = 'K'

    def __str__(self) -> str:
        return self.value
    def is_king(self) -> bool:
        return self.value == 'K'
    def is_rook(self) -> bool:
        return self.value == 'R'
    def get_piece_value(self) -> int:
        value = {'P':100, 'N':300, 'B':300, 'R':500, 'Q':900, 'K':10000}
        return value[self.value]

class Piece(ABC):
    def __init__(self, piece_type: PieceType, 
                 position: int, 
                 alliance: Alliance, 
                 is_first_move: bool) -> None:
        self._piece_type = piece_type
        self._position = position
        self._alliance = alliance
        self._is_first_move = is_first_move

    def get_piece_type(self) -> PieceType:
        return self._piece_type
    def get_position(self) -> int:
        return self._position
    def get_alliance(self) -> Alliance:
        return self._alliance
    def is_first_move(self) -> bool:
        return self._is_first_move
    def get_piece_value(self) -> int:
        return self._piece_type.get_piece_value()
    
    @abstractmethod
    def calculate_legal_move(self, board: Board) -> List[Move]:
        pass

    @abstractmethod
    def move(self, move: Move):
        ''' Return a piece that identical this piece, except the position, it is this piece after execute the move'''
        pass

    def __eq__(self, __value: object) -> bool:
        if __value is None:
            return False
        if not isinstance(__value, Piece):
            return False
        return self._piece_type == __value._piece_type and \
               self._position == __value._position and \
               self._alliance == __value._alliance and \
               self._is_first_move == __value._is_first_move
    
    def __hash__(self) -> int:
        result = hash(self._piece_type)
        result = result * 31 + self._position
        result = result * 31 + hash(self._alliance)
        result = result * 31 + (1 if self._is_first_move else 0)
        return result
    
    def __str__(self) -> str:
        if self._alliance.is_black():
            return self._piece_type.value.lower()
        return self._piece_type.value

class Knight(Piece):
    CANDIDATE_MOVE_COORDINATES = (-17, -15, -10, -6, 6, 10, 15, 17)

    def __init__(self, position: int, alliance: Alliance, is_first_move: bool) -> None:
        if is_first_move == None:
            super().__init__(PieceType.KNIGHT, position, alliance, True)
        else:
            super().__init__(PieceType.KNIGHT, position, alliance, is_first_move)
        
    def calculate_legal_move(self, board: Board) -> List[Move]:
        legal_moves = []
        for candidate in Knight.CANDIDATE_MOVE_COORDINATES:
            if self.first_column_exclusion(candidate) or \
               self.second_column_exclusion(candidate) or \
               self.seventh_column_exclusion(candidate) or \
               self.eigth_column_exclusion(candidate) :
                continue
            destination_coordinate = self._position + candidate
            if BoardUtils.validate_tile_coordinate(destination_coordinate):
                destination_tile = board.get_tile(destination_coordinate)
                if not destination_tile.is_occupied():
                    legal_moves.append(MajorMove(board, self, destination_coordinate))
                else:
                    piece_at_destination = destination_tile.get_piece()
                    if piece_at_destination.get_alliance() != self._alliance:
                        legal_moves.append(MajorAttackMove(board, self, destination_coordinate, piece_at_destination))
        return legal_moves
            
    def move(self, move: Move):
        return Knight(move.get_destination_coordinate(), self._alliance, False)

    def first_column_exclusion(self, candidate: int) -> bool:
        return BoardUtils.FISRT_COLUMN[self._position] and candidate in (-17, -10, 6, 15) 

    def second_column_exclusion(self, candidate: int) -> bool:
        return BoardUtils.SECOND_COLUMN[self._position] and candidate in (-10, 6)
    
    def seventh_column_exclusion(self, candidate: int) -> bool:
        return BoardUtils.SEVENTH_COLUMN[self._position] and candidate in (-6, 10)
    
    def eigth_column_exclusion(self, candidate: int) -> bool:
        return BoardUtils.EIGHTH_COLUMN[self._position] and candidate in (-15, -6, 10, 17)
    
class Bishop(Piece):
    CANDIDATE_MOVE_COORDINATES = (-9, -7, 9, 7)

    def __init__(self, position: int, alliance: Alliance, is_first_move: bool) -> None:
        if is_first_move == None:
            super().__init__(PieceType.BISHOP, position, alliance, True)
        else:
            super().__init__(PieceType.BISHOP, position, alliance, is_first_move)

    def calculate_legal_move(self, board: Board) -> List[Move]:
        legal_moves = []
        for candidate in Bishop.CANDIDATE_MOVE_COORDINATES:
            destination_coordinate = self._position
            while BoardUtils.validate_tile_coordinate(destination_coordinate):
                if self.first_column_exclusion(candidate) or \
                   self.eigth_column_exclusion(candidate):
                    break
                destination_coordinate += candidate
                if BoardUtils.validate_tile_coordinate(destination_coordinate):
                    destination_tile = board.get_tile(destination_coordinate)
                    if not destination_tile.is_occupied():
                        legal_moves.append(MajorMove(board, self, destination_coordinate))
                    else:
                        piece_at_destination = destination_tile.get_piece()
                        if piece_at_destination.get_alliance() != self._alliance:
                            legal_moves.append(MajorAttackMove(board, self, destination_coordinate, piece_at_destination))
                        break
        return legal_moves

    def move(self, move: Move):
        return Bishop(move.get_destination_coordinate(), self._alliance, False)
    
    def first_column_exclusion(self, candidate: int) -> bool:
        return BoardUtils.FISRT_COLUMN[self._position] and candidate in (-9, 7) 
    
    def eigth_column_exclusion(self, candidate: int) -> bool:
        return BoardUtils.EIGHTH_COLUMN[self._position] and candidate in (-7, 9)
    
class Rook(Piece):
    CANDIDATE_MOVE_COORDINATES = (-8, -1, 1, 8)
    
    def __init__(self, position: int, alliance: Alliance, is_first_move: bool) -> None:
        if is_first_move == None:
            super().__init__(PieceType.ROOK, position, alliance, True)
        else:
            super().__init__(PieceType.ROOK, position, alliance, is_first_move)

    def calculate_legal_move(self, board: Board) -> List[Move]:
        legal_moves = []
        for candidate in Rook.CANDIDATE_MOVE_COORDINATES:
            destination_coordinate = self._position
            while BoardUtils.validate_tile_coordinate(destination_coordinate):
                if self.first_column_exclusion(candidate) or \
                   self.eigth_column_exclusion(candidate):
                    break
                destination_coordinate += candidate
                if BoardUtils.validate_tile_coordinate(destination_coordinate):
                    destination_tile = board.get_tile(destination_coordinate)
                    if not destination_tile.is_occupied():
                        legal_moves.append(MajorMove(board, self, destination_coordinate))
                    else:
                        piece_at_destination = destination_tile.get_piece()
                        if piece_at_destination.get_alliance() != self._alliance:
                            legal_moves.append(MajorAttackMove(board, self, destination_coordinate, piece_at_destination))
                        break
        return legal_moves

    def move(self, move: Move):
        return Rook(move.get_destination_coordinate(), self._alliance, False)
    
    def first_column_exclusion(self, candidate: int) -> bool:
        return BoardUtils.FISRT_COLUMN[self._position] and candidate == -1
    
    def eigth_column_exclusion(self, candidate: int) -> bool:
        return BoardUtils.EIGHTH_COLUMN[self._position] and candidate == 1
    
class Queen(Piece):
    CANDIDATE_MOVE_COORDINATES = (-9, -8, -7, -1, 1, 7, 8, 9)
    
    def __init__(self, position: int, alliance: Alliance, is_first_move: bool) -> None:
        if is_first_move == None:
            super().__init__(PieceType.QUEEN, position, alliance, True)
        else:
            super().__init__(PieceType.QUEEN, position, alliance, is_first_move)

    def calculate_legal_move(self, board: Board) -> List[Move]:
        legal_moves = []
        for candidate in Queen.CANDIDATE_MOVE_COORDINATES:
            destination_coordinate = self._position
            while BoardUtils.validate_tile_coordinate(destination_coordinate):
                if self.first_column_exclusion(candidate) or \
                   self.eigth_column_exclusion(candidate):
                    break
                destination_coordinate += candidate
                if BoardUtils.validate_tile_coordinate(destination_coordinate):
                    destination_tile = board.get_tile(destination_coordinate)
                    if not destination_tile.is_occupied():
                        legal_moves.append(MajorMove(board, self, destination_coordinate))
                    else:
                        piece_at_destination = destination_tile.get_piece()
                        if piece_at_destination.get_alliance() != self._alliance:
                            legal_moves.append(MajorAttackMove(board, self, destination_coordinate, piece_at_destination))
                        break
        return legal_moves
    
    def move(self, move: Move):
        return Queen(move.get_destination_coordinate(), self._alliance, False)
    
    def first_column_exclusion(self, candidate: int) -> bool:
        return BoardUtils.FISRT_COLUMN[self._position] and candidate in (-1, -9, 7) 
    
    def eigth_column_exclusion(self, candidate: int) -> bool:
        return BoardUtils.EIGHTH_COLUMN[self._position] and candidate in (-7, 1, 9)
    
class King(Piece):
    CANDIDATE_MOVE_COORDINATES = (-9, -8, -7, -1, 1, 7, 8, 9)

    def __init__(self, position: int, alliance: Alliance, is_first_move: bool,
                 king_side_castle_capable: bool, queen_side_castle_capable: bool) -> None:
        if is_first_move == None:
            super().__init__(PieceType.KING, position, alliance, True)
        else:
            super().__init__(PieceType.KING, position, alliance, is_first_move)
        self._king_side_castle_capable = king_side_castle_capable
        self._queen_side_castle_capable = queen_side_castle_capable
        self._is_castled = False

    def is_king_side_castle_capable(self) -> bool:
        return self._king_side_castle_capable
    
    def is_queen_side_castle_capable(self) -> bool:
        return self._queen_side_castle_capable
    
    def is_castled(self) -> bool:
        return self._is_castled
    
    def set_castle(self, castled: bool) -> None:
        self._is_castled = castled
    
    def calculate_legal_move(self, board: Board) -> List[Move]:
        legal_moves = []
        for candidate in King.CANDIDATE_MOVE_COORDINATES:
            if self.first_column_exclusion(candidate) or \
               self.eigth_column_exclusion(candidate):
                continue
            destination_coordinate = self._position + candidate
            if BoardUtils.validate_tile_coordinate(destination_coordinate):
                destination_tile = board.get_tile(destination_coordinate)
                if not destination_tile.is_occupied():
                    legal_moves.append(MajorMove(board, self, destination_coordinate))
                else:
                    piece_at_destination = destination_tile.get_piece()
                    if piece_at_destination.get_alliance() != self._alliance:
                        legal_moves.append(MajorAttackMove(board, self, destination_coordinate, piece_at_destination))
        return legal_moves

    def move(self, move: Move):
        king = King(move.get_destination_coordinate(), self._alliance, False, False, False)
        king.set_castle(move.is_castling_move())
        return king    

    def first_column_exclusion(self, candidate: int) -> bool:
        return BoardUtils.FISRT_COLUMN[self._position] and candidate in (-1, -9, 7) 
    
    def eigth_column_exclusion(self, candidate: int) -> bool:
        return BoardUtils.EIGHTH_COLUMN[self._position] and candidate in (-7, 1, 9)
    
class Pawn(Piece):
    CANDIDATE_MOVE_COORDINATES = (8, 16, 7, 9)

    def __init__(self, position: int, alliance: Alliance, is_first_move: bool) -> None:
        if is_first_move == None:
            super().__init__(PieceType.PAWN, position, alliance, True)
        else:
            super().__init__(PieceType.PAWN, position, alliance, is_first_move)

    def calculate_legal_move(self, board: Board) -> List[Move]:
        legal_moves = []
        for candidate in Pawn.CANDIDATE_MOVE_COORDINATES:
            destination_coordinate = self._position + self._alliance.get_direction() * candidate
            if not BoardUtils.validate_tile_coordinate(destination_coordinate):
                continue
            if candidate == 8 and not board.get_tile(destination_coordinate).is_occupied():
                if self._alliance.is_pawn_promotion_square(destination_coordinate):
                    legal_moves.append(PawnPromotionMove(PawnMove(board, self, destination_coordinate)))
                else:
                    legal_moves.append(PawnMove(board, self, destination_coordinate))
            elif candidate == 16 and self._is_first_move and \
                 ((BoardUtils.SEVENTH_RANK[self._position] and self._alliance.is_black()) or 
                  (BoardUtils.SECOND_RANK[self._position] and self._alliance.is_white())):
                behind_destination_coordinate = self._position + self._alliance.get_direction() * 8
                if not board.get_tile(destination_coordinate).is_occupied() and \
                   not board.get_tile(behind_destination_coordinate).is_occupied():
                    legal_moves.append(PawnJump(board, self, destination_coordinate))
            elif candidate == 7 and not ((BoardUtils.EIGHTH_COLUMN[self._position] and self._alliance.is_white()) or \
                                        (BoardUtils.FISRT_COLUMN[self._position] and self._alliance.is_black())):
                if board.get_tile(destination_coordinate).is_occupied():
                    piece_at_destination = board.get_tile(destination_coordinate).get_piece()
                    if piece_at_destination.get_alliance() != self._alliance:
                        if self._alliance.is_pawn_promotion_square(destination_coordinate):
                            legal_moves.append(PawnPromotionMove(PawnAttackMove(board, self, destination_coordinate, piece_at_destination)))
                        else:
                            legal_moves.append(PawnAttackMove(board, self, destination_coordinate, piece_at_destination))
                elif board.get_enpassant_pawn():
                    if board.get_enpassant_pawn().get_position() == self._position + self._alliance.get_opposite_direction():
                        piece_at_destination = board.get_enpassant_pawn()
                        if self._alliance != piece_at_destination.get_alliance():
                            legal_moves.append(PawnEnpassantAttackMove(board, self, destination_coordinate, piece_at_destination))
            elif candidate == 9 and not ((BoardUtils.EIGHTH_COLUMN[self._position] and self._alliance.is_black()) or \
                                        (BoardUtils.FISRT_COLUMN[self._position] and self._alliance.is_white())):
                if board.get_tile(destination_coordinate).is_occupied():
                    piece_at_destination = board.get_tile(destination_coordinate).get_piece()
                    if piece_at_destination.get_alliance() != self._alliance:
                        if self._alliance.is_pawn_promotion_square(destination_coordinate):
                            legal_moves.append(PawnPromotionMove(PawnAttackMove(board, self, destination_coordinate, piece_at_destination)))
                        else:
                            legal_moves.append(PawnAttackMove(board, self, destination_coordinate, piece_at_destination))
                elif board.get_enpassant_pawn():
                    if board.get_enpassant_pawn().get_position() == self._position - self._alliance.get_opposite_direction():
                        piece_at_destination = board.get_enpassant_pawn()
                        if self._alliance != piece_at_destination.get_alliance():
                            legal_moves.append(PawnEnpassantAttackMove(board, self, destination_coordinate, piece_at_destination))
        return legal_moves
    
    def move(self, move: Move):
        return Pawn(move.get_destination_coordinate(), self._alliance, False)
    
    def get_promotion_piece(self) ->  Queen:
        return Queen(self._position, self._alliance, False)
