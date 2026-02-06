import chess
from chess import STARTING_FEN
import chess.polyglot as polyglot
import random
import sys
import time as t

class HashBoard(chess.Board):
    def __init__(self, fen: str | None = STARTING_FEN, *, chess960: bool = False) -> None: # pyright: ignore[reportArgumentType]
        super().__init__(fen, chess960 = chess960)
    def __hash__(self) -> int:
        return polyglot.zobrist_hash(self)

class TTEntry:
    __slots__ = ("value", "depth", "flag", "best")
    def __init__(self, value, depth, flag, best):
        self.value = value
        self.depth = depth
        self.flag = flag
        self.best = best

# the base piece values in centipawns
PIECE_VALUES = {
    'k': 60000.0,
    'q': 900.0,
    'r': 490.0,
    'b': 320.0,
    'n': 290.0,
    'p': 100.0
}

# phase piece values
PHASE_VALUES = {
    'k': 0,
    'q': 4,
    'r': 2,
    'b': 1,
    'n': 1,
    'p': 0
}

# the bonus tables for the middlegame and endgame
# TODO: Get better PSQTs
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

TIME_LIMIT = 5
DEPTH_LIMIT = 9
CAPTURE_EXTENSION = False
USE_UCI = "--uci" in sys.argv

EXACT, LOWER, UPPER = 0, 1, 2
TT: dict[int, TTEntry] = {}

MIDDLEGAME_CHECK_PENALTY = 0
ENDGAME_CHECK_PENALTY = 0

positions = 0
hits = 0
s = 0

def test_cases() -> None:
    '''
    Docstring for test_cases
    '''
    def test(fen: str, expected: str) -> bool:
        return get_best_move(HashBoard(fen), time = TIME_LIMIT) == chess.Move.from_uci(expected)
    assert test('1k6/8/1K6/8/4R3/8/8/8 w - - 0 1', 'e4e8')
    assert test('8/k1P5/8/1K6/8/8/5PBB/8 w - - 0 1', 'c7c8n')
    assert test('6R1/8/4K2k/5Pp1/8/6N1/3B4/8 w - g6 0 2', 'f5g6')
    print('All tests passed!')

def get_user_move(b: HashBoard) -> chess.Move:
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

# this was generated with Gemini
def uci_loop():
    sys.stdout.reconfigure(line_buffering=True) # pyright: ignore[reportAttributeAccessIssue]

    board = HashBoard()
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
                board = HashBoard()
            elif "fen" in parts:
                # Find where 'moves' starts to isolate the FEN
                fen_end = parts.index("moves") if "moves" in parts else len(parts)
                fen_string = " ".join(parts[parts.index("fen")+1 : fen_end])
                board = HashBoard(fen_string)
            
            if "moves" in parts:
                for move in parts[parts.index("moves") + 1:]:
                    board.push_uci(move)

        elif parts[0] == "go":
            # Pass the board to your search function
            move = get_best_move(board, time = TIME_LIMIT)
            
            # Validation (Good safety net!)
            if move not in board.legal_moves:
                move = random.choice(list(board.legal_moves))
            
            print(f"bestmove {move.uci()}", flush=True)

        elif parts[0] == "ucinewgame":
            board = HashBoard() 

        elif parts[0] == "quit":
            break

def evaluate(b: HashBoard) -> float:
    '''
    Docstring for evalulate
    
    :param b: The input board
    :type b: HashBoard
    :return: An evaluation of the position
    :rtype: float
    '''
    if b.is_checkmate():
        return -INF if b.turn == chess.WHITE else INF
    elif b.is_game_over():
        return 0
    
    endgame = 24
    for square, piece in b.piece_map().items():
        endgame -= PHASE_VALUES[piece.symbol().lower()]
    
    t = endgame / 24
    
    evaluation = 0.0
    for square, piece in b.piece_map().items():
        symbol = piece.symbol().lower()
        value = PIECE_VALUES[symbol]
        if piece.color == chess.WHITE:
            idx = MIRROR_BOARD[square]
        else:
            idx = int(square)
        middlegame_value = MIDDLEGAME_BONUS[symbol][idx]
        endgame_value = ENDGAME_BONUS[symbol][idx]
        # lerp
        value += (t * endgame_value + (1 - t) * middlegame_value)

        if piece.color != b.turn:
            value = -value
        evaluation += value
    
    if b.is_check():
        evaluation -= (ENDGAME_CHECK_PENALTY * t + MIDDLEGAME_CHECK_PENALTY * (1 - t))

    return evaluation

