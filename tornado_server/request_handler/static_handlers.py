from tornado.web import StaticFileHandler


class JsStaticFileHandler(StaticFileHandler):
    def get_content_type(self):
        return "text/javascript"


class CssStaticFileHandler(StaticFileHandler):
    def get_content_type(self):
        return "text/css"
