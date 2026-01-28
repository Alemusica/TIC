"""
Test per il sistema di Propagazione PTI
"""

import pytest
import sys
sys.path.insert(0, '..')

from pti_core.propagazione import Tessuto


class TestTessuto:
    """Test sistema di propagazione."""

    def test_fatto_base(self):
        tessuto = Tessuto()

        @tessuto.fatto('tavolo.1.stato')
        def _():
            return 'libero'

        assert tessuto.legge('tavolo.1.stato') == 'libero'

    def test_imposta_legge(self):
        tessuto = Tessuto()
        tessuto.imposta('x', 10)
        assert tessuto.legge('x') == 10

    def test_derivato_semplice(self):
        tessuto = Tessuto()

        # Setup stato
        tessuto.imposta('a', 5)
        tessuto.imposta('b', 3)

        @tessuto.derivato('somma', dipende_da=['a', 'b'])
        def _():
            return tessuto.legge('a') + tessuto.legge('b')

        assert tessuto.legge('somma') == 8

    def test_propagazione_automatica(self):
        tessuto = Tessuto()
        tessuto.imposta('base', 10)

        derivato_calcolato = [0]  # counter per verificare ricalcolo

        @tessuto.derivato('derivato', dipende_da=['base'])
        def _():
            derivato_calcolato[0] += 1
            return tessuto.legge('base') * 2

        # Prima lettura: calcola
        assert tessuto.legge('derivato') == 20
        assert derivato_calcolato[0] == 1

        # Seconda lettura senza cambio: non ricalcola
        assert tessuto.legge('derivato') == 20
        assert derivato_calcolato[0] == 1

        # Cambio base: marca come sporco
        tessuto.imposta('base', 15)

        # Lettura dopo cambio: ricalcola
        assert tessuto.legge('derivato') == 30
        assert derivato_calcolato[0] == 2

    def test_pattern_matching(self):
        tessuto = Tessuto()

        # Imposta più tavoli
        tessuto.imposta('tavolo.1.stato', 'libero')
        tessuto.imposta('tavolo.2.stato', 'occupato')
        tessuto.imposta('tavolo.3.stato', 'libero')

        # Query con pattern
        risultati = tessuto.query('tavolo.*.stato')

        assert len(risultati) == 3
        assert risultati['tavolo.1.stato'] == 'libero'
        assert risultati['tavolo.2.stato'] == 'occupato'

    def test_derivato_con_pattern(self):
        tessuto = Tessuto()

        tavoli_stati = {}

        tessuto.imposta('tavolo.1.stato', 'libero')
        tessuto.imposta('tavolo.2.stato', 'libero')

        @tessuto.derivato('tavoli.liberi.count', dipende_da=['tavolo.*.stato'])
        def _():
            risultati = tessuto.query('tavolo.*.stato')
            return sum(1 for v in risultati.values() if v == 'libero')

        assert tessuto.legge('tavoli.liberi.count') == 2

        tessuto.imposta('tavolo.1.stato', 'occupato')
        assert tessuto.legge('tavoli.liberi.count') == 1

    def test_batch_mode(self):
        tessuto = Tessuto()
        tessuto.imposta('a', 1)
        tessuto.imposta('b', 1)

        ricalcoli = [0]

        @tessuto.derivato('somma', dipende_da=['a', 'b'])
        def _():
            ricalcoli[0] += 1
            return tessuto.legge('a') + tessuto.legge('b')

        # Prima lettura
        tessuto.legge('somma')

        # Batch: più modifiche, una propagazione
        with tessuto.batch():
            tessuto.imposta('a', 10)
            tessuto.imposta('b', 20)

        # Dopo batch, derivato è sporco
        tessuto.legge('somma')

    def test_listener(self):
        tessuto = Tessuto()
        tessuto.imposta('x', 0)

        cambiamenti = []

        tessuto.ascolta('x', lambda v, n: cambiamenti.append((v, n)))

        tessuto.imposta('x', 1)
        tessuto.imposta('x', 2)

        assert len(cambiamenti) == 2
        assert cambiamenti[0] == (0, 1)
        assert cambiamenti[1] == (1, 2)

    def test_grafo(self):
        tessuto = Tessuto()

        @tessuto.fatto('a')
        def _():
            return 1

        @tessuto.derivato('b', dipende_da=['a'])
        def _():
            return tessuto.legge('a') * 2

        grafo = tessuto.grafo()
        assert 'a' in grafo
        assert 'b' in grafo['a']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
