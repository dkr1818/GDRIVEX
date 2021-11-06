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
  try:
    #dl = SmartDL(url, dl_path, progress_bar=False)
    dl = SmartDL(url, dl_path, progress_bar=True)
    LOGGER.info(f'Downloading: {url} in {dl_path}')
    dl.start()
    dl.get_dest()
    return True, dl_path
  except HTTPError as error:
    return False, error
  except Exception as error:
    if '[400 MESSAGE_NOT_MODIFIED]' in error:
      return True, dl_path
    else:
      sw1 = "bbb"
  
  if sw1 == "bbb":
    try:
      filename = wget.download(url, dl_path)
      #return True, os.path.join(f"{DOWNLOAD_DIRECTORY}/{filename}")
      return True, dl_path
    except HTTPError as err2:
      return False, err2
    except Exception as err2:
      if '[400 MESSAGE_NOT_MODIFIED]' in err2:
        return True, dl_path
      else:
        return False, err2


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
