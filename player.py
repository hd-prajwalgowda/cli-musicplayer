import curses
import os
import time
from tinytag import TinyTag
import argparse
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

parser = argparse.ArgumentParser(description='Music Player Options')
parser.add_argument('DirPath', metavar='path', type=str, help='Path to music folder')
args = parser.parse_args()
musicDir = args.DirPath


def durationtomillisec(ms):
    h, r = divmod(ms, 3600000)
    m, r = divmod(r, 60000)
    s, _ = divmod(r, 1000)
    return ("%d:%02d:%02d" % (h, m, s)) if h else ("%d:%02d" % (m, s))


class Player(object):
    UP = -1
    DOWN = 1
    TITLE = " Music Player "
    SONGS = []
    PLAYLIST = list()
    SONGNO = 1

    def __init__(self, items):
        self.window = None
        self.width = 0
        self.height = 0

        self.init_curses()

        self.statusbar = curses.newwin(1, self.width, self.height - 1, 0)
        self.playerBar = curses.newwin(2, self.width, self.height - 3, 0)

        self.items = []
        self.SONGS = items

        for idx, song in enumerate(items):
            title = song['title']
            title = f'{idx + 1}. {title}'
            data = {
                'title': (title[:((self.width // 3) - 10)] + '...') if len(title) > ((self.width // 3) - 10) else title,
                'duration': durationtomillisec(song['duration']),
                'artist': song['artist']}
            self.items.append(data)

        self.max_lines = curses.LINES
        self.top = 0
        self.bottom = len(self.items)
        self.current = 0
        self.page = self.bottom // self.max_lines

    def init_curses(self):
        """Setup the curses"""
        self.window = curses.initscr()
        self.window.keypad(True)
        self.window.idcok(False)
        self.window.idlok(False)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        self.height, self.width = self.window.getmaxyx()

    def run(self):
        """Continue running the TUI until get interrupted"""
        try:
            self.input_stream()
        except KeyboardInterrupt:
            pass
        finally:
            curses.endwin()

    def input_stream(self):
        """Waiting an input and run a proper method according to type of input"""
        while True:
            self.height, self.width = self.window.getmaxyx()
            self.max_lines = self.height - 6
            self.page = self.bottom // self.max_lines

            self.display()

            ch = self.window.getch()
            if (ch == curses.KEY_UP) and self.top >= 0:
                time.sleep(0.05)
                self.scroll(self.UP)
            elif (ch == curses.KEY_DOWN) and self.current <= self.max_lines:
                time.sleep(0.05)
                self.scroll(self.DOWN)
            elif ch == curses.KEY_LEFT:
                time.sleep(0.05)
                self.paging(self.UP)
            elif ch == curses.KEY_RIGHT:
                time.sleep(0.05)
                self.paging(self.DOWN)
            elif ch == curses.KEY_RESIZE:
                time.sleep(0.05)
                self.items = []
                for idx, song in enumerate(self.SONGS):
                    title = song['title']
                    title = f'{idx + 1}. {title}'
                    data = {
                        'title': (title[:((self.width // 3) - 10)] + '...') if len(title) > (
                                    (self.width // 3) - 10) else title,
                        'duration': durationtomillisec(song['duration']),
                        'artist': song['artist']}
                    self.items.append(data)
            elif ch == ord(':'):
                curses.echo()
                curses.curs_set(1)
                self.statusbar.refresh()
                self.SONGNO = self.statusbar.getstr(0,20)
                curses.curs_set(0)
                curses.noecho()
            elif ch == ord(' '):
                # Have play pause function
                pass
            elif ch == ord('p'):
                # Previous song function
                pass
            elif ch == ord('n'):
                # Next song function
                pass
            elif ch == ord('+'):
                # Volume inc function
                pass
            elif ch == ord('-'):
                # Volume dec function
                pass
            elif ch == ord('f'):
                # Song forward function
                pass
            elif ch == ord('r'):
                # Song rewind function
                pass
            elif ch == ord('q'):
                break

    def scroll(self, direction):
        """Scrolling the window when pressing up/down arrow keys"""
        next_line = self.current + direction

        if (direction == self.UP) and (self.top > 0 and self.current == 0):
            self.top += direction
            return
        if (direction == self.DOWN) and (next_line == self.max_lines) and (self.top + self.max_lines < self.bottom):
            self.top += direction
            return
        if (direction == self.UP) and (self.top > 0 or self.current > 0):
            self.current = next_line
            return
        if (direction == self.DOWN) and (next_line < self.max_lines) and (self.top + next_line < self.bottom):
            self.current = next_line
            return

    def paging(self, direction):
        current_page = (self.top + self.current) // self.max_lines
        next_page = current_page + direction
        if next_page == self.page:
            self.current = min(self.current, self.bottom % self.max_lines - 1)

        if (direction == self.UP) and (current_page > 0):
            self.top = max(0, self.top - self.max_lines)
            return
        if (direction == self.DOWN) and (current_page < self.page):
            self.top += self.max_lines
            return

    def display(self):
        self.window.erase()
        songsListView = curses.newwin(self.height - 3, self.width, 0, 0)
        songsListView.resize(self.height - 3, self.width)
        songsListView.box()
        songsListView.addstr(0, self.width // 2 - len(self.TITLE) // 2, self.TITLE)
        topBar = 'Title' + ' ' * (self.width // 3 - 1) + 'Artist' + ' ' * (self.width // 6 - 2) + 'Duration'
        songsListView.attron(curses.color_pair(3))
        songsListView.addstr(1, 1, topBar)
        songsListView.addstr(1, len(topBar) + 1, " " * (self.width - len(topBar) - 2))
        songsListView.attroff(curses.color_pair(3))

        for idx, item in enumerate(self.items[self.top:self.top + self.max_lines]):
            row = item["title"] + ' ' * (self.width // 3 - len(item['title']) - 3) + "   |   " + \
                  item["artist"] + ' ' * (self.width // 6 - len(item['artist']) - 3) + "   |   " + \
                  f'{item["duration"]}'
            if idx == self.current:
                songsListView.addstr(idx + 2, 1, row + " " * (self.width - len(row) - 2), curses.color_pair(2))
            else:
                songsListView.addstr(idx + 2, 1, row + " " * (self.width - len(row) - 2), curses.color_pair(1))

        self.playerBar.mvwin(self.height - 3, 0)

        self.playerBar.addstr(0, 1, '0:00')
        self.playerBar.addstr(1, 1, '0:00')

        self.statusbar.mvwin(self.height - 1, 0)
        statusbarText = f'q to exit:{self.SONGNO}'
        self.statusbar.attron(curses.color_pair(3))
        self.statusbar.addstr(0, 0, f'{statusbarText}' + " " * (self.width - len(statusbarText) - 1))
        self.statusbar.attroff(curses.color_pair(3))

        self.window.refresh()
        songsListView.refresh()
        self.playerBar.refresh()
        self.statusbar.refresh()

    def makePlaylist(self):
        pass

def main():
    items = []
    musicList = os.listdir(musicDir)
    for idx, song in enumerate(musicList):
        if song.endswith('.mp3'):
            tag = TinyTag.get(os.path.join(musicDir, song))
            songDict = {'title': song, 'duration': (int)(tag.duration) * 1000, 'artist': tag.artist}
            items.append(songDict)
    player = Player(items)
    player.run()


if __name__ == '__main__':
    main()
