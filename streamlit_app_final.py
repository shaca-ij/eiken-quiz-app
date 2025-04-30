elif st.session_state.page == "quiz":
    quiz = st.session_state.quiz
    current_idx = st.session_state.current_q_idx
    current_q = quiz[current_idx]

    # 進捗バーとパーセンテージ表示
    progress_ratio = (current_idx + 1) / len(quiz)
    st.markdown(f"### 進捗: {int(progress_ratio * 100)}%")
    st.progress(progress_ratio)

    # 問題表示
    bg_color = "#f0f0f0" if st.get_option("theme.base") == "light" else "#333333"
    st.markdown(f"<div style='background-color:{bg_color}; padding:15px; border-radius:10px;'>"
                f"<b>Q{current_idx + 1}:</b><br>{current_q['sentence_with_blank'].replace(chr(10), '<br>')}"
                f"</div>", unsafe_allow_html=True)

    # 選択肢の表示
    choices = current_q["choices"].split("|")
    random.seed(current_idx)
    choices = random.sample(choices, len(choices))

    selected = st.radio("選択肢を選んでください：", choices, key=f"answer_{current_idx}")

    if f"answered_{current_idx}" not in st.session_state:
        st.session_state[f"answered_{current_idx}"] = False

    if not st.session_state[f"answered_{current_idx}"]:
        if st.button("✅ 解答する"):
            correct = current_q["answer"]
            st.session_state.user_answers.append({
                "selected": selected,
                "correct": correct,
                "word": current_q['word']
            })

            if selected == correct:
                st.success("正解！ 🎉")
            else:
                st.markdown(f"<span style='color:red; font-weight:bold;'>✖ 不正解... 正解は <u>{correct}</u></span>", unsafe_allow_html=True)
                word = current_q["word"]
                st.session_state.mistake_counts[word] = st.session_state.mistake_counts.get(word, 0) + 1

            st.markdown(f"**意味：** {current_q['meaning_jp']}")
            sentence_jp = current_q['sentence_jp']
            if pd.notna(sentence_jp):
                st.markdown(f"**和訳：** {sentence_jp.replace('\n', '<br>')}", unsafe_allow_html=True)
            else:
                st.markdown("**和訳：** （和訳なし）")

            st.session_state[f"answered_{current_idx}"] = True
            st.rerun()

    elif st.session_state[f"answered_{current_idx}"]:
        # 解答表示（再表示用）
        correct = current_q["answer"]
        user_answer = st.session_state.user_answers[current_idx]["selected"]
        if user_answer == correct:
            st.success("正解！ 🎉")
        else:
            st.markdown(f"<span style='color:red; font-weight:bold;'>✖ 不正解... 正解は <u>{correct}</u></span>", unsafe_allow_html=True)
        st.markdown(f"**意味：** {current_q['meaning_jp']}")
        sentence_jp = current_q['sentence_jp']
        if pd.notna(sentence_jp):
            st.markdown(f"**和訳：** {sentence_jp.replace('\n', '<br>')}", unsafe_allow_html=True)
        else:
            st.markdown("**和訳：** （和訳なし）")

        # 次の問題へ
        if st.button("次の問題へ"):
            if current_idx + 1 < len(quiz):
                st.session_state.current_q_idx += 1
                st.rerun()
            else:
                st.session_state.page = "review"
                st.rerun()
