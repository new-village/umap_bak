import responder
import re
import datetime
import time

from base.database import vault
from base.task import start_log, update_log, warning_log, end_log
from crawler.common import str_fmt, to_place_name, load_page

api = responder.API()


def collect_holds(_param):
    # Parse url parameter
    urls = create_url_list(_param)
    if len(urls) == 0:
        return {"status": "ERROR", "message": "Invalid URL parameter: " + _param}

    # Collect and insert records
    job_manager(urls)
    return {"status": "SUCCESS", "message": "Start holds collection process for " + _param}


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


@api.background.task
def job_manager(_urls):
    # Put log
    task_id = start_log(len(_urls))

    for url in _urls:
        # Collect target page html
        page = load_page(url, ".layoutCol2M")
        if page is None:
            warning_log(task_id, "There is no page: " + url)
        else:
            # Parse & Insert page elements
            db = vault()
            for hold in parse_sportsnavi(page):
                if "_id" in hold:
                    db.holds.update({"_id": hold["_id"]}, hold, upsert=True)
                else:
                    warning_log(task_id, "There is no _id in page: " + hold)
            update_log(task_id)

        time.sleep(5)
    end_log(task_id)


def parse_sportsnavi(page):
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
            id_list = [hold["_id"] + str(i + 1).zfill(2) for i in range(12)]
            hold["races"] = id_list
            holds.append(hold)

    return holds
