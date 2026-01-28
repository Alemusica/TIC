"""
ARCHETIPO: elemento
Operazioni su singoli elementi/entità.

elemento.crea     → crea un nuovo elemento
elemento.legge    → legge un attributo
elemento.scrive   → scrive un attributo
elemento.esiste   → verifica esistenza
elemento.elimina  → marca come eliminato
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class Elemento:
    """Wrapper per entità PTI con metadata."""
    _dati: Dict[str, Any] = field(default_factory=dict)
    _meta: Dict[str, Any] = field(default_factory=lambda: {
        'creato': None,
        'modificato': None,
        'eliminato': False
    })

    def __getitem__(self, key: str) -> Any:
        return self._dati.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self._dati[key] = value


class _ElementoArchetipo:
    """
    Namespace per operazioni su elementi.
    Uso: elemento.crea({...}), elemento.legge(e, 'campo')
    """

    @staticmethod
    def crea(dati: Dict[str, Any] = None) -> Elemento:
        """
        elemento.crea → crea un nuovo elemento

        >>> e = elemento.crea({'nome': 'Mario', 'eta': 30})
        >>> elemento.legge(e, 'nome')
        'Mario'
        """
        from datetime import datetime
        el = Elemento(_dati=dati or {})
        el._meta['creato'] = datetime.now()
        el._meta['modificato'] = datetime.now()
        return el

    @staticmethod
    def legge(el: Elemento, campo: str, default: Any = None) -> Any:
        """
        elemento.legge → legge un attributo

        >>> e = elemento.crea({'x': 10})
        >>> elemento.legge(e, 'x')
        10
        >>> elemento.legge(e, 'y', 0)
        0
        """
        if isinstance(el, Elemento):
            return el._dati.get(campo, default)
        elif isinstance(el, dict):
            return el.get(campo, default)
        else:
            return getattr(el, campo, default)

    @staticmethod
    def scrive(el: Elemento, campo: str, valore: Any) -> Elemento:
        """
        elemento.scrive → scrive un attributo (immutabile, ritorna copia)

        >>> e = elemento.crea({'x': 10})
        >>> e2 = elemento.scrive(e, 'x', 20)
        >>> elemento.legge(e2, 'x')
        20
        """
        from datetime import datetime
        nuovo = deepcopy(el)
        if isinstance(nuovo, Elemento):
            nuovo._dati[campo] = valore
            nuovo._meta['modificato'] = datetime.now()
        elif isinstance(nuovo, dict):
            nuovo[campo] = valore
        else:
            setattr(nuovo, campo, valore)
        return nuovo

    @staticmethod
    def esiste(el: Elemento) -> bool:
        """
        elemento.esiste → verifica esistenza (non eliminato)

        >>> e = elemento.crea({'x': 1})
        >>> elemento.esiste(e)
        True
        """
        if el is None:
            return False
        if isinstance(el, Elemento):
            return not el._meta.get('eliminato', False)
        return True

    @staticmethod
    def elimina(el: Elemento) -> Elemento:
        """
        elemento.elimina → marca come eliminato (soft delete)

        >>> e = elemento.crea({'x': 1})
        >>> e2 = elemento.elimina(e)
        >>> elemento.esiste(e2)
        False
        """
        from datetime import datetime
        nuovo = deepcopy(el)
        if isinstance(nuovo, Elemento):
            nuovo._meta['eliminato'] = True
            nuovo._meta['modificato'] = datetime.now()
        return nuovo

    @staticmethod
    def clona(el: Elemento) -> Elemento:
        """
        elemento.clona → crea copia profonda
        """
        return deepcopy(el)

    @staticmethod
    def campi(el: Elemento) -> list:
        """
        elemento.campi → lista dei campi
        """
        if isinstance(el, Elemento):
            return list(el._dati.keys())
        elif isinstance(el, dict):
            return list(el.keys())
        return []


# Istanza singleton per uso come namespace
elemento = _ElementoArchetipo()
