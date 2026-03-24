import os
import re
import sys
import random
def read_dictionary(file_path="dictionary.txt"):
    dictionary = {}
    if not os.path.exists(file_path):
        print(f"错误：词典文件 {file_path} 不存在")
        return dictionary
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(' ', 1)
            if len(parts) < 2:
                continue
            hanzi, code = parts[0], parts[1]
            if '.' in code:
                continue
            if len(code) < 4:
                continue
            dictionary[code] = hanzi
    return dictionary

def get_abc_zone_entries(dictionary, abc_code):
    zone_entries = {}
    for code, hanzi in dictionary.items():
        if code.startswith(abc_code):
            if len(code) > 4:
                d_code = code[3] 
                e_code = code[4] 
            else:
                d_code = code[3]
                e_code = 'a'
            zone_entries[hanzi] = {
                'full_code': code,
                'd_code': d_code,
                'e_code': e_code
            }
    return zone_entries

def generate_tables(zone_entries):
    one_dim_table = {}
    for i in range(10):
        one_dim_table[str(i)] = []
    d_letters = [chr(i) for i in range(ord('b'), ord('z')+1) if chr(i) != 'e']
    e_letters = [chr(i) for i in range(ord('a'), ord('z')+1)] + [';']
    
    two_dim_table = {}
    for d in d_letters:
        two_dim_table[d] = {}
        for e in e_letters:
            two_dim_table[d][e] = []
    for hanzi, info in zone_entries.items():
        d_code = info['d_code']
        e_code = info['e_code']
        if d_code.isdigit():
            one_dim_table[d_code].append(hanzi)
        else:
            if d_code in two_dim_table:
                if e_code in two_dim_table[d_code]:
                    two_dim_table[d_code][e_code].append(hanzi)
                else:
                    print(f"警告：汉字 '{hanzi}' 的副码 '{e_code}' 不在有效范围内")
            else:
                print(f"警告：汉字 '{hanzi}' 的主码 '{d_code}' 不在有效范围内")
    return one_dim_table, two_dim_table, d_letters, e_letters

def print_one_dim_table(one_dim_table, abc_code):
    print("独体字表：")
    d_codes = [str(i) for i in range(10)]
    first_row = "|" + " |".join(d_codes)+" |"
    print(first_row)
    second_row_parts = []
    for d_code in d_codes:
        hanzi_list = one_dim_table[d_code]
        if hanzi_list:
            hanzi_str = "、".join(hanzi_list)
            cell_width = max(6, len(hanzi_str) + 2)
            second_row_parts.append(f"{hanzi_str}")
        else:
            second_row_parts.append("  ")
    second_row = "|" + "|".join(second_row_parts)+"|"
    print(second_row)
    total_single = sum(len(hanzi_list) for hanzi_list in one_dim_table.values())

def print_two_dim_table(two_dim_table, d_letters, e_letters, abc_code):
    print("合体字表：")
    transposed_table = {}
    for e_letter in e_letters:
        transposed_table[e_letter] = {}
        for d_letter in d_letters:
            transposed_table[e_letter][d_letter] = two_dim_table[d_letter][e_letter]
    header = "E\\D|" + " |".join([f"{d}" for d in d_letters])+" |"
    separator_len = len(header) + 5
    print(header)
    for e_letter in e_letters:
        row_parts = [f"{e_letter:}  "]
        for d_letter in d_letters:
            hanzi_list = transposed_table[e_letter][d_letter]
            if hanzi_list:
                if len(hanzi_list) > 2:
                    cell_content = "、".join(hanzi_list[:2]) + f"等{len(hanzi_list)}"
                else:
                    cell_content = "、".join(hanzi_list)
                cell_width = 6
                row_parts.append(f"{cell_content}")
            else:
                row_parts.append(f"{'  '}")
        
        print("|".join(row_parts)+"|")
    total_combined = 0
    for d_letter in d_letters:
        for e_letter in e_letters:
            total_combined += len(two_dim_table[d_letter][e_letter])

