"""
ARCHETIPO: testo
Operazioni su stringhe/testo.

testo.pulisce      → strip + normalizza
testo.maiuscolo    → upper
testo.minuscolo    → lower
testo.contiene     → substring check
testo.inizia       → startswith
testo.finisce      → endswith
testo.divide       → split
testo.unisce       → join
testo.sostituisce  → replace
testo.vuoto        → is empty
testo.lunghezza    → len
"""

from typing import List, Optional
import re


class _TestoArchetipo:
    """
    Namespace per operazioni su testo.
    Uso: testo.pulisce('  hello  ')
    """

    @staticmethod
    def pulisce(s: str) -> str:
        """
        testo.pulisce → strip + normalizza spazi multipli

        >>> testo.pulisce('  hello   world  ')
        'hello world'
        """
        if s is None:
            return ''
        return ' '.join(s.split())

    @staticmethod
    def maiuscolo(s: str) -> str:
        """
        testo.maiuscolo → UPPER

        >>> testo.maiuscolo('hello')
        'HELLO'
        """
        return s.upper() if s else ''

    @staticmethod
    def minuscolo(s: str) -> str:
        """
        testo.minuscolo → lower
        """
        return s.lower() if s else ''

    @staticmethod
    def capitalizza(s: str) -> str:
        """
        testo.capitalizza → Prima Lettera Maiuscola

        >>> testo.capitalizza('hello world')
        'Hello World'
        """
        return s.title() if s else ''

    @staticmethod
    def contiene(s: str, sottostringa: str) -> bool:
        """
        testo.contiene → True se contiene sottostringa

        >>> testo.contiene('hello world', 'wor')
        True
        """
        if not s or not sottostringa:
            return False
        return sottostringa in s

    @staticmethod
    def inizia(s: str, prefisso: str) -> bool:
        """
        testo.inizia → startswith
        """
        if not s:
            return False
        return s.startswith(prefisso)

    @staticmethod
    def finisce(s: str, suffisso: str) -> bool:
        """
        testo.finisce → endswith
        """
        if not s:
            return False
        return s.endswith(suffisso)

    @staticmethod
    def divide(s: str, separatore: str = ' ') -> List[str]:
        """
        testo.divide → split

        >>> testo.divide('a,b,c', ',')
        ['a', 'b', 'c']
        """
        if not s:
            return []
        return s.split(separatore)

    @staticmethod
    def unisce(parti: List[str], separatore: str = '') -> str:
        """
        testo.unisce → join

        >>> testo.unisce(['a', 'b', 'c'], '-')
        'a-b-c'
        """
        return separatore.join(parti)

    @staticmethod
    def sostituisce(s: str, vecchio: str, nuovo: str) -> str:
        """
        testo.sostituisce → replace

        >>> testo.sostituisce('hello world', 'world', 'PTI')
        'hello PTI'
        """
        if not s:
            return ''
        return s.replace(vecchio, nuovo)

    @staticmethod
    def vuoto(s: str) -> bool:
        """
        testo.vuoto → True se vuoto o solo spazi

        >>> testo.vuoto('')
        True
        >>> testo.vuoto('   ')
        True
        >>> testo.vuoto('a')
        False
        """
        return not s or not s.strip()

    @staticmethod
    def lunghezza(s: str) -> int:
        """
        testo.lunghezza → len
        """
        return len(s) if s else 0

    @staticmethod
    def tronca(s: str, max_len: int, suffisso: str = '...') -> str:
        """
        testo.tronca → tronca con ellipsis

        >>> testo.tronca('hello world', 8)
        'hello...'
        """
        if not s or len(s) <= max_len:
            return s or ''
        return s[:max_len - len(suffisso)] + suffisso

    @staticmethod
    def rimuovi_accenti(s: str) -> str:
        """
        testo.rimuovi_accenti → normalizza caratteri accentati
        """
        import unicodedata
        if not s:
            return ''
        nfkd = unicodedata.normalize('NFKD', s)
        return ''.join(c for c in nfkd if not unicodedata.combining(c))

    @staticmethod
    def formato_valido(s: str, pattern: str) -> bool:
        """
        testo.formato_valido → verifica regex

        >>> testo.formato_valido('test@example.com', r'.+@.+\\..+')
        True
        """
        if not s or not pattern:
            return False
        return bool(re.match(pattern, s))

    @staticmethod
    def estrai(s: str, pattern: str) -> Optional[str]:
        """
        testo.estrai → estrai primo match regex
        """
        if not s or not pattern:
            return None
        match = re.search(pattern, s)
        return match.group() if match else None

    @staticmethod
    def padding_sx(s: str, lunghezza: int, carattere: str = ' ') -> str:
        """
        testo.padding_sx → pad left
        """
        return s.rjust(lunghezza, carattere) if s else carattere * lunghezza

    @staticmethod
    def padding_dx(s: str, lunghezza: int, carattere: str = ' ') -> str:
        """
        testo.padding_dx → pad right
        """
        return s.ljust(lunghezza, carattere) if s else carattere * lunghezza


# Istanza singleton per uso come namespace
testo = _TestoArchetipo()
