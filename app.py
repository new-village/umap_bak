import responder
import traceback
from umap import netkeiba

api = responder.API()


@api.route('/')
class ViewIndex:
    def on_get(self, req, resp):
        resp.content = api.template("index.html")


@api.route('/api/race/{race_id}')
class GetData:
    def on_get(self, req, resp, race_id):
        try:
            resp.headers = {"Content-Type": "application/json; charset=utf-8"}
            resp.content = netkeiba.main(race_id)
        except Exception:
            traceback.print_exc()
            resp.media = {"errmessage": "Error occured"}


if __name__ == '__main__':
    api.run()
