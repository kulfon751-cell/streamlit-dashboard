# Obciążenie i dostępność urządzeń

Krótka instrukcja uruchomienia i użycia aplikacji Streamlit.

Wymagania:
- Python 3.10+ (virtualenv rekomendowane)
- Zainstalowane zależności: `pip install -r requirements.txt`

Uruchomienie lokalne:

```bash
/workspaces/streamlit-dashboard/.venv/bin/python -m streamlit run /workspaces/streamlit-dashboard/app.py
```

Jak korzystać:
- W sidebarze wgraj jeden lub więcej plików CSV/XLS/XLSX.
- Jeżeli Excel zawiera wiele arkuszy, aplikacja domyślnie wczyta wszystkie i doda kolumny `_source_file` i `_source_sheet`.
- W sidebarze przypisz kolumny z pliku do oczekiwanych pól (część mapowań jest wykonywana automatycznie).
- Jeśli `Brakujące Godziny` nie jest w pliku, aplikacja obliczy je jako max(0, Dostępność/h - Obciążenie/h).

Jeżeli chcesz, mogę rozbudować README o przykładowy format pliku i przykładowe dane.