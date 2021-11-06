import os
import wget
import glob
import youtube_dl
from pySmartDL import SmartDL
from urllib.error import HTTPError
from youtube_dl import DownloadError
from bot import DOWNLOAD_DIRECTORY, LOGGER


def download_file2(url, dl_path):
  
  sw1 = "aaa"
  dl = SmartDL(url, dl_path, progress_bar=False)
  LOGGER.info(f'Downloading: {url} in {dl_path}')
  dl.start()
  dl.get_dest()
  sz = os.path.getsize(dl_path)
  if sz:
    return True, dl_path
  else:
    sw1 = "bbb"
  
  if sw1 == "bbb":
    wget.download(url, dl_path)
    sz = os.path.getsize(dl_path)
    if sz:
      return True, dl_path
    else:
      return False, "Erorr"

def utube_dl(link):
  ytdl_opts = {
    'outtmpl' : os.path.join(DOWNLOAD_DIRECTORY, '%(title)s'),
    'noplaylist' : True,
    'logger': LOGGER,
    'format': 'bestvideo+bestaudio/best',
    'geo_bypass_country': 'IN'
  }
  with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
    try:
      meta = ytdl.extract_info(link, download=True)
    except DownloadError as e:
      return False, str(e)
    for path in glob.glob(os.path.join(DOWNLOAD_DIRECTORY, '*')):
      if path.endswith(('.avi', '.mov', '.flv', '.wmv', '.3gp','.mpeg', '.webm', '.mp4', '.mkv')) and \
          path.startswith(ytdl.prepare_filename(meta)):
        return True, path
    return False, 'Something went wrong! No video file exists on server.'
