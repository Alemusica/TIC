"""
Test per gli Archetipi PTI (Livello 1)
"""

import pytest
import sys
sys.path.insert(0, '..')

from tic_core.archetipi import elemento, contenitore, confronta, valore, testo


class TestElemento:
    """Test archetipo elemento."""

    def test_crea(self):
        e = elemento.crea({'nome': 'test', 'valore': 42})
        assert elemento.legge(e, 'nome') == 'test'
        assert elemento.legge(e, 'valore') == 42

    def test_crea_vuoto(self):
        e = elemento.crea()
        assert elemento.campi(e) == []

    def test_legge_default(self):
        e = elemento.crea({'x': 1})
        assert elemento.legge(e, 'y', 'default') == 'default'

    def test_scrive_immutabile(self):
        e1 = elemento.crea({'x': 1})
        e2 = elemento.scrive(e1, 'x', 2)
        assert elemento.legge(e1, 'x') == 1  # originale non modificato
        assert elemento.legge(e2, 'x') == 2

    def test_esiste(self):
        e = elemento.crea({'x': 1})
        assert elemento.esiste(e) is True
        assert elemento.esiste(None) is False

    def test_elimina(self):
        e = elemento.crea({'x': 1})
        e2 = elemento.elimina(e)
        assert elemento.esiste(e) is True
        assert elemento.esiste(e2) is False


class TestContenitore:
    """Test archetipo contenitore."""

    def test_crea(self):
        c = contenitore.crea([1, 2, 3])
        assert contenitore.conta(c) == 3

    def test_aggiunge_immutabile(self):
        c1 = contenitore.crea([1, 2])
        c2 = contenitore.aggiunge(c1, 3)
        assert c1 == [1, 2]
        assert c2 == [1, 2, 3]

    def test_rimuove(self):
        c = contenitore.crea([1, 2, 3])
        c2 = contenitore.rimuove(c, 2)
        assert c2 == [1, 3]

    def test_filtra(self):
        c = contenitore.crea([1, 2, 3, 4, 5])
        pari = contenitore.filtra(c, lambda x: x % 2 == 0)
        assert pari == [2, 4]

    def test_mappa(self):
        c = contenitore.crea([1, 2, 3])
        doppi = contenitore.mappa(c, lambda x: x * 2)
        assert doppi == [2, 4, 6]

    def test_riduce(self):
        c = contenitore.crea([1, 2, 3, 4])
        somma = contenitore.riduce(c, lambda acc, x: acc + x, 0)
        assert somma == 10

    def test_primo_ultimo(self):
        c = contenitore.crea([1, 2, 3])
        assert contenitore.primo(c) == 1
        assert contenitore.ultimo(c) == 3
        assert contenitore.primo([], 'vuoto') == 'vuoto'

    def test_trova(self):
        c = contenitore.crea([1, 2, 3, 4])
        trovato = contenitore.trova(c, lambda x: x > 2)
        assert trovato == 3

    def test_vuoto(self):
        assert contenitore.vuoto([]) is True
        assert contenitore.vuoto([1]) is False


class TestConfronta:
    """Test archetipo confronta."""

    def test_uguale_diverso(self):
        assert confronta.uguale(1, 1) is True
        assert confronta.uguale(1, 2) is False
        assert confronta.diverso(1, 2) is True

    def test_maggiore_minore(self):
        assert confronta.maggiore(5, 3) is True
        assert confronta.minore(3, 5) is True

    def test_almeno_alpiu(self):
        assert confronta.almeno(5, 5) is True
        assert confronta.almeno(5, 3) is True
        assert confronta.alpiù(3, 5) is True

    def test_tra(self):
        assert confronta.tra(5, 1, 10) is True
        assert confronta.tra(0, 1, 10) is False

    def test_nullo(self):
        assert confronta.nullo(None) is True
        assert confronta.nullo(0) is False

    def test_vero_falso(self):
        assert confronta.vero(1) is True
        assert confronta.vero('') is False
        assert confronta.falso('') is True

    def test_in_lista(self):
        assert confronta.in_lista(2, [1, 2, 3]) is True
        assert confronta.in_lista(5, [1, 2, 3]) is False


class TestValore:
    """Test archetipo valore."""

    def test_incrementa_decrementa(self):
        assert valore.incrementa(5) == 6
        assert valore.incrementa(5, 3) == 8
        assert valore.decrementa(5) == 4

    def test_moltiplica_divide(self):
        assert valore.moltiplica(3, 4) == 12
        assert valore.divide(10, 2) == 5.0
        assert valore.divide(10, 0) is None

    def test_minimo_massimo(self):
        nums = [3, 1, 4, 1, 5]
        assert valore.minimo(nums) == 1
        assert valore.massimo(nums) == 5

    def test_somma_media(self):
        nums = [2, 4, 6]
        assert valore.somma(nums) == 12
        assert valore.media(nums) == 4.0

    def test_clamp(self):
        assert valore.clamp(15, 0, 10) == 10
        assert valore.clamp(-5, 0, 10) == 0
        assert valore.clamp(5, 0, 10) == 5


class TestTesto:
    """Test archetipo testo."""

    def test_pulisce(self):
        assert testo.pulisce('  hello   world  ') == 'hello world'

    def test_maiuscolo_minuscolo(self):
        assert testo.maiuscolo('hello') == 'HELLO'
        assert testo.minuscolo('HELLO') == 'hello'

    def test_contiene(self):
        assert testo.contiene('hello world', 'wor') is True
        assert testo.contiene('hello', 'xyz') is False

    def test_inizia_finisce(self):
        assert testo.inizia('hello', 'hel') is True
        assert testo.finisce('hello', 'lo') is True

    def test_divide_unisce(self):
        assert testo.divide('a,b,c', ',') == ['a', 'b', 'c']
        assert testo.unisce(['a', 'b', 'c'], '-') == 'a-b-c'

    def test_vuoto(self):
        assert testo.vuoto('') is True
        assert testo.vuoto('   ') is True
        assert testo.vuoto('a') is False

    def test_tronca(self):
        assert testo.tronca('hello world', 8) == 'hello...'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
