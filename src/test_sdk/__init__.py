from .wit.exports import Run


class RunHandler(Run):
    def run(self) -> None:
        self.handle()

    def handle(self):
        pass
