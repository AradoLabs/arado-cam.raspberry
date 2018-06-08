# -*- coding: utf-8 -*-
"""Rasperry PI camera capture and upload"""
import os
import sys

ARADOCAM_API_BASE_URL = os.environ['ARADOCAM_API_BASE_URL']
ARADOCAM_BOT_ID = os.environ['ARADOCAM_BOT_ID']
ARADOCAM_BOT_KEY = os.environ['ARADOCAM_BOT_KEY']
ARADOCAM_BOT_PART_ID = os.environ['ARADOCAM_BOT_PART_ID']
ARADOCAM_BOT_CAPTURE_WIDTH = int(os.environ['ARADOCAM_BOT_CAPTURE_WIDTH'])
ARADOCAM_BOT_CAPTURE_HEIGHT = int(os.environ['ARADOCAM_BOT_CAPTURE_HEIGHT'])

if ARADOCAM_API_BASE_URL is None:
    raise Exception('ARADOCAM_API_BASE_URL is not set')

if ARADOCAM_BOT_KEY is None:
    raise Exception('ARADOCAM_API_KEY is not set')

TOKEN_URL = ARADOCAM_API_BASE_URL + 'token'
VISION_URL = ARADOCAM_API_BASE_URL + 'vision/' + ARADOCAM_BOT_PART_ID


def post_frame(data, token):
    """POST frame (i.e. picture from PI camera) to API"""
    import requests

    def refresh_token():
        """Refresh the API token"""
        headers = {
            'bot-id':  ARADOCAM_BOT_ID,
            'bot-key': ARADOCAM_BOT_KEY}

        response = requests.get(url=TOKEN_URL, headers=headers)

        if response.status_code != 200:
            raise Exception('authentication failed: ' + response.status_code)
        else:
            return response.content


    def post_data(data, token):
        """POST data to API"""
        headers = {'Content-Type': 'application/octet-stream',
                   'authorization': 'bearer ' + token}
        response = requests.post(url=VISION_URL, data=data, headers=headers)

        return response

    response = post_data(data, token)

    if response.status_code == 401:
        print 'refreshing API token'
        token = refresh_token()
        response = post_data(data, token)

        if response.status_code != 201:
            raise Exception('failed to post with fresh token: ' + response.status_code)

    elif response.status_code != 201:
        print response.status_code
        raise Exception('post failed: ' + response.status_code)

    return token

def wait():
    import time
    seconds_between_captures = 60
    now_seconds = time.time()
    now_minutes = int(now_seconds / 60)
    now_seconds_rounded = now_minutes * 60
    next_capure_seconds = now_seconds_rounded + seconds_between_captures
    delay = next_capure_seconds - now_seconds
    print 'delay: ' + str(delay)
    sys.stdout.flush()
    time.sleep(delay)


def main_loop():
    """take stills from PI camera and upload them using API"""

    print VISION_URL
    sys.stdout.flush()

    import time
    import picamera
    import io

    token = ''
    with picamera.PiCamera() as camera:
        # http://picamera.readthedocs.io/en/release-1.12/fov.html
        # http://picamera.readthedocs.io/en/release-1.10/recipes1.html

        # camera.resolution = (3280, 2464)
        # camera.color_effects = (128, 128) # black and white
        # camera.resolution = (ARADOCAM_BOT_CAPTURE_WIDTH, ARADOCAM_BOT_CAPTURE_HEIGHT)

        # camera.resolution = (1920, 1080)
        camera.resolution = (3280, 2464)
        camera.framerate = 30

        # Wait for the automatic gain control to settle
        time.sleep(2)

        camera.exposure_mode = 'off'
        awb_gains = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = awb_gains

        time.sleep(2)

        while True:
            wait()

            print 'capturing'
            sys.stdout.flush()

            stream = io.BytesIO()
            camera.capture(stream, format='jpeg', quality=80, resize=(640, 480))
            # camera.capture(stream, format='jpeg', quality=80)
            data = stream.getvalue()
            token = post_frame(data, token)

main_loop()
