import requests
import time

# --- CONFIGURAZIONE MESSENGER ---
TOKEN = "9075447043:AAF9TE-ETT7tp8DhVHXcAR63chukUT-1Et8"
CHAT_ID = "7942569194"

CAPITALE = 1000.0
RISCHIO_PERCENTUALE = 1.0
ASSETS = {
    "EURUSD=X": "EUR/USD",
    "GC=F": "Oro"
}
TIMEFRAMES = ["1h", "30m", "15m", "5m"]

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": messaggio, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Errore Telegram: {e}")

# --- AGENTE 1: DATI REALI ---
def ottieni_candele(simbolo, timeframe):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}?interval={timeframe}&range=5d"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        risposta = requests.get(url, headers=headers, timeout=10).json()
        quote = risposta['chart']['result'][0]['indicators']['quote'][0]
        candele = []
        for h, l, c, v in zip(quote['high'], quote['low'], quote['close'], quote['volume']):
            if h is not None and l is not None and c is not None:
                candele.append({"high": h, "low": l, "close": c, "volume": v if v else 0})
        return candele
    except Exception:
        return []

# --- AGENTE 2: TREND (SMA 20 + Teoria di Dow) ---
def calcola_sma(candele, periodo=20):
    if len(candele) < periodo:
        return None
    chiusure = [c["close"] for c in candele[-periodo:]]
    return sum(chiusure) / periodo

def conferma_teoria_dow(candele):
    if len(candele) < 5:
        return "NEUTRO"
    ultimi_massimi = [c["high"] for c in candele[-5:]]
    ultimi_minimi = [c["low"] for c in candele[-5:]]
    if ultimi_massimi[-1] > ultimi_massimi[-3] and ultimi_minimi[-1] > ultimi_minimi[-3]:
        return "TREND_RIALZISTA"
    elif ultimi_massimi[-1] < ultimi_massimi[-3] and ultimi_minimi[-1] < ultimi_minimi[-3]:
        return "TREND_RIBASSISTA"
    return "LATERALE"

# --- AGENTE 3: MOMENTUM (RSI 14) ---
def calcola_rsi(candele, periodo=14):
    if len(candele) < periodo + 1:
        return 50.0
    chiusure = [c["close"] for c in candele]
    delta = [chiusure[i] - chiusure[i-1] for i in range(1, len(chiusure))]
    guadagni = [d if d > 0 else 0 for d in delta[-periodo:]]
    perdite = [-d if d < 0 else 0 for d in delta[-periodo:]]
    media_g = sum(guadagni) / periodo
    media_p = sum(perdite) / periodo
    if media_p == 0:
        return 100.0
    rs = media_g / media_p
    return round(100 - (100 / (1 + rs)), 2)

# --- AGENTE 4: RISK MANAGEMENT & MURPHY ---
def calcola_livelli_murphy(candele, direzione, simbolo):
    if len(candele) < 15:
        return None
    tr_list = []
    for i in range(1, len(candele)):
        high = candele[i]["high"]
        low = candele[i]["low"]
        prev_close = candele[i-1]["close"]
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        tr_list.append(tr)
    atr = sum(tr_list[-14:]) / 14
    prezzo = candele[-1]["close"]
    
    distanza_sl = atr * 1.5
    distanza_tp = atr * 3.0
    
    if direzione == "LONG":
        sl = prezzo - distanza_sl
        tp = prezzo + distanza_tp
    else:
        sl = prezzo + distanza_sl
        tp = prezzo - distanza_tp
        
    rischio_euro = CAPITALE * (RISCHIO_PERCENTUALE / 100.0)
    if simbolo == "EURUSD=X":
        decimali, valore_pip, pips_sl = 5, 10.0, distanza_sl * 10000
    else:
        decimali, valore_pip, pips_sl = 2, 1.0, distanza_sl * 10
        
    lotti = round(rischio_euro / (pips_sl * valore_pip), 2) if pips_sl > 0 else 0.01
    return {"prezzo": round(prezzo, decimali), "sl": round(sl, decimali), "tp": round(tp, decimali), "lotti": max(0.01, lotti)}

