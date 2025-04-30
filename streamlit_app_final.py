import streamlit as st
import pandas as pd
import random

# --- 設定 ---
CSV_FILENAME = "words.csv"

# --- データ読み込み関数 ---
def load_quiz_data():
    df = pd.read_csv(CSV_FILENAME)
    quiz_list = []
    for _, row in df.iterrows():
        quiz_list.append({
            "sentence_with_blank": row["sentence_with_blank"],
            "choices": row["choices"].split("|"),
            "answer": row["answer"],
            "sentence_jp": row["sentence_jp"],
            "meaning_jp": row["meaning_jp"]
        })
    return quiz_list

# --- クイズの初期化関数 ---
def initialize_quiz():
    full_quiz = load_quiz_data()
    random.shuffle(full_quiz)
    st.session_state.quiz = full_quiz[:st.session_state.num_questions]
    st.session_state.current_q_idx = 0
    st.session_state.correct_count = 0
    st.session_state.user_answers = []
    st.session_state.show_result = False

# --- Streamlit UI 開始 ---
st.set_page_config(page_title="英検準2級クイズ", layout="centered")
st.title("英検準2級 単語クイズ")

# --- 初回起動時のセッション初期化 ---
if "quiz" not in st.session_state:
    st.session_state.num_questions = 5
    st.session_state.page = "start"

# --- スタートページ ---
if st.session_state.page == "start":
    st.subheader("出題数を選んでスタート！")
    st.session_state.num_questions = st.slider("問題数", min_value=1, max_value=50, value=5)
    if st.button("スタート"):
        initialize_quiz()
        st.session_state.page = "quiz"
        st.experimental_rerun()
    st.stop()

# --- クイズ中 ---
quiz = st.session_state.quiz
current_idx = st.session_state.current_q_idx
current_q = quiz[current_idx]

# --- 進捗バー ---
st.progress((current_idx) / len(quiz), text=f"{current_idx + 1} / {len(quiz)} 問目")

# --- 問題文表示（背景色付き） ---
question_html = f"""
<div style='background-color:#f0f8ff; padding:15px; border-radius:10px; font-size:20px;'>
  <strong>Q{current_idx + 1}:</strong><br>{current_q['sentence_with_blank'].replace('\n', '<br>')}
</div>
"""
st.markdown(question_html, unsafe_allow_html=True)

# --- 選択肢表示（ラジオボタン形式で大きめ文字） ---
choice = st.radio("選択肢を選んでください：",
                  options=current_q['choices'],
                  index=None,
                  format_func=lambda x: f"  {x}",
                  key=f"q{current_idx}")

# --- 解答ボタン表示 ---
if choice is not None and not st.session_state.show_result:
    if st.button("解答する"):
        st.session_state.user_answers.append(choice)
        st.session_state.show_result = True
        if choice == current_q['answer']:
            st.session_state.correct_count += 1

# --- 解答結果表示 ---
if st.session_state.show_result:
    if choice == current_q['answer']:
        st.success("✅ 正解！")
    else:
        st.markdown(f"<div style='color:red; font-weight:bold;'>✖ 不正解... 正解は <u>{current_q['answer']}</u></div>", unsafe_allow_html=True)

    # 和訳と意味
    st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)
    st.markdown(f"**意味：** {current_q['meaning_jp']}")

    # 次の問題へ or 結果表示
    if current_idx + 1 < len(quiz):
        if st.button("次の問題へ"):
            st.session_state.current_q_idx += 1
            st.session_state.show_result = False
            st.experimental_rerun()
    else:
        if st.button("結果を見る"):
            st.session_state.page = "result"
            st.experimental_rerun()

# --- 結果ページ ---
if st.session_state.page == "result":
    st.subheader("結果")
    total = len(st.session_state.quiz)
    correct = st.session_state.correct_count
    st.markdown(f"### 正解数: {correct} / {total}")
    st.markdown("---")
    st.button("もう一度やる", on_click=lambda: st.session_state.clear())
