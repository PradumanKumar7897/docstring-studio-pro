# Docstring Studio Pro V3

AI-Powered Python Docstring Generator

## Features
- AST-based parsing of Python files
- Google, NumPy, and reST docstring styles
- Multi-provider AI: OpenAI, Gemini, Groq
- PEP 257 validation engine
- Safe code rewriting with LibCST
- CLI + Streamlit Web UI

## Installation
```bash
git clone https://github.com/PradumanKumar7897/docstring-studio-pro.git
cd docstring-studio-pro
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Setup API Keys
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Run CLI
```bash
python main.py scan yourfile.py
python main.py generate yourfile.py --style google --write
```

## Run Web UI
```bash
streamlit run ui/app.py
```

## Run Tests
```bash
pip install -r requirements-test.txt
pytest
```

## License

MIT License — see [LICENSE](LICENSE)