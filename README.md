# Neural Networks Study System

An interactive study and quiz application that helps you learn neural network topics using artificial intelligence.

## Features

- **Dynamic Checkpoint Selection**: Choose checkpoints in any order you prefer
- **Web Search Integration**: Automatically fetches study material from the web using Tavily API when notes are unavailable
- **RAG-Based Hints**: Get relevant context-based help during quizzes by typing 'hint'
- **Local AI Model**: Uses TinyLlama model that runs locally without internet dependency
- **Smart Grading**: Automatically evaluates answers using keyword-based assessment
- **Weak Area Identification**: Provides simple explanations for topics where you need improvement

## Checkpoints

1. **Basics of Neural Networks** - Understanding neurons, weights, bias, and activation functions
2. **Forward Propagation** - How data flows through network layers
3. **Loss Function** - Measuring loss and training metrics

## Setup

### Requirements
```bash
pip install -r requirements.txt
```

### Environment Variables

Add to `.env` file:
```
TAVILY_API_KEY=your_tavily_api_key
```

## Usage

```bash
python infosys.py
```

After running the program:
1. Select a checkpoint from the menu
2. Study material is automatically fetched (from saved notes or web search)
3. Attempt the quiz and submit your answers
4. Type 'hint' to get help based on the study material
5. View your score and identify areas for improvement

## Project Structure

- `infosys.py` - Main application file
- `.env` - API keys configuration (Tavily)
- `README.md` - This file

## How It Works

1. **Study Material Fetching**: First checks USER_NOTES dictionary, then fetches from web search if needed
2. **Question Generation**: TinyLlama model generates questions based on study material
3. **RAG System**: Uses FAISS vector database for intelligent context retrieval
4. **Grading**: Automatic scoring based on keyword matching and word count

## Notes

- TinyLlama model downloads automatically on first run
- Tavily API key is required for web search functionality
- Passing score is 60% by default
- Simple explanations are provided before retaking the quiz if you fail
