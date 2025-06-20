# 📊 Retrieval-Augmented Generation (RAG) Evaluation

This document summarizes the evaluation of hybrid retrieval strategies for a psychology course assistant. We tested combinations of **semantic vector search** with **lexical search** methods (TF-IDF, BM25), tuning various parameters to measure retrieval performance.

## 🔍 Methods

### Lexical Search Approaches

| Method  | Description |
|---------|-------------|
| **TF-IDF** | Measures how important a word is to a document relative to the corpus. Common words (e.g. "und", "Abschnitt") get lower scores. |
| **BM25**  | Builds on TF-IDF by adding document length normalization and non-linear term frequency scaling. Performs better on sparse or short queries. |

### Semantic Search

Uses `text-embedding-3-small` from OpenAI to embed both the query and document chunks. Cosine similarity is used to find relevant matches.

### Parameters

- **K (Top-K)**: Number of top documents retrieved.
- **Alpha**: Weight between semantic similarity (vector-based) and lexical similarity (keyword-based).  
  - α = 1 → pure vector search  
  - α = 0 → pure lexical search
- **BM25 k1**: Term frequency saturation (higher = more weight on frequent terms).
- **BM25 b**: Document length normalization (higher = more penalty on long docs).

---

## 📈 Evaluation Results

### TF-IDF Results

| K | Alpha | Misses | Total | Recall@K |
|---|-------|--------|--------|----------|
| 5 | 0.9   | 3      | 80     | 96.3% ✅✅ |
| 3 | 1.0   | 4      | 80     | 95.0% ✅✅ |
| 3 | 0.9   | 4      | 80     | 95.0% ✅✅ |
| 3 | 0.5   | 6      | 80     | 92.5% ✅ |
| 3 | 0.1   | 14     | 80     | 82.5% ❌ |

### BM25 Results

| K | Alpha | k1  | b    | Misses | Total | Recall@K |
|---|-------|-----|------|--------|--------|-----------|
| 3 | 1.0   | 1.2 | 0.8  | 4      | 81     | 95.1% ✅✅ |
| 3 | 0.9   | 1.5 | 0.75 | 7      | 81     | 91.4% ✅ |
| 3 | 0.9   | 0.9 | 0.85 | 7      | 81     | 91.4% ✅ |
| 3 | 0.9   | 1.2 | 0.8  | 7      | 81     | 91.4% ✅ |
| 3 | 0.9   | 1.2 | 0.0  | 7      | 81     | 91.4% ✅ |
| 3 | 0.6   | 1.5 | 0.75 | 12     | 81     | 85.2% ❌ |



---

## 🧠 Discussion

- **Hybrid search didn’t outperform pure vector search.** This was surprising and raises questions about:
  - BM25 implementation. Recall values never change with varying k1 and b values, which is weird.
  - Whether **semantic embeddings already capture relevance** better in this domain.
  -	The book sections may not differ significantly in their word specificity (in that case we would not benefit from hybrid search -> stay with semantic search)
  -	Is the testset biased to benefit semantic search? (e.g., more synonyms/paraphrases than exact text excerpts)

- **More Testset questions** may be needed to draw strong conclusions.

## ✅ Conclusion

Current best configuration is **K=3 (or even 5 with more resources), Alpha=1.0 (semantic only)** yielding ~95% Recall@K. Hybrid search may still be useful in certain cases (TBD).