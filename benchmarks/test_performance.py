"""
BENCHMARK: Performance PTI vs Tradizionale

Confronta:
1. Throughput operazioni
2. Memory footprint
3. Composizione funzioni
4. Propagazione cambiamenti

Requisiti: pytest-benchmark
Run: pytest benchmarks/test_performance.py --benchmark-autosave
"""

import pytest
import sys
sys.path.insert(0, '..')

from tic_core.archetipi import elemento, contenitore, confronta, valore, flusso
from tic_core.propagazione import Tessuto
from tic_core.biocache import BiocCache


# =============================================================================
# BENCHMARK 1: Creazione e Manipolazione Elementi
# =============================================================================

class TestElementoBenchmark:
    """Benchmark operazioni su elementi."""

    # --- PTI ---
    def test_pti_elemento_crea(self, benchmark):
        """PTI: Creazione elemento"""
        def create():
            return elemento.crea({'x': 1, 'y': 2, 'z': 3})
        benchmark(create)

    def test_pti_elemento_legge(self, benchmark):
        """PTI: Lettura attributo"""
        el = elemento.crea({'x': 1, 'y': 2, 'z': 3})
        benchmark(lambda: elemento.legge(el, 'x'))

    def test_pti_elemento_scrive(self, benchmark):
        """PTI: Scrittura attributo (immutabile)"""
        el = elemento.crea({'x': 1})
        benchmark(lambda: elemento.scrive(el, 'x', 2))

    # --- Tradizionale (dict) ---
    def test_trad_dict_crea(self, benchmark):
        """Tradizionale: Creazione dict"""
        benchmark(lambda: {'x': 1, 'y': 2, 'z': 3})

    def test_trad_dict_legge(self, benchmark):
        """Tradizionale: Lettura dict"""
        d = {'x': 1, 'y': 2, 'z': 3}
        benchmark(lambda: d['x'])

    def test_trad_dict_scrive(self, benchmark):
        """Tradizionale: Scrittura dict (mutabile)"""
        d = {'x': 1}
        def write():
            d['x'] = 2
        benchmark(write)


# =============================================================================
# BENCHMARK 2: Operazioni su Collezioni
# =============================================================================

class TestContenitoreBenchmark:
    """Benchmark operazioni su collezioni."""

    @pytest.fixture
    def lista_grande(self):
        return list(range(10000))

    @pytest.fixture
    def lista_elementi(self):
        return [elemento.crea({'val': i}) for i in range(1000)]

    # --- PTI ---
    def test_pti_mappa(self, benchmark, lista_grande):
        """PTI: map su 10k elementi"""
        benchmark(lambda: contenitore.mappa(lista_grande, lambda x: x * 2))

    def test_pti_filtra(self, benchmark, lista_grande):
        """PTI: filter su 10k elementi"""
        benchmark(lambda: contenitore.filtra(lista_grande, lambda x: x % 2 == 0))

    def test_pti_riduce(self, benchmark, lista_grande):
        """PTI: reduce su 10k elementi"""
        benchmark(lambda: contenitore.riduce(lista_grande, lambda a, x: a + x, 0))

    def test_pti_filtra_elementi(self, benchmark, lista_elementi):
        """PTI: filter su 1k elementi strutturati"""
        benchmark(lambda: contenitore.filtra(
            lista_elementi,
            lambda e: elemento.legge(e, 'val') > 500
        ))

    # --- Tradizionale ---
    def test_trad_map(self, benchmark, lista_grande):
        """Tradizionale: list comprehension map"""
        benchmark(lambda: [x * 2 for x in lista_grande])

    def test_trad_filter(self, benchmark, lista_grande):
        """Tradizionale: list comprehension filter"""
        benchmark(lambda: [x for x in lista_grande if x % 2 == 0])

    def test_trad_reduce(self, benchmark, lista_grande):
        """Tradizionale: sum builtin"""
        benchmark(lambda: sum(lista_grande))


# =============================================================================
# BENCHMARK 3: Composizione Funzionale
# =============================================================================

