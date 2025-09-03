import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Mój dashboard", layout="wide")
st.title("Mój pierwszy dashboard w Streamlit 🎉")

df = pd.DataFrame({
    "Kategoria": ["A","B","C","A","B","C"],
    "Wartość": [10,20,30,15,25,5],
    "Rok": [2023,2023,2023,2024,2024,2024]
})

rok = st.sidebar.selectbox("Wybierz rok", sorted(df["Rok"].unique()))
df_filtered = df[df["Rok"] == rok]

fig = px.bar(df_filtered, x="Kategoria", y="Wartość", title=f"Wartości w {rok} roku")
st.plotly_chart(fig, use_container_width=True)
st.dataframe(df_filtered, use_container_width=True)

