from src.prompts.prompt_builder import build_game_generation_prompt


def run_game_generation(model, theme: str, constraints: str = "") -> dict:
    seed_idea = theme if not constraints else f"{theme}\nConstraints: {constraints}"

    prompt = build_game_generation_prompt(seed_idea=seed_idea)
    response = model.generate(prompt)

    return {
        "theme": theme,
        "constraints": constraints,
        "prompt": prompt,
        "response": response,
    }