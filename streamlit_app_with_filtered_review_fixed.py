
import streamlit as st
import pandas as pd
import random
from google.oauth2.service_account import Credentials
import gspread

# --- Google Sheets 認証設定 ---
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
gc = gspread.authorize(credentials)
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1IfqASoqhNwKFYoJdjkIPIXcO3mCE5j2Ng2PtmlWdj1c/edit#gid=0"
worksheet = gc.worksheet("履歴")

# --- データ読込 ---
df = pd.read_csv("words.csv")

# --- モード選択 ---
st.title("英検単語クイズ")
mode = st.radio("モードを選んでください", ("通常モード", "復習モード"))

# --- 過去の間違いデータ読込 ---
if "mistakes" not in st.session_state:
    st.session_state.mistakes = []

# --- 復習モード用データ準備 ---
if mode == "復習モード":
    if not st.session_state.mistakes:
        st.warning("復習対象の間違いデータがありません。通常モードを試してください。")
        st.stop()
    else:
        quiz_base = pd.DataFrame(st.session_state.mistakes)
else:
    quiz_base = df.copy()

# --- 出題数選択 ---
max_questions = len(quiz_base)
if max_questions == 0:
    st.error("出題できる問題がありません。")
    st.stop()

quiz_size = st.slider("出題数を選んでください", 1, max_questions, min(5, max_questions), key="quiz_size_slider")

# --- クイズ開始ボタン ---
if st.button("▶ クイズを始める", key="start_quiz"):
    selected = quiz_base.sample(quiz_size).to_dict(orient="records")
    for q in selected:
        q["shuffled_choices"] = random.sample(q["choices"].split("|"), 4)
    st.session_state.quiz = selected
    st.session_state.answers = {}
    st.session_state.score = 0
    st.session_state.quiz_mode = mode

# --- クイズ実施画面 ---
if "quiz" in st.session_state:
    with st.form("quiz_form"):
        for idx, q in enumerate(st.session_state.quiz):
            st.subheader(f"Q{idx+1}: {q['sentence_with_blank']}")
            choice = st.radio("選択肢", q["shuffled_choices"], key=f"q{idx}")
            st.session_state.answers[idx] = choice
        submitted = st.form_submit_button("解答する")

    if submitted:
        score = 0
        mistakes = []
        for idx, q in enumerate(st.session_state.quiz):
            user_answer = st.session_state.answers.get(idx)
            correct_answer = q["answer"]
            if user_answer == correct_answer:
                score += 1
            else:
                mistakes.append(q)
            # --- スプレッドシートに結果保存 ---
            worksheet.append_row([
                st.session_state.get("user", "unknown_user"),
                q["word"],
                user_answer,
                correct_answer,
                "〇" if user_answer == correct_answer else "✕"
            ])

        st.success(f"スコア: {score}/{len(st.session_state.quiz)}")

        # 間違えた問題だけ保存
        if st.session_state.quiz_mode == "通常モード":
            st.session_state.mistakes = mistakes
        elif st.session_state.quiz_mode == "復習モード":
            st.session_state.mistakes = mistakes  # 復習モードでもさらに間違えたものだけ残す

        # --- 復習モードへボタン ---
        if mistakes:
            if st.button("🔁 復習モードに進む"):
                st.experimental_rerun()
        else:
            st.info("すべて正解しました！復習モードはありません。")
