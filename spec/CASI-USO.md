# TIC — Casi d'Uso Pratici

> Esempi reali che mostrano dove TIC aggiunge valore (e dove no).

---

## Caso 1: Selection Box (Canvas Editor)

**Contesto:** Implementare selezione rettangolare come in Paint, Keynote, Figma.

### Approccio Tradizionale

```javascript
// Stato mutabile ovunque
let selecting = false;
let startX, startY, endX, endY;
let selectedObjects = [];

canvas.onMouseDown = (e) => {
    selecting = true;
    startX = e.x; startY = e.y;
    selectedObjects = []; // MUTAZIONE
};

canvas.onMouseMove = (e) => {
    if (!selecting) return;
    endX = e.x; endY = e.y;
    redrawSelectionRect();
};

canvas.onMouseUp = (e) => {
    selecting = false;
    for (let obj of allObjects) {
        if (intersects(obj.bounds, selectionRect)) {
            selectedObjects.push(obj); // MUTAZIONE
            obj.selected = true;        // MUTAZIONE
        }
    }
};

// UNDO? Devi implementarlo manualmente
// Multi-criteria? Altro codice imperativo
// Selezione gerarchica? Ancora più codice
```

**Problemi:**
- Stato mutabile distribuito
- UNDO richiede snapshot manuale
- Selezione solo geometrica
- Multi-select con shift richiede altro codice

### Approccio TIC

```python
from tic_core.archetipi import elemento, contenitore, confronta, valore, flusso

# FATTO: area di selezione (puro)
def area_selezione(p1, p2):
    return elemento.crea({
        'x_min': valore.minimo(p1['x'], p2['x']),
        'y_min': valore.minimo(p1['y'], p2['y']),
        'x_max': valore.massimo(p1['x'], p2['x']),
        'y_max': valore.massimo(p1['y'], p2['y'])
    })

# REGOLA: elemento in area (pura)
def elemento_in_area(elem, area):
    bounds = elemento.legge(elem, 'bounds')
    centro_x = valore.media([elemento.legge(bounds, 'x1'), elemento.legge(bounds, 'x2')])
    centro_y = valore.media([elemento.legge(bounds, 'y1'), elemento.legge(bounds, 'y2')])

    return confronta.tutti([
        confronta.tra(centro_x, elemento.legge(area, 'x_min'), elemento.legge(area, 'x_max')),
        confronta.tra(centro_y, elemento.legge(area, 'y_min'), elemento.legge(area, 'y_max'))
    ])

# QUERY: selezione base (pura)
def query_selezionati(canvas, area):
    elementi = elemento.legge(canvas, 'elementi')
    return contenitore.filtra(elementi, lambda e: elemento_in_area(e, area))
```

### Vantaggi Emergenti TIC

#### 1. UNDO/REDO Gratis

```python
history = []

def seleziona(canvas, area):
    history.append(canvas)  # Snapshot automatico (immutabilità)
    nuova_selezione = query_selezionati(canvas, area)
    return elemento.scrive(canvas, 'selezione', nuova_selezione)

def undo():
    return history.pop() if history else None

# Funziona GRATIS - nulla è stato mutato
```

#### 2. Query Composte Semantiche

```python
# Seleziona SOLO i testi nell'area
def query_testi_in_area(canvas, area):
    return contenitore.filtra(
        query_selezionati(canvas, area),
        lambda e: confronta.uguale(elemento.legge(e, 'tipo'), 'testo')
    )

# Seleziona elementi di un certo layer
def query_layer_in_area(canvas, area, layer):
    return contenitore.filtra(
        query_selezionati(canvas, area),
        lambda e: confronta.uguale(elemento.legge(e, 'layer'), layer)
    )

# Seleziona elementi CON i loro connessi
def query_con_connessi(canvas, area):
    diretti = query_selezionati(canvas, area)
    connessi = contenitore.riduce(
        diretti,
        lambda acc, e: contenitore.unisce(acc, elemento.legge(e, 'connessioni')),
        []
    )
    return contenitore.unisce(diretti, connessi)
```

#### 3. Composizione come Frase

```python
# Query "linguistica" - si legge come una frase
selezione = flusso.componi(
    query_selezionati,           # "seleziona"
    query_solo_tipo('testo'),    # "i testi"
    query_solo_layer('fg'),      # "nel layer foreground"
    query_con_connessi           # "con i loro connessi"
)(canvas, area)
```

#### 4. Selezione Gerarchica (Propagazione)

```python
from tic_core.propagazione import Tessuto, propaga_a, derivato

tessuto = Tessuto()

# Selezionare un gruppo propaga ai figli
@derivato(tessuto, propaga_a('figli'))
def selezione_propaga(gruppo):
    if elemento.legge(gruppo, 'selezionato'):
        figli = elemento.legge(gruppo, 'figli')
        return contenitore.mappa(figli,
            lambda f: elemento.scrive(f, 'selezionato_via_parent', True)
        )
```

