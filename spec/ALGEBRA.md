# PTI Algebra Specification v0.1

## Definizione Formale

```
PTI-lang := (Cells, Compose, Pure, Effects)

dove:
  Cells   : Set di operazioni atomiche
  Compose : Cell × Cell → Cell
  Pure    : ∀c ∈ Cells, c(x) è deterministico, no side effects
  Effects : Boundary controllati da Runtime (non nell'algebra)
```

## Primitivi Algebra (Layer 3)

### Categoria: Data

```
elemento.crea    : Schema → Data → Element
elemento.legge   : Element → Field → Value
elemento.scrive  : Element → Field → Value → Element  (immutabile!)
elemento.esiste  : Element → Bool

contenitore.crea   : List[A] → Container[A]
contenitore.mappa  : (A → B) → Container[A] → Container[B]
contenitore.filtra : (A → Bool) → Container[A] → Container[A]
contenitore.riduce : (B → A → B) → B → Container[A] → B
contenitore.trova  : (A → Bool) → Container[A] → Maybe[A]
```

### Categoria: Predicati

```
confronta.uguale   : A → A → Bool
confronta.maggiore : Ord[A] → A → A → Bool
confronta.tra      : Ord[A] → A → A → A → Bool
confronta.nullo    : A → Bool
confronta.tutti    : List[(A → Bool)] → A → Bool
confronta.almeno   : List[(A → Bool)] → A → Bool
```

### Categoria: Composizione

```
componi.sequenza : (A → B) → (B → C) → (A → C)
componi.parallelo : (A → B) → (A → C) → (A → (B, C))
componi.condizione : (A → Bool) → (A → B) → (A → B) → (A → B)
componi.ripeti : (A → Bool) → (A → A) → A → A  // BOUNDED!
```

### Categoria: Pattern Matching

```
scegli.su : A → List[(Pattern, A → B)] → B
scegli.tipo : Any → List[(Type, Any → B)] → B
scegli.valore : A → List[(A, B)] → B → B
```

## Effetti (Layer 4 - Runtime Controlled)

**QUESTI NON SONO NELL'ALGEBRA. IL RUNTIME LI INTERCETTA.**

```
effetto.emetti  : Event → Effect[Unit]
effetto.leggi   : Source → Effect[Data]
effetto.scrivi  : Sink → Data → Effect[Unit]
effetto.attendi : Duration → Effect[Unit]
```

Il runtime decide:
- SE l'effetto è permesso
- COME eseguirlo
- AUDIT di ogni esecuzione

## Regole di Composizione

### R1: Chiusura
```
∀ c1, c2 ∈ Cells: compose(c1, c2) ∈ Cells
```
La composizione di celle produce sempre una cella valida.

### R2: Purezza
```
∀ c ∈ Cells, ∀ x: c(x) = c(x)  (determinismo)
∀ c ∈ Cells: effects(c) = ∅    (no side effects)
```

### R3: Terminazione
```
∀ c ∈ Cells: terminates(c) = true
```
Garantito da:
- No ricorsione unbounded
- `ripeti` ha sempre condizione di terminazione verificabile
- No loop infiniti by construction

### R4: Boundary Effects
```
Effects ∉ Cells
Effects sono SOLO al boundary, gestiti da Runtime
```

## Esempi di Codice Valido

```pti
// VALIDO: pura composizione di primitivi
cell processOrder = componi.sequenza(
  elemento.legge('items'),
  contenitore.mappa(item => elemento.legge(item, 'price')),
  contenitore.riduce(valore.somma, 0)
)

// VALIDO: pattern matching
cell handleStatus = scegli.su(status, [
  ('pending', () => processOrder),
  ('shipped', () => notifyCustomer),
  ('_', () => logError)
])

// VALIDO: effetto al boundary (runtime controlla)
cell submitOrder = componi.sequenza(
  processOrder,
  effetto.emetti('order.created')  // Runtime intercepts!
)
```

## Esempi di Codice INVALIDO

```pti
// INVALIDO: I/O diretto (non esiste nell'algebra)
cell badCode = fetch('http://...')  // ❌ fetch non è primitivo

// INVALIDO: eval/exec (non esiste)
cell dangerous = eval(userInput)  // ❌ eval non esiste

// INVALIDO: file system diretto
cell risky = fs.writeFile(...)  // ❌ fs non esiste

// INVALIDO: loop infinito
cell infinite = componi.ripeti(
  () => true,  // ❌ condizione sempre vera = non termina
  identity
)
```

## Enforcement

### Compile-time (Parser)
- Verifica che ogni operazione sia in `Cells`
- Verifica che composizioni siano well-typed
- Verifica terminazione di `ripeti`

### Runtime
- Sandbox execution
- Intercetta Effects
- Audit trail
- Permission check per ogni Effect

## Mapping a Linguaggi Host

### Python
```python
# Primitivo algebra → funzione Python pura
def elemento_legge(el, campo):
    return el.get(campo)

# Effetto → wrapper che passa per runtime
def effetto_emetti(event):
    return Effect('emit', event)  # Runtime gestisce
```

### JavaScript
```javascript
// Primitivo algebra → funzione JS pura
const elemento_legge = (el, campo) => el[campo];

// Effetto → Promise gestita da runtime
const effetto_emetti = (event) => new Effect('emit', event);
```

## Estensibilità

Nuovi primitivi possono essere aggiunti SOLO SE:
1. Sono puri (deterministici, no side effects)
2. Terminano sempre
3. Sono type-safe
4. Passano review di sicurezza

Gli Effects sono estesi SOLO dal Runtime, non dall'algebra.
