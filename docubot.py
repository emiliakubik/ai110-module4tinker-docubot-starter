"""
Core DocuBot class responsible for:
- Loading documents from the docs/ folder
- Building a simple retrieval index (Phase 1)
- Retrieving relevant snippets (Phase 1)
- Supporting retrieval only answers
- Supporting RAG answers when paired with Gemini (Phase 2)
"""

import os
import glob

class DocuBot:
    def __init__(self, docs_folder="docs", llm_client=None):
        """
        docs_folder: directory containing project documentation files
        llm_client: optional Gemini client for LLM based answers
        """
        self.docs_folder = docs_folder
        self.llm_client = llm_client

        # Load documents into memory
        self.documents = self.load_documents()  # List of (chunk_id, text)

        # Build a retrieval index (implemented in Phase 1)
        self.index = self.build_index(self.documents)

    # -----------------------------------------------------------
    # Document Loading
    # -----------------------------------------------------------

    def chunk_text(self, text):
        """
        Splits text into paragraphs (chunks separated by blank lines).
        Returns a list of non-empty paragraph strings.
        """
        # Split on double newlines (paragraph breaks)
        paragraphs = text.split("\n\n")
        
        # Filter out empty chunks and strip whitespace
        chunks = [p.strip() for p in paragraphs if p.strip()]
        
        return chunks

    def load_documents(self):
        """
        Loads all .md and .txt files inside docs_folder and chunks them into paragraphs.
        Returns a list of tuples: (chunk_id, chunk_text)
        where chunk_id is "filename::para_0", "filename::para_1", etc.
        """
        chunks = []
        pattern = os.path.join(self.docs_folder, "*.*")
        for path in glob.glob(pattern):
            if path.endswith(".md") or path.endswith(".txt"):
                with open(path, "r", encoding="utf8") as f:
                    text = f.read()
                filename = os.path.basename(path)
                
                # Split into paragraphs
                paragraphs = self.chunk_text(text)
                
                # Create chunk entries with unique IDs
                for idx, para in enumerate(paragraphs):
                    chunk_id = f"{filename}::para_{idx}"
                    chunks.append((chunk_id, para))
        
        return chunks

    # -----------------------------------------------------------
    # Index Construction (Phase 1)
    # -----------------------------------------------------------

    def build_index(self, documents):
        """
        Build a tiny inverted index mapping lowercase words to the chunks
        they appear in.

        Example structure:
        {
            "token": ["AUTH.md::para_0", "API_REFERENCE.md::para_2"],
            "database": ["DATABASE.md::para_1"]
        }

        Keep this simple: split on whitespace, lowercase tokens,
        ignore punctuation if needed.
        """
        index = {}
        
        for chunk_id, text in documents:
            # Extract words: lowercase and split on whitespace
            words = text.lower().split()
            
            # Add each unique word to the index
            unique_words = set(words)
            for word in unique_words:
                if word not in index:
                    index[word] = []
                if chunk_id not in index[word]:
                    index[word].append(chunk_id)
        
        return index

    # -----------------------------------------------------------
    # Scoring and Retrieval (Phase 1)
    # -----------------------------------------------------------

    def score_document(self, query, text):
        """
        Return a simple relevance score for how well the text matches the query.

        Suggested baseline:
        - Convert query into lowercase words
        - Filter out very short words (noise like single digits, articles)
        - Count how many meaningful words appear in the text
        - Return the count as the score
        """
        # Convert query to lowercase words
        query_words = query.lower().split()
        
        # Filter out very short words (single chars, digits, articles, etc.)
        # Only keep words with 3+ characters to avoid noise
        meaningful_words = [w for w in query_words if len(w) >= 3]
        
        # If no meaningful words remain, return 0 (prevents matching on noise)
        if not meaningful_words:
            return 0
        
        # Convert text to lowercase for matching
        text_lower = text.lower()
        
        # Count occurrences of each meaningful query word in the text
        score = 0
        for word in meaningful_words:
            score += text_lower.count(word)
        
        return score

    def retrieve(self, query, top_k=3, min_score=3):
        """
        Use the index and scoring function to select top_k relevant paragraph chunks.

        Return a list of (chunk_id, text) sorted by score descending.
        
        Args:
            query: The search query
            top_k: Maximum number of results to return
            min_score: Minimum score threshold - chunks scoring below this are filtered out.
                       This acts as a guardrail to prevent answering with weak evidence.
                       Default is 3 (at least 3 query word occurrences).
        """
        # Get query words and filter out short/meaningless ones
        query_words = query.lower().split()
        meaningful_words = [w for w in query_words if len(w) >= 3]
        
        # If no meaningful words, return empty (prevents noise matching)
        if not meaningful_words:
            return []
        
        # Find candidate chunks using the index
        candidate_chunk_ids = set()
        for word in meaningful_words:
            if word in self.index:
                candidate_chunk_ids.update(self.index[word])
        
        # If no candidates found, fall back to scoring all chunks
        if not candidate_chunk_ids:
            candidate_chunk_ids = {chunk_id for chunk_id, _ in self.documents}
        
        # Score each candidate chunk
        scored_chunks = []
        for chunk_id, text in self.documents:
            if chunk_id in candidate_chunk_ids:
                score = self.score_document(query, text)
                # Only include chunks that meet the minimum score threshold
                if score >= min_score:
                    scored_chunks.append((score, chunk_id, text))
        
        # Sort by score descending (highest first)
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        
        # Return top_k results as (chunk_id, text) tuples
        results = [(chunk_id, text) for score, chunk_id, text in scored_chunks]
        
        return results[:top_k]

    # -----------------------------------------------------------
    # Answering Modes
    # -----------------------------------------------------------

    def answer_retrieval_only(self, query, top_k=3, min_score=3):
        """
        Phase 1 retrieval only mode.
        Returns raw snippets and chunk identifiers with no LLM involved.
        
        Args:
            query: The user's question
            top_k: Number of chunks to retrieve
            min_score: Minimum relevance score threshold (guardrail against weak evidence)
        """
        snippets = self.retrieve(query, top_k=top_k, min_score=min_score)

        if not snippets:
            return "I do not know based on these docs."

        formatted = []
        for chunk_id, text in snippets:
            formatted.append(f"[{chunk_id}]\n{text}\n")

        return "\n---\n".join(formatted)

    def answer_rag(self, query, top_k=3, min_score=3):
        """
        Phase 2 RAG mode.
        Uses student retrieval to select snippets, then asks Gemini
        to generate an answer using only those snippets.
        
        Args:
            query: The user's question
            top_k: Number of chunks to retrieve
            min_score: Minimum relevance score threshold (guardrail against weak evidence)
        """
        if self.llm_client is None:
            raise RuntimeError(
                "RAG mode requires an LLM client. Provide a GeminiClient instance."
            )

        snippets = self.retrieve(query, top_k=top_k, min_score=min_score)

        if not snippets:
            return "I do not know based on these docs."

        return self.llm_client.answer_from_snippets(query, snippets)

    # -----------------------------------------------------------
    # Bonus Helper: concatenated docs for naive generation mode
    # -----------------------------------------------------------

    def full_corpus_text(self):
        """
        Returns all documents concatenated into a single string.
        This is used in Phase 0 for naive 'generation only' baselines.
        """
        return "\n\n".join(text for _, text in self.documents)
