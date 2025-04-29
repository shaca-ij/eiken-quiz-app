import streamlit as st
import pandas as pd
import random

# CSV読み込み
@st.cache_data
def load_data():
    return pd.read_csv("words.csv")

# 🌟 初期化（最初に一度だけ）
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
    st.session_state.selected_question_count = 10
    st.stop()

# タイトル
st.title("📝 英検準2級クイズアプリ")

# 🌟 スタート前の画面
if not st.session_state.quiz_started:
    st.markdown("### ✅ 出題数を選んでください")
    st.session_state.selected_question_count = st.slider("問題数", 5, 30, 10)
    if st.button("クイズスタート！"):
        df = load_data()
        st.session_state.quiz = df.sample(frac=1).head(st.session_state.selected_question_count).to_dict(orient="records")
        st.session_state.current_q_idx = 0
        st.session_state.user_answer = None
        st.session_state.show_result = False
        st.session_state.review_list = []
        st.session_state.quiz_started = True
        st.experimental_rerun()
    st.stop()

# 🌟 クイズ進行画面
current_idx = st.session_state.current_q_idx
current_q = st.session_state.quiz[current_idx]
choices = current_q["choices"].split("|")

# シャッフル済み選択肢を記録
if "choices_shuffled" not in st.session_state:
    st.session_state.choices_shuffled = {}

if current_idx not in st.session_state.choices_shuffled:
    st.session_state.choices_shuffled[current_idx] = random.sample(choices, len(choices))

shuffled_choices = st.session_state.choices_shuffled[current_idx]

# 🌟 進捗バー
progress = (current_idx + 1) / len(st.session_state.quiz)
st.progress(progress, text=f"{current_idx + 1} / {len(st.session_state.quiz)} 問目")

# 🌟 問題表示（背景色あり・改行処理）
st.markdown(
    f"""
    <div style="background-color: #f0f8ff; padding: 16px; border-radius: 10px; margin-bottom: 10px;">
        <strong>Q{current_idx + 1}:</strong><br>
        {current_q['sentence_with_blank'].replace("\\n", "<br>")}
    </div>
    """,
    unsafe_allow_html=True
)

# 🌟 選択肢（大きく見やすく）
st.markdown("### 選択肢：")
for choice in shuffled_choices:
    if st.button(choice, key=f"choice_{current_idx}_{choice}"):
        st.session_state.user_answer = choice
        st.session_state.show_result = True
        st.experimental_rerun()

# 🌟 結果表示
if st.session_state.show_result:
    correct = current_q["answer"]
    if st.session_state.user_answer == correct:
        st.success("🎉 正解！")
    else:
        st.markdown(
            f"""
            <div style="background-color: #ffe4e1; padding: 10px; border-radius: 10px;">
                <span style="font-size: 22px; color: red;">✖ 不正解... 正解は <strong>{correct}</strong></span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.session_state.review_list.append(current_q)

    st.markdown(f"**意味：** {current_q['meaning_jp']}")
    st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)

    if st.button("次の問題へ"):
        if current_idx + 1 < len(st.session_state.quiz):
            st.session_state.current_q_idx += 1
            st.session_state.user_answer = None
            st.session_state.show_result = False
            st.experimental_rerun()
        else:
            st.success("✅ すべての問題が終了しました！")
            if st.session_state.review_list:
                st.markdown("### 🔁 間違えた問題を復習しますか？")
                if st.button("復習モードへ"):
                    st.session_state.quiz = st.session_state.review_list
                    st.session_state.current_q_idx = 0
                    st.session_state.user_answer = None
                    st.session_state.show_result = False
                    st.session_state.review_list = []
                    st.experimental_rerun()
            else:
                st.markdown("お疲れ様でした！🎉")
            st.stop()
