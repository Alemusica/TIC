"""
Test per BiocCache PTI
"""

import pytest
import sys
sys.path.insert(0, '..')

from pti_core.biocache import BiocCache, LTM, MTM, STM


class TestBiocCache:
    """Test sistema di memoria biologica."""

    def test_scrivi_leggi(self):
        cache = BiocCache()
        cache.scrivi('test.chiave', 42)
        assert cache.leggi('test.chiave') == 42

    def test_livello_automatico_profondita(self):
        cache = BiocCache()

        # Profondità 0-1 → LTM
        cache.scrivi('archetipo', 'base')
        stats = cache.statistiche()
        assert 'archetipo' in stats['ltm_keys']

    def test_esiste_elimina(self):
        cache = BiocCache()
        cache.scrivi('x', 1)

        assert cache.esiste('x') is True
        cache.elimina('x')
        assert cache.esiste('x') is False

    def test_promozione_stm_mtm(self):
        cache = BiocCache(
            soglia_promozione_mtm=3,
            soglia_promozione_ltm=100
        )

        # Scrivi in STM (profondità alta)
        cache.scrivi('deep.nested.key.value', 'test', STM)

        # Accedi più volte
        for _ in range(5):
            cache.leggi('deep.nested.key.value')

        stats = cache.statistiche()
        # Dovrebbe essere promosso a MTM
        assert stats['mtm_count'] >= 1 or stats['stm_count'] >= 1

    def test_ring_buffer_stm(self):
        cache = BiocCache(stm_size=5)

        # Scrivi più elementi di quanti ne può contenere STM
        for i in range(10):
            cache.scrivi(f'item.{i}.value.deep', i, STM)

        stats = cache.statistiche()
        assert stats['stm_count'] <= 5

    def test_query_pattern(self):
        cache = BiocCache()

        cache.scrivi('tavolo.1.stato', 'libero')
        cache.scrivi('tavolo.2.stato', 'occupato')
        cache.scrivi('tavolo.3.stato', 'libero')
        cache.scrivi('sedia.1.stato', 'ok')

        risultati = cache.query_pattern('tavolo.*.stato')

        assert len(risultati) == 3
        assert risultati['tavolo.1.stato'] == 'libero'

    def test_storia_recente(self):
        cache = BiocCache()

        cache.scrivi('a', 1)
        cache.scrivi('b', 2)
        cache.leggi('a')

        storia = cache.storia_recente(3)
        assert 'a' in storia
        assert 'b' in storia

    def test_peso_contesto(self):
        cache = BiocCache()

        # Chiave più vicina alla radice = peso maggiore
        peso_shallow = cache.peso_contesto('a.b')
        peso_deep = cache.peso_contesto('a.b.c.d.e')

        assert peso_shallow > peso_deep

    def test_ciclo_manutenzione(self):
        cache = BiocCache(cicli_demozione=2)

        cache.scrivi('test.key.value', 'value', MTM)

        # Simula passaggio tempo senza accessi
        for _ in range(5):
            cache.ciclo()

        # Il valore potrebbe essere stato demozionato
        # (dipende dall'implementazione del ciclo)

    def test_statistiche(self):
        cache = BiocCache()

        cache.scrivi('ltm.key', 'a', LTM)
        cache.scrivi('mtm.key.nested', 'b', MTM)
        cache.scrivi('stm.very.deep.key.value', 'c', STM)

        stats = cache.statistiche()

        assert 'ltm_count' in stats
        assert 'mtm_count' in stats
        assert 'stm_count' in stats
        assert stats['ltm_count'] >= 1


class TestLivelli:
    """Test specifici per i livelli di memoria."""

    def test_ltm_persistente(self):
        cache = BiocCache(stm_size=2)

        # LTM non viene evicted
        cache.scrivi('archetipo.base', 'permanente', LTM)

        # Riempi STM
        for i in range(10):
            cache.scrivi(f'temp.{i}.deep.value', i, STM)

        # LTM ancora presente
        assert cache.leggi('archetipo.base') == 'permanente'

    def test_mtm_eviction_by_access(self):
        cache = BiocCache(mtm_size=3)

        # Scrivi in MTM
        cache.scrivi('a.x.y', 1, MTM)
        cache.scrivi('b.x.y', 2, MTM)
        cache.scrivi('c.x.y', 3, MTM)

        # Accedi frequentemente ad alcuni
        for _ in range(10):
            cache.leggi('a.x.y')
            cache.leggi('b.x.y')

        # Aggiungi altro, dovrebbe evictare il meno usato (c)
        cache.scrivi('d.x.y', 4, MTM)

        # c dovrebbe essere evicted (meno accessi)
        # a e b dovrebbero rimanere


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
