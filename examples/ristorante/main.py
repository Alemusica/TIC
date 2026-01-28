#!/usr/bin/env python3
"""
DEMO PTI: Sistema Prenotazione Ristorante

Esegui: python main.py
"""

import sys
sys.path.insert(0, '../../')

from organismi.ristorante import Ristorante


def main():
    print("=" * 60)
    print("PTI DEMO: Sistema Prenotazione Ristorante")
    print("=" * 60)
    print()

    # === 1. Crea ristorante ===
    print("1. Creazione ristorante...")
    ristorante = Ristorante("Trattoria Da Mario", num_tavoli=5)
    print(f"   ✓ Ristorante '{ristorante.nome}' creato con {len(ristorante.tavoli)} tavoli")
    print()

    # === 2. Stato iniziale ===
    print("2. Stato iniziale:")
    stato = ristorante.stato()
    print(f"   Tavoli liberi:        {stato['tavoli_liberi']}/{stato['tavoli_totali']}")
    print(f"   Capienza disponibile: {stato['capienza_disponibile']} posti")
    print()

    # === 3. Prima prenotazione ===
    print("3. Prima prenotazione: Mario Rossi, 4 persone, ore 20:00")
    ok, risultato = ristorante.prenota("Mario Rossi", 4, "20:00")
    if ok:
        print(f"   ✓ {risultato['messaggio']}")
    else:
        print(f"   ✗ Errore: {risultato['errore']}")
    print()

    # === 4. Seconda prenotazione ===
    print("4. Seconda prenotazione: Giulia Bianchi, 2 persone, ore 21:00")
    ok, risultato = ristorante.prenota("Giulia Bianchi", 2, "21:00")
    if ok:
        print(f"   ✓ {risultato['messaggio']}")
    else:
        print(f"   ✗ Errore: {risultato['errore']}")
    print()

    # === 5. Stato dopo prenotazioni ===
    print("5. Stato dopo prenotazioni:")
    stato = ristorante.stato()
    print(f"   Tavoli liberi:        {stato['tavoli_liberi']}/{stato['tavoli_totali']}")
    print(f"   Capienza disponibile: {stato['capienza_disponibile']} posti")
    print(f"   Prenotazioni attive:  {stato['prenotazioni_attive']}")
    print()

    # === 6. Prenotazione gruppo grande ===
    print("6. Prenotazione gruppo: Famiglia Verdi, 6 persone, ore 19:30")
    ok, risultato = ristorante.prenota("Famiglia Verdi", 6, "19:30")
    if ok:
        print(f"   ✓ {risultato['messaggio']}")
    else:
        print(f"   ✗ Errore: {risultato.get('errore', risultato)}")
    print()

    # === 7. Annullamento ===
    print("7. Annullamento prenotazione Mario Rossi...")
    ok, risultato = ristorante.annulla("Mario Rossi")
    if ok:
        print(f"   ✓ {risultato['messaggio']}")
    else:
        print(f"   ✗ Errore: {risultato['errore']}")
    print()

    # === 8. Stato finale ===
    print("8. Stato finale:")
    stato = ristorante.stato()
    print(f"   Tavoli liberi:        {stato['tavoli_liberi']}/{stato['tavoli_totali']}")
    print(f"   Capienza disponibile: {stato['capienza_disponibile']} posti")
    print(f"   Prenotazioni attive:  {stato['prenotazioni_attive']}")
    print()

    # === 9. Test validazione ===
    print("9. Test validazione (prenotazione invalida):")
    print("   Tentativo: nome vuoto, 0 persone")
    ok, risultato = ristorante.prenota("", 0, "25:00")
    if not ok:
        print(f"   ✓ Correttamente rifiutata: {risultato.get('dettagli', risultato.get('errore'))}")
    print()

    print("=" * 60)
    print("Demo completata!")
    print()
    print("Questo esempio dimostra:")
    print("  • Naming semantico (tavolo.libero, prenotazione.valida)")
    print("  • Gerarchia (molecole → organismi)")
    print("  • Propagazione automatica dello stato")
    print("  • Uso degli archetipi (elemento, contenitore, confronta)")
    print("=" * 60)


if __name__ == "__main__":
    main()
