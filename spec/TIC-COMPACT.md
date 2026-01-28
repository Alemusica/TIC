# TIC — Tessuto Interconnesso Computante (Compact)

> Safe algebra for LLM-generated code.

---

## Architettura 4 Layer

```
USER → LLM → ALGEBRA → RUNTIME
         │
         └─► LLM genera SOLO da algebra
             Runtime esegue in sandbox + audit
```

---

## Algebra TIC (Layer 3)

### Primitivi Puri (sempre permessi)

```
ELEMENTO      crea legge scrive elimina clona
CONTENITORE   crea aggiunge rimuove mappa filtra riduce trova primo ultimo conta vuoto ordina
CONFRONTA     uguale diverso maggiore minore almeno alpiù tra nullo vero falso tutti in_lista
VALORE        incrementa decrementa moltiplica divide somma media minimo massimo clamp
TESTO         pulisce maiuscolo minuscolo contiene inizia finisce divide unisce vuoto tronca
FLUSSO        se scegli componi sequenza parallelo identita costante ripeti(BOUNDED!)
```

### Effetti (Boundary - Runtime controlla)

```
effetto.emetti(evento, dati)     → emit event
effetto.leggi(sorgente, query)   → read from source
effetto.scrivi(dest, dati)       → write to sink
effetto.log(livello, msg)        → logging
effetto.fallisce(motivo)         → controlled failure
```

**Gli effetti NON eseguono nulla** — creano descrizioni che il Runtime decide se permettere.

### NON Esiste nell'Algebra

```
❌ eval  exec  open  import  __import__
❌ os  subprocess  socket  requests
❌ getattr  setattr  globals  locals
❌ while True  (ripeti è BOUNDED)
```

---

## Assiomi

```
1. IDENTITÀ    Stesso nome = stessa cosa
2. GERARCHIA   Grafo = albero con ripetizioni numerate
3. PROPAGAZIONE Cambiamento → propaga a connessi con pesi
4. PUREZZA     Celle sono deterministiche, no side effects
5. TERMINAZIONE Tutto termina (ripeti ha limite)
```

---

## 4 Livelli di Codice

```
L1 ARCHETIPI  → primitive pure universali
               elemento.crea  contenitore.filtra  valore.incrementa

L2 MOLECOLE   → regole dominio-specifiche
               prodotto.sotto.soglia  prenotazione.valida

L3 ORGANISMI  → flow completi, entry point
               ordine.processa  ristorante.prenota

L4 SISTEMI    → insiemi cooperanti
               server.http  auth.sistema
```

**Regola**: Livello N usa SOLO livello N-1 o inferiore.

---

## Naming

```
soggetto.verbo              → "il testo si pulisce"
soggetto.verbo.oggetto      → "il contenitore aggiunge l'elemento"
soggetto.stato              → "il prodotto è disponibile"
```

**Se non sai come chiamarla, non sai cosa fa.**

---

## Pattern

```python
# FATTO (dato base)
fatto_soglia = 5

# REGOLA (predicato)
def regola_sotto_soglia(p):
    return confronta.sotto(elemento.legge(p, 'qty'), fatto_soglia)

# QUERY (derivato)
def query_da_riordinare(magazzino):
    return contenitore.filtra(magazzino, regola_sotto_soglia)

# CELLA CON EFFETTO (boundary)
def cella_notifica_riordino(prodotto):
    return effetto.emetti('prodotto.sotto.soglia', {
        'sku': elemento.legge(prodotto, 'sku')
    })
```

---

## LLM Workflow

```
1. ARCHETIPI   → scegli primitive necessarie
2. FATTI       → definisci dati/costanti
3. MOLECOLE    → componi regole dominio
4. ORGANISMI   → assembla flow completo
5. EFFETTI     → aggiungi boundary I/O (runtime controlla)
```

---

## Esempio Completo

```python
# Task: "Calcola totale carrello con sconto e notifica"

# L1: usa archetipi
from tic_core.archetipi import elemento, contenitore, valore, flusso, effetto

# L2: molecola calcolo
def calcola_subtotale(item):
    return valore.moltiplica(
        elemento.legge(item, 'qty'),
        elemento.legge(item, 'prezzo')
    )

def calcola_totale(carrello):
    items = elemento.legge(carrello, 'items')
    subtotali = contenitore.mappa(items, calcola_subtotale)
    return valore.somma(subtotali)

# L2: molecola sconto
def applica_sconto(totale, percentuale):
    sconto = valore.moltiplica(totale, valore.divide(percentuale, 100))
    return valore.decrementa(totale, sconto)

# L3: organismo checkout
def checkout(carrello, sconto_pct):
    totale = calcola_totale(carrello)
    finale = applica_sconto(totale, sconto_pct)

    # Effetti al boundary
    return (finale, [
        effetto.emetti('checkout.completato', {'totale': finale}),
        effetto.log('info', f'Checkout: €{finale}')
    ])
```

---

## Proprietà Garantite

| Proprietà | Significato |
|-----------|-------------|
| Purezza | f(x) = f(x) sempre |
| Terminazione | No loop infiniti |
| Immutabilità | Input non modificato |
| Sicurezza | No eval/exec/I/O diretto |
| Auditabilità | Ogni effetto loggato |

---

## Sintesi

```
TIC = Algebra sicura + Runtime controllato

L'LLM genera SOLO da primitivi algebra.
Il Runtime decide quali effetti permettere.
Audit trail di tutto.

Constraint nell'algebra, non nelle permission.
```
