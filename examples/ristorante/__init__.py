"""
ESEMPIO PTI: Sistema Prenotazione Ristorante

Struttura:
- molecole/tavolo.py      → stato e query tavoli
- molecole/prenotazione.py → creazione e validazione prenotazioni
- organismi/prenota.py    → flow completo prenotazione
- main.py                 → demo

Questo esempio mostra:
1. Naming semantico (tavolo.libero, prenotazione.valida)
2. Propagazione (cambio stato → aggiorna derivati)
3. Gerarchia (molecole usano archetipi, organismi usano molecole)
"""

from .molecole import tavolo, prenotazione
from .organismi import ristorante

__all__ = ['tavolo', 'prenotazione', 'ristorante']
