import re
import responder
import datetime
from base.database import vault
from crawler.common import load_page, str_fmt, int_fmt, to_course_full, to_place_name

api = responder.API()


@api.background.task
def collect_races(target):
    # Create Netkeiba URL from the argument
    urls = create_url_list(target)

    # Load URL Pages
    if len(urls) != 0:
        all_pages = load_page(urls)
        pages = [page for page in all_pages if len(page.find(".race_table_old")) != 0]
    else:
        return {"status": "ERROR", "message": "Invalid URL parameters: " + target}

    # Parse and Insert Elements
    if len(pages) != 0:
        db = vault()
        for page in pages:
            race = parse_nk_race(page)
            db.races.update({"_id": race["_id"]}, race, upsert=True)
    else:
        return {"status": "ERROR", "message": "There is no page or element"}
    return urls


def create_url_list(_id):
    urls = []
    base_url = "https://race.netkeiba.com/?pid=race_old&id=c{rid}"

    # Case of Year and Month (YYYYMM)
    if re.match(r"^\d{12}$", _id):
        url = base_url.replace("{rid}", _id)
        urls.append(url)
    # Case of Year only
    elif re.match(r"^\d{10}$", _id):
        for i in range(12):
            rid = _id + str(i + 1).zfill(2)
            urls.append(base_url.replace("{rid}", rid))

    return urls


def parse_nk_race(_page):
    """取得したレース出走情報のHTMLから辞書を作成
    netkeiba.comのレースページから情報をパースしてjson形式で返すファンクション
    """
    race = {}

    race["_id"] = str_fmt(_page.find("ul.fc > li > a.active", first=True).html, r"\d+")
    race["round"] = int(race["_id"][10:12])
    race["title"] = str_fmt(_page.find("dl.racedata > dd > h1", first=True).text, r"[^!-~\xa0]+")
    race["grade"] = str_fmt(_page.find("title", first=True).text, r"(G\d{1})")
    abbr_course = str_fmt(_page.find("dl.racedata > dd > p", first=True).text, r"芝|ダ|障")
    race["course"] = to_course_full(abbr_course)
    race["distance"] = int_fmt(_page.find("dl.racedata > dd > p", first=True).text, r"\d{4}")
    race["weather"] = str_fmt(_page.find("dl.racedata > dd > p")[1].text, r"晴|曇|小雨|雨|小雪|雪")
    race["going"] = str_fmt(_page.find("dl.racedata > dd > p")[1].text, r"良|稍重|重|不良")
    race_date = str_fmt(_page.find("div.race_otherdata > p", first=True).text, r"\d{4}/\d{2}/\d{2}")
    race_time = str_fmt(_page.find("dl.racedata > dd > p")[1].text, r"\d{2}:\d{2}")
    race["race_date"] = datetime.datetime.strptime(race_date + " " + race_time, "%Y/%m/%d %H:%M")
    race["place_id"] = race["_id"][4:6]
    race["place_name"] = to_place_name(race["place_id"])
    race["count"] = int_fmt(_page.find("div.race_otherdata > p")[2].text, r"\d+")
    race["max_prize"] = int_fmt(_page.find("div.race_otherdata > p")[3].text, r"\d+")
    race["entry"] = [str_fmt(list(h.links)[0], r"\d+") for h in _page.find("td.horsename")]

    return race
