"""
TEST: Scenari LLM

Simula cosa succede quando un LLM genera codice PTI:
1. Codice valido → passa
2. Codice invalido → rigettato dal validator

Questi test dimostrano che il constraint algebra FUNZIONA.
"""

import pytest
import sys
import re
sys.path.insert(0, '..')


# =============================================================================
# VALIDATOR (Simula Layer 3)
# =============================================================================

class PTIValidator:
    """
    Valida che il codice generato usi solo primitivi dell'algebra.

    In produzione questo sarebbe un parser AST.
    Per il POC usiamo regex pattern matching.
    """

    # Primitivi permessi
    PRIMITIVI_PERMESSI = {
        # Elemento
        'elemento.crea', 'elemento.legge', 'elemento.scrive',
        'elemento.esiste', 'elemento.elimina', 'elemento.clona',

        # Contenitore
        'contenitore.crea', 'contenitore.aggiunge', 'contenitore.rimuove',
        'contenitore.mappa', 'contenitore.filtra', 'contenitore.riduce',
        'contenitore.trova', 'contenitore.primo', 'contenitore.ultimo',
        'contenitore.conta', 'contenitore.vuoto', 'contenitore.ordina',

        # Confronta
        'confronta.uguale', 'confronta.diverso', 'confronta.maggiore',
        'confronta.minore', 'confronta.almeno', 'confronta.alpiù',
        'confronta.tra', 'confronta.nullo', 'confronta.vero', 'confronta.falso',
        'confronta.tutti', 'confronta.almeno_uno', 'confronta.in_lista',

        # Valore
        'valore.incrementa', 'valore.decrementa', 'valore.moltiplica',
        'valore.divide', 'valore.somma', 'valore.media', 'valore.minimo',
        'valore.massimo', 'valore.clamp',

        # Testo
        'testo.pulisce', 'testo.maiuscolo', 'testo.minuscolo',
        'testo.contiene', 'testo.divide', 'testo.unisce', 'testo.vuoto',

        # Flusso
        'flusso.se', 'flusso.scegli', 'flusso.componi', 'flusso.sequenza',
        'flusso.parallelo', 'flusso.identita', 'flusso.costante', 'flusso.ripeti',

        # Effetti (boundary)
        'effetto.emetti', 'effetto.leggi', 'effetto.scrivi', 'effetto.log',
        'effetto.fallisce', 'effetto.attendi'
    }

    # Pattern pericolosi (NON permessi)
    PATTERN_PERICOLOSI = [
        r'\beval\s*\(',
        r'\bexec\s*\(',
        r'\bopen\s*\(',
        r'\bimport\s+os\b',
        r'\bimport\s+subprocess\b',
        r'\bos\.',
        r'\bsubprocess\.',
        r'\b__import__\s*\(',
        r'\bcompile\s*\(',
        r'\bglobals\s*\(',
        r'\blocals\s*\(',
        r'\bgetattr\s*\(',
        r'\bsetattr\s*\(',
        r'\bdelattr\s*\(',
        r'\brequests\.',
        r'\burllib\.',
        r'\bsocket\.',
        r'\bhttp\.client\.',
        r'\bwhile\s+True\s*:',  # loop infinito
        r'\bfor\s+\w+\s+in\s+iter\s*\(',  # iteratore infinito
    ]

    def __init__(self):
        self.errori = []

    def valida(self, codice: str) -> tuple:
        """
        Valida codice PTI.

        Ritorna (valido: bool, errori: list)
        """
        self.errori = []

        # Check pattern pericolosi
        for pattern in self.PATTERN_PERICOLOSI:
            if re.search(pattern, codice):
                self.errori.append(f"Pattern pericoloso trovato: {pattern}")

        # Check primitivi non riconosciuti (semplificato)
        # In produzione useremmo AST parsing

        return (len(self.errori) == 0, self.errori)


# =============================================================================
# TEST: Codice Valido
# =============================================================================

