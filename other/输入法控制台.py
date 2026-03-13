import os

# 定义必要的函数和变量
DATA_FILE = "dictionary.txt"

def check_second_char(char):
    special_chars = "acegijmnopqrsuvwxyz;"
    return char in special_chars

def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8'):  
            pass                   

def get_entry_count():
    ensure_data_file()
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    return 0

def query_by_prefix(prefix):
    ensure_data_file()
    
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        return []
    
    results = []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(' ', 1)
            if len(parts) == 2:
                code = parts[1]
                
                if len(prefix) >= 5 and prefix[4] == 'a':
                    if code.startswith(prefix):
                        rest = code[len(prefix):]
                        results.append(f"{parts[0]}{rest}")
                    elif len(code) >= 4 and code.startswith(prefix[:4]) and (len(code) == 4 or code[4] in ['.', 'a']) and code[4:].startswith(prefix[5:]):
                        rest = code[len(prefix)-1:]
                        results.append(f"{parts[0]}{rest}")
                    elif len(code) >= 5 and code.startswith(prefix[:4]) and code[4] == '.' and code[5:].startswith(prefix[5:]):
                        rest = code[len(prefix):]  
                        results.append(f"{parts[0]}{rest}")
                else:
                    if code.startswith(prefix):
                        rest = code[len(prefix):]
                        results.append(f"{parts[0]}{rest}")
    
    return results

def ffkl(yr2):
    # 初始分割
    parts = yr2.split("'")
    changed = True
    while changed:
        changed = False
        new_parts = []
        for part in parts:
            # 检查这个part是否需要处理：tc1, tc2
            tc1 = False
            tc2 = False
            wzvi = []

            # 检查条件：pjdr函数
            # 如果part不含数字且长度大于2，则tc1为True
            if not any(char.isdigit() for char in part) and len(part) > 2:
                tc1 = True
            # 遍历part的每个字符，检查数字位置
            for idx, char in enumerate(part):
                if char.isdigit():
                    # 检查前一位不是数字且索引大于2
                    if idx > 0 and not part[idx-1].isdigit() and idx > 2:
                        tc2 = True
                        wzvi.append(idx)

            # 根据条件进行处理
            if tc1:
                # 每两个字符分组并用单引号连接
                new_part = "'".join([part[i:i+2] for i in range(0, len(part), 2)])
                new_parts.extend(new_part.split("'"))
                changed = True
            elif tc2:
                # 从后往前插入单引号，避免索引变化
                temp_part = part
                for pos in sorted(wzvi, reverse=True):
                    temp_part = temp_part[:pos-2] + "'" + temp_part[pos-2:]
                new_parts.extend(temp_part.split("'"))
                changed = True
            else:
                new_parts.append(part)
        parts = new_parts

    # 过滤空字符串
    parts = [p for p in parts if p != '']
    return parts

def main():
    print("解书音形 - 控制台版输入法")
    print("输入'a'退出程序")
    print(f"当前数据库条目数: {get_entry_count()}")
    print("-" * 50)
    
    while True:
        query_input = input("请输入解书码: ").strip()
        
        if query_input.lower() == 'a':
            print("程序已退出")
            break
            
        if not query_input:
            print("输入不能为空，请重新输入")
            continue
            
        # 使用ffkl函数处理输入
        prefixes = ffkl(query_input)
        
        if len(prefixes) > 1:
            # 多个前缀的情况
            print("首选字: ", end="")
            for prefix in prefixes:
                prefix_results = query_by_prefix(prefix)
                if prefix_results:
                    # 提取第一个汉字
                    first_char = prefix_results[0][0]
                    print(first_char, end="")
                else:
                    print("--", end="")
            print()  # 换行
        else:
            # 单个前缀的情况
            prefix = prefixes[0]
            results = query_by_prefix(prefix)
            if results:
                result_str = "/".join(results)
                print(f"候选: {result_str}")
            else:
                print("候选: --")

if __name__ == "__main__":
    main()
