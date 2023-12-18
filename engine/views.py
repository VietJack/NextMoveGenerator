from rest_framework.response import Response
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .src.engine import generate_next_move, fenPass
# Create your views here.

@api_view(['GET', 'POST'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def next_move_maker(request):
    '''Calculate and return next move from a FEN string
    Parameter: 
        - depth (optional): The depth of search
    Response:
        - move: The string represent the move that current player should make
        - fen: FEN string of the board after make move
        - player_make_this_move: Player who makes move(white of black)
        - depth: The depth of search, default depth is 3
    '''
    if request.method == 'POST':
        fen = request.data.get('fen')
        try:
            fenPass(fen)
        except:
            return Response({'Message':'Invalid FEN string'})
        depth = request.query_params.get('depth')
        if depth:
            depth = int(depth)
            move_generator = generate_next_move(fen, depth)
        else:
            move_generator = generate_next_move(fen)
        moved_piece = move_generator['moved_piece']
        from_position = move_generator['from']
        destination_position = move_generator['to']
        fen = move_generator['fen_board']
        player_make_this_move = move_generator['player']
        depth = move_generator['depth']
        return Response(data={'moved_piece': moved_piece,
                              'from': from_position,
                              'to': destination_position,
                              'fen': fen,
                              'player_make_this_move': player_make_this_move,
                              'depth': depth})
    return Response({'Message':'Welcome to my chess engine api'})
