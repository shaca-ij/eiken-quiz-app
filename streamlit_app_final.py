import streamlit as st
import pandas as pd
import random

# ---------- データ読み込み ----------
@st.cache_data
def load_data():
    df = pd.read_csv("words.csv")
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    return df

data = load_data()

# ---------- Quiz クラス定義 ----------
class Quiz:
    def __init__(self, df, num_questions):
        self.questions = df.sample(n=min(num_questions, len(df)), random_state=42).to_dict(orient="records")
        self.total = len(self.questions)
        self.current = 0
        self.correct_count = 0
        self.user_answers = []

    def get_current_question(self):
        return self.questions[self.current]

    def check_answer(self, user_answer):
        correct = self.questions[self.current]["answer"].strip()
        is_correct = (user_answer.strip() == correct)
        self.user_answers.append({
            "question": self.questions[self.current],
            "user_answer": user_answer,
            "is_correct": is_correct
        })
        if is_correct:
            self.correct_count += 1
        return is_correct, correct

    def next(self):
        self.current += 1
        return self.current < self.total

# ---------- セッション状態の初期化 ----------
if "started" not in st.session_state:
    st.session_state.started = False
if "quiz" not in st.session_state:
    st.session_state.quiz = None

# ---------- スタート画面 ----------
if not st.session_state.started:
    st.title("英単語クイズアプリ")
    num_questions = st.slider("出題する問題数を選んでください", 1, 30, 10)
    if st.button("スタート"):
        st.session_state.quiz = Quiz(data, num_questions)
        st.session_state.started = True
        st.rerun()
    st.stop()

# ---------- クイズ進行 ----------
quiz = st.session_state.quiz
current_q = quiz.get_current_question()
choices = [c.strip() for c in current_q["choices"].split("|")]

st.markdown(f"### Q{quiz.current + 1}:")
st.markdown(f"""
<div style='background-color: #f0f8ff; padding: 15px; border-radius: 8px; font-size: 20px;'>
{current_q['sentence_with_blank'].replace('\n', '<br>')}
</div>
""", unsafe_allow_html=True)

# ---------- 選択肢表示 ----------
selected = st.radio("選択肢", choices, key=quiz.current, format_func=lambda x: f"  {x}  ")

# ---------- 解答ボタン ----------
if "answered" not in st.session_state:
    st.session_state.answered = False

if not st.session_state.answered:
    if st.button("解答する"):
        is_correct, correct = quiz.check_answer(selected)
        if is_correct:
            st.success("✔ 正解！")
        else:
            st.markdown(
                f"<div style='color:red; font-weight:bold;'>✖ 不正解... 正解は <u>{correct}</u></div>",
                unsafe_allow_html=True
            )
        st.markdown(f"**意味：** {current_q['meaning_jp']}")
        st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)
        st.session_state.answered = True
        st.stop()

# ---------- 次の問題へ ----------
else:
    if st.button("次の問題へ"):
        st.session_state.answered = False
        if quiz.next():
            st.rerun()
        else:
            st.session_state.started = False
            st.success(f"全{quiz.total}問中 {quiz.correct_count}問 正解しました！")
            st.balloons()
            st.stop()

# ---------- 進捗バー ----------
progress = (quiz.current + 1) / quiz.total
st.progress(progress, text=f"{quiz.current + 1} / {quiz.total} 問")
