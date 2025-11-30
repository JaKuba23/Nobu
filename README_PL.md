# Nobu

```
 ███╗   ██╗ ██████╗ ██████╗ ██╗   ██╗
 ████╗  ██║██╔═══██╗██╔══██╗██║   ██║
 ██╔██╗ ██║██║   ██║██████╔╝██║   ██║
 ██║╚██╗██║██║   ██║██╔══██╗██║   ██║
 ██║ ╚████║╚██████╔╝██████╔╝╚██████╔╝
 ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝  ╚═════╝ 
```

**Lekki skaner portów CLI do rozpoznania sieciowego i nauki.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/JaKuba23/nobu/actions/workflows/ci.yml/badge.svg)](https://github.com/JaKuba23/nobu/actions)

---

## Motywacja

Stworzyłem Nobu, aby pogłębić swoją wiedzę z zakresu podstaw sieci, jednocześnie rozwijając umiejętności w Pythonie. Praca nad koncepcjami takimi jak TCP handshake, programowanie socketów i współbieżne wykonywanie pomogła mi połączyć wiedzę teoretyczną z praktyczną implementacją.

Projekt został nazwany na cześć postaci z Ghost of Tsushima - subtelne nawiązanie do motywów skradania i rozpoznania, które pasują do koncepcji skanowania sieci.

**Ważne:** To narzędzie jest przeznaczone wyłącznie do celów edukacyjnych i autoryzowanego testowania. Nigdy nie skanuj sieci ani systemów bez wyraźnej zgody właściciela.

---

## Funkcje

- **Skanowanie TCP Connect** — Pełny TCP handshake dla niezawodnego wykrywania portów
- **Obsługa zakresów CIDR** — Skanuj całe podsieci z notacją `/24`, `/16`
- **Wielowątkowy silnik** — Konfigurowalna pula wątków (1-1000 wątków)
- **Pobieranie banerów** — Wyodrębnianie informacji o usługach z otwartych portów
- **Predefiniowane profile** — Szybki dostęp do popularnych konfiguracji skanowania
- **Kolorowy output** — Kolory ANSI dla łatwej interpretacji wyników
- **Eksport JSON/CSV** — Zapisuj wyniki do dalszej analizy
- **Śledzenie postępu** — Pasek postępu w czasie rzeczywistym
- **Zero zależności** — Używa tylko biblioteki standardowej Pythona

---

## Instalacja

### Wymagania

- Python 3.10 lub nowszy
- System Unix-like (Linux, macOS) lub Windows

### Ze źródła

```bash
# Sklonuj repozytorium
git clone https://github.com/JaKuba23/nobu.git
cd nobu

# Utwórz środowisko wirtualne (zalecane)
python -m venv venv
source venv/bin/activate  # Na Windows: venv\Scripts\activate

# Zainstaluj w trybie deweloperskim
pip install -e .

# Sprawdź instalację
nobu --version
```

### Konfiguracja deweloperska

```bash
# Zainstaluj z zależnościami deweloperskimi
pip install -e ".[dev]"

# Lub użyj pliku requirements
pip install -r requirements-dev.txt
```

---

## Użycie

### Podstawowe skanowanie

Skanuj popularne porty na pojedynczym hoście:

```bash
nobu scan --target 192.168.1.1 --ports 1-1024
```

### Używanie profili

Profile zapewniają predefiniowane konfiguracje dla typowych scenariuszy:

```bash
# Szybkie skanowanie - top 100 portów
nobu profile fast --target 192.168.1.1

# Porty serwerów webowych
nobu profile web --target example.com

# Porty baz danych
nobu profile database --target db.internal

# Pełne skanowanie - porty 1-1024
nobu profile full --target 10.0.0.5
```

Dostępne profile:

| Profil | Porty | Opis |
|--------|-------|------|
| `fast` | Top 100 | Szybkie skanowanie rozpoznawcze |
| `full` | 1-1024 | Wszystkie znane porty |
| `web` | 15 portów | HTTP, HTTPS, popularne frameworki |
| `database` | 15 portów | MySQL, PostgreSQL, MongoDB, Redis |
| `mail` | 8 portów | SMTP, POP3, IMAP |
| `stealth` | Top 20 | Wolne, dyskretne skanowanie |

### Skanowanie podsieci

Skanuj całe zakresy sieci używając notacji CIDR:

```bash
# Skanuj podsieć /24
nobu scan --target 192.168.1.0/24 --ports 22,80,443

# Skanuj konkretne porty w sieci
nobu scan --target 10.0.0.0/24 --ports 3389 --threads 200
```

### Pobieranie banerów

Próbuj pobrać banery usług z otwartych portów:

```bash
nobu scan --target 192.168.1.1 --ports 20-100 --banner
```

### Eksport wyników

Zapisz wyniki skanowania do JSON lub CSV:

```bash
# Output JSON
nobu scan --target 192.168.1.1 --ports 1-1024 --output results.json

# Output CSV
nobu profile fast --target example.com --output scan.csv
```

### Dodatkowe opcje

```bash
# Dostosuj timeout (sekundy)
nobu scan --target slow-host.local --ports 80,443 --timeout 3.0

# Zwiększ liczbę wątków dla szybszych skanów
nobu scan --target 192.168.1.1 --ports 1-65535 --threads 500

# Wyłącz kolorowy output (do pipe'owania/logowania)
nobu scan --target 192.168.1.1 --ports 80 --no-color

# Tryb cichy - pokazuj tylko otwarte porty
nobu scan --target 192.168.1.1 --ports 1-1024 --quiet

# Tryb szczegółowy - pokazuj info debugowania
nobu scan --target 192.168.1.1 --ports 80 --verbose
```

### Referencja komend

```
nobu <komenda> [opcje]

Komendy:
  scan      Wykonaj niestandardowe skanowanie portów
  profile   Uruchom predefiniowany profil skanowania

Opcje globalne:
  --version     Pokaż informacje o wersji
  --no-color    Wyłącz kolorowy output
  --help        Pokaż pomoc
```

---

## Jak to działa

### Przegląd architektury

```
┌─────────────────────────────────────────────────────────────────┐
│                         Warstwa CLI                              │
│  ┌─────────┐    ┌──────────────┐    ┌─────────────────────┐     │
│  │ argparse│───▶│ NobuCLI      │───▶│ Profile/Scan Config │     │
│  └─────────┘    └──────────────┘    └─────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Silnik skanera                             │
│  ┌─────────────────┐    ┌─────────────────────────────────┐     │
│  │ ThreadPoolExec. │───▶│ Wątki robocze (scan_port)       │     │
│  │ (concurrent.    │    │ ┌────────┐ ┌────────┐ ┌────────┐│     │
│  │  futures)       │    │ │Socket 1│ │Socket 2│ │Socket N││     │
│  └─────────────────┘    │ └────────┘ └────────┘ └────────┘│     │
│                         └─────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Warstwa wyjściowa                          │
│  ┌─────────────────┐    ┌──────────────┐    ┌───────────────┐   │
│  │ OutputFormatter │───▶│ Kolory ANSI  │───▶│ JSON/CSV      │   │
│  │ (wyrównany tekst)│   │ (opcjonalne) │    │ (opcjonalne)  │   │
│  └─────────────────┘    └──────────────┘    └───────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Proces skanowania

1. **Rozwiązywanie celu**: Nazwy hostów są rozwiązywane na adresy IP. Zakresy CIDR są rozwijane do list pojedynczych hostów.

2. **Tworzenie puli wątków**: Inicjowany jest `ThreadPoolExecutor` z określoną liczbą wątków roboczych.

3. **Skanowanie portów**: Każde skanowanie portu tworzy socket TCP i próbuje `connect()`. Wynik określa stan portu:
   - **Połączenie udane** → Port jest `OPEN`
   - **Połączenie odrzucone** → Port jest `CLOSED`
   - **Timeout/Brak odpowiedzi** → Port jest `FILTERED`

4. **Pobieranie banerów** (opcjonalne): Dla otwartych portów skaner próbuje odebrać dane lub wysyła podstawowe zapytanie HTTP, aby wyodrębnić informacje o usłudze.

5. **Agregacja wyników**: Wyniki są zbierane, sortowane według numeru portu i formatowane do wyświetlenia.

### Szczegóły techniczne

Skaner używa **skanowania TCP Connect**, które wykonuje pełny trójstronny handshake:

```
Klient          Serwer
  │    SYN       │
  │─────────────▶│
  │   SYN-ACK    │
  │◀─────────────│
  │    ACK       │
  │─────────────▶│
  │  (połączono) │
```

To podejście jest niezawodne, ale nie jest dyskretne - pozostawia logi połączeń na systemach docelowych. Do profesjonalnych testów penetracyjnych narzędzia takie jak Nmap z skanowaniem SYN zapewniają lepsze opcje.

**Rozważania wydajnościowe:**

- Domyślna liczba wątków (100) równoważy szybkość i użycie zasobów
- Wyższa liczba wątków poprawia szybkość, ale może wywołać rate limiting
- Timeouty socketów wpływają na czas skanowania na filtrowanych/wolnych hostach
- Zakresy CIDR > /16 są blokowane, aby zapobiec przypadkowym skanom na dużą skalę

---

## Struktura projektu

```
nobu/
├── nobu/
│   ├── __init__.py     # Metadane pakietu, banner ASCII
│   ├── __main__.py     # Punkt wejścia modułu
│   ├── cli.py          # Parsowanie argumentów, dyspozycja komend
│   ├── scanner.py      # Rdzeń silnika skanowania
│   ├── output.py       # Formatowanie, kolory, eksport
│   └── utils.py        # Parsowanie portów/celów, helpery
├── tests/
│   ├── test_utils.py   # Testy funkcji pomocniczych
│   ├── test_scanner.py # Testy logiki skanera
│   └── test_output.py  # Testy formatowania wyjścia
├── examples/
│   └── commands.md     # Referencja przykładowych komend
├── .github/
│   └── workflows/
│       └── ci.yml      # GitHub Actions CI
├── pyproject.toml      # Konfiguracja projektu
├── requirements-dev.txt
├── LICENSE
├── README.md           # Dokumentacja angielska
└── README_PL.md        # Dokumentacja polska
```

---

## Testowanie

Uruchom zestaw testów:

```bash
# Uruchom wszystkie testy
pytest

# Z raportem pokrycia
pytest --cov=nobu --cov-report=term-missing

# Konkretny plik testowy
pytest tests/test_utils.py -v
```

---

## Docker Test Lab

Projekt zawiera środowisko Docker Compose do bezpiecznego, legalnego testowania. Tworzy izolowane kontenery z różnymi usługami do skanowania.

### Szybki start

```bash
cd docker-lab
docker-compose up -d

# Skanuj lab
nobu profile lab --target 127.0.0.1 --banner
```

### Dostępne usługi

| Usługa      | Port(y)     | Opis                         |
|-------------|-------------|------------------------------|
| Nginx       | 8080, 8443  | Serwer web (HTTP/HTTPS)      |
| Apache      | 8081        | Alternatywny serwer web      |
| SSH         | 2222        | Serwer OpenSSH               |
| MySQL       | 3306        | Baza danych MySQL 8.0        |
| PostgreSQL  | 5432        | Baza danych PostgreSQL 15    |
| Redis       | 6379        | Cache Redis                  |
| MongoDB     | 27017       | Baza danych MongoDB 6        |
| MailHog     | 1025, 8025  | Serwer SMTP + Web UI         |
| FTP         | 21          | Serwer FTP vsftpd            |

Zobacz [docker-lab/README.md](docker-lab/README.md) po szczegółową dokumentację.

---

## Ograniczenia i etyka

### Ograniczenia techniczne

- **Tylko TCP** — Brak skanowania UDP (planowane na przyszłe wydanie)
- **Brak fingerprinting OS** — Wykrywa otwarte porty, nie systemy operacyjne
- **Skanowanie Connect** — Tworzy pełne połączenia, widoczne w logach celu
- **Brak technik evasion** — Rate limiting i IDS mogą blokować skany

### Wytyczne etyczne

To narzędzie jest przeznaczone do:

- ✅ Nauki podstaw sieci
- ✅ Skanowania własnych środowisk laboratoryjnych
- ✅ Autoryzowanych testów penetracyjnych z pisemną zgodą
- ✅ Rozwiązywania problemów sieciowych na systemach, którymi zarządzasz

To narzędzie **NIE** jest przeznaczone do:

- ❌ Skanowania sieci bez autoryzacji
- ❌ Omijania kontroli bezpieczeństwa
- ❌ Jakiejkolwiek złośliwej lub nielegalnej działalności

**Zawsze uzyskaj pisemną zgodę przed skanowaniem jakiejkolwiek sieci lub systemu, którego nie jesteś właścicielem.** Nieautoryzowane skanowanie portów może naruszać prawo w Twojej jurysdykcji (CFAA w USA, Computer Misuse Act w UK, Kodeks Karny w Polsce itp.).

Do profesjonalnych ocen bezpieczeństwa używaj sprawdzonych narzędzi takich jak Nmap, Masscan lub rozwiązań komercyjnych i postępuj zgodnie z politykami bezpieczeństwa swojej organizacji.

---

## Roadmapa

Planowane funkcje na przyszłe wydania:

- [ ] **Skanowanie UDP** — Wykrywanie usług UDP (DNS, SNMP itp.)
- [ ] **Service Fingerprinting** — Identyfikacja wersji usług za pomocą bazy sond
- [ ] **Raporty XML/HTML** — Generowanie sformatowanych raportów skanowania
- [ ] **Pliki konfiguracyjne** — Zapisywanie i ładowanie konfiguracji skanowania
- [ ] **Ping Sweep** — Wykrywanie hostów przed skanowaniem portów
- [ ] **Kontrola rate limiting** — Precyzyjna kontrola nad szybkością skanowania
- [ ] **System pluginów** — Rozszerzalna architektura dla niestandardowych sprawdzeń
- [ ] **Interfejs webowy** — Prosty dashboard do zarządzania skanami

---

## Współtworzenie

Współpraca jest mile widziana! Zobacz [CONTRIBUTING.md](CONTRIBUTING.md) po wytyczne.

1. Sforkuj repozytorium
2. Stwórz branch funkcjonalności (`git checkout -b feature/nowa-funkcja`)
3. Napisz testy dla swoich zmian
4. Upewnij się, że wszystkie testy przechodzą (`pytest`)
5. Złóż pull request

---

## Licencja

Ten projekt jest licencjonowany na warunkach licencji MIT - zobacz plik [LICENSE](LICENSE) po szczegóły.

---

## Podziękowania

- Techniki programowania socketów są inspirowane klasycznymi zasobami bezpieczeństwa sieciowego
- Wybór portów w profilach bazuje na popularnych konfiguracjach usług
- Struktura projektu podąża za najlepszymi praktykami pakietowania Pythona

---

**Notka:** "Nobu to subtelne nawiązanie do Ghost of Tsushima"

