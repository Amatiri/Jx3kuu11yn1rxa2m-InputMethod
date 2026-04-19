import os
from config import DATA_FILE, CIYU_FILE


def ensure_data_file():
    """确保词典文件存在，若不存在则创建空文件"""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8'):
            pass


def query_phrase(code):
    """从词库文件 ciyu.txt 中查询短语"""
    try:
        with open(CIYU_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(" ")
                if len(parts) >= 2 and code in parts[1:]:
                    return "(" + parts[0] + ")"
    except FileNotFoundError:
        pass
    return ""


def get_entry_count():
    """返回词典文件中的词条总数"""
    ensure_data_file()
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    return 0


def query_by_prefix(prefix, start_idx=0, count=5):
    """根据编码前缀查询候选词。支持副码a和补码规则"""
    ensure_data_file()
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        return []
    results = []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(' ', 1)
            if len(parts) == 2:
                word = parts[0]
                code = parts[1]
                # 处理特殊规则：前缀长度>=5且副码为a
                if len(prefix) >= 5 and prefix[4] == 'a':
                    if len(prefix) == 5 and code == prefix[:4]:
                        results.append(f"{word}")
                    elif len(code) >= 5 and code.startswith(prefix[:4]):
                        if code[4:].startswith(prefix[5:]) and code[4] == ".":
                            rest = code[len(prefix)-1:]
                            results.append(f"{word}{rest}")
                elif code.startswith(prefix):
                    # 处理补码
                    if "." in code[:6]:
                        if '.' in prefix:
                            rest = code[len(prefix):]
                            results.append(f"{word}{rest}")
                        elif (len(code) > 5 and "." == code[5]) or (len(prefix) == 4 and prefix[3].isdigit()):
                            code_before_dot = code.split('.')[0]
                            if prefix == code_before_dot:
                                rest = code[len(prefix):]
                                results.append(f"{word}{rest}")
                    else:
                        rest = code[len(prefix):]
                        results.append(f"{word}{rest}")
    return results[start_idx:start_idx + count]


def query_by_char(char):
    """根据汉字查询其编码"""
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
    goly = ""
    for char in chars_string:
        if '\u3400' <= char <= '\u9fff' or 0x20000 <= ord(char) <= 0x33479 or '\uf900' <= char <= '\ufad9':
            goly += char
    for char in goly:
        codes = query_by_char(char)
        if codes:
            result_parts.append('/'.join(codes))
        else:
            result_parts.append("--")
            missing_chars.append(char)
    return ' '.join(result_parts), missing_chars


def load_dictionary():
    """加载词典，返回 (汉字音码集合, 按音区分组的完整词典)"""
    dictionary_set = set()
    full_dictionary = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
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
