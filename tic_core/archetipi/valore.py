"""
ARCHETIPO: valore
Operazioni su valori numerici/scalari.

valore.incrementa → +delta
valore.decrementa → -delta
valore.moltiplica → *fattore
valore.divide     → /divisore
valore.assoluto   → |x|
valore.arrotonda  → round
valore.minimo     → min di lista
valore.massimo    → max di lista
valore.somma      → somma di lista
valore.media      → media di lista
"""

from typing import Any, List, Optional, Union

Numero = Union[int, float]


class _ValoreArchetipo:
    """
    Namespace per operazioni su valori numerici.
    Uso: valore.incrementa(n, 1)
    """

    @staticmethod
    def incrementa(n: Numero, delta: Numero = 1) -> Numero:
        """
        valore.incrementa → n + delta

        >>> valore.incrementa(5)
        6
        >>> valore.incrementa(5, 3)
        8
        """
        return n + delta

    @staticmethod
    def decrementa(n: Numero, delta: Numero = 1) -> Numero:
        """
        valore.decrementa → n - delta
        """
        return n - delta

    @staticmethod
    def moltiplica(n: Numero, fattore: Numero) -> Numero:
        """
        valore.moltiplica → n * fattore
        """
        return n * fattore

    @staticmethod
    def divide(n: Numero, divisore: Numero) -> Optional[float]:
        """
        valore.divide → n / divisore (None se divisore è 0)

        >>> valore.divide(10, 2)
        5.0
        >>> valore.divide(10, 0) is None
        True
        """
        if divisore == 0:
            return None
        return n / divisore

    @staticmethod
    def assoluto(n: Numero) -> Numero:
        """
        valore.assoluto → |n|
        """
        return abs(n)

    @staticmethod
    def arrotonda(n: float, decimali: int = 0) -> float:
        """
        valore.arrotonda → round(n, decimali)
        """
        return round(n, decimali)

    @staticmethod
    def minimo(valori: List[Numero]) -> Optional[Numero]:
        """
        valore.minimo → min(valori)

        >>> valore.minimo([3, 1, 4, 1, 5])
        1
        """
        return min(valori) if valori else None

    @staticmethod
    def massimo(valori: List[Numero]) -> Optional[Numero]:
        """
        valore.massimo → max(valori)
        """
        return max(valori) if valori else None

    @staticmethod
    def somma(valori: List[Numero]) -> Numero:
        """
        valore.somma → sum(valori)

        >>> valore.somma([1, 2, 3, 4])
        10
        """
        return sum(valori)

    @staticmethod
    def media(valori: List[Numero]) -> Optional[float]:
        """
        valore.media → media aritmetica

        >>> valore.media([2, 4, 6])
        4.0
        """
        if not valori:
            return None
        return sum(valori) / len(valori)

    @staticmethod
    def clamp(n: Numero, minimo: Numero, massimo: Numero) -> Numero:
        """
        valore.clamp → limita n tra minimo e massimo

        >>> valore.clamp(15, 0, 10)
        10
        >>> valore.clamp(-5, 0, 10)
        0
        """
        return max(minimo, min(n, massimo))

    @staticmethod
    def percentuale(parte: Numero, totale: Numero) -> Optional[float]:
        """
        valore.percentuale → (parte / totale) * 100
        """
        if totale == 0:
            return None
        return (parte / totale) * 100

    @staticmethod
    def positivo(n: Numero) -> bool:
        """
        valore.positivo → n > 0
        """
        return n > 0

    @staticmethod
    def negativo(n: Numero) -> bool:
        """
        valore.negativo → n < 0
        """
        return n < 0

    @staticmethod
    def zero(n: Numero) -> bool:
        """
        valore.zero → n == 0
        """
        return n == 0


# Istanza singleton per uso come namespace
valore = _ValoreArchetipo()
