# Języki skryptowe - API - lista 5
## Jakub Smołka - 246987

W implementacji listy 5 użyłem następujących technologii:
* Python 3.7
* API - Flask
* Baza danych - PostgreSQL

## Instalacja i uruchomienie

```bash
pip install requests
pip install flask
pip install psycopg2

python3.7 main.py
```
Do uruchomienia aplikacji potrzebna będzie baza danych PostgreSQL postawiona lokalnie. W katalogu z kodem należy umieścić plik database.ini:
```ini
[postgresql]
host=localhost
database=dvdrental
user=<user>
password=<user_password>
```
Bazę danych 'dvdrental', z której korzystałem do wykonania tego zadania można znaleźć [tutaj](https://www.postgresqltutorial.com/postgresql-sample-database/).


## Opis adresacji i działania API

### Adresacja

Notowania z konkretnego dnia lub zakresu dat wraz z informacją 'interpolated':
```python
GET http://127.0.0.1:5000/USD/<data> 
GET http://127.0.0.1:5000/USD/<data_od>/<data_do> 
```
Suma sprzedaży wraz z przeliczeniem po kursie z danego dnia, lub zakresu dat:
```python
GET http://127.0.0.1:5000/sales/<data>
GET http://127.0.0.1:5000/sales/<data_od>/<data_do>
```

### Cache

W zadaniu zaimplementowałem bardzo prosty system cache'u, który sprawdza czy zapytanie użytkownika zostało wykonane wcześniej i jeśli tak, to zwraca zapamiętaną wcześniej wartość. W przeciwnym wypadku zapamiętuje odpowiedź na zapytanie użytkownika w słowniku.

Cache odświeża się co ok. **24 godziny.**

### Limity

Limity są nałożone na adres sieciowy użytkownika i mają następujące ograniczenia:
* Zapytania o notowania: **10 na minutę**
* Zapytania o sprzedaż z konkretnego dnia: **5 na minutę**
* Zapytania o sprzedaż z zakresu dat: **1 na minutę** (do testów)

Oprócz tego zaimplementowane są również domyślne limity.

Odpowiedzią na przekroczony limit zapytań jest kod błędu **429**.

## Struktura projektu

* **api.py** - główny program FLASK'a odpowiedzialny za API, uruchamiany w **main.py**
* **cache.py** - prosty system cache'u opisany wyżej
* **db_config.py** - plik konfiguracyjny zapewniający dostęp do PostgreSQL (korzysta z pliku database.ini, którego nie zamieszczam w repo)
* **db_handler.py** - zawiera wszystkie operacje korzystające z bazy danych oraz sprawdza poprawności zapytań, główna logika programu
* **db_init.py** - inicjalizacja bazy, danymi z api NBP, wykonywana tylko raz przy uruchomieniu programu
* **stock_rates.py** - plik z poprzednich laboratoriów pobierający dane z api NBP, wykorzystywany w **db_init.py**
* **main.py** - inicjalizacja bazy oraz uruchomienie API

