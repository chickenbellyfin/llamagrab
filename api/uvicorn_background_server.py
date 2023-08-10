import uvicorn
from threading import Thread

class UvicornBackgroundServer(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    def run_nonblocking(self):
        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()

    def kill(self):
        self.should_exit = True
        self.thread.join()
