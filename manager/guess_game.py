import random
import os
from config import DATA_FILE


class GuessCodingGame:
    def __init__(self):
        self.dictionary = []
        self.e_codes_dict = []
        self.current_mode = None

    def load_dictionary(self):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and ' ' in line:
                        parts = line.split(' ')
                        if len(parts) >= 2:
                            word = parts[0]
                            code = parts[1]
                            self.dictionary.append((word, code))
                            if len(code) >= 5 and code[4] != '.':
                                self.e_codes_dict.append((word, code))
        except FileNotFoundError:
            return False
        except Exception:
            return False
        return True

    def get_random_word_with_d(self):
        if not self.dictionary:
            return None
        return random.choice(self.dictionary)

    def get_random_word_with_e(self):
        if not self.e_codes_dict:
            return None
        return random.choice(self.e_codes_dict)

    def get_d_code(self, code):
        if len(code) >= 4:
            return code[3]
        return None

    def get_e_code(self, code):
        if len(code) >= 5 and code[4] != '.':
            return code[4]
        return None

    def guess_d_mode(self):
        print("猜主码,a返回")
        while True:
            word, code = self.get_random_word_with_d()
            d_code = self.get_d_code(code)
            ABC = code[:3]
            print(f"*{word}*,音码{ABC}")
            while True:
                user_input = input("猜主码: ").strip()
                if user_input.lower() == 'a':
                    return
                if not user_input or len(user_input) != 1:
                    print("请输入一个字符")
                    continue
                if user_input == d_code:
                    print(f"正确！主码是{d_code}，完整编码{code}")
                    break
                else:
                    print("错误，请再试一次")

    def guess_e_mode(self):
        print("猜E码，a返回")
        while True:
            word, code = self.get_random_word_with_e()
            e_code = self.get_e_code(code)
            d_code = self.get_d_code(code)
            ABC = code[:3]
            print(f"*{word}*,音码{ABC}")
            attempts = 0
            while True:
                user_input = input("猜副码: ").strip()
                if user_input.lower() == 'a':
                    return
                if not user_input or len(user_input) != 1:
                    print("请输入一个字符")
                    continue
                attempts += 1
                if user_input == e_code:
                    print(f"正确！副码是{e_code}，完整编码: {code}")
                    break
                else:
                    print("错误，请再试一次")
                    if attempts > 1:
                        print(f"提示主码：{d_code}")

    def show_menu(self):
        print("解书音形 - 猜编码小游戏")
        print("D - 猜主码(形部)")
        print("E - 猜副码")

    def run(self):
        if not self.load_dictionary():
            return
        while True:
            self.show_menu()
            choice = input("选择: ").strip().upper()
            if choice == '':
                break
            elif choice == 'D':
                self.guess_d_mode()
            elif choice == 'E':
                if not self.e_codes_dict:
                    continue
                self.guess_e_mode()
            else:
                print("请重新输入")


def bmmamain():
    """猜编码游戏入口"""
    game = GuessCodingGame()
    if not os.path.exists(DATA_FILE):
        print("未找到 dictionary.txt 文件")
    game.run()
