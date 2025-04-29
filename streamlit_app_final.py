import streamlit as st
import pandas as pd
import random

# --- データ読み込み ---
@st.cache_data
def load_data():
    df = pd.read_csv("words.csv")
    return df

df = load_data()

# --- セッション初期化 ---
if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answered" not in st.session_state:
    st.session_state.answered = False
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = ""
if "choices_shuffled" not in st.session_state:
    st.session_state.choices_shuffled = {}

# --- 問題を選択 ---
questions = df.to_dict(orient="records")

if st.session_state.current_q_idx >= len(questions):
    st.success(f"クイズ終了！スコア: {st.session_state.score} / {len(questions)}")
    if st.button("▶ 最初からやり直す"):
        st.session_state.current_q_idx = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.selected_answer = ""
        st.session_state.choices_shuffled = {}
        st.experimental_rerun()
        st.stop()

current_q = questions[st.session_state.current_q_idx]
sentence_with_blank = current_q["sentence_with_blank"]
correct_answer = current_q["answer"]
choices = current_q["choices"].split("|")
meaning_jp = current_q["meaning_jp"]
sentence_jp = current_q["sentence_jp"]

st.header(f"Q{st.session_state.current_q_idx + 1}")
st.write(sentence_with_blank)

# --- 選択肢シャッフル（1回だけ） ---
if st.session_state.current_q_idx not in st.session_state.choices_shuffled:
    st.session_state.choices_shuffled[st.session_state.current_q_idx] = random.sample(choices, len(choices))

shuffled_choices = st.session_state.choices_shuffled[st.session_state.current_q_idx]

# --- ラジオボタンで選択肢表示 ---
selected = st.radio("選択肢を選んでください", shuffled_choices, key=f"q{st.session_state.current_q_idx}")

# --- 解答ボタン ---
if not st.session_state.answered:
    if st.button("✅ 解答する"):
        st.session_state.selected_answer = selected
        st.session_state.answered = True
        st.experimental_rerun()
        st.stop()

# --- 正誤判定 ---
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
        st.stop()
