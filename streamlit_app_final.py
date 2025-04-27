import streamlit as st
import pandas as pd
import random
import gspread
from google.oauth2 import service_account

# --- Google Sheets 設定（履歴保存用） ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account_json"],
    scopes=scope
)
gc = gspread.authorize(credentials)

# あなたのスプレッドシートURLに変更してください
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/【あなたのシートID】"
spreadsheet = gc.open_by_url(SPREADSHEET_URL)
worksheet = spreadsheet.worksheet("履歴")

# --- クイズ問題読み込み ---
df = pd.read_csv("words.csv")

# --- セッション初期化 ---
if "mode" not in st.session_state:
    st.session_state.mode = "normal"
if "quiz" not in st.session_state:
    st.session_state.quiz = []
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "score" not in st.session_state:
    st.session_state.score = 0

st.title("英検準2級 英単語クイズ")

# --- モード選択 ---
mode = st.radio("モード選択", ["通常モード", "復習モード"])

# --- 復習モードは未実装なので注意表示だけ ---
if mode == "復習モード":
    st.warning("復習モードは現在準備中です。まず通常モードで進めてください。")

# --- クイズ開始準備 ---
quiz_base = df
max_questions = len(quiz_base)
if max_questions == 0:
    st.error("出題できる問題がありません。")
    st.stop()

quiz_size = st.slider("出題数を選んでください", 1, max_questions, min(5, max_questions), key="quiz_size_slider")

if st.button("▶ クイズを始める"):
    selected = quiz_base.sample(quiz_size).to_dict(orient="records")
    for q in selected:
        q["shuffled_choices"] = random.sample(q["choices"].split("|"), len(q["choices"].split("|")))
    st.session_state.quiz = selected
    st.session_state.answers = {}
    st.session_state.score = 0

# --- クイズ出題 ---
if st.session_state.quiz:
    st.subheader("問題")
    for idx, q in enumerate(st.session_state.quiz):
        st.write(f"Q{idx+1}: {q['sentence_with_blank']}")
        choice = st.radio("選択肢", q["shuffled_choices"], key=f"choice_{idx}")
        st.session_state.answers[idx] = choice

    if st.button("▶ 答え合わせ"):
        score = 0
        for idx, q in enumerate(st.session_state.quiz):
            user_answer = st.session_state.answers.get(idx, "")
            if user_answer == q["answer"]:
                score += 1
        st.session_state.score = score

        st.success(f"スコア: {score} / {len(st.session_state.quiz)}")

        # --- 履歴保存 ---
        st.subheader("結果を保存")
        username = st.text_input("あなたの名前（記録用）")
        if st.button("📄 履歴を保存"):
            if username:
                for idx, q in enumerate(st.session_state.quiz):
                    user_answer = st.session_state.answers.get(idx, "")
                    is_correct = "〇" if user_answer == q["answer"] else "×"
                    worksheet.append_row([
                        username,
                        q["word"],
                        user_answer,
                        q["answer"],
                        is_correct
                    ])
                st.success("履歴を保存しました！")
            else:
                st.error("名前を入力してください。")
