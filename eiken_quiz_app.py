import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="英検準2級クイズ", layout="centered")

@st.cache_data
def load_data():
    df = pd.read_csv("word.csv")
    return df

if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'mode' not in st.session_state:
    st.session_state.mode = 'quiz'

def go_to(page):
    st.session_state.page = page

def home_page():
    st.title("英検準2級 英単語クイズ")
    st.markdown("英検準2級レベルの単語を使ったクイズに挑戦しましょう！")
    st.markdown("出題数は10問です。")

    if st.button("スタート"):
        df = load_data()
        st.session_state.questions = df.sample(10).to_dict(orient='records')
        st.session_state.current_q_index = 0
        st.session_state.answers = []
        st.session_state.mode = 'quiz'
        go_to('quiz')

    if st.button("復習モード"):
        df = load_data()
        wrong = df[df['correct_rate'] < 0.6]
        if len(wrong) < 10:
            st.warning("復習対象の問題が10問未満のため、通常モードで開始します。")
            st.session_state.questions = df.sample(10).to_dict(orient='records')
        else:
            st.session_state.questions = wrong.sample(10).to_dict(orient='records')
        st.session_state.current_q_index = 0
        st.session_state.answers = []
        st.session_state.mode = 'review'
        go_to('quiz')

def quiz_page():
    idx = st.session_state.current_q_index
    current_q = st.session_state.questions[idx]

    st.markdown(f"<b>Q{idx + 1}:</b><br>{current_q['sentence_with_blank'].replace(chr(10), '<br>').replace('(', '').replace(')', '').replace('________', '<u>________</u>')}",
                unsafe_allow_html=True)

    choices = current_q['choices'].split('|')
    selected = st.radio("選択肢", choices, key=f"q_{idx}")

    if st.button("次の問題へ"):
        st.session_state.answers.append({
            'question': current_q['sentence_with_blank'],
            'selected': selected,
            'correct': current_q['answer'],
            'explanation': current_q.get('sentence_jp', '')
        })
        st.session_state.current_q_index += 1
        if st.session_state.current_q_index >= len(st.session_state.questions):
            go_to('result')

def result_page():
    correct = sum(1 for a in st.session_state.answers if a['selected'] == a['correct'])
    total = len(st.session_state.answers)
    st.markdown(f"## 結果: {correct} / {total} 正解")
    st.progress(correct / total)

    for idx, a in enumerate(st.session_state.answers):
        correct_color = "#e0ffe0" if a['selected'] == a['correct'] else "#ffe0e0"
        html = f"""
<div style="background-color:{correct_color};padding:10px;border-radius:8px;margin:10px 0;">
<b>Q{idx + 1}:</b> {a['question'].replace('________', f"<u>{a['correct']}</u>")}<br>
<b>あなたの答え:</b> {a['selected']}<br>
<b>正解:</b> {a['correct']}<br>
<i>{a['explanation']}</i>
</div>
"""
        st.markdown(html, unsafe_allow_html=True)

    if st.button("ホームに戻る"):
        go_to('home')

# ページルーティング
if st.session_state.page == 'home':
    home_page()
elif st.session_state.page == 'quiz':
    quiz_page()
elif st.session_state.page == 'result':
    result_page()
