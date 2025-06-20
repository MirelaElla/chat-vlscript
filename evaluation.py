import streamlit as st
import pandas as pd
import time
import datetime
from utils import get_embedding, retrieve_top_k, generate_answer, TOP_K, ALPHA, K1, B
import re

def parse_expected_files(raw):
    normalized = re.sub(r"[;|]", ",", str(raw))  # Convert other delimiters to commas
    parts = re.split(r"[\s,]+", normalized.strip())  # Split on spaces and commas
    return [p.strip() for p in parts if p.strip()]

# Load test set
testset = pd.read_excel("testset.xlsx")

# Streamlit UI
st.title("📊 RAG Evaluation Dashboard")
st.markdown("Evaluate performance of the RAG system on testset.xlsx. Note that this may take some time depending on the size of the test set and the models used. Also, the timings may vary depending on OpenAI API response times.")

st.markdown("### 📐 Quantitative Evaluation")
st.markdown("Use the button below to calculate speed and accuracy metrics for retrieval. If you want to include answer generation time, check the box below.")

# --- Quantitative Evaluation ---
evaluate_answers = st.checkbox("Include answer generation time", value=False)
if st.button("▶️ Run Quantitative Evaluation"):
    embedding_times = []
    retrieval_times = []
    answer_times = []
    recall_at_k = []
    reciprocal_ranks = []

    for i, row in testset.iterrows():
        question = row["question"]
        expected_files_raw = row["file"]
        expected_file = parse_expected_files(expected_files_raw)

        # Measure embedding time
        start = time.time()
        query_embedding = get_embedding(question)
        embedding_duration = time.time() - start
        embedding_times.append(embedding_duration)

        # Measure retrieval time
        start = time.time()
        context, references = retrieve_top_k(query_embedding, question)
        retrieval_duration = time.time() - start
        retrieval_times.append(retrieval_duration)

        # Evaluate recall@K
        retrieved_files = [ref["filename"] for ref in references]
        hit = any(f in retrieved_files for f in expected_file)
        recall_at_k.append(1 if hit else 0)

        # Evaluate MRR
        reciprocal_rank = 0
        for rank, file in enumerate(retrieved_files, start=1):
            if file in expected_file:
                reciprocal_rank = 1 / rank
                break
        reciprocal_ranks.append(reciprocal_rank)

        # Measure answer generation time
        if evaluate_answers:
            start = time.time()
            _ = generate_answer(context, question)
            answer_duration = time.time() - start
        else:
            answer_duration = 0.0
        answer_times.append(answer_duration)

    # Results
    st.success("✅ Evaluation complete.")
    st.markdown(f"**⚙️ Retrieval Parameters:**  \n"
            f"- `ALPHA`: {ALPHA} (semantic vs. lexical weight)  \n"
            f"- `K1`: {K1} (BM25 term saturation)  \n"
            f"- `B`: {B} (BM25 length normalization)")

    st.markdown("### 📈 Metrics Summary")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Avg. Embedding Time", f"{sum(embedding_times)/len(embedding_times):.3f} s")
        st.metric("Avg. Retrieval Time", f"{sum(retrieval_times)/len(retrieval_times):.3f} s")
        if evaluate_answers:
            st.metric("Avg. Answer Gen. Time", f"{sum(answer_times)/len(answer_times):.3f} s")
        else:
            st.metric("Avg. Answer Gen. Time", "Not measured")

    with col2:
        st.metric("Recall@K", f"{sum(recall_at_k)/len(recall_at_k):.2%}")
        st.metric("MRR", f"{sum(reciprocal_ranks)/len(reciprocal_ranks):.3f}")

    st.markdown("---")
        # --- Show failed retrievals ---
    failed_logs = []

    for i, row in testset.iterrows():
        question = row["question"]
        expected_file_list = parse_expected_files(row["file"])

        query_embedding = get_embedding(question)
        context, references = retrieve_top_k(query_embedding, question)

        top_k_files = [ref["filename"] for ref in references]
        top_k_scores = [f"{ref['similarity']:.2f}" for ref in references]

        if not any(f in top_k_files for f in expected_file_list):
            failed_logs.append({
                "question": question,
                "expected_file(s)": ", ".join(expected_file_list),
                "top_k_files": ", ".join(top_k_files),
                "similarity_scores": ", ".join(top_k_scores)
            })
    
    num_failed = len(failed_logs)
    num_total = len(testset)
    st.markdown(f"### ❌ Failed Queries (Recall@{TOP_K} Misses) – {num_failed} of {num_total}")

    if failed_logs:
        failed_df = pd.DataFrame(failed_logs)
        st.dataframe(failed_df)
    else:
        st.success("🎉 All queries retrieved the correct file within the top-K!")


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
        context, references = retrieve_top_k(query_embedding, question)
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
