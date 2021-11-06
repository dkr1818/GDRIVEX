import os
import time
import asyncio
from pyrogram import Client, filters
from bot.helpers.sql_helper import gDriveDB, idsDB
from bot.helpers.utils import CustomFilters, humanbytes
from bot.helpers.downloader import download_file2, utube_dl
from bot.helpers.download_from_url import download_file, get_size
from bot.helpers.gdrive_utils import GoogleDrive
from bot.helpers.mega_dl import megadl
from bot import DOWNLOAD_DIRECTORY, LOGGER
from bot.config import Messages, BotCommands
from pyrogram.errors import FloodWait, RPCError
from bot.helpers.display_progress import progress_for_pyrogram

@Client.on_message(filters.private & filters.incoming & filters.text & (filters.command(BotCommands.Download) | filters.regex('^(ht|f)tp*')) & CustomFilters.auth_users)
async def _download(client, message):
  file_path = ""
  sw = "aaa"
  user_id = message.from_user.id
  if not message.media:
    sent_message = await message.reply_text('🕵️**Checking link...**', quote=True)
    if message.command:
      link = message.command[1]
    else:
      link = message.text
    if 'drive.google.com' in link:
      await sent_message.edit(Messages.CLONING.format(link))
      LOGGER.info(f'Copy:{user_id}: {link}')
      msg = GoogleDrive(user_id).clone(link)
      await sent_message.edit(msg)
    elif 'mega.nz' in link:
      LOGGER.info(f'ID:{user_id} URL: {link}')
      file_path = await megadl(client, message, sent_message)
      if file_path == "error":
        await sent_message.edit(f"Error Occurred !\n\nTry Again Later.")
        LOGGER.info(f'MegaDL Failed !')
        return
      LOGGER.info(f'SUCCESSFULLY DOWNLOADED . URL: {link} DST_Folder: {file_path}')
      await sent_message.edit(Messages.DOWNLOADED_SUCCESSFULLY.format(os.path.basename(file_path), humanbytes(os.path.getsize(file_path))))
      
      msg = GoogleDrive(user_id).upload_file(file_path)
      #await sent_message.edit(msg)
      #await asyncio.sleep(2)
      if 'rateLimitExceeded' in msg:
        LOGGER.info(f'msg : {msg}')
        await sent_message.edit(f"{msg}\n\n trying again in 5 sec")
        await asyncio.sleep(5)
        await sent_message.edit(f"`uploading 2nd ...`")
        msg = GoogleDrive(user_id).upload_file(file_path)
        await sent_message.edit(msg)
        if 'rateLimitExceeded' in msg:
          LOGGER.info(f'msg : {msg}')
          await sent_message.edit(f"{msg}\n\n trying again in 5 sec")
          await asyncio.sleep(5)
          await sent_message.edit(f"`uploading 3rd ...`")
          msg = GoogleDrive(user_id).upload_file(file_path)
        else:
          LOGGER.info(f'SUCCESSFULLY UPLOADED TO GDRIVE.')
      else:
        LOGGER.info(f'SUCCESSFULLY UPLOADED TO GDRIVE.')
      
      await sent_message.edit(msg)
      LOGGER.info(f'Deleteing: {file_path}')
      try:
        os.remove(file_path)
      except:
        pass
    else:
      if '|' in link:
        link, filename = link.split('|')
        link = link.strip()
        filename = filename.strip()
        dl_path = os.path.join(f'{DOWNLOAD_DIRECTORY}{filename}')
      else:
        link = link.strip()
        filename = os.path.basename(link)
        dl_path = os.path.join(DOWNLOAD_DIRECTORY, os.path.basename(link))

        #LOGGER.info(f'ID:{user_id} URL: {link} Filename: {filename} DL_PATH: {dl_path}')
        await sent_message.edit(Messages.DOWNLOADING.format(link))
      
        #time.sleep(1)
        result, file_path = download_file2(link, dl_path)
        if result == True:
          #await sent_message.edit(Messages.DOWNLOADED_SUCCESSFULLY.format(os.path.basename(file_path), humanbytes(os.path.getsize(file_path))))
          fn = os.path.basename(file_path)
          sz = humanbytes(os.path.getsize(file_path))
          await sent_message.edit(f"`uploading 1st ...`\n\n{fn} [{sz}]")
          #sw = "ccc"
        else:
          await sent_message.edit(Messages.DOWNLOAD_ERROR.format(file_path, link))
          await asyncio.sleep(3)
          sw = "bbb"

        if sw == "bbb":
          await sent_message.edit(f"Trying to Download with Second Method !\n\n`{link}`")
          start = time.time()
          try:
            file_path = await download_file(link, dl_path, sent_message, start, client)
            fn = os.path.basename(file_path)
            sz = humanbytes(os.path.getsize(file_path))
            await sent_message.edit(f"`uploading 1st ...`\n\n{fn} [{sz}]")
            #await sent_message.edit(Messages.DOWNLOADED_SUCCESSFULLY.format(os.path.basename(file_path), humanbytes(os.path.getsize(file_path))))
          except Exception as e:
            print(e)
            LOGGER.info(f'Error:{e}')
            await sent_message.edit(f"Second Method Failed :\n\n{e}")
            try:
              os.remove(file_path)
            except:
              pass
            return

        msg = GoogleDrive(user_id).upload_file(file_path)
        if 'rateLimitExceeded' in msg:
          await sent_message.edit(f"{msg}\n\n trying again in 5 sec")
          await asyncio.sleep(5)
          await sent_message.edit(f"`uploading 2nd ...`")
          msg = GoogleDrive(user_id).upload_file(file_path)
          if 'rateLimitExceeded' in msg:
            await sent_message.edit(f"{msg}\n\n trying again in 5 sec")
            await asyncio.sleep(5)
            await sent_message.edit(f"`uploading 3rd ...`")
            msg = GoogleDrive(user_id).upload_file(file_path)
        await sent_message.edit(msg)
        LOGGER.info(f'Deleteing: {file_path}')
        try:
          os.remove(file_path)
        except:
          pass 
                
