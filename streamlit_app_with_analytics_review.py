
import streamlit as st
import pandas as pd
import random
import json
import os
import plotly.express as px

MISTAKE_FILE = "last_mistakes.json"
HISTORY_FILE = "answer_history.json"

def save_mistakes(mistakes):
    with open(MISTAKE_FILE, "w", encoding="utf-8") as f:
        json.dump(mistakes, f, ensure_ascii=False, indent=2)

def load_mistakes():
    if os.path.exists(MISTAKE_FILE):
        with open(MISTAKE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def append_history(entries):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    history.extend(entries)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@st.cache_data
def load_data():
    df = pd.read_csv("words.csv", encoding="utf-8-sig")
    return df

df = load_data()

st.title("📘 英検単語クイズ（復習・正答率付き）")

mode = st.radio("モードを選択してください", ["クイズを解く", "復習モード", "正答率グラフを見る"])

if mode == "正答率グラフを見る":
    st.subheader("📊 単語ごとの正答率")
    history = pd.DataFrame(load_history())
    if history.empty:
        st.info("まだ履歴がありません。クイズを解いてください。")
    else:
        summary = history.groupby("word").agg(
            attempts=("correct", "count"),
            corrects=("correct", "sum")
        ).reset_index()
        summary["accuracy"] = (summary["corrects"] / summary["attempts"] * 100).round(1)
        st.dataframe(summary.sort_values("accuracy"))

        fig = px.bar(
            summary.sort_values("accuracy"),
            x="accuracy",
            y="word",
            orientation="h",
            title="単語ごとの正答率（%）",
            labels={"accuracy": "正答率（%）", "word": "英単語"}
        )
        st.plotly_chart(fig, use_container_width=True)
    st.stop()

# --- クイズ or 復習モード ---
if mode == "復習モード":
    mistakes = load_mistakes()
    if not mistakes:
        st.warning("復習する問題はありません。")
        st.stop()
    quiz_base = pd.DataFrame(mistakes)
else:
    quiz_base = df.copy()

max_questions = len(quiz_base)
if max_questions == 0:
    st.error("出題できる問題がありません。")
    st.stop()
elif max_questions == 1:
    st.info("出題できる問題は1問のみです。")
    quiz_size = 1
else:
    quiz_size = st.slider("出題数を選んでください", 1, max_questions, min(5, max_questions), key="quiz_size_slider")

if st.button("▶ クイズを始める"):
    selected = quiz_base.sample(quiz_size).to_dict(orient="records")
    for q in selected:
        q["shuffled_choices"] = random.sample(q["choices"].split("|"), 4)
    st.session_state["quiz"] = selected
    st.session_state["answers"] = {}
    st.session_state["mode"] = mode

if "quiz" in st.session_state:
    st.subheader("📝 問題")

    for i, q in enumerate(st.session_state["quiz"]):
        st.markdown(f"**Q{i+1}: {q['sentence_with_blank']}**")
        user_answer = st.radio(
            f"選択肢を選んでください - Q{i+1}",
            q["shuffled_choices"],
            key=f"answer_{i}"
        )
        st.session_state["answers"][i] = user_answer

    if st.button("✅ 答え合わせ"):
        score = 0
        new_mistakes = []
        history_log = []

        st.subheader("📊 結果")

        for i, q in enumerate(st.session_state["quiz"]):
            correct = q["correct"]
            user = st.session_state["answers"].get(i, "")
            is_correct = user == correct

            st.markdown(f"**Q{i+1}: {q['sentence_with_blank']}**")
            st.write(f"あなたの答え: {user} → {'✅ 正解' if is_correct else f'❌ 不正解（正解は: {correct}）'}")
            st.write(f"意味: {q['meaning_jp']}")
            st.write(f"和訳: {q['sentence_jp']}")
            st.markdown("---")

            history_log.append({
                "word": q["word"],
                "correct": is_correct
            })

            if not is_correct:
                new_mistakes.append(q)
            else:
                score += 1

        st.success(f"あなたのスコア: {score} / {len(st.session_state['quiz'])}")
        save_mistakes(new_mistakes)
        append_history(history_log)
