import streamlit as st
import pandas as pd
import random

# データ読み込み（キャッシュ）
@st.cache_data
def load_data():
    df = pd.read_csv("words.csv")
    return df

# 初期画面の表示
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
    st.session_state.total_questions = 5  # デフォルト値
    st.title("📝 英検準2級クイズ")
    st.slider("出題する問題数を選んでください（最大20問）", 1, 20, 5, key="total_questions")
    if st.button("スタート！"):
        st.session_state.quiz_started = True
        st.session_state.quiz = load_data().sample(frac=1).head(st.session_state.total_questions).to_dict(orient="records")
        st.session_state.current_q_idx = 0
        st.session_state.user_answer = None
        st.session_state.show_result = False
        st.session_state.correct_count = 0
        st.stop()  # スタート後に即再描画
    st.stop()

# クイズ開始後の画面
df = load_data()
quiz = st.session_state.quiz
current_idx = st.session_state.current_q_idx
current_q = quiz[current_idx]
choices = current_q["choices"].split("|")

# 選択肢のシャッフル管理
if "choices_shuffled" not in st.session_state:
    st.session_state.choices_shuffled = {}

if current_idx not in st.session_state.choices_shuffled:
    st.session_state.choices_shuffled[current_idx] = random.sample(choices, len(choices))

shuffled_choices = st.session_state.choices_shuffled[current_idx]

# タイトルと進捗バー
st.title("📝 英検準2級クイズ")
st.progress((current_idx) / st.session_state.total_questions)

# 問題番号 + 問題文の表示
st.markdown(f"<div style='font-size: 22px; font-weight: bold; margin-top: 20px;'>Q{current_idx + 1}:</div>", unsafe_allow_html=True)
sentence_html = current_q['sentence_with_blank'].replace("\n", "<br>").replace("、", "、<br>")
st.markdown(f"""
<div style='background-color: #f0f8ff; padding: 16px; border-radius: 10px; font-size: 20px; line-height: 1.6'>
{sentence_html}
</div>
""", unsafe_allow_html=True)

# 選択肢の表示（フォント大きめ）
st.session_state.user_answer = st.radio(
    "選択肢：",
    shuffled_choices,
    index=None if st.session_state.user_answer is None else shuffled_choices.index(st.session_state.user_answer),
    key=f"answer_{current_idx}",
    format_func=lambda x: f"　{x}",  # 少しインデント入れる
)

# 解答ボタン
if st.button("✅ 解答する"):
    if st.session_state.user_answer is not None:
        correct_answer = current_q["answer"]
        is_correct = st.session_state.user_answer == correct_answer
        st.session_state.show_result = True

        if is_correct:
            st.success("✅ 正解！ 🎉")
            st.session_state.correct_count += 1
        else:
            st.markdown(
                f"<div style='color: red; font-size: 22px; font-weight: bold;'>✖ 不正解... 正解は {correct_answer}</div>",
                unsafe_allow_html=True
            )

        st.markdown(f"**意味：** {current_q['meaning_jp']}")
        st.markdown(f"**和訳：** {current_q['sentence_jp'].replace(chr(10), '<br>')}", unsafe_allow_html=True)
    else:
        st.warning("答えを選んでください。")

# 次の問題へボタン
if st.session_state.show_result:
    if st.button("次の問題へ"):
        if current_idx + 1 < st.session_state.total_questions:
            st.session_state.current_q_idx += 1
            st.session_state.user_answer = None
            st.session_state.show_result = False
            st.stop()
        else:
            st.markdown("## ✅ すべての問題が終了しました！")
            st.markdown(f"🎯 正解数: **{st.session_state.correct_count} / {st.session_state.total_questions}**")
            if st.button("最初に戻る"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.stop()
