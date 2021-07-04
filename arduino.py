from pynput.keyboard import Listener, Controller
from pynput.keyboard import Key, KeyCode
from typing import Union, List, Tuple
from enum import Enum
import time
from SleepCountdown.SleepCountdown import sleep_countdown
import pickle
import serial


KeyState = Enum("KeyState", "Pressed Released")


KEY_UP_ARROW = 0xDA
KEY_DOWN_ARROW = 0xD9
KEY_LEFT_ARROW = 0xD8
KEY_RIGHT_ARROW = 0xD7
KEY_ESC = 0xB1


"""

"""


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


class RecordKeys:
    def __init__(self):
        self._last_action_time = time.time()
        self._curr_pressed_keys = dict()
        self._recorded_keys = []

    def on_press(self, key: Union[KeyCode, Key]):
        if key in self._curr_pressed_keys:  # key is already pressed, no need to do anything
            return

        print(key)

        self._curr_pressed_keys[key] = time.time()
        self._recorded_keys.append((key, KeyState.Pressed, time.time() - self._last_action_time))
        self._last_action_time = time.time()

    def on_release(self, key: Union[KeyCode, Key]):
        del self._curr_pressed_keys[key]
        self._recorded_keys.append((key, KeyState.Released, time.time() - self._last_action_time))
        self._last_action_time = time.time()

        if key == Key.esc:
            return False  # stop the listener

    def record(self) -> List[Tuple[Union[KeyCode, Key], KeyState, float]]:
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

        return self._recorded_keys


def send_print(serial_port: serial.Serial, data):
    serial_port.write(data)
    print(int.from_bytes(data, 'big'))


def parse_key(key: Union[KeyCode, Key]) -> bytes:
    if isinstance(key, KeyCode):
        return str(key).replace("'", '').encode()

    if key == Key.up:
        return int_to_bytes(KEY_UP_ARROW)

    elif key == Key.down:
        return int_to_bytes(KEY_DOWN_ARROW)

    elif key == Key.left:
        return int_to_bytes(KEY_LEFT_ARROW)

    elif key == Key.right:
        return int_to_bytes(KEY_RIGHT_ARROW)

    elif key == Key.space:
        return b' '

    elif key == Key.esc:
        return int_to_bytes(KEY_ESC)

    else:
        raise ValueError("Only characters and arrows")


def send_actions(recorded_keys: List[Tuple[Union[KeyCode, Key], KeyState, float]], serial_port: serial.Serial):
    to_send: bytes

    for action in recorded_keys:
        send_print(serial_port, parse_key(action[0]))
        send_print(serial_port, int_to_bytes(action[1].value))
        send_print(serial_port, (int(action[2] * 1000000)).to_bytes(4, 'big', signed=False) + b'\x00')  # + b'\x00'
        print()


def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def main():
    time.sleep(0.5)
    print("Start")

    recorded_keys = RecordKeys().record()
    print(recorded_keys)

    save_object(recorded_keys, 'recorded_keys.pkl')

    print("Done record, now do action")

    ser = serial.Serial('COM4')

    sleep_countdown(2)

    send_actions(recorded_keys, ser)


if __name__ == '__main__':
    main()
