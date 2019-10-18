import responder
from base import common
from crawler import sportsnavi, netkeiba

api = responder.API()


@api.route('/')
class ViewIndex:
    def on_get(self, req, resp):
        resp.content = api.template("index.html")


@api.route('/crawler/hold/{year_month}')
class GetHoldData:
    def on_get(self, req, resp, year_month):
        sportsnavi.collect_holds(year_month)
        msg = {"message": "Start process"}
        common.respJson(resp, msg)


@api.route('/crawler/race/{rid_hid}')
class GetRaceData:
    def on_get(self, req, resp, rid_hid):
        netkeiba.collect_races(rid_hid)
        msg = {"message": "Start process"}
        common.respJson(resp, msg)


if __name__ == '__main__':
    api.run()
