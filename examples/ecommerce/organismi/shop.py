"""
ORGANISMO: shop
Entry point per e-commerce.

Dimostra:
- Composizione di molecole
- Runtime che gestisce effetti
- Audit trail
"""

import sys
import os
# Aggiungi path per imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tic_core.archetipi import (
    elemento, contenitore, confronta, valore, flusso,
    effetto, Effetto, RuntimeEffettiMock
)
from molecole import prodotto, carrello, ordine


class Shop:
    """
    Organismo Shop.

    Gestisce:
    - Catalogo prodotti
    - Carrelli utenti
    - Ordini
    - Effetti (tramite runtime)
    """

    def __init__(self, nome: str):
        self.nome = nome
        self.prodotti = []
        self.carrelli = {}  # utente_id → carrello
        self.ordini = []

        # Runtime per gestione effetti
        self.runtime = RuntimeEffettiMock()

    # === CATALOGO ===

    def aggiungi_prodotto(self, sku: str, nome: str, prezzo: float, qty: int) -> dict:
        """shop.aggiungi_prodotto"""
        p = prodotto.prodotto_crea(sku, nome, prezzo, qty)
        self.prodotti.append(p)
        return p

    def trova_prodotto(self, sku: str) -> dict:
        """shop.trova_prodotto"""
        return contenitore.trova(
            self.prodotti,
            lambda p: confronta.uguale(elemento.legge(p, 'sku'), sku)
        )

    # === CARRELLO ===

    def ottieni_carrello(self, utente_id: str) -> dict:
        """shop.ottieni_carrello → crea o ritorna carrello esistente"""
        if utente_id not in self.carrelli:
            self.carrelli[utente_id] = carrello.carrello_crea(utente_id)
        return self.carrelli[utente_id]

    def aggiungi_a_carrello(self, utente_id: str, sku: str, quantita: int = 1) -> tuple:
        """
        shop.aggiungi_a_carrello

        Ritorna (successo, carrello | errore)
        """
        # Trova prodotto
        p = self.trova_prodotto(sku)
        if p is None:
            return (False, 'Prodotto non trovato')

        # Verifica disponibilità
        if not prodotto.prodotto_disponibile(p):
            return (False, 'Prodotto non disponibile')

        # Verifica quantità sufficiente
        qty_disponibile = elemento.legge(p, 'quantita')
        if qty_disponibile < quantita:
            return (False, f'Solo {qty_disponibile} disponibili')

        # Aggiungi a carrello
        c = self.ottieni_carrello(utente_id)
        prezzo = elemento.legge(p, 'prezzo')
        c = carrello.carrello_aggiungi(c, sku, quantita, prezzo)
        self.carrelli[utente_id] = c

        return (True, c)

    def rimuovi_da_carrello(self, utente_id: str, sku: str) -> dict:
        """shop.rimuovi_da_carrello"""
        c = self.ottieni_carrello(utente_id)
        c = carrello.carrello_rimuovi(c, sku)
        self.carrelli[utente_id] = c
        return c

    # === CHECKOUT ===

    def checkout(self, utente_id: str, metodo_pagamento: str) -> tuple:
        """
        shop.checkout → processa ordine completo

        Ritorna (successo, ordine | errore, audit_log)
        """
        c = self.ottieni_carrello(utente_id)

        # Esegui flow checkout
        ord, effetti = ordine.flow_checkout(c, metodo_pagamento)

        # Processa effetti tramite runtime
        for eff in effetti:
            try:
                self.runtime.esegui(eff)
            except Exception as e:
                # Effetto fallito - ritorna errore
                return (False, str(e), self.runtime.log)

        if ord is None:
            return (False, 'Checkout fallito', self.runtime.log)

        # Aggiorna inventario
        items = elemento.legge(ord, 'items')
        for item in items:
            sku = elemento.legge(item, 'prodotto_sku')
            qty = elemento.legge(item, 'quantita')
            self._decrementa_stock(sku, qty)

        # Salva ordine e svuota carrello
        self.ordini.append(ord)
        self.carrelli[utente_id] = carrello.carrello_svuota(c)

        return (True, ord, self.runtime.log)

    def _decrementa_stock(self, sku: str, quantita: int) -> None:
        """Helper: decrementa stock prodotto"""
        for i, p in enumerate(self.prodotti):
            if elemento.legge(p, 'sku') == sku:
                self.prodotti[i] = prodotto.prodotto_decrementa_quantita(p, quantita)
                break

    # === QUERY ===

    def stato_shop(self) -> dict:
        """shop.stato → stato attuale"""
        disponibili = prodotto.query_prodotti_disponibili(self.prodotti)
        sotto_soglia = prodotto.query_prodotti_sotto_soglia(self.prodotti)

        return {
            'nome': self.nome,
            'prodotti_totali': len(self.prodotti),
            'prodotti_disponibili': len(disponibili),
            'prodotti_sotto_soglia': len(sotto_soglia),
            'valore_inventario': prodotto.query_valore_inventario(self.prodotti),
            'ordini_totali': len(self.ordini),
            'vendite_totali': ordine.query_totale_vendite(self.ordini),
            'carrelli_attivi': len([c for c in self.carrelli.values()
                                   if not carrello.carrello_vuoto(c)])
        }

    def ordini_utente(self, utente_id: str) -> list:
        """shop.ordini_utente"""
        return ordine.query_ordini_utente(self.ordini, utente_id)

    def audit_log(self) -> list:
        """shop.audit_log → log di tutti gli effetti eseguiti"""
        return self.runtime.log


# === Funzioni stateless ===

def shop_crea(nome: str) -> Shop:
    """shop.crea"""
    return Shop(nome)
