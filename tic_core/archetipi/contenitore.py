"""
ARCHETIPO: contenitore
Operazioni su collezioni/liste/insiemi.

contenitore.crea     → crea un contenitore vuoto
contenitore.aggiunge → aggiunge elemento
contenitore.rimuove  → rimuove elemento
contenitore.filtra   → filtra con predicato
contenitore.mappa    → trasforma ogni elemento
contenitore.riduce   → riduce a singolo valore
contenitore.conta    → conta elementi
contenitore.primo    → primo elemento
contenitore.ultimo   → ultimo elemento
contenitore.vuoto    → verifica se vuoto
"""

from typing import Any, Callable, Iterable, List, Optional, TypeVar
from copy import deepcopy

T = TypeVar('T')
R = TypeVar('R')


class _ContenitoreArchetipo:
    """
    Namespace per operazioni su collezioni.
    Uso: contenitore.aggiunge(lista, elem)
    """

    @staticmethod
    def crea(elementi: Iterable[T] = None) -> List[T]:
        """
        contenitore.crea → crea un contenitore

        >>> c = contenitore.crea([1, 2, 3])
        >>> contenitore.conta(c)
        3
        """
        if elementi is None:
            return []
        return list(elementi)

    @staticmethod
    def aggiunge(cont: List[T], elem: T) -> List[T]:
        """
        contenitore.aggiunge → aggiunge elemento (immutabile)

        >>> c = contenitore.crea([1, 2])
        >>> c2 = contenitore.aggiunge(c, 3)
        >>> c2
        [1, 2, 3]
        """
        nuovo = deepcopy(cont)
        nuovo.append(elem)
        return nuovo

    @staticmethod
    def rimuove(cont: List[T], elem: T) -> List[T]:
        """
        contenitore.rimuove → rimuove prima occorrenza (immutabile)

        >>> c = contenitore.crea([1, 2, 3])
        >>> contenitore.rimuove(c, 2)
        [1, 3]
        """
        nuovo = deepcopy(cont)
        if elem in nuovo:
            nuovo.remove(elem)
        return nuovo

    @staticmethod
    def rimuove_a(cont: List[T], indice: int) -> List[T]:
        """
        contenitore.rimuove_a → rimuove a indice (immutabile)

        >>> c = contenitore.crea(['a', 'b', 'c'])
        >>> contenitore.rimuove_a(c, 1)
        ['a', 'c']
        """
        nuovo = deepcopy(cont)
        if 0 <= indice < len(nuovo):
            nuovo.pop(indice)
        return nuovo

    @staticmethod
    def filtra(cont: List[T], predicato: Callable[[T], bool]) -> List[T]:
        """
        contenitore.filtra → filtra con predicato

        >>> c = contenitore.crea([1, 2, 3, 4, 5])
        >>> contenitore.filtra(c, lambda x: x > 2)
        [3, 4, 5]
        """
        return [e for e in cont if predicato(e)]

    @staticmethod
    def mappa(cont: List[T], funzione: Callable[[T], R]) -> List[R]:
        """
        contenitore.mappa → trasforma ogni elemento

        >>> c = contenitore.crea([1, 2, 3])
        >>> contenitore.mappa(c, lambda x: x * 2)
        [2, 4, 6]
        """
        return [funzione(e) for e in cont]

    @staticmethod
    def riduce(cont: List[T], funzione: Callable[[R, T], R], iniziale: R) -> R:
        """
        contenitore.riduce → riduce a singolo valore

        >>> c = contenitore.crea([1, 2, 3, 4])
        >>> contenitore.riduce(c, lambda acc, x: acc + x, 0)
        10
        """
        acc = iniziale
        for e in cont:
            acc = funzione(acc, e)
        return acc

    @staticmethod
    def conta(cont: List[T]) -> int:
        """
        contenitore.conta → numero di elementi

        >>> contenitore.conta([1, 2, 3])
        3
        """
        return len(cont)

    @staticmethod
    def primo(cont: List[T], default: T = None) -> Optional[T]:
        """
        contenitore.primo → primo elemento o default

        >>> contenitore.primo([1, 2, 3])
        1
        >>> contenitore.primo([], 'vuoto')
        'vuoto'
        """
        return cont[0] if cont else default

    @staticmethod
    def ultimo(cont: List[T], default: T = None) -> Optional[T]:
        """
        contenitore.ultimo → ultimo elemento o default
        """
        return cont[-1] if cont else default

    @staticmethod
    def vuoto(cont: List[T]) -> bool:
        """
        contenitore.vuoto → True se vuoto

        >>> contenitore.vuoto([])
        True
        >>> contenitore.vuoto([1])
        False
        """
        return len(cont) == 0

    @staticmethod
    def trova(cont: List[T], predicato: Callable[[T], bool]) -> Optional[T]:
        """
        contenitore.trova → primo che soddisfa predicato

        >>> c = contenitore.crea([1, 2, 3, 4])
        >>> contenitore.trova(c, lambda x: x > 2)
        3
        """
        for e in cont:
            if predicato(e):
                return e
        return None

    @staticmethod
    def contiene(cont: List[T], elem: T) -> bool:
        """
        contenitore.contiene → verifica presenza
        """
        return elem in cont

    @staticmethod
    def ordina(cont: List[T], chiave: Callable[[T], Any] = None, inverso: bool = False) -> List[T]:
        """
        contenitore.ordina → ordina (immutabile)
        """
        return sorted(cont, key=chiave, reverse=inverso)

    @staticmethod
    def unisce(cont1: List[T], cont2: List[T]) -> List[T]:
        """
        contenitore.unisce → concatena due contenitori
        """
        return cont1 + cont2

    @staticmethod
    def piatto(cont: List[List[T]]) -> List[T]:
        """
        contenitore.piatto → appiattisce lista di liste

        >>> contenitore.piatto([[1, 2], [3, 4]])
        [1, 2, 3, 4]
        """
        return [e for lista in cont for e in lista]


# Istanza singleton per uso come namespace
contenitore = _ContenitoreArchetipo()

# Alias
collezione = contenitore
