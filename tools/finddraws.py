import chess

import agent

for attempt in range(30):
    board = chess.Board()
    agent.TT.clear()
    agent.HISTORY.clear()
    while not board.is_game_over(claim_draw=True) and board.fullmove_number < 150:
        if board.turn == chess.WHITE:
            move = chess.Move.from_uci(agent.get_move(board.fen(), 10_000))
        else:
            move = max(
                board.legal_moves,
                key=lambda m: 10 if board.is_capture(m) else 0,
            )
        board.push(move)
    outcome = board.outcome(claim_draw=True)
    if outcome is not None and outcome.winner is None:
        print(f"DRAW on attempt {attempt}: {outcome.termination}")
        print(board.fen())
        print(board)
        break
else:
    print("no draw in 30 games")