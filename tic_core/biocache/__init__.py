"""
BIOCACHE — Memoria Unificata a 3 Livelli

Gestisce permanenza di DATI e OPERAZIONI con pattern biologico:

LTM (Long Term Memory):
  - Radici, livello 0-2
  - Mai rimosso
  - Archetipi, strutture base

MTM (Medium Term Memory):
  - Livello 3-4
  - Promosso da STM se usato frequentemente

STM (Short Term Memory):
  - Foglie, livello 5+
  - Ring buffer, sovrascrive vecchi
"""

from .cache import BiocCache, LTM, MTM, STM

__all__ = ['BiocCache', 'LTM', 'MTM', 'STM']
