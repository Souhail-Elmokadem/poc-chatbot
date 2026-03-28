import json
import os
import re
import unicodedata
from difflib import SequenceMatcher

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(page_title="Chatbot FAQ", page_icon="💬", layout="centered")

# =========================
# CONFIG
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"
FALLBACK_ANSWER = "Désolé, je n'ai pas trouvé de réponse claire dans la FAQ."
SIMILARITY_THRESHOLD = 0.45
TOP_K = 3

client = None
if GROQ_API_KEY:
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )

# =========================
# LOAD FAQ FROM JSON FILE
# =========================
def load_faq():
    try:
        with open("faq.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [
            {
                "questions": ["bonjour", "salut"],
                "answer": "Bonjour 👋"
            }
        ]


FAQ_DATA = load_faq()

# =========================
# HELPERS
# =========================
def normalize(text):
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def retrieve_matches(user_input, top_k=TOP_K):
    user_input = normalize(user_input)
    matches = []

    for item in FAQ_DATA:
        for q in item["questions"]:
            score = similarity(user_input, normalize(q))
            matches.append({
                "score": score,
                "question": q,
                "answer": item["answer"]
            })

    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:top_k]


def build_context(matches):
    blocks = []
    for i, match in enumerate(matches, start=1):
        blocks.append(
            f"FAQ {i}\n"
            f"Question: {match['question']}\n"
            f"Réponse: {match['answer']}"
        )
    return "\n\n".join(blocks)


# =========================
# MODE 1 : STANDARD
# =========================
def get_standard_answer(user_input):
    matches = retrieve_matches(user_input, top_k=1)

    if not matches:
        return FALLBACK_ANSWER

    best_match = matches[0]
    if best_match["score"] >= SIMILARITY_THRESHOLD:
        return best_match["answer"]

    return FALLBACK_ANSWER


# =========================
# MODE 2 : GROQ
# =========================
def get_groq_answer(user_input):
    matches = retrieve_matches(user_input, top_k=TOP_K)

    if not matches or matches[0]["score"] < SIMILARITY_THRESHOLD:
        return FALLBACK_ANSWER

    if client is None:
        return "Clé Groq absente. Ajoute GROQ_API_KEY dans le fichier .env."

    context = build_context(matches)

    system_prompt = (
        "Tu es un assistant FAQ.\n"
        "Tu réponds uniquement à partir du contexte fourni.\n"
        "N'invente aucune information.\n"
        "Si le contexte ne permet pas de répondre clairement, réponds exactement : "
        f"'{FALLBACK_ANSWER}'\n"
        "Réponds de façon courte, claire et naturelle."
    )

    user_prompt = (
        f"Question utilisateur : {user_input}\n\n"
        f"Contexte FAQ :\n{context}\n\n"
        "Donne la meilleure réponse possible en te basant uniquement sur le contexte."
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=200
    )

    return response.choices[0].message.content.strip()


# =========================
# UI
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Pose-moi une question 👇"}
    ]

with st.sidebar:
    st.title("⚙️ Paramètres")

    mode = st.selectbox(
        "Choisir le mode",
        ["Standard", "Groq"]
    )

    st.write(f"Mode actuel : **{mode}**")

    if mode == "Groq":
        if GROQ_API_KEY:
            st.success("Clé Groq détectée")
            st.write(f"Modèle : `{GROQ_MODEL}`")
        else:
            st.error("Clé Groq absente dans .env")

    with st.expander("Voir les questions FAQ"):
        for item in FAQ_DATA:
            st.write("- " + " / ".join(item["questions"]))

    if st.button("Vider la conversation"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Conversation réinitialisée. Pose-moi une question 👇"}
        ]
        st.rerun()

st.title("💬 Chatbot configurable")
st.caption("FAQ JSON modifiable avec 2 modes : Standard ou Groq")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Ta question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        if mode == "Standard":
            answer = get_standard_answer(user_input)
        else:
            answer = get_groq_answer(user_input)
    except Exception as e:
        answer = f"Erreur : {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
