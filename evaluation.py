import streamlit as st
import pandas as pd
import time
from utils import get_embedding, cosine_similarity, df, retrieve_top_k, generate_answer, TOP_K

# Load test set
testset = pd.read_excel("testset.xlsx")

# Streamlit UI
st.title("📊 RAG Evaluation Dashboard")
st.markdown("Evaluate performance of the RAG system on testset.xlsx. Note that this may take some time depending on the size of the test set and the models used.")

if st.button("🔍 Run Evaluation"):
    embedding_times = []
    retrieval_times = []
    answer_times = []
    recall_at_k = []
    reciprocal_ranks = []

    for i, row in testset.iterrows():
        question = row["question"]
        expected_file = row["file"]

        # Measure embedding time
        start = time.time()
        query_embedding = get_embedding(question)
        embedding_duration = time.time() - start
        embedding_times.append(embedding_duration)

        # Measure retrieval time
        start = time.time()
        context, references = retrieve_top_k(query_embedding)
        retrieval_duration = time.time() - start
        retrieval_times.append(retrieval_duration)

        # Evaluate recall@K
        retrieved_files = [ref["filename"] for ref in references]
        hit = expected_file in retrieved_files
        recall_at_k.append(1 if hit else 0)

        # Evaluate MRR
        if expected_file in retrieved_files:
            rank = retrieved_files.index(expected_file) + 1
            reciprocal_ranks.append(1 / rank)
        else:
            reciprocal_ranks.append(0)

        # Measure answer generation time
        start = time.time()
        _ = generate_answer(context, question)
        answer_duration = time.time() - start
        answer_times.append(answer_duration)

    # Results
    st.success("✅ Evaluation complete.")
    st.markdown("### 📈 Metrics Summary")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Avg. Embedding Time", f"{sum(embedding_times)/len(embedding_times):.3f} s")
        st.metric("Avg. Retrieval Time", f"{sum(retrieval_times)/len(retrieval_times):.3f} s")
        st.metric("Avg. Answer Gen. Time", f"{sum(answer_times)/len(answer_times):.3f} s")

    with col2:
        st.metric("Recall@K", f"{sum(recall_at_k)/len(recall_at_k):.2%}")
        st.metric("MRR", f"{sum(reciprocal_ranks)/len(reciprocal_ranks):.3f}")

    st.markdown("---")
    st.markdown("### 🧪 Test Set Details")
    st.dataframe(testset)
