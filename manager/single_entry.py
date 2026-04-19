import os
from config import DATA_FILE
from manager.dictionary import load_dictionary
from manager.file_processor import process_file


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
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            entries = f.readlines()
    for hanzi, full_code in modified_entries:
        entries = [entry for entry in entries if not (entry.strip().startswith(f"{hanzi} ") and entry.strip().endswith(f"{full_code}"))]
    new_entry = f"{char} {code}\n"
    entries.append(new_entry)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.writelines(entries)
    for hanzi, full_code in modified_entries:
        entries.append(f"{hanzi} {full_code}\n")
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.writelines(entries)
    process_file(DATA_FILE, DATA_FILE)
    return f"{char} {code}"


def update_or_delete_by_code(old_code, new_code):
    """通过编码更新或删除条目"""
    entries = []
    old_code_exists = False
    old_code_hanzis = []

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
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
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_entries)
        process_file(DATA_FILE, DATA_FILE)
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
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            f.writelines(final_entries)
        process_file(DATA_FILE, DATA_FILE)
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

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_entries)
    process_file(DATA_FILE, DATA_FILE)
    return f"操作成功"


def single_add_entry():
    """添加单字"""
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
    """编辑修改条目"""
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
