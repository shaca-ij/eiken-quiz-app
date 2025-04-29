import streamlit as st
import pandas as pd
import random

# CSV読み込み（キャッシュ）
@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

data = load_data()

st.set_page_config(page_title="英単語クイズ", layout="centered")

st.title("📝 英検準2級 英単語クイズ")

# セッション初期化
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
    st.session_state.num_questions = 5  # デフォルト
    st.session_state.current_q_idx = 0
    st.session_state.correct_count = 0
    st.session_state.incorrect_qs = []
    st.session_state.quiz_data = []
    st.session_state.user_answer = None
    st.session_state.show_result = False

# スタート前画面
if not st.session_state.quiz_started:
    st.subheader("出題数を選んでスタート")
    st.session_state.num_questions = st.slider("出題数", 1, len(data), 5)
    if st.button("🚀 スタート"):
        st.session_state.quiz_data = data.sample(frac=1).head(st.session_state.num_questions).to_dict(orient="records")
        st.session_state.quiz_started = True
        st.experimental_rerun()
    st.stop()

# クイズデータ取得
quiz = st.session_state.quiz_data
current_idx = st.session_state.current_q_idx
current_q = quiz[current_idx]
choices = current_q["choices"].split("|")

# 選択肢シャッフル
if "shuffled_choices" not in st.session_state:
    st.session_state.shuffled_choices = {}

if current_idx not in st.session_state.shuffled_choices:
    st.session_state.shuffled_choices[current_idx] = random.sample(choices, len(choices))

shuffled_choices = st.session_state.shuffled_choices[current_idx]

# 進捗バー
st.progress((current_idx) / st.session_state.num_questions)

# 問題番号と本文（背景色付き）
st.markdown(f"<div style='font-size: 20px; font-weight: bold;'>Q{current_idx + 1}:</div>", unsafe_allow_html=True)
problem_html = current_q["sentence_with_blank"].replace("\\n", "<br>").replace("\n", "<br>")
st.markdown(f"<div style='background-color:#f0f8ff; padding:10px; border-radius:8px;'>{problem_html}</div>", unsafe_allow_html=True)

# 選択肢表示（大きめボタン風）
st.session_state.user_answer = st.radio(
    label="\n",
    options=shuffled_choices,
    index=None if st.session_state.user_answer is None else shuffled_choices.index(st.session_state.user_answer),
    key=f"answer_{current_idx}"
)

# 解答ボタン
if st.button("✅ 解答する"):
    if st.session_state.user_answer is not None:
        correct = current_q["answer"]
        if st.session_state.user_answer == correct:
            st.session_state.correct_count += 1
            st.success("🎉 正解！")
        else:
            st.session_state.incorrect_qs.append(current_q)
            st.markdown(
                f"<div style='color: red; font-weight: bold; font-size: 20px;'>✖ 不正解... 正解は <u>{correct}</u></div>",
                unsafe_allow_html=True
            )
        st.markdown(f"**意味：** {current_q['meaning_jp']}")
        st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)
        st.session_state.show_result = True
    else:
        st.warning("答えを選んでください。")

# 次の問題へ
if st.session_state.show_result:
    if st.button("➡ 次の問題へ"):
        st.session_state.current_q_idx += 1
        st.session_state.user_answer = None
        st.session_state.show_result = False

        if st.session_state.current_q_idx >= st.session_state.num_questions:
            st.session_state.quiz_started = False
            st.experimental_rerun()
        else:
            st.experimental_rerun()

# クイズ終了時
if not st.session_state.quiz_started and st.session_state.current_q_idx >= st.session_state.num_questions:
    st.subheader("✅ 結果発表")
    st.write(f"正解数：{st.session_state.correct_count} / {st.session_state.num_questions}")
    
    if st.session_state.incorrect_qs:
        with st.expander("復習モード ✏"):
            for q in st.session_state.incorrect_qs:
                st.markdown(f"**{q['sentence_with_blank'].replace('\n', '<br>')}**", unsafe_allow_html=True)
                st.markdown(f"- 正解：**{q['answer']}**")
                st.markdown(f"- 意味：{q['meaning_jp']}")
                st.markdown(f"- 和訳：{q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)

    if st.button("🔁 最初からもう一度"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