### Analisi Onesta

| Aspetto | Tradizionale | TIC | Differenza Reale |
|---------|-------------|-----|------------------|
| Algoritmo hit-test | O(n) | O(n) | **Nessuna** |
| Mouse events | Imperativo | Imperativo (boundary) | **Nessuna** |
| Rendering | Imperativo | Effetto | Solo audit |
| Performance | Dipende da struttura | Identica | **Nessuna** |
| **UNDO/REDO** | Implementazione manuale | **Gratis** | **TIC vince** |
| **Multi-criteria** | Codice ad-hoc | **Composizione** | **TIC vince** |
| **Selezione gerarchica** | Codice complesso | **Propagazione** | **TIC vince** |
| **Testing** | Mock complessi | **Funzioni pure** | **TIC vince** |

### Verdict

TIC **non** rende la selezione più veloce. L'algoritmo è identico.

TIC rende:
- UNDO/REDO **triviale**
- Query composte **naturali**
- Testing **semplice**
- Codice **leggibile come frasi**

---

## Caso 2: Carrello E-Commerce

**Contesto:** Calcolo totale con sconti, tasse, promozioni.

### Tradizionale

```javascript
class Cart {
    constructor() {
        this.items = [];
        this.discount = 0;
    }

    addItem(item) {
        this.items.push(item); // MUTAZIONE
        this.recalculate();    // Side effect
    }

    applyDiscount(code) {
        // Chiamata API, stato globale, side effects...
        fetch('/api/discount/' + code)
            .then(d => {
                this.discount = d.value; // MUTAZIONE
                this.recalculate();
            });
    }

    recalculate() {
        // Logica intrecciata con stato
    }
}
```

### TIC

```python
# L2: Molecole pure
def calcola_subtotale(item):
    return valore.moltiplica(
        elemento.legge(item, 'qty'),
        elemento.legge(item, 'prezzo')
    )

def calcola_totale(items):
    subtotali = contenitore.mappa(items, calcola_subtotale)
    return valore.somma(subtotali)

def applica_sconto(totale, percentuale):
    sconto = valore.moltiplica(totale, valore.divide(percentuale, 100))
    return valore.decrementa(totale, sconto)

# L3: Organismo (entry point)
def checkout(carrello, sconto_pct):
    items = elemento.legge(carrello, 'items')
    totale = calcola_totale(items)
    finale = applica_sconto(totale, sconto_pct)

    # Effetti al boundary - Runtime decide
    return (finale, [
        effetto.emetti('checkout.completato', {'totale': finale}),
        effetto.log('info', f'Checkout completato: €{finale}')
    ])
```

**Vantaggi:**
- Ogni funzione testabile in isolamento
- Nessuno stato mutabile
- Effetti espliciti e controllati
- Composizione chiara

---

## Caso 3: Validazione Form

**Contesto:** Validare input utente con regole multiple.

### TIC

```python
# Regole atomiche (L2: Molecole)
def regola_non_vuoto(campo):
    return confronta.falso(testo.vuoto(elemento.legge(campo, 'valore')))

def regola_email_valida(campo):
    return testo.contiene(elemento.legge(campo, 'valore'), '@')

def regola_lunghezza_minima(min_len):
    def regola(campo):
        return confronta.almeno(
            testo.lunghezza(elemento.legge(campo, 'valore')),
            min_len
        )
    return regola

# Composizione regole
def valida_campo(campo, regole):
    risultati = contenitore.mappa(regole, lambda r: r(campo))
    return confronta.tutti(risultati)

# Uso
regole_email = [regola_non_vuoto, regola_email_valida]
regole_password = [regola_non_vuoto, regola_lunghezza_minima(8)]

email_valida = valida_campo(campo_email, regole_email)
password_valida = valida_campo(campo_password, regole_password)
```

**Vantaggi:**
- Regole riutilizzabili
- Composizione dichiarativa
- Testing triviale per ogni regola
- Estensibile senza modificare esistente

---

## Quando TIC NON Serve

| Scenario | Perché TIC non aiuta |
|----------|---------------------|
| Script one-shot | Overhead non giustificato |
| Performance-critical inner loop | Immutabilità ha costo |
| Codice legacy brownfield | Refactoring troppo invasivo |
| Prototipo usa-e-getta | Semplicità > architettura |

---

## Sintesi

```
TIC non è una silver bullet.

È un trade-off consapevole:
+ Composabilità, testing, undo/redo, auditability
- Overhead concettuale, curva apprendimento

Usa TIC quando:
- Il dominio è complesso
- Servono garanzie (audit, undo, testing)
- Il codice deve durare
- Più persone lavorano insieme

Non usare TIC quando:
- È uno script veloce
- Performance è critica al nanosecondo
- Il team non è pronto
```
