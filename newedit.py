import os
import re
import subprocess
import sys
from pypinyin import pinyin, Style
try:
    from vgli import main_menu
    from vgli import process_file
    from vgli import sort_file_by_second_part
except ImportError:
    def process_file(input_file, output_file):
        print("警告：vgli模块导入失败，使用备用排序函数")
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = sorted(f.readlines())
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
try:
    from addition import query_chars
    from addition import interactive_mode
    from addition import ciyumain
    from addition import bmmamain
    fujw = True
except ImportError:
    fujw = False
    print("警告：无法导入,选项4、7、8、9不可用")

final_dict = {
    "q": ["iu"], "w": ["ia", "ua"], "e": ["e"], "r": ["uan", "er"],
    "t": ["ve", "ue"], "y": ["uai", "v"], "u": ["u"], "i": ["i"],
    "o": ["o", "uo"], "p": ["un", "vn"], "a": ["a"], "s": ["ong", "iong"],
    "d": ["iang", "uang"], "f": ["en"], "g": ["eng"], "h": ["ang"],
    "j": ["an"], "k": ["ao"], "l": ["ai"], "z": ["ei"], "x": ["ie"],
    "c": ["iao"], "v": ["ui"], "b": ["ou"], "n": ["in"], "m": ["ian"],
    ";": ["ing"]
}

special_cases = {
    "噷": ["hm0"],
    "哼": ["hn0"],
    "嗯": ["nv0"]
}

def get_initial(pinyin_str):
    pinyin_clean = re.sub(r'\d', '', pinyin_str)
    if not pinyin_clean:
        return 'o'
    if pinyin_clean[0] in 'jqxyw':
        return pinyin_clean[0]
    if pinyin_clean.startswith('ch'):
        return 'i'
    if pinyin_clean.startswith('sh'):
        return 'u'
    if pinyin_clean.startswith('zh'):
        return 'v'
    if pinyin_clean[0] in 'aeiou':
        return 'o'
    if pinyin_clean[0] in 'bpmfdtnlgkhzcsr':
        return pinyin_clean[0]
    return 'o'

def get_final(pinyin_str):
    pinyin_str = pinyin_str.replace('ü', 'v')
    pinyin_clean = re.sub(r'\d', '', pinyin_str)
    initial = get_initial(pinyin_str)
    if initial in 'jqxyw':
        pinyin_clean = pinyin_clean.replace('v', 'u')
    if initial == 'o':
        remaining = pinyin_clean
    elif initial in 'jqxyw':
        remaining = pinyin_clean[1:] if len(pinyin_clean) > 1 else ""
    else:
        if pinyin_clean.startswith('ch'):
            remaining = pinyin_clean[2:] if len(pinyin_clean) > 2 else ""
        elif pinyin_clean.startswith('sh'):
            remaining = pinyin_clean[2:] if len(pinyin_clean) > 2 else ""
        elif pinyin_clean.startswith('zh'):
            remaining = pinyin_clean[2:] if len(pinyin_clean) > 2 else ""
        else:
            remaining = pinyin_clean[1:] if len(pinyin_clean) > 1 else ""
    if not remaining and initial == 'o':
        remaining = 'a'
    matched_final = ""
    result = ""
    final_items = sorted(final_dict.items(), key=lambda x: max(len(p) for p in x[1]), reverse=True)
    for final_code, patterns in final_items:
        for pattern in patterns:
            if remaining == pattern or remaining.startswith(pattern):
                if len(pattern) > len(matched_final):
                    matched_final, result = pattern, final_code
    return result if matched_final else ""

def get_tone(pinyin_str):
    tone_match = re.search(r'\d', pinyin_str)
    if tone_match:
        tone_num = int(tone_match.group())
        return '0' if tone_num == 5 else str(tone_num)
    return '0'

def hanzi_to_abc(hanzi):
    if hanzi in special_cases:
        return special_cases[hanzi]
    pinyin_list = pinyin(hanzi, style=Style.TONE3, heteronym=True)
    abc_codes = []
    for pinyin_variants in pinyin_list:
        for py in pinyin_variants:
            if not py:
                continue
            py_with_tone = py
            if py.endswith('5'):
                py_with_tone = py[:-1] + '0'
            a_code = get_initial(py_with_tone)
            b_code = get_final(py_with_tone)
            c_code = get_tone(py_with_tone)
            if a_code and b_code and c_code:
                abc_code = f"{a_code}{b_code}{c_code}"
                if abc_code not in abc_codes:
                    abc_codes.append(abc_code)
    return abc_codes if abc_codes else []

