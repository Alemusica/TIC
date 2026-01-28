#!/usr/bin/env python3
"""
DEMO PTI: E-Commerce con Algebra + Effetti Controllati

Dimostra:
1. Algebra pura per business logic (celle)
2. Effetti come boundary (runtime li gestisce)
3. Audit trail automatico
4. Composizione funzionale
"""

import sys
sys.path.insert(0, '../../')

from tic_core.archetipi import elemento
from organismi.shop import Shop


def main():
    print("=" * 70)
    print("PTI DEMO: E-Commerce con Algebra Sicura")
    print("=" * 70)
    print()

    # === 1. Setup Shop ===
    print("1. Creazione shop...")
    shop = Shop("PTI Store")
    print(f"   ✓ Shop '{shop.nome}' creato")
    print()

    # === 2. Aggiungi prodotti ===
    print("2. Aggiunta prodotti al catalogo...")
    shop.aggiungi_prodotto('WIDGET-001', 'Widget Pro', 29.99, 50)
    shop.aggiungi_prodotto('GADGET-002', 'Gadget Plus', 49.99, 30)
    shop.aggiungi_prodotto('TOOL-003', 'Tool Master', 19.99, 100)
    shop.aggiungi_prodotto('RARE-004', 'Articolo Raro', 199.99, 2)

    stato = shop.stato_shop()
    print(f"   ✓ {stato['prodotti_totali']} prodotti aggiunti")
    print(f"   ✓ Valore inventario: €{stato['valore_inventario']:.2f}")
    print()

    # === 3. Utente aggiunge al carrello ===
    print("3. Utente 'mario' aggiunge prodotti al carrello...")
    ok, _ = shop.aggiungi_a_carrello('mario', 'WIDGET-001', 2)
    print(f"   {'✓' if ok else '✗'} Widget Pro x2")

    ok, _ = shop.aggiungi_a_carrello('mario', 'GADGET-002', 1)
    print(f"   {'✓' if ok else '✗'} Gadget Plus x1")

    ok, _ = shop.aggiungi_a_carrello('mario', 'TOOL-003', 3)
    print(f"   {'✓' if ok else '✗'} Tool Master x3")

    carrello = shop.ottieni_carrello('mario')
    from molecole.carrello import query_carrello_totale, query_carrello_num_items
    print(f"   → Totale carrello: €{query_carrello_totale(carrello):.2f}")
    print(f"   → Items nel carrello: {query_carrello_num_items(carrello)}")
    print()

    # === 4. Checkout ===
    print("4. Checkout con carta di credito...")
    successo, risultato, audit = shop.checkout('mario', 'carta_credito')

    if successo:
        print(f"   ✓ Ordine creato: {elemento.legge(risultato, 'id')}")
        print(f"   ✓ Stato: {elemento.legge(risultato, 'stato')}")
        print(f"   ✓ Totale: €{elemento.legge(risultato, 'totale'):.2f}")
    else:
        print(f"   ✗ Errore: {risultato}")
    print()

    # === 5. Audit Trail ===
    print("5. Audit Trail (effetti eseguiti dal runtime):")
    for i, entry in enumerate(audit, 1):
        tipo = entry['tipo']
        if tipo == 'emit':
            evento = entry['payload']['evento']
            print(f"   [{i}] EMIT: {evento}")
        elif tipo == 'log':
            msg = entry['payload']['messaggio']
            print(f"   [{i}] LOG: {msg}")
        elif tipo == 'write':
            dest = entry['payload']['destinazione']
            print(f"   [{i}] WRITE: {dest}")
        else:
            print(f"   [{i}] {tipo}: {entry['payload']}")
    print()

    # === 6. Stato finale ===
    print("6. Stato finale shop:")
    stato = shop.stato_shop()
    print(f"   Prodotti disponibili: {stato['prodotti_disponibili']}/{stato['prodotti_totali']}")
    print(f"   Valore inventario:    €{stato['valore_inventario']:.2f}")
    print(f"   Ordini completati:    {stato['ordini_totali']}")
    print(f"   Vendite totali:       €{stato['vendite_totali']:.2f}")
    print()

    # === 7. Test prodotto esaurito ===
    print("7. Test: tentativo acquisto prodotto quasi esaurito...")
    ok, msg = shop.aggiungi_a_carrello('luigi', 'RARE-004', 5)
    if not ok:
        print(f"   ✓ Correttamente rifiutato: {msg}")
    print()

    # === 8. Secondo ordine ===
    print("8. Secondo ordine (luigi)...")
    shop.aggiungi_a_carrello('luigi', 'RARE-004', 1)
    shop.aggiungi_a_carrello('luigi', 'WIDGET-001', 1)
    successo, risultato, _ = shop.checkout('luigi', 'paypal')
    if successo:
        print(f"   ✓ Ordine {elemento.legge(risultato, 'id')} completato")
    print()

    # === 9. Stato finale ===
    print("9. Stato finale dopo 2 ordini:")
    stato = shop.stato_shop()
    print(f"   Ordini totali:     {stato['ordini_totali']}")
    print(f"   Vendite totali:    €{stato['vendite_totali']:.2f}")
    print(f"   Sotto soglia:      {stato['prodotti_sotto_soglia']} prodotti")

    print()
    print("=" * 70)
    print("PUNTI CHIAVE DIMOSTRATI:")
    print("=" * 70)
    print("""
  1. ALGEBRA PURA: Tutta la business logic (carrello, ordine, prodotto)
     è composta da archetipi puri - deterministici, no side effects.

  2. EFFETTI CONTROLLATI: Email, eventi, log sono DESCRITTI come Effetto,
     ma eseguiti SOLO dal Runtime. Il codice non può fare I/O diretto.

  3. AUDIT TRAIL: Ogni effetto è loggato. Tracciabilità completa.

  4. COMPOSIZIONE: Le celle si compongono:
     flow_checkout = conferma → paga → (emetti eventi)

  5. L'LLM PUÒ GENERARE SOLO DA QUESTA ALGEBRA.
     Non può generare fetch(), fs.write(), eval().
     Il constraint è nell'algebra, non nelle permission.
""")
    print("=" * 70)


if __name__ == "__main__":
    main()
