from src.data.game_loader import load_game_data
from src.games.registry import create_game


def main():
    data = load_game_data("tictactoe")
    game = create_game("tictactoe", data["rules_text"])

    state = game.initial_state()

    print("Game:", game.name)
    print("Rules preview:")
    print(game.get_rules_text()[:200])
    print("\nInitial state:")
    print(game.state_to_text(state))

    move = (0, 0)
    print("\nTesting move:", move)
    print("Valid?", game.is_valid_move(state, move, state.current_player))

    new_state = game.apply_move(state, move, state.current_player)
    print("\nState after move:")
    print(game.state_to_text(new_state))
    print("\nWinner:", game.get_winner(new_state))
    print("Terminal?", game.is_terminal(new_state))


if __name__ == "__main__":
    main()