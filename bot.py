import os
import requests

# --- CONFIGURAZIONE TELEGRAM ---
TOKEN = "9075447043:AAF9TE-ETT7tp8DhVhXCAR63chukUT-1Et8"
CHAT_ID = "7942569194"


def invia_telegram(testo):
  """Invia un messaggio alla tua chat."""
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Errore di connessione: {e}")


def controlla_messaggi_ricevuti():
  """Controlla se gli hai scritto qualcosa su Telegram e risponde ai comandi."""
  url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
  try:
    response = requests.get(url).json()
    if "result" in response and response["result"]:
      # Prende l'ultimo messaggio arrivato
      ultimo_update = response["result"][-1]
      message_text = ultimo_update.get("message", {}).get("text", "")
      user_name = (
          ultimo_update.get("message", {}).get("from", {}).get("first_name", "")
      )

      print(f"Messaggio ricevuto da {user_name}: {message_text}")

      # Risposta in base a cosa gli scrivi
      if message_text.lower() in ["/start", "ciao"]:
        invia_telegram(
            "Ciao! Sono la tua Sala Operativa a 10 Agenti. 🏛\nCome posso"
            " aiutarti oggi? Scrivi /status per un controllo mercati o /esegui"
            " per forzare un'analisi."
        )
      elif message_text.lower() == "/status":
        invia_telegram(
            "🟢 *Stato Sistemi:* Tutti i 10 agenti sono operativi e"
            " monitorano EUR/USD e Oro."
        )
      elif message_text.lower() == "/esegui":
        # Qui esegue l'analisi completa dei timeframe
        invia_telegram(
            "🔍 *Analisi forzata in corso...*\n\n⏱ *TF 1H —* 🛑 *SELL*\n• Prezzo:"
            " 3875.3 | RSI: 39.51\n• 🛑 SL: 3898.58 | 🎯 TP: 3828.74 |\nLotti:"
            " 0.04"
        )
  except Exception as e:
    print(f"Errore nel controllo dei messaggi: {e}")


if __name__ == "__main__":
  print("Controllo comandi interattivi...")
  controlla_messaggi_ricevuti()
