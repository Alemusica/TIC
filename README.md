# TIC — Tessuto Interconnesso Computante

**Tissular Interconnected Code** — Safe algebra for LLM-generated code.

> "Un mattone resta sempre un mattone. Lo togli di lì, lo metti di là. Sempre mattoni sono."

## Cos'è TIC?

TIC è un **metalinguaggio** che definisce un'algebra sicura per la generazione di codice da LLM.

**Il problema:**
```typescript
// LLM genera codice tradizionale
function processData(data) {
  // Può fare QUALSIASI COSA:
  fetch('http://evil.com')     // network I/O
  fs.writeFile('/etc/passwd')  // filesystem
  eval(userInput)              // arbitrary code execution
}
```

**La soluzione TIC:**
```python
# LLM genera SOLO da algebra TIC
cell processData = componi.sequenza(
    elemento.legge('data'),
    contenitore.mappa(trasforma),
    effetto.emetti('result')  # Runtime controlla!
)
```

L'LLM **non può** generare `eval`, `fetch`, `os.system` — non esistono nell'algebra.

## Architettura 4 Layer

```
┌─────────────────────────────────────┐
│ LAYER 1: USER                       │
│ "Aggiungi feature X"                │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ LAYER 2: LLM                        │
│ Genera codice TIC-compliant         │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ LAYER 3: ALGEBRA TIC                │
│ Solo primitivi puri permessi        │
│ NO: eval, exec, I/O diretto         │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ LAYER 4: RUNTIME                    │
│ Esegue in sandbox, audit trail      │
└─────────────────────────────────────┘
```

## Quick Start

```python
from tic_core.archetipi import elemento, contenitore, confronta, valore, flusso

# Crea un elemento (puro, immutabile)
prodotto = elemento.crea({
    'nome': 'Widget',
    'prezzo': 10.00,
    'quantita': 5
})

# Composizione funzionale
calcola_totale = flusso.sequenza(
    lambda items: contenitore.mappa(items, lambda i: elemento.legge(i, 'prezzo')),
    valore.somma
)

# Pattern matching
gestisci_stato = flusso.scegli(stato, [
    ('pending', lambda x: processa),
    ('done', lambda x: archivia),
    ('_', lambda x: ignora)
])
```

## Algebra Base

### Primitivi Puri (Layer 3)

```
ELEMENTO      → crea, legge, scrive, elimina
CONTENITORE   → mappa, filtra, riduce, trova, ordina
CONFRONTA     → uguale, maggiore, tra, nullo, tutti
VALORE        → incrementa, somma, media, clamp
TESTO         → pulisce, contiene, divide, unisce
FLUSSO        → se, scegli, componi, sequenza, ripeti (BOUNDED!)
```

### Effetti (Boundary - Runtime controlla)

```
effetto.emetti   → emit event (runtime intercepts)
effetto.leggi    → read from source (runtime provides)
effetto.scrivi   → write to sink (runtime controls)
```

Gli effetti **non eseguono nulla**. Creano descrizioni che il Runtime decide se permettere.

## I 4 Livelli di Codice

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

## Proprietà Garantite

L'algebra TIC garantisce matematicamente:

| Proprietà | Significato |
|-----------|-------------|
| **Purezza** | Stessa input → stessa output |
| **Terminazione** | No loop infiniti (`ripeti` è bounded) |
| **Immutabilità** | Operazioni non modificano input |
| **Chiusura** | Composizione produce sempre celle valide |
| **Sicurezza** | No eval, exec, I/O diretto |

## Proprietà Emergenti

Dal design TIC emergono **gratis** capacità che normalmente richiedono implementazione esplicita:

| Constraint TIC | Emergenza |
|----------------|-----------|
| **Immutabilità** | UNDO/REDO triviale — ogni stato è snapshot |
| **Purezza** | Testing triviale — f(x) sempre = f(x) |
| **Effetti boundary** | Audit trail gratis — ogni I/O è intercettato |
| **Naming semantico** | Documentazione gratis — il codice si legge |
| **Propagazione** | Reactive gratis — dipendenze auto-tracked |
| **Terminazione** | No deadlock — tutto finisce |

```python
# Esempio: UNDO/REDO emergente dall'immutabilità
history = []

def azione(stato, operazione):
    nuovo_stato = operazione(stato)  # Immutabile: stato originale intatto
    history.append(stato)            # Snapshot automatico
    return nuovo_stato

def undo():
    return history.pop() if history else None

# Funziona GRATIS perché le operazioni TIC non modificano mai l'input
```

> "Non aggiungi feature. Le scopri." — Filosofia TIC

## Esempi

```bash
# Ristorante
cd examples/ristorante && python main.py

# E-Commerce con effetti
cd examples/ecommerce && python main.py
```

## Test & Benchmark

```bash
# Unit tests (55 test)
pytest tests/ -v

# Proprietà algebra (26 test)
pytest benchmarks/test_algebra_properties.py -v

# Scenari LLM (18 test)
pytest benchmarks/test_llm_scenarios.py -v

# Performance benchmark
pytest benchmarks/test_performance.py --benchmark-autosave
```

## Struttura

```
TIC/
├── tic_core/
│   ├── archetipi/      # Primitivi algebra
│   ├── propagazione/   # Sistema reattivo
│   └── biocache/       # Memoria 3 livelli
├── examples/
│   ├── ristorante/
│   └── ecommerce/
├── benchmarks/         # Performance + validazione
├── spec/               # Specifiche formali
└── tests/
```

## Roadmap

```
[x] FASE 1: POC Python
[ ] FASE 2: Linter/Validator TIC
[ ] FASE 3: Runtime ottimizzato
[ ] FASE 4: Linguaggio nativo + benchmark LLM
```

## Filosofia

```
TIC non è una nuova arte marziale.
È il Jeet Kune Do del codice.

Prendi le mosse migliori da ogni stile.
Usa con efficienza massima.

Un seme di sesamo contiene l'universo intero.
```

---

**Versione:** 0.1.0
**Autori:** Flutur (ideatore), Claude (executor)
**Licenza:** MIT