#音码生成到此为止

def ensure_data_file():
    DATA_FILE = "dictionary.txt"
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8'):  
            pass
        print(f"已创建词典文件: {DATA_FILE}")

def load_dictionary():
    dictionary_set = set()#原条目中所有汉字的音码元组
    full_dictionary = {}#按音区分类的所有条目
    if os.path.exists("dictionary.txt"):
        with open("dictionary.txt", 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        hanzi, full_code = parts[0], parts[1]
                        abc_prefix = full_code[:3] if len(full_code) >= 3 else full_code
                        dictionary_set.add((hanzi, abc_prefix))
                        if abc_prefix not in full_dictionary:
                            full_dictionary[abc_prefix] = []
                        full_dictionary[abc_prefix].append((hanzi, full_code))
    return dictionary_set, full_dictionary

#前期准备到此为止

def generate_pending_list(hanzi_string):#待录入列表
    existing_dict, full_dict = load_dictionary()
    pending_list = []    
    for hanzi in hanzi_string:
        abc_codes = hanzi_to_abc(hanzi)
        if not abc_codes:
            pending_list.append((hanzi, 'bb0'))#空码码区
            continue
        missing_codes = []#每个汉字的待录入列表
        all_exist = True
        for abc_code in abc_codes:
            if (hanzi, abc_code) not in existing_dict:
                missing_codes.append(abc_code)
                all_exist = False
        if all_exist:
            pending_list.append((hanzi, ''))
        else:
            for abc_code in missing_codes:
                pending_list.append((hanzi, abc_code))
    return pending_list, len(pending_list), full_dict

def handle_conflict(han_zi, abc_code, check_list, full_code, modified_entries):#重码递归
    conflict_found = False
    conflict_hanzi = ""
    conflict_full_code = ""
    for entry in check_list:
        if entry[1] == full_code and entry[0] != han_zi:
            conflict_found = True
            conflict_hanzi = entry[0]
            conflict_full_code = entry[1]
            break
    if not conflict_found:
        return full_code, modified_entries
    print(f"{han_zi}与{conflict_hanzi}重码")
    new_conflict_full_code =abc_code+input(f"{conflict_hanzi}{abc_code} 形码改: ")
    new_check_list = [entry for entry in check_list if not (entry[0] == conflict_hanzi and entry[1] == conflict_full_code)]
    new_conflict_in_list = any(entry[1] == new_conflict_full_code for entry in new_check_list)
    if new_conflict_in_list:
        new_conflict_full_code, modified_entries = handle_conflict(
            conflict_hanzi, abc_code, new_check_list, new_conflict_full_code, modified_entries
        )
    modified_entries.append((conflict_hanzi, new_conflict_full_code))
    new_full_code = abc_code+input(f"{han_zi}{abc_code} 形码改: ")
    final_check_list = [entry for entry in new_check_list]
    final_check_list.append((conflict_hanzi, new_conflict_full_code))
    new_in_list = any(entry[1] == new_full_code for entry in final_check_list)
    if new_in_list:
        new_full_code, modified_entries = handle_conflict(
            han_zi, abc_code, final_check_list, new_full_code, modified_entries
        )
    abc_to_entries = {}
    for entry in modified_entries:
        key = (entry[0], entry[1][:3])
        abc_to_entries[key] = entry
    cleaned_modified_entries = list(abc_to_entries.values())
    return new_full_code, cleaned_modified_entries

def batch_add_entries():  # 核心
    while True:
        user_input = input("连续汉字: ").strip()
        if not user_input:
            return
        all_non_chinese = True
        chinese_input = ''
        for char in user_input:
            if '\u3400' <= char <= '\u9fff' or 0x20000 <= ord(char) <= 0x33479 or '\uf900' <= char <= '\ufad9':
                chinese_input += char
                all_non_chinese = False
        if all_non_chinese:
            print("全非中文,请重新输入:")
            continue
        break
    pending_list, count, full_dict = generate_pending_list(chinese_input)
    # 待录入列表,待录入列表长度，按音区分类的所有条目
    new_entries = []  # 新添加条目
    modified_entries = []  # 修改条目
    hanzi_abc_map = {}  # 待录入列表中汉字与其音码组成的字典
    for hanzi, abc_code in pending_list:
        if abc_code:
            if hanzi not in hanzi_abc_map:
                hanzi_abc_map[hanzi] = []
            if abc_code not in hanzi_abc_map[hanzi]:
                hanzi_abc_map[hanzi].append(abc_code)
    i = 0  # 控制while循环
    while i < count:
        hanzi, abc_code = pending_list[i]
        if abc_code:
            current_abc_list = hanzi_abc_map[hanzi]
            index = current_abc_list.index(abc_code)
            if abc_code == current_abc_list[0]:
                print(f"========{hanzi}========")
            position = f"{index + 1}/{len(current_abc_list)}"
            print(f"{position}", end="")
            existing_entries = []  # 当前音码既有条目
            if abc_code in full_dict:
                for entry in full_dict[abc_code]:
                    existing_entries.append(entry)
            if existing_entries:
                print("存在")
                for entry_hanzi, entry_code in existing_entries:
                    print(f"***{entry_hanzi} {entry_code}***")
            else:
                print("暂无")
            d_code_input = input(f"{hanzi}{abc_code} 形码: ")
            if d_code_input == "a":
                i += 1
                new_entries.append((hanzi,abc_code))#清零
                print(f"跳过{abc_code}")
                continue
            elif d_code_input == "e":
                i -= 1
                if i == -1:
                    return
                else:
                    hanzi, abc_code = pending_list[i]
                    print(f"返回{hanzi}{abc_code}")
                    continue
            full_code = abc_code + d_code_input
            check_list = []  # 重码检查列表
            for entry in new_entries:
                if entry[1][:3] == abc_code:
                    check_list.append(entry)
            for entry in modified_entries:
                if entry[1][:3] == abc_code:
                    check_list.append(entry)
            for entry_hanzi, entry_code in existing_entries:
                modified = False
                for mod_entry in modified_entries:
                    if mod_entry[0] == entry_hanzi and mod_entry[1][:3] == abc_code:
                        modified = True
                        break
                if not modified:
                    check_list.append((entry_hanzi, entry_code))
            is_conflict = any(entry[1] == full_code and entry[0] != hanzi for entry in check_list)
            if is_conflict:
                full_code, modified_entries = handle_conflict(
                    hanzi, abc_code, check_list, full_code, modified_entries
                )
            print(hanzi, full_code)
            new_entries.append((hanzi, full_code))
        else:
            print(f"========{hanzi}========")
            print(f"{hanzi} 已编码完毕")
        i += 1
    abc_to_entries_dict = {}
    for entry in new_entries:
        abc_part = entry[1][:3] if len(entry[1]) >= 3 else entry[1]
        key = (entry[0], abc_part)
        abc_to_entries_dict[key] = entry
    new_entries = list(abc_to_entries_dict.values())
    original_entries = []
    if os.path.exists("dictionary.txt"):
        with open("dictionary.txt", 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        original_entries.append((parts[0], parts[1]))
    modified_map = {}
    for hanzi, full_code in modified_entries:
        abc_prefix = full_code[:3]
        modified_map[(hanzi, abc_prefix)] = full_code
    final_entries = []
    for hanzi, full_code in original_entries:
        abc_prefix = full_code[:3] if len(full_code) >= 3 else full_code
        key = (hanzi, abc_prefix)
        if key not in modified_map:  
            final_entries.append((hanzi, full_code))
    for key, full_code in modified_map.items():
        hanzi = key[0]
        final_entries.append((hanzi, full_code))
    for hanzi, full_code in new_entries:
        final_entries.append((hanzi, full_code))
    temp_file = "dictionary_temp.txt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        for hanzi, full_code in final_entries:
            f.write(f"{hanzi} {full_code}\n")
    try:
        single_count=process_file(temp_file, "dictionary.txt")
        print(f"完成！汉字条目：{single_count}")
        os.remove(temp_file)
    except ImportError:
        import subprocess
        subprocess.run(["python", "vgli.py"])
        if os.path.exists(temp_file):
            os.remove(temp_file)
def add_entry(char, code):
    """添加条目，已添加重码处理"""
    if len(code) < 3:
        print(f"编码 '{code}' 过短，至少需要3位")
        return None
    
    abc_code = code[:3] 
    d_code = code[3:] if len(code) > 3 else ""  
    
    _, full_dict = load_dictionary()
    
    check_list = []
    modified_entries = []
    
    if abc_code in full_dict:
        for entry_hanzi, entry_code in full_dict[abc_code]:
            check_list.append((entry_hanzi, entry_code))
    
    conflict_found = False
    conflict_hanzi = ""
    for entry_hanzi, entry_code in check_list:
        if entry_code == code and entry_hanzi != char:
            conflict_found = True
            conflict_hanzi = entry_hanzi
            break
    
    if conflict_found:
        print(f"编码 '{code}' 已分配给 '{conflict_hanzi}'")
        print("请处理重码冲突:")
        temp_check_list = [entry for entry in check_list if not (entry[0] == conflict_hanzi and entry[1] == code)]
        new_conflict_code = abc_code + input(f"为 '{conflict_hanzi}' 输入新的形码: ")
        new_conflict_in_list = any(entry[1] == new_conflict_code for entry in temp_check_list)
        if new_conflict_in_list:
            print(f"新编码 '{new_conflict_code}' 仍与其他条目冲突，请继续处理")
            new_conflict_code = abc_code + input(f"为 '{conflict_hanzi}' 输入另一个新的形码: ")
        modified_entries.append((conflict_hanzi, new_conflict_code))
        new_code = abc_code + input(f"为 '{char}' 输入新的形码: ")
        temp_check_list.append((conflict_hanzi, new_conflict_code))
        new_in_list = any(entry[1] == new_code for entry in temp_check_list)
        if new_in_list:
            print(f"新编码 '{new_code}' 仍与其他条目冲突")
            new_code = abc_code + input(f"为 '{char}' 输入另一个新的形码: ")
        
        code = new_code
    entries = []
    if os.path.exists("dictionary.txt"):
        with open("dictionary.txt", 'r', encoding='utf-8') as f:
            entries = f.readlines()
    for hanzi, full_code in modified_entries:
        entries = [entry for entry in entries if not (entry.strip().startswith(f"{hanzi} ") and entry.strip().endswith(f"{full_code}"))]
    
    new_entry = f"{char} {code}\n"
    entries.append(new_entry)
    
    with open("dictionary.txt", 'w', encoding='utf-8') as f:
        f.writelines(entries)
    for hanzi, full_code in modified_entries:
        entries.append(f"{hanzi} {full_code}\n")
    with open("dictionary.txt", 'w', encoding='utf-8') as f:
        f.writelines(entries)
    process_file("dictionary.txt", "dictionary.txt")
    
    return f"{char} {code}"

def update_or_delete_by_code(old_code, new_code):
    entries = []
    old_code_exists = False
    old_code_hanzis = []
    
    if os.path.exists("dictionary.txt"):
        with open("dictionary.txt", 'r', encoding='utf-8') as f:
            entries = f.readlines()
    for entry in entries:
        parts = entry.strip().split(' ', 1)
        if len(parts) == 2 and parts[1] == old_code:
            old_code_exists = True
            old_code_hanzis.append(parts[0])
    
    if not old_code_exists:
        print(f"编码 '{old_code}' 不存在")
        return f"编码 '{old_code}' 不存在"
    if new_code == 'x':
        new_entries = []
        for entry in entries:
            parts = entry.strip().split(' ', 1)
            if len(parts) == 2 and parts[1] == old_code:
                print(f"找到并删除: {entry.strip()}")
            else:
                new_entries.append(entry)
        
        with open("dictionary.txt", 'w', encoding='utf-8') as f:
            f.writelines(new_entries)
        process_file("dictionary.txt", "dictionary.txt")
        return f"已删除编码 '{old_code}' 的所有条目"
    if len(new_code) < 3:
        print(f"新编码 '{new_code}' 过短，至少需要3位")
        return "操作失败：编码过短"
    
    abc_code = new_code[:3]
    _, full_dict = load_dictionary()
    check_list = []
    if abc_code in full_dict:
        for entry_hanzi, entry_code in full_dict[abc_code]:
            if entry_code != old_code:  
                check_list.append((entry_hanzi, entry_code))
    conflict_found = False
    conflict_hanzi = ""
    for entry_hanzi, entry_code in check_list:
        if entry_code == new_code:
            conflict_found = True
            conflict_hanzi = entry_hanzi
            break
    if conflict_found:
        print(f"新编码 '{new_code}' 已分配给 '{conflict_hanzi}'")
        print("请处理重码冲突:")
        new_conflict_code = abc_code + input(f"为 '{conflict_hanzi}' 输入新的形码: ")
        temp_check_list = [entry for entry in check_list if not (entry[0] == conflict_hanzi and entry[1] == new_code)]
        new_conflict_in_list = any(entry[1] == new_conflict_code for entry in temp_check_list)
        if new_conflict_in_list:
            new_conflict_code = abc_code + input(f"为 '{conflict_hanzi}' 输入另一个新的形码: ")
        new_entries = []
        for entry in entries:
            parts = entry.strip().split(' ', 1)
            if len(parts) == 2 and parts[0] == conflict_hanzi and parts[1] == new_code:
                new_entries.append(f"{conflict_hanzi} {new_conflict_code}\n")
            else:
                new_entries.append(entry)
        updated = False
        final_entries = []
        for entry in new_entries:
            parts = entry.strip().split(' ', 1)
            if len(parts) == 2 and parts[1] == old_code:
                final_entries.append(f"{parts[0]} {new_code}\n")
                updated = True
            else:
                final_entries.append(entry)
        
        if not updated:
            print(f"未找到编码 '{old_code}' 对应的条目")
            return "操作失败"
        with open("dictionary.txt", 'w', encoding='utf-8') as f:
            f.writelines(final_entries)
        process_file("dictionary.txt", "dictionary.txt")
        return f"操作成功，已解决重码冲突"
    new_entries = []
    updated = False
    for entry in entries:
        parts = entry.strip().split(' ', 1)
        if len(parts) == 2 and parts[1] == old_code:
            new_entries.append(f"{parts[0]} {new_code}\n")
            updated = True
            print(f"将{entry.strip()}更新为{new_code}")
        else:
            new_entries.append(entry)
    
    if not updated:
        char = input(f"未找到编码 '{old_code}'，请输入要添加的汉字: ").strip()
        if not char:
            print("汉字不能为空")
            return "操作取消"
        
        new_entries.append(f"{char} {new_code}\n")
    
    with open("dictionary.txt", 'w', encoding='utf-8') as f:
        f.writelines(new_entries)
    process_file("dictionary.txt", "dictionary.txt")
    
    return f"操作成功"

def single_add_entry():
    char = input("汉字: ").strip()
    if not char:
        print("汉字不能为空")
        return
    
    code = input("编码: ").strip()
    if not code:
        print("编码不能为空")
        return
    if len(code) < 3:
        print("编码至少需要3位")
        return
    
    result = add_entry(char, code)
    if result:
        print(f"添加成功: {result}")
    else:
        print("添加失败")

def modify_entry():
    """编辑修改条目，已添加重码检查"""
    old_code = input("要修改的编码: ").strip()
    if not old_code:
        print("编码不能为空")
        return
    
    if len(old_code) < 3:
        print("编码至少需要3位")
        return
    
    new_code = input("新编码（x删除）: ").strip()
    if not new_code:
        print("新编码不能为空")
        return
    
    if old_code == new_code:
        print("编码相同，无需修改")
        return
    
    result = update_or_delete_by_code(old_code, new_code)
    print(result)

def run_input_method():
    """启动输入法"""
    print("启动解书音形...")
    try:
        subprocess.run([sys.executable, "输入法6.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"启动输入法失败: {e}")
    except FileNotFoundError:
        print("错误：未找到 输入法6.py 文件")
    except Exception as e:
        print(f"启动输入法时发生未知错误: {e}")

def show_menu():
    print("解书音形 - 管理程序")
    print("1.批量录入 ",end="")
    print("2.添加单字 ",end="")
    print("3.编辑修改 ")
    print("4.分析音区 ",end="")
    print("5.整理码表 ",end="")
    print("6.启动输入 ")
    print("7.查询字码 ",end="")
    print("8.添加词语 ",end="")
    print("9.猜测编码")

def main():
    ensure_data_file()
    while True:
        show_menu()
        try:
            choice = input("选项: ").strip()
            if choice == '1':
                batch_add_entries()
            elif choice == '2':
                single_add_entry()
            elif choice == '3':
                modify_entry()
            elif choice == '4':
                interactive_mode()
            elif choice == '5':
                single,phrase=main_menu()
                print(f"整理完成！码表条目：{single}+{phrase} ")
            elif choice == '6':
                run_input_method()
            elif choice == '7':
                while True:
                    a=input("连续汉字：")
                    if a=="":
                        break
                    b, missing = query_chars(a)
                    print(b)
                    if missing:
                        print(f"未录入汉字：{''.join(missing)}")
            elif choice == '8':
                ciyumain()
                a=sort_file_by_second_part("ciyu.txt", "ciyu.txt")
                print(f"完成！词语条目：{a}")
            elif choice == '9':
                bmmamain()
            elif choice == '':
                print("感谢使用，再见！")
                break
            else:
                print("无效选项，请重新选择")
            print()
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"程序运行出错: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序启动出错: {str(e)}")
