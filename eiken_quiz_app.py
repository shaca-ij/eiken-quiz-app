import streamlit as st
import pandas as pd
import random
import os
import sqlite3
from datetime import datetime

st.set_page_config(page_title="英単語クイズ", layout="centered")

@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

def init_db():
    conn = sqlite3.connect("quiz_results.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            timestamp TEXT,
            word TEXT,
            selected TEXT,
            correct TEXT,
            is_correct INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_result(user, word, selected, correct, is_correct):
    conn = sqlite3.connect("quiz_results.db")
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO results (username, timestamp, word, selected, correct, is_correct)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user, timestamp, word, selected, correct, int(is_correct)))
    conn.commit()
    conn.close()

def load_user_stats(username):
    conn = sqlite3.connect("quiz_results.db")
    query = '''
        SELECT word, SUM(is_correct) AS correct_count, COUNT(*) AS total_count
        FROM results
        WHERE username = ?
        GROUP BY word
    '''
    stats = pd.read_sql_query(query, conn, params=(username,))
    conn.close()
    if not stats.empty:
        stats["accuracy"] = stats["correct_count"] / stats["total_count"]
    return stats

# 復習モードの状態をセッションに保持
if "review_mode" not in st.session_state:
    st.session_state.review_mode = False

# サイドバーにチェックボックスを表示
st.sidebar.markdown("## モード設定")
st.session_state.review_mode = st.sidebar.checkbox(
    "復習モード（正答率が低い単語を優先）",
    value=st.session_state.review_mode
)


# 初期化
init_db()
if "page" not in st.session_state:
    st.session_state.page = "start"
if "quiz" not in st.session_state:
    st.session_state.quiz = []
if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = []
if "answered" not in st.session_state:
    st.session_state.answered = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "selected" not in st.session_state:
    st.session_state.selected = None

# スタート画面
if st.session_state.page == "start":
    st.title("📝 英単語クイズ")
    st.session_state.username = st.text_input("あなたの名前を入力してください：", value=st.session_state.username)
    num_questions = st.slider("出題する問題数を選んでください", min_value=1, max_value=50, value=10)

    if st.button("スタート") and st.session_state.username.strip():
        df = load_data()
        if st.session_state.review_mode:
            stats = load_user_stats(st.session_state.username)
            if not stats.empty:
                low_score_words = stats[stats["accuracy"] < 0.5]["word"].tolist()
                df = df[df["answer"].isin(low_score_words + df["answer"].tolist())]


        quiz = df.sample(frac=1).head(num_questions).to_dict(orient="records")
        st.session_state.quiz = quiz
        st.session_state.current_q_idx = 0
        st.session_state.user_answers = []
        st.session_state.answered = False
        st.session_state.selected = None
        st.session_state.page = "quiz"
        st.rerun()

# クイズ画面
elif st.session_state.page == "quiz":
    quiz = st.session_state.quiz
    current_idx = st.session_state.current_q_idx
    current_q = quiz[current_idx]

    percent_complete = int((current_idx + 1) / len(quiz) * 100)
    st.progress((current_idx + 1) / len(quiz), text=f"進捗: {percent_complete}%")

    st.markdown(f"<b>Q{current_idx + 1}:</b><br>{current_q['sentence_with_blank']}", unsafe_allow_html=True)

    choices = current_q["choices"].split("|")
    random.seed(current_idx)
    choices = random.sample(choices, len(choices))

    # ボタン式の選択肢表示
    selected = st.session_state.get("selected")
    if not st.session_state.answered:
        for choice in choices:
            if st.button(choice, key=f"choice_{current_idx}_{choice}"):
                st.session_state.selected = choice
                correct = current_q["answer"]
                is_correct = (choice == correct)
                st.session_state.user_answers.append({"selected": choice, "correct": correct})
                st.session_state.answered = True
                save_result(st.session_state.username, correct, choice, correct, is_correct)
                st.rerun()

    else:
        correct = current_q["answer"]
        choice = st.session_state.selected
        if choice == correct:
            st.success(f"✅ 正解！ {correct}")
        else:
            st.error(f"❌ 不正解... 正解は **{correct}**")

        st.markdown(f"**意味：** {current_q['meaning_jp']}")
        sentence_jp = current_q.get("sentence_jp", "")
        if pd.notna(sentence_jp):
            st.markdown(f"**和訳：** {sentence_jp.replace(chr(10), '<br>')}", unsafe_allow_html=True)

        if st.button("➡ 次の問題へ"):
            if current_idx + 1 < len(quiz):
                st.session_state.current_q_idx += 1
                st.session_state.answered = False
                st.session_state.selected = None
                st.rerun()
            else:
                st.session_state.page = "review"
                st.rerun()

# 結果と復習画面
elif st.session_state.page == "review":
    st.title("📊 結果と復習")
    score = sum(1 for ans in st.session_state.user_answers if ans["selected"] == ans["correct"])
    total = len(st.session_state.user_answers)
    st.markdown(f"### 正解数： {score} / {total}")

    st.markdown("---")
    st.markdown("### ❗ 復習（間違えた問題）")
    for i, (q, ans) in enumerate(zip(st.session_state.quiz, st.session_state.user_answers)):
        if ans["selected"] != ans["correct"]:
            st.markdown(f"**Q{i+1}:** {q['sentence_with_blank']}")
            st.markdown(f"- あなたの答え: {ans['selected']}")
            st.markdown(f"- 正解: **{ans['correct']}**")
            st.markdown(f"- 意味: {q['meaning_jp']}")
            if pd.notna(q['sentence_jp']):
                st.markdown(f"- 和訳: {q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)

    if st.button("🔁 もう一度挑戦"):
        st.session_state.page = "start"
        st.session_state.quiz = []
        st.session_state.user_answers = []
        st.session_state.current_q_idx = 0
        st.session_state.answered = False
        st.session_state.selected = None
        st.rerun()
