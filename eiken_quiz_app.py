import streamlit as st
import pandas as pd
import random
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

st.set_page_config(page_title="英単語クイズ", layout="centered")

# 日本語フォント設定
font_path = fm.findfont("Noto Sans JP") or "sans-serif"
plt.rcParams["font.family"] = "Noto Sans JP" if font_path != "sans-serif" else "sans-serif"

@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

# データベース接続をセッションで保持
if "db_conn" not in st.session_state:
    st.session_state.db_conn = sqlite3.connect("quiz_results.db")

# その他の関数（init_db, save_result, load_user_stats, load_all_results, compute_accuracy）は変更なし

# クイズページの改良
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
            st.button(choice, key=button_key, use_container_width=True)
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

# 履歴ページのグラフ改良
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
