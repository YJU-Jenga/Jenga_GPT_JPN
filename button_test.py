import RPi.GPIO as GPIO

# GPIO 설정
BUTTON_PIN = 29
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def button_pressed(channel):
    print("Button Pressed!")
    global btn_status
    btn_status = True

# 버튼 이벤트 핸들러 등록
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_pressed, bouncetime=200)

# 초기 버튼 상태
btn_status = False

# 버튼을 누를 때 200을 반환하는 함수
def btn_detect():
    global btn_status
    if btn_status:
        btn_status = False  # 버튼 상태 초기화
        return 200
    return 0  # 버튼이 눌리지 않았을 때

# 버튼 누를 때 200을 반환하도록 설정
while True:
    result = btn_detect()
    if result == 200:
        print("Button Pressed: 200 Returned")
    # 여기에서 다른 코드 또는 동작을 수행할 수 있습니다.
