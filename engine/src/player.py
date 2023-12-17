from .board import *
from .piece import *
from typing import List

class MoveStatus(Enum):
    DONE = True
    ILLEGAL_MOVE = False
    LEAVE_PLAYER_IN_CHECK = False
    def is_done(self):
        return self.value

class MoveTransition:
    def __init__(self, transition_board: Board, move: Move, move_status: MoveStatus) -> None:
        self._transition_board = transition_board
        self._move = move
        self._move_status = move_status
    def get_move_status(self) -> MoveStatus:
        return self._move_status
    def get_transition_board(self) -> Board:
        return self._transition_board

class Player:
    def __init__(self, board: Board, legal_moves: List[Move], opponent_moves: List[Move]) -> None:
        self._board = board
        self._player_king = self.establish_king()
        self._is_in_check = True if len(Player.calculate_attack_on_tile(self._player_king.get_position(), opponent_moves)) > 0 else False
        castling_moves = self.calculate_king_castle(legal_moves, opponent_moves)
        legal_moves.extend(castling_moves)
        self._legal_moves = legal_moves
        

    def get_player_king(self) -> King:
        return self._player_king
    
    def get_legal_moves(self) -> List[Move]:
        return self._legal_moves
    
    def is_move_legal(self, move: Move) -> bool:
        return move in self._legal_moves
    
    def is_in_check(self) -> bool:
        return self._is_in_check

    def is_in_checkmate(self) -> bool:
        return self._is_in_check and not self.has_escape_moves()
    
    def is_in_stalemate(self) -> bool:
        return not self._is_in_check and not self.has_escape_moves()
    
    def is_castled(self) -> bool:
        return self._player_king.is_castled()
    
    def is_king_side_castle_capable(self) -> bool:
        return self._player_king.is_king_side_castle_capable()
    
    def is_queen_side_castle_capable(self) -> bool:
        return self._player_king.is_queen_side_castle_capable()
    
    def has_castle_oppotunities(self) -> bool:
        return not self._is_in_check and (self._player_king.is_king_side_castle_capable() 
                                          or self._player_king.is_king_side_castle_capable())

    def establish_king(self) -> King:
        for piece in self.get_active_pieces():
            if piece.get_piece_type().is_king():
                return piece
        raise RuntimeError()

    def has_escape_moves(self) -> bool:
        for move in self._legal_moves:
            transition = self.make_move(move)
            if transition.get_move_status().is_done():
                return True
        return False

    def make_move(self, move: Move) -> MoveTransition:
        if not self.is_move_legal(move):
            return MoveTransition(self._board, move, MoveStatus.ILLEGAL_MOVE)
        transition_board = move.execute()
        king_attack = Player.calculate_attack_on_tile(transition_board.get_current_player().get_opponent().get_player_king().get_position(), 
                                                      transition_board.get_current_player().get_legal_moves())
        if len(king_attack) != 0:
            return MoveTransition(transition_board, move, MoveStatus.LEAVE_PLAYER_IN_CHECK)
        return MoveTransition(transition_board, move, MoveStatus.DONE)

    @abstractmethod
    def calculate_king_castle(self, legal_moves: List[Move], opponent_moves: List[Move]) -> List[Move]:
        pass

    @abstractmethod
    def get_active_pieces(self) -> List[Piece]:
        pass

    @abstractmethod
    def get_alliance(self) -> Alliance:
        pass

    @abstractmethod
    def get_opponent(self):
        '''Return opponent player'''
        pass

    @staticmethod
    def calculate_attack_on_tile(position: int, opponent_moves: List[Move]) -> List[Move]:
        attack_moves = []
        for move in opponent_moves:
            if move.get_destination_coordinate() == position:
                attack_moves.append(move)
        return attack_moves


