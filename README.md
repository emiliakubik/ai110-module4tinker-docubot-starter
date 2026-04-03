# Final reflection

I think the biggest concepts a student needs to get out of this is understanding a RAG model and understanding the difference between each of the 3 models we work with here. Something that stood out to me during this assignment is I believe this one could be really easy for students to shortcut and rely too much on AI to complete this for them, rather than really immersing themselves in it and getting something out of it. I think that's where my role comes in, during breakouts, I need to be really vigilant to what they are discussing and making sure they are not having AI do all of the work for them. AI was really helpful in understanding the problem, but when it came to designing how it would work, it had to be a collaboration between me and the AI because the AI could not do everything without me leading it in the right direction. One way I would give a student guidance without giving them the answer is by encouraging them to explain to me what they do understand and then really breaking down the part they are confused on into more simpler terms through asking them follow up questions, rather than just explaining it to them straight up. 

# DocuBot

DocuBot is a small documentation assistant that helps answer developer questions about a codebase.  
It can operate in three different modes:

1. **Naive LLM mode**  
   Sends the entire documentation corpus to a Gemini model and asks it to answer the question.

2. **Retrieval only mode**  
   Uses a simple indexing and scoring system to retrieve relevant snippets without calling an LLM.

3. **RAG mode (Retrieval Augmented Generation)**  
   Retrieves relevant snippets, then asks Gemini to answer using only those snippets.

The docs folder contains realistic developer documents (API reference, authentication notes, database notes), but these files are **just text**. They support retrieval experiments and do not require students to set up any backend systems.

---

## Setup

### 1. Install Python dependencies

    pip install -r requirements.txt

### 2. Configure environment variables

Copy the example file:

    cp .env.example .env

Then edit `.env` to include your Gemini API key:

    GEMINI_API_KEY=your_api_key_here

If you do not set a Gemini key, you can still run retrieval only mode.

---

## Running DocuBot

Start the program:

    python main.py

Choose a mode:

- **1**: Naive LLM (Gemini reads the full docs)  
- **2**: Retrieval only (no LLM)  
- **3**: RAG (retrieval + Gemini)

You can use built in sample queries or type your own.

---

## Running Retrieval Evaluation (optional)

    python evaluation.py

This prints simple retrieval hit rates for sample queries.

---

## Modifying the Project

You will primarily work in:

- `docubot.py`  
  Implement or improve the retrieval index, scoring, and snippet selection.

- `llm_client.py`  
  Adjust the prompts and behavior of LLM responses.

- `dataset.py`  
  Add or change sample queries for testing.

---

## Requirements

- Python 3.9+
- A Gemini API key for LLM features (only needed for modes 1 and 3)
- No database, no server setup, no external services besides LLM calls
