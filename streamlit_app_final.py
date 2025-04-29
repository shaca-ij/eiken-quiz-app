import streamlit as st
import pandas as pd
import random

# データ読み込み
@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

# セッション状態の初期化
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.page = "start"
    st.session_state.quiz = []
    st.session_state.current_q_idx = 0
    st.session_state.user_answer = None
    st.session_state.show_result = False
    st.session_state.num_questions = 5  # デフォルト出題数
    st.session_state.correct_count = 0

# スタート画面
if st.session_state.page == "start":
    st.title("📝 英単語クイズ")
    st.markdown("クイズの問題数を選んでスタートしましょう！")
    num = st.slider("出題数を選択", 1, 20, st.session_state.num_questions)
    st.session_state.num_questions = num

    if st.button("スタート"):  # データ読み込みとシャッフル
        df = load_data().sample(frac=1).reset_index(drop=True)
        st.session_state.quiz = df.head(num).to_dict(orient="records")
        st.session_state.page = "quiz"
        st.session_state.current_q_idx = 0
        st.session_state.correct_count = 0
        st.session_state.show_result = False
        st.rerun()

# クイズ画面
elif st.session_state.page == "quiz":
    quiz = st.session_state.quiz
    idx = st.session_state.current_q_idx
    current_q = quiz[idx]

    # 進捗バー
    st.progress((idx) / st.session_state.num_questions)

    # 問題番号と問題文
    st.markdown(f"<div style='font-weight: bold; font-size: 20px;'>Q{idx + 1}:</div>", unsafe_allow_html=True)
    question_html = f"""
    <div style='background-color: #f0f0f0; padding: 15px; margin-bottom: 10px; border-radius: 10px; font-size: 18px;'>
        {current_q['sentence_with_blank'].replace(chr(10), '<br>')}
    </div>"""
    st.markdown(question_html, unsafe_allow_html=True)

    # 選択肢の表示
    choices = current_q["choices"].split("|")
    if "shuffled_choices" not in st.session_state:
        st.session_state.shuffled_choices = {}

    if idx not in st.session_state.shuffled_choices:
        st.session_state.shuffled_choices[idx] = random.sample(choices, len(choices))

    shuffled_choices = st.session_state.shuffled_choices[idx]

    st.markdown("<style>label.css-1fcb9m2 {font-size: 20px !important;}</style>", unsafe_allow_html=True)
    st.session_state.user_answer = st.radio(
        "選択肢:", shuffled_choices,
        index=None if st.session_state.user_answer is None else shuffled_choices.index(st.session_state.user_answer),
        key=f"answer_{idx}"
    )

    # 解答ボタン
    if st.button("✅ 解答する"):
        if st.session_state.user_answer:
            correct = current_q["answer"]
            if st.session_state.user_answer == correct:
                st.session_state.correct_count += 1
                st.success("✅ 正解！ 🎉")
            else:
                st.markdown(
                    f"<div style='color:red; font-weight:bold;'>✖ 不正解... 正解は <u>{correct}</u></div>",
                    unsafe_allow_html=True
                )

            st.markdown(f"**意味：** {current_q['meaning_jp']}")
            st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)
            st.session_state.show_result = True

    # 次の問題へ
    if st.session_state.show_result:
        if st.button("次の問題へ"):
            st.session_state.user_answer = None
            st.session_state.show_result = False
            st.session_state.current_q_idx += 1

            if st.session_state.current_q_idx >= st.session_state.num_questions:
                st.session_state.page = "review"
            st.rerun()

# 結果・復習
elif st.session_state.page == "review":
    st.title("✅ 結果と復習")
    total = st.session_state.num_questions
    correct = st.session_state.correct_count
    st.markdown(f"### 正解数: {correct} / {total}")
    st.progress(correct / total)

    st.write("もう一度挑戦しますか？")
    if st.button("最初に戻る"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
