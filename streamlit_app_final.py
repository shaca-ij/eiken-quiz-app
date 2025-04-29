import streamlit as st
import pandas as pd
import random

# CSV読み込みと整形
@st.cache_data
def load_data():
    df = pd.read_csv("words.csv")

    # 改行コードと選択肢整形
    df["sentence_with_blank"] = df["sentence_with_blank"].astype(str).str.replace("\\n", "\n")
    df["sentence_jp"] = df["sentence_jp"].astype(str).str.replace("\\n", "\n")
    df["choices"] = df["choices"].apply(lambda x: "|".join([c.strip() for c in str(x).split("|")]))
    return df

df = load_data()

# 初期化
if "quiz" not in st.session_state:
    st.session_state.quiz = df.sample(frac=1).to_dict(orient="records")
    st.session_state.current_q_idx = 0
    st.session_state.user_answer = None
    st.session_state.show_result = False

st.title("📝 英単語クイズ")

# カスタムCSS：選択肢の文字サイズ、問題ボックスのスタイル
st.markdown("""
    <style>
    div[role="radiogroup"] > label {
        font-size: 20px !important;
        padding: 8px 0;
    }
    .question-box {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
        font-size: 20px;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

# 進捗バー表示
progress = (st.session_state.current_q_idx + 1) / len(st.session_state.quiz)
st.progress(progress, text=f"{st.session_state.current_q_idx + 1} / {len(st.session_state.quiz)} 問")

# 現在の問題
current_q = st.session_state.quiz[st.session_state.current_q_idx]
choices = current_q["choices"].split("|")

# 選択肢シャッフル
if "choices_shuffled" not in st.session_state:
    st.session_state.choices_shuffled = {}

if st.session_state.current_q_idx not in st.session_state.choices_shuffled:
    st.session_state.choices_shuffled[st.session_state.current_q_idx] = random.sample(choices, len(choices))

shuffled_choices = st.session_state.choices_shuffled[st.session_state.current_q_idx]

# 問題表示
question_number = f"Q{st.session_state.current_q_idx + 1}:"
question_text = current_q["sentence_with_blank"].replace("\n", "<br>")

st.markdown(f"<p style='font-size: 26px; font-weight: bold; color: #2c3e50;'>{question_number}</p>", unsafe_allow_html=True)
st.markdown(f"<div class='question-box'>{question_text}</div>", unsafe_allow_html=True)

# 選択肢の表示（縦並び＆大きめフォント）
st.session_state.user_answer = st.radio(
    "選択肢：",
    shuffled_choices,
    index=None if st.session_state.user_answer is None else shuffled_choices.index(st.session_state.user_answer),
    key=f"answer_{st.session_state.current_q_idx}",
    horizontal=False
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

        # 意味と和訳の表示（改行処理含む）
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