class TestComposizioneBenchmark:
    """Benchmark composizione di funzioni."""

    def test_pti_componi_2(self, benchmark):
        """PTI: composizione 2 funzioni"""
        f = lambda x: x + 1
        g = lambda x: x * 2
        composta = flusso.componi(f, g)
        benchmark(lambda: composta(5))

    def test_pti_sequenza_5(self, benchmark):
        """PTI: pipe di 5 funzioni"""
        pipe = flusso.sequenza(
            lambda x: x + 1,
            lambda x: x * 2,
            lambda x: x - 3,
            lambda x: x ** 2,
            lambda x: x // 2
        )
        benchmark(lambda: pipe(5))

    def test_trad_nested_calls(self, benchmark):
        """Tradizionale: chiamate annidate"""
        def f(x): return x + 1
        def g(x): return x * 2
        benchmark(lambda: g(f(5)))

    def test_trad_sequential_5(self, benchmark):
        """Tradizionale: 5 chiamate sequenziali"""
        def f1(x): return x + 1
        def f2(x): return x * 2
        def f3(x): return x - 3
        def f4(x): return x ** 2
        def f5(x): return x // 2

        def run(x):
            return f5(f4(f3(f2(f1(x)))))

        benchmark(lambda: run(5))


# =============================================================================
# BENCHMARK 4: Propagazione Reattiva
# =============================================================================

class TestPropagationBenchmark:
    """Benchmark sistema di propagazione."""

    def test_pti_propagazione_singola(self, benchmark):
        """PTI: propagazione singolo derivato"""
        tessuto = Tessuto()
        tessuto.imposta('base', 10)

        @tessuto.derivato('derivato', dipende_da=['base'])
        def _():
            return tessuto.legge('base') * 2

        def update_and_read():
            tessuto.imposta('base', 20)
            return tessuto.legge('derivato')

        benchmark(update_and_read)

    def test_pti_propagazione_catena(self, benchmark):
        """PTI: propagazione catena di 5 derivati"""
        tessuto = Tessuto()
        tessuto.imposta('base', 1)

        @tessuto.derivato('d1', dipende_da=['base'])
        def _(): return tessuto.legge('base') + 1

        @tessuto.derivato('d2', dipende_da=['d1'])
        def _(): return tessuto.legge('d1') * 2

        @tessuto.derivato('d3', dipende_da=['d2'])
        def _(): return tessuto.legge('d2') + 10

        @tessuto.derivato('d4', dipende_da=['d3'])
        def _(): return tessuto.legge('d3') * 3

        @tessuto.derivato('d5', dipende_da=['d4'])
        def _(): return tessuto.legge('d4') - 5

        def update_and_read():
            tessuto.imposta('base', 5)
            return tessuto.legge('d5')

        benchmark(update_and_read)

    def test_trad_computed_property(self, benchmark):
        """Tradizionale: computed property (ricalcola ogni volta)"""
        class Container:
            def __init__(self):
                self.base = 10

            @property
            def derivato(self):
                return self.base * 2

        c = Container()

        def update_and_read():
            c.base = 20
            return c.derivato

        benchmark(update_and_read)


# =============================================================================
# BENCHMARK 5: BiocCache
# =============================================================================

class TestCacheBenchmark:
    """Benchmark sistema di cache."""

    def test_pti_cache_write(self, benchmark):
        """PTI: scrittura in cache"""
        cache = BiocCache()
        i = [0]

        def write():
            cache.scrivi(f'key.{i[0]}', i[0])
            i[0] += 1

        benchmark(write)

    def test_pti_cache_read(self, benchmark):
        """PTI: lettura da cache"""
        cache = BiocCache()
        cache.scrivi('test.key', 'value')
        benchmark(lambda: cache.leggi('test.key'))

    def test_pti_cache_pattern_query(self, benchmark):
        """PTI: query con pattern"""
        cache = BiocCache()
        for i in range(100):
            cache.scrivi(f'item.{i}.value', i)

        benchmark(lambda: cache.query_pattern('item.*.value'))

    def test_trad_dict_cache(self, benchmark):
        """Tradizionale: dict come cache"""
        cache = {}
        cache['test.key'] = 'value'
        benchmark(lambda: cache.get('test.key'))


