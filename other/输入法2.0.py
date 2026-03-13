import tkinter as tk
import os

DATA_FILE = "dictionary.txt"
table1 = "1234567890qwertyuiopasdfghjklzxcvbnm;'."
table2 = "1234567890qwertyuiopasdfghjklzxcvbnm;'.-= "

# Global variables for navigation
current_page = 0
current_part_index = -1  # 初始化为-1，表示未进入部分选择模式
current_query_type = ""  # "single" or "multi_part"
current_split_parts = []
previous_input = ""
in_part_selection = False  # 标记是否已进入部分选择模式
skip_reset_flag = False  # 修复-=切换问题的标志

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

def query_by_prefix(prefix, start_idx=0, count=5):
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
    
    # Apply pagination
    end_idx = start_idx + count
    return results[start_idx:end_idx]

def process_input(input_text):
    result = ""
    for char in input_text:
        if char in table1:
            result += char
    return result

def replace_content(original, processed):
    output = ""
    
    for char in original:
        if char not in table2:
            output += char
    output += processed
    entry_box.delete(0, tk.END)  
    entry_box.insert(0, output)  

def split_sequence(original):
    parts = original.split("'")
    can_split_more = True
    while can_split_more:
        can_split_more = False
        new_parts = []
        for part in parts:
            condition1 = False
            condition2 = False
            positions = []
            
            if not any(char.isdigit() for char in part) and len(part) > 2:
                condition1 = True
                
            for index, char in enumerate(part):
                if char.isdigit() and index > 2 and not part[index-1].isdigit():
                    condition2 = True
                    positions.append(index)
                    
            if condition1:
                new_part = "'".join([part[i:i+2] for i in range(0, len(part), 2)])
                new_parts.extend(new_part.split("'"))
                can_split_more = True
            elif condition2:
                new_part = part
                for pos in sorted(positions, reverse=True):
                    new_part = new_part[:pos-2] + "'" + new_part[pos-2:]
                new_parts.extend(new_part.split("'"))
                can_split_more = True
            else:
                new_parts.append(part)
        parts = new_parts
        
    parts = [part for part in parts if part != '']
    merged = ""
    for part in parts:
        merged = merged + part + "'"
    merged = merged[:-1]
    return merged

def query_single_char(split_text, start_idx=0, count=5):
    candidates = query_by_prefix(split_text, start_idx, count)
    if candidates:
        candidate_str = "/".join(candidates)
        return candidate_str
    else:
        return ""

def query_multi_chars(split_text):
    char_codes = split_text.split("'")
    first_chars = ''
    for code in char_codes:
        candidates = query_by_prefix(code)
        if candidates:
            first_char = candidates[0][0]
            first_chars += first_char
    return first_chars

def clear_display_if_no_code(input_text):
    should_clear = True
    for char in input_text:
        if char in table1:
            should_clear = False
    if should_clear:
        first_chars_label.config(text='')
        current_part_label.config(text='')
        page_label.config(text='')

def navigate_parts(direction):
    global current_part_index, current_page, in_part_selection
    
    if current_query_type != "multi_part" or not current_split_parts:
        return
        
    # 如果尚未进入部分选择模式，第一次按键时进入
    if not in_part_selection:
        in_part_selection = True
        if direction == "next":
            current_part_index = 0
        elif direction == "prev":
            current_part_index = len(current_split_parts) - 1
    else:
        if direction == "next":
            current_part_index = (current_part_index + 1) % len(current_split_parts)
        elif direction == "prev":
            current_part_index = (current_part_index - 1) % len(current_split_parts)
    
    current_page = 0  # Reset page when navigating parts
    update_display()

def navigate_pages(direction):
    global current_page
    
    # 检查是否可以向下翻页
    if direction == "down":
        # 查询下一页是否有内容
        input_text = real_time_var.get()
        processed = process_input(input_text)
        split_text = split_sequence(processed)
        
        if current_query_type == "single":
            next_page_candidates = query_single_char(split_text, (current_page + 1) * 5, 5)
            if next_page_candidates:  # 只有下一页有内容时才翻页
                current_page += 1
        elif current_query_type == "multi_part" and current_split_parts and current_part_index >= 0:
            part = current_split_parts[current_part_index]
            next_page_candidates = query_single_char(part, (current_page + 1) * 5, 5)
            if next_page_candidates:  # 只有下一页有内容时才翻页
                current_page += 1
    elif direction == "up" and current_page > 0:
        current_page -= 1
        
    update_display()

