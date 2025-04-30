import streamlit as st
import pandas as pd
import random

# CSV読み込み（適宜パスを変更）
df = pd.read_csv("words.csv")

st.set_page_config(page_title="英単語クイズ", layout="wide")
st.markdown("<h1 style='text-align:center;'>英単語クイズ</h1>", unsafe_allow_html=True)

# セッション状態の初期化
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "quiz" not in st.session_state:
    st.session_state.quiz = []
if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "user_answer" not in st.session_state:
    st.session_state.user_answer = None
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "correct_history" not in st.session_state:
    st.session_state.correct_history = []
if "review_mode" not in st.session_state:
    st.session_state.review_mode = False
if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0
if "progress" not in st.session_state:
    st.session_state.progress = 0.0

# スタート画面
if not st.session_state.quiz_started:
    st.subheader("出題数を選んでスタート")
    num_questions = st.slider("問題数", min_value=5, max_value=len(df), value=10)
    if st.button("スタート"):
        st.session_state.quiz_started = True
        st.session_state.quiz = df.sample(frac=1).head(num_questions).to_dict(orient="records")
        st.session_state.current_q_idx = 0
        st.session_state.user_answer = None
        st.session_state.show_result = False
        st.session_state.correct_history = []
        st.session_state.review_mode = False
        st.session_state.total_questions = num_questions
        st.session_state.progress = 0.0
        st.stop()
    st.stop()

# クイズ進行中
quiz = st.session_state.quiz
idx = st.session_state.current_q_idx
current_q = quiz[idx]

# 進捗バー
st.progress(st.session_state.progress)

# 問題文表示
st.markdown(f"<div style='background-color:#f0f8ff; padding:10px; border-radius:10px;'>"
            f"<strong>Q{idx+1}:</strong><br>{current_q['sentence_with_blank'].replace('\\n', '<br>')}</div>", unsafe_allow_html=True)

# 和訳
st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)

# 選択肢表示
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    for i, opt in enumerate(current_q['choices'].split("/")):
        if st.button(f"{opt}", key=f"opt_{i}"):
            st.session_state.user_answer = opt
            st.session_state.show_result = True
            is_correct = (opt == current_q['answer'])
            st.session_state.correct_history.append(is_correct)
            st.session_state.progress = (idx + 1) / st.session_state.total_questions
            st.stop()

# 解答結果の表示
if st.session_state.show_result:
    user_ans = st.session_state.user_answer
    correct = current_q['answer']
    if user_ans == correct:
        st.success(f"✅ 正解！ {correct}")
    else:
        st.error(f"✖ 不正解... 正解は {correct}")
    st.markdown(f"**意味：** {current_q['meaning_jp']}")

    if st.button("次の問題へ"):
        st.session_state.current_q_idx += 1
        st.session_state.user_answer = None
        st.session_state.show_result = False
        if st.session_state.current_q_idx >= st.session_state.total_questions:
            st.session_state.review_mode = True
        st.stop()

# 終了時
if st.session_state.review_mode:
    st.subheader("🎉 終了！お疲れ様でした。")
    corrects = sum(st.session_state.correct_history)
    total = st.session_state.total_questions
    st.write(f"スコア: {corrects} / {total} ({corrects/total*100:.1f}%)")
    st.session_state.quiz_started = False
