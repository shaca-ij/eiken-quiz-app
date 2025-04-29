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
if "quiz" not in st.session_state:
    st.session_state.quiz = df.sample(frac=1).to_dict(orient="records")
    st.session_state.current_q_idx = 0
    st.session_state.user_answer = None
    st.session_state.show_result = False
    st.session_state.incorrect_answers = []

# 進捗バーの表示
total_questions = len(st.session_state.quiz)
progress = (st.session_state.current_q_idx + 1) / total_questions
st.progress(progress)

st.title("📝 英単語クイズ")

# 現在の問題を取得
current_q = st.session_state.quiz[st.session_state.current_q_idx]
choices = current_q["choices"].split("|")

# 選択肢のシャッフル（初回のみ）
if "choices_shuffled" not in st.session_state:
    st.session_state.choices_shuffled = {}

if st.session_state.current_q_idx not in st.session_state.choices_shuffled:
    st.session_state.choices_shuffled[st.session_state.current_q_idx] = random.sample(choices, len(choices))

shuffled_choices = st.session_state.choices_shuffled[st.session_state.current_q_idx]

# 問題番号の表示
st.markdown(f"<div style='font-size: 22px; font-weight: bold;'>Q{st.session_state.current_q_idx + 1}:</div>", unsafe_allow_html=True)

# 問題文の表示（改行処理付き）
sentence = str(current_q["sentence_with_blank"]).replace("\\n", "<br>").replace("\n", "<br>")
st.markdown(f"<div style='font-size: 20px; padding-bottom: 10px;'>{sentence}</div>", unsafe_allow_html=True)

# ラジオボタンで選択肢表示（大きめのフォントと背景色）
choice = st.radio(
    "選択肢：",
    shuffled_choices,
    index=None if st.session_state.user_answer is None else shuffled_choices.index(st.session_state.user_answer),
    key=f"answer_{st.session_state.current_q_idx}",
    label_visibility="collapsed"
)

st.session_state.user_answer = choice

# 「解答する」ボタン
if st.button("✅ 解答する"):
    if st.session_state.user_answer is not None:
        correct_answer = current_q["answer"]
        is_correct = st.session_state.user_answer == correct_answer
        st.session_state.show_result = True

        if is_correct:
            st.markdown(
                "<div style='color: green; font-weight: bold; font-size: 22px;'>✅ 正解！ よくできました 🎉</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='color: red; font-weight: bold; font-size: 22px;'>✖ 不正解... 正解は <span style='color: black;'>{correct_answer}</span></div>",
                unsafe_allow_html=True
            )
            st.session_state.incorrect_answers.append(current_q)

        st.markdown(f"**意味：** {current_q['meaning_jp']}")
        sentence_jp = str(current_q.get('sentence_jp', '')).replace("\n", "<br>")
        st.markdown(f"**和訳：** {sentence_jp}", unsafe_allow_html=True)
    else:
        st.warning("答えを選んでください。")

# 「次の問題へ」ボタン
if st.session_state.show_result:
    if st.button("次の問題へ"):
        if st.session_state.current_q_idx + 1 < len(st.session_state.quiz):
            st.session_state.current_q_idx += 1
            st.session_state.show_result = False
            st.session_state.user_answer = None
            st.rerun()
        else:
            st.success("すべての問題が終了しました！")

# 復習モード：不正解だけ再出題
if st.button("🔁 間違えた問題を復習"):
    if st.session_state.incorrect_answers:
        st.session_state.quiz = st.session_state.incorrect_answers
        st.session_state.current_q_idx = 0
        st.session_state.incorrect_answers = []
        st.session_state.user_answer = None
        st.session_state.show_result = False
        st.session_state.choices_shuffled = {}
        st.experimental_rerun()
    else:
        st.warning("間違えた問題がありません！")

# CSSスタイル調整
st.markdown("""
    <style>
    div[role="radiogroup"] > label {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        font-size: 18px;
        font-weight: 500;
        display: block;
    }
    </style>
""", unsafe_allow_html=True)
