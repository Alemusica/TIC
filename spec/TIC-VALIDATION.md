# TIC Validation: Algebra come Prima Prova

## La Gerarchia

```
TIC (Tessular Interconnected Coding)
 │
 └── Framework concettuale: codice come tessuto interconnesso
      │
      └── PTI (Paradigma Tissutale Interconnesso)
           │
           └── Implementazione Python: archetipi, propagazione, biocache
                │
                └── ALGEBRA BASE
                     │
                     └── Prima prova empirica: LLM + JSOM
```

## Cosa Stiamo Testando

### Ipotesi TIC
> "Il codice è ridondanza mascherata. Il 90% delle funzioni sono variazioni
> dello stesso pattern. Riconoscili, dai nome semantico, componi."

### Ipotesi Algebra
> "Un set minimo di primitivi puri + boundary controllati è sufficiente
> per esprimere qualsiasi logica applicativa, mantenendo sicurezza."

### Test JSOM
Il test empirico verifica:

1. **Espressività**: L'algebra è sufficiente per task reali?
2. **Generabilità**: L'LLM riesce a comporre da questi primitivi?
3. **Qualità**: Il codice generato è mantenibile, atomico, corretto?
4. **Sicurezza**: L'LLM è effettivamente "costretto" dentro l'algebra?
5. **Performance**: Scaffolding è veloce? Retry sono rari?

## Metriche da Raccogliere

### Quantitative

| Metrica | Cosa Misura |
|---------|-------------|
| Tempo generazione | Quanto ci mette l'LLM a produrre codice PTI |
| Retry rate | Quante volte il validator rigetta output LLM |
| LOC generato | Volume di codice prodotto |
| Copertura algebra | % primitivi usati su totale disponibili |
| Complessità ciclomatica | Semplicità del codice |

### Qualitative

| Metrica | Cosa Misura |
|---------|-------------|
| Leggibilità | Il codice è auto-documentante? |
| Atomicità | Funzioni fanno una cosa sola? |
| Riusabilità | Celle si compongono facilmente? |
| Debugging | Errori sono tracciabili? |
| Manutenibilità | Modifiche sono localizzate? |

## Risultati Attesi

### Se l'Ipotesi è Corretta

```
✓ L'LLM genera codice PTI-compliant al primo/secondo tentativo
✓ Il codice è più leggibile del tradizionale
✓ Le celle si compongono naturalmente
✓ Il debug è più facile (audit trail)
✓ Lo scaffolding è deterministico
```

### Se l'Ipotesi è Sbagliata

```
✗ L'LLM richiede molti retry (algebra troppo limitata?)
✗ Il codice è verboso/illeggibile (naming non funziona?)
✗ Le celle non compongono bene (algebra mal progettata?)
✗ Lo scaffolding rompe spesso (constraint troppo stretti?)
```

## Design dell'Esperimento

### Setup

1. **Task**: Definire N task di complessità variabile per JSOM
2. **Baseline**: LLM genera codice tradizionale (JS/TS)
3. **Test**: LLM genera codice PTI-compliant
4. **Confronto**: Stesse metriche su entrambi

### Task Proposti

```
SEMPLICE:
- Aggiungi bottone con click handler
- Valida input email
- Calcola totale carrello

MEDIO:
- Gesture zoom con pinch
- Form multi-step con validazione
- Lista con sorting/filtering

COMPLESSO:
- Flusso checkout completo
- Sistema notifiche real-time
- Dashboard con grafici interattivi
```

### Protocollo

```
PER OGNI TASK:
  1. Descrivi task in linguaggio naturale
  2. LLM genera codice (baseline o PTI)
  3. Se PTI: validator verifica compliance
  4. Se rigettato: retry (max 3)
  5. Misura metriche
  6. Confronta baseline vs PTI
```

## Algebra Minima per Test

Per JSOM, serve almeno:

```pti
// Data
elemento.crea, elemento.legge, elemento.scrive
contenitore.mappa, contenitore.filtra, contenitore.trova

// Flusso
flusso.se, flusso.scegli, flusso.componi, flusso.sequenza

// Effetti (UI-specific)
effetto.emetti('evento')           // emit DOM event
effetto.leggi('state.path')        // read from state
effetto.scrivi('state.path', val)  // write to state
effetto.render(componente)         // render UI

// UI Primitivi
ui.testo(contenuto)
ui.bottone(label, onClick)
ui.input(tipo, value, onChange)
ui.lista(items, renderItem)
ui.contenitore(children, style)
```

## Domande per i Test

Dopo i test, rispondere a:

1. **L'algebra è sufficiente?**
   - Ci sono task che non si possono esprimere?
   - Quali primitivi mancano?

2. **L'LLM capisce l'algebra?**
   - Genera codice valido al primo tentativo?
   - Gli errori sono sistematici o casuali?

3. **Il codice è migliore?**
   - Più leggibile del baseline?
   - Più facile da modificare?
   - Bug più facili da trovare?

4. **Lo scaffolding funziona?**
   - Il runtime gestisce bene gli effetti?
   - L'audit trail è utile?

## Outcome Possibili

### Outcome A: Validazione Forte
```
Risultati "enormi" come ipotizzato.
L'algebra funziona, l'LLM è più efficace, il codice è migliore.
→ Procedi con linguaggio nativo + runtime production
```

### Outcome B: Validazione Parziale
```
Funziona per task semplici/medi, fatica su complessi.
→ Estendi algebra, itera su primitivi
```

### Outcome C: Invalidazione
```
L'algebra è troppo limitante, l'LLM non riesce a comporsi.
→ Ripensa il design, forse constraint diversi
```

## Timeline Proposta

```
SETTIMANA 1: Definire task e baseline
SETTIMANA 2: Eseguire test baseline (codice tradizionale)
SETTIMANA 3: Eseguire test PTI
SETTIMANA 4: Analisi risultati e conclusioni
```

## Conclusione

L'algebra è il **punto di validazione critico**.

Se funziona → TIC è validato empiricamente
Se non funziona → Sappiamo dove fallisce e come iterare

**I test JSOM sono il momento della verità.**

---

*"Un seme di sesamo contiene l'universo intero."*

Se l'algebra minima contiene abbastanza "universo" per costruire applicazioni reali,
TIC passa da teoria a pratica.
