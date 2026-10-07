"""
4WD TT 모터 제어 (gpiozero + 화살표 키)
라즈베리 파이 5 기준 (lgpio 백엔드)
────────────────────────────────────────
화살표 키를 누르는 동안 움직이고
손을 떼면 즉시 정지합니다.

  ↑  : 전진
  ↓  : 후진
  ←  : 왼쪽 회전
  →  : 오른쪽 회전
  ESC: 종료

설치:
  pip install gpiozero lgpio pynput

GPIO 핀 → L298N 연결:
  GPIO 17 → ENA   GPIO 27 → IN1   GPIO 22 → IN2
  GPIO 18 → ENB   GPIO 23 → IN3   GPIO 24 → IN4
"""

import os
os.environ['GPIOZERO_PIN_FACTORY'] = 'lgpio'   # 라즈베리 파이 5 필수
#os.environ['GPIOZERO_PIN_FACTORY'] = 'rpigpio'

from gpiozero import Motor
from pynput import keyboard

# ────────────────────────────────────────────
# 모터 초기화
# Motor(forward=방향A핀, backward=방향B핀, enable=PWM핀)
# ────────────────────────────────────────────
left  = Motor(forward=27, backward=22, enable=17)   # 왼쪽 모터 (앞+뒤 병렬)
right = Motor(forward=23, backward=24, enable=18)   # 오른쪽 모터 (앞+뒤 병렬)

SPEED = 0.8   # 속도 0.0 ~ 1.0

# ────────────────────────────────────────────
# 주행 함수
# ────────────────────────────────────────────
def forward():
    left.forward(SPEED)
    right.forward(SPEED)
    print("⬆️  전진")

def backward():
    left.backward(SPEED)
    right.backward(SPEED)
    print("⬇️  후진")

def turn_left():
    left.backward(SPEED)    # 왼쪽 후진
    right.forward(SPEED)    # 오른쪽 전진
    print("⬅️  왼쪽")

def turn_right():
    left.forward(SPEED)     # 왼쪽 전진
    right.backward(SPEED)   # 오른쪽 후진
    print("➡️  오른쪽")

def stop():
    left.stop()
    right.stop()
    print("⏹  정지")

# ────────────────────────────────────────────
# 키보드 이벤트
# ────────────────────────────────────────────
def on_press(key):
    """키를 누를 때 → 모터 동작"""
    if   key == keyboard.Key.up:    forward()
    elif key == keyboard.Key.down:  backward()
    elif key == keyboard.Key.left:  turn_left()
    elif key == keyboard.Key.right: turn_right()
    elif key == keyboard.Key.esc:
        print("\n🛑 종료합니다.")
        stop()
        return False   # 리스너 종료

def on_release(key):
    """키를 뗄 때 → 즉시 정지"""
    if key in (keyboard.Key.up,
               keyboard.Key.down,
               keyboard.Key.left,
               keyboard.Key.right):
        stop()

# ────────────────────────────────────────────
# 실행
# ────────────────────────────────────────────
print("🚗 4WD 모터 제어 시작")
print("   ↑↓←→ 화살표 키로 조종  |  ESC 종료\n")

stop()   # 시작 시 정지 확인

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()