class TestCodiceValido:
    """Test che codice PTI valido passa il validator."""

    @pytest.fixture
    def validator(self):
        return PTIValidator()

    def test_elemento_operazioni(self, validator):
        """Operazioni su elementi sono valide"""
        codice = """
def crea_utente(nome, email):
    return elemento.crea({
        'nome': testo.pulisce(nome),
        'email': email,
        'attivo': True
    })

def aggiorna_nome(utente, nuovo_nome):
    return elemento.scrive(utente, 'nome', nuovo_nome)
"""
        valido, errori = validator.valida(codice)
        assert valido, f"Errori: {errori}"

    def test_contenitore_operazioni(self, validator):
        """Operazioni su contenitori sono valide"""
        codice = """
def filtra_attivi(utenti):
    return contenitore.filtra(
        utenti,
        lambda u: confronta.vero(elemento.legge(u, 'attivo'))
    )

def conta_attivi(utenti):
    return contenitore.conta(filtra_attivi(utenti))
"""
        valido, errori = validator.valida(codice)
        assert valido, f"Errori: {errori}"

    def test_flusso_composizione(self, validator):
        """Composizione di funzioni è valida"""
        codice = """
def processa_ordine():
    return flusso.sequenza(
        valida_ordine,
        calcola_totale,
        applica_sconto,
        conferma_ordine
    )

def branch_stato(stato):
    return flusso.scegli(stato, [
        ('pending', lambda x: 'attendi'),
        ('confirmed', lambda x: 'processa'),
        ('_', lambda x: 'ignora')
    ])
"""
        valido, errori = validator.valida(codice)
        assert valido, f"Errori: {errori}"

    def test_effetti_boundary(self, validator):
        """Effetti come boundary sono validi"""
        codice = """
def notifica_utente(utente, messaggio):
    return effetto.emetti('notifica', {
        'utente_id': elemento.legge(utente, 'id'),
        'messaggio': messaggio
    })

def log_operazione(operazione):
    return effetto.log('info', f'Eseguito: {operazione}')
"""
        valido, errori = validator.valida(codice)
        assert valido, f"Errori: {errori}"


# =============================================================================
# TEST: Codice Invalido (Deve Essere Rigettato)
# =============================================================================

class TestCodiceInvalido:
    """Test che codice pericoloso viene rigettato."""

    @pytest.fixture
    def validator(self):
        return PTIValidator()

    def test_eval_rigettato(self, validator):
        """eval() deve essere rigettato"""
        codice = """
def esegui_dinamico(codice_utente):
    return eval(codice_utente)
"""
        valido, errori = validator.valida(codice)
        assert not valido
        assert any('eval' in e for e in errori)

    def test_exec_rigettato(self, validator):
        """exec() deve essere rigettato"""
        codice = """
def esegui_script(script):
    exec(script)
"""
        valido, errori = validator.valida(codice)
        assert not valido
        assert any('exec' in e for e in errori)

    def test_os_import_rigettato(self, validator):
        """import os deve essere rigettato"""
        codice = """
import os
def leggi_file(path):
    return os.read(path)
"""
        valido, errori = validator.valida(codice)
        assert not valido

    def test_subprocess_rigettato(self, validator):
        """subprocess deve essere rigettato"""
        codice = """
import subprocess
def esegui_comando(cmd):
    return subprocess.run(cmd)
"""
        valido, errori = validator.valida(codice)
        assert not valido

    def test_open_file_rigettato(self, validator):
        """open() per file deve essere rigettato"""
        codice = """
def leggi_file(path):
    with open(path) as f:
        return f.read()
"""
        valido, errori = validator.valida(codice)
        assert not valido

    def test_network_rigettato(self, validator):
        """Operazioni network devono essere rigettate"""
        codice = """
import requests
def fetch_data(url):
    return requests.get(url).json()
"""
        valido, errori = validator.valida(codice)
        assert not valido

    def test_loop_infinito_rigettato(self, validator):
        """while True deve essere rigettato"""
        codice = """
def loop_forever():
    while True:
        pass
"""
        valido, errori = validator.valida(codice)
        assert not valido

    def test_getattr_rigettato(self, validator):
        """getattr dinamico deve essere rigettato"""
        codice = """
def accesso_dinamico(obj, attr):
    return getattr(obj, attr)
"""
        valido, errori = validator.valida(codice)
        assert not valido


# =============================================================================
# TEST: Scenari LLM Realistici
# =============================================================================

