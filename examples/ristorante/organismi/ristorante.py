"""
ORGANISMO: ristorante
Flow completo per sistema prenotazioni.

ristorante.inizializza  → crea ristorante con tavoli
ristorante.prenota      → ENTRY POINT principale
ristorante.annulla      → annulla prenotazione
ristorante.stato        → stato attuale
"""

import sys
sys.path.insert(0, '../../../')

from pti_core.archetipi import elemento, contenitore, confronta
from pti_core.propagazione import Tessuto

# Import molecole
from ..molecole import tavolo, prenotazione

# SALTI per notifiche esterne
SALTO = ["sistema.email", "sistema.sms"]


class Ristorante:
    """
    Organismo Ristorante.

    Gestisce:
    - Lista tavoli
    - Prenotazioni
    - Propagazione stato
    """

    def __init__(self, nome: str, num_tavoli: int = 10):
        """
        ristorante.inizializza

        >>> r = Ristorante('Da Mario', num_tavoli=5)
        >>> len(r.tavoli)
        5
        """
        self.nome = nome
        self.tavoli = []
        self.prenotazioni = []
        self.tessuto = Tessuto()

        # Crea tavoli iniziali
        for i in range(1, num_tavoli + 1):
            posti = 4 if i % 3 != 0 else 6  # ogni 3° tavolo ha 6 posti
            t = tavolo.tavolo_crea(f'T{i}', posti=posti)
            self.tavoli.append(t)

        # Registra derivati nel tessuto
        self._setup_derivati()

    def _setup_derivati(self):
        """Setup fatti derivati con propagazione."""

        @self.tessuto.derivato(
            'ristorante.tavoli.liberi',
            dipende_da=['tavolo.*.stato']
        )
        def _():
            return tavolo.query_tavoli_liberi(self.tavoli)

        @self.tessuto.derivato(
            'ristorante.capienza.disponibile',
            dipende_da=['tavolo.*.stato']
        )
        def _():
            return tavolo.query_capienza_disponibile(self.tavoli)

    def prenota(self, nome: str, persone: int, ora: str, telefono: str = None) -> tuple:
        """
        ristorante.prenota → ENTRY POINT

        Ritorna (successo: bool, risultato: dict|str)

        >>> r = Ristorante('Test', num_tavoli=3)
        >>> ok, res = r.prenota('Mario', 4, '20:00')
        >>> ok
        True
        """
        # 1. Crea prenotazione
        p = prenotazione.prenotazione_crea(nome, persone, ora, telefono)

        # 2. Valida prenotazione
        valida, errori = prenotazione.prenotazione_valida(p)
        if not valida:
            return (False, {'errore': 'prenotazione.non.valida', 'dettagli': errori})

        # 3. Trova tavoli liberi
        tavoli_liberi = tavolo.query_tavoli_liberi(self.tavoli)
        if contenitore.vuoto(tavoli_liberi):
            return (False, {'errore': 'nessun.tavolo.disponibile'})

        # 4. Filtra tavoli compatibili (capienza)
        tavoli_ok = contenitore.filtra(
            tavoli_liberi,
            lambda t: prenotazione.prenotazione_compatibile(p, t)
        )

        if contenitore.vuoto(tavoli_ok):
            return (False, {'errore': 'nessun.tavolo.capienza.sufficiente'})

        # 5. Prendi primo tavolo disponibile
        t = contenitore.primo(tavoli_ok)
        tavolo_id = elemento.legge(t, 'id')

        # 6. Assegna
        idx = self._trova_indice_tavolo(tavolo_id)
        self.tavoli[idx] = tavolo.tavolo_assegna(t, p)
        p = prenotazione.prenotazione_assegna_tavolo(p, tavolo_id)
        self.prenotazioni.append(p)

        # 7. Propaga (il tessuto si aggiorna automaticamente)
        self.tessuto.imposta(f'tavolo.{tavolo_id}.stato', 'occupato')

        return (True, {
            'prenotazione': p,
            'tavolo': tavolo_id,
            'messaggio': f'Prenotazione confermata per {nome}, tavolo {tavolo_id}'
        })

    def annulla(self, nome: str) -> tuple:
        """
        ristorante.annulla → annulla prenotazione per nome

        >>> r = Ristorante('Test', num_tavoli=3)
        >>> r.prenota('Mario', 2, '20:00')
        (True, ...)
        >>> ok, _ = r.annulla('Mario')
        >>> ok
        True
        """
        # Trova prenotazione
        p = contenitore.trova(
            self.prenotazioni,
            lambda x: elemento.legge(x, 'nome') == nome and
                      elemento.legge(x, 'stato') == 'confermata'
        )

        if p is None:
            return (False, {'errore': 'prenotazione.non.trovata'})

        tavolo_id = elemento.legge(p, 'tavolo_id')

        # Libera tavolo
        idx = self._trova_indice_tavolo(tavolo_id)
        if idx is not None:
            self.tavoli[idx] = tavolo.tavolo_libera(self.tavoli[idx])
            self.tessuto.imposta(f'tavolo.{tavolo_id}.stato', 'libero')

        # Aggiorna prenotazione
        idx_p = self.prenotazioni.index(p)
        self.prenotazioni[idx_p] = prenotazione.prenotazione_annulla(p)

        return (True, {'messaggio': f'Prenotazione di {nome} annullata'})

    def stato(self) -> dict:
        """
        ristorante.stato → stato attuale

        >>> r = Ristorante('Test', num_tavoli=5)
        >>> s = r.stato()
        >>> s['tavoli_totali']
        5
        """
        liberi = tavolo.query_tavoli_liberi(self.tavoli)
        occupati = tavolo.query_tavoli_occupati(self.tavoli)

        return {
            'nome': self.nome,
            'tavoli_totali': len(self.tavoli),
            'tavoli_liberi': len(liberi),
            'tavoli_occupati': len(occupati),
            'capienza_totale': tavolo.query_capienza_totale(self.tavoli),
            'capienza_disponibile': tavolo.query_capienza_disponibile(self.tavoli),
            'prenotazioni_attive': len([
                p for p in self.prenotazioni
                if elemento.legge(p, 'stato') == 'confermata'
            ])
        }

    def _trova_indice_tavolo(self, tavolo_id: str) -> int:
        """Helper: trova indice tavolo per id."""
        for i, t in enumerate(self.tavoli):
            if elemento.legge(t, 'id') == tavolo_id:
                return i
        return None


# === Funzioni stateless per uso funzionale ===

def ristorante_crea(nome: str, num_tavoli: int = 10) -> Ristorante:
    """ristorante.crea → crea nuovo ristorante"""
    return Ristorante(nome, num_tavoli)


def ristorante_prenota(r: Ristorante, nome: str, persone: int, ora: str) -> tuple:
    """ristorante.prenota → prenota tavolo"""
    return r.prenota(nome, persone, ora)


def ristorante_stato(r: Ristorante) -> dict:
    """ristorante.stato → stato attuale"""
    return r.stato()
