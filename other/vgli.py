import re
def char_priority(c):
    if c in '123456789.':
        return (0, c)
    elif c in '0abcdefghijklmnopqrstuvwxyz':
        return (1, c)
    elif c == ';':
        return (2, ';')
    else:
        return (3, c)

def sort_key(non_han_str):
    return tuple(char_priority(c) for c in non_han_str)

def get_abc_code(full_code):
    if len(full_code) < 3:
        return full_code
    return full_code[:3]
first_level_map = {
    '不': 'bu44',  
    '从': 'cs2r',
    '的': 'de0b', 
    '发': 'fa1k',  
    '个': 'ge41',
    '好': 'hk3n',  
    '成': 'ig2g',
    '就': 'jq4d',
    '可': 'ke3k',
    '了': 'le01',
    '们': 'mf0r',  
    '你': 'ni3r',
    '哦': 'oo4k',
    '平': 'p;25',
    '去': 'qu4t',
    '人': 'rf22',
    '所': 'so3j',
    '他': 'ta1r',
    '是': 'ui4r',
    '这': 've4z',
    '我': 'wo3g',
    '小': 'xc33',
    '有': 'yb3r',
    '在': 'zl4t'
}
def process_file(input_file, output_file):
    seen_entries = set()
    entries = []
    
    global first_level_map 
    
    entries_by_first_char = {}
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip() 
            if not line:
                continue

            parts = line.split(' ', 1)
            if len(parts) < 2:
                continue  
            
            hanzi, non_han = parts
            non_han_clean = non_han.rstrip()  

            if len(non_han_clean) <= 3:
                continue

            entry_key = f"{hanzi} {non_han_clean}"

            if entry_key not in seen_entries:
                seen_entries.add(entry_key)
                entries.append((hanzi, non_han_clean))
    
    seen_codes = set()
    code_unique_entries = []
    for hanzi, code in entries:
        if code not in seen_codes:
            seen_codes.add(code)
            code_unique_entries.append((hanzi, code))
    
    for hanzi, code in code_unique_entries:
        if code and code[0].isalpha():
            first_char = code[0]
            if first_char not in entries_by_first_char:
                entries_by_first_char[first_char] = []
            entries_by_first_char[first_char].append((hanzi, code))
    
    for first_char, entry_list in entries_by_first_char.items():
        first_level_hanzi = None
        for hanzi, target_code in first_level_map.items():
            if target_code[0] == first_char:
                first_level_hanzi = hanzi
                target_first_level_code = target_code
                break
        
        if first_level_hanzi:
            for i, (hanzi, code) in enumerate(entry_list):
                if hanzi == first_level_hanzi and code == target_first_level_code:
                    entry_list.insert(0, entry_list.pop(i))
                    break
        
        if len(entry_list) > 1:
            tail_entries = entry_list[1:]
            tail_entries.sort(key=lambda x: sort_key(x[1]))
            entry_list[1:] = tail_entries
    
    all_entries = []
    for first_char in sorted(entries_by_first_char.keys()):
        all_entries.extend(entries_by_first_char[first_char])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for hanzi, non_han in all_entries:
            f.write(f"{hanzi} {non_han}\n")


            


def sort_file_by_second_part(input_file, output_file):

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        parsed_lines = []
        for line_num, line in enumerate(lines, 1): 
            if not line.strip():  
                continue
                
            parts = line.split(' ', 1)
            if len(parts) < 2:
                print(f"警告: 第{line_num}行没有空格分隔: {line}")
                continue
                
            first_part, second_part = parts
            parsed_lines.append((first_part, second_part, line))
        
        parsed_lines.sort(key=lambda x: x[1])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for _, _, original_line in parsed_lines:
                f.write(original_line)
        
        print(f"排序完成!")
        
    except FileNotFoundError:
        print(f"错误: 找不到输入文件 '{input_file}'")
    except Exception as e:
        print(f"错误: {e}")
