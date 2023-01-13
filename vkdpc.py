#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys
import requests
from picoVkApi import VkApi
from PIL import Image, ImageDraw, ImageFont

COVER_WIDTH  = 1920
COVER_HEIGHT = 768
COVER_SIZE   = (COVER_WIDTH, COVER_HEIGHT)

BACK_COLOR = (0, 0, 0)
TEXT_COLOR = (192, 192, 192)

FONT_FILE  = "clacon2.ttf"
TEXT_START = (200, 170)

def genCoverText(api):
  curr_time = time.strftime("%H:%M", time.localtime())

  f = open("script.txt", "r")
  code = f.read()
  f.close()

  params = { "code": code }
  resp = api.method("execute", params)

  unread       = resp["unread"]
  blocked      = resp["blocked"]
  friends      = resp["friends"]
  friends_req  = resp["friends_req"]
  first_name   = resp["first_name"]
  last_name    = resp["last_name"]
  screen_name  = resp["screen_name"]
  online       = resp["isOnline"]

  if online:
    last_seen = "Онлайн"
  else:
    last_seen_ts = resp["last_seen_ts"]
    last_seen_time = time.strftime("%d.%m.%Y %H:%M", time.localtime(last_seen_ts))
    last_seen = "Был в сети: {}".format(last_seen_time)

  f = open("template.txt", "r")
  template = f.read()
  f.close()

  text = template.format(
    time        = curr_time,
    unread      = unread,
    blocked     = blocked,
    friends     = friends,
    friends_req = friends_req,
    first_name  = first_name,
    last_name   = last_name,
    screen_name = screen_name,
    last_seen   = last_seen
  )

  print(text)
  return text

def uploadCover(api, imageFile):
  # Get image upload server URL
  params = {
    "crop_height": COVER_HEIGHT,
    "crop_width":  COVER_WIDTH
  }
  resp = api.method("photos.getOwnerCoverPhotoUploadServer", params)
  upload_url = resp["upload_url"]
  print(resp)

  # Upload image to server
  files = { "file": open(imageFile, "rb") }
  resp = requests.post(upload_url, files=files)
  upload_result = resp.json()
  print(upload_result)

  hash = upload_result["hash"]
  photo = upload_result["photo"]

  # Set image as profile cover
  params = { "hash": hash, "photo": photo }
  resp = api.method("photos.saveOwnerCoverPhoto", params)
  print(resp)

def main():
  f = open("token.txt", "r")
  token = f.read().strip()
  f.close()

  api = VkApi(token)

  cover_image = Image.new(mode="RGB", size=COVER_SIZE, color=BACK_COLOR)
  font = ImageFont.truetype(FONT_FILE, 40)
  draw = ImageDraw.Draw(cover_image)

  text = genCoverText(api)
  draw.multiline_text(TEXT_START, text, font=font, fill=TEXT_COLOR, spacing=12)
  cover_image.save("cover.jpg", "jpeg")

  if len(sys.argv) >= 2 and sys.argv[1] == "test":
    cover_image.show()
    exit()

  uploadCover(api, "cover.jpg")

if __name__ == "__main__":
  main()
