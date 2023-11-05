from __future__ import print_function

import audioop
from ctypes import *

import MicrophoneStream as MS
import RPi.GPIO as GPIO
import ktkws  # KWS

RATE = 16000
CHUNK = 512

def btn_detect():
    global btn_status
    with MS.MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()

        for content in audio_generator:
            GPIO.output(31, GPIO.HIGH)
            rc = ktkws.detect(content)
            rms = audioop.rms(content, 2)
            # print('audio rms = %d' % (rms))
            GPIO.output(31, GPIO.LOW)
            if btn_status:
                rc = 1
                btn_status = False
            if rc == 1:
                GPIO.output(31, GPIO.HIGH)
                # MS.play_file("../data/sample_sound.wav")
                return 200

def btn_test():
    global btn_status
    rc = ktkws.init("../data/kwsmodel.pack")
    print('init rc = %d' % rc)
    rc = ktkws.start()
    print('start rc = %d' % rc)
    print('\n버튼을 눌러보세요~\n')
    rc = btn_detect()
    print('detect rc = %d' % rc)
    print('\n\n호출어가 정상적으로 인식되었습니다.\n\n')
    ktkws.stop()
    return rc

def main():
    btn_test()


if __name__ == '__main__':
    main()
