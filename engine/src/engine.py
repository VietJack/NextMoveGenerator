from .board import *
from .piece import *
from .player import Player

class BoardEvaluator:
    CHECK_BONUS = 50
    CHECK_MATE_BONUS = 10000
    DEPTH_BONUS = 100
    CASTLE_BONUS = 60
    MOBILITY_BONUS = 100

    def evaluate(self, board: Board, depth: int) -> int:
        return self.score_player(board.get_white_player(), depth) - self.score_player(board.get_black_player(), depth)
    
    def score_player(self, player: Player, depth: int) -> int:
        return BoardEvaluator.piece_value(player) + BoardEvaluator.mobility(player) + BoardEvaluator.check(player) + \
        BoardEvaluator.checkmate(player, depth) + BoardEvaluator.castle(player)

    @staticmethod
    def castle(player: Player) -> int:
        return BoardEvaluator.CASTLE_BONUS if player.is_castled() else 0
    
    @staticmethod
    def checkmate(player: Player, depth: int) -> int:
        return BoardEvaluator.CHECK_MATE_BONUS * BoardEvaluator.depth_bonus(depth) if player.get_opponent().is_in_checkmate() else 0

    @staticmethod
    def check(player: Player) -> int:
        return BoardEvaluator.CHECK_BONUS if player.get_opponent().is_in_check() else 0
    
    @staticmethod
    def mobility(player: Player) -> int:
        return len(player.get_legal_moves()) * BoardEvaluator.MOBILITY_BONUS
    
    @staticmethod
    def depth_bonus(depth: int) -> int:
        return BoardEvaluator.DEPTH_BONUS * depth if depth != 0 else 1
    
    @staticmethod
    def piece_value(player: Player) -> int:
        total_value = 0
        for piece in player.get_active_pieces():
            total_value += piece.get_piece_value()
        return total_value
    
# import time
class MiniMax:
    
    def __init__(self, depth: int) -> None:
        self._depth = depth
        self._board_evaluator = BoardEvaluator()

    def min(self, board: Board, depth: int, alpha: int, beta: int) -> int:
        if depth == 0 or board.get_current_player().is_in_checkmate() or board.get_current_player().is_in_stalemate():
            return self._board_evaluator.evaluate(board, depth)
        lowest_seen_value = 500000000
        for move in board.get_current_player().get_legal_moves():
            transition = board.get_current_player().make_move(move)
            if transition.get_move_status().is_done():
                current_value = self.max(transition.get_transition_board(), depth - 1, alpha, beta)
                lowest_seen_value = min(current_value, lowest_seen_value)
                beta = min(beta, current_value)
                if beta <= alpha:
                    break
        return lowest_seen_value

    def max(self, board: Board, depth: int, alpha: int, beta: int) -> int:
        if depth == 0 or board.get_current_player().is_in_checkmate() or board.get_current_player().is_in_stalemate():
            return self._board_evaluator.evaluate(board, depth)
        highest_seen_value = -500000000
        for move in board.get_current_player().get_legal_moves():
            transition = board.get_current_player().make_move(move)
            if transition.get_move_status().is_done():
                current_value = self.min(transition.get_transition_board(), depth - 1, alpha, beta)
                highest_seen_value = max(current_value, highest_seen_value)
                alpha = max(alpha, current_value)
                if beta <= alpha:
                    break
        return highest_seen_value 
    
    def execute(self, board: Board) -> Move:
        best_move = None
        highest_seen_value = -500000000
        lowest_seen_value = 500000000
        current_value = None
        #start = time.time()
        print('Computer is thinking ...')
        for move in board.get_current_player().get_legal_moves():
            transition = board.get_current_player().make_move(move)
            if transition.get_move_status().is_done():
                current_value = self.min(transition.get_transition_board(), self._depth - 1, -50000000, 5000000) \
                                if board.get_current_player().get_alliance().is_white() \
                                else self.max(transition.get_transition_board(), self._depth - 1, -50000000, 5000000)
                if board.get_current_player().get_alliance().is_white():
                    highest_seen_value = max(current_value, highest_seen_value)
                    best_move = move
                elif board.get_current_player().get_alliance().is_black():
                    lowest_seen_value = min(current_value, lowest_seen_value)
                    best_move = move
        # print(time.time() - start)
        return best_move


