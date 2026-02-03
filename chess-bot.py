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
MIDDLEGAME_BONUS = {
    'p': [
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ],
    'n': [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ],
    'b': [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    ],
    'r': [
        0,  0,  0,  5,  5,  0,  0,  0,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        5, 10, 10, 10, 10, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ],
    'q': [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ],
    'k': [
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20
    ]
}

ENDGAME_BONUS = {
    'p': [
        0,  0,  0,  0,  0,  0,  0,  0,
        80, 80, 80, 80, 80, 80, 80, 80,
        40, 40, 50, 60, 60, 50, 40, 40,
        20, 20, 30, 40, 40, 30, 20, 20,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 20, 20, 10,  5,  5,
        0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0
    ],
    'n': [
        -40,-30,-20,-20,-20,-20,-30,-40,
        -30,-10,  0,  5,  5,  0,-10,-30,
        -20,  5, 10, 15, 15, 10,  5,-20,
        -20, 10, 15, 20, 20, 15, 10,-20,
        -20, 10, 15, 20, 20, 15, 10,-20,
        -20,  5, 10, 15, 15, 10,  5,-20,
        -30,-10,  0,  5,  5,  0,-10,-30,
        -40,-30,-20,-20,-20,-20,-30,-40
    ],
    'b': [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    ],
    'r': [
        0,  0,  5, 10, 10,  5,  0,  0,
        0,  5, 10, 15, 15, 10,  5,  0,
        0,  5, 10, 15, 15, 10,  5,  0,
        0,  5, 10, 15, 15, 10,  5,  0,
        0,  5, 10, 15, 15, 10,  5,  0,
        0,  5, 10, 15, 15, 10,  5,  0,
        0,  0,  5, 10, 10,  5,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0
    ],
    'q': [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ],
    'k': [
        -50,-40,-30,-20,-20,-30,-40,-50,
        -30,-20,-10,  0,  0,-10,-20,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-30,  0,  0,  0,  0,-30,-30,
        -50,-30,-30,-30,-30,-30,-30,-50
    ]
}

INF = float('inf')

def test_cases() -> None:
    assert get_best_move(chess.Board('1k6/8/1K6/8/4R3/8/8/8 w - - 0 1')) == chess.Move.from_uci('e4e8')
    assert get_best_move(chess.Board('8/8/8/3r4/8/6k1/8/6K1 b - - 0 1')) == chess.Move.from_uci('d5d1')
    assert get_best_move(chess.Board('8/k1P5/8/1K6/8/8/5PBB/8 w - - 0 1')) == chess.Move.from_uci('c7c8n')
    print('Success!')

def get_user_move(b: chess.Board) -> chess.Move:
    move = input('Enter move (e.g. e2e4): ')
    try:
        chess_move = chess.Move.from_uci(move)
    except chess.InvalidMoveError:
        chess_move = chess.Move.from_uci('0000')
    while not b.is_legal(chess_move):
        print(f'Invalid move: \'{move}\'')
        try:
            move = input('Enter move (e.g. e2e4): ')
            chess_move = chess.Move.from_uci(move)
        except chess.InvalidMoveError:
            continue
    return chess_move

def evaluate(b: chess.Board) -> float:
    '''
    Docstring for evalulate
    
    :param b: The input board
    :type b: chess.Board
    :return: An evaluation of the position
    :rtype: float
    '''
    if b.is_checkmate():
        return INF
    elif b.is_game_over():
        return 0
    
    evaluation = 0.0
    for square, piece in b.piece_map().items():
        value = PIECE_VALUES[piece.symbol().lower()]
        if piece.color == chess.BLACK:
            value = -value
        evaluation += value
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

def main() -> None:
    board = chess.Board()
    print(board)

    while not board.is_game_over():
        move = get_user_move(board)
        board.push(move)
        print(board)
        print('Bot is thinking...')
        move = get_best_move(board, depth = 3)
        board.push(move)
        print(board)
        print(f'Bot played: {move}')

if __name__ == '__main__':
    main()
    #test_cases()