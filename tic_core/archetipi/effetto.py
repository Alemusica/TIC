"""
ARCHETIPO: effetto
Operazioni con side effects - CONTROLLATE DAL RUNTIME.

IMPORTANTE: Questi NON sono puri. Sono BOUNDARY.
Il runtime intercetta ogni effetto e decide se eseguirlo.

effetto.emetti   → emit event (runtime intercepts)
effetto.leggi    → read from source (runtime provides)
effetto.scrivi   → write to sink (runtime controls)
effetto.fallisce → controlled failure
"""

from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar
from dataclasses import dataclass
from enum import Enum

A = TypeVar('A')


class TipoEffetto(Enum):
    """Tipi di effetti supportati."""
    EMIT = 'emit'
    READ = 'read'
    WRITE = 'write'
    LOG = 'log'
    FAIL = 'fail'
    ASYNC = 'async'


@dataclass
class Effetto(Generic[A]):
    """
    Rappresentazione di un effetto.

    L'effetto NON viene eseguito quando creato.
    Il Runtime lo intercetta e decide se/come eseguirlo.
    """
    tipo: TipoEffetto
    payload: Any
    meta: Dict[str, Any] = None

    def __post_init__(self):
        if self.meta is None:
            self.meta = {}


class _EffettoArchetipo:
    """
    Namespace per effetti controllati.

    NOTA: Questi metodi CREANO descrizioni di effetti.
    Il RUNTIME li esegue (o li blocca).
    """

    @staticmethod
    def emetti(evento: str, dati: Any = None) -> Effetto:
        """
        effetto.emetti → crea un effetto di emissione evento

        >>> e = effetto.emetti('order.created', {'id': 123})
        >>> e.tipo
        <TipoEffetto.EMIT: 'emit'>

        NOTA: Questo NON emette nulla. Crea una descrizione.
        Il runtime decide se propagare l'evento.
        """
        return Effetto(
            tipo=TipoEffetto.EMIT,
            payload={'evento': evento, 'dati': dati}
        )

    @staticmethod
    def leggi(sorgente: str, query: Any = None) -> Effetto:
        """
        effetto.leggi → crea un effetto di lettura

        >>> e = effetto.leggi('database', {'table': 'users'})
        >>> e.tipo
        <TipoEffetto.READ: 'read'>

        NOTA: Questo NON legge nulla. Il runtime fornisce i dati.
        """
        return Effetto(
            tipo=TipoEffetto.READ,
            payload={'sorgente': sorgente, 'query': query}
        )

    @staticmethod
    def scrivi(destinazione: str, dati: Any) -> Effetto:
        """
        effetto.scrivi → crea un effetto di scrittura

        >>> e = effetto.scrivi('file', {'path': '/tmp/x', 'content': 'hello'})
        >>> e.tipo
        <TipoEffetto.WRITE: 'write'>

        NOTA: Questo NON scrive nulla. Il runtime decide se permetterlo.
        """
        return Effetto(
            tipo=TipoEffetto.WRITE,
            payload={'destinazione': destinazione, 'dati': dati}
        )

    @staticmethod
    def log(livello: str, messaggio: str, contesto: Dict = None) -> Effetto:
        """
        effetto.log → crea un effetto di logging

        >>> e = effetto.log('info', 'Operazione completata')
        >>> e.tipo
        <TipoEffetto.LOG: 'log'>
        """
        return Effetto(
            tipo=TipoEffetto.LOG,
            payload={
                'livello': livello,
                'messaggio': messaggio,
                'contesto': contesto or {}
            }
        )

    @staticmethod
    def fallisce(motivo: str, codice: str = None) -> Effetto:
        """
        effetto.fallisce → crea un effetto di fallimento controllato

        >>> e = effetto.fallisce('Utente non trovato', 'USER_NOT_FOUND')
        >>> e.tipo
        <TipoEffetto.FAIL: 'fail'>

        NOTA: Il runtime decide come gestire il fallimento.
        """
        return Effetto(
            tipo=TipoEffetto.FAIL,
            payload={'motivo': motivo, 'codice': codice}
        )

    @staticmethod
    def attendi(millisecondi: int) -> Effetto:
        """
        effetto.attendi → crea un effetto di attesa

        >>> e = effetto.attendi(1000)
        >>> e.tipo
        <TipoEffetto.ASYNC: 'async'>
        """
        return Effetto(
            tipo=TipoEffetto.ASYNC,
            payload={'tipo': 'delay', 'ms': millisecondi}
        )

    @staticmethod
    def catena(*effetti: Effetto) -> List[Effetto]:
        """
        effetto.catena → sequenza di effetti

        >>> es = effetto.catena(
        ...     effetto.log('info', 'start'),
        ...     effetto.emetti('done')
        ... )
        >>> len(es)
        2
        """
        return list(effetti)

    @staticmethod
    def puro(valore: A) -> A:
        """
        effetto.puro → wrappa un valore puro (nessun effetto)

        Utile per uniformare interfacce.
        """
        return valore


# Singleton
effetto = _EffettoArchetipo()


# === Runtime Interface ===

class RuntimeEffetti:
    """
    Interfaccia che il Runtime deve implementare per gestire effetti.

    Il Runtime INTERCETTA ogni Effetto e decide:
    - Se è permesso
    - Come eseguirlo
    - Cosa loggare nell'audit trail
    """

    def esegui(self, eff: Effetto) -> Any:
        """Esegue un effetto. Override nel runtime reale."""
        raise NotImplementedError("Il runtime deve implementare esegui()")

    def permesso(self, eff: Effetto) -> bool:
        """Verifica se l'effetto è permesso."""
        raise NotImplementedError("Il runtime deve implementare permesso()")

    def audit(self, eff: Effetto, risultato: Any) -> None:
        """Registra l'effetto nell'audit trail."""
        raise NotImplementedError("Il runtime deve implementare audit()")


class RuntimeEffettiMock(RuntimeEffetti):
    """
    Runtime mock per testing.
    Permette tutti gli effetti e li logga.
    """

    def __init__(self):
        self.log: List[Dict] = []
        self.permessi: Dict[TipoEffetto, bool] = {t: True for t in TipoEffetto}

    def esegui(self, eff: Effetto) -> Any:
        if not self.permesso(eff):
            raise PermissionError(f"Effetto {eff.tipo} non permesso")

        risultato = self._esegui_interno(eff)
        self.audit(eff, risultato)
        return risultato

    def _esegui_interno(self, eff: Effetto) -> Any:
        """Esecuzione mock."""
        if eff.tipo == TipoEffetto.EMIT:
            return {'emesso': eff.payload['evento']}
        elif eff.tipo == TipoEffetto.READ:
            return {'dati': 'mock_data'}
        elif eff.tipo == TipoEffetto.WRITE:
            return {'scritto': True}
        elif eff.tipo == TipoEffetto.LOG:
            print(f"[{eff.payload['livello']}] {eff.payload['messaggio']}")
            return None
        elif eff.tipo == TipoEffetto.FAIL:
            raise Exception(eff.payload['motivo'])
        elif eff.tipo == TipoEffetto.ASYNC:
            return {'atteso': eff.payload.get('ms', 0)}
        return None

    def permesso(self, eff: Effetto) -> bool:
        return self.permessi.get(eff.tipo, False)

    def audit(self, eff: Effetto, risultato: Any) -> None:
        self.log.append({
            'tipo': eff.tipo.value,
            'payload': eff.payload,
            'risultato': risultato
        })

    def nega(self, tipo: TipoEffetto) -> None:
        """Nega un tipo di effetto (per testing)."""
        self.permessi[tipo] = False
