import streamlit as st
import pandas as pd
import random
import gspread
from google.oauth2 import service_account
import json
import streamlit_authenticator as stauth

# 認証設定
st.set_page_config(page_title="英検クイズ", page_icon="📝")


# 事前にハッシュ化されたパスワードを手動で用意する
# （このハッシュはパスワード「1234」をハッシュしたものです）

credentials = {
    "usernames": {
        "student1": {
            "name": "student1",
            "password": "$2b$12$0e7eGBlZnpYPgDklHxxh8.qP6Y79UQk3.CI/WTmf9x3BvutHRVKjO"  # 1234
        },
        "student2": {
            "name": "student2",
            "password": "$2b$12$0e7eGBlZnpYPgDklHxxh8.qP6Y79UQk3.CI/WTmf9x3BvutHRVKjO"  # 1234
        },
        "student3": {
            "name": "student3",
            "password": "$2b$12$0e7eGBlZnpYPgDklHxxh8.qP6Y79UQk3.CI/WTmf9x3BvutHRVKjO"  # 1234
        }
    }
}


authenticator = stauth.Authenticate(
    credentials,
    "eiken_quiz_app",  # cookie名
    "abcdef",          # cookieのシークレット
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("ログイン", "main")

if not authentication_status:
    st.error("ユーザー名またはパスワードが違います")
    st.stop()
if authentication_status is None:
    st.warning("ユーザー名とパスワードを入力してください")
    st.stop()


# Googleスプレッドシート接続
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = json.loads(st.secrets["gcp_service_account_json"])
credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=scope)
gc = gspread.authorize(credentials)

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1IfqASoqhNwKFYoJdjkIPIXcO3mCE5j2Ng2PtmlWdj1c/edit#gid=0"
spreadsheet = gc.open_by_url(SPREADSHEET_URL)
worksheet = spreadsheet.worksheet("履歴")

# データ読み込み
df = pd.read_csv("words.csv")

# モード選択
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

# 出題
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


