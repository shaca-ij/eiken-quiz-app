import streamlit as st
import pandas as pd
import random

# CSV読み込み
@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

# 初期状態の定義
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "quiz" not in st.session_state:
    st.session_state.quiz = []
if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "user_answer" not in st.session_state:
    st.session_state.user_answer = None
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "num_questions" not in st.session_state:
    st.session_state.num_questions = 5  # デフォルト値
if "choices_shuffled" not in st.session_state:
    st.session_state.choices_shuffled = {}

st.title("📝 英検準2級 英単語クイズ")

# クイズ開始前の設定画面
if not st.session_state.quiz_started:
    st.markdown("### クイズを始める準備をしましょう")
    num = st.slider("出題する問題数を選んでください", 1, 30, st.session_state.num_questions)
    st.session_state.num_questions = num

    if st.button("▶ スタート"):
        df = load_data().sample(frac=1).reset_index(drop=True)
        st.session_state.quiz = df.head(num).to_dict(orient="records")
        st.session_state.quiz_started = True
        st.session_state.current_q_idx = 0
        st.session_state.user_answer = None
        st.session_state.show_result = False
        st.session_state.choices_shuffled = {}
        st.rerun()

# クイズ開始後
if st.session_state.quiz_started:
    quiz = st.session_state.quiz
    current_idx = st.session_state.current_q_idx
    current_q = quiz[current_idx]
    choices = current_q["choices"].split("|")

    # 選択肢シャッフル
    if current_idx not in st.session_state.choices_shuffled:
        st.session_state.choices_shuffled[current_idx] = random.sample(choices, len(choices))
    shuffled_choices = st.session_state.choices_shuffled[current_idx]

    # 進捗バー
    progress = (current_idx) / st.session_state.num_questions
    st.progress(progress, text=f"Q{current_idx + 1} / {st.session_state.num_questions}")

    # 問題文表示
    st.markdown(f"### Q{current_idx + 1}：")
    st.markdown(
        f"<div style='background-color:#f0f8ff; padding:12px; border-radius:8px; font-size:18px; line-height:1.6;'>"
        f"{current_q['sentence_with_blank'].replace('\\n', '<br>')}</div>",
        unsafe_allow_html=True,
    )

    # 選択肢ラジオ
    st.session_state.user_answer = st.radio(
        "選択肢：",
        shuffled_choices,
        index=None if st.session_state.user_answer is None else shuffled_choices.index(st.session_state.user_answer),
        key=f"answer_{current_idx}",
        format_func=lambda x: f"　　{x}",  # 文字ずれ防止の余白
    )

    # 解答ボタン
    if st.button("✅ 解答する"):
        if st.session_state.user_answer is not None:
            correct = current_q["answer"]
            if st.session_state.user_answer == correct:
                st.success("🎉 正解！")
            else:
                st.error(f"<span style='color:red; font-weight:bold;'>✖ 不正解... 正解は <u>{correct}</u></span>",
                         unsafe_allow_html=True)

            st.markdown(f"**意味：** {current_q['meaning_jp']}")
            st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)
            st.session_state.show_result = True
        else:
            st.warning("答えを選んでください。")

    # 次の問題へ
    if st.session_state.show_result:
        if st.button("➡ 次の問題へ"):
            if st.session_state.current_q_idx + 1 < len(st.session_state.quiz):
                st.session_state.current_q_idx += 1
                st.session_state.user_answer = None
                st.session_state.show_result = False
                st.rerun()
            else:
                st.success("🎉 すべての問題が終了しました！お疲れ様でした。")
