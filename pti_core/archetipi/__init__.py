"""
LIVELLO 1: ARCHETIPI
Funzioni pure, agnostiche. Operazioni universali metafisiche.

"Un mattone resta sempre un mattone."

NOTA: 'effetto' è un BOUNDARY, non puro. Il runtime lo controlla.
"""

from .elemento import elemento
from .contenitore import contenitore
from .confronta import confronta
from .valore import valore
from .testo import testo
from .flusso import flusso
from .effetto import effetto, Effetto, TipoEffetto, RuntimeEffetti, RuntimeEffettiMock

__all__ = [
    'elemento', 'contenitore', 'confronta', 'valore', 'testo',
    'flusso',
    'effetto', 'Effetto', 'TipoEffetto', 'RuntimeEffetti', 'RuntimeEffettiMock'
]
