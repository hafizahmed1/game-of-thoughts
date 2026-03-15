Game-of-Thoughts
This project investigates whether Large Language Models (LLMs) can understand structured rule systems and generate new games with logically consistent rules. Board games provide a controlled environment with explicit rules, constraints, and objectives, making them a useful testbed for evaluating reasoning abilities in language models.
---
Research Question
Can large language models understand existing game rules and generate new games with logically consistent rule systems?
---
Project Overview
Games provide structured environments where players must follow strict rules to reach defined goals. In this project, we evaluate whether LLMs can interpret, apply, analyze, and extend such rule systems.
The project focuses on two main capabilities.
Game Understanding
The model is provided with the rules of an existing game (Tic-Tac-Toe). It must:
explain the rules clearly
detect inconsistencies or missing constraints
suggest valid moves for different board states
This evaluates whether the model can internalize structured rule systems.
Game Generation
The model is asked to design a new board game based on a given theme. The generated rules are evaluated for:
structural completeness
logical consistency
playability
This evaluates whether the model can extend rule systems creatively while maintaining logical constraints.
---
Experiments
The project evaluates four different reasoning abilities of LLMs.
Experiment 1 — Rule Understanding
The model receives the rules of Tic-Tac-Toe and must explain them clearly.
Three input conditions are tested:
clean rules
raw rulebook text
broken or incomplete rules
Evaluation metrics:
rule completeness score
invented rules
missed constraints
This experiment measures how well the model understands structured rule descriptions.
---
Experiment 2 — Move Prediction
The model is given different Tic-Tac-Toe board states and must suggest a valid move.
Evaluation metrics:
valid move rate
optimal move rate
This experiment tests whether the model can apply game rules to specific board situations.
---
Experiment 3 — Rule Error Detection
The model is given a deliberately flawed rule set and must identify logical issues.
The model must:
detect missing rules
explain why they are problematic
propose corrected rules
Evaluation metric:
number of detected rule inconsistencies
This experiment evaluates logical reasoning about rule systems.
---
Experiment 4 — Game Generation
The model is prompted to create a new two-player board game.
The generated output must include:
game name
objective
setup
turn structure
rules
winning condition
Evaluation criteria:
structural completeness
logical consistency
playability
This experiment evaluates creative rule synthesis under logical constraints.
---
Project Structure
game-of-thoughts  
│  
├── data  
│   ├── raw  
│   │   └── TIC_TAC_TOE_RULES.docx  
│   │  
│   └── processed  
│       ├── tictactoe_rulebook.json  
│       └── broken_tic_tac_toe.txt  
│  
├── experiments  
│   ├── experiment_01_tictactoe.ipynb  
│   ├── prepare_tictactoe_rulebook.py  
│   ├── rule_understanding.py  
│   ├── move_prediction.py  
│   ├── rule_errors.py  
│   └── game_generation.py  
│  
├── results  
│   ├── figures  
│   ├── prompts  
│   ├── responses  
│   └── tables  
│  
├── src  
│   ├── games  
│   ├── prompts  
│   ├── pipelines  
│   ├── utils  
│   └── evaluation  
│  
├── report  
│  
├── README.md  
└── requirements.txt
---
How to Reproduce the Experiments
1. Clone the Repository
git clone https://github.com/hafizahmed1/game-of-thoughts.git  
cd game-of-thoughts
---
2. Create a Virtual Environment
python -m venv .venv  
source .venv/bin/activate
On Windows:
.venv\Scripts\activate
---
3. Install Dependencies
pip install -r requirements.txt
---
4. Configure API Access
Create a `.env` file in the project root and add your API key:
GEMINI_API_KEY=your_api_key_here  
MODEL_NAME=models/gemini-3.1-flash-lite-preview
The project uses the Gemini API to run the language model.
---
5. Prepare the Rulebook Data
Convert the rulebook document into structured JSON format:
python experiments/prepare_tictactoe_rulebook.py
This generates:
data/processed/tictactoe_rulebook.json
---
6. Run the Experiments
Run the following scripts from the project root.
Rule Understanding:
python experiments/rule_understanding.py
Move Prediction:
python experiments/move_prediction.py
Rule Error Detection:
python experiments/rule_errors.py
Game Generation:
python experiments/game_generation.py
---
Results
Experiment outputs are stored in the `results` directory.
results  
│  
├── prompts  
├── responses  
├── tables  
└── figures
These files contain the prompts sent to the model, the model responses, and the evaluation metrics used in the analysis.
---
