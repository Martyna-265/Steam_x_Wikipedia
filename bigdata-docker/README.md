# Środowisko Docker – projekt Steam + Wikipedia

Wersje takie jak na maszynie z laboratoriów: Hadoop 3.4.1, Hive 4.1.0, Spark 3.5.6, Kafka 3.9.2, NiFi 1.28.0, HBase 2.6.7, Python 3.12, Java 17.

Środowisko jest podzielone na etapy, żeby zmieściło się w laptopie z 8 GB RAM:

| Etap | Usługi | Do czego |
|---|---|---|
| **baza** (zawsze włączona) | HDFS, metastore Hive | składowanie danych |
| **ingest** | + NiFi, Kafka, HiveServer2 | pobieranie danych i zapis do HDFS/Hive |
| **analysis** | + Jupyter ze Sparkiem, HBase | analizy, widoki, wykresy |

Naraz uruchamiamy **bazę + jeden etap**. Dane zapisują się na dysku, więc nic nie ginie przy przełączaniu.

## Czego potrzebujesz

- **Docker Desktop** dla Windows (z WSL 2, instalator ustawia to sam)
- **Git**
- ok. **30 GB** wolnego miejsca na dysku
- internet (pierwsze uruchomienie pobiera kilka GB)

Wszystkie komendy poniżej wpisuj w **PowerShellu** (nie w Git Bashu – on psuje ścieżki w komendach Dockera).

## Pierwsze uruchomienie (raz)

### 1. Ogranicz pamięć Dockera

Bez tego Docker może zabrać Windowsowi cały RAM. W PowerShellu:

```powershell
notepad $env:USERPROFILE\.wslconfig
```

Notatnik zapyta, czy utworzyć plik – kliknij **Tak**. Wklej i zapisz:

```ini
[wsl2]
memory=6GB
processors=4
swap=4GB
```

> Masz 16 GB RAM? Wpisz `memory=10GB`.
> Plik już istniał? Nie kasuj jego zawartości, tylko dopisz lub zmień te linie.

Potem zamknij Docker Desktop (ikonka przy zegarze → *Quit Docker Desktop*), wpisz:

```powershell
wsl --shutdown
```

i uruchom Docker Desktop ponownie. Poczekaj, aż na dole okna pojawi się *Engine running*.

### 2. Pobierz repozytorium

```powershell
git clone https://github.com/Martyna-265/Steam_x_Wikipedia.git
cd Steam_x_Wikipedia\bigdata-docker
```

Wszystkie kolejne komendy wpisuj w tym katalogu (`bigdata-docker`).

### 3. Pobierz sterownik bazy danych dla Hive

```powershell
Invoke-WebRequest -Uri https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.4/postgresql-42.7.4.jar -OutFile jars/postgresql-42.7.4.jar
```

### 4. Zbuduj obrazy

```powershell
docker compose --profile analysis build
```

Trwa ok. 10–20 minut.

### 5. Uruchom bazę

```powershell
docker compose up -d
```

Za pierwszym razem Docker pobierze obrazy Hadoopa i Hive (kilka GB), więc może to chwilę potrwać.

Gotowe, gdy http://localhost:9870 otwiera stronę HDFS, a w zakładce *Datanodes* jest 1 węzeł.

## Codzienna praca

### Etap ingest (NiFi, Kafka, Hive)

```powershell
docker compose --profile ingest up -d
```

Ta komenda uruchamia też bazę. NiFi startuje ok. 2 minut – potem otwórz http://localhost:8080/nifi.

### Etap analysis (Spark, HBase, Jupyter)

```powershell
docker compose stop nifi kafka hiveserver2
docker compose --profile analysis up -d
```

Jupyter: http://localhost:8888.

> Pierwsze uruchomienie Sparka z Hive w notebooku trwa ok. 2–3 minut, bo Spark pobiera biblioteki (~240 MB). Później startuje w kilkanaście sekund.

### Powrót do ingest

```powershell
docker compose stop jupyter hbase
docker compose --profile ingest up -d
```

### Koniec pracy

```powershell
docker compose --profile ingest --profile analysis stop
```

Następnym razem uruchom Docker Desktop i od razu wybrany etap (`--profile ingest up -d` albo `--profile analysis up -d`) – baza wystartuje razem z nim.

> ⚠️ **Nigdy nie używaj `docker compose down -v`** – kasuje wszystkie dane: HDFS, tabele Hive i przepływy NiFi.

## Adresy

| Usługa | Adres |
|---|---|
| HDFS | http://localhost:9870 |
| NiFi | http://localhost:8080/nifi |
| HiveServer2 (beeline / JDBC) | `localhost:10000`, UI: http://localhost:10002 |
| Jupyter Lab | http://localhost:8888 |
| HBase | http://localhost:16010 |
| Kafka | `kafka:9092` z NiFi i Jupytera, `localhost:29092` z Pythona na Windowsie |
| HBase Thrift (happybase) | `hbase:9090` z Jupytera, `localhost:9090` z Windowsa |

## Gdzie co jest

- `notebooks/` – notebooki Jupytera (widoczne w Jupyterze jako katalog główny)
- `data/input/` – pliki do wczytania przez NiFi (w NiFi to `/opt/nifi/input`)
- `config/` – konfiguracja Hadoopa, Hive i Sparka

## Ustawienia w NiFi

- **PutHDFS** → *Hadoop Configuration Resources*:
  `/opt/nifi/hadoop-conf/core-site.xml,/opt/nifi/hadoop-conf/hdfs-site.xml`
- **PublishKafka_2_6 / ConsumeKafka_2_6** → *Kafka Brokers*: `kafka:9092`
- **GetFile** → *Input Directory*: `/opt/nifi/input`

## Tabele Hive

Twórz tabele jako `EXTERNAL` w formacie ORC (np. w `/user/hive/external/steam_reviews`). Zwykłe tabele w Hive 4 mogą powstać jako transakcyjne (ACID), a takich Spark nie zapisze.

## Gdy coś nie działa

Komputer bardzo zwalnia albo kontener sam się restartuje – sprawdź `docker stats` i upewnij się, że działa tylko jeden etap naraz.
