import re
from pypinyin import pinyin, Style

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
    pinyin_str = pinyin_str.replace('\u00fc', 'v')
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
