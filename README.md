# ROBIN (Real-time Operational Bot for Intelligent Navigation)

ROBIN is a clean, modular, production-ready AI CLI assistant designed for resource efficiency. 
It operates continuously, processes system commands directly without AI overhead, and only triggers an LLM when explicitly requested via a keyword ("robin" or "ai").

## 🎯 Features
- **Ultra-lightweight**: Highly optimized for systems with low RAM limitations (e.g. 6GB).
- **Hybrid Processing**: 
  - Direct execution for static commands (`time`, `open chrome`, `search google <query>`).
  - LLM integration for complex requests (powered by local `Ollama`).
- **On-Demand AI**: AI is never preloaded or called unless prompted.

## 📁 Installation

1. **Clone or navigate to the project directory**
2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Copy the `.env.example`**
   ```bash
   cp .env.example .env
   ```

## 🧠 Using the AI (Ollama Setup)

ROBIN uses Ollama for local LLM inference.
1. Download and install [Ollama](https://ollama.com/).
2. Pull a small model (for example, `tinyllama` which is optimized for small RAM configs):
   ```bash
   ollama run tinyllama
   ```
3. Make sure the Ollama server is running (usually localized at `http://localhost:11434`).

## 🚀 Running ROBIN

Start ROBIN using Python:
```bash
python main.py
```

## 💬 Usage Examples

**System Commands (NO AI used)**
- `time`
- `open chrome`
- `search google python programming`
- `hello`

**AI Commands (Uses Ollama)**
- `robin explain recursion`
- `ai what is the capital of France?`
