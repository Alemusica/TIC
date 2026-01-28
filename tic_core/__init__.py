"""
TIC — Tessuto Interconnesso Computante
       Tissular Interconnected Code

Core Implementation - Safe algebra for LLM-generated code.
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
