# NutriSport

App web per tracciare l'alimentazione di uno sportivo: diario, piano alimentare,
ricette, lista della spesa, calendario e promemoria.

**Stack:** Python, FastAPI, SQLAlchemy, SQLite, Alembic, Jinja2, HTMX

*Work in progress.*

## Avvio

```bash
git clone git@github.com:feddde/nutrisport.git
cd nutrisport
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload
```

L'app è su http://127.0.0.1:8000 e la documentazione interattiva su `/docs`.

## Test

```bash
pytest -v
```

## Struttura
app/ # applicazione FastAPI (modelli, route, servizi, template)
migrations/ # migrazioni Alembic
scripts/ # script di utilità (seed alimenti)
data/ # dati di partenza (alimenti.csv)
tests/ # test pytest


## Funzionalità

- [x] Schema del database e migrazioni
- [x] Seed di 44 alimenti
- [x] Test dei modelli
- [x] Route `/health`
- [ ] CRUD alimenti e ricette
- [ ] Diario alimentare con totali di macro e kcal
- [ ] Piano settimanale con opzioni per pasto
- [ ] Lista della spesa generata dal piano
- [ ] Calendario settimanale
- [ ] Promemoria (export `.ics` e bot Telegram)
- [ ] CI con GitHub Actions
