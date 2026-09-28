"""
4WD TT 모터 제어 (lgpio + 화살표 키)
라즈베리 파이 5 전용
────────────────────────────────────────
화살표 키를 누르는 동안 움직이고
손을 떼면 즉시 정지합니다.

  ↑  : 전진
  ↓  : 후진
  ←  : 왼쪽 회전
  →  : 오른쪽 회전
  ESC: 종료

설치:
  pip install lgpio pynput

GPIO 핀 → L298N 연결:
  GPIO 17 → ENA   GPIO 27 → IN1   GPIO 22 → IN2
  GPIO 18 → ENB   GPIO 23 → IN3   GPIO 24 → IN4
"""

import lgpio
from pynput import keyboard

# ────────────────────────────────────────────
# GPIO 핀 번호 (BCM)
# ────────────────────────────────────────────
ENA = 17   # 왼쪽 모터 PWM
IN1 = 27   # 왼쪽 방향 A
IN2 = 22   # 왼쪽 방향 B

ENB = 18   # 오른쪽 모터 PWM
IN3 = 23   # 오른쪽 방향 A
IN4 = 24   # 오른쪽 방향 B

PWM_FREQ = 1000   # PWM 주파수 (Hz)
SPEED    = 80     # 속도 0~100 (%)

# ────────────────────────────────────────────
# lgpio 초기화
# ────────────────────────────────────────────
chip = lgpio.gpiochip_open(0)   # GPIO 칩 열기

# 방향 핀 출력 설정
for pin in [IN1, IN2, IN3, IN4]:
    lgpio.gpio_claim_output(chip, pin, 0)   # 초기값 LOW

# PWM 핀 설정
lgpio.gpio_claim_output(chip, ENA, 0)
lgpio.gpio_claim_output(chip, ENB, 0)

print("✅ lgpio 초기화 완료")

# ────────────────────────────────────────────
# 모터 제어 함수
# ────────────────────────────────────────────
def set_left(direction, speed=SPEED):
    """
    direction: 'forward' / 'backward' / 'stop'
    speed: 0~100
    """
    if direction == 'forward':
        lgpio.gpio_write(chip, IN1, 1)
        lgpio.gpio_write(chip, IN2, 0)
        lgpio.tx_pwm(chip, ENA, PWM_FREQ, speed)
    elif direction == 'backward':
        lgpio.gpio_write(chip, IN1, 0)
        lgpio.gpio_write(chip, IN2, 1)
        lgpio.tx_pwm(chip, ENA, PWM_FREQ, speed)
    else:
        lgpio.gpio_write(chip, IN1, 0)
        lgpio.gpio_write(chip, IN2, 0)
        lgpio.tx_pwm(chip, ENA, PWM_FREQ, 0)

def set_right(direction, speed=SPEED):
    if direction == 'forward':
        lgpio.gpio_write(chip, IN3, 1)
        lgpio.gpio_write(chip, IN4, 0)
        lgpio.tx_pwm(chip, ENB, PWM_FREQ, speed)
    elif direction == 'backward':
        lgpio.gpio_write(chip, IN3, 0)
        lgpio.gpio_write(chip, IN4, 1)
        lgpio.tx_pwm(chip, ENB, PWM_FREQ, speed)
    else:
        lgpio.gpio_write(chip, IN3, 0)
        lgpio.gpio_write(chip, IN4, 0)
        lgpio.tx_pwm(chip, ENB, PWM_FREQ, 0)

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
    if   key == keyboard.Key.up:    forward()
    elif key == keyboard.Key.down:  backward()
    elif key == keyboard.Key.left:  turn_left()
    elif key == keyboard.Key.right: turn_right()
    elif key == keyboard.Key.esc:
        print("\n🛑 종료합니다.")
        stop()
        return False

def on_release(key):
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

stop()

try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
finally:
    stop()
    lgpio.gpiochip_close(chip)   # GPIO 칩 닫기
    print("✅ lgpio 정리 완료")