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

TIME_LIMIT = 3
DEPTH_LIMIT = 100
CAPTURE_EXTENSION = True
USE_UCI = "--uci" in sys.argv

EXACT, LOWER, UPPER = 0, 1, 2
TT: dict[int, TTEntry] = {}
KILLER1 = [None] * 64
KILLER2 = [None] * 64
HISTORY = [[0]*64 for _ in range(64)]

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
            move = get_best_move(board, time = TIME_LIMIT)[0]
            
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
    
    phase = 0
    for square, piece in b.piece_map().items():
        phase += PHASE_VALUES[piece.symbol().lower()]
    
    t = min(phase / 24, 1.0)
    
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
        value += (t * middlegame_value + (1 - t) * endgame_value)

        if piece.color != b.turn:
            value = -value
        evaluation += value

    return evaluation

def ordered_moves(b: HashBoard, depth: int, tt_move = None):
    def score(m: chess.Move):
        s = 0
        if tt_move and m == tt_move:
            return 20000
        if (cap := b.piece_at(m.to_square)):
            return 10000 + PIECE_VALUES[cap.symbol().lower()]
        idx = max(0, min(depth, len(KILLER1) - 1))
        if m == KILLER1[idx]:
            s += 9000
        elif m == KILLER2[idx]:
            s += 8000
        s += HISTORY[m.from_square][m.to_square]
        return s
    return sorted(b.legal_moves, key = score, reverse = True)

def _extend_search(b: HashBoard, alpha: float, beta: float, depth: int = 0) -> float:
    if b.is_checkmate():
        return -INF
    elif b.is_game_over():
        return 0.0

    key = hash(b)
    entry = TT.get(key)
    if entry:
        if entry.flag == EXACT:
            return entry.value
        elif entry.flag == LOWER:
            alpha = max(alpha, entry.value)
        elif entry.flag == UPPER:
            beta = min(beta, entry.value)
        if alpha >= beta:
            return entry.value

    stand = evaluate(b)
    if stand >= beta:
        TT[key] = TTEntry(stand, 0, LOWER, None)
        return beta
    alpha = max(alpha, stand)

    value = alpha

    for m in ordered_moves(b, depth):
        if not (b.is_capture(m) or m.promotion or b.gives_check(m)):
            break
        b.push(m)
        score = -_extend_search(b, -beta, -alpha, depth + 1)
        b.pop()

        if score >= beta:
            TT[key] = TTEntry(score, 0, LOWER, m)
            return beta

        value = max(value, score)
        alpha = max(alpha, score)

    TT[key] = TTEntry(value, 0, EXACT, None)
    return value

def _search_moves(b: HashBoard, depth: int, alpha: float, beta: float, eval_only: bool = True) -> float | tuple[chess.Move, float]:
    '''
    Docstring for _search_moves
    
    :param b: The board to find the best move for
    :type b: HashBoard
    :param depth: The depth to search to
    :type depth: int
    :return: The position\'s best move and evaluation
    :rtype: float | tuple[chess.Move, float]
    '''
    global positions, hits
    if t.time() - s > TIME_LIMIT:
        raise TimeoutError

    positions += 1

    alpha_orig = alpha
    beta_orig = beta
    key = hash(b)

    entry = TT.get(key)
    if entry and entry.depth >= depth:
        
        hits += 1

        if entry.flag == EXACT:
            return entry.value if eval_only else (entry.best, entry.value)
        elif entry.flag == LOWER:
            alpha = max(alpha, entry.value)
        elif entry.flag == UPPER:
            beta = min(beta, entry.value)

        if alpha >= beta:
            return entry.value if eval_only else (entry.best, entry.value)

    if b.is_checkmate():
        return -INF if eval_only else (chess.Move.null(), -INF)
    elif b.is_game_over():
        return 0.0 if eval_only else (chess.Move.null(), 0.0)

    best_move = random.choice(list(b.legal_moves))
    value = -INF

    tt_move = entry.best if entry else None
    moves = ordered_moves(b, depth, tt_move)

    for move in moves:
        b.push(move)

        if depth > 1:
            evaluation = -(_search_moves(b, depth - 1, -beta, -alpha)) # pyright: ignore[reportOperatorIssue]
        else:
            if CAPTURE_EXTENSION:
                evaluation = -(_extend_search(b, -beta, -alpha))
            else:
                evaluation = -evaluate(b)
        
        b.pop()

        if evaluation > value:
            value = evaluation
            best_move = move
        
        alpha = max(alpha, evaluation)
        if alpha >= beta:
            if not b.is_capture(move):
                idx = max(0, min(depth, len(KILLER1) - 1))
                KILLER2[idx] = KILLER1[idx]
                KILLER1[idx] = move # pyright: ignore[reportCallIssue, reportArgumentType]
                HISTORY[move.from_square][move.to_square] += depth * depth
            break


    if value <= alpha_orig:
        flag = UPPER
    elif value >= beta_orig:
        flag = LOWER
    else:
        flag = EXACT

    TT[key] = TTEntry(value, depth, flag, best_move)

    return value if eval_only else (best_move, value) # pyright: ignore[reportReturnType]

def get_best_move(b: HashBoard, time: int | float) -> tuple[chess.Move, float, int]:
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
    best = random.choice(list(b.legal_moves))

    s = t.time()
    d = 0

    for depth in range(1, DEPTH_LIMIT + 1): 
        try:
            best, evaluation = _search_moves(b.copy(), depth, -INF, INF, eval_only = False) # pyright: ignore[reportGeneralTypeIssues]
        except TimeoutError:
            break
        d = depth
        if not USE_UCI:
            print(f'Depth: {depth}', end = '\r')

    return best, evaluation, d # pyright: ignore[reportPossiblyUnboundVariable, reportReturnType]

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
        move, evaluation, depth = get_best_move(board, time = TIME_LIMIT)
        if move == chess.Move.null():
            break
        board.push(move)
        print(board)
        print(f'Bot played: {move}')
        print(f'{positions} positions | {hits} hit | evaluation {evaluation / 100} | depth {depth}')
    print('Game over!')

if __name__ == '__main__':
    if not USE_UCI:
        #try:
            main()
        #except Exception as e:
        #    print(e)
        #    print(KILLER1)
        #    print(KILLER2)
        #test_cases()
    else:
        uci_loop()