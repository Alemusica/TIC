# PTI: Architettura a 4 Layer per LLM Sicuri

## Il Problema

```typescript
// LLM genera codice "tradizionale"
function processData(data) {
  // Può fare QUALSIASI COSA:
  fetch('http://evil.com')     // network I/O
  fs.writeFile('/etc/passwd')  // filesystem
  eval(userInput)              // arbitrary code execution
}
```

**Non c'è modo di sapere cosa farà il codice finché non lo esegui.**

## La Soluzione: 4 Layer

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: USER                                               │
│ "Aggiungi feature X al progetto"                           │
│ Linguaggio naturale → intenzioni                            │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ LAYER 2: LLM                                                │
│ Interprete che genera codice PTI-compliant                  │
│ PUÒ SOLO comporre da algebra base                          │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: SCHEMA/ALGEBRA                                     │
│ IL CUORE - operazioni primitive permesse                    │
│ Composizione | Pattern matching | Trasformazioni pure       │
│ NON permesso: I/O arbitrario, accesso sistema              │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ LAYER 4: RUNTIME                                            │
│ Executor protetto con audit trail                           │
│ Intercetta effetti, decide se permetterli                   │
│ Log di ogni operazione                                      │
└─────────────────────────────────────────────────────────────┘
```

## Layer 3: L'Algebra Base

Questa è la chiave. L'LLM può SOLO usare questi primitivi:

### Primitivi Data (puri)

```
elemento.crea    : Schema → Data → Element
elemento.legge   : Element → Field → Value
elemento.scrive  : Element → Field → Value → Element

contenitore.mappa  : (A → B) → [A] → [B]
contenitore.filtra : (A → Bool) → [A] → [A]
contenitore.riduce : (B → A → B) → B → [A] → B
```

### Primitivi Flusso (puri)

```
flusso.se       : Bool → (→ A) → (→ A) → A
flusso.scegli   : A → [(Pattern, A → B)] → B
flusso.componi  : (A → B) → (B → C) → (A → C)
flusso.ripeti   : (A → Bool) → (A → A) → A → A  // BOUNDED
```

### Primitivi Effetto (BOUNDARY - Runtime controlla)

```
effetto.emetti  : Event → Effect[Unit]
effetto.leggi   : Source → Effect[Data]
effetto.scrivi  : Sink → Data → Effect[Unit]
```

**GLI EFFETTI NON ESEGUONO NULLA.**

Creano una **descrizione** di cosa fare. Il Runtime decide se farlo.

## Cosa NON Esiste nell'Algebra

```
❌ fetch()          // Non esiste
❌ fs.readFile()    // Non esiste
❌ eval()           // Non esiste
❌ exec()           // Non esiste
❌ import()         // Non esiste dinamicamente
❌ new Function()   // Non esiste
❌ while(true)      // ripeti è BOUNDED
```

**L'LLM non può generarli perché non sono nell'algebra.**

Non è un permission check a runtime. È un constraint a compile-time.

## Confronto

| Sistema | Constraint | Quando |
|---------|------------|--------|
| WebAssembly | Sandbox | Runtime |
| Deno | Permissions | Runtime |
| **PTI** | **Algebra limitata** | **Compile-time** |

PTI è **sicuro by construction**, non by permission.

## Esempio Concreto

### Richiesta User (Layer 1)
```
"Processa ordine e invia email di conferma"
```

### LLM Genera (Layer 2)
```pti
cell processaOrdine = componi.sequenza(
  // Tutto puro
  ordine.valida,
  ordine.calcola_totale,
  ordine.cambia_stato('confermato'),

  // Effetto al boundary
  effetto.emetti('ordine.confermato'),
  effetto.scrivi('email', templateConferma)
)
```

### Algebra Verifica (Layer 3)
```
✓ componi.sequenza  → primitivo valido
✓ ordine.valida     → cella pura
✓ ordine.calcola    → cella pura
✓ effetto.emetti    → boundary controllato
✓ effetto.scrivi    → boundary controllato

→ CODICE VALIDO
```

### Runtime Esegue (Layer 4)
```
1. Esegue celle pure in sandbox
2. Intercetta effetto.emetti → decide se propagare evento
3. Intercetta effetto.scrivi → decide se inviare email
4. Log tutto in audit trail
```

## Audit Trail

Ogni operazione è tracciata:

```json
{
  "timestamp": "2024-01-28T10:30:00Z",
  "user": "mario",
  "request": "Processa ordine #123",
  "llm_generated": "cell processaOrdine = ...",
  "effects_executed": [
    {"type": "emit", "event": "ordine.confermato", "allowed": true},
    {"type": "write", "sink": "email", "allowed": true}
  ],
  "result": "success"
}
```

**Tracciabilità completa. Rollback possibile. Debugging facile.**

## Guardrails LLM (Layer 2)

Come enforci che l'LLM generi SOLO da algebra?

### Opzione A: Prompt Engineering
```
System: You can ONLY use these primitives: {list}
Any other operation is invalid.
```
→ Fallibile, l'LLM può "allucinare"

### Opzione B: Parser + Validator (RACCOMANDATO)
```
LLM generates → Parser checks → If invalid, reject and retry
```
→ Sicuro, ma richiede retry loop

### Opzione C: Constrained Decoding
```
LLM genera token da vocabulary limitato a sintassi PTI
```
→ Richiede fine-tuning o constrained decoding

**Per POC, Opzione B è la più pratica.**

## Implicazioni per JSOM

Con questa architettura, JSOM diventa:

```
┌─────────────────────────────────────┐
│ User: "Aggiungi gesture per zoom"   │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ LLM: genera da algebra PTI          │
│ cell zoomGesture = componi(         │
│   detectPinch,     // puro          │
│   calculateScale,  // puro          │
│   emitZoomEvent    // boundary      │
│ )                                   │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ Runtime: esegue in sandbox          │
│ - detectPinch: pure math ✓          │
│ - calculateScale: pure math ✓       │
│ - emitZoomEvent: runtime intercepts │
│   e decide se propagare             │
└─────────────────────────────────────┘
```

L'LLM **non può generare**:
```javascript
document.addEventListener('pinch', ...)  // ❌ non esiste
fetch('/api/zoom', ...)                  // ❌ non esiste
eval(userCode)                           // ❌ non esiste
```

## Domande Aperte

### 1. Superficie dell'Algebra
Quanti primitivi servono per essere espressivi ma sicuri?

```
Troppo pochi → LLM limitato, UX frustrante
Troppo tanti → Aumenta superficie attacco
```

### 2. Performance
Il layer di indirezione (Runtime) introduce overhead?

```
Mitigazione: JIT compilation di celle pure
```

### 3. Escape Hatch
Servono casi dove il codice "tradizionale" è necessario?

```
Proposta: "unsafe" block esplicito, richiede approval manuale
```

## Next Steps

1. **Definire algebra minima** per casi d'uso reali
2. **Implementare parser/validator** per codice PTI
3. **Testare con LLM** su task reali (JSOM?)
4. **Misurare** retry rate, code quality, developer experience

---

## Conclusione

PTI + 4 Layer = **LLM che può solo generare codice sicuro**.

Non è "speriamo che non faccia cose brutte".
È "matematicamente non può fare cose brutte".

Il constraint è nell'algebra, non nelle permission.
