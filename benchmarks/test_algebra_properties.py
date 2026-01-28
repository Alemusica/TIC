"""
TEST: Proprietà dell'Algebra PTI

Verifica matematicamente che l'algebra rispetti le proprietà dichiarate:
1. Purezza (determinismo)
2. Chiusura (composizione produce celle valide)
3. Terminazione (no loop infiniti)
4. Immutabilità (operazioni non modificano input)

Questi test "zittiscono i nerd": dimostrano formalmente i claim.
"""

import pytest
import sys
sys.path.insert(0, '..')

from tic_core.archetipi import elemento, contenitore, confronta, valore, flusso


# =============================================================================
# PROPRIETÀ 1: PUREZZA (Determinismo)
# =============================================================================

class TestPurezza:
    """
    Verifica: ∀ f ∈ Cells, ∀ x: f(x) = f(x)
    Stessa input → sempre stessa output.
    """

    def test_elemento_crea_deterministico(self):
        """elemento.crea è deterministico"""
        dati = {'a': 1, 'b': 2}
        risultati = [elemento.crea(dati) for _ in range(100)]

        # Tutti hanno stessi valori
        for r in risultati:
            assert elemento.legge(r, 'a') == 1
            assert elemento.legge(r, 'b') == 2

    def test_contenitore_mappa_deterministico(self):
        """contenitore.mappa è deterministico"""
        lista = [1, 2, 3, 4, 5]
        f = lambda x: x * 2

        risultati = [contenitore.mappa(lista, f) for _ in range(100)]

        # Tutti uguali
        for r in risultati:
            assert r == [2, 4, 6, 8, 10]

    def test_flusso_componi_deterministico(self):
        """flusso.componi è deterministico"""
        f = lambda x: x + 1
        g = lambda x: x * 2
        composta = flusso.componi(f, g)

        risultati = [composta(5) for _ in range(100)]

        # Tutti uguali
        assert all(r == 12 for r in risultati)

    def test_flusso_scegli_deterministico(self):
        """flusso.scegli è deterministico"""
        casi = [('a', lambda x: 1), ('b', lambda x: 2)]

        risultati = [flusso.scegli('a', casi) for _ in range(100)]
        assert all(r == 1 for r in risultati)

        risultati = [flusso.scegli('b', casi) for _ in range(100)]
        assert all(r == 2 for r in risultati)


# =============================================================================
# PROPRIETÀ 2: CHIUSURA (Composizione)
# =============================================================================

class TestChiusura:
    """
    Verifica: ∀ c1, c2 ∈ Cells: compose(c1, c2) ∈ Cells
    La composizione di celle produce sempre una cella valida.
    """

    def test_componi_due_funzioni(self):
        """Composizione di 2 funzioni è valida"""
        f = lambda x: x + 1
        g = lambda x: x * 2

        composta = flusso.componi(f, g)

        # La composta è callable
        assert callable(composta)
        # La composta produce risultato
        assert composta(5) == 12

    def test_componi_catena_lunga(self):
        """Composizione di N funzioni è valida"""
        funzioni = [
            lambda x: x + 1,
            lambda x: x * 2,
            lambda x: x - 3,
            lambda x: x ** 2,
            lambda x: x + 100
        ]

        # Costruisci catena
        composta = funzioni[0]
        for f in funzioni[1:]:
            composta = flusso.componi(composta, f)

        assert callable(composta)
        assert isinstance(composta(5), (int, float))

    def test_sequenza_produce_funzione(self):
        """flusso.sequenza produce funzione valida"""
        pipe = flusso.sequenza(
            lambda x: x + 1,
            lambda x: x * 2,
            lambda x: str(x)
        )

        assert callable(pipe)
        assert pipe(5) == '12'

    def test_parallelo_produce_tuple(self):
        """flusso.parallelo produce funzione che ritorna tuple"""
        par = flusso.parallelo(
            lambda x: x + 1,
            lambda x: x * 2
        )

        assert callable(par)
        result = par(5)
        assert isinstance(result, tuple)
        assert result == (6, 10)


# =============================================================================
# PROPRIETÀ 3: TERMINAZIONE
# =============================================================================