# --- AGENTE 5 & 6: VOLUMI & FIBONACCI ---
def analizza_volumi(candele):
    if len(candele) < 5:
        return False
    volumi_recenti = [c["volume"] for c in candele[-5:]]
    media_volumi = sum(volumi_recenti) / len(volumi_recenti)
    return candele[-1]["volume"] > media_volumi * 1.2

def check_fibonacci_salute(candele, direzione):
    if len(candele) < 10:
        return True
    recente_high = max([c["high"] for c in candele[-10:]])
    recente_low = min([c["low"] for c in candele[-10:]])
    range_totale = recente_high - recente_low
    prezzo_attuale = candele[-1]["close"]
    if range_totale == 0:
        return True
    if direzione == "LONG":
        ritracciamento = (recente_high - prezzo_attuale) / range_totale
        return 0.15 <= ritracciamento <= 0.85
    else:
        ritracciamento = (prezzo_attuale - recente_low) / range_totale
        return 0.15 <= ritracciamento <= 0.85

# --- AGENTE 10: CALENDARIO MACRO / NEWS ---
def controllo_macro_news():
    return True  # True = Semaforo verde

# --- AGENTE SUPERIORE: MONITORAGGIO IN TEMPO REALE ---
def esegui_monitoraggio():
    print("⏳ Controllo dei mercati in corso...")
    
    if not controllo_macro_news():
        return

    for simbolo, nome in ASSETS.items():
        for tf in TIMEFRAMES:
            candele = ottieni_candele(simbolo, tf)
            if len(candele) < 25:
                continue
                
            prezzo = candele[-1]["close"]
            sma20 = calcola_sma(candele, 20)
            rsi = calcola_rsi(candele, 14)
            if sma20 is None:
                continue
                
            direzione_grezza = "LONG" if prezzo > sma20 else "SHORT"
            dow_status = conferma_teoria_dow(candele)
            volumi_ok = analizza_volumi(candele)
            fibo_ok = check_fibonacci_salute(candele, direzione_grezza)
            
            trend_confermato = (direzione_grezza == "LONG" and dow_status in ["TREND_RIALZISTA", "LATERALE"]) or \
                               (direzione_grezza == "SHORT" and dow_status in ["TREND_RIBASSISTA", "LATERALE"])
            
            if 30 <= rsi <= 70 and volumi_ok and trend_confermato and fibo_ok:
                azione = "🟢 **PRE-ALLARME LONG (BUY)**" if direzione_grezza == "LONG" else "🔴 **PRE-ALLARME SHORT (SELL)**"
                livelli = calcola_livelli_murphy(candele, direzione_grezza, simbolo)
                
                messaggio = (
                    f"⚡ **SALA OPERATIVA: SEGNALE IN TEMPO REALE** ⚡\n\n"
                    f"🪙 Asset: *{nome}*\n"
                    f"⏱ Timeframe: `{tf.upper()}`\n"
                    f"💡 Direzione: {azione}\n"
                    f"• Prezzo Rilevato: `{livelli['prezzo']}`\n"
                    f"• 🛑 Stop Loss: `{livelli['sl']}`\n"
                    f"• 🎯 Take Profit: `{livelli['tp']}`\n"
                    f"• ⚖️ Lotti Consigliati: `{livelli['lotti']}`\n"
                    f"🚀 *Il mercato sta prendendo questa direzione con volumi confermati!*"
                )
                invia_telegram(messaggio)
                print(f"Segnale inviato per {nome} su {tf}!")
                return

if __name__ == "__main__":
    print("🤖 Agente Superiore in ascolto continuo...")
    while True:
        try:
            esegui_monitoraggio()
        except Exception as e:
            print(f"Errore nel ciclo: {e}")
        
        # Pausa di 15 minuti tra un controllo e l'altro (900 secondi)
        time.sleep(900)
