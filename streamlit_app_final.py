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

# 問題文の表示
problem_text = f"Q{st.session_state.current_q_idx + 1}: {current_q['sentence_with_blank']}"

# 長い文章を改行したい場合は、適切な場所で <br> を追加
problem_text = problem_text.replace("、", "、<br>")  # 例: 句読点の後で改行

# HTMLタグを使用して問題文のフォントサイズを調整
problem_text = f"<div style='font-size: 22px'>{problem_text}</div>"

# Markdownとして1回だけ表示
st.markdown(problem_text, unsafe_allow_html=True)


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
            st.error(f"不正解... 正解は **{correct_answer}**")

        st.markdown(f"**意味：** {current_q['meaning_jp']}")
        st.markdown(f"**和訳：** {current_q['sentence_jp']}")
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
