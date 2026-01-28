"""
BIOCACHE — Implementazione

Sistema di memoria a 3 livelli con promozione/demozione automatica.

Uso:
    cache = BiocCache()

    # Scrittura (automaticamente in STM)
    cache.scrivi('ordine.123.totale', 150.00)

    # Lettura (incrementa contatore accessi)
    totale = cache.leggi('ordine.123.totale')

    # Promozione automatica se soglia raggiunta
    # STM → MTM → LTM
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from collections import OrderedDict
from enum import Enum
from datetime import datetime
import time


class Livello(Enum):
    """Livelli di memoria."""
    LTM = 1  # Long Term Memory
    MTM = 2  # Medium Term Memory
    STM = 3  # Short Term Memory


# Costanti di default
LTM = Livello.LTM
MTM = Livello.MTM
STM = Livello.STM


@dataclass
class Voce:
    """Una voce in cache."""
    chiave: str
    valore: Any
    livello: Livello = STM
    accessi: int = 0
    creato: float = field(default_factory=time.time)
    ultimo_accesso: float = field(default_factory=time.time)
    profondita: int = 0  # profondità gerarchica (conta i '.')

    def __post_init__(self):
        self.profondita = self.chiave.count('.')


class BiocCache:
    """
    Cache biologica a 3 livelli con promozione automatica.

    Configurazione:
        stm_size: dimensione ring buffer STM
        mtm_size: dimensione MTM
        soglia_promozione_mtm: accessi per promuovere STM → MTM
        soglia_promozione_ltm: accessi per promuovere MTM → LTM
        cicli_demozione: cicli senza accesso per demozionare
    """

    def __init__(
        self,
        stm_size: int = 1000,
        mtm_size: int = 500,
        soglia_promozione_mtm: int = 10,
        soglia_promozione_ltm: int = 100,
        cicli_demozione: int = 50
    ):
        self._stm: OrderedDict[str, Voce] = OrderedDict()
        self._mtm: Dict[str, Voce] = {}
        self._ltm: Dict[str, Voce] = {}

        self._stm_size = stm_size
        self._mtm_size = mtm_size
        self._soglia_mtm = soglia_promozione_mtm
        self._soglia_ltm = soglia_promozione_ltm
        self._cicli_demozione = cicli_demozione

        self._ciclo_corrente = 0
        self._storia: List[str] = []  # buffer storia operazioni
        self._storia_max = 100

    def scrivi(self, chiave: str, valore: Any, livello: Livello = None) -> None:
        """
        Scrive un valore in cache.

        Se livello non specificato, va in STM (tranne chiavi brevi → LTM).
        """
        # Determina livello automatico basato su profondità
        if livello is None:
            profondita = chiave.count('.')
            if profondita <= 1:
                livello = LTM  # archetipi
            elif profondita <= 3:
                livello = MTM  # molecole
            else:
                livello = STM  # foglie

        voce = Voce(chiave=chiave, valore=valore, livello=livello)

        if livello == LTM:
            self._ltm[chiave] = voce
        elif livello == MTM:
            self._mtm[chiave] = voce
            self._evict_mtm_se_necessario()
        else:
            self._stm[chiave] = voce
            self._stm.move_to_end(chiave)
            self._evict_stm_se_necessario()

        self._registra_storia(chiave)

    def leggi(self, chiave: str) -> Optional[Any]:
        """
        Legge un valore dalla cache.

        Cerca in ordine: LTM → MTM → STM.
        Incrementa contatore accessi e valuta promozione.
        """
        voce = self._trova(chiave)

        if voce is None:
            return None

        # Aggiorna statistiche
        voce.accessi += 1
        voce.ultimo_accesso = time.time()

        # Valuta promozione
        self._valuta_promozione(voce)

        self._registra_storia(chiave)
        return voce.valore

    def _trova(self, chiave: str) -> Optional[Voce]:
        """Trova voce in qualsiasi livello."""
        # LTM ha priorità (sempre disponibile)
        if chiave in self._ltm:
            return self._ltm[chiave]
        if chiave in self._mtm:
            return self._mtm[chiave]
        if chiave in self._stm:
            self._stm.move_to_end(chiave)  # LRU
            return self._stm[chiave]
        return None

    def esiste(self, chiave: str) -> bool:
        """Verifica se chiave esiste (e non è soft-deleted)."""
        voce = self._trova(chiave)
        if voce is None:
            return False
        # LTM soft delete: valore = None
        return voce.valore is not None

    def elimina(self, chiave: str) -> bool:
        """Elimina da cache."""
        if chiave in self._stm:
            del self._stm[chiave]
            return True
        if chiave in self._mtm:
            del self._mtm[chiave]
            return True
        # LTM non si elimina (solo soft delete)
        if chiave in self._ltm:
            self._ltm[chiave].valore = None
            return True
        return False

    def _valuta_promozione(self, voce: Voce) -> None:
        """Valuta se promuovere la voce."""
        if voce.livello == STM and voce.accessi >= self._soglia_mtm:
            self._promuovi(voce, MTM)
        elif voce.livello == MTM and voce.accessi >= self._soglia_ltm:
            self._promuovi(voce, LTM)

    def _promuovi(self, voce: Voce, nuovo_livello: Livello) -> None:
        """Promuove una voce a un livello superiore."""
        chiave = voce.chiave
        vecchio_livello = voce.livello

        # Rimuovi dal vecchio livello
        if vecchio_livello == STM and chiave in self._stm:
            del self._stm[chiave]
        elif vecchio_livello == MTM and chiave in self._mtm:
            del self._mtm[chiave]

        # Aggiungi al nuovo livello
        voce.livello = nuovo_livello
        if nuovo_livello == MTM:
            self._mtm[chiave] = voce
            self._evict_mtm_se_necessario()
        elif nuovo_livello == LTM:
            self._ltm[chiave] = voce

    def _evict_stm_se_necessario(self) -> None:
        """Rimuove voci vecchie da STM se pieno (ring buffer)."""
        while len(self._stm) > self._stm_size:
            # Rimuovi il più vecchio (FIFO)
            self._stm.popitem(last=False)

    def _evict_mtm_se_necessario(self) -> None:
        """Rimuove voci meno usate da MTM se pieno."""
        while len(self._mtm) > self._mtm_size:
            # Trova il meno acceduto
            min_voce = min(self._mtm.values(), key=lambda v: v.accessi)
            del self._mtm[min_voce.chiave]

    def _registra_storia(self, chiave: str) -> None:
        """Registra operazione nel buffer storia."""
        self._storia.append(chiave)
        if len(self._storia) > self._storia_max:
            self._storia.pop(0)

    def ciclo(self) -> None:
        """
        Esegue un ciclo di manutenzione.

        - Valuta demozioni
        - Incrementa contatore ciclo
        """
        self._ciclo_corrente += 1

        # Valuta demozioni in MTM
        da_demozionare = []
        for chiave, voce in self._mtm.items():
            cicli_inattivo = self._ciclo_corrente - int(voce.ultimo_accesso)
            if cicli_inattivo > self._cicli_demozione:
                da_demozionare.append(chiave)

        for chiave in da_demozionare:
            voce = self._mtm.pop(chiave)
            voce.livello = STM
            voce.accessi = 0  # reset
            self._stm[chiave] = voce

    def storia_recente(self, n: int = 10) -> List[str]:
        """Ritorna le ultime n operazioni."""
        return self._storia[-n:]

    def statistiche(self) -> Dict[str, Any]:
        """Ritorna statistiche della cache."""
        return {
            'ltm_count': len(self._ltm),
            'mtm_count': len(self._mtm),
            'stm_count': len(self._stm),
            'ciclo': self._ciclo_corrente,
            'ltm_keys': list(self._ltm.keys())[:10],
            'mtm_top': sorted(
                self._mtm.values(),
                key=lambda v: v.accessi,
                reverse=True
            )[:5] if self._mtm else [],
        }

    def query_pattern(self, pattern: str) -> Dict[str, Any]:
        """
        Query tutte le chiavi che matchano un pattern.

        cache.query_pattern('tavolo.*.stato')
        """
        import re
        regex = pattern.replace('.', r'\.').replace('*', r'[^.]+')
        risultati = {}

        for store in [self._ltm, self._mtm, self._stm]:
            for chiave, voce in store.items():
                if re.match(f'^{regex}$', chiave):
                    risultati[chiave] = voce.valore

        return risultati

    def peso_contesto(self, chiave: str) -> float:
        """
        Calcola il peso topologico di una chiave.

        Chiavi più vicine alla radice hanno peso maggiore.
        """
        profondita = chiave.count('.')
        return 1.0 / (profondita + 1)


# === Cache globale ===
_cache_globale = BiocCache()


def scrivi(chiave: str, valore: Any, livello: Livello = None) -> None:
    """Scrivi nella cache globale."""
    _cache_globale.scrivi(chiave, valore, livello)


def leggi(chiave: str) -> Any:
    """Leggi dalla cache globale."""
    return _cache_globale.leggi(chiave)
