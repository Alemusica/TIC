"""
TESSUTO — Sistema di Propagazione Reattiva

Implementa il pattern di esistenza derivata:
- FATTI BASE: valori primitivi
- FATTI DERIVATI: calcolati da fatti base, cachati
- PROPAGAZIONE: quando un fatto base cambia, i derivati si aggiornano

Esempio:
    tessuto = Tessuto()

    # Fatto base
    @tessuto.fatto('tavolo.1.stato')
    def _():
        return 'libero'

    # Fatto derivato (dipende da tavolo.*.stato)
    @tessuto.derivato('tavoli.liberi', dipende_da=['tavolo.*.stato'])
    def _():
        return [t for t in tavoli if t.stato == 'libero']

    # Quando tavolo.1.stato cambia → tavoli.liberi si aggiorna
"""

from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from functools import wraps
import re
from collections import defaultdict


@dataclass
class Nodo:
    """Un nodo nel tessuto (fatto o derivato)."""
    nome: str
    valore: Any = None
    calcolatore: Callable = None
    dipendenze: List[str] = field(default_factory=list)
    dipendenti: Set[str] = field(default_factory=set)
    è_derivato: bool = False
    sporco: bool = True  # True = deve essere ricalcolato
    salti: List[str] = field(default_factory=list)  # SALTO connections

    def __hash__(self):
        return hash(self.nome)


