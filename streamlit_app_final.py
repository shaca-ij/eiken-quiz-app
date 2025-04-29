import streamlit as st
import pandas as pd
import random

# データ読み込み
@st.cache_data
def load_data():
    df = pd.read_csv("words.csv")
    return df

df = load_data()

# 出題数選択（初回のみ）
if "quiz_started" not in st.session_state:
    st.title("📝 英単語クイズ")
    num_questions = st.slider("出題数を選んでください", 1, min(20, len(df)), 10)
    if st.button("クイズスタート"):
        st.session_state.quiz_started = True
        st.session_state.num_questions = num_questions
        st.session_state.quiz = df.sample(n=num_questions).to_dict(orient="records")
        st.session_state.current_q_idx = 0
        st.session_state.user_answer = None
        st.session_state.show_result = False
        st.session_state.in_review_mode = False
        st.session_state.incorrect_questions = []
        st.rerun()
    st.stop()

st.title("📝 英単語クイズ")

quiz = st.session_state.quiz
current_idx = st.session_state.current_q_idx
current_q = quiz[current_idx]

# 選択肢シャッフル
if "choices_shuffled" not in st.session_state:
    st.session_state.choices_shuffled = {}

if current_idx not in st.session_state.choices_shuffled:
    choices = current_q["choices"].split("|")
    st.session_state.choices_shuffled[current_idx] = random.sample(choices, len(choices))

shuffled_choices = st.session_state.choices_shuffled[current_idx]

# 進捗バー
progress = (current_idx + 1) / len(quiz)
st.progress(progress, text=f"進捗: {current_idx + 1} / {len(quiz)}")

# 問題表示（装飾付き）
st.markdown(f"""
<div style='background-color:#f0f8ff;padding:15px;border-radius:10px;margin-bottom:10px'>
    <strong>Q{current_idx + 1}:</strong><br>
    {current_q['sentence_with_blank'].replace("\\n", "<br>")}
</div>
""", unsafe_allow_html=True)

# 選択肢表示（大きく、整列）
st.markdown("<style>.choice-btn label span {font-size: 20px;}</style>", unsafe_allow_html=True)
user_choice = st.radio(
    "選択肢：",
    shuffled_choices,
    index=None if st.session_state.user_answer is None else shuffled_choices.index(st.session_state.user_answer),
    key=f"answer_{current_idx}",
    label_visibility="collapsed",
    format_func=lambda x: f"　{x}　",
)

st.session_state.user_answer = user_choice

# 解答ボタン
if st.button("✅ 解答する"):
    if st.session_state.user_answer is not None:
        correct = current_q["answer"]
        is_correct = st.session_state.user_answer == correct
        st.session_state.show_result = True

        if is_correct:
            st.success("✅ 正解！ 🎉")
        else:
            st.session_state.incorrect_questions.append(current_q)
            st.error(f"✖ 不正解... 正解は **{correct}**")

        st.markdown(f"**意味：** {current_q['meaning_jp']}")
        st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)
    else:
        st.warning("答えを選んでください。")

# 次の問題へ
if st.session_state.show_result:
    if st.button("次の問題へ"):
        st.session_state.user_answer = None
        st.session_state.show_result = False
        st.session_state.current_q_idx += 1

        if st.session_state.current_q_idx >= len(quiz):
            st.session_state.quiz_started = False
            if not st.session_state.in_review_mode and st.session_state.incorrect_questions:
                st.session_state.in_review_mode = True
                st.session_state.quiz = st.session_state.incorrect_questions
                st.session_state.current_q_idx = 0
                st.session_state.choices_shuffled = {}
                st.info("📘 間違えた問題だけ復習モードに入りました")
            else:
                st.success("✅ すべての問題が終了しました！")
                st.stop()
