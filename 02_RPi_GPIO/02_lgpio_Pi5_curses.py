# -*- coding: utf-8 -*-
"""
4WD TT 모터 제어 (lgpio + curses 키보드)
라즈베리 파이 5 전용
────────────────────────────────────────
화살표 키를 누르는 동안 움직이고
키를 떼면 즉시 정지합니다.

  ↑  : 전진
  ↓  : 후진
  ←  : 왼쪽 회전
  →  : 오른쪽 회전
  q  : 종료
"""

import lgpio
import curses

# GPIO 핀 번호 (BCM 기준)
ENA = 18   # 왼쪽 모터 PWM  (물리 핀 12)
IN1 = 27   # 왼쪽 방향 A    (물리 핀 13)
IN2 = 22   # 왼쪽 방향 B    (물리 핀 15)

ENB = 17   # 오른쪽 모터 PWM (물리 핀 11)
IN3 = 23   # 오른쪽 방향 A   (물리 핀 16)
IN4 = 24   # 오른쪽 방향 B   (물리 핀 18)

PWM_FREQ = 1000   # PWM 주파수 (Hz)
SPEED    = 25     # 속도 0~100 (%)

# lgpio 초기화
chip = lgpio.gpiochip_open(0)
for pin in [IN1, IN2, IN3, IN4]:
    lgpio.gpio_claim_output(chip, pin, 0)
lgpio.gpio_claim_output(chip, ENA, 0)
lgpio.gpio_claim_output(chip, ENB, 0)


def set_left(direction, speed=SPEED):
    if direction == 'forward':
        lgpio.gpio_write(chip, IN1, 1); lgpio.gpio_write(chip, IN2, 0)
        lgpio.tx_pwm(chip, ENA, PWM_FREQ, speed)
    elif direction == 'backward':
        lgpio.gpio_write(chip, IN1, 0); lgpio.gpio_write(chip, IN2, 1)
        lgpio.tx_pwm(chip, ENA, PWM_FREQ, speed)
    else:
        lgpio.gpio_write(chip, IN1, 0); lgpio.gpio_write(chip, IN2, 0)
        lgpio.tx_pwm(chip, ENA, PWM_FREQ, 0)

def set_right(direction, speed=SPEED):
    if direction == 'forward':
        lgpio.gpio_write(chip, IN3, 1); lgpio.gpio_write(chip, IN4, 0)
        lgpio.tx_pwm(chip, ENB, PWM_FREQ, speed)
    elif direction == 'backward':
        lgpio.gpio_write(chip, IN3, 0); lgpio.gpio_write(chip, IN4, 1)
        lgpio.tx_pwm(chip, ENB, PWM_FREQ, speed)
    else:
        lgpio.gpio_write(chip, IN3, 0); lgpio.gpio_write(chip, IN4, 0)
        lgpio.tx_pwm(chip, ENB, PWM_FREQ, 0)

def forward():    set_left('forward');   set_right('forward')
def backward():   set_left('backward');  set_right('backward')
def turn_left():  set_left('backward');  set_right('forward')
def turn_right(): set_left('forward');   set_right('backward')
def stop():       set_left('stop');      set_right('stop')


def main(stdscr):
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.addstr(0, 0, "4WD 모터 제어 | 화살표키: 이동 | q: 종료")
    stdscr.addstr(1, 0, "상태: 정지")

    stop()

    while True:
        key = stdscr.getch()

        if key == curses.KEY_UP:
            forward();    stdscr.addstr(1, 0, "상태: 전진   ")
        elif key == curses.KEY_DOWN:
            backward();   stdscr.addstr(1, 0, "상태: 후진   ")
        elif key == curses.KEY_LEFT:
            turn_left();  stdscr.addstr(1, 0, "상태: 좌회전 ")
        elif key == curses.KEY_RIGHT:
            turn_right(); stdscr.addstr(1, 0, "상태: 우회전 ")
        elif key == ord('q'):
            stop()
            break
        else:
            stop();       stdscr.addstr(1, 0, "상태: 정지   ")

        stdscr.refresh()


try:
    curses.wrapper(main)
finally:
    stop()
    lgpio.gpiochip_close(chip)
    print("종료 완료")