def ordered_moves(b: HashBoard) -> list[chess.Move]:
    quiet, caps = [], []
    for move in b.legal_moves:
        if b.is_capture(move): caps.append(move) 
        else: quiet.append(move)
    return caps + quiet

def _search_captures(b: HashBoard, alpha: float, beta: float) -> float:
    evaluation = evaluate(b)
    if evaluation >= beta:
        return beta
    if evaluation > alpha:
        alpha = evaluation
    
    capture_moves = filter(b.is_capture, b.legal_moves)

    for move in capture_moves:
        b.push(move)
        evaluation = -(_search_captures(b, -beta, -alpha))
        b.pop()

        if evaluation >= beta:
            return beta
        
        if evaluation > alpha:
            alpha = evaluation

    return alpha

def _search_moves(b: HashBoard, depth: int, alpha: float, beta: float, eval_only: bool = True) -> chess.Move | float:
    global positions, hits
    '''
    Docstring for _search_moves
    
    :param b: The board to find the best move for
    :type b: HashBoard
    :param depth: The depth to search to
    :type depth: int
    :return: The position\'s best move and evaluation
    :rtype: tuple[Move, float]
    '''
    positions += 1

    alpha_orig = alpha
    key = hash(b)

    entry = TT.get(key)
    if entry and entry.depth >= depth:
        
        hits += 1

        if entry.flag == EXACT:
            return entry.value if eval_only else entry.best
        elif entry.flag == LOWER:
            alpha = max(alpha, entry.value)
        elif entry.flag == UPPER:
            beta = min(beta, entry.value)

        if alpha >= beta:
            return entry.value if eval_only else entry.best

    if b.is_checkmate():
        return -INF if eval_only else chess.Move.null()
    elif b.is_game_over():
        return 0 if eval_only else chess.Move.null()

    best_move = None
    value = -INF

    moves = ordered_moves(b)

    if entry and entry.best in moves:
        moves.remove(entry.best)
        moves.insert(0, entry.best)

    for move in moves:
        b.push(move)

        if depth > 1:
            evaluation = -(_search_moves(b, depth - 1, -beta, -alpha)) # pyright: ignore[reportOperatorIssue]
        else:
            if CAPTURE_EXTENSION:
                evaluation = -(_search_captures(b, -beta, -alpha))
            else:
                evaluation = -evaluate(b)
        
        b.pop()

        if evaluation > value:
            value = evaluation
            best_move = move
        
        alpha = max(alpha, evaluation)
        if alpha >= beta:
            break

    if value <= alpha_orig:
        flag = UPPER
    elif value >= beta:
        flag = LOWER
    else:
        flag = EXACT

    TT[key] = TTEntry(value, depth, flag, best_move)

    return value if eval_only else best_move # pyright: ignore[reportReturnType]

def get_best_move(b: HashBoard, time: int | float) -> chess.Move:
    global s
    '''     
    Docstring for get_best_move
    
    :param b: The board to find the best move for
    :type b: HashBoard
    :param depth: How long to search for
    :type time: int | depth
    :return: The position\'s best move
    :rtype: Move
    '''
    best = chess.Move.null()

    s = t.time()

    for depth in range(1, DEPTH_LIMIT + 1):
        if t.time() - s > time:
            break
        best = _search_moves(b, depth, -INF, INF, eval_only = False)
        print(f'Depth: {depth}', end = '\r')

    return best # pyright: ignore[reportReturnType]

def main() -> None:
    global positions, hits

    board = HashBoard()
    print(board)

    while not board.is_game_over():
        move = get_user_move(board)
        board.push(move)
        print(board)
        print('Bot is thinking...')
        positions = 0
        hits = 0
        move = get_best_move(board, time = TIME_LIMIT)
        if move == chess.Move.null():
            break
        board.push(move)
        print(board)
        print(f'Bot played: {move}')
        print(f'{positions} positions, {hits} hit')
    print('Game over!')

if __name__ == '__main__':
    if not USE_UCI:
        main()
        #test_cases()
    else:
        uci_loop()