def analyze_abc_zone(abc_code):
    dictionary = read_dictionary()
    if not dictionary:
        print("词典为空或读取失败")
        return
    zone_entries = get_abc_zone_entries(dictionary, abc_code)
    if not zone_entries:
        print(f"{abc_code}区为空")
        return
    one_dim_table, two_dim_table, d_letters, e_letters = generate_tables(zone_entries)
    print_one_dim_table(one_dim_table, abc_code)
    print_two_dim_table(two_dim_table, d_letters, e_letters, abc_code)
    print()
    print(f"{abc_code}区详细分析")
    single_count = sum(len(hanzi_list) for hanzi_list in one_dim_table.values())
    combined_count = 0
    for d_letter in d_letters:
        for e_letter in e_letters:
            combined_count += len(two_dim_table[d_letter][e_letter])
    total_count = single_count + combined_count
    if total_count > 0:
        single_ratio = single_count / total_count * 100
        print(f"独体率：{single_count}/{total_count} {single_ratio:.1f}%")
    else:
        print("独体率：0/0 0.0%")
    d_code_stats = {}
    for hanzi, info in zone_entries.items():
        d_code = info['d_code']
        d_code_stats[d_code] = d_code_stats.get(d_code, 0) + 1
    
    print(f"主码分布：")
    if total_count > 0:
        for d_code, count in sorted(d_code_stats.items()):
            percentage = count / total_count * 100
            print(f"  D={d_code}: {count}字 ({percentage:.1f}%)")
    used_d_codes = set(d_code_stats.keys())
    print(f"使用的主码数量：{len(used_d_codes)}")
    e_not_a_count = 0
    for hanzi, info in zone_entries.items():
        if info['e_code'] != 'a':
            e_not_a_count += 1
    
    if total_count > 0:
        e_rate = e_not_a_count / total_count * 100
        print(f"副码率：{e_rate:.1f}%")
    else:
        print(f"副码率：0.0%")
        
def interactive_mode():
    print("解书音形 - 音区分析工具")
    while True:
        user_input = input("音区: ").strip().lower()
        if user_input == '':
            break
        elif len(user_input) < 2 or not (user_input[0].isalpha() and user_input[-1].isdigit()):
            print("错误：音码格式不正确")
            continue
        analyze_abc_zone(user_input)
        print()
def abcmain():
    if not os.path.exists("dictionary.txt"):
        print("错误：找不到 dictionary.txt 文件")
        print("请确保 dictionary.txt 文件与程序在同一目录下")
        return
    interactive_mode()

