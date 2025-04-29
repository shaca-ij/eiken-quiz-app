import streamlit as st
import pandas as pd
import random

# CSVファイルを読み込み
questions_df = pd.read_csv("words.csv")

# セッション初期化
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = questions_df.sample(frac=1).reset_index(drop=True)

if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answered" not in st.session_state:
    st.session_state.answered = False
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = ""

# ← 必ずこのリストを使う！
quiz_questions = st.session_state.quiz_questions


# 問題シャッフル
quiz_questions = questions_df.sample(frac=1).reset_index(drop=True)

# 現在の問題
if st.session_state.current_q_idx < len(quiz_questions):
    current_q = quiz_questions.iloc[st.session_state.current_q_idx]
    question_text = current_q["sentence_with_blank"]
    choices = current_q["choices"].split("|")
    correct_answer = current_q["answer"]
    meaning_jp = current_q["meaning_jp"]
    sentence_jp = current_q["sentence_jp"]

    st.markdown(f"### 問題 {st.session_state.current_q_idx + 1}")
    st.write(question_text)

    # フォームで選択肢と回答ボタン
    with st.form(key="quiz_form"):
        selected_choice = st.radio("選択肢を選んでください", choices)
        submitted = st.form_submit_button("回答する")

        if submitted:
            st.session_state.selected_answer = selected_choice
            st.session_state.answered = True

    # 回答後の処理
if st.session_state.answered:
    if st.session_state.selected_answer == correct_answer:
        st.success(f"✅ 正解！ {correct_answer}")
        st.session_state.score += 1
    else:
        st.error(f"❌ 不正解！ 正解は {correct_answer}")

    st.info(f"【意味】{meaning_jp}")
    st.info(f"【和訳】{sentence_jp}")

    next_button = st.button("▶ 次の問題へ")
    if next_button:
        st.session_state.current_q_idx += 1
        st.session_state.answered = False
        st.session_state.selected_answer = ""
        st.experimental_rerun()  # ← 🔥これでページをリロード！！



else:
    # 全問終了
    st.balloons()
    st.success(f"🎉 全問終了！スコア：{st.session_state.score} / {len(quiz_questions)}")
    if st.button("🔄 もう一度挑戦"):
        st.session_state.current_q_idx = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.selected_answer = ""
