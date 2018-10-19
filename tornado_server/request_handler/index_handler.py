from tornado_server.request_handler.base_handlers import BaseRequestHandler


class IndexHandler(BaseRequestHandler):
    """
    Handles the default request on the server.
    - it will load the main view on the client
    """
    def get(self):
        self.render("{}/{}".format(self._web_path, "index.html"), title="DiViCo mobile view")
