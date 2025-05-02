import streamlit as st
import pandas as pd
import random
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

# データベース初期化
init_db()

# セッション状態の初期化
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
if "review_mode" not in st.session_state:
    st.session_state.review_mode = False

# スタートページ
if st.session_state.page == "start":
    st.title("📝 英単語クイズ")
    st.session_state.username = st.text_input("あなたの名前を入力してください：", value=st.session_state.username)
    num_questions = st.slider("出題する問題数を選んでください", min_value=1, max_value=50, value=10)

    # 復習モードのオン/オフ切り替え
    st.session_state.review_mode = st.checkbox(
        "復習モードをオンにする（正答率が低い単語を優先）", 
        value=st.session_state.review_mode
    )

    if st.button("スタート") and st.session_state.username.strip():
        df = load_data()
        if st.session_state.review_mode:
            stats = load_user_stats(st.session_state.username)
            if not stats.empty:
                df["weight"] = df["answer"].apply(lambda word: 
                    1.0 if word not in stats["word"].values else 
                    max(0.1, 1.0 - stats.loc[stats["word"] == word, "accuracy"].values[0])
                )
                df = df.sample(n=num_questions, weights=df["weight"], replace=True)
            else:
                df = df.sample(n=num_questions)
        else:
            df = df.sample(n=num_questions)

        st.session_state.quiz = df.to_dict(orient="records")
        st.session_state.current_q_idx = 0
        st.session_state.user_answers = []
        st.session_state.page = "quiz"
        st.session_state.answered = False
        st.rerun()

# クイズページ
elif st.session_state.page == "quiz":
    quiz = st.session_state.quiz
    idx = st.session_state.current_q_idx
    current_q = quiz[idx]

    st.progress((idx + 1) / len(quiz), text=f"進捗: {int((idx + 1) / len(quiz) * 100)}%")

    st.markdown(f"""
        <div style='
            padding:15px; 
            border-radius:10px; 
            background-color:rgba(240, 248, 255, 0.7); 
            color:inherit;
        '>
            <b>Q{idx + 1}:</b><br>{current_q['sentence_with_blank'].replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

    # 選択肢との間にスペースを挿入
    st.markdown("<br>", unsafe_allow_html=True)

    choices = current_q["choices"].split("|")
    random.seed(idx)
    choices = random.sample(choices, len(choices))

    if not st.session_state.answered:
        for choice in choices:
            button_key = f"{idx}_{choice}"
            button_html = f"""
            <style>
                div[data-testid="stButton"] > button[{button_key}] {{
                    background-color: #e0f0ff;
                    color: black;
                    width: 100%;
                    padding: 0.5em;
                    margin: 0.3em 0;
                    border-radius: 5px;
                    border: 1px solid #ccc;
                }}
            </style>
            """
            st.markdown(button_html, unsafe_allow_html=True)
            if st.button(choice, key=button_key, use_container_width=True):
                correct = current_q["answer"]
                st.session_state.user_answers.append({"selected": choice, "correct": correct})
                st.session_state.answered = True
                save_result(st.session_state.username, correct, choice, correct, choice == correct)
                st.rerun()
    else:
        selected = st.session_state.user_answers[-1]["selected"]
        correct = current_q["answer"]
        if selected == correct:
            st.success(f"✅ 正解！ {correct}")
        else:
            st.error(f"❌ 不正解... 正解は {correct}")

        st.markdown(f"**意味：** {current_q['meaning_jp']}")
        if pd.notna(current_q["sentence_jp"]):
            st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)

        if st.button("➡ 次の問題へ"):
            if idx + 1 < len(quiz):
                st.session_state.current_q_idx += 1
                st.session_state.answered = False
                st.rerun()
            else:
                st.session_state.page = "review"
                st.rerun()

# 結果・復習ページ
elif st.session_state.page == "review":
    st.title("📊 結果と復習")

    score = sum(1 for ans in st.session_state.user_answers if ans["selected"] == ans["correct"])
    total = len(st.session_state.user_answers)
    st.markdown(f"### ✅ 正解数： {score} / {total}")

    st.markdown("---")
    st.markdown("### ❗ 間違えた問題の復習")

    for i, (q, ans) in enumerate(zip(st.session_state.quiz, st.session_state.user_answers)):
        if ans["selected"] != ans["correct"]:
            st.markdown(f"""
                <div style='padding:10px; margin:10px 0; background-color:#fff8f8; border-left: 5px solid #e74c3c;'>
                    <b>Q{i+1}:</b> {q['sentence_with_blank']}<br>
                    ❌ <b>あなたの答え:</b> {ans['selected']}<br>
                    ✅ <b>正解:</b> {ans['correct']}<br>
                    🧠 <b>意味:</b> {q['meaning_jp']}<br>
                    🌐 <b>和訳:</b> {q['sentence_jp'].replace(chr(10), '<br>') if pd.notna(q['sentence_jp']) else ''}
                </div>
            """, unsafe_allow_html=True)

    if st.button("🔁 もう一度挑戦"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

