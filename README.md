# PTI — Paradigma Tissutale Interconnesso

> "Un mattone resta sempre un mattone. Lo togli di lì, lo metti di là. Sempre mattoni sono."

## Cos'è PTI?

PTI è un **meta-paradigma** di programmazione che riconosce un fatto semplice:

**Il 90% del codice è ridondanza mascherata.**

```python
# Queste sembrano funzioni diverse...
def validate_user_email(user):
    return "@" in user.email

def validate_product_sku(product):
    return len(product.sku) == 8

def validate_order_total(order):
    return order.total > 0

# ...ma sono tutte la stessa operazione: verifica.formato
```

PTI non inventa nulla. Riconosce pattern esistenti e li applica sistematicamente:

| Fonte | Cosa prende |
|-------|-------------|
| Prolog | naming = logica |
| Database | normalizzazione, no duplicazione |
| Funzionale | purity, composizione |
| Reactive | propagazione automatica |
| Biologico | tessuti, gerarchia, memoria |

## Quick Start

```python
from pti_core.archetipi import elemento, contenitore, confronta, valore

# Crea un elemento
prodotto = elemento.crea({
    'nome': 'Widget',
    'prezzo': 10.00,
    'quantita': 5
})

# Leggi attributi
nome = elemento.legge(prodotto, 'nome')  # 'Widget'

# Operazioni immutabili
prodotto2 = elemento.scrive(prodotto, 'quantita', 10)

# Contenitori
prodotti = contenitore.crea([prodotto, prodotto2])
economici = contenitore.filtra(prodotti, lambda p: elemento.legge(p, 'prezzo') < 20)

# Confronti semantici
sotto_soglia = confronta.sotto(elemento.legge(prodotto, 'quantita'), 3)
```

## I 4 Livelli

```
LIVELLO 1: ARCHETIPI
  └── Funzioni pure universali
  └── elemento.crea, contenitore.filtra, valore.incrementa

LIVELLO 2: MOLECOLE
  └── Regole dominio-specifiche
  └── prodotto.sotto.soglia, prenotazione.valida

LIVELLO 3: ORGANISMI
  └── Flow completi, entry point
  └── ordine.processa, ristorante.prenota

LIVELLO 4: SISTEMI
  └── Insiemi cooperanti
  └── server.http, auth.sistema
```

**Regola ferrea**: Livello N usa **solo** livello N-1 o inferiore.

## Naming Semantico

Il nome **è** la documentazione:

```
soggetto.verbo              → "il testo si pulisce"
soggetto.verbo.oggetto      → "il contenitore aggiunge l'elemento"
soggetto.stato              → "il prodotto è disponibile"
```

Se non sai come chiamarla, non sai cosa fa.

## Propagazione

Le variabili non sono isolate. Sono **cellule in un tessuto**:

```python
from pti_core.propagazione import Tessuto, fatto, derivato

tessuto = Tessuto()

# Fatto base
tessuto.imposta('tavolo.1.stato', 'libero')
tessuto.imposta('tavolo.2.stato', 'occupato')

# Fatto derivato (si aggiorna automaticamente)
@tessuto.derivato('tavoli.liberi', dipende_da=['tavolo.*.stato'])
def calcola():
    return [t for t in tavoli if t.stato == 'libero']

# Quando tavolo.1.stato cambia → tavoli.liberi si aggiorna
tessuto.imposta('tavolo.1.stato', 'occupato')
# tavoli.liberi è già aggiornato, O(1)
```

## BiocCache (Memoria)

Tre livelli di permanenza:

```
LTM (Long Term) → Archetipi, mai rimosso
MTM (Medium Term) → Pattern frequenti
STM (Short Term) → Ring buffer, temporaneo
```

Promozione automatica basata su frequenza d'uso.

## Struttura Progetto

```
PTI/
├── pti_core/
│   ├── archetipi/      # Livello 1
│   │   ├── elemento.py
│   │   ├── contenitore.py
│   │   ├── confronta.py
│   │   ├── valore.py
│   │   └── testo.py
│   ├── propagazione/   # Sistema reattivo
│   │   └── tessuto.py
│   └── biocache/       # Memoria
│       └── cache.py
├── examples/
│   └── ristorante/     # Demo completa
├── spec/               # Specifiche formali
├── tools/              # Linter, analyzer
└── tests/
```

## Esempio: Ristorante

```bash
cd examples/ristorante
python main.py
```

Output:
```
PTI DEMO: Sistema Prenotazione Ristorante
=========================================

1. Creazione ristorante...
   ✓ Ristorante 'Trattoria Da Mario' creato con 5 tavoli

2. Stato iniziale:
   Tavoli liberi:        5/5
   Capienza disponibile: 22 posti

3. Prima prenotazione: Mario Rossi, 4 persone, ore 20:00
   ✓ Prenotazione confermata per Mario Rossi, tavolo T1

...
```

## Roadmap

```
[x] FASE 1: POC Python - proof of concept
[ ] FASE 2: Tool/Linter - enforcing convenzioni
[ ] FASE 3: Runtime ottimizzato
[ ] FASE 4: Linguaggio nativo con benchmark
```

## Filosofia

```
PTI non è una nuova arte marziale.
È il Jeet Kune Do del codice.

Prendi le mosse migliori da ogni stile.
Usa con efficienza massima.

Un seme di sesamo contiene l'universo intero.
```

---

**Versione:** 0.1.0
**Autori:** Flutur (ideatore), Claude (executor)
