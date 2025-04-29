import streamlit as st
import pandas as pd
import random

# --- 初期設定 ---
st.set_page_config(page_title="英検準2級クイズ", layout="centered")

# --- セッション状態の初期化 ---
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "num_questions" not in st.session_state:
    st.session_state.num_questions = 5
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "answers" not in st.session_state:
    st.session_state.answers = []

# --- データ読み込み関数 ---
def load_quiz_data():
    df = pd.read_csv("quiz_data.csv")
    quiz_list = df.to_dict(orient="records")
    random.shuffle(quiz_list)
    return quiz_list

# --- クイズデータ初期化 ---
def initialize_quiz():
    st.session_state.quiz = load_quiz_data()[:st.session_state.num_questions]
    st.session_state.current_q_idx = 0
    st.session_state.score = 0
    st.session_state.show_result = False
    st.session_state.answers = []

# --- スタート画面 ---
if st.session_state.quiz is None:
    st.title("英検準2級 英単語クイズ")
    st.session_state.num_questions = st.slider("出題数を選んでください", min_value=1, max_value=20, value=5)
    if st.button("スタート"):
        initialize_quiz()
        st.experimental_rerun()
    st.stop()

# --- クイズ中 ---
quiz = st.session_state.quiz
current_q = quiz[st.session_state.current_q_idx]

# --- 進捗バー（画面上部） ---
st.markdown(f"### {st.session_state.current_q_idx + 1} / {st.session_state.num_questions} 問")
progress = (st.session_state.current_q_idx + 1) / st.session_state.num_questions
st.progress(progress)

# --- 問題文 ---
st.markdown("""
<div style="background-color:#f0f8ff; padding: 15px; border-radius: 10px;">
  <span style="font-weight: bold; font-size: 20px; color: black;">Q{}</span><br>
  <span style="font-size: 22px; color: black;">{}</span>
</div>
""".format(
    st.session_state.current_q_idx + 1,
    current_q['sentence_with_blank'].replace("\n", "<br>")
), unsafe_allow_html=True)

# --- 和訳 ---
st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)

# --- 選択肢の表示 ---
col1, col2 = st.columns(2)
choices = current_q['choices'].split("|")
selected = None
with col1:
    for i in range(0, len(choices), 2):
        if st.button(choices[i], key=f"btn_{i}"):
            selected = choices[i]
with col2:
    for i in range(1, len(choices), 2):
        if st.button(choices[i], key=f"btn_{i}"):
            selected = choices[i]

# --- 回答処理 ---
if selected and not st.session_state.show_result:
    correct = current_q['correct']
    is_correct = (selected.strip() == correct.strip())
    if is_correct:
        st.session_state.score += 1
        st.success(f"✅ 正解！")
    else:
        st.error(f"<span style='color:red; font-weight:bold;'>✖ 不正解... 正解は <u>{correct}</u></span>", unsafe_allow_html=True)
    st.session_state.answers.append({
        "question": current_q['sentence_with_blank'],
        "selected": selected,
        "correct": correct,
        "is_correct": is_correct
    })
    st.session_state.show_result = True

# --- 次の問題へ ---
if st.session_state.show_result:
    if st.session_state.current_q_idx + 1 < st.session_state.num_questions:
        if st.button("次の問題へ"):
            st.session_state.current_q_idx += 1
            st.session_state.show_result = False
            st.experimental_rerun()
    else:
        st.markdown("## 結果発表")
        st.write(f"スコア: {st.session_state.score} / {st.session_state.num_questions}")
        if st.button("もう一度挑戦"):
            initialize_quiz()
            st.experimental_rerun()
