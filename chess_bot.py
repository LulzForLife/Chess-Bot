import chess
import random
import sys

# the base piece values in centipawns
PIECE_VALUES = {
    'k': 20000.0,
    'q': 900.0,
    'r': 500.0,
    'b': 330.0,
    'n': 300.0,
    'p': 100.0
}

# simple piece values for middle/endgame phasing
SIMPLE_PIECE_VALUES = {
    'k': 20,
    'q': 9,
    'r': 5,
    'b': 3,
    'n': 3,
    'p': 1
}

# the bonus tables for the middlegame and endgame
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

# a list for mirroring squares
MIRROR_BOARD = [
    56, 57, 58, 59, 60, 61, 62, 63,
    48, 49, 50, 51, 52, 53, 54, 55,
    40, 41, 42, 43, 44, 45, 46, 47,
    32, 33, 34, 35, 36, 37, 38, 39,
    24, 25, 26, 27, 28, 29, 30, 31,
    16, 17, 18, 19, 20, 21, 22, 23,
    8,  9,  10, 11, 12, 13, 14, 15,
    0,  1,  2,  3,  4,  5,  6,  7,
]

INF = float('inf')

def test_cases() -> None:
    '''
    Docstring for test_cases
    '''
    def test(fen: str, expected: str) -> bool:
        return get_best_move(chess.Board(fen)) == chess.Move.from_uci(expected)
    assert test('1k6/8/1K6/8/4R3/8/8/8 w - - 0 1', 'e4e8')
    assert test('8/k1P5/8/1K6/8/8/5PBB/8 w - - 0 1', 'c7c8n')
    assert test('6R1/8/4K2k/5Pp1/8/6N1/3B4/8 w - g6 0 2', 'f5g6')
    print('All tests passed!')

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

def uci_loop():
    sys.stdout.reconfigure(line_buffering=True) # pyright: ignore[reportAttributeAccessIssue]

    board = chess.Board()
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        parts = line.split()
        if not parts:
            continue

        if parts[0] == "uci":
            print("id name KikiBot")
            print("id author kiranmjlowe")
            print("uciok", flush=True)
            
        elif parts[0] == "isready":
            print("readyok", flush=True)
            
        elif parts[0] == "position":
            if "startpos" in parts:
                board = chess.Board()
            elif "fen" in parts:
                # Find where 'moves' starts to isolate the FEN
                fen_end = parts.index("moves") if "moves" in parts else len(parts)
                fen_string = " ".join(parts[parts.index("fen")+1 : fen_end])
                board = chess.Board(fen_string)
            
            if "moves" in parts:
                for move in parts[parts.index("moves") + 1:]:
                    board.push_uci(move)

        elif parts[0] == "go":
            # Pass the board to your search function
            move = get_best_move(board, depth=3)
            
            # Validation (Good safety net!)
            if move not in board.legal_moves:
                move = random.choice(list(board.legal_moves))
            
            print(f"bestmove {move.uci()}", flush=True)

        elif parts[0] == "ucinewgame":
            board = chess.Board() 

        elif parts[0] == "quit":
            break

def evaluate(b: chess.Board) -> float:
    '''
    Docstring for evalulate
    
    :param b: The input board
    :type b: chess.Board
    :return: An evaluation of the position
    :rtype: float
    '''
    if b.is_checkmate():
        return -INF if b.turn == chess.WHITE else INF
    elif b.is_game_over():
        return 0
    
    endgame = 24
    for square, piece in b.piece_map().items():
        if not piece.piece_type in {chess.PAWN, chess.KING}:
            endgame -= SIMPLE_PIECE_VALUES[piece.symbol().lower()]
    
    t = endgame / 24
    
    evaluation = 0.0
    for square, piece in b.piece_map().items():
        symbol = piece.symbol().lower()
        value = PIECE_VALUES[symbol]
        if b.turn == chess.WHITE:
            idx = MIRROR_BOARD[square]
        else:
            idx = int(square)
        middlegame_value = MIDDLEGAME_BONUS[symbol][idx]
        endgame_value = ENDGAME_BONUS[symbol][idx]
        # lerp
        value += (t * middlegame_value + (1 - t) * endgame_value)

        if piece.color != b.turn:
            value = -value
        evaluation += value
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
    if b.is_checkmate():
        return (chess.Move.null(), -INF if b.turn == chess.WHITE else INF)
    elif b.is_game_over():
        return (chess.Move.null(), 0)
    moves = list(b.legal_moves)
    best_move = random.choice(moves)
    best_eval = -INF
    for move in moves:
        b.push(move)
        if depth > 1:
            evaluation = -(_search_moves(b, depth - 1)[1])
        else: 
            evaluation = -evaluate(b)
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
        if move == chess.Move.null():
            break
        board.push(move)
        print(board)
        print(f'Bot played: {move}')
    print('Game over!')

if __name__ == '__main__':
    #main()
    #test_cases()
    pass
uci_loop()