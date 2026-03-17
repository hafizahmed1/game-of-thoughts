import random


def generate_cases(game, num_cases=6, prefix="case", max_turns=None, seed=42):
    random.seed(seed)
    cases = []

    max_possible_moves = game.get_max_moves()
    simulation_max_turns = max_turns if max_turns is not None else max_possible_moves

    for i in range(num_cases):
        state = game.initial_state()
        moves_to_play = random.randint(0, max_possible_moves)

        for _ in range(moves_to_play):
            if game.is_terminal(state):
                break

            legal_moves = list(game.get_legal_moves(state))
            if not legal_moves:
                break

            move = random.choice(legal_moves)
            state = game.apply_move(state, move)

        cases.append(
            {
                "id": f"{prefix}_{i}",
                "state": {
                    "board": state.board,
                    "current_player": state.current_player,
                },
                "max_turns": simulation_max_turns,
            }
        )

    return cases