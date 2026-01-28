"""
MOLECOLA: ordine
Regole per gestione ordini.

Dimostra:
- Pattern matching con flusso.scegli
- Effetti controllati (boundary)
- Transizioni di stato
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pti_core.archetipi import elemento, contenitore, confronta, valore, flusso, effetto


# === STATI ORDINE ===

STATI_ORDINE = ['creato', 'confermato', 'pagato', 'spedito', 'consegnato', 'annullato']

TRANSIZIONI_VALIDE = {
    'creato': ['confermato', 'annullato'],
    'confermato': ['pagato', 'annullato'],
    'pagato': ['spedito', 'annullato'],
    'spedito': ['consegnato'],
    'consegnato': [],
    'annullato': []
}


# === FATTI ===

def ordine_crea(utente_id: str, items: list, totale: float) -> dict:
    """
    ordine.crea → crea nuovo ordine

    >>> o = ordine_crea('user123', [{'sku': 'A', 'qty': 1}], 100.0)
    >>> elemento.legge(o, 'stato')
    'creato'
    """
    import uuid
    return elemento.crea({
        'id': str(uuid.uuid4())[:8],
        'utente_id': utente_id,
        'items': items,
        'totale': totale,
        'stato': 'creato',
        'storico_stati': ['creato']
    })


# === REGOLE ===

def ordine_transizione_valida(ordine: dict, nuovo_stato: str) -> bool:
    """
    ordine.transizione_valida → verifica se transizione è permessa

    >>> o = ordine_crea('u1', [], 100)
    >>> ordine_transizione_valida(o, 'confermato')
    True
    >>> ordine_transizione_valida(o, 'consegnato')
    False
    """
    stato_attuale = elemento.legge(ordine, 'stato')
    stati_permessi = TRANSIZIONI_VALIDE.get(stato_attuale, [])
    return confronta.in_lista(nuovo_stato, stati_permessi)


def ordine_annullabile(ordine: dict) -> bool:
    """
    ordine.annullabile → True se può essere annullato
    """
    stato = elemento.legge(ordine, 'stato')
    return confronta.in_lista(stato, ['creato', 'confermato', 'pagato'])


def ordine_completato(ordine: dict) -> bool:
    """
    ordine.completato → True se consegnato
    """
    return confronta.uguale(
        elemento.legge(ordine, 'stato'),
        'consegnato'
    )


# === TRASFORMAZIONI ===

def ordine_cambia_stato(ordine: dict, nuovo_stato: str) -> tuple:
    """
    ordine.cambia_stato → cambia stato se transizione valida

    Ritorna (successo, ordine_nuovo | errore)

    >>> o = ordine_crea('u1', [], 100)
    >>> ok, o2 = ordine_cambia_stato(o, 'confermato')
    >>> ok
    True
    >>> elemento.legge(o2, 'stato')
    'confermato'
    """
    if not ordine_transizione_valida(ordine, nuovo_stato):
        stato_attuale = elemento.legge(ordine, 'stato')
        return (False, f"Transizione {stato_attuale} → {nuovo_stato} non valida")

    storico = elemento.legge(ordine, 'storico_stati')
    nuovo_storico = contenitore.aggiunge(storico, nuovo_stato)

    nuovo = elemento.scrive(ordine, 'stato', nuovo_stato)
    nuovo = elemento.scrive(nuovo, 'storico_stati', nuovo_storico)

    return (True, nuovo)


# === CELLE CON EFFETTI ===

def cella_conferma_ordine(ordine: dict) -> tuple:
    """
    Cella: conferma ordine + emette evento

    Ritorna (ordine_nuovo, effetti)
    """
    ok, risultato = ordine_cambia_stato(ordine, 'confermato')

    if ok:
        # Successo: emetti evento
        eff = effetto.emetti('ordine.confermato', {
            'ordine_id': elemento.legge(risultato, 'id'),
            'utente_id': elemento.legge(risultato, 'utente_id')
        })
        return (risultato, [eff])
    else:
        # Fallimento: emetti errore
        eff = effetto.log('warn', f"Conferma fallita: {risultato}")
        return (ordine, [eff])


def cella_paga_ordine(ordine: dict, metodo_pagamento: str) -> tuple:
    """
    Cella: processa pagamento + emette eventi

    Ritorna (ordine_nuovo, effetti)
    """
    # Prima verifica stato
    if elemento.legge(ordine, 'stato') != 'confermato':
        return (ordine, [
            effetto.fallisce('Ordine non confermato', 'ORDER_NOT_CONFIRMED')
        ])

    # Cambia stato
    ok, risultato = ordine_cambia_stato(ordine, 'pagato')

    if ok:
        effetti = [
            effetto.emetti('ordine.pagato', {
                'ordine_id': elemento.legge(risultato, 'id'),
                'totale': elemento.legge(risultato, 'totale'),
                'metodo': metodo_pagamento
            }),
            effetto.log('info', f"Ordine {elemento.legge(risultato, 'id')} pagato")
        ]
        return (risultato, effetti)
    else:
        return (ordine, [effetto.fallisce(risultato, 'PAYMENT_FAILED')])


def cella_spedisci_ordine(ordine: dict, tracking: str) -> tuple:
    """
    Cella: spedisce ordine + notifica

    Ritorna (ordine_nuovo, effetti)
    """
    ok, risultato = ordine_cambia_stato(ordine, 'spedito')

    if ok:
        risultato = elemento.scrive(risultato, 'tracking', tracking)
        effetti = [
            effetto.emetti('ordine.spedito', {
                'ordine_id': elemento.legge(risultato, 'id'),
                'tracking': tracking
            }),
            # Questo effetto richiede I/O esterno (email)
            effetto.scrivi('email', {
                'to': elemento.legge(risultato, 'utente_id'),
                'template': 'ordine_spedito',
                'data': {'tracking': tracking}
            })
        ]
        return (risultato, effetti)
    else:
        return (ordine, [effetto.fallisce(risultato, 'SHIP_FAILED')])


# === FLOW COMPLETO ===

def flow_checkout(carrello: dict, metodo_pagamento: str) -> tuple:
    """
    Flow completo: carrello → ordine pagato

    Ritorna (ordine | None, effetti)
    """
    from molecole.carrello import query_carrello_totale, carrello_vuoto

    # Validazione
    if carrello_vuoto(carrello):
        return (None, [effetto.fallisce('Carrello vuoto', 'CART_EMPTY')])

    # Crea ordine
    ordine = ordine_crea(
        utente_id=elemento.legge(carrello, 'utente_id'),
        items=elemento.legge(carrello, 'items'),
        totale=query_carrello_totale(carrello)
    )

    tutti_effetti = []

    # Conferma
    ordine, eff = cella_conferma_ordine(ordine)
    tutti_effetti.extend(eff)

    # Paga
    ordine, eff = cella_paga_ordine(ordine, metodo_pagamento)
    tutti_effetti.extend(eff)

    return (ordine, tutti_effetti)


# === QUERY ===

def query_ordini_per_stato(ordini: list, stato: str) -> list:
    """
    ?- ordini.per_stato
    """
    return contenitore.filtra(
        ordini,
        lambda o: confronta.uguale(elemento.legge(o, 'stato'), stato)
    )


def query_ordini_utente(ordini: list, utente_id: str) -> list:
    """
    ?- ordini.utente
    """
    return contenitore.filtra(
        ordini,
        lambda o: confronta.uguale(elemento.legge(o, 'utente_id'), utente_id)
    )


def query_totale_vendite(ordini: list) -> float:
    """
    ?- ordini.totale_vendite (solo pagati/spediti/consegnati)
    """
    completati = contenitore.filtra(
        ordini,
        lambda o: confronta.in_lista(
            elemento.legge(o, 'stato'),
            ['pagato', 'spedito', 'consegnato']
        )
    )
    totali = contenitore.mappa(completati, lambda o: elemento.legge(o, 'totale'))
    return valore.somma(totali)
