from core.api import *


def main():
    helper = MusicHelper()
    app = ConsoleApp()

    app.start(helper)
