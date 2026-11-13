# Steam × Wikipedia

**System analizy recenzji gier na platformie Steam w kontekście zainteresowania w Wikipedii**

Projekt realizowany w ramach przedmiotu Składowanie danych w systemach Big Data, Politechnika Warszawska, 2026.

## Cel projektu

Celem projektu jest zbudowanie systemu do analizy recenzji gier komputerowych publikowanych na platformie Steam, zestawionych z zainteresowaniem tymi grami w internecie, mierzonym liczbą wyświetleń artykułów w Wikipedii. System będzie codziennie pobierał nowe dane z obu źródeł, składował pełną historię i generował widoki wsadowe pozwalające odpowiedzieć m.in. na pytania:

- kiedy dochodzi do tzw. *review bombingu*, czyli nagłego napływu negatywnych recenzji, i czy system potrafi wykryć takie zdarzenia,
- jak zmienia się reputacja gry w czasie (np. po premierze, aktualizacjach),
- jak czas gry autora w chwili pisania recenzji wpływa na jej wydźwięk i czy autorzy negatywnych recenzji grają dalej,
- czy wzrost zainteresowania grą w Wikipedii jest związany z falą recenzji na Steamie.

### Potencjalne korzyści

- **Twórcy gier** – analiza napływu recenzji i monitorowanie reputacji gry.
- **Gracze i kupujący** – rzetelniejsza ocena gry dzięki odróżnieniu rzeczywistego spadku jej jakości od krótkotrwałej fali negatywnych opinii.
- **Analitycy rynku gier** – pełniejszy obraz popularności gry, łączący aktywność jej społeczności z zainteresowaniem szerszej publiczności, mierzonym ruchem w Wikipedii.

## Struktura repozytorium

- [`bigdata-docker/`](bigdata-docker/) – środowisko Docker (Hadoop, Hive, Spark, Kafka, NiFi, HBase) z instrukcją uruchomienia
- [`scripts/`](scripts/) – skrypty w Pythonie do pobierania i testowania danych

## Autorzy:

- Aleksandra Zawadka – [@Ola-zaw](https://github.com/Ola-zaw)
- Martyna Sadowska – [@Martyna-265](https://github.com/Martyna-265)
