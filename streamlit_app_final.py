import pandas as pd
import streamlit as st

def load_quiz_data():
    df = pd.read_csv("words.csv")

    # ★列名の確認を表示（デバッグ用）
    st.write("CSVの列名:", df.columns.tolist())

    # もとの処理に続けて使う
    quiz_data = []
    for _, row in df.iterrows():
        quiz_data.append({
            "word": row["word"],
            "answer": row["answer"],
            "choices": row["choices"].split("|"),
            "sentence_with_blank": row["sentence_with_blank"],
            "meaning_jp": row["meaning_jp"],
            "sentence_jp": row["sentence_jp"]
        })
    return quiz_data


