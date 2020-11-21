from __future__ import unicode_literals

import os
from concurrent.futures import ThreadPoolExecutor, wait
from typing import List, Tuple

from pytube import YouTube
from youtube_search import YoutubeSearch

# requires:
#   youtube_search -    https://github.com/joetats/youtube_search
#   ffmpeg -            https://ffmpeg.org/
#   pytube -            https://github.com/nficano/pytube


def get_youtube_urls(video_name: str, max_results: int = 10) -> List[str]:
    # get {max_results} results from a youtube query of the video name
    results = YoutubeSearch(video_name, max_results=max_results)
    # convert the object to a list of dictionaries
    results = results.to_dict()
    # make sure there is at least one item in the list of dictionaries
    assert len(results) > 0
    # return the videos' urls
    return ["youtube.com" + d['url_suffix'] for d in results]


def download_youtube_song(url: str, path: str, song_name: str = '') -> None:
    if song_name != '':
        try:
            yt_obj = YouTube(url)

            yt_obj.streams.get_audio_only().download(output_path=path, filename=yt_obj.title)
            print(f'{song_name} downloaded successfully')
        except Exception as e:
            print(f'failed to download: {song_name} from playlist {path.split("/")[-1]}')
            print(e)


def handle_songs_file(filename: str) -> str:
    with open(filename, 'r') as f:
        songs_names = f.readlines()
    songs_names = [name.strip() for name in songs_names]
    songs_names = [name for name in songs_names if len(name) > 0]
    filename = filename[filename.rfind('/') + 1:-4]
    path = os.getcwd() + '/Downloaded/' + filename
    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except Exception as e:
            print(f"exception raised: {str(e)}")
    workers = []
    with ThreadPoolExecutor() as executor:
        for name in songs_names:
            # download it to mp3 from youtube
            try:
                url = get_youtube_urls(name, 1)[0]
                workers.append(executor.submit(download_youtube_song, url, path, name))
            except Exception as e:
                print(f"failed to download {name}")
        print(wait(workers))
    return f"Finished Handling File {filename}"


def main():
    files_names = [os.getcwd() + '/Lists/' + file for file in os.listdir(os.getcwd() + '/Lists') if
                   file.endswith('.txt')]
    workers = []
    with ThreadPoolExecutor() as executor:
        for file_name in files_names:
            workers.append(executor.submit(handle_songs_file, file_name))
            print(f"submited {file_name}")
        print(wait(workers))


if __name__ == "__main__":
    main()
