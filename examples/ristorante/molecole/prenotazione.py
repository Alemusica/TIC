"""
MOLECOLA: prenotazione
Regole per gestione prenotazioni.

prenotazione.crea     → crea nuova prenotazione
prenotazione.valida   → verifica validità
prenotazione.conferma → conferma prenotazione
"""

import sys
sys.path.insert(0, '../../../')

from pti_core.archetipi import elemento, confronta, testo, valore


def prenotazione_crea(nome: str, persone: int, ora: str, telefono: str = None) -> dict:
    """
    prenotazione.crea → crea nuova prenotazione

    >>> p = prenotazione_crea('Mario Rossi', 4, '20:00')
    >>> elemento.legge(p, 'nome')
    'Mario Rossi'
    """
    return elemento.crea({
        'nome': testo.pulisce(nome),
        'persone': persone,
        'ora': ora,
        'telefono': telefono,
        'stato': 'pending',
        'tavolo_id': None
    })


def prenotazione_nome_valido(prenotazione: dict) -> bool:
    """
    prenotazione.nome.valido → nome non vuoto

    >>> p = prenotazione_crea('Mario', 2, '20:00')
    >>> prenotazione_nome_valido(p)
    True
    >>> p2 = prenotazione_crea('', 2, '20:00')
    >>> prenotazione_nome_valido(p2)
    False
    """
    nome = elemento.legge(prenotazione, 'nome')
    return not testo.vuoto(nome)


def prenotazione_persone_valide(prenotazione: dict, min_p: int = 1, max_p: int = 20) -> bool:
    """
    prenotazione.persone.valide → persone tra min e max

    >>> p = prenotazione_crea('Mario', 4, '20:00')
    >>> prenotazione_persone_valide(p)
    True
    >>> p2 = prenotazione_crea('Mario', 0, '20:00')
    >>> prenotazione_persone_valide(p2)
    False
    """
    persone = elemento.legge(prenotazione, 'persone')
    return confronta.tra(persone, min_p, max_p)


def prenotazione_ora_valida(prenotazione: dict, apertura: str = '12:00', chiusura: str = '23:00') -> bool:
    """
    prenotazione.ora.valida → ora tra apertura e chiusura

    >>> p = prenotazione_crea('Mario', 4, '20:00')
    >>> prenotazione_ora_valida(p)
    True
    """
    ora = elemento.legge(prenotazione, 'ora')
    return confronta.tra(ora, apertura, chiusura)


def prenotazione_valida(prenotazione: dict) -> tuple:
    """
    prenotazione.valida → (True/False, errori[])

    Verifica tutte le regole di validazione.

    >>> p = prenotazione_crea('Mario Rossi', 4, '20:00')
    >>> valido, errori = prenotazione_valida(p)
    >>> valido
    True
    """
    errori = []

    if not prenotazione_nome_valido(prenotazione):
        errori.append('nome.vuoto')

    if not prenotazione_persone_valide(prenotazione):
        errori.append('persone.non.valide')

    if not prenotazione_ora_valida(prenotazione):
        errori.append('ora.fuori.orario')

    return (len(errori) == 0, errori)


def prenotazione_assegna_tavolo(prenotazione: dict, tavolo_id: str) -> dict:
    """
    prenotazione.assegna_tavolo → assegna tavolo a prenotazione
    """
    nuovo = elemento.scrive(prenotazione, 'tavolo_id', tavolo_id)
    nuovo = elemento.scrive(nuovo, 'stato', 'confermata')
    return nuovo


def prenotazione_annulla(prenotazione: dict) -> dict:
    """
    prenotazione.annulla → annulla prenotazione
    """
    return elemento.scrive(prenotazione, 'stato', 'annullata')


def prenotazione_compatibile(prenotazione: dict, tavolo: dict) -> bool:
    """
    prenotazione.compatibile → prenotazione può stare in tavolo

    Verifica che persone <= posti.

    >>> from .tavolo import tavolo_crea
    >>> t = tavolo_crea('T1', posti=4)
    >>> p = prenotazione_crea('Mario', 3, '20:00')
    >>> prenotazione_compatibile(p, t)
    True
    """
    persone = elemento.legge(prenotazione, 'persone')
    posti = elemento.legge(tavolo, 'posti')
    return confronta.almeno(posti, persone)
