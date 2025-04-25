
import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="学習履歴（管理者ビュー）", layout="wide")

st.title("👩‍🏫 学習者ごとの正答履歴")

USER_HISTORY_DIR = "user_history"

# 履歴ファイル一覧を取得
if not os.path.exists(USER_HISTORY_DIR):
    st.warning("履歴フォルダが存在しません。")
    st.stop()

files = [f for f in os.listdir(USER_HISTORY_DIR) if f.endswith("_history.json")]

if not files:
    st.info("まだ履歴データがありません。")
    st.stop()

data = []

# ファイルごとに読み込む
for file in files:
    username = file.replace("_history.json", "")
    with open(os.path.join(USER_HISTORY_DIR, file), "r", encoding="utf-8") as f:
        records = json.load(f)
        for r in records:
            data.append({
                "user": username,
                "word": r["word"],
                "correct": r["correct"]
            })

df = pd.DataFrame(data)

st.write(f"📦 合計記録数: {len(df)} 件")

# 集計表示
summary = df.groupby(["user", "word"]).agg(
    attempts=("correct", "count"),
    corrects=("correct", "sum")
).reset_index()

summary["accuracy (%)"] = (summary["corrects"] / summary["attempts"] * 100).round(1)

# 表示設定
selected_user = st.selectbox("ユーザーを選択", options=["すべて"] + sorted(df["user"].unique().tolist()))

if selected_user != "すべて":
    filtered = summary[summary["user"] == selected_user]
else:
    filtered = summary

st.dataframe(filtered.sort_values(by=["user", "accuracy (%)"]))

# オプション: CSVダウンロード
csv = filtered.to_csv(index=False, encoding="utf-8-sig")
st.download_button(
    label="📥 CSVとしてダウンロード",
    data=csv,
    file_name="user_accuracy_report.csv",
    mime="text/csv"
)
