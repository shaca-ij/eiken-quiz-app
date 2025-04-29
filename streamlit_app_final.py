import streamlit as st
import random
import pandas as pd

# --- 読み込み ---
df = pd.read_csv("words.csv")

# --- 最初だけシャッフルセット ---
if "questions" not in st.session_state:
    questions = df.to_dict(orient="records")
    for q in questions:
        q["choices_shuffled"] = random.sample(q["choices"].split("|"), len(q["choices"].split("|")))
    random.shuffle(questions)
    st.session_state.questions = questions
    st.session_state.current_q_idx = 0
    st.session_state.correct_count = 0

questions = st.session_state.questions
current_idx = st.session_state.current_q_idx
current_q = questions[current_idx]

# --- UI表示 ---
st.title("英検クイズアプリ")
st.write(f"**Q{current_idx+1}: {current_q['sentence_with_blank']}**")

# --- ラジオボタン ---
user_answer = st.radio(
    "選択肢から選んでください",
    current_q["choices_shuffled"],
    key=f"q_{current_idx}"
)

# --- ボタン ---
if st.button("回答する"):
    if user_answer is None:
        st.warning("選択肢を選んでからボタンを押してください！")
        st.stop()

    correct_answer = current_q["answer"]
    if user_answer == correct_answer:
        st.success("正解です！")
        st.session_state.correct_count += 1
    else:
        st.error(f"不正解！ 正解は {correct_answer} です")
    st.info(f"意味: {current_q['meaning_jp']}")
    st.info(f"和訳: {current_q['sentence_jp']}")

    # --- 次の問題へ進むボタンを表示 ---
    if st.button("次の問題へ"):
        if current_idx + 1 < len(questions):
            st.session_state.current_q_idx += 1
            st.experimental_rerun()
        else:
            st.balloons()
            st.success(f"クイズ終了！正解数: {st.session_state.correct_count} / {len(questions)}")

