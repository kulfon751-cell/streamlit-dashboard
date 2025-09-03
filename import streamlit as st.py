import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Obciążenie i dostępność urządzeń", layout="wide")
st.title("⚙️ Obciążenie i dostępność urządzeń")

# ----------------- DANE -----------------
file = st.sidebar.file_uploader(
    "Wgraj dane (CSV lub XLS/XLSX)", type=["csv", "xls", "xlsx"]
)

if file is None:
    st.info("Wgraj plik CSV lub XLS/XLSX z kolumnami: Dział, Nazwa Urządzenia, Dostępność/h, Obciążenie/h, Brakujące Godziny, Tydzień, Miesiąc, Numer części")
    st.stop()

if file.name.endswith(".csv"):
    try:
        df = pd.read_csv(file, encoding="utf-8", sep=None, engine="python", on_bad_lines='skip')
    except UnicodeDecodeError:
        df = pd.read_csv(file, encoding="cp1250", sep=None, engine="python", on_bad_lines='skip')
else:
    df = pd.read_excel(file)

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