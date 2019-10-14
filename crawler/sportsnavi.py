import responder
import re
import datetime

from crawler.common import str_fmt, to_place_name, load_page
from base.database import vault

api = responder.API()


@api.background.task
def collect_holds(target):
    # Create Yahoo keiba URL from the argument
    urls = create_url_list(target)

    # Load URL Pages
    if len(urls) != 0:
        pages = load_page(urls, ".layoutCol2M")
    else:
        return {"status": "ERROR", "message": "Invalid URL parameters: " + target}

    # Parse and Insert Elements

    if len(pages) != 0:
        db = vault()
        for page in pages:
            holds = parse_sportsnave(page)
            for hold in holds:
                db.holds.update({"_id": hold["_id"]}, hold, upsert=True)
    else:
        return {"status": "ERROR", "message": "There is no page or element"}


def create_url_list(yrmo):
    urls = []
    base_url = "https://keiba.yahoo.co.jp/schedule/list/{yr}/?month={mo}"

    # Case of Year and Month (YYYYMM)
    if re.match(r"^\d{6}$", yrmo):
        url = base_url.replace("{yr}", yrmo[0:4]).replace("{mo}", yrmo[4:6])
        urls.append(url)
    # Case of Year only
    elif re.match(r"^\d{4}$", yrmo):
        url = base_url.replace("{yr}", yrmo)
        for i in range(12):
            urls.append(url.replace("{mo}", str(i + 1).zfill(2)))

    return urls


def parse_sportsnave(page):
    """取得したレース・カレンダーのHTMLから辞書を作成
    Yahoo!競馬の日程・結果ページから情報をパースしてdict形式で返すファンクション
    """
    yrmo = page.find(".midashi3rd", first=True).text
    yr, mo = re.search(r"(\d{4})年(\d{1,2})月", yrmo).groups()
    holds = []

    for row in page.find("tr"):
        cells = row.find("td")
        if len(cells) == 3 and len(cells[0].links) != 0:
            hold = {}
            dy = str_fmt(cells[0].text, r"(\d+)日（[日|月|火|水|木|金|土]）").zfill(2)
            hold["_id"] = "20" + str_fmt(list(cells[0].links)[0], r"\d+")
            hold["hold_date"] = datetime.datetime(int(yr), int(mo), int(dy))
            hold["place_id"] = hold["_id"][4:6]
            hold["place_name"] = to_place_name(hold["place_id"])
            hold["days"] = int(hold["_id"][6:8])
            hold["times"] = int(hold["_id"][8:10])
            id_list = [{"race_id": hold["_id"] + str(i + 1).zfill(2)} for i in range(12)]
            hold["races"] = id_list
            holds.append(hold)

    return holds
