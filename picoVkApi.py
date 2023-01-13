# -*- coding: utf-8 -*-

import requests
import time

APIVER = "5.131"
RPS_DELAY = 0.34

class VkApiError(Exception):
  pass

class VkApi(object):

  def __init__(self, token):
    self.token = token
    self.last_request = 0.0

  def method(self, method, params=None):

    delay = RPS_DELAY - (time.time() - self.last_request)
    if delay > 0:
      time.sleep(delay)

    url = "https://api.vk.com/method/{}".format(method)
    payload = { "access_token": self.token, "v": APIVER }

    if params is not None:
      payload.update(params)

    resp = requests.post(url, data=payload)
    self.last_request = time.time()

    result = resp.json()
    if "error" in result:
      error_code = result["error"]["error_code"]
      error_msg = result["error"]["error_msg"]
      error_str = "[{}] {}".format(error_code, error_msg)

      raise VkApiError(error_str)

    return result["response"]