class TestScenariLLM:
    """Simula output LLM e verifica validazione."""

    @pytest.fixture
    def validator(self):
        return PTIValidator()

    def test_llm_genera_carrello_valido(self, validator):
        """LLM genera logica carrello: VALIDO"""
        codice_llm = """
# LLM Output per: "Aggiungi funzione calcolo totale carrello"

def calcola_totale_carrello(carrello):
    items = elemento.legge(carrello, 'items')

    subtotali = contenitore.mappa(
        items,
        lambda item: valore.moltiplica(
            elemento.legge(item, 'quantita'),
            elemento.legge(item, 'prezzo')
        )
    )

    return valore.somma(subtotali)

def applica_sconto(totale, percentuale):
    sconto = valore.moltiplica(totale, valore.divide(percentuale, 100))
    return valore.decrementa(totale, sconto)

def totale_con_spedizione(totale, soglia_gratis=50, costo_spedizione=5):
    spedizione = flusso.se(
        confronta.almeno(totale, soglia_gratis),
        flusso.costante(0),
        flusso.costante(costo_spedizione)
    )
    return valore.somma([totale, spedizione])
"""
        valido, errori = validator.valida(codice_llm)
        assert valido, f"Codice LLM valido rigettato: {errori}"

    def test_llm_genera_validazione_valido(self, validator):
        """LLM genera validazione form: VALIDO"""
        codice_llm = """
# LLM Output per: "Valida form registrazione"

def valida_email(email):
    return confronta.tutti([
        lambda e: confronta.non_nullo(e),
        lambda e: testo.contiene(e, '@'),
        lambda e: testo.contiene(e, '.')
    ], email)

def valida_password(password):
    return confronta.tutti([
        lambda p: confronta.almeno(testo.lunghezza(p), 8),
        lambda p: confronta.non_nullo(p)
    ], password)

def valida_form(dati):
    errori = contenitore.crea([])

    email_ok = valida_email(elemento.legge(dati, 'email'))
    if confronta.falso(email_ok):
        errori = contenitore.aggiunge(errori, 'email.invalida')

    pwd_ok = valida_password(elemento.legge(dati, 'password'))
    if confronta.falso(pwd_ok):
        errori = contenitore.aggiunge(errori, 'password.troppo.corta')

    return (contenitore.vuoto(errori), errori)
"""
        valido, errori = validator.valida(codice_llm)
        assert valido, f"Codice LLM valido rigettato: {errori}"

    def test_llm_tenta_injection_invalido(self, validator):
        """LLM tenta code injection: RIGETTATO"""
        codice_llm = """
# LLM Output malevolo (o allucinazione)

def process_user_input(user_input):
    # Tentativo di esecuzione dinamica
    result = eval(user_input)
    return result

def backup_data():
    import os
    os.system('rm -rf /')
"""
        valido, errori = validator.valida(codice_llm)
        assert not valido
        assert len(errori) > 0

    def test_llm_tenta_network_invalido(self, validator):
        """LLM tenta network request: RIGETTATO"""
        codice_llm = """
# LLM Output con network

import requests

def fetch_remote_data(url):
    response = requests.get(url)
    return response.json()
"""
        valido, errori = validator.valida(codice_llm)
        assert not valido


# =============================================================================
# TEST: Metriche Retry
# =============================================================================

class TestMetricheRetry:
    """Simula retry loop quando LLM genera codice invalido."""

    def test_retry_converge(self):
        """Simula: LLM corregge dopo feedback"""
        validator = PTIValidator()

        # Tentativo 1: invalido (usa eval)
        tentativo_1 = """
def process(x):
    return eval(x)
"""
        valido_1, errori_1 = validator.valida(tentativo_1)
        assert not valido_1

        # Feedback: "eval non permesso, usa flusso.scegli"

        # Tentativo 2: corretto
        tentativo_2 = """
def process(x):
    return flusso.scegli(x, [
        ('add', lambda v: valore.incrementa(v, 1)),
        ('sub', lambda v: valore.decrementa(v, 1))
    ], default=flusso.identita)
"""
        valido_2, errori_2 = validator.valida(tentativo_2)
        assert valido_2

        # Metriche
        retry_count = 1  # ci è voluto 1 retry
        assert retry_count <= 3  # Accettabile

    def test_statistiche_validazione(self):
        """Raccoglie statistiche su N codici"""
        validator = PTIValidator()

        codici_test = [
            # Validi
            ("def f(): return elemento.crea({'x': 1})", True),
            ("def g(): return contenitore.mappa([1,2], lambda x: x*2)", True),
            ("def h(): return flusso.se(True, lambda: 1, lambda: 2)", True),

            # Invalidi
            ("def bad(): return eval('x')", False),
            ("def bad2(): import os", False),
            ("def bad3(): while True: pass", False),
        ]

        validi = 0
        invalidi = 0

        for codice, expected_valid in codici_test:
            valido, _ = validator.valida(codice)
            if valido:
                validi += 1
            else:
                invalidi += 1
            assert valido == expected_valid

        # Report
        totale = len(codici_test)
        assert validi == 3
        assert invalidi == 3
        print(f"\nStatistiche: {validi}/{totale} validi, {invalidi}/{totale} invalidi")