def update_display():
    global current_part_index, current_page, current_query_type, current_split_parts, in_part_selection
    
    input_text = real_time_var.get()
    processed = process_input(input_text)
    split_text = split_sequence(processed)
    
    # 清空所有标签
    first_chars_label.config(text='')
    current_part_label.config(text='')
    page_label.config(text='')
    
    if current_query_type == "multi_part" and current_split_parts:
        # 始终显示首字符（第一行）
        first_chars = query_multi_chars(split_text)
        if first_chars:
            first_chars_label.config(text=first_chars)
        
        if in_part_selection and current_part_index >= 0 and current_part_index < len(current_split_parts):
            # 显示当前部分的单字候选（第二行）
            part = current_split_parts[current_part_index]
            candidates = query_single_char(part, current_page * 5, 5)
            if candidates:
                current_part_label.config(text=candidates)
                # 显示当前部分和页数信息（第三行）
                page_label.config(text=f"字 {current_part_index + 1}/{len(current_split_parts)} 页 {current_page + 1}")
    elif current_query_type == "single":
        # 显示单字查询结果（第二行）
        candidates = query_single_char(split_text, current_page * 5, 5)
        if candidates:
            current_part_label.config(text=candidates)
            # 显示页数信息（第三行）
            page_label.config(text=f"页 {current_page + 1}")

def handle_special_keys(input_text):
    """处理特殊按键（-=）并返回处理后的文本和是否跳过的标志"""
    global skip_reset_flag
    
    # 检查输入框中是否包含-=符号
    if '=' in input_text or '-' in input_text:
        # 获取当前光标位置
        cursor_pos = entry_box.index(tk.INSERT)
        
        # 检查是否在multi_part模式下
        if current_query_type == "multi_part" and current_split_parts:
            # 查找-=符号的位置
            equals_pos = input_text.find('=')
            minus_pos = input_text.find('-')
            
            # 处理=符号
            if equals_pos != -1:
                skip_reset_flag = True
                navigate_parts("next")
                # 删除=符号
                new_text = input_text[:equals_pos] + input_text[equals_pos+1:]
                # 调整光标位置
                if cursor_pos > equals_pos:
                    new_cursor_pos = cursor_pos - 1
                else:
                    new_cursor_pos = cursor_pos
                return new_text, new_cursor_pos, True
            
            # 处理-符号
            if minus_pos != -1:
                skip_reset_flag = True
                navigate_parts("prev")
                # 删除-符号
                new_text = input_text[:minus_pos] + input_text[minus_pos+1:]
                # 调整光标位置
                if cursor_pos > minus_pos:
                    new_cursor_pos = cursor_pos - 1
                else:
                    new_cursor_pos = cursor_pos
                return new_text, new_cursor_pos, True
    
    return input_text, None, False

