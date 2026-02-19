import streamlit as st
from utils import get_response

# Streamlit UI
st.image("assets/Unidistance_Logo_couleur_RVB.png", width=200)  # Display logo
st.markdown("""
*This is a digital reference tool for a psychology methods course, providing quick access to key information from the official textbook.*
""")
st.markdown("### ✍️ Wissenschaftliches Arbeiten und Kommunizieren")
st.markdown("""
Erhalte KI-gestützte Antworten auf Fragen zum wissenschaftlichen Arbeiten und Kommunizieren – 
basierend auf dem offiziellen [Lehrbuch](https://wissarbkom.bitbucket.io/) der Fakultät für Psychologie der Fernuni/UniDistance Schweiz.
""")

# Usage instructions
with st.expander("#### 🔍 So funktioniert es:"):
    st.markdown("""
    Gib eine konkrete Frage zum wissenschaftlichen Arbeiten in das Textfeld ein – z. B. zur Literaturrecherche, Zitierweise oder zur Gliederung wissenschaftlicher Arbeiten.  
    Das System durchsucht das Lehrbuch und liefert dir eine präzise Antwort samt Quellenangabe.  
    Wenn die Frage nicht im Buch behandelt wird, erhältst du eine entsprechende Rückmeldung.
    """)

# User input for the query
user_query = st.text_input(
    "Gib deine Frage ein:",
    placeholder="z. B. Was sind die Abschnitte in einer wissenschaftlichen Arbeit?"
)

if user_query:
    response, references = get_response(user_query)
    st.write("### Antwort:")
    st.write(response)

    if references:
        st.write("### Quellen:")
        for ref in references:
            score = ref.get("similarity", 0)

            if score >= 0.6:
                icon = "✅"
            elif score >= 0.4:
                icon = "ℹ️"
            else:
                icon = "⚠️"

            score_str = f"{score:.2f}"
            link_text = f"{ref['title']} ({ref['filename']}) - Ähnlichkeit: {score_str} {icon}"
            if ref.get("weblink"):
                st.markdown(f"- [{link_text}]({ref['weblink']})", unsafe_allow_html=True)
            else:
                st.write(f"- {link_text}")
    else:
        st.write("### Hinweis:")
        st.write("Die Frage scheint nicht im Zusammenhang mit den Inhalten des Lehrbuches zu stehen. Frage etwas zum Thema wissenschaftliches Arbeiten und Kommunizieren.")
