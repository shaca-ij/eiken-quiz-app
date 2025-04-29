import streamlit as st
import pandas as pd
import random

# CSVファイルの読み込み
@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

# セッション状態の初期化
if "app_started" not in st.session_state:
    st.session_state.app_started = False
if "quiz" not in st.session_state:
    st.session_state.quiz = []
if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "user_answer" not in st.session_state:
    st.session_state.user_answer = None
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "choices_shuffled" not in st.session_state:
    st.session_state.choices_shuffled = {}
if "quiz_length" not in st.session_state:
    st.session_state.quiz_length = 5

# タイトル
st.title("📝 英単語クイズアプリ")

# 開始前の画面
if not st.session_state.app_started:
    df = load_data()
    total_questions = len(df)
    st.session_state.quiz_length = st.slider("出題する問題数を選んでください：", 1, total_questions, 5)

    if st.button("スタート！"):
        df = df.sample(frac=1).reset_index(drop=True)
        st.session_state.quiz = df.iloc[:st.session_state.quiz_length].to_dict(orient="records")
        st.session_state.current_q_idx = 0
        st.session_state.app_started = True
        st.rerun()
    st.stop()

# クイズ中の処理
quiz = st.session_state.quiz
current_idx = st.session_state.current_q_idx
current_q = quiz[current_idx]
choices = current_q["choices"].split("|")

# 選択肢のシャッフル（初回のみ）
if current_idx not in st.session_state.choices_shuffled:
    st.session_state.choices_shuffled[current_idx] = random.sample(choices, len(choices))
shuffled_choices = st.session_state.choices_shuffled[current_idx]

# 進捗バー
progress = (current_idx + 1) / st.session_state.quiz_length
st.progress(progress, text=f"{current_idx + 1} / {st.session_state.quiz_length} 問目")

# 問題文の表示（背景と文字色つき）
st.markdown(f"""
<div style="background-color: #f0f8ff; padding: 10px; border-radius: 8px; color: black;">
    <strong>Q{current_idx + 1}:</strong><br>
    {current_q['sentence_with_blank'].replace('\n', '<br>')}
</div>
""", unsafe_allow_html=True)

# 選択肢の表示（ラジオボタン + スタイル調整）
st.markdown("<style>.stRadio > div{ flex-direction: column; }</style>", unsafe_allow_html=True)
st.session_state.user_answer = st.radio(
    "選択肢：",
    shuffled_choices,
    index=None if st.session_state.user_answer is None else shuffled_choices.index(st.session_state.user_answer),
    key=f"answer_{current_idx}"
)

# 解答ボタン
if st.button("✅ 解答する"):
    if st.session_state.user_answer is not None:
        correct = current_q["answer"]
        is_correct = st.session_state.user_answer == correct
        st.session_state.show_result = True

        if is_correct:
            st.success("正解！ 🎉")
        else:
            st.markdown(
                f"<div style='color:red; font-weight:bold;'>✖ 不正解... 正解は <u>{correct}</u></div>",
                unsafe_allow_html=True
            )

        st.markdown(f"**意味：** {current_q['meaning_jp']}")
        st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)
    else:
        st.warning("答えを選んでください。")

# 次の問題へ
if st.session_state.show_result:
    if st.button("次の問題へ"):
        if current_idx + 1 < st.session_state.quiz_length:
            st.session_state.current_q_idx += 1
            st.session_state.show_result = False
            st.session_state.user_answer = None
            st.rerun()
        else:
            st.success("すべての問題が終了しました！ お疲れさまでした。")
            st.session_state.app_started = False