class FenUtilities:
    @staticmethod
    def create_game_from_fen(fen_str: str) -> Board:
        return FenUtilities.parseFEN(fen_str)
    
    def create_fen_from_game(board: Board) -> str:
        result = FenUtilities.calculate_board_text(board) + ' ' + \
                 FenUtilities.calculate_player_text(board) + ' ' + \
                 FenUtilities.calculate_castle_text(board) + ' ' + \
                 FenUtilities.calculate_enpassant_square_text(board) + ' 0 1'
        return result

    @staticmethod
    def parseFEN(fen_str: str) -> Board:
        fen_partitions = fen_str.split(' ')
        builder = BoardBuilder()
        white_king_side_castle = FenUtilities.white_king_side_castle(fen_partitions[2])
        white_queen_side_castle = FenUtilities.white_queen_side_castle(fen_partitions[2])
        black_king_side_castle = FenUtilities.black_king_side_castle(fen_partitions[2])
        black_queen_side_castle = FenUtilities.black_queen_side_castle(fen_partitions[2])
        game_config = fen_partitions[0]
        board_tiles = game_config.replace('/', '').\
        replace('8', '--------').\
        replace('7', '-------').\
        replace('6', '------').\
        replace('5', '-----').\
        replace('4', '----').\
        replace('3', '---').\
        replace('2', '--').\
        replace('1', '-')
        i = 0
        while i < len(board_tiles):
            match board_tiles[i]:
                case 'r':
                    builder.set_piece(Rook(i, Alliance.BLACK, None));
                    i += 1
                case 'n':
                    builder.set_piece(Knight(i, Alliance.BLACK, None));
                    i += 1
                case 'b':
                    builder.set_piece(Bishop(i, Alliance.BLACK, None));
                    i += 1
                case 'q':
                    builder.set_piece(Queen(i, Alliance.BLACK, None));
                    i += 1
                case 'k':
                    builder.set_piece(King(i, Alliance.BLACK, None, black_king_side_castle, black_queen_side_castle))
                    i += 1
                case 'p':
                    builder.set_piece(Pawn(i, Alliance.BLACK, None));
                    i += 1
                case 'R':
                    builder.set_piece(Rook(i, Alliance.WHITE, None));
                    i += 1
                case 'N':
                    builder.set_piece(Knight(i, Alliance.WHITE, None));
                    i += 1
                case 'B':
                    builder.set_piece(Bishop(i, Alliance.WHITE, None));
                    i += 1
                case 'Q':
                    builder.set_piece(Queen(i, Alliance.WHITE, None));
                    i += 1
                case 'K':
                    builder.set_piece(King(i, Alliance.WHITE, None, white_king_side_castle, white_queen_side_castle))
                    i += 1
                case 'P':
                    builder.set_piece(Pawn(i, Alliance.WHITE, None));
                    i += 1
                case '-':
                    i += 1
        builder.set_move_maker(FenUtilities.move_maker(fen_partitions[1]))
        return builder.build()


    @staticmethod
    def white_king_side_castle(fen_castle: str) -> bool:
        return 'K' in fen_castle
    @staticmethod
    def white_queen_side_castle(fen_castle: str) -> bool:
        return 'Q' in fen_castle
    @staticmethod
    def black_king_side_castle(fen_castle: str) -> bool:
        return 'k' in fen_castle 
    @staticmethod
    def black_queen_side_castle(fen_castle: str) -> bool:
        return 'q' in fen_castle
    @staticmethod
    def move_maker(fen_move_maker: str) -> Alliance:
        if fen_move_maker == 'w':
            return Alliance.WHITE
        elif fen_move_maker == 'b':
            return Alliance.BLACK
        else:
            raise RuntimeError()
        
    @staticmethod
    def calculate_board_text(board: Board) -> str:
        board_text = ''
        for i in range(0, BoardUtils.NUMBER_TILES):
            tile_text = str(board.get_tile(i))
            board_text += tile_text
        board_text = FenUtilities.insert(board_text, 8)
        board_text = FenUtilities.insert(board_text, 17)
        board_text = FenUtilities.insert(board_text, 26)
        board_text = FenUtilities.insert(board_text, 35)
        board_text = FenUtilities.insert(board_text, 44)
        board_text = FenUtilities.insert(board_text, 53)
        board_text = FenUtilities.insert(board_text, 62)
        board_text = board_text.replace('--------', '8').\
                   replace('-------', '7').\
                   replace('------', '6').\
                   replace('-----', '5').\
                   replace('----', '4').\
                   replace('---', '3').\
                   replace('--', '2').\
                   replace('-', '1')
        return board_text                                      
    @staticmethod
    def insert(text, offset) -> str:
        return text[:offset] + '/' + text[offset:]
    @staticmethod
    def calculate_player_text(board: Board) -> str:
        return board.get_current_player().get_alliance().value.lower()
    @staticmethod
    def calculate_enpassant_square_text(board: Board) -> str:
        enpassant_pawn = board.get_enpassant_pawn()
        if enpassant_pawn:
            return BoardUtils.get_position_at_coordinate(enpassant_pawn.get_position() + enpassant_pawn.get_alliance().get_opposite_direction() * 8)
        return '-'
    @staticmethod
    def calculate_castle_text(board: Board) -> str:
        castle_text = ''
        if board.get_white_player().is_king_side_castle_capable():
            castle_text += 'K'
        if board.get_white_player().is_queen_side_castle_capable():
            castle_text += 'Q'
        if board.get_black_player().is_king_side_castle_capable():
            castle_text += 'k'
        if board.get_black_player().is_queen_side_castle_capable():
            castle_text += 'q'
        return '-' if castle_text == '' else castle_text