def check_code_exists(code):
    if not os.path.exists("ciyu.txt"):
        return False
    
    with open("ciyu.txt", "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) > 1 and code in parts[1:]:
                return True
    return False

def parse_code(code):
    AB = code[:2]
    
    if len(code) > 2 and code[2].isdigit():
        C = code[2]
        if len(code) > 3:
            D = code[3]
            if len(code) > 4:
                E = code[4]
                return {"AB": AB, "C": C, "D": D, "E": E, "len": 5}
            else:
                return {"AB": AB, "C": C, "D": D, "E": None, "len": 4}
        else:
            return {"AB": AB, "C": C, "D": None, "E": None, "len": 3}
    else:
        return {"AB": AB, "C": None, "D": None, "E": None, "len": 2}

def generate_all_combinations(code1, code2):
    combos = []
    
    c1 = parse_code(code1)
    c2 = parse_code(code2)
    
    if c1["AB"] and c2["AB"]:
        combos.append(c1["AB"] + c2["AB"][0])
    
    combos.append(c1["AB"] + c2["AB"])
    
    if c2["C"]:
        combos.append(c1["AB"] + c2["AB"] + c2["C"])
    if c2["C"] and c2["D"]:
        combos.append(c1["AB"] + c2["AB"] + c2["C"] + c2["D"])
    if c2["C"] and c2["D"] and c2["E"]:
        combos.append(c1["AB"] + c2["AB"] + c2["C"] + c2["D"] + c2["E"])
    if c1["C"] and c2["C"]:
        combos.append(c1["AB"] + c1["C"] + c2["AB"] + c2["C"])
    if c1["C"] and c2["C"] and c2["D"]:
        combos.append(c1["AB"] + c1["C"] + c2["AB"] + c2["C"] + c2["D"])
    if c1["C"] and c2["C"] and c2["D"] and c2["E"]:
        combos.append(c1["AB"] + c1["C"] + c2["AB"] + c2["C"] + c2["D"] + c2["E"])
    if c1["C"] and c1["D"] and c2["C"]:
        combos.append(c1["AB"] + c1["C"] + c1["D"] + c2["AB"] + c2["C"])
    if c1["C"] and c1["D"] and c2["C"] and c2["D"]:
        combos.append(c1["AB"] + c1["C"] + c1["D"] + c2["AB"] + c2["C"] + c2["D"])
    if c1["C"] and c1["D"] and c2["C"] and c2["D"] and c2["E"]:
        combos.append(c1["AB"] + c1["C"] + c1["D"] + c2["AB"] + c2["C"] + c2["D"] + c2["E"])
    if c1["C"] and c1["D"] and c1["E"] and c2["C"]:
        combos.append(c1["AB"] + c1["C"] + c1["D"] + c1["E"] + c2["AB"] + c2["C"])
    if c1["C"] and c1["D"] and c1["E"] and c2["C"] and c2["D"]:
        combos.append(c1["AB"] + c1["C"] + c1["D"] + c1["E"] + c2["AB"] + c2["C"] + c2["D"])
    if c1["C"] and c1["D"] and c1["E"] and c2["C"] and c2["D"] and c2["E"]:
        combos.append(c1["AB"] + c1["C"] + c1["D"] + c1["E"] + c2["AB"] + c2["C"] + c2["D"] + c2["E"])
    
    combos = [c for c in combos if c]
    
    unique_combos = []
    for c in combos:
        if c not in unique_combos:
            unique_combos.append(c)
    
    return unique_combos
def generate_default_codes_for_word(word, selected_codes):
    n = len(word)
    codes_info = [parse_code(code) for code in selected_codes]
    ab_list = [info["AB"] for info in codes_info]
    initial_list = [ab[0] if ab else "" for ab in ab_list]

    defaults = ""
    if n == 3:
        code = ab_list[0] + ab_list[1] + initial_list[2]
    elif n == 4:
        code1 = ''.join(initial_list)
        code2 = ab_list[0] + ab_list[1] + ab_list[2] + initial_list[3]
        code=code1+" "+code2
    elif n >= 5:
        code1 = ''.join(initial_list[:3]) + initial_list[-1]
        code2 = ''.join(initial_list)
        code=code1+" "+code2
    defaults=code
    return defaults
def process_two_char_word(word):
    code_str, missing = query_chars(word)
    if missing:
        print(f"未录入：{''.join(missing)}")
    codes_per_char = code_str.split()

    for i, codes in enumerate(codes_per_char):
        if codes == "--":
            return None

    code1 = codes_per_char[0].split('/')
    code2 = codes_per_char[1].split('/')

    print(f"{word[0]}{codes_per_char[0]}")
    print(f"{word[1]}{codes_per_char[1]}")
    if len(code1) > 1:
        xr1 = input(f"{word[0]} 读音选")
        if not xr1.isdigit():
            return None
        xr1=int(xr1)-1
        if 0 <= xr1 < len(code1):
            code1xr = code1[xr1]
        else:
            code1xr = code1[0]
    else:
        code1xr = code1[0]
    if len(code2) > 1:
        xr2 = input(f"{word[1]} 读音选")
        if not xr2.isdigit():
            return None
        xr2=int(xr2)-1
        if 0 <= xr2 < len(code2):
            code2xr = code2[xr2]
        else:
            code2xr = code2[0]
    else:
        code2xr = code2[0]

    all_combinations = generate_all_combinations(code1xr, code2xr)
    if not all_combinations:
        print("无法生成任何编码组合")
        return None

    for i, combo in enumerate(all_combinations, 1):
        print(f"{i:2d}.{combo}")

    while True:
        try:
            choice = input("编码选(0跳过)：")
            if choice == "0":
                return None
            start_index = int(choice)
            if 1 <= start_index <= len(all_combinations):
                selected_combinations = [all_combinations[start_index-1]]
                return selected_combinations
            else:
                print(f"请输入1到{len(all_combinations)}之间的数字")
        except ValueError:
            print("请输入有效的数字")

def process_multi_char_word(word):
    code_str, missing = query_chars(word)
    if missing:
        print(f"未录入：{''.join(missing)}")
    codes_per_char = code_str.split()

    for i, codes in enumerate(codes_per_char):
        if codes == "--":
            return None

    selected_codes = []
    for i, char in enumerate(word):
        codes = codes_per_char[i].split('/')
        print(f"{char}{codes_per_char[i]}")
        if len(codes) > 1:
            try:
                choice = input(f"{char} 读音选")
                if not choice.isdigit():
                    return None
                choice=int(choice)-1
                if 0 <= choice < len(codes):
                    selected_codes.append(codes[choice])
                else:
                    print("输入无效，使用第一个编码")
                    selected_codes.append(codes[0])
            except:
                print("输入无效，使用第一个编码")
                selected_codes.append(codes[0])
        else:
            selected_codes.append(codes[0])

    default_code = generate_default_codes_for_word(word, selected_codes)
    print(f"默认：{default_code}")
    choice = input("输入1添加默认编码，或直接输入自定义编码：").strip()
    if choice=="1":
        selected_codes_list = [default_code]
    else:
        if choice == "":
            print("未输入编码，放弃添加")
            return None
        selected_codes_list = choice.split()

    return selected_codes_list

def add_to_ciyu(word, codes, overwrite=False):
    if not word or not codes:
        return False

    lines = []
    if os.path.exists("ciyu.txt"):
        with open("ciyu.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

    new_lines = [line for line in lines if not line.startswith(word + " ")]
    existing = (len(new_lines) != len(lines))

    if existing and not overwrite:
        print(f"词语 '{word}' 已存在，原有编码将被保留。若要覆盖，请使用覆盖模式。")
        return False

    entry = word + " " + " ".join(codes) + "\n"
    new_lines.append(entry)

    with open("ciyu.txt", "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    if existing:
        print(f"已覆盖原编码")
    return True

def ciyumain():
    if not os.path.exists("ciyu.txt"):
        with open("ciyu.txt", "w", encoding="utf-8") as f:
            pass

    while True:
        line = input("连续词语：").strip()
        if not line:
            break

        words = line.split()
        for word in words:
            print(f"========{word}========")
            if len(word) == 2:
                codes = process_two_char_word(word)
            elif len(word)==1:
                general_symbol=input("识别为通用符号，请输入自定义编码：").strip()
                codes = general_symbol.split()
            else:
                codes = process_multi_char_word(word)

            if not word or not codes:
                print(f"跳过 {word}")
                continue

            print(f"{word}{' '.join(codes)}")
            add_to_ciyu(word, codes, overwrite=True)

DATA_FILE = "dictionary.txt"

def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8'):  
            pass

def query_by_char(char):
    ensure_data_file()
    
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        return []
    
    results = []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(' ', 1)
            if len(parts) == 2 and parts[0] == char:
                results.append(parts[1])
    
    return results

def query_chars(chars_string):
    """核心查询函数，返回 (编码字符串, 未录入汉字列表)"""
    result_parts = []
    missing_chars = []
    goly=""
    for char in chars_string:
        if '\u3400' <= char <= '\u9fff' or 0x20000 <= ord(char) <= 0x33479 or '\uf900' <= char <= '\ufad9':
            goly+=char
    for char in goly:
        codes = query_by_char(char)
        if codes:
            result_parts.append('/'.join(codes))
        else:
            result_parts.append("--")
            missing_chars.append(char)
    return ' '.join(result_parts), missing_chars

class GuessCodingGame:
    def __init__(self):
        self.dictionary = []
        self.e_codes_dict = []
        self.current_mode = None
        
    def load_dictionary(self):
        try:
            with open('dictionary.txt', 'r', encoding='utf-8') as f:
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
        except Exception as e:
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
            ABC=code[:3]
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
            ABC=code[:3]
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
                    if attempts>1:
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
    game = GuessCodingGame()
    if not os.path.exists('dictionary.txt'):
        print("未找到 dictionary.txt 文件")
    game.run()
if __name__ == "__main__":
    print("此文件为管理程序 newedit.py 的辅助模块。请勿直接运行此文件，如需使用请通过 newedit.py 的菜单调用。")
    _=input()