@Client.on_message(filters.private & filters.incoming & (filters.document | filters.audio | filters.video | filters.photo) & CustomFilters.auth_users)
def _telegram_file(client, message):
  user_id = message.from_user.id
  sent_message = message.reply_text('🕵️**Checking File...**', quote=True)
  if message.document:
    file = message.document
  elif message.video:
    file = message.video
  elif message.audio:
    file = message.audio
  elif message.photo:
  	file = message.photo
  	file.mime_type = "images/png"
  	file.file_name = f"IMG-{user_id}-{message.message_id}.png"
  sent_message.edit(Messages.DOWNLOAD_TG_FILE.format(file.file_name, humanbytes(file.file_size), file.mime_type))
  LOGGER.info(f'Download:{user_id}: {file.file_id}')
  c_time = time.time()
  file_path = message.download(
    file_name=DOWNLOAD_DIRECTORY,
    progress=progress_for_pyrogram,
    progress_args=(
      "Downloading Status ...",
      sent_message,
      c_time
    )
  )
  sent_message.edit(Messages.DOWNLOADED_SUCCESSFULLY.format(os.path.basename(file_path), humanbytes(os.path.getsize(file_path))))
  msg = GoogleDrive(user_id).upload_file(file_path, file.mime_type)
  if 'rateLimitExceeded' in msg:
    sent_message.edit(f"{msg}\n\n trying again in 5 sec")
    time.sleep(5)
    sent_message.edit(f"`uploading 2nd ...`")
    msg = GoogleDrive(user_id).upload_file(file_path, file.mime_type)
    if 'rateLimitExceeded' in msg:
      sent_message.edit(f"{msg}\n\n trying again in 5 sec")
      time.sleep(5)
      sent_message.edit(f"`uploading 3rd ...`")
      msg = GoogleDrive(user_id).upload_file(file_path, file.mime_type)
  sent_message.edit(msg)
  LOGGER.info(f'Deleteing: {file_path}')
  try:
    os.remove(file_path)
  except:
    pass

@Client.on_message(filters.incoming & filters.private & filters.command(BotCommands.YtDl) & CustomFilters.auth_users)
def _ytdl(client, message):
  user_id = message.from_user.id
  if len(message.command) > 1:
    sent_message = message.reply_text('🕵️**Checking Link...**', quote=True)
    link = message.command[1]
    LOGGER.info(f'YTDL:{user_id}: {link}')
    sent_message.edit(Messages.DOWNLOADING.format(link))
    result, file_path = utube_dl(link)
    if result:
      sent_message.edit(Messages.DOWNLOADED_SUCCESSFULLY.format(os.path.basename(file_path), humanbytes(os.path.getsize(file_path))))
      msg = GoogleDrive(user_id).upload_file(file_path)
      if 'rateLimitExceeded' in msg:
        sent_message.edit(f"{msg}\n\n trying again in 5 sec")
        time.sleep(5)
        sent_message.edit(f"`uploading 2nd ...`")
        msg = GoogleDrive(user_id).upload_file(file_path)
        if 'rateLimitExceeded' in msg:
          sent_message.edit(f"{msg}\n\n trying again in 5 sec")
          time.sleep(5)
          sent_message.edit(f"`uploading 3rd ...`")
          msg = GoogleDrive(user_id).upload_file(file_path)
      sent_message.edit(msg)
      LOGGER.info(f'Deleteing: {file_path}')
      try:
        os.remove(file_path)
      except:
        pass
    else:
      sent_message.edit(Messages.DOWNLOAD_ERROR.format(file_path, link))
  else:
    message.reply_text(Messages.PROVIDE_YTDL_LINK, quote=True)
