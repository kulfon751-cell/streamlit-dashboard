import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Obciążenie i dostępność urządzeń", layout="wide")
st.title("⚙️ Obciążenie i dostępność urządzeń")

# ----------------- DANE -----------------
# Wgraj CSV z tymi samymi kolumnami, co w BI
file = st.sidebar.file_uploader("Wgraj dane (CSV)", type="csv")

if file is None:
    st.info("Wgraj plik CSV z kolumnami: Dział, Nazwa Urządzenia, Dostępność/h, Obciążenie/h, Brakujące Godziny, Tydzień, Miesiąc, Numer części")
    st.stop()

df = pd.read_csv(file)

# ----------------- FILTRY -----------------
st.sidebar.header("Filtry")

dzial = st.sidebar.multiselect("Dział", df["Dział"].unique())
urz = st.sidebar.multiselect("Urządzenie", df["Nazwa Urządzenia"].unique())
mies = st.sidebar.multiselect("Miesiąc", df["Miesiąc"].unique())
tydz = st.sidebar.multiselect("Tydzień", df["Tydzień"].unique())

df_f = df.copy()
if dzial: df_f = df_f[df_f["Dział"].isin(dzial)]
if urz: df_f = df_f[df_f["Nazwa Urządzenia"].isin(urz)]
if mies: df_f = df_f[df_f["Miesiąc"].isin(mies)]
if tydz: df_f = df_f[df_f["Tydzień"].isin(tydz)]

if df_f.empty:
    st.warning("Brak danych po filtrach.")
    st.stop()

# ----------------- KPI -----------------
c1, c2, c3 = st.columns(3)
c1.metric("Dostępność [h]", f"{df_f['Dostępność/h'].sum():,.0f}")
c2.metric("Obciążenie [h]", f"{df_f['Obciążenie/h'].sum():,.0f}")
c3.metric("Brakujące godziny", f"{df_f['Brakujące Godziny'].sum():,.0f}")

# ----------------- WYKRESY -----------------
# Obciążenie vs Braki per maszyna
fig1 = px.bar(df_f, x="Nazwa Urządzenia", y=["Obciążenie/h","Brakujące Godziny"],
              barmode="group", title="Obciążenie i braki wg urządzenia")
st.plotly_chart(fig1, use_container_width=True)

# Obciążenie wg numeru części
fig2 = px.bar(df_f, x="Numer części", y="Obciążenie/h",
              title="Obciążenie wg numeru części")
st.plotly_chart(fig2, use_container_width=True)

# ----------------- TABELA -----------------
st.subheader("Tabela szczegółowa")
st.dataframe(df_f, use_container_width=True)

# ----------------- EXPORT -----------------
st.download_button("📥 Pobierz dane filtrowane (CSV)",
                   df_f.to_csv(index=False).encode("utf-8"),
                   file_name="obciazenie_filtrowane.csv",
                   mime="text/csv")
