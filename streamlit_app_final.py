import streamlit as st
import pandas as pd
import random

# CSVファイルを読み込み
@st.cache_data
def load_data():
    df = pd.read_csv("words.csv")
    return df

df = load_data()

# セッション状態の初期化
if "quiz_initialized" not in st.session_state:
    # ユーザーが設定した出題数を記憶
    st.session_state.quiz_length = 10
    st.session_state.quiz_initialized = False

if not st.session_state.quiz_initialized:
    st.title("📝 英単語クイズ")
    st.markdown("#### 出題数を選んでください")
    quiz_length = st.slider("問題数", min_value=1, max_value=min(30, len(df)), value=10)
    if st.button("スタート!"):
        st.session_state.quiz = df.sample(frac=1).head(quiz_length).to_dict(orient="records")
        st.session_state.current_q_idx = 0
        st.session_state.user_answer = None
        st.session_state.show_result = False
        st.session_state.in_review_mode = False
        st.session_state.incorrect_questions = []
        st.session_state.quiz_length = quiz_length
        st.session_state.quiz_initialized = True
        st.experimental_rerun()
    st.stop()

quiz = st.session_state.quiz
current_q = quiz[st.session_state.current_q_idx]
choices = current_q["choices"].split("|")

if "choices_shuffled" not in st.session_state:
    st.session_state.choices_shuffled = {}

if st.session_state.current_q_idx not in st.session_state.choices_shuffled:
    st.session_state.choices_shuffled[st.session_state.current_q_idx] = random.sample(choices, len(choices))

shuffled_choices = st.session_state.choices_shuffled[st.session_state.current_q_idx]

# スタイル設定
st.markdown("""
    <style>
    div.question-box {
        background-color: #f0f9ff;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 20px;
        line-height: 1.6;
    }
    div[role="radiogroup"] > label {
        font-size: 18px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 4px 0;
    }
    </style>
""", unsafe_allow_html=True)

# 進捗バー
progress = (st.session_state.current_q_idx + 1) / st.session_state.quiz_length
st.progress(progress, text=f"進捗: {st.session_state.current_q_idx + 1} / {st.session_state.quiz_length}")

# 問題番号と文
st.markdown(f"### Q{st.session_state.current_q_idx + 1}:")
st.markdown(f"<div class='question-box'>{current_q['sentence_with_blank'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

# ラジオボタンで選択肢表示
st.session_state.user_answer = st.radio(
    "選択肢：",
    shuffled_choices,
    index=None if st.session_state.user_answer is None else shuffled_choices.index(st.session_state.user_answer),
    key=f"answer_{st.session_state.current_q_idx}"
)

# 「解答する」ボタン
if st.button("✅ 解答する"):
    if st.session_state.user_answer is not None:
        correct_answer = current_q["answer"]
        is_correct = st.session_state.user_answer == correct_answer
        st.session_state.show_result = True

        if is_correct:
            st.success("正解！ 🎉")
        else:
            st.error(f"❌ 不正解... 正解は **{correct_answer}**")
            st.session_state.incorrect_questions.append(current_q)

        st.markdown(f"**意味：** {current_q['meaning_jp']}")
        st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)
    else:
        st.warning("答えを選んでください。")

# 「次の問題へ」ボタン
if st.session_state.show_result:
    if st.button("次の問題へ"):
        if st.session_state.current_q_idx + 1 < len(quiz):
            st.session_state.current_q_idx += 1
            st.session_state.show_result = False
            st.session_state.user_answer = None
            st.experimental_rerun()
        else:
            st.success("すべての問題が終了しました！")
            if st.session_state.incorrect_questions:
                if st.button("🔁 間違えた問題を復習する"):
                    st.session_state.quiz = st.session_state.incorrect_questions
                    st.session_state.quiz_length = len(st.session_state.incorrect_questions)
                    st.session_state.current_q_idx = 0
                    st.session_state.show_result = False
                    st.session_state.user_answer = None
                    st.session_state.incorrect_questions = []
                    st.session_state.choices_shuffled = {}
                    st.experimental_rerun()
            else:
                st.info("すべて正解でした！ 🎉")
