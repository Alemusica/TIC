"""
ARCHETIPO: flusso
Operazioni di controllo flusso PURE.

flusso.se        → branching condizionale
flusso.scegli    → pattern matching
flusso.ripeti    → iteration bounded
flusso.componi   → composition
flusso.sequenza  → pipe
flusso.parallelo → parallel execution
"""

from typing import Any, Callable, List, Tuple, TypeVar, Optional

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class _FlussoArchetipo:
    """
    Namespace per controllo flusso puro.
    NOTA: Tutto è deterministico, no side effects.
    """

    @staticmethod
    def se(condizione: bool, se_vero: Callable[[], A], se_falso: Callable[[], A]) -> A:
        """
        flusso.se → branching condizionale

        >>> flusso.se(True, lambda: 'yes', lambda: 'no')
        'yes'
        >>> flusso.se(5 > 3, lambda: 'greater', lambda: 'lesser')
        'greater'
        """
        return se_vero() if condizione else se_falso()

    @staticmethod
    def scegli(valore: A, casi: List[Tuple[Any, Callable[[A], B]]], default: Callable[[A], B] = None) -> B:
        """
        flusso.scegli → pattern matching

        >>> flusso.scegli('a', [('a', lambda x: 1), ('b', lambda x: 2)])
        1
        >>> flusso.scegli('c', [('a', lambda x: 1)], default=lambda x: 0)
        0
        """
        for pattern, handler in casi:
            if pattern == '_' or pattern == valore:
                return handler(valore)
        if default:
            return default(valore)
        raise ValueError(f"Nessun pattern matcha {valore} e nessun default")

    @staticmethod
    def scegli_tipo(valore: Any, casi: List[Tuple[type, Callable[[Any], B]]], default: Callable[[Any], B] = None) -> B:
        """
        flusso.scegli_tipo → pattern matching su tipo

        >>> flusso.scegli_tipo(42, [(int, lambda x: 'int'), (str, lambda x: 'str')])
        'int'
        """
        for tipo, handler in casi:
            if isinstance(valore, tipo):
                return handler(valore)
        if default:
            return default(valore)
        raise ValueError(f"Nessun tipo matcha {type(valore)} e nessun default")

    @staticmethod
    def ripeti(
        condizione: Callable[[A], bool],
        corpo: Callable[[A], A],
        iniziale: A,
        max_iterazioni: int = 1000
    ) -> A:
        """
        flusso.ripeti → iteration BOUNDED (sicuro per terminazione)

        >>> flusso.ripeti(lambda x: x < 5, lambda x: x + 1, 0)
        5
        """
        stato = iniziale
        iterazioni = 0

        while condizione(stato) and iterazioni < max_iterazioni:
            stato = corpo(stato)
            iterazioni += 1

        if iterazioni >= max_iterazioni:
            raise RuntimeError(f"ripeti: max iterazioni ({max_iterazioni}) raggiunto")

        return stato

    @staticmethod
    def componi(f: Callable[[A], B], g: Callable[[B], C]) -> Callable[[A], C]:
        """
        flusso.componi → f andThen g (composition)

        >>> add1 = lambda x: x + 1
        >>> mul2 = lambda x: x * 2
        >>> flusso.componi(add1, mul2)(5)
        12
        """
        return lambda x: g(f(x))

    @staticmethod
    def sequenza(*funzioni: Callable) -> Callable[[A], Any]:
        """
        flusso.sequenza → pipe di funzioni

        >>> pipe = flusso.sequenza(lambda x: x + 1, lambda x: x * 2, lambda x: x - 3)
        >>> pipe(5)
        9
        """
        def pipe(valore):
            risultato = valore
            for f in funzioni:
                risultato = f(risultato)
            return risultato
        return pipe

    @staticmethod
    def parallelo(f: Callable[[A], B], g: Callable[[A], C]) -> Callable[[A], Tuple[B, C]]:
        """
        flusso.parallelo → esegue due funzioni sullo stesso input

        >>> both = flusso.parallelo(lambda x: x + 1, lambda x: x * 2)
        >>> both(5)
        (6, 10)
        """
        return lambda x: (f(x), g(x))

    @staticmethod
    def identita(x: A) -> A:
        """
        flusso.identita → funzione identità

        >>> flusso.identita(42)
        42
        """
        return x

    @staticmethod
    def costante(valore: A) -> Callable[[Any], A]:
        """
        flusso.costante → funzione che ritorna sempre lo stesso valore

        >>> always5 = flusso.costante(5)
        >>> always5('anything')
        5
        """
        return lambda _: valore

    @staticmethod
    def applica(f: Callable[[A], B], valore: A) -> B:
        """
        flusso.applica → applica funzione a valore

        >>> flusso.applica(lambda x: x * 2, 5)
        10
        """
        return f(valore)

    @staticmethod
    def curry(f: Callable[[A, B], C]) -> Callable[[A], Callable[[B], C]]:
        """
        flusso.curry → currying

        >>> add = lambda a, b: a + b
        >>> curried = flusso.curry(add)
        >>> curried(3)(4)
        7
        """
        return lambda a: lambda b: f(a, b)

    @staticmethod
    def uncurry(f: Callable[[A], Callable[[B], C]]) -> Callable[[A, B], C]:
        """
        flusso.uncurry → uncurrying
        """
        return lambda a, b: f(a)(b)


# Singleton
flusso = _FlussoArchetipo()
