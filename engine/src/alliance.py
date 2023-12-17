from enum import Enum

class Alliance(Enum):
    WHITE = 'W'
    BLACK = 'B'

    def is_white(self) -> bool:
        if self.value == 'W':
            return True
        return False
    
    def is_black(self) -> bool:
        if self.value == 'B':
            return True
        return False
    
    def get_direction(self) -> int:
        return 1 if self.value == 'B' else -1
    
    def choose_player(self, white_player, black_player):
        ''' Return player correspond to this alliance'''
        return white_player if self.value == 'W' else black_player
    
    def get_opposite_direction(self):
        return -1 if self.value == 'B' else 1
    
    def is_pawn_promotion_square(self, position: int) -> bool:
        from .board import BoardUtils
        BoardUtils.init()
        if self.value == 'W':
            return BoardUtils.EIGHTH_RANK[position]
        return BoardUtils.FIRST_RANK[position]
    