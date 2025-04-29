import streamlit as st
import pandas as pd
import random

# CSV読み込み
@st.cache_data
def load_data():
    df = pd.read_csv("words.csv")
    return df

df = load_data()

# セッション状態の初期化
if "started" not in st.session_state:
    st.session_state.started = False
if "quiz" not in st.session_state:
    st.session_state.quiz = []
if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "user_answer" not in st.session_state:
    st.session_state.user_answer = None
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "review_list" not in st.session_state:
    st.session_state.review_list = []
if "total_questions" not in st.session_state:
    st.session_state.total_questions = 5  # デフォルト問題数

st.title("📝 英検準2級 英単語クイズ")

# スタート前画面
if not st.session_state.started:
    st.slider("出題数を選んでください（最大50問）", 1, min(50, len(df)), key="total_questions")
    if st.button("スタート"):
        st.session_state.quiz = df.sample(frac=1).head(st.session_state.total_questions).to_dict(orient="records")
        st.session_state.started = True
        st.session_state.current_q_idx = 0
        st.session_state.user_answer = None
        st.session_state.show_result = False
        st.session_state.review_list = []
    st.stop()

# クイズ進行画面
current_idx = st.session_state.current_q_idx
quiz = st.session_state.quiz
current_q = quiz[current_idx]
choices = current_q["choices"].split("|")

if "choices_shuffled" not in st.session_state:
    st.session_state.choices_shuffled = {}

if current_idx not in st.session_state.choices_shuffled:
    st.session_state.choices_shuffled[current_idx] = random.sample(choices, len(choices))

shuffled_choices = st.session_state.choices_shuffled[current_idx]

# 進捗バー
st.progress((current_idx + 1) / st.session_state.total_questions)

# 問題文表示（背景色付き）
st.markdown(f"""
<div style="background-color: #f0f8ff; padding: 10px; border-radius: 8px;">
    <strong>Q{current_idx + 1}:</strong><br>
    {current_q['sentence_with_blank'].replace("\\n", "<br>")}
</div>
""", unsafe_allow_html=True)

# 選択肢表示（フォント大きめ、横並び防止）
selected = st.radio(
    "選択肢：",
    shuffled_choices,
    index=None if st.session_state.user_answer is None else shuffled_choices.index(st.session_state.user_answer),
    key=f"answer_{current_idx}"
)

st.session_state.user_answer = selected

# 解答ボタン
if not st.session_state.show_result:
    if st.button("✅ 解答する"):
        if selected is not None:
            correct = current_q["answer"]
            st.session_state.show_result = True

            if selected == correct:
                st.success("✅ 正解！")
            else:
                st.session_state.review_list.append(current_q)
                st.error(f"<span style='color:red; font-weight:bold;'>✖ 不正解... 正解は <u>{correct}</u></span>", unsafe_allow_html=True)

            st.markdown(f"**意味：** {current_q['meaning_jp']}")
            st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)

# 次の問題ボタン
if st.session_state.show_result:
    if st.button("次の問題へ"):
        if current_idx + 1 < st.session_state.total_questions:
            st.session_state.current_q_idx += 1
            st.session_state.user_answer = None
            st.session_state.show_result = False
        else:
            st.success("すべての問題が終了しました！")

            # 復習モードの開始案内
            if len(st.session_state.review_list) > 0:
                st.markdown("---")
                st.subheader("🔁 復習モード")
                st.write(f"{len(st.session_state.review_list)} 問の復習があります。")
                if st.button("復習スタート"):
                    st.session_state.quiz = st.session_state.review_list
                    st.session_state.total_questions = len(st.session_state.review_list)
                    st.session_state.current_q_idx = 0
                    st.session_state.user_answer = None
                    st.session_state.show_result = False
                    st.session_state.review_list = []