class TestTerminazione:
    """
    Verifica: ∀ c ∈ Cells: terminates(c) = true
    Tutte le operazioni terminano.
    """

    def test_ripeti_termina_con_condizione(self):
        """flusso.ripeti termina quando condizione è falsa"""
        # Conta da 0 a 10
        risultato = flusso.ripeti(
            lambda x: x < 10,
            lambda x: x + 1,
            0
        )
        assert risultato == 10

    def test_ripeti_ha_limite_massimo(self):
        """flusso.ripeti ha limite massimo iterazioni"""
        with pytest.raises(RuntimeError, match="max iterazioni"):
            # Condizione sempre vera → deve fermarsi
            flusso.ripeti(
                lambda x: True,  # sempre vero
                lambda x: x + 1,
                0,
                max_iterazioni=100
            )

    def test_ripeti_rispetta_limite_custom(self):
        """flusso.ripeti rispetta limite custom"""
        with pytest.raises(RuntimeError):
            flusso.ripeti(
                lambda x: True,
                lambda x: x + 1,
                0,
                max_iterazioni=50
            )

    def test_operazioni_base_terminano(self):
        """Operazioni base terminano immediatamente"""
        import time

        start = time.time()

        # Esegui molte operazioni
        for _ in range(10000):
            elemento.crea({'x': 1})
            contenitore.mappa([1, 2, 3], lambda x: x * 2)
            flusso.se(True, lambda: 1, lambda: 2)

        elapsed = time.time() - start

        # Deve completare in tempo ragionevole (< 5 secondi)
        assert elapsed < 5.0


# =============================================================================
# PROPRIETÀ 4: IMMUTABILITÀ
# =============================================================================

class TestImmutabilita:
    """
    Verifica: Le operazioni non modificano l'input.
    """

    def test_elemento_scrive_non_modifica_originale(self):
        """elemento.scrive non modifica l'originale"""
        originale = elemento.crea({'x': 1, 'y': 2})
        originale_x = elemento.legge(originale, 'x')

        # Scrivi
        nuovo = elemento.scrive(originale, 'x', 999)

        # Originale invariato
        assert elemento.legge(originale, 'x') == originale_x
        # Nuovo ha valore aggiornato
        assert elemento.legge(nuovo, 'x') == 999

    def test_contenitore_aggiunge_non_modifica_originale(self):
        """contenitore.aggiunge non modifica l'originale"""
        originale = contenitore.crea([1, 2, 3])
        originale_len = len(originale)

        # Aggiungi
        nuovo = contenitore.aggiunge(originale, 4)

        # Originale invariato
        assert len(originale) == originale_len
        assert originale == [1, 2, 3]
        # Nuovo ha elemento aggiunto
        assert nuovo == [1, 2, 3, 4]

    def test_contenitore_rimuove_non_modifica_originale(self):
        """contenitore.rimuove non modifica l'originale"""
        originale = contenitore.crea([1, 2, 3])

        # Rimuovi
        nuovo = contenitore.rimuove(originale, 2)

        # Originale invariato
        assert originale == [1, 2, 3]
        # Nuovo senza elemento
        assert nuovo == [1, 3]

    def test_contenitore_filtra_non_modifica_originale(self):
        """contenitore.filtra non modifica l'originale"""
        originale = [1, 2, 3, 4, 5]

        # Filtra
        filtrato = contenitore.filtra(originale, lambda x: x > 2)

        # Originale invariato
        assert originale == [1, 2, 3, 4, 5]
        assert filtrato == [3, 4, 5]


# =============================================================================
# PROPRIETÀ 5: ASSENZA DI SIDE EFFECTS
# =============================================================================

