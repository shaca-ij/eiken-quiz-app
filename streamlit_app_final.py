import streamlit as st
import pandas as pd
import random

# CSVファイルを読み込む関数
def load_data():
    df = pd.read_csv("words.csv")
    return df

# セッションステートの初期化
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
if "choices_shuffled" not in st.session_state:
    st.session_state.choices_shuffled = {}

st.title("📝 英単語クイズ")

# スタート画面
if not st.session_state.quiz_started:
    if st.button("スタート"):
        df = load_data()
        st.session_state.quiz = df.sample(frac=1).to_dict(orient="records")
        st.session_state.quiz_started = True
        st.session_state.current_q_idx = 0
        st.session_state.user_answer = None
        st.session_state.show_result = False
        st.session_state.choices_shuffled = {}
        st.experimental_rerun()
else:
    # 現在の問題
    current_q = st.session_state.quiz[st.session_state.current_q_idx]
    choices = current_q["choices"].split("|")

    if st.session_state.current_q_idx not in st.session_state.choices_shuffled:
        st.session_state.choices_shuffled[st.session_state.current_q_idx] = random.sample(choices, len(choices))

    shuffled_choices = st.session_state.choices_shuffled[st.session_state.current_q_idx]

    # 問題文の表示
    st.markdown(f"<div style='background-color: #f0f8ff; padding: 10px; border-radius: 10px; font-size: 20px;'>"
                f"<strong>Q{st.session_state.current_q_idx + 1}:</strong><br>"
                f"{current_q['sentence_with_blank'].replace('\n', '<br>')}"
                f"</div>", unsafe_allow_html=True)

    # 選択肢の表示
    st.session_state.user_answer = st.radio(
        "選択肢：",
        shuffled_choices,
        index=None if st.session_state.user_answer is None else shuffled_choices.index(st.session_state.user_answer),
        key=f"answer_{st.session_state.current_q_idx}"
    )

    # 解答ボタン
    if st.button("✅ 解答する"):
        if st.session_state.user_answer is not None:
            correct = current_q["answer"]
            is_correct = (st.session_state.user_answer == correct)
            st.session_state.show_result = True

            if is_correct:
                st.success("正解！ 🎉")
            else:
                st.error(f"✖ 不正解... 正解は **{correct}**")

            st.markdown(f"**意味：** {current_q['meaning_jp']}")
            st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)
        else:
            st.warning("答えを選んでください。")

    # 次の問題へ
    if st.session_state.show_result:
        if st.button("次の問題へ"):
            st.session_state.current_q_idx += 1
            st.session_state.user_answer = None
            st.session_state.show_result = False

            if st.session_state.current_q_idx >= len(st.session_state.quiz):
                st.success("全ての問題が終了しました！")
                st.session_state.quiz_started = False
            else:
                st.experimental_rerun()

    # 進捗バー
    progress = (st.session_state.current_q_idx + 1) / len(st.session_state.quiz)
    st.progress(progress)