def main_function(*args):
    global current_page, current_part_index, current_query_type, current_split_parts, previous_input, in_part_selection, skip_reset_flag
    
    input_text = real_time_var.get()
    
    # 处理特殊按键（-=）
    processed_text, new_cursor_pos, key_processed = handle_special_keys(input_text)
    if key_processed:
        # 更新输入框内容
        entry_box.delete(0, tk.END)
        entry_box.insert(0, processed_text)
        # 恢复光标位置
        if new_cursor_pos is not None:
            entry_box.icursor(new_cursor_pos)
        # 更新输入文本变量
        real_time_var.set(processed_text)
        return
    
    # 修复-=切换问题：如果设置了跳过重置标志，则不重置状态
    if not skip_reset_flag and input_text != previous_input:
        current_page = 0
        current_part_index = -1
        current_query_type = ""
        current_split_parts = []
        in_part_selection = False
    
    skip_reset_flag = False  # 重置标志
    
    processed = process_input(input_text)
    split_text = split_sequence(processed)
    
    output_text = ''
    candidates = ''
    first_chars = ''
    
    if split_text != "" and ' ' not in split_text:
        if "'" not in split_text:
            # Single character query
            current_query_type = "single"
            candidates = query_single_char(split_text, current_page * 5, 5)
            update_display()
            
            if candidates != '':
                if "/" in candidates:
                    output_text = candidates.split("/")[0][0]
                else:
                    output_text = candidates[0]
        else:
            # Multi-character query
            current_query_type = "multi_part"
            current_split_parts = split_text.split("'")
            first_chars = query_multi_chars(split_text)
            
            update_display()
            output_text = first_chars
    
    if input_text == "":
        first_chars_label.config(text='')
        current_part_label.config(text='')
        page_label.config(text='')
        current_query_type = ""
        current_split_parts = []
        in_part_selection = False
    
    # 修改上屏逻辑：采用ceui.py中的简单逻辑
    if " " in input_text:
        # 直接使用output_text替换输入内容
        replace_content(input_text, output_text)
        
        # 清空显示和重置状态
        first_chars_label.config(text='')
        current_part_label.config(text='')
        page_label.config(text='')
        current_page = 0
        current_part_index = -1
        current_query_type = ""
        current_split_parts = []
        in_part_selection = False
    
    if "-" in input_text or "=" in input_text:
        replace_content(input_text, processed)
    
    clear_display_if_no_code(input_text)
    previous_input = input_text

def on_key_press(event):
    if event.keysym == "Down":
        navigate_pages("down")
    elif event.keysym == "Up":
        navigate_pages("up")

# Create UI with improved aesthetics
window = tk.Tk()
window.title("纪释析义输入法")
window.geometry("500x200")  # 设置窗口大小
window.configure(bg='#f0f0f0')  # 设置背景色

# 设置样式
font_medium = ("Microsoft YaHei", 12)
font_small = ("Microsoft YaHei", 10)
bg_color = '#f0f0f0'
label_bg = '#e8e8e8'

real_time_var = tk.StringVar()
real_time_var.trace("w", main_function)

# 创建主框架
main_frame = tk.Frame(window, bg=bg_color, padx=10, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# 输入框
entry_box = tk.Entry(main_frame, textvariable=real_time_var, font=font_medium, width=40, 
                    relief=tk.FLAT, bg='white', highlightthickness=1, highlightcolor='#4a86e8')
entry_box.pack(pady=(0, 10))
entry_box.focus_set()
entry_box.bind("<KeyPress>", on_key_press)

# 创建显示区域框架
display_frame = tk.Frame(main_frame, bg=bg_color)
display_frame.pack(fill=tk.X)

# 第一行：显示多字输入时的首字
first_chars_label = tk.Label(display_frame, text="", font=font_medium, bg=label_bg, 
                            relief=tk.RAISED, bd=1, padx=10, pady=5, width=40, anchor='w')
first_chars_label.pack(fill=tk.X, pady=(0, 5))

# 第二行：显示当前字符（单字候选或当前部分的候选）
current_part_label = tk.Label(display_frame, text="", font=font_medium, bg=label_bg, 
                             relief=tk.RAISED, bd=1, padx=10, pady=5, width=40, anchor='w')
current_part_label.pack(fill=tk.X, pady=(0, 5))

# 第三行：显示页数或部分信息
page_label = tk.Label(display_frame, text="", font=font_small, bg=bg_color, 
                     fg='#666666', padx=10, pady=2)
page_label.pack(fill=tk.X)

# 底部信息栏
bottom_frame = tk.Frame(main_frame, bg=bg_color)
bottom_frame.pack(fill=tk.X, pady=(10, 0))

entry_count_label = tk.Label(bottom_frame, text=f"词典条目数: {get_entry_count()}", 
                            font=font_small, bg=bg_color, fg='#666666')
entry_count_label.pack(side=tk.LEFT)

# 添加使用提示
hint_label = tk.Label(bottom_frame, text="使用↑↓翻页，-=切换部分", 
                     font=font_small, bg=bg_color, fg='#999999')
hint_label.pack(side=tk.RIGHT)

window.mainloop()
