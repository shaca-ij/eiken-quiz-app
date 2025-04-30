import streamlit as st
import pandas as pd
import random

# CSVファイル読み込み関数
def load_quiz_data():
    df = pd.read_csv("words.csv")
    quiz_data = []
    for _, row in df.iterrows():
        choices = row["choices"].split("|")
        random.shuffle(choices)
        quiz_data.append({
            "word": row["word"],
            "answer": row["answer"],
            "choices": choices,
            "sentence_with_blank": row["sentence_with_blank"],
            "meaning_jp": row["meaning_jp"],
            "sentence_jp": row["sentence_jp"]
        })
    return quiz_data

# クイズ状態初期化関数
def initialize_quiz(num_questions):
    full_quiz = load_quiz_data()
    random.shuffle(full_quiz)
    st.session_state.quiz = full_quiz[:num_questions]
    st.session_state.current_q_idx = 0
    st.session_state.score = 0
    st.session_state.show_answer = False
    st.session_state.selected = None
    st.session_state.page = "quiz"

# 進捗バー表示
def show_progress():
    progress = (st.session_state.current_q_idx) / len(st.session_state.quiz)
    st.progress(progress, text=f"{st.session_state.current_q_idx} / {len(st.session_state.quiz)}")

# クイズ1問の表示
def show_question():
    q = st.session_state.quiz[st.session_state.current_q_idx]

    show_progress()

    st.markdown(f"### Q{st.session_state.current_q_idx + 1}:")
    st.markdown(
        f"""
        <div style='background-color:#f0f2f6; padding: 12px; border-radius: 10px;'>
            {q['sentence_with_blank']}
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 5])
    for choice in q["choices"]:
        c1, c2 = st.columns([1, 5])
        with c1:
            if st.session_state.show_answer is False:
                if st.button("選ぶ", key=choice):
                    st.session_state.selected = choice
                    st.session_state.show_answer = True
                    if choice == q["answer"]:
                        st.session_state.score += 1
        with c2:
            st.markdown(f"**{choice}**")

    if st.session_state.show_answer:
        if st.session_state.selected == q["answer"]:
            st.success("〇 正解！")
        else:
            st.error(
                f"<span style='color:red; font-weight:bold;'>✖ 不正解... 正解は <u>{q['answer']}</u></span>",
                unsafe_allow_html=True
            )
        st.markdown(f"**意味：** {q['meaning_jp']}")
        st.markdown(f"**和訳：** {q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)

        if st.button("次の問題へ"):
            st.session_state.current_q_idx += 1
            st.session_state.show_answer = False
            st.session_state.selected = None

    # クイズ終了判定
    if st.session_state.current_q_idx >= len(st.session_state.quiz):
        st.session_state.page = "result"

# 結果画面
def show_result():
    score = st.session_state.score
    total = len(st.session_state.quiz)
    st.markdown(f"# 結果: {score} / {total} 正解")
    if st.button("もう一度挑戦"):
        st.session_state.page = "start"

# アプリ本体
st.set_page_config(page_title="英単語クイズ", layout="centered")
st.title("英検準2級 英単語クイズ")

if "page" not in st.session_state:
    st.session_state.page = "start"

if st.session_state.page == "start":
    num = st.slider("出題数を選んでください", min_value=1, max_value=30, value=10)
    if st.button("スタート"):
        initialize_quiz(num)

elif st.session_state.page == "quiz":
    show_question()

elif st.session_state.page == "result":
    show_result()
