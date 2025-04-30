import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="英単語クイズ", layout="centered")

@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

# セッション状態初期化
if "page" not in st.session_state:
    st.session_state.page = "start"
if "quiz" not in st.session_state:
    st.session_state.quiz = []
if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = []
if "answered" not in st.session_state:
    st.session_state.answered = False

# スタート画面
if st.session_state.page == "start":
    st.title("📝 英単語クイズ")
    num_questions = st.slider("出題する問題数を選んでください", min_value=1, max_value=50, value=10)

    if st.button("スタート"):
        df = load_data()
        quiz = df.sample(frac=1).head(num_questions).to_dict(orient="records")
        st.session_state.quiz = quiz
        st.session_state.current_q_idx = 0
        st.session_state.user_answers = []
        st.session_state.page = "quiz"
        st.session_state.answered = False
        st.rerun()

# クイズ画面
elif st.session_state.page == "quiz":
    quiz = st.session_state.quiz
    current_idx = st.session_state.current_q_idx
    current_q = quiz[current_idx]

    # 進捗バー（上部）
    st.progress((current_idx + 1) / len(quiz))

    # 問題文（ダーク／ライト対応）
    st.markdown(f"""
        <div style='
            padding:15px; 
            border-radius:10px; 
            background-color:rgba(240, 248, 255, 0.7); 
            color:inherit;
        '>
            <b>Q{current_idx + 1}:</b><br>{current_q['sentence_with_blank'].replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

    # 選択肢の表示（シャッフル）
    choices = current_q["choices"].split("|")
    random.seed(current_idx)  # 再現性のため
    choices = random.sample(choices, len(choices))

    selected = st.radio("選択肢を選んでください：", choices, key=f"answer_{current_idx}")

    # 解答ボタン（未回答時のみ表示）
    if not st.session_state.answered and st.button("✅ 解答する"):
        correct = current_q["answer"]
        st.session_state.user_answers.append({"selected": selected, "correct": correct})
        st.session_state.answered = True

        if selected == correct:
            st.success("正解！ 🎉")
        else:
            st.markdown(
                f"<span style='color:red; font-weight:bold;'>✖ 不正解... 正解は <u>{correct}</u></span>",
                unsafe_allow_html=True
            )

        # 解説
        st.markdown(f"**意味：** {current_q['meaning_jp']}")
        sentence_jp = current_q['sentence_jp']
        if pd.notna(sentence_jp):
            sentence_jp = sentence_jp.replace("\n", "<br>")
            st.markdown(f"**和訳：** {sentence_jp}", unsafe_allow_html=True)
        else:
            st.markdown("**和訳：** （和訳なし）")

    # 次の問題へ（解答後のみ表示）
    if st.session_state.answered:
        if st.button("➡ 次の問題へ"):
            if current_idx + 1 < len(quiz):
                st.session_state.current_q_idx += 1
                st.session_state.answered = False
                st.rerun()
            else:
                st.session_state.page = "review"
                st.rerun()

# 結果画面
elif st.session_state.page == "review":
    st.title("📊 結果と復習")
    score = sum(1 for ans in st.session_state.user_answers if ans["selected"] == ans["correct"])
    total = len(st.session_state.user_answers)
    st.markdown(f"### 正解数： {score} / {total}")

    # 間違えた問題
    st.markdown("---")
    st.markdown("### ❗ 復習（間違えた問題）")
    for i, (q, ans) in enumerate(zip(st.session_state.quiz, st.session_state.user_answers)):
        if ans["selected"] != ans["correct"]:
            st.markdown(f"**Q{i+1}:** {q['sentence_with_blank']}")
            st.markdown(f"- あなたの答え: {ans['selected']}")
            st.markdown(f"- 正解: **{ans['correct']}**")
            st.markdown(f"- 意味: {q['meaning_jp']}")
            if pd.notna(q['sentence_jp']):
                st.markdown(f"- 和訳: {q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)

    if st.button("🔁 もう一度挑戦"):
        st.session_state.page = "start"
        st.session_state.quiz = []
        st.session_state.user_answers = []
        st.session_state.current_q_idx = 0
        st.session_state.answered = False
        st.rerun()