def merge_files_to_ahk(dictionary_file, ciyu_file, output_file):

    result_dict = {}
    
    try:
        with open(dictionary_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith(';'):
                    continue  
                
                parts = line.split()
                if len(parts) >= 2:
                    value = parts[0]  
                    key = parts[1]    
                    result_dict[key] = value
                else:
                    print(f"警告: {dictionary_file} 第{line_num}行格式不正确: {line}")
    except FileNotFoundError:
        print(f"错误: 找不到文件 {dictionary_file}")
        return
    try:
        with open(ciyu_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith(';'):
                    continue  
                
                parts = line.split()
                if len(parts) >= 2:
                    value = parts[0]  
                    key = parts[1]    
                    result_dict[key] = value
                else:
                    print(f"警告: {ciyu_file} 第{line_num}行格式不正确: {line}")
    except FileNotFoundError:
        print(f"错误: 找不到文件 {ciyu_file}")
        return
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for zi,ma in first_level_map.items():
                f.write(f':o:{ma[0]} ::{zi}"\n')
            
            for key, value in result_dict.items():
                f.write(f':o:{key} ::{value}\n')

            
            print(f"成功生成AHK文件: {output_file}")
            print(f"共生成 {len(result_dict)} 个热键")
            
    except IOError as e:
        print(f"错误: 无法写入文件 {output_file}: {e}")
def process_second_part(text):
    if '.' in text:
        text = text.split('.')[0]
    
    if len(text) < 2:
        return text.lower()
    
    daydue = ["pqwertyuio", "masdfghjkl", "zxcvbncvbn"]
    
    chars = list(text)
    
    if len(chars) >= 2 and chars[1] == ';':
        mapping = {
            'b': 'd', 'd': 'd', 'j': 'a', 'l': 'v', 'm': 'v',
            'n': 'v', 'p': 'd', 'q': 'a', 't': 'd', 'x': 'a', 'y': 'd'
        }
        first_char = chars[0].lower()
        chars[1] = mapping.get(first_char, 'a')
    
    while len(chars) < 4:
        chars.append('a')  # 这里补a更好
    
    if chars[3].isdigit(): 
        tone = chars[2]  
        d_digit = chars[3]  
        
        third_char = 'a' if tone in ['1', '2'] else 'e'
        
        if tone == '0':  
            row = 2
        elif tone in ['1', '3']:  
            row = 0
        else:  
            row = 1
        
        if d_digit.isdigit() and 0 <= int(d_digit) <= 9:
            fourth_char = daydue[row][int(d_digit)]
        else:
            fourth_char = 'a'
        
        result = chars[0] + chars[1] + third_char + fourth_char
    
    else:  
        d_letter = chars[3]
        
        has_e_code = len(chars) >= 5 and (chars[4].isalpha() or chars[4]==";")
        
        if has_e_code:
            e_code = chars[4]
            if e_code == ';':
                e_code = 'e'
            fourth_char = e_code
        else:
            tone = chars[2]
            fourth_char = 'a' if tone in ['1', '2'] else 'e'
        
        result = chars[0] + chars[1] + d_letter + fourth_char
    
    result = re.sub(r'[^a-z]', '', result)
    return result[:4]

def process_filey(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
        
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for line in lines:
                line = line.strip()
                if not line:
                    outfile.write('\n')
                    continue
                
                parts = line.split(' ', 1)
                
                if len(parts) == 2:
                    first_part = parts[0]
                    second_part = parts[1]
                    
                    processed_second = process_second_part(second_part)
                    if processed_second:
                        outfile.write(f"{first_part} {processed_second}\n")
                else:

                    outfile.write(f"{line}\n")
            for zi,ma in first_level_map.items():
                outfile.write(f'{zi} {ma[0]}\n')
        print(f"处理完成！结果已保存到 {output_file}")
        
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
    except Exception as e:
        print(f"处理文件时发生错误: {e}")
    
    
def main_menu():
    process_file("dictionary.txt", "dictionary.txt")
    sort_file_by_second_part("ciyu.txt", "ciyu.txt")
    merge_files_to_ahk("dictionary.txt", "ciyu.txt", "dictionary+t.ahk")
    process_filey("dictionary.txt", "dictionary_no_number.txt")
if __name__ == "__main__":
    main_menu()
