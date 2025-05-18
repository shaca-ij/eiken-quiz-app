import streamlit as st
import pandas as pd
import random
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# ページ設定
st.set_page_config(page_title="英単語クイズ", layout="centered")

# 日本語フォント設定
font_path = fm.findfont("Noto Sans JP") or "sans-serif"
plt.rcParams["font.family"] = "Noto Sans JP" if font_path != "sans-serif" else "sans-serif"

# データ読み込み
@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

# データベース初期化
def init_db():
    db_path = "quiz_results.db"
    # ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(db_path), exist_ok=True) if os.path.dirname(db_path) else None
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            timestamp TEXT,
            word TEXT,
            selected TEXT,
            correct TEXT,
            is_correct INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# 結果保存
def save_result(user, word, selected, correct, is_correct):
    try:
        conn = sqlite3.connect("quiz_results.db", check_same_thread=False)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO results (username, timestamp, word, selected, correct, is_correct)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user, timestamp, word, selected, correct, int(is_correct)))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"データベースエラー: {e}")
    finally:
        conn.close()

# ユーザー統計
@st.cache_data
def load_user_stats(username):
    try:
        conn = sqlite3.connect("quiz_results.db", check_same_thread=False)
        query = '''
            SELECT word, SUM(is_correct) AS correct_count, COUNT(*) AS total_count
            FROM results
            WHERE username = ?
            GROUP BY word
        '''
        stats = pd.read_sql_query(query, conn, params=(username,))
        if not stats.empty:
            stats["accuracy"] = stats["correct_count"] / stats["total_count"]
        return stats
    except sqlite3.Error as e:
        st.error(f"データベースエラー: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# 全結果取得
def load_all_results(username):
    try:
        conn = sqlite3.connect("quiz_results.db", check_same_thread=False)
        query = '''
            SELECT word, selected, correct, is_correct, timestamp
            FROM results
            WHERE username = ?
        '''
        df = pd.read_sql_query(query, conn, params=(username,))
        return df
    except sqlite3.Error as e:
        st.error(f"データベースエラー: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# 正答率計算
def compute_accuracy(df):
    stats = df.groupby("word").agg(
        total=("is_correct", "count"),
        correct=("is_correct", "sum")
    )
    stats["accuracy"] = stats["correct"] / stats["total"]
    return stats.reset_index()

# セッション状態の初期化
def initialize_session_state():
    defaults = {
        "page": "start",
        "quiz": [],
        "current_q_idx": 0,
        "user_answers": [],
        "answered": False,
        "username": "",
        "review_mode": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# 初期化実行
initialize_session_state()
init_db()

# デバッグ情報
st.write("Session State:", dict(st.session_state))  # デバッグ用

# スタートページ
if st.session_state.page == "start":
    st.title("📝 英単語クイズ")
    st.session_state.username = st.text_input("あなたの名前を入力してください：", value=st.session_state.username)
    num_questions = st.slider("出題する問題数を選んでください", min_value=1, max_value=50, value=10)

    st.session_state.review_mode = st.checkbox("復習モードをオンにする（正答率が低い単語を優先）", value=st.session_state.review_mode)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("スタート") and st.session_state.username.strip():
            df = load_data()
            if st.session_state.review_mode:
                stats = load_user_stats(st.session_state.username)
                if not stats.empty:
                    df["weight"] = df["answer"].apply(lambda word: 
                        1.0 if word not in stats["word"].values else 
                        max(0.1, 1.0 - stats.loc[stats["word"] == word, "accuracy"].values[0])
                    )
                    df = df.sample(n=num_questions, weights=df["weight"], replace=True)
                else:
                    df = df.sample(n=num_questions)
            else:
                df = df.sample(n=num_questions)

            st.session_state.quiz = df.to_dict(orient="records")
            st.session_state.current_q_idx = 0
            st.session_state.user_answers = []
            st.session_state.page = "quiz"
            st.session_state.answered = False
            st.rerun()

    with col2:
        if st.button("履歴を見る"):
            st.session_state.page = "history"
            st.rerun()

# クイズページ
elif st.session_state.page == "quiz":
    quiz = st.session_state.quiz
    idx = st.session_state.current_q_idx
    current_q = quiz[idx]

    st.progress((idx + 1) / len(quiz), text=f"進捗: {idx + 1}/{len(quiz)} ({int((idx + 1) / len(quiz) * 100)}%)")

    st.markdown(f"""
        <div style='padding:15px; border-radius:10px; background-color:rgba(240, 248, 255, 0.7);'>
            {current_q['sentence_with_blank'].replace(chr(10), '<br>').replace('A :', '<span style="color: #4682B4; font-weight: bold;">A:</span>').replace('B :', '<span style="color: #228B22; font-weight: bold;">B:</span>')}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    choices = current_q["choices"].split("|")
    random.seed(idx)
    choices = random.sample(choices, len(choices))

    st.markdown("""
    <style>
        div.stButton > button[kind="primary"][help="正解"] {
            background-color: #90EE90 !important;
            color: black;
        }
        div.stButton > button[kind="primary"][help="あなたの選択（不正解）"] {
            background-color: #FF6347 !important;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state.answered:
        for choice in choices:
            button_key = f"{idx}_{choice}"
            if st.button(choice, key=button_key, use_container_width=True):
                correct = current_q["answer"]
                st.session_state.user_answers.append({"selected": choice, "correct": correct})
                st.session_state.answered = True
                save_result(st.session_state.username, correct, choice, correct, choice == correct)
                st.rerun()
    else:
        selected = st.session_state.user_answers[-1]["selected"]
        correct = current_q["answer"]
        for choice in choices:
            button_key = f"{idx}_{choice}"
            if choice == correct:
                st.button(choice, key=button_key, disabled=True, use_container_width=True, help="正解")
            elif choice == selected:
                st.button(choice, key=button_key, disabled=True, use_container_width=True, help="あなたの選択（不正解）")
            else:
                st.button(choice, key=button_key, disabled=True, use_container_width=True)

        if selected == correct:
            st.success(f"✅ 正解！ {correct}")
        else:
            st.error(f"❌ 不正解... 正解は {correct}")

        st.markdown(f"**意味：** {current_q['meaning_jp']}")
        if pd.notna(current_q["sentence_jp"]):
            st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)

        if st.button("➡ 次の問題へ"):
            if idx + 1 < len(quiz):
                st.session_state.current_q_idx += 1
                st.session_state.answered = False
                st.rerun()
            else:
                st.session_state.page = "review"
                st.rerun()

# 結果ページ
elif st.session_state.page == "review":
    st.title("📊 結果と復習")
    score = sum(1 for ans in st.session_state.user_answers if ans["selected"] == ans["correct"])
    total = len(st.session_state.user_answers)
    st.markdown(f"### 正解数： {score} / {total}")

    st.markdown("---")
    st.markdown("### ❗ 間違えた問題の復習")
    for i, (q, ans) in enumerate(zip(st.session_state.quiz, st.session_state.user_answers)):
        if ans["selected"] != ans["correct"]:
            st.markdown(f"**Q{i+1}:** {q['sentence_with_blank'].replace(chr(10), '<br>')}", unsafe_allow_html=True)
            st.markdown(f"- あなたの答え: {ans['selected']}")
            st.markdown(f"- 正解: **{ans['correct']}**")
            st.markdown(f"- 意味: {q['meaning_jp']}")
            if pd.notna(q['sentence_jp']):
                st.markdown(f"- 和訳: {q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)

    if st.button("🔁 もう一度挑戦"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

# 履歴ページ
elif st.session_state.page == "history":
    st.title("📚 過去のクイズ履歴")

    stats = load_user_stats(st.session_state.username)
    if stats.empty:
        st.info("履歴がありません。まずはクイズを解いてみましょう。")
    else:
        stats = stats.sort_values(by="accuracy")
        st.dataframe(stats[["word", "correct_count", "total_count", "accuracy"]].rename(columns={
            "word": "単語",
            "correct_count": "正解数",
            "total_count": "出題数",
            "accuracy": "正答率"
        }), use_container_width=True)

        import matplotlib.ticker as mtick
        st.subheader("📊 単語ごとの正答率（正答率が低い上位10単語）")
        top_n = 10
        stats = stats.sort_values(by="accuracy").head(top_n)
        fig, ax = plt.subplots(figsize=(8, top_n * 0.4))
        colors = plt.cm.RdYlBu(stats["accuracy"])
        ax.barh(stats["word"], stats["accuracy"], color=colors)
        ax.set_xlabel("正答率")
        ax.set_xlim(0, 1.0)
        ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        ax.tick_params(axis="y", labelsize=10)
        plt.tight_layout()
        st.pyplot(fig)

    if st.button("⬅ ホームに戻る"):
        st.session_state.page = "start"
        st.rerun()