class WhitePlayer(Player):
    def __init__(self, board: Board, legal_moves: List[Move], opponent_moves: List[Move]) -> None:
        super().__init__(board, legal_moves, opponent_moves)

    def get_active_pieces(self) -> List[Piece]:
        return self._board.get_white_piece()
    
    def get_alliance(self) -> Alliance:
        return Alliance.WHITE
    
    def get_opponent(self):
        return self._board.get_black_player()
    
    def calculate_king_castle(self, legal_moves: List[Move], opponent_moves: List[Move]) -> List[Move]:
        king_castle = []
        if not self.has_castle_oppotunities():
            return king_castle
        if self._player_king.is_first_move() and not self._is_in_check:
            if not self._board.get_tile(61).is_occupied() and \
               not self._board.get_tile(62).is_occupied():
                rook_tile = self._board.get_tile(63)
                if rook_tile.is_occupied() and rook_tile.get_piece().is_first_move():
                    if len(Player.calculate_attack_on_tile(61, opponent_moves)) == 0 and \
                       len(Player.calculate_attack_on_tile(61, opponent_moves)) == 0 and \
                       rook_tile.get_piece().get_piece_type().is_rook():
                        king_castle.append(KingSideCastleMove(self._board, self._player_king, 62,
                                                              rook_tile.get_piece(), rook_tile.get_coordinate(), 61))
            if not self._board.get_tile(59).is_occupied and \
               not self._board.get_tile(58).is_occupied() and \
               not self._board.get_tile(57).is_occupied():
                rook_tile = self._board.get_tile(56)
                if rook_tile.is_occupied() and rook_tile.get_piece().is_first_move():
                    if len(Player.calculate_attack_on_tile(59, opponent_moves)) == 0 and \
                       len(Player.calculate_attack_on_tile(58, opponent_moves)) == 0 and \
                       rook_tile.get_piece().get_piece_type().is_rook():
                        king_castle.append(QueenSideCastleMove(self._board, self._player_king, 58,
                                                              rook_tile.get_piece(), rook_tile.get_coordinate(), 59))
        return king_castle
    
    def __str__(self) -> str:
        return 'white'


class BlackPlayer(Player):
    def __init__(self, board: Board, legal_moves: List[Move], opponent_moves: List[Move]) -> None:
        super().__init__(board, legal_moves, opponent_moves)

    def get_active_pieces(self) -> List[Piece]:
        return self._board.get_black_piece()
    
    def get_alliance(self) -> Alliance:
        return Alliance.BLACK
    
    def get_opponent(self):
        return self._board.get_white_player()
    
    def calculate_king_castle(self, legal_moves: List[Move], opponent_moves: List[Move]) -> List[Move]:
        king_castle = []
        if not self.has_castle_oppotunities():
            return king_castle
        if self._player_king.is_first_move() and not self._is_in_check:
            if not self._board.get_tile(5).is_occupied() and \
               not self._board.get_tile(6).is_occupied():
                rook_tile = self._board.get_tile(7)
                if rook_tile.is_occupied() and rook_tile.get_piece().is_first_move():
                    if len(Player.calculate_attack_on_tile(5, opponent_moves)) == 0 and \
                       len(Player.calculate_attack_on_tile(6, opponent_moves)) == 0 and \
                       rook_tile.get_piece().get_piece_type().is_rook():
                        king_castle.append(KingSideCastleMove(self._board, self._player_king, 6,
                                                              rook_tile.get_piece(), rook_tile.get_coordinate(), 5))
            if not self._board.get_tile(1).is_occupied and \
               not self._board.get_tile(2).is_occupied() and \
               not self._board.get_tile(3).is_occupied():
                rook_tile = self._board.get_tile(0)
                if rook_tile.is_occupied() and rook_tile.get_piece().is_first_move():
                    if len(Player.calculate_attack_on_tile(2, opponent_moves)) == 0 and \
                       len(Player.calculate_attack_on_tile(3, opponent_moves)) == 0 and \
                       rook_tile.get_piece().get_piece_type().is_rook():
                        king_castle.append(QueenSideCastleMove(self._board, self._player_king, 2,
                                                              rook_tile.get_piece(), rook_tile.get_coordinate(), 3))
        return king_castle
    
    def __str__(self) -> str:
        return 'black'
