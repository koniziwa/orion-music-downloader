# Modules
from bs4 import BeautifulSoup
import yt_dlp
import requests
import os
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

# Files
from .constants import WEB_DATABASE_URL


class MusicHelper:
    # TODO: Get title of type 'AUTHOR - TITLE (...)'
    def __getCorrectTitle(self, title: str, author: str):
        if ' - ' in title:
            author = title.split(' - ')[0]
            newTitle = title.split(' - ')[1]
            return f"{author} - {newTitle}"
        else:
            return f"{author} - {title}"

    # TODO: Download music from YouTube
    def downloadMusic(self, links):
        for url in links:
            try:
                video_page = requests.get(url)
                video_page_soup = BeautifulSoup(video_page.text, 'html.parser')

                title = video_page_soup.find(
                    "meta", itemprop="name")['content']
                author = video_page_soup.find(
                    "span", itemprop="author").next.next['content']

                file_name = self.__getCorrectTitle(title, author)

                ydl_opts = {
                    'format': 'm4a/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                    }],
                    'outtmpl': f'././done/songs/{file_name}',
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                print(f'The "{file_name}.mp3" is downloaded!')

                self.__setInfo(file_name)
            except Exception as e:
                print('ERROR! The audio ({url}) was not downloaded!')

    # TODO: Get audio's tags from database
    def __parseInfo(self, title: str):
        search_url = f"{WEB_DATABASE_URL}/search?query={title.replace(' ', '+')}&type=recording&method=indexed"

        search_page = requests.get(search_url)
        search_page_soup = BeautifulSoup(search_page.text, 'html.parser')

        song_page = requests.get(
            WEB_DATABASE_URL + search_page_soup.td.a['href'])
        song_page_soup = BeautifulSoup(song_page.text, 'html.parser')

        tags_info = song_page_soup.select('tr.odd td')

        album_page = requests.get(
            WEB_DATABASE_URL + tags_info[4].a['href'])
        album_page_soup = BeautifulSoup(album_page.text, 'html.parser')

        album_url = f"https:{album_page_soup.select('div.cover-art img')[0]['src']}".replace(
            'thumb250', 'thumb500')

        return tags_info[1].bdi.text, tags_info[3].text, tags_info[4].bdi.text, tags_info[5].text, album_url

    # Setting the cover and the following tags: title, artist, album, albumartist
    def __setInfo(self, filename: str):
        path = f'././done/songs/{filename}.mp3'
        title, artist, album, album_artist, album_url = self.__parseInfo(
            filename)

        try:
            audio = MP3(path, ID3=EasyID3)

            audio['title'] = [title]
            audio['artist'] = [artist]
            audio['album'] = [album]
            audio['albumartist'] = [album_artist]

            audio.save()

            # Set album cover
            audio = ID3(path)

            if not os.path.exists('././done/covers'):
                os.makedirs('././done/covers')

            if not os.path.exists(f'././done/covers/{album}.jpg'):
                img_data = requests.get(album_url).content
                with open(f'././done/covers/{album}.jpg', 'wb') as handler:
                    handler.write(img_data)

            with open(f'././done/covers/{album}.jpg', 'rb') as albumart:
                audio['APIC'] = APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3, desc=u'Cover',
                    data=albumart.read()
                )

            audio.save()

            print(f'Successfully downloaded file ({filename}.mp3)')
        except Exception as e:
            print("ERROR!", str(e))
