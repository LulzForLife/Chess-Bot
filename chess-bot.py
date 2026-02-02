import chess
import random

# the base piece values in centipawns
PIECE_VALUES = {
    'k': 20000.0,
    'q': 900.0,
    'r': 500.0,
    'b': 330.0,
    'n': 300.0,
    'p': 100.0
}
INF = float('inf')

def evaluate(b: chess.Board) -> float:
    '''
    Docstring for evalulate
    
    :param b: The input board
    :type b: chess.Board
    :return: An evaluation of the position
    :rtype: float
    '''
    evaluation = 0.0
    for square, piece in b.piece_map().items():
        value = PIECE_VALUES[piece.symbol().lower()]
        if piece.color == chess.BLACK:
            value = -value
        evaluation += value
    if b.is_checkmate():
        evaluation = INF
    elif b.is_stalemate():
        evaluation = 0
    if b.turn == chess.WHITE:
        evaluation = -evaluation
    return evaluation

def _search_moves(b: chess.Board, depth: int) -> tuple[chess.Move, float]:
    '''
    Docstring for _search_moves
    
    :param b: The board to find the best move for
    :type b: chess.Board
    :param depth: The depth to search to
    :type depth: int
    :return: The positions best move in the position
    :rtype: tuple[Move, float]
    '''
    moves = list(b.legal_moves)
    best_move = random.choice(moves)
    best_eval = -INF
    for move in moves:
        b.push(move)
        if depth > 1:
            evaluation = -(_search_moves(b, depth - 1)[1])
        else: 
            evaluation = evaluate(b)
        b.pop()
        if evaluation > best_eval:
            best_eval = evaluation
            best_move = move
    return (best_move, best_eval)

def get_best_move(b: chess.Board, *, depth: int = 1) -> chess.Move:
    '''     
    Docstring for get_best_move
    
    :param b: The board to find the best move for
    :type b: chess.Board
    :param depth: The depth to search to
    :type depth: int
    :return: The positions best move in the position
    :rtype: Move
    '''
    return _search_moves(b, depth)[0]

board = chess.Board()
print(board)

while not board.is_game_over():
    move = chess.Move.from_uci('0000')
    while not board.is_legal(move):
        move = chess.Move.from_uci(input('Enter move: '))
    board.push(move)
    print(board)
    print('Bot is thinking...')
    move = get_best_move(board, depth = 3)
    board.push(move)
    print(board)
    print(f'Bot played: {move}')