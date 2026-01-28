# TIC Mini — Context for LLM

## Algebra (ONLY these primitives allowed)

```
elemento:    crea legge scrive elimina
contenitore: mappa filtra riduce trova primo conta vuoto
confronta:   uguale maggiore minore tra nullo vero tutti
valore:      incrementa decrementa moltiplica divide somma
testo:       pulisce contiene divide unisce vuoto
flusso:      se scegli componi sequenza ripeti(BOUNDED)
effetto:     emetti leggi scrivi log fallisce (RUNTIME CONTROLS)
```

## NOT Allowed
```
❌ eval exec open import os subprocess getattr while(True)
```

## Levels
```
L1 ARCHETIPI  → elemento.crea, contenitore.filtra
L2 MOLECOLE   → prodotto.sotto.soglia
L3 ORGANISMI  → ordine.processa
```

## Naming
```
soggetto.verbo.oggetto → readable phrase
```

## Pattern
```python
# REGOLA
def regola_valida(x):
    return confronta.maggiore(elemento.legge(x, 'val'), 0)

# QUERY
def query_validi(lista):
    return contenitore.filtra(lista, regola_valida)

# EFFETTO (runtime decides)
effetto.emetti('evento', dati)
```

## Generate code using ONLY these primitives.
