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

def evalulate(b: chess.Board) -> float:
    '''
    Docstring for evalulate
    
    :param b: The input board
    :type b: chess.Board
    :return: An evaluation of the position
    :rtype: float
    '''
    evaluation = 0.0
    if b.turn == chess.BLACK:
        b = b.mirror()
    for square, piece in b.piece_map().items():
        value = PIECE_VALUES[piece.symbol().lower()]
        if piece.color == chess.BLACK:
            value = -value
        evaluation += value
    return evaluation

def best_move(b: chess.Board) -> chess.Move:
    '''
    Docstring for best_move
    
    :param b: The board to find the best move for
    :type b: chess.Board
    :return: The positions best move in the position
    :rtype: Move
    '''
    moves = b.legal_moves
    best_move = random.choice(list(moves))
    best_eval = -float('inf')
    for move in moves:
        b.push(move)
        evaluation = evalulate(b)
        if evaluation > best_eval:
            best_eval = evaluation
            best_move = move
        b.pop()
    return best_move

board = chess.Board()
print(board)

while not board.is_game_over():
    move = chess.Move.from_uci('0000')
    while not board.is_legal(move):
        move = chess.Move.from_uci(input('Enter move: '))
    board.push(move)
    print(board)
    move = best_move(board)
    board.push(move)
    print(board)
    print(f'Bot played: {move}')