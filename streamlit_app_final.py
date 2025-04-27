import streamlit as st
import pandas as pd
import random
import gspread
from google.oauth2 import service_account
import json
import streamlit_authenticator as stauth

# ==================== 認証設定 ====================
st.set_page_config(page_title="英検クイズ", page_icon="📝")

# 認証ユーザー情報
usernames = ["student1", "student2", "student3"]
passwords = ["1234", "1234", "1234"]
hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    {"usernames": {u: {"email": f"{u}@example.com", "name": u, "password": p}
    for u, p in zip(usernames, hashed_passwords)}},
    "eiken_quiz_app", "abcdef", cookie_expiry_days=1
)
name, authentication_status, username = authenticator.login("ログイン", "main")

if not authentication_status:
    st.error("ユーザー名またはパスワードが違います")
    st.stop()
if authentication_status is None:
    st.warning("ユーザー名とパスワードを入力してください")
    st.stop()

# ==================== スプレッドシート接続設定 ====================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = json.loads(st.secrets["gcp_service_account_json"])
credentials = {
    "usernames": {
        "student1": {
            "name": "student1",
            "password": stauth.Hasher(["1234"]).generate()[0]
        },
        "student2": {
            "name": "student2",
            "password": stauth.Hasher(["1234"]).generate()[0]
        },
        "student3": {
            "name": "student3",
            "password": stauth.Hasher(["1234"]).generate()[0]
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "eiken_quiz_app",
    "abcdef",
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("ログイン", "main")

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1IfqASoqhNwKFYoJdjkIPIXcO3mCE5j2Ng2PtmlWdj1c/edit#gid=0"
spreadsheet = gc.open_by_url(SPREADSHEET_URL)
worksheet = spreadsheet.worksheet("履歴")

# ==================== データ読み込み ====================
df = pd.read_csv("words.csv")

# ==================== モード選択 ====================
mode = st.radio("モードを選択してください", ("通常モード", "復習モード"))

if mode == "復習モード":
    threshold = st.selectbox("正答率のしきい値を選んでください", (25, 50, 75))
    history = pd.DataFrame(worksheet.get_all_records())
    user_history = history[history["user"] == username]
    if not user_history.empty:
        correct_rate = user_history.groupby("word")["correct"].mean() * 100
        low_accuracy_words = correct_rate[correct_rate < threshold].index.tolist()
        quiz_base = df[df["word"].isin(low_accuracy_words)]
        if quiz_base.empty:
            st.warning("指定条件に該当する復習単語がありません。")
            st.stop()
    else:
        st.warning("履歴が存在しません。通常モードで学習してください。")
        st.stop()
else:
    quiz_base = df

# ==================== 出題 ====================
max_questions = len(quiz_base)
quiz_size = st.slider("出題数を選んでください", 1, max_questions, min(5, max_questions), key="quiz_size_slider")

if "quiz" not in st.session_state:
    st.session_state.quiz = []
    st.session_state.answers = {}
    st.session_state.score = 0
    st.session_state.finished = False

if st.button("▶ クイズを始める"):
    selected = quiz_base.sample(quiz_size).to_dict(orient="records")
    for q in selected:
        q["shuffled_choices"] = random.sample(q["choices"].split("|"), 4)
    st.session_state.quiz = selected
    st.session_state.answers = {}
    st.session_state.score = 0
    st.session_state.finished = False

if st.session_state.quiz and not st.session_state.finished:
    for idx, q in enumerate(st.session_state.quiz):
        st.subheader(f"Q{idx+1}: {q['sentence_with_blank']}")
        st.session_state.answers[idx] = st.radio(
            "選択肢", q["shuffled_choices"], key=f"choice_{idx}"
        )

    if st.button("✅ 解答を提出"):
        score = 0
        for idx, q in enumerate(st.session_state.quiz):
            user_answer = st.session_state.answers.get(idx)
            correct = user_answer == q["answer"]
            if correct:
                score += 1
            worksheet.append_row([username, q["word"], int(correct)])
        st.session_state.score = score
        st.session_state.finished = True

if st.session_state.finished:
    st.success(f"スコア: {st.session_state.score}/{len(st.session_state.quiz)}")
