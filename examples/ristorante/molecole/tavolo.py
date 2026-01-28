"""
MOLECOLA: tavolo
Regole per gestione tavoli.

tavolo.crea       → crea un nuovo tavolo
tavolo.libero     → verifica se libero
tavolo.assegna    → assegna prenotazione
tavolo.libera     → libera tavolo
"""

import sys
sys.path.insert(0, '../../../')

from tic_core.archetipi import elemento, confronta
from tic_core.propagazione import Tessuto

# Tessuto locale per questo dominio
tessuto = Tessuto()

# SALTI: quando un tavolo cambia stato, notifica questi sistemi
SALTO = ["sistema.dashboard", "sistema.notifiche"]


def tavolo_crea(id: str, posti: int = 4) -> dict:
    """
    tavolo.crea → crea un nuovo tavolo

    >>> t = tavolo_crea('T1', posti=6)
    >>> elemento.legge(t, 'posti')
    6
    """
    return elemento.crea({
        'id': id,
        'posti': posti,
        'prenotazione': None,
        'stato': 'libero'
    })


def tavolo_libero(tavolo: dict) -> bool:
    """
    tavolo.libero → True se prenotazione è None

    >>> t = tavolo_crea('T1')
    >>> tavolo_libero(t)
    True
    """
    return confronta.nullo(
        elemento.legge(tavolo, 'prenotazione')
    )


def tavolo_assegna(tavolo: dict, prenotazione: dict) -> dict:
    """
    tavolo.assegna → assegna prenotazione a tavolo

    Ritorna nuovo tavolo con prenotazione assegnata.
    Propaga ai SALTI.
    """
    nuovo = elemento.scrive(tavolo, 'prenotazione', prenotazione)
    nuovo = elemento.scrive(nuovo, 'stato', 'occupato')

    # Registra nel tessuto per propagazione
    id_tavolo = elemento.legge(tavolo, 'id')
    tessuto.imposta(f'tavolo.{id_tavolo}.stato', 'occupato')

    return nuovo


def tavolo_libera(tavolo: dict) -> dict:
    """
    tavolo.libera → rimuove prenotazione

    >>> t = tavolo_crea('T1')
    >>> t = tavolo_assegna(t, {'nome': 'Mario'})
    >>> t = tavolo_libera(t)
    >>> tavolo_libero(t)
    True
    """
    nuovo = elemento.scrive(tavolo, 'prenotazione', None)
    nuovo = elemento.scrive(nuovo, 'stato', 'libero')

    id_tavolo = elemento.legge(tavolo, 'id')
    tessuto.imposta(f'tavolo.{id_tavolo}.stato', 'libero')

    return nuovo


def tavolo_capienza_ok(tavolo: dict, persone: int) -> bool:
    """
    tavolo.capienza_ok → True se posti >= persone

    >>> t = tavolo_crea('T1', posti=4)
    >>> tavolo_capienza_ok(t, 3)
    True
    >>> tavolo_capienza_ok(t, 6)
    False
    """
    posti = elemento.legge(tavolo, 'posti')
    return confronta.almeno(posti, persone)


# === QUERY (fatti derivati) ===

def query_tavoli_liberi(tavoli: list) -> list:
    """
    ?- tavoli.liberi

    >>> tavoli = [tavolo_crea('T1'), tavolo_crea('T2')]
    >>> len(query_tavoli_liberi(tavoli))
    2
    """
    from tic_core.archetipi import contenitore
    return contenitore.filtra(tavoli, tavolo_libero)


def query_tavoli_occupati(tavoli: list) -> list:
    """?- tavoli.occupati"""
    from tic_core.archetipi import contenitore
    return contenitore.filtra(tavoli, lambda t: not tavolo_libero(t))


def query_capienza_totale(tavoli: list) -> int:
    """?- ristorante.capienza"""
    from tic_core.archetipi import contenitore, valore
    posti = contenitore.mappa(tavoli, lambda t: elemento.legge(t, 'posti'))
    return valore.somma(posti)


def query_capienza_disponibile(tavoli: list) -> int:
    """?- ristorante.capienza.disponibile"""
    liberi = query_tavoli_liberi(tavoli)
    return query_capienza_totale(liberi)
