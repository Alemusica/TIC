"""
MOLECOLA: carrello
Regole per gestione carrello.

Dimostra:
- Composizione funzionale pura
- Pattern matching con flusso.scegli
- Operazioni su collezioni
"""

import sys
sys.path.insert(0, '../../../')

from pti_core.archetipi import elemento, contenitore, confronta, valore, flusso


# === FATTI ===

def carrello_crea(utente_id: str = None) -> dict:
    """
    carrello.crea → crea nuovo carrello

    >>> c = carrello_crea('user123')
    >>> elemento.legge(c, 'items')
    []
    """
    return elemento.crea({
        'utente_id': utente_id,
        'items': [],
        'stato': 'attivo'
    })


def item_carrello_crea(prodotto_sku: str, quantita: int, prezzo_unitario: float) -> dict:
    """
    item_carrello.crea → crea item per carrello
    """
    return elemento.crea({
        'prodotto_sku': prodotto_sku,
        'quantita': quantita,
        'prezzo_unitario': prezzo_unitario
    })


# === REGOLE ===

def carrello_vuoto(carrello: dict) -> bool:
    """
    carrello.vuoto → True se nessun item
    """
    items = elemento.legge(carrello, 'items')
    return contenitore.vuoto(items)


def carrello_contiene(carrello: dict, sku: str) -> bool:
    """
    carrello.contiene → True se sku presente
    """
    items = elemento.legge(carrello, 'items')
    trovato = contenitore.trova(
        items,
        lambda i: confronta.uguale(elemento.legge(i, 'prodotto_sku'), sku)
    )
    return confronta.non_nullo(trovato)


def carrello_attivo(carrello: dict) -> bool:
    """
    carrello.attivo → True se stato è 'attivo'
    """
    return confronta.uguale(
        elemento.legge(carrello, 'stato'),
        'attivo'
    )


# === TRASFORMAZIONI ===

def carrello_aggiungi(carrello: dict, sku: str, quantita: int, prezzo: float) -> dict:
    """
    carrello.aggiungi → aggiunge item o incrementa quantita esistente

    >>> c = carrello_crea()
    >>> c = carrello_aggiungi(c, 'SKU001', 2, 10.0)
    >>> len(elemento.legge(c, 'items'))
    1
    """
    items = elemento.legge(carrello, 'items')

    # Cerca item esistente
    esistente_idx = None
    for i, item in enumerate(items):
        if elemento.legge(item, 'prodotto_sku') == sku:
            esistente_idx = i
            break

    if esistente_idx is not None:
        # Incrementa quantità esistente
        item = items[esistente_idx]
        nuova_qty = valore.incrementa(
            elemento.legge(item, 'quantita'),
            quantita
        )
        nuovo_item = elemento.scrive(item, 'quantita', nuova_qty)
        nuovi_items = items[:esistente_idx] + [nuovo_item] + items[esistente_idx + 1:]
    else:
        # Aggiungi nuovo item
        nuovo_item = item_carrello_crea(sku, quantita, prezzo)
        nuovi_items = contenitore.aggiunge(items, nuovo_item)

    return elemento.scrive(carrello, 'items', nuovi_items)


def carrello_rimuovi(carrello: dict, sku: str) -> dict:
    """
    carrello.rimuovi → rimuove item per sku
    """
    items = elemento.legge(carrello, 'items')
    nuovi_items = contenitore.filtra(
        items,
        lambda i: confronta.diverso(elemento.legge(i, 'prodotto_sku'), sku)
    )
    return elemento.scrive(carrello, 'items', nuovi_items)


def carrello_svuota(carrello: dict) -> dict:
    """
    carrello.svuota → rimuove tutti gli items
    """
    return elemento.scrive(carrello, 'items', [])


def carrello_checkout(carrello: dict) -> dict:
    """
    carrello.checkout → cambia stato in 'checkout'
    """
    return elemento.scrive(carrello, 'stato', 'checkout')


# === QUERY ===

def query_carrello_totale(carrello: dict) -> float:
    """
    ?- carrello.totale

    >>> c = carrello_crea()
    >>> c = carrello_aggiungi(c, 'A', 2, 10.0)
    >>> c = carrello_aggiungi(c, 'B', 1, 25.0)
    >>> query_carrello_totale(c)
    45.0
    """
    items = elemento.legge(carrello, 'items')

    subtotali = contenitore.mappa(
        items,
        lambda i: valore.moltiplica(
            elemento.legge(i, 'quantita'),
            elemento.legge(i, 'prezzo_unitario')
        )
    )

    return valore.somma(subtotali)


def query_carrello_num_items(carrello: dict) -> int:
    """
    ?- carrello.num_items

    >>> c = carrello_crea()
    >>> c = carrello_aggiungi(c, 'A', 3, 10.0)
    >>> c = carrello_aggiungi(c, 'B', 2, 5.0)
    >>> query_carrello_num_items(c)
    5
    """
    items = elemento.legge(carrello, 'items')
    quantita = contenitore.mappa(items, lambda i: elemento.legge(i, 'quantita'))
    return valore.somma(quantita)


# === CELLE COMPOSTE ===

# Cella: calcola totale con sconto percentuale
def cella_totale_scontato(percentuale_sconto: float):
    """
    Ritorna una cella che calcola totale con sconto.

    >>> calcola = cella_totale_scontato(10)  # 10% sconto
    >>> c = carrello_crea()
    >>> c = carrello_aggiungi(c, 'A', 1, 100.0)
    >>> calcola(c)
    90.0
    """
    return flusso.componi(
        query_carrello_totale,
        lambda totale: valore.moltiplica(totale, (100 - percentuale_sconto) / 100)
    )


# Cella: applica logica di spedizione gratuita
def cella_spedizione(soglia_gratis: float = 50.0, costo_spedizione: float = 5.0):
    """
    Ritorna cella che calcola costo spedizione.

    >>> calcola = cella_spedizione(soglia_gratis=50, costo_spedizione=5)
    >>> c = carrello_crea()
    >>> c = carrello_aggiungi(c, 'A', 1, 60.0)
    >>> calcola(c)
    0
    """
    return flusso.componi(
        query_carrello_totale,
        lambda totale: flusso.se(
            confronta.almeno(totale, soglia_gratis),
            flusso.costante(0),
            flusso.costante(costo_spedizione)
        )
    )


# Cella: calcola totale finale (subtotale + spedizione)
def cella_totale_finale(soglia_gratis: float = 50.0, costo_spedizione: float = 5.0):
    """
    Cella composta: totale + spedizione
    """
    calc_spedizione = cella_spedizione(soglia_gratis, costo_spedizione)

    return lambda carrello: valore.somma([
        query_carrello_totale(carrello),
        calc_spedizione(carrello)
    ])
