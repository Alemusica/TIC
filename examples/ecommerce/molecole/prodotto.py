"""
MOLECOLA: prodotto
Regole per gestione prodotti.

Dimostra composizione pura di archetipi.
"""

import sys
sys.path.insert(0, '../../../')

from pti_core.archetipi import elemento, confronta, valore, contenitore, flusso


# === FATTI (creazione) ===

def prodotto_crea(sku: str, nome: str, prezzo: float, quantita: int = 0) -> dict:
    """
    prodotto.crea → crea nuovo prodotto

    >>> p = prodotto_crea('SKU001', 'Widget', 29.99, 100)
    >>> elemento.legge(p, 'nome')
    'Widget'
    """
    return elemento.crea({
        'sku': sku,
        'nome': nome,
        'prezzo': prezzo,
        'quantita': quantita,
        'attivo': True
    })


# === REGOLE (predicati) ===

def prodotto_disponibile(prodotto: dict) -> bool:
    """
    prodotto.disponibile → True se quantita > 0 e attivo

    >>> p = prodotto_crea('SKU001', 'Widget', 29.99, 10)
    >>> prodotto_disponibile(p)
    True
    """
    return confronta.tutti([
        lambda p: confronta.vero(elemento.legge(p, 'attivo')),
        lambda p: confronta.maggiore(elemento.legge(p, 'quantita'), 0)
    ], prodotto)


def prodotto_sotto_soglia(prodotto: dict, soglia: int = 5) -> bool:
    """
    prodotto.sotto_soglia → True se quantita < soglia

    >>> p = prodotto_crea('SKU001', 'Widget', 29.99, 3)
    >>> prodotto_sotto_soglia(p)
    True
    """
    return confronta.sotto(
        elemento.legge(prodotto, 'quantita'),
        soglia
    )


def prodotto_prezzo_valido(prodotto: dict) -> bool:
    """
    prodotto.prezzo.valido → True se prezzo > 0
    """
    return confronta.maggiore(
        elemento.legge(prodotto, 'prezzo'),
        0
    )


# === TRASFORMAZIONI (pure) ===

def prodotto_applica_sconto(prodotto: dict, percentuale: float) -> dict:
    """
    prodotto.applica_sconto → ritorna prodotto con prezzo scontato

    >>> p = prodotto_crea('SKU001', 'Widget', 100.0, 10)
    >>> p2 = prodotto_applica_sconto(p, 20)
    >>> elemento.legge(p2, 'prezzo')
    80.0
    """
    prezzo_originale = elemento.legge(prodotto, 'prezzo')
    sconto = valore.moltiplica(prezzo_originale, percentuale / 100)
    nuovo_prezzo = valore.decrementa(prezzo_originale, sconto)
    return elemento.scrive(prodotto, 'prezzo', nuovo_prezzo)


def prodotto_decrementa_quantita(prodotto: dict, quantita: int = 1) -> dict:
    """
    prodotto.decrementa_quantita → decrementa stock

    >>> p = prodotto_crea('SKU001', 'Widget', 29.99, 10)
    >>> p2 = prodotto_decrementa_quantita(p, 3)
    >>> elemento.legge(p2, 'quantita')
    7
    """
    attuale = elemento.legge(prodotto, 'quantita')
    nuovo = valore.decrementa(attuale, quantita)
    return elemento.scrive(prodotto, 'quantita', max(0, nuovo))


def prodotto_incrementa_quantita(prodotto: dict, quantita: int) -> dict:
    """
    prodotto.incrementa_quantita → incrementa stock
    """
    attuale = elemento.legge(prodotto, 'quantita')
    nuovo = valore.incrementa(attuale, quantita)
    return elemento.scrive(prodotto, 'quantita', nuovo)


def prodotto_disattiva(prodotto: dict) -> dict:
    """
    prodotto.disattiva → marca come non attivo
    """
    return elemento.scrive(prodotto, 'attivo', False)


# === QUERY (su collezioni) ===

def query_prodotti_disponibili(prodotti: list) -> list:
    """
    ?- prodotti.disponibili

    >>> ps = [prodotto_crea('A', 'A', 10, 5), prodotto_crea('B', 'B', 10, 0)]
    >>> len(query_prodotti_disponibili(ps))
    1
    """
    return contenitore.filtra(prodotti, prodotto_disponibile)


def query_prodotti_sotto_soglia(prodotti: list, soglia: int = 5) -> list:
    """
    ?- prodotti.sotto_soglia
    """
    return contenitore.filtra(
        prodotti,
        lambda p: prodotto_sotto_soglia(p, soglia)
    )


def query_valore_inventario(prodotti: list) -> float:
    """
    ?- inventario.valore_totale

    >>> ps = [prodotto_crea('A', 'A', 10, 5), prodotto_crea('B', 'B', 20, 3)]
    >>> query_valore_inventario(ps)
    110
    """
    valori = contenitore.mappa(
        prodotti,
        lambda p: valore.moltiplica(
            elemento.legge(p, 'prezzo'),
            elemento.legge(p, 'quantita')
        )
    )
    return valore.somma(valori)


# === CELLE COMPOSTE (using flusso) ===

# Cella: verifica e aggiorna stock
verifica_e_aggiorna = flusso.componi(
    # Prima verifica disponibilità
    lambda p: (p, prodotto_disponibile(p)),
    # Poi decrementa se disponibile
    lambda t: flusso.se(
        t[1],  # disponibile?
        lambda: prodotto_decrementa_quantita(t[0]),
        lambda: t[0]  # ritorna invariato
    )
)
