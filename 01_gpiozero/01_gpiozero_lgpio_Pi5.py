"""
4WD TT 모터 제어 (gpiozero + 화살표 키, SSH 원격용)
라즈베리 파이 5 기준 (lgpio 백엔드)
  ↑ 전진  ↓ 후진  ← 왼쪽  → 오른쪽  ESC 종료

GPIO → L298N:
  GPIO 17 → ENA   GPIO 27 → IN1   GPIO 22 → IN2
  GPIO 18 → ENB   GPIO 23 → IN3   GPIO 24 → IN4
"""
import os
os.environ['GPIOZERO_PIN_FACTORY'] = 'lgpio'

from gpiozero import Motor
from sshkeyboard import listen_keyboard, stop_listening

left  = Motor(forward=27, backward=22, enable=17)
right = Motor(forward=23, backward=24, enable=18)
SPEED = 0.8

def forward():
    left.forward(SPEED);  right.forward(SPEED);  print("전진")
def backward():
    left.backward(SPEED); right.backward(SPEED); print("후진")
def turn_left():
    left.backward(SPEED); right.forward(SPEED);  print("왼쪽")
def turn_right():
    left.forward(SPEED);  right.backward(SPEED); print("오른쪽")
def stop():
    left.stop(); right.stop(); print("정지")

ACTIONS = {
            "up": forward, 
            "down": backward,
            "left": turn_left, 
            "right": turn_right
           }

def on_press(key):
    if key in ACTIONS:
        ACTIONS[key]()
    elif key == "esc":
        print("\n 종료합니다.")
        stop_listening()

def on_release(key):
    if key in ACTIONS:
        stop()

print("4WD 모터 제어 시작  |  ↑↓←→ 조종, ESC 종료\n")
stop()
try:
    listen_keyboard(
        on_press=on_press,
        on_release=on_release,
        delay_second_char=0.25,   # 키를 뗀 것으로 판단하는 대기 시간
        delay_other_chars=0.05,
    )
finally:
    stop()                       # ESC, Ctrl+C, 오류가 나도 반드시 정지