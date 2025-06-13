import streamlit as st
import pandas as pd
import time
import datetime
from utils import get_embedding, retrieve_top_k, generate_answer, TOP_K

# Load test set
testset = pd.read_excel("testset.xlsx")

# Streamlit UI
st.title("📊 RAG Evaluation Dashboard")
st.markdown("Evaluate performance of the RAG system on testset.xlsx. Note that this may take some time depending on the size of the test set and the models used. Also, the timings may vary depending on OpenAI API response times.")

st.markdown("### 📐 Quantitative Evaluation")
st.markdown("Use the button below to calculate speed and accuracy metrics for retrieval and speed of answer generation.")

# --- Quantitative Evaluation ---
if st.button("▶️ Run Quantitative Evaluation"):
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
    st.markdown("### 🔍 Test Set Details")
    st.dataframe(testset)

# --- Qualitative Evaluation ---
st.markdown("---")
st.markdown("### 📝 Qualitative Evaluation of Answers")
st.markdown("Use the button below to generate answers and save them (with context) to a CSV for manual inspection.")

if st.button("▶️ Run Qualitative Evaluation"):
    st.info("Generating responses and collecting retrieval data...")

    questions = []
    expected_files = []
    generated_responses = []
    top_k_lists = []
    embedding_times = []
    retrieval_times = []
    answer_times = []

    for i, row in testset.iterrows():
        question = row["question"]
        expected_file = row["file"]

        # Embedding
        start = time.time()
        query_embedding = get_embedding(question)
        embedding_duration = time.time() - start
        embedding_times.append(embedding_duration)

        # Retrieval
        start = time.time()
        context, references = retrieve_top_k(query_embedding)
        retrieval_duration = time.time() - start
        retrieval_times.append(retrieval_duration)

        top_k_files = [ref["filename"] for ref in references]

        # Answer generation
        start = time.time()
        answer = generate_answer(context, question)
        answer_duration = time.time() - start
        answer_times.append(answer_duration)

        # Collect
        questions.append(question)
        expected_files.append(expected_file)
        generated_responses.append(answer)
        top_k_lists.append(top_k_files)

    # Create results DataFrame
    results_df = pd.DataFrame({
        "id": testset.get("id", range(len(testset))),
        "question": questions,
        "expected_file": expected_files,
        "top_k_files": top_k_lists,
        "generated_response": generated_responses,
        "embedding_time_s": embedding_times,
        "retrieval_time_s": retrieval_times,
        "answer_time_s": answer_times
    })

    # Add timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"rag_qualitative_eval_{timestamp}.csv"
    results_df.to_csv(output_file, index=False)

    st.success(f"✅ Evaluation complete. Results saved to `{output_file}`.")
