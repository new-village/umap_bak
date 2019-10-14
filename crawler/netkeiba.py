import responder
import re
# from crawler.common import load_page

api = responder.API()


def collect_races(target):
    # Create Netkeiba URL from the argument
    urls = create_url_list(target)

    # Load URL Pages
    if len(urls) != 0:
        # pages = load_page(urls)
        print("TODO")
    else:
        return {"status": "ERROR", "message": "Invalid URL parameters: " + target}

    # Parse and Insert Elements
    # TODO: ページのパーサー部分
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
