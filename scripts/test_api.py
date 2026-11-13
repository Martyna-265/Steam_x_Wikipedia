import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone

HEADERS = {"User-Agent": "student-bigdata-project/1.0 (kontakt: twoj@email)"}  # Wikimedia wymaga User-Agent

# Kilka tytulow = artykul zmienil nazwe. Pageviews API nie podaza za przekierowaniami,
# a historia sprzed zmiany zostaje pod starym tytulem, wiec wyswietlenia sumujemy.
GAMES = [
    # review bomb
    ("Slay the Spire 2",         2868840, 2026, "review bomb", ["Slay_the_Spire_II", "Slay_the_Spire_2"]),
    ("Helldivers 2",             553850,  2024, "review bomb", ["Helldivers_2"]),
    ("Cities: Skylines II",      949230,  2023, "review bomb", ["Cities:_Skylines_II"]),
    ("Overwatch 2",              2357570, 2023, "review bomb", ["Overwatch_(2023_video_game)", "Overwatch_2"]),
    ("Total War: Warhammer III", 1142710, 2022, "review bomb", ["Total_War:_Warhammer_III"]),
    ("Apex Legends",             1172470, 2020, "review bomb", ["Apex_Legends"]),
    ("Battlefield 2042",         1517290, 2021, "review bomb", ["Battlefield_2042"]),
    # grupa kontrolna
    ("Baldur's Gate 3",          1086940, 2023, "kontrolna",   ["Baldur's_Gate_3"]),
    ("Elden Ring",               1245620, 2022, "kontrolna",   ["Elden_Ring"]),
    ("Cyberpunk 2077",           1091500, 2020, "kontrolna",   ["Cyberpunk_2077"]),
]

APPID = 553850
WIKI_ARTICLE = "Helldivers_2"
START = datetime(2024, 5, 3, tzinfo=timezone.utc)
END = datetime(2024, 5, 8, tzinfo=timezone.utc)


def get_json(url, retries=5):
    """GET z ponawianiem przy 429 (Steam i Wikimedia): czeka Retry-After albo coraz dluzej."""
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == retries:
                raise
            wait = int(e.headers.get("Retry-After") or 0) or 5 * 2 ** attempt
            print(f"  [429 - czekam {wait} s]")
            time.sleep(wait)


def steam_reviews(appid, start, end, max_pages=20):
    """Pobiera recenzje z zakresu dat (historia!) z paginacja kursorem."""
    cursor, out = "*", []
    for _ in range(max_pages):
        params = {
            "appid": appid,
            "filter": 1,                       # 1 = Recent (pozwala przejsc przez wszystko)
            "languages": ["all"],
            "purchase_type": 1,                # 1 = wszystkie zakupy
            "num_per_page": 100,
            "filter_offtopic_activity": False, # WAZNE: domyslnie Steam ukrywa review bomby!
            "date_range_start": int(start.timestamp()),
            "date_range_end": int(end.timestamp()),
            "cursor": cursor,
        }
        url = ("https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/?input_json="
               + urllib.parse.quote(json.dumps(params)))
        data = get_json(url)
        if "response" in data:
            data = data["response"]
        reviews = data.get("reviews", [])
        if not reviews:
            break
        out.extend(reviews)
        cursor = data.get("cursor")
        time.sleep(1.5)
    return out


def wiki_views(article, start, end):
    url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
           f"en.wikipedia/all-access/user/{urllib.parse.quote(article, safe='')}/daily/"
           f"{start:%Y%m%d}/{end:%Y%m%d}")
    return {i["timestamp"][:8]: i["views"] for i in get_json(url)["items"]}


def wiki_views_sum(articles, start, end):
    """Sumuje dzienne wyswietlenia kilku tytulow (artykul po zmianie nazwy)."""
    total = Counter()
    for article in articles:
        try:
            total.update(wiki_views(article, start, end))
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
    return dict(total)


def steam_count(appid, start, end, review_type):
    """Zwraca total_matching (liczbe recenzji) bez pobierania wszystkich stron.
    review_type: 1 = pozytywne, 2 = negatywne."""
    params = {
        "appid": appid, "filter": 1, "languages": ["all"], "purchase_type": 1,
        "num_per_page": 1, "filter_offtopic_activity": False,
        "review_type": review_type,
        "date_range_start": int(start.timestamp()), "date_range_end": int(end.timestamp()),
    }
    url = ("https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/?input_json="
           + urllib.parse.quote(json.dumps(params)))
    data = get_json(url)
    data = data.get("response", data)
    return data.get("total_matching")


def steam_total(appid):
    """Liczba wszystkich recenzji gry (bez zakresu dat)."""
    params = {"appid": appid, "filter": 1, "languages": ["all"], "purchase_type": 1,
              "num_per_page": 1, "filter_offtopic_activity": False}
    url = ("https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/?input_json="
           + urllib.parse.quote(json.dumps(params)))
    data = get_json(url)
    data = data.get("response", data)
    return data.get("total_matching") or 0


if __name__ == "__main__":
    from datetime import timedelta
    print("== LISTA GIER: recenzje na Steamie i wyswietlenia Wikipedii (ostatnie 30 dni) ==")
    w_end = datetime.now(timezone.utc) - timedelta(days=1)
    w_start = w_end - timedelta(days=29)
    total_reviews = 0
    print(f"  {'Gra':26} {'appid':>8} {'rok':>5} {'grupa':12} {'recenzje':>10} {'wiki/30 dni':>12}")
    for name, appid, year, group, articles in GAMES:
        n = steam_total(appid)
        views = sum(wiki_views_sum(articles, w_start, w_end).values())
        total_reviews += n
        print(f"  {name:26} {appid:>8} {year:>5} {group:12} {n:>10,} {views:>12,}")
        time.sleep(1.5)
    print(f"  {'RAZEM':26} {'':>8} {'':>5} {'':12} {total_reviews:>10,}\n")

    print("== STEAM: liczba recenzji dzien po dniu (z total_matching) ==")
    day = START
    while day < END:
        nxt = day + timedelta(days=1)
        pos = steam_count(APPID, day, nxt, 1)
        neg = steam_count(APPID, day, nxt, 2)
        tot = (pos or 0) + (neg or 0)
        share = f"{neg / tot:.0%}" if tot else "-"
        print(f"  {day:%Y-%m-%d}: pozytywne {pos}, negatywne {neg}, udzial negatywnych {share}")
        day = nxt
        time.sleep(1.5)

    print("\n== STEAM: probka 300 recenzji z 5 maja - ile zostalo pozniej edytowanych ==")
    d5 = datetime(2024, 5, 5, tzinfo=timezone.utc)
    revs = steam_reviews(APPID, d5, d5 + timedelta(days=1), max_pages=3)
    edited = [r for r in revs if r["timestamp_updated"] - r["timestamp_created"] > 86400]
    print(f"  pobrano {len(revs)}, edytowanych po >1 dniu: {len(edited)} "
          f"({len(edited) / max(len(revs), 1):.0%})")
    if edited:
        print(f"  z edytowanych teraz pozytywnych: {sum(r['voted_up'] for r in edited)}")

    print("\n== WIKIPEDIA ==")
    for d, v in sorted(wiki_views(WIKI_ARTICLE, START, END).items()):
        print(f"  {d}: {v} wyswietlen")
