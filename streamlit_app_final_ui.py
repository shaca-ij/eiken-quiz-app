import streamlit as st
import pandas as pd
import random

# ページ設定
st.set_page_config(
    page_title="英単語クイズ",
    page_icon="📝",
    layout="wide",
)

# カスタムCSSで全体デザイン
st.markdown(
    """
    <style>
    body {
        background-color: #f7f9fc;
    }
    .question-card {
        background-color: #ffffff;
        padding: 20px;
        margin: 20px 0;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .choice-button {
        display: block;
        width: 100%;
        padding: 10px 20px;
        margin-bottom: 10px;
        background-color: #eef2f7;
        border: none;
        border-radius: 10px;
        font-size: 18px;
        text-align: center;
        transition: background-color 0.3s;
    }
    .choice-button:hover {
        background-color: #d0e0f0;
    }
    .correct {
        background-color: #c8f7c5 !important;
    }
    .wrong {
        background-color: #f8c6c8 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 問題データ読み込み
@st.cache_data
def load_questions():
    df = pd.read_csv("words.csv")
    return df

questions_df = load_questions()

# セッション状態を初期化
if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answered" not in st.session_state:
    st.session_state.answered = False
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = ""

# 問題をランダムにシャッフルして選ぶ
quiz_questions = questions_df.sample(frac=1).reset_index(drop=True)

# 現在の問題
current_q = quiz_questions.iloc[st.session_state.current_q_idx]
question_text = current_q["sentence_with_blank"]
choices = current_q["choices"].split("|")
correct_answer = current_q["answer"]
meaning_jp = current_q["meaning_jp"]
sentence_jp = current_q["sentence_jp"]

# カード形式で表示
st.markdown(f"""
<div class="question-card">
    <h3>問題 {st.session_state.current_q_idx + 1}</h3>
    <p style="font-size:20px;">{question_text}</p>
</div>
""", unsafe_allow_html=True)

# 選択肢をボタンで表示
selected = None
for choice in choices:
    if st.button(choice, key=choice, use_container_width=True):
        st.session_state.selected_answer = choice
        st.session_state.answered = True

# 回答判定
if st.session_state.answered:
    if st.session_state.selected_answer == correct_answer:
        st.session_state.score += 1
        st.success(f"✅ 正解！ {correct_answer}")
    else:
        st.error(f"❌ 不正解！ 正解は {correct_answer}")

    st.info(f"【意味】{meaning_jp}")
    st.info(f"【和訳】{sentence_jp}")

    if st.button("▶ 次の問題へ", key="next_button"):
        st.session_state.current_q_idx += 1
        st.session_state.answered = False
        st.session_state.selected_answer = ""

# 全問終わったら結果表示
if st.session_state.current_q_idx >= len(quiz_questions):
    st.balloons()
    st.success(f"🎉 全問終了！スコア：{st.session_state.score} / {len(quiz_questions)}")
    if st.button("🔄 もう一度挑戦", key="retry_button"):
        st.session_state.current_q_idx = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.selected_answer = ""
