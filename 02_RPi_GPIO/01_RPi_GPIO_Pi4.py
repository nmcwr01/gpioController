"""
4WD TT 모터 제어 (RPi.GPIO + 화살표 키)
라즈베리 파이 4 기준
────────────────────────────────────────
화살표 키를 누르는 동안 움직이고
손을 떼면 즉시 정지합니다.

  ↑  : 전진
  ↓  : 후진
  ←  : 왼쪽 회전
  →  : 오른쪽 회전
  ESC: 종료

설치:
  pip install pynput
  (RPi.GPIO는 라즈베리 파이 OS 기본 내장)

GPIO 핀 → L298N 연결:
  GPIO 17 → ENA   GPIO 27 → IN1   GPIO 22 → IN2
  GPIO 18 → ENB   GPIO 23 → IN3   GPIO 24 → IN4
"""

import RPi.GPIO as GPIO
from pynput import keyboard
import time

# ────────────────────────────────────────────
# GPIO 핀 번호 (BCM 기준)
# ────────────────────────────────────────────
ENA = 17   # 왼쪽 모터 PWM
IN1 = 27   # 왼쪽 방향 A
IN2 = 22   # 왼쪽 방향 B

ENB = 18   # 오른쪽 모터 PWM
IN3 = 23   # 오른쪽 방향 A
IN4 = 24   # 오른쪽 방향 B

SPEED = 80   # 속도 0~100 (%)

# ────────────────────────────────────────────
# GPIO 초기화
# ────────────────────────────────────────────
GPIO.setmode(GPIO.BCM)          # BCM 핀 번호 사용
GPIO.setwarnings(False)

# 방향 핀 출력 설정
for pin in [IN1, IN2, IN3, IN4]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# PWM 핀 설정
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

# PWM 객체 생성 (주파수: 1000Hz)
pwm_left  = GPIO.PWM(ENA, 1000)
pwm_right = GPIO.PWM(ENB, 1000)

pwm_left.start(0)    # 0%로 시작 (정지)
pwm_right.start(0)

print("✅ GPIO 초기화 완료")

# ────────────────────────────────────────────
# 모터 제어 함수
# ────────────────────────────────────────────
def set_left(direction, speed=SPEED):
    """
    direction: 'forward' / 'backward' / 'stop'
    speed: 0~100
    """
    if direction == 'forward':
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        pwm_left.ChangeDutyCycle(speed)
    elif direction == 'backward':
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        pwm_left.ChangeDutyCycle(speed)
    else:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        pwm_left.ChangeDutyCycle(0)

def set_right(direction, speed=SPEED):
    if direction == 'forward':
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
        pwm_right.ChangeDutyCycle(speed)
    elif direction == 'backward':
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
        pwm_right.ChangeDutyCycle(speed)
    else:
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
        pwm_right.ChangeDutyCycle(0)

def forward():
    set_left('forward')
    set_right('forward')
    print("⬆️  전진")

def backward():
    set_left('backward')
    set_right('backward')
    print("⬇️  후진")

def turn_left():
    set_left('backward')    # 왼쪽 후진
    set_right('forward')    # 오른쪽 전진
    print("⬅️  왼쪽")

def turn_right():
    set_left('forward')     # 왼쪽 전진
    set_right('backward')   # 오른쪽 후진
    print("➡️  오른쪽")

def stop():
    set_left('stop')
    set_right('stop')
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

try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
finally:
    # 종료 시 GPIO 정리
    stop()
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()
    print("✅ GPIO 정리 완료")