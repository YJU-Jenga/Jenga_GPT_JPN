#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example 9: 버튼 음성인식 대화 결합 예제
"""

from __future__ import print_function

import MicrophoneStream as MS
import ex1_kwstest as kws
import ex6_queryVoice as dss
import GPT_Kinou2 as gpt


def main():
    while 1:
        recog = kws.btn_test()
        if recog == 200:
            print('Button On')
            text = gpt.speech_to_text()
            if text == '':
                print('질의한 내용이 없습니다.')
            else:
                print(text)
        # time.sleep(2)
        else:
            print('KWS Not Dectected ...')


if __name__ == '__main__':
    main()
