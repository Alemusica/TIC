"""
PTI — Paradigma Tissutale Interconnesso
Core Implementation

Questo modulo fornisce le primitive per implementare PTI in Python.
"""

from .archetipi import elemento, contenitore, confronta, valore, testo
from .propagazione import Tessuto, propaga_a, fatto, derivato
from .biocache import BiocCache, LTM, MTM, STM

__version__ = "0.1.0"
__all__ = [
    'elemento', 'contenitore', 'confronta', 'valore', 'testo',
    'Tessuto', 'propaga_a', 'fatto', 'derivato',
    'BiocCache', 'LTM', 'MTM', 'STM'
]
