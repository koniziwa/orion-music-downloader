from .helper import MusicHelper


class ConsoleApp:
    __links = []

    # TODO: Get links from .txt file and add them to list
    def __getLinks(self):
        try:
            with open('././done/links.txt', 'r') as file:
                for line in file.readlines():
                    if line.startswith('https://'):
                        self.__links.append(line)
        except Exception as e:
            print('ERROR!', e)

    # TODO: Start console application
    def start(self, helper: MusicHelper):
        self.__getLinks()
        helper.downloadMusic(self.__links)
        print('PRESS ANY KEY TO CLOSE THIS WINDOW:')
        input()
