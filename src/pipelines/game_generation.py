from src.prompts.prompt_builder import build_game_generation_prompt


def run_game_generation(model, theme: str, constraints: str = "") -> dict:
    prompt = build_game_generation_prompt(theme=theme, constraints=constraints)
    response = model.generate(prompt)

    return {
        "theme": theme,
        "constraints": constraints,
        "prompt": prompt,
        "response": response,
    }