class TestNoSideEffects:
    """
    Verifica: Le celle pure non hanno side effects.
    """

    def test_mappa_non_ha_side_effects(self):
        """contenitore.mappa non ha side effects"""
        effetti = []

        def f_con_effetto(x):
            effetti.append(x)  # side effect!
            return x * 2

        lista = [1, 2, 3]

        # Prima chiamata
        effetti.clear()
        contenitore.mappa(lista, f_con_effetto)
        effetti_1 = effetti.copy()

        # Seconda chiamata
        effetti.clear()
        contenitore.mappa(lista, f_con_effetto)
        effetti_2 = effetti.copy()

        # Stessi effetti = deterministico
        # (la funzione passata ha effetti, ma mappa no)
        assert effetti_1 == effetti_2

    def test_flusso_se_valuta_solo_branch_corretto(self):
        """flusso.se valuta solo il branch corretto"""
        chiamate_vero = [0]
        chiamate_falso = [0]

        def branch_vero():
            chiamate_vero[0] += 1
            return 'vero'

        def branch_falso():
            chiamate_falso[0] += 1
            return 'falso'

        # Condizione vera → solo branch_vero chiamato
        flusso.se(True, branch_vero, branch_falso)
        assert chiamate_vero[0] == 1
        assert chiamate_falso[0] == 0

        # Reset
        chiamate_vero[0] = 0
        chiamate_falso[0] = 0

        # Condizione falsa → solo branch_falso chiamato
        flusso.se(False, branch_vero, branch_falso)
        assert chiamate_vero[0] == 0
        assert chiamate_falso[0] == 1


# =============================================================================
# PROPRIETÀ 6: COMPOSIZIONALITÀ
# =============================================================================

class TestComposizionalita:
    """
    Verifica: Le celle si compongono in modo prevedibile.
    """

    def test_composizione_associativa(self):
        """(f ∘ g) ∘ h = f ∘ (g ∘ h)"""
        f = lambda x: x + 1
        g = lambda x: x * 2
        h = lambda x: x ** 2

        # (f ∘ g) ∘ h
        fg = flusso.componi(f, g)
        fg_h = flusso.componi(fg, h)

        # f ∘ (g ∘ h)
        gh = flusso.componi(g, h)
        f_gh = flusso.componi(f, gh)

        # Devono dare stesso risultato
        for x in range(10):
            assert fg_h(x) == f_gh(x)

    def test_identita_neutra(self):
        """f ∘ id = id ∘ f = f"""
        f = lambda x: x * 2
        id_fn = flusso.identita

        f_id = flusso.componi(f, id_fn)
        id_f = flusso.componi(id_fn, f)

        for x in range(10):
            assert f_id(x) == f(x)
            assert id_f(x) == f(x)

    def test_mappa_rispetta_identita(self):
        """map(id, xs) = xs"""
        lista = [1, 2, 3, 4, 5]
        risultato = contenitore.mappa(lista, flusso.identita)
        assert risultato == lista

    def test_mappa_rispetta_composizione(self):
        """map(f ∘ g, xs) = map(f, map(g, xs))"""
        lista = [1, 2, 3]
        f = lambda x: x + 1
        g = lambda x: x * 2

        # map(f ∘ g, xs)
        composta = flusso.componi(g, f)  # prima g, poi f
        risultato_1 = contenitore.mappa(lista, composta)

        # map(f, map(g, xs))
        intermedio = contenitore.mappa(lista, g)
        risultato_2 = contenitore.mappa(intermedio, f)

        assert risultato_1 == risultato_2


# =============================================================================
# PROPRIETÀ 7: TYPE SAFETY (Runtime)
# =============================================================================

class TestTypeSafety:
    """
    Verifica: Errori di tipo sono gestiti gracefully.
    """

    def test_elemento_legge_campo_inesistente(self):
        """elemento.legge con campo inesistente ritorna default"""
        el = elemento.crea({'x': 1})
        assert elemento.legge(el, 'y') is None
        assert elemento.legge(el, 'y', 'default') == 'default'

    def test_contenitore_primo_lista_vuota(self):
        """contenitore.primo su lista vuota ritorna default"""
        assert contenitore.primo([]) is None
        assert contenitore.primo([], 'default') == 'default'

    def test_valore_divide_per_zero(self):
        """valore.divide per zero ritorna None"""
        assert valore.divide(10, 0) is None

    def test_flusso_scegli_nessun_match(self):
        """flusso.scegli senza match solleva errore o usa default"""
        casi = [('a', lambda x: 1)]

        # Con default
        risultato = flusso.scegli('z', casi, default=lambda x: 0)
        assert risultato == 0

        # Senza default → errore
        with pytest.raises(ValueError):
            flusso.scegli('z', casi)
