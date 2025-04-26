
import streamlit as st
import pandas as pd
import random
import gspread
import json
from google.oauth2 import service_account

# Google Sheets認証（超正しいバージョン）
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

service_account_info = json.loads(st.secrets["gcp_service_account_json"])
credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=scope)
gc = gspread.authorize(credentials)

# スプレッドシートとワークシートを開く
spreadsheet = gc.open_by_key("1IfqASoqhNwKFYoJdjkIPIXcO3mCE5j2Ng2PtmlWdj1c")
worksheet = spreadsheet.worksheet("履歴")

# 単語データ読み込み
df = pd.read_csv("words.csv")

# 初期設定
if "mode" not in st.session_state:
    st.session_state["mode"] = "normal"
if "quiz" not in st.session_state:
    st.session_state["quiz"] = []
if "score" not in st.session_state:
    st.session_state["score"] = 0
if "answers" not in st.session_state:
    st.session_state["answers"] = {}
if "mistakes" not in st.session_state:
    st.session_state["mistakes"] = []

# UI部分
st.title("英単語クイズ")

mode = st.radio("モード選択", ["通常モード", "復習モード"], index=0)

if mode == "復習モード" and not st.session_state["mistakes"]:
    st.warning("復習できる問題がまだありません。通常モードで間違えてください。")
    st.stop()

quiz_base = df.copy()

if mode == "復習モード":
    quiz_base = quiz_base[quiz_base["word"].isin(st.session_state["mistakes"])]
    if quiz_base.empty:
        st.success("復習リストは全て正解しました！通常モードに戻ります。")
        st.session_state["mode"] = "normal"
        st.stop()

max_questions = len(quiz_base)
if max_questions == 0:
    st.error("出題できる問題がありません。")
    st.stop()

quiz_size = st.slider("出題数を選んでください", 1, max_questions, min(5, max_questions), key="quiz_size_slider")

if st.button("▶ クイズを始める", key="start_quiz_button"):
    selected = quiz_base.sample(quiz_size).to_dict(orient="records")
    for q in selected:
        q["shuffled_choices"] = random.sample(q["choices"].split("|"), 4)
    st.session_state["quiz"] = selected
    st.session_state["score"] = 0
    st.session_state["answers"] = {}
    st.session_state["mode"] = mode

# クイズ問題出題
if st.session_state["quiz"]:
    quiz = st.session_state["quiz"]
    st.subheader(f"全{len(quiz)}問中 {len(st.session_state['answers'])+1}問目")

    current_q = quiz[len(st.session_state["answers"])]

    st.write(current_q["sentence_with_blank"])
    user_answer = st.radio("選択肢を選んでください", current_q["shuffled_choices"], key=f"q{len(st.session_state['answers'])}")

    if st.button("解答する", key=f"submit{len(st.session_state['answers'])}"):
        is_correct = user_answer == current_q["answer"]
        st.session_state["answers"][len(st.session_state["answers"])] = (user_answer, is_correct)
        if is_correct:
            st.session_state["score"] += 1
            if current_q["word"] in st.session_state["mistakes"]:
                st.session_state["mistakes"].remove(current_q["word"])
        else:
            if current_q["word"] not in st.session_state["mistakes"]:
                st.session_state["mistakes"].append(current_q["word"])
        st.experimental_rerun()

# 結果表示
if st.session_state["quiz"] and len(st.session_state["answers"]) == len(st.session_state["quiz"]):
    st.success(f"あなたのスコアは {st.session_state['score']} / {len(st.session_state['quiz'])} です。")

    # 履歴に記録する
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for idx, (user_answer, is_correct) in st.session_state["answers"].items():
        q = st.session_state["quiz"][idx]
        worksheet.append_row([
            timestamp,
            q["word"],
            user_answer,
            q["answer"],
            "正解" if is_correct else "不正解"
        ])

    if st.session_state["mode"] == "復習モード":
        st.success("復習リストが更新されました！")

    if st.button("もう一度挑戦する", key="retry_button"):
        st.session_state["quiz"] = []
        st.session_state["answers"] = {}
        st.session_state["score"] = 0
        st.experimental_rerun()