# =============================================================================
# BENCHMARK 6: Pattern Matching
# =============================================================================

class TestPatternMatchingBenchmark:
    """Benchmark pattern matching."""

    def test_pti_scegli_3_casi(self, benchmark):
        """PTI: pattern matching 3 casi"""
        def match(val):
            return flusso.scegli(val, [
                ('a', lambda x: 1),
                ('b', lambda x: 2),
                ('c', lambda x: 3)
            ], default=lambda x: 0)

        benchmark(lambda: match('b'))

    def test_pti_scegli_tipo(self, benchmark):
        """PTI: pattern matching su tipo"""
        def match(val):
            return flusso.scegli_tipo(val, [
                (int, lambda x: 'int'),
                (str, lambda x: 'str'),
                (list, lambda x: 'list')
            ], default=lambda x: 'other')

        benchmark(lambda: match(42))

    def test_trad_if_chain(self, benchmark):
        """Tradizionale: catena if-elif"""
        def match(val):
            if val == 'a':
                return 1
            elif val == 'b':
                return 2
            elif val == 'c':
                return 3
            else:
                return 0

        benchmark(lambda: match('b'))

    def test_trad_isinstance_chain(self, benchmark):
        """Tradizionale: catena isinstance"""
        def match(val):
            if isinstance(val, int):
                return 'int'
            elif isinstance(val, str):
                return 'str'
            elif isinstance(val, list):
                return 'list'
            else:
                return 'other'

        benchmark(lambda: match(42))


# =============================================================================
# BENCHMARK 7: Scenario Reale - E-Commerce
# =============================================================================

class TestScenarioEcommerce:
    """Benchmark scenario e-commerce completo."""

    def test_pti_calcola_carrello(self, benchmark):
        """PTI: calcolo totale carrello 100 items"""
        items = [
            elemento.crea({'sku': f'SKU{i}', 'qty': i % 5 + 1, 'price': 10.0 + i})
            for i in range(100)
        ]

        def calcola():
            subtotali = contenitore.mappa(
                items,
                lambda i: valore.moltiplica(
                    elemento.legge(i, 'qty'),
                    elemento.legge(i, 'price')
                )
            )
            return valore.somma(subtotali)

        benchmark(calcola)

    def test_trad_calcola_carrello(self, benchmark):
        """Tradizionale: calcolo totale carrello 100 items"""
        items = [
            {'sku': f'SKU{i}', 'qty': i % 5 + 1, 'price': 10.0 + i}
            for i in range(100)
        ]

        def calcola():
            return sum(item['qty'] * item['price'] for item in items)

        benchmark(calcola)

    def test_pti_filtra_e_ordina(self, benchmark):
        """PTI: filtra prodotti disponibili e ordina per prezzo"""
        prodotti = [
            elemento.crea({
                'sku': f'SKU{i}',
                'price': 100 - i,
                'qty': i % 10,
                'active': i % 3 != 0
            })
            for i in range(500)
        ]

        def filtra_ordina():
            disponibili = contenitore.filtra(
                prodotti,
                lambda p: confronta.tutti([
                    lambda x: confronta.vero(elemento.legge(x, 'active')),
                    lambda x: confronta.maggiore(elemento.legge(x, 'qty'), 0)
                ], p)
            )
            return contenitore.ordina(
                disponibili,
                chiave=lambda p: elemento.legge(p, 'price')
            )

        benchmark(filtra_ordina)

    def test_trad_filtra_e_ordina(self, benchmark):
        """Tradizionale: filtra prodotti disponibili e ordina per prezzo"""
        prodotti = [
            {'sku': f'SKU{i}', 'price': 100 - i, 'qty': i % 10, 'active': i % 3 != 0}
            for i in range(500)
        ]

        def filtra_ordina():
            disponibili = [p for p in prodotti if p['active'] and p['qty'] > 0]
            return sorted(disponibili, key=lambda p: p['price'])

        benchmark(filtra_ordina)
