"""
ARCHETIPO: confronta
Operazioni di confronto e verifica.

confronta.uguale    → a == b
confronta.diverso   → a != b
confronta.maggiore  → a > b
confronta.minore    → a < b
confronta.almeno    → a >= b
confronta.alpiù     → a <= b
confronta.tra       → min <= a <= max
confronta.nullo     → a is None
confronta.vero      → bool(a) is True
confronta.falso     → bool(a) is False
"""

from typing import Any, Callable


class _ConfrontaArchetipo:
    """
    Namespace per operazioni di confronto.
    Uso: confronta.uguale(a, b)
    """

    @staticmethod
    def uguale(a: Any, b: Any) -> bool:
        """
        confronta.uguale → a == b

        >>> confronta.uguale(1, 1)
        True
        >>> confronta.uguale('a', 'b')
        False
        """
        return a == b

    @staticmethod
    def diverso(a: Any, b: Any) -> bool:
        """
        confronta.diverso → a != b
        """
        return a != b

    @staticmethod
    def maggiore(a: Any, b: Any) -> bool:
        """
        confronta.maggiore → a > b

        >>> confronta.maggiore(5, 3)
        True
        """
        return a > b

    @staticmethod
    def minore(a: Any, b: Any) -> bool:
        """
        confronta.minore → a < b
        """
        return a < b

    @staticmethod
    def almeno(a: Any, b: Any) -> bool:
        """
        confronta.almeno → a >= b (a è almeno b)

        >>> confronta.almeno(5, 3)
        True
        >>> confronta.almeno(3, 3)
        True
        """
        return a >= b

    @staticmethod
    def alpiù(a: Any, b: Any) -> bool:
        """
        confronta.alpiù → a <= b (a è al più b)
        """
        return a <= b

    @staticmethod
    def sotto(a: Any, soglia: Any) -> bool:
        """
        confronta.sotto → a < soglia

        >>> confronta.sotto(3, 5)
        True
        """
        return a < soglia

    @staticmethod
    def sopra(a: Any, soglia: Any) -> bool:
        """
        confronta.sopra → a > soglia
        """
        return a > soglia

    @staticmethod
    def tra(valore: Any, minimo: Any, massimo: Any) -> bool:
        """
        confronta.tra → minimo <= valore <= massimo

        >>> confronta.tra(5, 1, 10)
        True
        >>> confronta.tra(0, 1, 10)
        False
        """
        return minimo <= valore <= massimo

    @staticmethod
    def nullo(a: Any) -> bool:
        """
        confronta.nullo → a is None

        >>> confronta.nullo(None)
        True
        >>> confronta.nullo(0)
        False
        """
        return a is None

    @staticmethod
    def non_nullo(a: Any) -> bool:
        """
        confronta.non_nullo → a is not None
        """
        return a is not None

    @staticmethod
    def vero(a: Any) -> bool:
        """
        confronta.vero → bool(a) is True

        >>> confronta.vero(1)
        True
        >>> confronta.vero('')
        False
        """
        return bool(a) is True

    @staticmethod
    def falso(a: Any) -> bool:
        """
        confronta.falso → bool(a) is False
        """
        return bool(a) is False

    @staticmethod
    def tutti(predicati: list, valore: Any) -> bool:
        """
        confronta.tutti → tutti i predicati sono veri

        >>> confronta.tutti([lambda x: x > 0, lambda x: x < 10], 5)
        True
        """
        return all(p(valore) for p in predicati)

    @staticmethod
    def almeno_uno(predicati: list, valore: Any) -> bool:
        """
        confronta.almeno_uno → almeno un predicato è vero
        """
        return any(p(valore) for p in predicati)

    @staticmethod
    def in_lista(valore: Any, lista: list) -> bool:
        """
        confronta.in_lista → valore in lista

        >>> confronta.in_lista(2, [1, 2, 3])
        True
        """
        return valore in lista

    @staticmethod
    def tipo(valore: Any, tipo_atteso: type) -> bool:
        """
        confronta.tipo → isinstance check

        >>> confronta.tipo(5, int)
        True
        """
        return isinstance(valore, tipo_atteso)


# Istanza singleton per uso come namespace
confronta = _ConfrontaArchetipo()
