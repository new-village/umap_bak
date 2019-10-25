import responder
from datetime import datetime, timedelta
from base import common, task
from crawler import sportsnavi, race

api = responder.API()


@api.route('/')
class ViewIndex:
    def on_get(self, req, resp):
        resp.content = api.template("index.html")


@api.route('/api/races')
class RaceListData:
    def on_get(self, req, resp):
        # Return Next Day Races
        msg = race.recent()
        common.respJson(resp, msg)

    def on_post(self, req, resp):
        # Collect This Month Races
        now = datetime.now() + timedelta(week=1)
        msg = race.bulk_collect(now.strftime('%Y'), now.strftime('%m'))
        common.respJson(resp, msg)


@api.route('/api/races/{rid}')
class RaceDetailData:
    def on_get(self, req, resp, rid):
        # Return Race ID's Race
        msg = race.detail(rid)
        common.respJson(resp, msg)

    def on_post(self, req, resp, rid):
        # Collect Race ID's Race
        msg = race.collect(rid)
        common.respJson(resp, msg)


@api.route('/task')
class ViewTask:
    def on_get(self, req, resp):
        resp.content = api.template("task.html")


@api.route('/crawler/race/bulk/{year}')
class HoldsDataByYear:
    def on_get(self, req, resp, year):
        msg = sportsnavi.collect_holds(year)
        common.respJson(resp, msg)

    def on_post(self, req, resp, year):
        msg = sportsnavi.collect_holds(year)
        common.respJson(resp, msg)


@api.route('/crawler/hold/{year}/{month}')
class HoldsDataByMonth:
    def on_get(self, req, resp, year, month):
        msg = sportsnavi.collect_holds(year + month)
        common.respJson(resp, msg)

    def on_post(self, req, resp, year, month):
        msg = sportsnavi.collect_holds(year + month)
        common.respJson(resp, msg)


@api.route('/task/recent')
class GetRecentTask:
    def on_get(self, req, resp):
        msg = task.find_recent()
        common.respJson(resp, msg)


if __name__ == '__main__':
    api.run()
