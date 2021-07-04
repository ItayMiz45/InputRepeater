from pynput.keyboard import Listener, Controller
from pynput.keyboard import Key, KeyCode
from typing import Union, List, Tuple
from enum import Enum
import time
from SleepCountdown.SleepCountdown import sleep_countdown
import pickle


KeyState = Enum("KeyState", "Pressed Released")


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
        if key == Key.esc:
            return False  # stop the listener

        del self._curr_pressed_keys[key]
        self._recorded_keys.append((key, KeyState.Released, time.time() - self._last_action_time))
        self._last_action_time = time.time()

    def record(self) -> List[Tuple[Union[KeyCode, Key], KeyState, float]]:
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

        return self._recorded_keys


def do_actions(recorded_keys: List[Tuple[Union[KeyCode, Key], KeyState, float]]):
    keyboard = Controller()

    for action in recorded_keys:
        time.sleep(action[2])
        if action[1] == KeyState.Pressed:
            keyboard.press(action[0])
        elif action[1] == KeyState.Released:
            keyboard.release(action[0])
        else:
            raise ValueError("KeyState is not pressed or released")


def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def main():
    time.sleep(0.5)
    print("Start")

    recorded_keys = RecordKeys().record()

    save_object(recorded_keys, 'recorded_keys.pkl')

    print("Done record, now do action")
    sleep_countdown(2)

    # do_actions(recorded_keys)


if __name__ == '__main__':
    main()
