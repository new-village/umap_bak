import traceback
import json


def respJson(resp, msg):
    try:
        resp.headers = {"Content-Type": "application/json; charset=utf-8"}
        resp.content = json.dumps(msg, ensure_ascii=False)
    except Exception:
        traceback.print_exc()
        resp.media = {"errmessage": "Error occured"}

    return resp