# if __name__ == '__main__':
#     BoardUtils.init()
#     board = Board.create_standard_board()
#     move = MoveFactory.create_move(board, 48, 32)
#     trans = board.get_current_player().make_move(move)
#     if trans.get_move_status().is_done():
#         board = trans.get_transition_board()
#     print(board)
#     minimax = MiniMax(4)
#     black_exe = minimax.execute(board)
#     trans = board.get_current_player().make_move(black_exe)
#     if trans.get_move_status().is_done():
#         board = trans.get_transition_board() 
#     print(board)
#     print(FenUtilities.create_fen_from_game(board))


def generate_next_move(fen, depth=3) -> dict:
    '''Return a string represents the next move that current player in FEN string should make and the fen after make that move'''
    BoardUtils.init()
    board = FenUtilities.create_game_from_fen(fen)
    player = board.get_current_player()
    minimax = MiniMax(depth)
    move = minimax.execute(board)
    transition_board = board.get_current_player().make_move(move)
    if transition_board.get_move_status().is_done():
        board = transition_board.get_transition_board()
    return {'moved_piece': str(move.get_moved_piece()),
            'from': BoardUtils.get_position_at_coordinate(move.get_current_coordinate()),
            'to': BoardUtils.get_position_at_coordinate(move.get_destination_coordinate()),
            'fen_board': FenUtilities.create_fen_from_game(board),
            'player': str(player),
            'depth': str(depth)}

import re
def fenPass(fen):
    regexMatch=re.match('\s*^(((?:[rnbqkpRNBQKP1-8]+\/){7})[rnbqkpRNBQKP1-8]+)\s([b|w])\s([K|Q|k|q]{1,4})\s(-|[a-h][1-8])\s(\d+\s\d+)$', fen)
    if  regexMatch:
        regexList = regexMatch.groups()
        fen = regexList[0].split("/")
        if len(fen) != 8:
            raise ValueError("expected 8 rows in position part of fen: {0}".format(repr(fen)))

        for fenPart in fen:
            field_sum = 0
            previous_was_digit, previous_was_piece = False,False

            for c in fenPart:
                if c in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    if previous_was_digit:
                        raise ValueError("two subsequent digits in position part of fen: {0}".format(repr(fen)))
                    field_sum += int(c)
                    previous_was_digit = True
                    previous_was_piece = False
                elif c == "~":
                    if not previous_was_piece:
                        raise ValueError("~ not after piece in position part of fen: {0}".format(repr(fen)))
                    previous_was_digit, previous_was_piece = False,False
                elif c.lower() in ["p", "n", "b", "r", "q", "k"]:
                    field_sum += 1
                    previous_was_digit = False
                    previous_was_piece = True
                else:
                    raise ValueError("invalid character in position part of fen: {0}".format(repr(fen)))

            if field_sum != 8:
                raise ValueError("expected 8 columns per row in position part of fen: {0}".format(repr(fen)))  

    else: raise ValueError("fen doesn`t match follow this example: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 ")  
