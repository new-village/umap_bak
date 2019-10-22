import re
import responder

from datetime import datetime

from base.database import vault, conv_dict
from crawler.common import load_page, str_fmt, int_fmt, to_course_full, to_place_name

api = responder.API()


def display(_param):
    db = vault()
    rec = [conv_dict(db.races.find_one({"_id": _param}))]
    return rec


def collect(_param):
    # Get html
    base_url = "https://race.netkeiba.com/?pid=race_old&id=c{rid}"
    if re.match(r"^\d{12}$", _param):
        url = base_url.replace("{rid}", _param)
        page = load_page(url, ".race_table_old")
    else:
        return {"status": "ERROR", "message": "Invalid URL parameter: " + _param}

    # Parse race info
    if page is not None:
        race = parse_nk_race(page)
    else:
        return {"status": "ERROR", "message": "There is no page: " + url}

    if "_id" in race:
        db = vault()
        db.races.update({"_id": race["_id"]}, race, upsert=True)
    else:
        return {"status": "ERROR", "message": "There is no id in page: " + race}

    return {"status": "SUCCESS", "message": "Start holds collection process for " + _param}


def parse_nk_race(_page):
    """取得したレース出走情報のHTMLから辞書を作成
    netkeiba.comのレースページから情報をパースしてjson形式で返すファンクション
    """
    race = {}

    # RACE ID
    row = list(_page.find("ul.fc > li > a.active", first=True).links)[0]
    race["_id"] = str_fmt(row, r"\d+")
    # ROUND
    row = _page.find("dl.racedata > dt", first=True).text
    race["round"] = int_fmt(row, r"(\d{1,2})R")
    # TITLE
    row = _page.find("dl.racedata > dd > h1", first=True).text
    race["title"] = str_fmt(row, r"[^!-~\xa0]+")
    # GRADE
    row = _page.find("title", first=True).text
    race["grade"] = str_fmt(row, r"(G\d{1})")
    # TRACK
    row = _page.find("dl.racedata > dd > p", first=True).text
    abbr_track = str_fmt(row, r"芝|ダ|障")
    race["track"] = to_course_full(abbr_track)
    # DISTANCE
    row = _page.find("dl.racedata > dd > p", first=True).text
    race["distance"] = int_fmt(row, r"\d{4}")
    # WEATHER
    row = _page.find("dl.racedata > dd > p")[1].text
    race["weather"] = str_fmt(row, r"晴|曇|小雨|雨|小雪|雪")
    # GOING
    row = _page.find("dl.racedata > dd > p")[1].text
    race["going"] = str_fmt(row, r"良|稍重|重|不良")
    # RACE DATE
    row = _page.find("div.race_otherdata > p", first=True).text
    date = str_fmt(row, r"\d{4}/\d{2}/\d{2}")
    row = _page.find("dl.racedata > dd > p")[1].text
    time = str_fmt(row, r"\d{2}:\d{2}")
    race["date"] = datetime.strptime(date + " " + time, "%Y/%m/%d %H:%M")
    # PLACE NAME
    place_code = race["_id"][4:6]
    race["place"] = to_place_name(place_code)
    # HEAD COUNT
    count = _page.find("div.race_otherdata > p")[2].text
    race["count"] = int_fmt(count, r"[0-9]+")
    # MAX PRIZE
    prize = _page.find("div.race_otherdata > p")[3].text
    race["max_prize"] = int_fmt(prize, r"\d+")
    # ENTRY
    urls = [list(horse.links)[0] for horse in _page.find("td.horsename")]
    horses = [{"horse_id": str_fmt(url, r"\d+")} for url in urls]
    race["entry"] = horses

    return race
