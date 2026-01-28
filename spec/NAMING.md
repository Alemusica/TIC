# PTI Naming Specification v1.0

## Principio Fondamentale

> **Il nome È la struttura. Il nome È la documentazione.**

Se due cose hanno lo stesso nome, **sono** la stessa cosa.
Se hanno nomi diversi, **sono** cose diverse.

## Sintassi

### Pattern Base

```
<soggetto>.<verbo>                    → azione su soggetto
<soggetto>.<verbo>.<oggetto>          → azione con target
<soggetto>.<attributo>                → proprietà
<soggetto>.<attributo>.<qualificatore> → proprietà qualificata
```

### Esempi

```
testo.pulisce                   → "il testo si pulisce"
contenitore.aggiunge.elemento   → "il contenitore aggiunge l'elemento"
prodotto.disponibile            → "il prodotto è disponibile"
utente.email.valida             → "l'email dell'utente è valida"
```

### Separatore

Usa `.` (punto) come separatore gerarchico.

```
✓ tavolo.stato.libero
✗ tavolo_stato_libero
✗ tavoloStatoLibero
✗ tavolo-stato-libero
```

## Convenzioni per Livello

### Livello 1: Archetipi

Nomi **generici e universali**. Nessun riferimento a dominio specifico.

```
✓ valore.incrementa
✓ elemento.crea
✓ contenitore.filtra
✓ confronta.uguale

✗ prezzo.incrementa       (troppo specifico)
✗ utente.crea             (dominio-specifico)
```

### Livello 2: Molecole

Nomi **dominio-specifici**. Composti da archetipi.

```
✓ prodotto.sotto.soglia
✓ prenotazione.valida
✓ tavolo.libero
✓ ordine.totale.calcola

✗ validateProductThreshold    (non leggibile)
```

### Livello 3: Organismi

Nomi che indicano **flow completi**. Entry point.

```
✓ ristorante.prenota
✓ ordine.processa
✓ utente.registra
✓ pagamento.esegue

✗ handleReservation          (verbo non chiaro)
```

### Livello 4: Sistemi

Nomi che indicano **insiemi cooperanti**.

```
✓ server.http
✓ auth.sistema
✓ notifiche.servizio
```

## Verbi Raccomandati

### Azioni su Elementi

| Verbo | Significato | Esempio |
|-------|-------------|---------|
| crea | istanzia nuovo | `elemento.crea` |
| legge | ottiene valore | `elemento.legge` |
| scrive | imposta valore | `elemento.scrive` |
| elimina | rimuove | `elemento.elimina` |
| clona | copia profonda | `elemento.clona` |

### Azioni su Contenitori

| Verbo | Significato | Esempio |
|-------|-------------|---------|
| aggiunge | append | `contenitore.aggiunge` |
| rimuove | remove | `contenitore.rimuove` |
| filtra | filter | `contenitore.filtra` |
| mappa | map | `contenitore.mappa` |
| riduce | reduce | `contenitore.riduce` |
| ordina | sort | `contenitore.ordina` |
| trova | find first | `contenitore.trova` |

### Azioni di Stato

| Verbo | Significato | Esempio |
|-------|-------------|---------|
| verifica | check boolean | `email.verifica.formato` |
| valida | validation completa | `prenotazione.valida` |
| calcola | compute | `ordine.totale.calcola` |
| propaga | propagate change | `stato.propaga` |

### Azioni di Flow

| Verbo | Significato | Esempio |
|-------|-------------|---------|
| processa | process flow | `ordine.processa` |
| prenota | reserve | `tavolo.prenota` |
| esegue | execute | `pagamento.esegue` |
| annulla | cancel | `prenotazione.annulla` |
| conferma | confirm | `ordine.conferma` |

## Query (Fatti Derivati)

Le query usano prefisso `query_` o notazione `?-`:

```python
# Funzione
def query_tavoli_liberi(ristorante):
    ...

# Commento Prolog-style
"""?- tavoli.liberi"""
```

## Anti-Pattern

### ❌ Nomi Non Semantici

```
✗ f(x)
✗ doStuff()
✗ tmp
✗ data
✗ result
```

### ❌ Nomi Troppo Lunghi

```
✗ validateUserEmailInputAndSendConfirmation
✗ processOrderAndUpdateInventoryAndNotifyCustomer
```

Spezza in funzioni atomiche:

```
✓ email.valida
✓ conferma.invia
✓ ordine.processa
✓ inventario.aggiorna
✓ cliente.notifica
```

### ❌ Verbi Vaghi

```
✗ handle
✗ manage
✗ process (se generico)
✗ do
✗ perform
```

### ❌ Notazione Mista

```
✗ get_user_Email        (underscore + camel)
✗ tavolo.GetStato       (punto + camel)
✗ TAVOLO.stato          (CAPS inconsistente)
```

## Regole di Unicità

### Stesso Nome = Stessa Cosa

```python
# Queste DEVONO essere la stessa implementazione
contenitore.aggiunge.elemento(cart, item)
contenitore.aggiunge.elemento(gruppo, utente)
contenitore.aggiunge.elemento(categoria, prodotto)
```

### Diverso Nome = Diversa Cosa

```python
# Se fanno cose diverse, nomi diversi
lista.accoda(item)      # append in fondo
lista.inserisce(item)   # insert in posizione
```

## Gerarchia nel Nome

Il nome riflette la gerarchia:

```
ristorante
├── ristorante.tavoli
│   ├── ristorante.tavoli.liberi
│   └── ristorante.tavoli.occupati
├── ristorante.prenota
└── ristorante.stato
```

## Istanze Multiple

Per istanze multiple, usa indice numerico:

```
tavolo.1.stato
tavolo.2.stato
loop.iterazione.1
loop.iterazione.2
```

## Internazionalizzazione

Scegli **una lingua** e mantienila consistente.

```
# Italiano (questo progetto)
contenitore.aggiunge
elemento.crea

# Inglese
container.adds
element.creates
```

Non mescolare:

```
✗ contenitore.add
✗ element.crea
```

## Validazione (Tool Futuro)

```bash
pti-lint check src/
```

Regole da verificare:
- [ ] Solo caratteri `[a-z0-9.]`
- [ ] Nessun underscore o camelCase
- [ ] Verbi dalla lista approvata
- [ ] Livello coerente con posizione file
- [ ] Nessun nome duplicato con implementazione diversa

---

**Versione:** 1.0
**Status:** Draft
