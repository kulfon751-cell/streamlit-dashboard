import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Obciążenie i dostępność urządzeń", layout="wide")
st.title("⚙️ Obciążenie i dostępność urządzeń")

# ----------------- DANE -----------------
# Wgraj jeden lub więcej plików (CSV, XLS, XLSX)
files = st.sidebar.file_uploader(
    "Wgraj dane (CSV lub XLS/XLSX)", type=["csv", "xls", "xlsx"], accept_multiple_files=True
)

if not files:
    st.info(
        "Wgraj jeden lub więcej plików CSV/XLS/XLSX z kolumnami: Dział, Nazwa Urządzenia, Dostępność/h, Obciążenie/h, Brakujące Godziny, Tydzień, Miesiąc, Numer części"
    )
    st.stop()

# Wczytaj i połącz wszystkie pliki
dfs = []
for f in files:
    name = f.name.lower()
    if name.endswith(".csv"):
        try:
            dfs.append(pd.read_csv(f, encoding="utf-8", sep=None, engine="python", on_bad_lines='skip'))
        except UnicodeDecodeError:
            dfs.append(pd.read_csv(f, encoding="cp1250", sep=None, engine="python", on_bad_lines='skip'))
    else:
        # xls/xlsx
        try:
            dfs.append(pd.read_excel(f, engine="openpyxl"))
        except Exception:
            # fallback without specifying engine
            dfs.append(pd.read_excel(f))

df = pd.concat(dfs, ignore_index=True)

# --- próbuj automatycznie wyliczyć brakujące kolumny ---
def try_compute_columns(df):
    df = df.copy()

    # 1) spróbuj znaleźć kolumnę daty i utworzyć 'Tydzień' i 'Miesiąc'
    date_candidates = [c for c in df.columns if 'date' in c.lower() or 'data' in c.lower()]
    if date_candidates:
        date_col = date_candidates[0]
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        if 'Tydzień' not in df.columns:
            df['Tydzień'] = df[date_col].dt.isocalendar().week
        if 'Miesiąc' not in df.columns:
            # zapisujemy w formacie YYYY-MM dla czytelności
            df['Miesiąc'] = df[date_col].dt.to_period('M').astype(str)

    # 2) spróbuj znaleźć parę start/end lub kolumnę czasu trwania
    start_col = next((c for c in df.columns if 'start' in c.lower()), None)
    end_col = next((c for c in df.columns if 'end' in c.lower()), None)
    duration_col = next((c for c in df.columns if 'czas' in c.lower() or 'duration' in c.lower()), None)

    if start_col and end_col:
        # oblicz dostępność w godzinach
        df[start_col] = pd.to_datetime(df[start_col], errors='coerce')
        df[end_col] = pd.to_datetime(df[end_col], errors='coerce')
        if 'Dostępność/h' not in df.columns:
            df['Dostępność/h'] = (df[end_col] - df[start_col]).dt.total_seconds() / 3600

    # 3) jeśli jest kolumna typu 'Czas pracy' lub 'czas', spróbuj skonwertować na godziny -> Obciążenie/h
    if duration_col and 'Obciążenie/h' not in df.columns:
        try:
            # obsługa formatów hh:mm:ss lub hh:mm
            td = pd.to_timedelta(df[duration_col])
            df['Obciążenie/h'] = td.dt.total_seconds() / 3600
        except Exception:
            # jeśli nie da się, próbujemy liczbowo
            try:
                df['Obciążenie/h'] = pd.to_numeric(df[duration_col], errors='coerce')
            except Exception:
                pass

    # 4) jeśli są kolumny nazwane w różnych wariantach, spróbuj prostego dopasowania
    # (np. 'Available', 'Available hours' -> 'Dostępność/h', 'Load' -> 'Obciążenie/h')
    col_lower = {c.lower(): c for c in df.columns}
    if 'dostępność' not in (c.lower() for c in df.columns):
        for key in ['available', 'available hours', 'available_hours', 'planowane', 'planowane godz']:
            if key in col_lower and 'Dostępność/h' not in df.columns:
                df['Dostępność/h'] = pd.to_numeric(df[col_lower[key]], errors='coerce')

    if 'obciążenie' not in (c.lower() for c in df.columns):
        for key in ['load', 'work hours', 'work_hours', 'obciazenie', 'czas pracy']:
            if key in col_lower and 'Obciążenie/h' not in df.columns:
                df['Obciążenie/h'] = pd.to_numeric(df[col_lower[key]], errors='coerce')

    # 5) oblicz 'Brakujące Godziny' jeśli mamy Dostępność i Obciążenie
    if 'Brakujące Godziny' not in df.columns and 'Dostępność/h' in df.columns and 'Obciążenie/h' in df.columns:
        df['Brakujące Godziny'] = (df['Dostępność/h'] - df['Obciążenie/h']).clip(lower=0)

    return df

# użycie:
df = try_compute_columns(df)
# -----------------------------------------------------------

# ----------------- FILTRY / MAPOWANIE KOLUMN -----------------
st.sidebar.header("Filtry / mapowanie kolumn")

# pokaż dostępne kolumny i pozwól użytkownikowi zmapować oczekiwane nazwy
expected_cols = [
    "Dział",
    "Nazwa Urządzenia",
    "Dostępność/h",
    "Obciążenie/h",
    "Brakujące Godziny",
    "Tydzień",
    "Miesiąc",
    "Numer części",
]

cols = list(df.columns)
st.sidebar.markdown("**Kolumny wykryte w danych:**")
st.sidebar.write(cols)

# tworzymy mapowanie: oczekiwana_nazwa -> wybrana kolumna z pliku
mapping = {}
for col in expected_cols:
    default_index = 0
    # jeśli nazwa oczekiwana występuje dokładnie, ustaw jako domyślną
    options = ["-- brak --"] + cols
    if col in cols:
        default_index = options.index(col)
    sel = st.sidebar.selectbox(f"Kolumna dla '{col}'", options, index=default_index)
    mapping[col] = None if sel == "-- brak --" else sel

# sprawdź czy wszystkie wymagane kolumny zostały zmapowane
missing = [k for k, v in mapping.items() if v is None]
if missing:
    st.error(f"Brakuje mapowania dla kolumn: {missing}. Wybierz odpowiednie kolumny po lewej.")
    st.stop()

# Zmieniamy nazwy kolumn na standardowe używane dalej w aplikacji
df = df.rename(columns={v: k for k, v in mapping.items()})

# teraz filtry - korzystamy ze zmapowanych, standaryzowanych nazw
dzial = st.sidebar.multiselect("Dział", df["Dział"].unique())
urz = st.sidebar.multiselect("Urządzenie", df["Nazwa Urządzenia"].unique())
mies = st.sidebar.multiselect("Miesiąc", df["Miesiąc"].unique())
tydz = st.sidebar.multiselect("Tydzień", df["Tydzień"].unique())

df_f = df.copy()
if dzial:
    df_f = df_f[df_f["Dział"].isin(dzial)]
if urz:
    df_f = df_f[df_f["Nazwa Urządzenia"].isin(urz)]
if mies:
    df_f = df_f[df_f["Miesiąc"].isin(mies)]
if tydz:
    df_f = df_f[df_f["Tydzień"].isin(tydz)]

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
