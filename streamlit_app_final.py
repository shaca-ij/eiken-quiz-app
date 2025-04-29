import streamlit as st
import pandas as pd
import random

# --- 設定 ---
CSV_FILE = "words.csv"  # CSVファイル名
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1IfqASoqhNwKFYoJdjkIPIXcO3mCE5j2Ng2PtmlWdj1c/edit"

# --- セッション初期化 ---
if "quiz_questions" not in st.session_state:
    questions_df = pd.read_csv(CSV_FILE)
    st.session_state.quiz_questions = questions_df.sample(frac=1).reset_index(drop=True)

if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answered" not in st.session_state:
    st.session_state.answered = False
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = ""

quiz_questions = st.session_state.quiz_questions

# --- 問題終了判定 ---
if st.session_state.current_q_idx >= len(quiz_questions):
    st.success(f"クイズ終了！正解数: {st.session_state.score}/{len(quiz_questions)}")
    st.stop()

# --- 現在の問題 ---
current_q = quiz_questions.iloc[st.session_state.current_q_idx]
question_text = current_q["sentence_with_blank"]
correct_answer = current_q["answer"]
choices = current_q["choices"].split("|")
meaning_jp = current_q["meaning_jp"]
sentence_jp = current_q["sentence_jp"]

# --- UI表示 ---
st.title("英検準2級 単語クイズ")

st.header(f"Q{st.session_state.current_q_idx + 1}: {question_text}")

# ランダムシャッフルして表示
shuffled_choices = random.sample(choices, len(choices))

selected = st.radio("選択肢を選んでください", shuffled_choices, key=f"question_{st.session_state.current_q_idx}")

# --- 解答ボタン ---
if not st.session_state.answered:
    if st.button("✅ 解答する"):
        st.session_state.selected_answer = selected
        st.session_state.answered = True
        st.experimental_rerun()
        st.stop()  # 🔥リロード後、強制停止！

if st.session_state.answered:
    if st.session_state.selected_answer == correct_answer:
        st.success(f"✅ 正解！ {correct_answer}")
        st.session_state.score += 1
    else:
        st.error(f"❌ 不正解！ 正解は {correct_answer}")

    st.info(f"【意味】{meaning_jp}")
    st.info(f"【和訳】{sentence_jp}")

    if st.button("▶ 次の問題へ"):
        st.session_state.current_q_idx += 1
        st.session_state.answered = False
        st.session_state.selected_answer = ""
        st.experimental_rerun()
        st.stop()  # 🔥リロード後、強制停止！
