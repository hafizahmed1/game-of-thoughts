# Game of Thoughts: Evaluating LLM Reasoning via Board Games

## Overview

This project investigates whether large language models (LLMs) can understand, apply, and reason over structured rule-based systems using board games.

We use two controlled environments:
- **Tic-Tac-Toe**
- **Connect Four**

These games allow systematic evaluation of reasoning abilities such as rule comprehension, consistency, and multi-step planning.

---

## Research Objective

Can LLMs:
1. Understand and explain game rules?
2. Detect inconsistencies in rule descriptions?
3. Simulate gameplay while respecting constraints?
4. Generate new games with coherent and playable rules?

---

## Project Structure

```
game-of-thoughts-oop-refactor/
├── notebooks/
│   └── demo.ipynb              # Final analysis and visualization
├── src/
│   ├── games/                 # Tic-Tac-Toe and Connect Four logic
│   ├── llm/                   # Model wrappers
│   ├── prompts/               # Prompt construction
│   ├── pipelines/             # Experiment pipelines
│   ├── evaluation/            # Metrics and scoring
│   ├── analysis/              # Result processing utilities
│   └── scripts/               # Run experiments and generate outputs
├── results/
│   ├── tables/                # Aggregated results
│   ├── plots/                 # Generated visualizations
│   └── responses/             # Raw model outputs
├── requirements.txt
└── README.md
```

---

## Experiments

### 1. Rule Understanding
Models explain game rules.

**Metrics:** precision, recall, F1-score

---

### 2. Rule Error Detection
Models identify inconsistencies in incorrect rules.

**Metrics:** precision, recall, F1-score

---

### 3. Game Simulation
Models play games step-by-step.

**Metrics:**
- legal move rate
- completion rate
- valid turns


---

### 4. Game Generation
Models generate new board games.

**Metrics:**
- clarity
- consistency
- completeness


---

## Setup

```bash
git clone <https://github.com/hafizahmed1/game-of-thoughts>
cd game-of-thoughts-oop-refactor

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

---

## Running the Project

### Run experiments
```bash
python -m src.scripts.run_all_experiments
```

### Evaluate results
```bash
python -m src.scripts.evaluate_all
```

### Generate plots
```bash
python -m src.scripts.plot_results
```

### Open notebook
```bash
jupyter notebook notebooks/demo.ipynb
```

---

## Outputs

Results are stored in:

- `results/tables/` → aggregated metrics  
- `results/plots/` → visualizations  
- `results/responses/` → raw outputs (if available)

---

## Key Findings

- Models perform well on **rule understanding** but struggle with **consistent multi-step reasoning**.
- Simulation results show **gradual degradation in rule adherence** over time.
- Error detection reveals **partial understanding of constraints**.
- Generated games are structurally valid but often **lack balance and depth**.

---

## Limitations

- Some evaluations rely on heuristic scoring.
- Raw simulation traces may be limited.
- Results are sensitive to prompt design.
- Generated games are not validated through real gameplay.

---

## AI Usage Disclaimer

This project was developed with assistance from generative AI tools for:
- code refactoring
- documentation
- notebook structuring

All outputs were manually reviewed, tested, and validated. The final implementation and analysis are my own.

---

## Conclusion

This project demonstrates that LLMs can approximate structured reasoning but still struggle with maintaining consistency over extended interactions. Board games provide an effective framework for evaluating these limitations in a controlled setting.
