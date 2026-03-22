# Game of Thoughts

This project evaluates whether Large Language Models (LLMs) can understand, apply, and generate rule-based systems using board games.

We use two games:
- Tic-Tac-Toe
- Connect Four

The goal is to study how well LLMs handle structured reasoning beyond simple text generation.

---

## Research Question

To what extent can LLMs understand, apply, critique, and generate rule-based game systems?

---

## Experiments

The project includes four tasks:

- Rule Understanding – explain game rules  
- Rule Error Detection – identify incorrect or missing rules  
- Game Simulation – play games step-by-step  
- Game Generation – create new board games  

---



## Project Structure

game-of-thoughts/  
├── notebooks/        # Final analysis notebook  
├── src/              # Core logic and pipelines  
├── results/          # Tables, plots, responses  
├── requirements.txt  
└── README.md  

---
## Code Organization

All core experiment logic is implemented inside the `src/` directory, including:

- game logic
- experiment pipelines
- evaluation metrics
- data processing

The notebook (`notebooks/demo.ipynb`) is used only for visualizing results and presenting analysis. It does not contain the main implementation.
-----------


## Setup

```bash
git clone https://github.com/hafizahmed1/game-of-thoughts.git
cd game-of-thoughts

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

---

## API Key Setup (IMPORTANT)

1. Go to: https://console.groq.com/keys  
2. Sign in  
3. Click **Create API Key**  
4. Copy your key  

Create a `.env` file in the project root and add:

```
GROQ_API_KEY=gskxxxxxxxxxxxxxxxxx
```

---

## Fix Common Path Issues

If you get:

```
ModuleNotFoundError: No module named 'src'
```

Run:

```bash
export PYTHONPATH=$(pwd)
```

On Windows (PowerShell):

```bash
$env:PYTHONPATH = (Get-Location)
```

---
## Quick Testing (Optional)

If you want to run a quick test instead of full experiments, you can reduce the number of simulation cases.

Go to:

src/scripts/experiments/game_simulation.py

Search for:

num_cases = 50

Change it to a smaller value such as:

num_cases = 5  
or  
num_cases = 10  

This will significantly reduce runtime for testing and debugging.
---

## Run the Project

```bash
python -m src.scripts.run_all_experiments
python -m src.scripts.evaluate_all
python -m src.scripts.plot_results
```

Open the notebook:

Aun All

---

## Results

Outputs are stored in:

- results/tables/ – metrics  
- results/plots/ – visualizations  
- results/responses/ – model outputs  

---

## Notes

- Experiments use LLaMA and Qwen models via Groq (free tier)  
- Earlier experiments with Gemini had rate limits and slower execution  

---

## Conclusion

LLMs can understand and describe rules well, but struggle with long-term consistency and strategic reasoning during gameplay.

---

## AI Usage Disclaimer

This project was developed with assistance from generative AI tools, including ChatGPT and Gemini, for tasks such as code refactoring, documentation, and structuring the notebook.

These tools were used in accordance with the project guidelines, both as an object of investigation and as support during development (e.g., ideation, drafting, and experimentation).

All outputs were carefully reviewed, tested, and modified. The final implementation, analysis, and conclusions are my own.