class Tessuto:
    """
    Il Tessuto è il grafo di propagazione.
    Gestisce fatti base, derivati e le connessioni tra loro.
    """

    def __init__(self):
        self._nodi: Dict[str, Nodo] = {}
        self._pattern_dipendenze: Dict[str, List[str]] = defaultdict(list)
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)
        self._batch_mode = False
        self._pending_propagations: Set[str] = set()

    def fatto(self, nome: str, salti: List[str] = None):
        """
        Decoratore per definire un fatto base.

        @tessuto.fatto('tavolo.1.stato')
        def _():
            return 'libero'
        """
        def decorator(func: Callable):
            nodo = Nodo(
                nome=nome,
                calcolatore=func,
                è_derivato=False,
                salti=salti or []
            )
            self._nodi[nome] = nodo
            # Calcola valore iniziale
            nodo.valore = func()
            nodo.sporco = False
            return func
        return decorator

    def derivato(self, nome: str, dipende_da: List[str], salti: List[str] = None):
        """
        Decoratore per definire un fatto derivato.

        @tessuto.derivato('tavoli.liberi', dipende_da=['tavolo.*.stato'])
        def calcola():
            return [t for t in tavoli if t.stato == 'libero']
        """
        def decorator(func: Callable):
            nodo = Nodo(
                nome=nome,
                calcolatore=func,
                dipendenze=dipende_da,
                è_derivato=True,
                salti=salti or []
            )
            self._nodi[nome] = nodo

            # Registra dipendenze (supporta pattern con *)
            for dip in dipende_da:
                if '*' in dip:
                    self._pattern_dipendenze[dip].append(nome)
                else:
                    if dip in self._nodi:
                        self._nodi[dip].dipendenti.add(nome)

            return func
        return decorator

    def imposta(self, nome: str, valore: Any) -> None:
        """
        Imposta un fatto base e propaga le modifiche.

        tessuto.imposta('tavolo.1.stato', 'occupato')
        """
        if nome not in self._nodi:
            # Crea nodo al volo se non esiste
            self._nodi[nome] = Nodo(nome=nome, è_derivato=False)

        nodo = self._nodi[nome]
        if nodo.è_derivato:
            raise ValueError(f"Non puoi impostare direttamente un derivato: {nome}")

        vecchio = nodo.valore
        nodo.valore = valore

        if vecchio != valore:
            self._propaga(nome)
            self._notifica_listeners(nome, vecchio, valore)

    def legge(self, nome: str) -> Any:
        """
        Legge un valore (base o derivato).
        Se derivato è sporco, lo ricalcola.

        stato = tessuto.legge('tavoli.liberi')
        """
        if nome not in self._nodi:
            return None

        nodo = self._nodi[nome]

        if nodo.è_derivato and nodo.sporco:
            # Ricalcola il derivato
            nodo.valore = nodo.calcolatore()
            nodo.sporco = False

        return nodo.valore

    def _propaga(self, nome: str) -> None:
        """Propaga il cambiamento ai nodi dipendenti."""
        if self._batch_mode:
            self._pending_propagations.add(nome)
            return

        da_aggiornare = self._trova_dipendenti(nome)

        for dep_nome in da_aggiornare:
            if dep_nome in self._nodi:
                self._nodi[dep_nome].sporco = True

        # Propaga ai SALTI
        nodo = self._nodi.get(nome)
        if nodo and nodo.salti:
            for salto in nodo.salti:
                self._notifica_salto(salto, nome)

    def _trova_dipendenti(self, nome: str) -> Set[str]:
        """Trova tutti i nodi che dipendono da questo (diretto + pattern)."""
        dipendenti = set()

        # Dipendenti diretti
        if nome in self._nodi:
            dipendenti.update(self._nodi[nome].dipendenti)

        # Dipendenti via pattern
        for pattern, nomi_dep in self._pattern_dipendenze.items():
            if self._match_pattern(nome, pattern):
                dipendenti.update(nomi_dep)

        return dipendenti

    def _match_pattern(self, nome: str, pattern: str) -> bool:
        """Verifica se un nome matcha un pattern con *."""
        regex = pattern.replace('.', r'\.').replace('*', r'[^.]+')
        return bool(re.match(f'^{regex}$', nome))

    def _notifica_salto(self, target: str, sorgente: str) -> None:
        """Notifica un SALTO (connessione non gerarchica)."""
        for listener in self._listeners.get(target, []):
            listener(sorgente)

    def _notifica_listeners(self, nome: str, vecchio: Any, nuovo: Any) -> None:
        """Notifica i listener registrati."""
        for listener in self._listeners.get(nome, []):
            listener(vecchio, nuovo)

    def ascolta(self, nome: str, callback: Callable) -> None:
        """
        Registra un listener per cambiamenti.

        tessuto.ascolta('tavolo.*.stato', lambda v, n: print(f'{v} → {n}'))
        """
        self._listeners[nome].append(callback)

    def batch(self):
        """
        Context manager per modifiche in batch.
        La propagazione avviene alla fine.

        with tessuto.batch():
            tessuto.imposta('a', 1)
            tessuto.imposta('b', 2)
            # propagazione avviene qui
        """
        return _BatchContext(self)

    def query(self, pattern: str) -> Dict[str, Any]:
        """
        Query tutti i nodi che matchano un pattern.

        tutti_tavoli = tessuto.query('tavolo.*.stato')
        """
        risultati = {}
        for nome, nodo in self._nodi.items():
            if self._match_pattern(nome, pattern):
                risultati[nome] = self.legge(nome)
        return risultati

    def grafo(self) -> Dict[str, List[str]]:
        """Ritorna il grafo delle dipendenze."""
        return {
            nome: list(nodo.dipendenti)
            for nome, nodo in self._nodi.items()
        }


class _BatchContext:
    """Context manager per batch updates."""

    def __init__(self, tessuto: Tessuto):
        self._tessuto = tessuto

    def __enter__(self):
        self._tessuto._batch_mode = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tessuto._batch_mode = False
        # Propaga tutte le modifiche pending
        for nome in self._tessuto._pending_propagations:
            self._tessuto._propaga(nome)
        self._tessuto._pending_propagations.clear()


# === Funzioni di convenienza ===

_tessuto_globale = Tessuto()


def fatto(nome: str, salti: List[str] = None):
    """Decoratore per fatto nel tessuto globale."""
    return _tessuto_globale.fatto(nome, salti)


def derivato(nome: str, dipende_da: List[str], salti: List[str] = None):
    """Decoratore per derivato nel tessuto globale."""
    return _tessuto_globale.derivato(nome, dipende_da, salti)


def imposta(nome: str, valore: Any) -> None:
    """Imposta nel tessuto globale."""
    _tessuto_globale.imposta(nome, valore)


def legge(nome: str) -> Any:
    """Legge dal tessuto globale."""
    return _tessuto_globale.legge(nome)


def propaga_a(targets: List[str]) -> None:
    """Notifica manualmente dei target (per SALTO espliciti)."""
    for target in targets:
        _tessuto_globale._notifica_salto(target, 'manual')
