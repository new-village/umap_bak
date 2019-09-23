import responder

api = responder.API()


@api.route('/{word}')
class Hello:
    def on_get(self, req, resp, word):
        resp.content = api.template("index.html", word=word)


if __name__ == '__main__':
    api.run()
