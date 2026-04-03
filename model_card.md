# DocuBot Model Card

This model card is a short reflection on your DocuBot system. Fill it out after you have implemented retrieval and experimented with all three modes:

1. Naive LLM over full docs  
2. Retrieval only  
3. RAG (retrieval plus LLM)

Use clear, honest descriptions. It is fine if your system is imperfect.

---

## 1. System Overview

**What is DocuBot trying to do?**  
Describe the overall goal in 2 to 3 sentences.

Take local input docs and use them to answer follow up questions. The aim here is to speed up the process of looking through any documentation by having the model do it rather than having a human read through it all. 

**What inputs does DocuBot take?**  
For example: user question, docs in folder, environment variables.

It has documents in the docs folder and it receives a simple, one sentence question from the user.

**What outputs does DocuBot produce?**

An answer to the question formulated with information retrieved from the given documents. 

---

## 2. Retrieval Design

**How does your retrieval system work?**  
Describe your choices for indexing and scoring.

- How do you turn documents into an index?

Documents are split into paragraphs, then each unique word is mapped to a list of paragraph chunk IDs where it appears, creating an inverted index.

- How do you score relevance for a query?

The system counts how many times meaningful query words (3+ characters) appear in each paragraph chunk, with higher counts indicating stronger relevance.

- How do you choose top snippets?

The system uses the index to find candidate chunks containing query words, scores them, filters out any below the minimum threshold (score < 3), sorts by score descending, and returns the top k results.

**What tradeoffs did you make?**  
For example: speed vs precision, simplicity vs accuracy.

Simplicity vs. Accuracy

---

## 3. Use of the LLM (Gemini)

**When does DocuBot call the LLM and when does it not?**  
Briefly describe how each mode behaves.

- Naive LLM mode: Always calls the LLM with the entire corpus of documents concatenated together, no retrieval filtering applied.
- Retrieval only mode: Never calls the LLM; returns raw paragraph chunks that match the query based on word-count scoring alone.
- RAG mode: Calls the LLM only after retrieval; sends the top-k most relevant paragraph snippets to the LLM to generate a natural language answer grounded in those specific chunks.

**What instructions do you give the LLM to keep it grounded?**  
Summarize the rules from your prompt. For example: only use snippets, say "I do not know" when needed, cite files.

The LLM is instructed to answer using only the information in the provided snippets and not to invent functions, endpoints, or configuration values. If the snippets don't provide enough evidence to answer confidently, it must reply exactly "I do not know based on the docs I have." When answering, the model is told to briefly mention which files it relied on for the answer.

---

## 4. Experiments and Comparisons

Run the **same set of queries** in all three modes. Fill in the table with short notes.

You can reuse or adapt the queries from `dataset.py`.

| Query | Naive LLM: helpful or harmful? | Retrieval only: helpful or harmful? | RAG: helpful or harmful? | Notes |
|------|---------------------------------|--------------------------------------|---------------------------|-------|
| Example: Where is the auth token generated? | | | | |
| Example: How do I connect to the database? | | | | |
| Example: Which endpoint lists all users? | | | | |
| Example: How does a client refresh an access token? | | | | |

**What patterns did you notice?**  

- When does naive LLM look impressive but untrustworthy?  
- When is retrieval only clearly better?  
- When is RAG clearly better than both?

Naive LLM generates fluent, confident-sounding answers but often invents plausible details not in the actual docs, making it untrustworthy. Retrieval only is better when you need exact source text or verifiable details like configuration values without LLM interpretation. RAG is clearly superior when answers require synthesizing multiple paragraphs into coherent explanations, combining retrieval's accuracy with natural language clarity.

---

## 5. Failure Cases and Guardrails

**Describe at least two concrete failure cases you observed.**  
For each one, say:

- What was the question?  
- What did the system do?  
- What should have happened instead?

> "What's 2 + 2" should have returned a guardrail but it did not because it was searching for the word "2" which does appear in the docs, so it returned irrelevant information


**When should DocuBot say “I do not know based on the docs I have”?**  
Give at least two specific situations.

When the query is about topics not covered in the documentation and when retrieved chunks score below the minimum threshold (< 3)

**What guardrails did you implement?**  
Examples: refusal rules, thresholds, limits on snippets, safe defaults.

Minimum score threshold (3)
Word length filter
Top-k limit (default of 3)
Explicit refusal message

---

## 6. Limitations and Future Improvements

**Current limitations**  
List at least three limitations of your DocuBot system.

1. No semantic understanding
2. Paragraph chunking breaks context
3. Fixed scoring threshold

**Future improvements**  
List two or three changes that would most improve reliability or usefulness.

1. Implement overlapping chunk windows
2. Add adaptive scoring thresholds


---

## 7. Responsible Use

**Where could this system cause real world harm if used carelessly?**  
Think about wrong answers, missing information, or over trusting the LLM.

Developers might trust incorrect or incomplete answers when configuring security-critical features like authentication, database permissions, or API access controls, leading to vulnerabilities in production systems. The system could miss crucial warnings or edge cases that are mentioned in parts of the documentation that didn't score highly enough, causing developers to skip important safety checks. In naive LLM mode, the model may confidently hallucinate plausible-sounding but completely wrong configuration values, endpoint names, or security practices that don't exist in the actual codebase, which could break systems or create security holes if implemented without verification

**What instructions would you give real developers who want to use DocuBot safely?**  
Write 2 to 4 short bullet points.

- Always verify security-critical info
- Use RAG mode over naive LLM
- Treat answers as starting points, not final authority

---
