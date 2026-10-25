# VicinoCasa V1 — demo

Demo Flask responsive per mostrare il concept a professionisti locali.

## Include
- vetrina con filtro per categoria e zona
- schede professionista
- chat dimostrativa
- area artigiano demo per cambiare il semaforo

## Limiti importanti
- i profili sono inventati e dimostrativi
- messaggi e stati sono conservati solo in RAM e si azzerano al riavvio
- non ci sono login, privacy/account reali, database, pagamenti, notifiche o invio di messaggi a persone reali
- non usare dati reali né presentare i profili di esempio come professionisti già aderenti

## Avvio locale
```bash
pip install -r requirements.txt
python app.py
```
Apri http://127.0.0.1:5000

## Pubblicazione su Render
Carica `app.py`, `requirements.txt` e `render.yaml` in un nuovo repository GitHub. Crea un Web Service su Render collegato al repository; il comando di avvio è `gunicorn app:app`. Imposta `SECRET_KEY` come variabile d'ambiente se non usi il file render.yaml.
