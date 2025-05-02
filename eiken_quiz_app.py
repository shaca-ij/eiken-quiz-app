import streamlit as st
import random

# セッション状態の初期化
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = [
        {"question": "Some students liked to study in a group, while ________ preferred to study alone.",
         "choices": ["such others", "other", "others", "the other"],
         "answer": "others",
         "meaning": "取引",
         "translation": "ジェイソンは"},
        # さらに問題を追加可能
    ]
    st.session_state.current_index = 0
    st.session_state.answered = False
    st.session_state.selected_choice = None
    st.session_state.score = 0

quiz = st.session_state.quiz_data
index = st.session_state.current_index
question = quiz[index]

st.markdown(f"### Q{index + 1}:")
st.markdown(f"<div style='margin-bottom: 20px; font-size: 18px;'>{question['question']}</div>", unsafe_allow_html=True)

# 選択肢ボタン
selected = st.radio("選択肢を選んでください：", question["choices"],
                    index=None, key=f"choice_{index}",
                    disabled=st.session_state.answered)

if selected is not None and not st.session_state.answered:
    st.session_state.selected_choice = selected

# 解答ボタン
if st.button("✅ 解答する"):
    if st.session_state.selected_choice:
        st.session_state.answered = True
        if st.session_state.selected_choice == question["answer"]:
            st.success("✔ 正解です！")
            st.session_state.score += 1
        else:
            st.error(f"❌ 不正解… 正解は **{question['answer']}**")
        st.markdown(f"**意味**：{question['meaning']}")
        st.markdown(f"**和訳**：{question['translation']}")

# 次の問題へ
if st.session_state.answered and st.button("➡ 次の問題へ"):
    if st.session_state.current_index + 1 < len(quiz):
        st.session_state.current_index += 1
        st.session_state.answered = False
        st.session_state.selected_choice = None
    else:
        st.markdown("### 🎉 すべての問題が完了しました！")
        st.markdown(f"**スコア**：{st.session_state.score} / {len(quiz)}")

# カスタム CSS（ボタン背景色や間隔）
st.markdown("""
<style>
div[data-baseweb="radio"] > div {
    margin-bottom: 10px;
}
label[data-baseweb="radio"] > div {
    background-color: #e0f0ff;
    padding: 6px 10px;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)
