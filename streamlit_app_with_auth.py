
import streamlit as st
import pandas as pd
import random
import json
import os
import streamlit_authenticator as stauth

# --- 初期設定 ---
USER_HISTORY_DIR = "user_history"

# --- 正しいユーザー情報形式 ---
usernames = ["student1", "student2", "student3"]
names = ["Student One", "Student Two", "Student Three"]
passwords = ["1234", "1234", "1234"]  # 仮パスワード（本番ではハッシュ保存）

hashed_passwords = stauth.Hasher(passwords).generate()

credentials = {
    "usernames": {
        username: {
            "name": name,
            "password": hashed
        }
        for username, name, hashed in zip(usernames, names, hashed_passwords)
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "eiken_quiz_app",
    "auth_cookie_secret",
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("ログイン", "main")

if authentication_status is False:
    st.error("ユーザー名またはパスワードが違います。")
elif authentication_status is None:
    st.warning("ユーザー名とパスワードを入力してください。")
elif authentication_status:
    st.success(f"{name} さん、ようこそ！")
    authenticator.logout("ログアウト", "sidebar")

    st.title("📘 英検単語クイズ")

    df = pd.read_csv("words.csv", encoding="utf-8-sig")

    # 履歴ファイルの準備
    os.makedirs(USER_HISTORY_DIR, exist_ok=True)
    history_path = os.path.join(USER_HISTORY_DIR, f"{username}_history.json")
    mistake_path = os.path.join(USER_HISTORY_DIR, f"{username}_mistakes.json")

    def load_json(filepath):
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_json(filepath, data):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    mode = st.radio("モードを選択してください", ["クイズを解く", "復習モード", "正答率グラフを見る"])

    if mode == "正答率グラフを見る":
        history = pd.DataFrame(load_json(history_path))
        if history.empty:
            st.info("まだ履歴がありません。クイズを解いてください。")
        else:
            summary = history.groupby("word").agg(
                attempts=("correct", "count"),
                corrects=("correct", "sum")
            ).reset_index()
            summary["accuracy"] = (summary["corrects"] / summary["attempts"] * 100).round(1)
            st.dataframe(summary.sort_values("accuracy"))
            st.bar_chart(data=summary.set_index("word")[["accuracy"]])
        st.stop()

    elif mode == "復習モード":
        mistakes = load_json(mistake_path)
        if not mistakes:
            st.warning("復習する問題はありません。")
            st.stop()
        quiz_base = pd.DataFrame(mistakes)
    else:
        quiz_base = df.copy()

    if len(quiz_base) == 0:
        st.error("出題できる問題がありません。")
        st.stop()

    quiz_size = st.slider("出題数を選んでください", 1, len(quiz_base), min(5, len(quiz_base)), key="quiz_size_slider")

    if st.button("▶ クイズを始める"):
        selected = quiz_base.sample(quiz_size).to_dict(orient="records")
        for q in selected:
            q["shuffled_choices"] = random.sample(q["choices"].split("|"), 4)
        st.session_state["quiz"] = selected
        st.session_state["answers"] = {}

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
            prev_history = load_json(history_path)
            save_json(history_path, prev_history + history_log)
            save_json(mistake_path, new_mistakes)
