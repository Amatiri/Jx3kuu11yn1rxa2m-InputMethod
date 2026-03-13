import tkinter as tk
import os
import pyperclip
import keyboard
import threading
import time
DATA_FILE = "dictionary.txt"
table1 = "1234567890qwertyuiopasdfghjklzxcvbnm;'."
table2 = "1234567890qwertyuiopasdfghjklzxcvbnm;'.-= "
current_page = 0#单字翻页
current_query_type = ""  #单多输入
current_phrase = ""
current_part_index = -1  #多字字序
current_split_parts = [] #多字每字
in_part_selection = False#多字候选
previous_input = ""
selection_symbols = ["!", "@", "#", "$", "%"]
symbol_to_index = {"!": 0, "@": 1, "#": 2, "$": 3, "%": 4}
xrze="1"#自动上字
phrase_commit = "1"#优先上词
switch = False#内输/外输
window = None


def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8'):  
            pass
        
def query_phrase(code):
    try:
        with open("ciyu.txt", 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(" ")
                if len(parts) >= 2 and code in parts[1:]:
                    return "(" + parts[0] + ")"
    except FileNotFoundError:
        pass
    return ""

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
                    if len(prefix)==5 and code==prefix[:4]:#取a
                        results.append(f"{parts[0]}")
                    elif len(code) >= 5 and code.startswith(prefix[:4]):#展开F
                        if code[4:].startswith(prefix[5:]) and code[4]==".":
                            rest = code[len(prefix)-1:]
                            results.append(f"{parts[0]}{rest}")
                elif code.startswith(prefix):
                    if "." in code[:6]:
                        if '.' in prefix:
                            rest = code[len(prefix):]
                            results.append(f"{parts[0]}{rest}")
                        elif (len(code)>5 and "." == code[5]) or (len(prefix)==4 and prefix[3].isdigit()):
                            code_before_dot = code.split('.')[0]
                            if prefix == code_before_dot:
                                rest = code[len(prefix):]
                                results.append(f"{parts[0]}{rest}")
                    else:
                        rest = code[len(prefix):]
                        results.append(f"{parts[0]}{rest}")
    return results[start_idx:start_idx + count]

def process_input(input_text):
    result = ""
    start_collecting = False
    for char in input_text:
        if not start_collecting and 'a' <= char <= 'z':
            start_collecting = True
        if start_collecting and char in table1:
            result += char
    return result
 
def replace_content(original, processed, do_paste=True, reset_entry=True):
    first_letter_pos = -1
    last_letter_pos = -1
    for i, char in enumerate(original):
        if 'a' <= char <= 'z':
            first_letter_pos = i
            break
    for j, char in enumerate(original):
        if (char not in table2) and j > i:
            last_letter_pos = j
            break
    if first_letter_pos == -1:
        output = original
    elif last_letter_pos == -1:
        prefix = original[:first_letter_pos]
        output = prefix + processed
    else:
        prefix = original[:first_letter_pos]
        hbjx = original[last_letter_pos:]
        output = prefix + processed + hbjx
    output = output.strip()
    if do_paste and switch:
        paste_text(output, reset_entry)
    else:
        pyperclip.copy(output)
        entry_box.delete(0, tk.END)
        entry_box.insert(0, output)
        real_time_var.set(output)
        
def split_sequence(original):
    parts = original.split("'")
    can_split_more = True
    while can_split_more:
        can_split_more = False
        new_parts = []
        for part in parts:
            condition1 = False
            condition2 = False
            condition3 = False  
            condition4 = False  
            positions = []
            if not any(char.isdigit() for char in part) and len(part) > 2:
                condition1 = True
            for index, char in enumerate(part):
                if char.isdigit() and index > 2 and not part[index-1].isdigit():
                    condition2 = True
                    positions.append(index)
            if len(part) > 5 and '.' not in part:
                condition3 = True
            if  '.' in part and len(part.split(".")[1])>1:
                condition4 = True
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
            elif condition3:
                new_part = part[:5] + "'" + part[5:]
                new_parts.extend(new_part.split("'"))
                can_split_more = True
            elif condition4:
                ff=len(part.split(".")[0])+2
                new_part = part[:ff] + "'" + part[ff:]
                new_parts.extend(new_part.split("'"))
                can_split_more = True
            else:
                new_parts.append(part)
        parts = new_parts
    parts = [part for part in parts if part != '']
    return "'".join(parts)

def query_single_char(split_text, start_idx=0):
    candidates = query_by_prefix(split_text, start_idx)
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
        else:
            return ""
    return first_chars

def clear_display_if_no_code(input_text):
    first_letter_pos = -1
    for i, char in enumerate(input_text):
        if 'a' <= char <= 'z':
            first_letter_pos = i
            break
    if first_letter_pos == -1:
        should_clear = True
    else:
        should_clear = True
        for char in input_text[first_letter_pos:]:
            if char in table1:
                should_clear = False
                break
    if should_clear:
        first_chars_label.config(text='')
        current_part_label.config(text='')
        page_label.config(text='')

def navigate_parts(direction):
    global current_part_index, current_page, in_part_selection, current_phrase
    if current_query_type != "multi_part" or not current_split_parts:
        return
    if not in_part_selection:
        if direction == "next":
            in_part_selection = True
            current_phrase = ""  
            current_part_index = 0
    else:
        current_phrase = ""  
        if direction == "next":
            current_part_index = (current_part_index + 1) % len(current_split_parts)
        elif direction == "prev":
            current_part_index = (current_part_index - 1) % len(current_split_parts)
    current_page = 0  
    update_display()
    
def navigate_pages(direction):
    global current_page
    if direction == "down":
        input_text = real_time_var.get()
        processed = process_input(input_text)
        split_text = split_sequence(processed)
        if current_query_type == "single":
            next_page_candidates = query_single_char(split_text, (current_page + 1) * 5)
            if next_page_candidates:  
                current_page += 1
        elif current_query_type == "multi_part" and current_split_parts and current_part_index >= 0:
            part = current_split_parts[current_part_index]
            next_page_candidates = query_single_char(part, (current_page + 1) * 5)
            if next_page_candidates:  
                current_page += 1
    elif direction == "up" and current_page > 0:
        current_page -= 1
    update_display()
    
def update_display():
    global current_part_index, current_page, current_query_type, current_split_parts, in_part_selection, current_phrase
    input_text = real_time_var.get()
    processed = process_input(input_text)
    split_text = split_sequence(processed)
    current_phrase = query_phrase(processed)
    first_chars_label.config(text='')
    current_part_label.config(text='')
    page_label.config(text='')
    if current_query_type == "multi_part":
        first_chars = query_multi_chars(split_text)
        if first_chars:
            if current_phrase and not in_part_selection:  
                if first_chars == current_phrase[1:-1]:
                    first_chars_label.config(text=first_chars)
                    current_phrase=""
                else:
                    first_chars_label.config(text=first_chars +"   "+ current_phrase)
            else:
                first_chars_label.config(text=first_chars)
        elif current_phrase:
            first_chars_label.config(text=current_phrase)
        if first_chars and in_part_selection and current_part_index >= 0 and current_part_index < len(current_split_parts):
            part = current_split_parts[current_part_index]
            candidates = query_single_char(part, current_page * 5)
            if candidates:
                current_phrase=""
                current_part_label.config(text=candidates)
                page_label.config(text=f"字 {current_part_index + 1}/{len(current_split_parts)} 页 {current_page + 1}")
    elif current_query_type == "single":
        candidates = query_single_char(split_text, current_page * 5)
        if candidates:
            current_part_label.config(text=candidates)
            page_label.config(text=f"页 {current_page + 1}")

def handle_special_keys(input_text):#处理-=光标
    global current_phrase
    if '=' in input_text or '-' in input_text:
        cursor_pos = entry_box.index(tk.INSERT)
        if current_query_type == "multi_part" and current_split_parts:
            equals_pos = input_text.find('=')
            minus_pos = input_text.find('-')
            if equals_pos != -1:
                current_phrase = ""  
                navigate_parts("next")
                new_text = input_text[:equals_pos] + input_text[equals_pos+1:]
                if cursor_pos > equals_pos:
                    new_cursor_pos = cursor_pos - 1
                else:
                    new_cursor_pos = cursor_pos
                return new_text, new_cursor_pos, True
            if minus_pos != -1:
                current_phrase = "" 
                navigate_parts("prev")
                new_text = input_text[:minus_pos] + input_text[minus_pos+1:]
                if cursor_pos > minus_pos:
                    new_cursor_pos = cursor_pos - 1
                else:
                    new_cursor_pos = cursor_pos
                return new_text, new_cursor_pos, True
    return input_text, None, False

def get_current_candidates():#候选上屏时的候选获取逻辑，见下
    input_text = real_time_var.get()
    processed = process_input(input_text)
    split_text = split_sequence(processed)
    if current_query_type == "single":
        candidates = query_single_char(split_text, current_page * 5)
        if candidates:
            return candidates.split("/")
    elif current_query_type == "multi_part" and current_split_parts and current_part_index >= 0:
        part = current_split_parts[current_part_index]
        candidates = query_single_char(part, current_page * 5)
        if candidates:
            current_phrase=""
            return candidates.split("/")
    return []

def handle_selection_keys(event):#!@#$%
    global current_split_parts, current_phrase
    if event.char == "!" and current_phrase:
        phrase_content = current_phrase[1:-1]
        input_text = real_time_var.get()
        replace_content(input_text, phrase_content, do_paste=True, reset_entry=True)
        reset_input_state()
        return "break"
    if event.char in selection_symbols:
        candidates = get_current_candidates()
        if not candidates:
            return
        index = symbol_to_index.get(event.char, -1)
        if 0 <= index < len(candidates):
            selected_char = candidates[index][0]
            input_text = real_time_var.get()
            if current_query_type == "single":
                replace_content(input_text, selected_char, do_paste=True, reset_entry=True)
                reset_input_state()
            elif current_query_type == "multi_part" and current_split_parts and current_part_index >= 0:
                processed = process_input(input_text)
                split_text = split_sequence(processed)
                if "'" in split_text:
                    parts = split_text.split("'")
                    if current_part_index < len(parts):#注：由于和上屏逻辑匹配问题，只有从前到后逐个候选才能正常输入
                        new_parts = parts.copy()
                        new_parts[current_part_index] = selected_char
                        new_processed = "".join(new_parts)
                        is_last_part = current_part_index == len(parts) - 1
                        if is_last_part:
                            replace_content(input_text, new_processed, do_paste=True, reset_entry=True)
                            reset_input_state()
                        else:
                            replace_content(input_text, new_processed, do_paste=False, reset_entry=False)
                            navigate_parts("next")
        return "break"

def reset_input_state():
    global current_page, current_part_index, current_query_type, current_split_parts, in_part_selection, current_phrase
    current_page = 0
    current_part_index = -1
    current_query_type = ""
    current_split_parts = []
    in_part_selection = False
    current_phrase = ""
    first_chars_label.config(text='')
    current_part_label.config(text='')
    page_label.config(text='')

def main_function(*args):
    global current_page, current_part_index, current_query_type, current_split_parts, previous_input, in_part_selection, current_phrase
    global xrze,total
    input_text = real_time_var.get()
    processed_text, new_cursor_pos, key_processed = handle_special_keys(input_text)
    if key_processed:
        entry_box.delete(0, tk.END)
        entry_box.insert(0, processed_text)
        if new_cursor_pos is not None:
            entry_box.icursor(new_cursor_pos)
        return
    if input_text != previous_input:
        current_page = 0
        current_part_index = -1
        current_query_type = ""
        current_split_parts = []
        in_part_selection = False
        current_phrase = ""
    processed = process_input(input_text)
    split_text = split_sequence(processed)
    output_text = ''
    candidates = ''
    first_chars = ''
    if split_text != "" and ' ' not in split_text:
        if "'" not in split_text:
            current_query_type = "single"
            candidates = query_single_char(split_text, current_page * 5)
            if candidates and xrze == "1" and len(processed) > 3:
                candidates_list = candidates.split("/")
                non_dot_candidates = []
                for candidate in candidates_list:
                    code_part = candidate[1:] if len(candidate) > 1 else ""
                    if "." not in code_part:
                        non_dot_candidates.append(candidate)
                if len(non_dot_candidates) == 1:
                    selected_char = non_dot_candidates[0][0]
                    replace_content(input_text, selected_char, do_paste=True, reset_entry=True)
                    reset_input_state()
                    return
            update_display()
            if candidates != '':
                if "/" in candidates:
                    output_text = candidates.split("/")[0][0]
                else:
                    output_text = candidates[0]
        else:
            current_query_type = "multi_part"
            first_chars = query_multi_chars(split_text)
            if first_chars:
                current_split_parts = split_text.split("'")
            update_display()
            output_text = first_chars
    if input_text == "":
        first_chars_label.config(text='')
        current_part_label.config(text='')
        page_label.config(text='')
        current_query_type = ""
        current_split_parts = []
        in_part_selection = False
        current_phrase = ""
    if key_processed:
        current_phrase = ""
    if " " in input_text:
        if phrase_commit == "1" and current_query_type == "multi_part" and current_phrase:
            output_text = current_phrase[1:-1]
        elif output_text == "":
            if current_phrase:
                output_text = current_phrase[1:-1]
            else:
                output_text = processed

        replace_content(input_text, output_text, do_paste=True, reset_entry=True)
        reset_input_state()
        return
    clear_display_if_no_code(input_text)
    previous_input = input_text

def on_key_press(event):
    if event.keysym == "Down":
        navigate_pages("down")
    elif event.keysym == "Up":
        navigate_pages("up")
    else:
        result = handle_selection_keys(event)
        if result == "break":
            return "break"

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass
# ==================== 全局输入功能====================

filt = 0
total = 0

def toggle():
    global switch
    if switch:
        switch = False
        window.title("解书音形-内输")
    else:
        switch = True
        window.title("解书音形-外输") 
    entry_box.delete(0, tk.END)
def initial(event):
    global filt, total, switch
    
    if not switch:
        filt = 0
        total = 0
        return
    filt += 1
    if filt == 2:
        filt = 1
        if event.name in "qwertyuiopasdfghjklzcxvbnm" or (event.name in ";.'1234567890" and total !=0):
            total += 1
            current_text = entry_box.get()
            cursor_pos = entry_box.index(tk.INSERT)
            new_text = current_text[:cursor_pos] + event.name + current_text[cursor_pos:]
            entry_box.delete(0, tk.END)
            entry_box.insert(0, new_text)
            entry_box.icursor(cursor_pos + 1)
        elif event.name in ["-", "=", "!", "@", "#", "$", "%", "space", "up", "down", "left", "right", "backspace"] and total!=0:
            if event.name == "-":
                navigate_parts("prev")
                time.sleep(0.05)
                keyboard.press_and_release("backspace")
            elif event.name == "=":
                navigate_parts("next")
                time.sleep(0.05)
                keyboard.press_and_release("backspace")
            elif event.name == "up":
                navigate_pages("up")
            elif event.name == "down":
                navigate_pages("down")
            elif event.name == "left":
                entry_box.icursor(entry_box.index(tk.INSERT) - 1)
            elif event.name == "right":
                entry_box.icursor(entry_box.index(tk.INSERT) + 1)
            elif event.name == "backspace":
                current_text = entry_box.get()
                cursor_pos = entry_box.index(tk.INSERT)
                if cursor_pos > 0:
                    new_text = current_text[:cursor_pos-1] + current_text[cursor_pos:]
                    entry_box.delete(0, tk.END)
                    entry_box.insert(0, new_text)
                    entry_box.icursor(cursor_pos - 1)
                if total > 0:
                    total -= 1
            elif event.name in ["!", "@", "#", "$", "%", "space"]:
                total+=1
                if event.name == "space":
                    current_text = entry_box.get()
                    cursor_pos = entry_box.index(tk.INSERT)
                    new_text = current_text[:cursor_pos] + " " + current_text[cursor_pos:]
                    entry_box.delete(0, tk.END)
                    entry_box.insert(0, new_text)
                    entry_box.icursor(cursor_pos + 1)
                else:
                    char = event.name
                    event = tk.Event()
                    event.char = char
                    handle_selection_keys(event)
    if total == 0:
        entry_box.delete(0, tk.END)

def paste_text(text, reset_entry=True):
    global switch, total
    if not switch or not text:
        return
    if total!=0:
        for _ in range(total):
            keyboard.press_and_release("backspace")
    total = 0
    pyperclip.copy(text)
    keyboard.release("shift")
    time.sleep(0.05)
    keyboard.press_and_release('ctrl+v')
    if reset_entry:
        entry_box.delete(0, tk.END)
        real_time_var.set('')
    return True
def start_keyboard_listener():
    global switch,filt,total
    keyboard.add_hotkey('left+right', toggle, suppress=True)
    keyboard.on_press(initial, suppress=False)
    keyboard.wait('esc+1')
    keyboard.clear_all_hotkeys()
    switch=False
    filt=0
    total=0
    if window: 
        window.title("解书音形-仅内输")
keyboard_thread = threading.Thread(target=start_keyboard_listener, daemon=True)
keyboard_thread.start()

window = tk.Tk()
window.title("解书音形-内输") 
window.geometry("600x215+2250+1100")  
window.configure(bg='#FFF3C7')
window.attributes('-topmost', True)  
window.attributes('-alpha', 0.95)  
drag_start_x = 0
drag_start_y = 0
def start_drag(event):
    global drag_start_x, drag_start_y
    drag_start_x = event.x
    drag_start_y = event.y
def do_drag(event):
    x = window.winfo_x() + (event.x - drag_start_x)
    y = window.winfo_y() + (event.y - drag_start_y)
    window.geometry(f"+{x}+{y}")
font_medium = ("华文中宋", 13)
font_small = ("黑体", 8)
bg_color = '#FFF3C7'
label_bg = '#EFE3AE'
real_time_var = tk.StringVar()
real_time_var.trace("w", main_function)
main_frame = tk.Frame(window, bg=bg_color, padx=2, pady=0)
main_frame.pack(fill=tk.BOTH, expand=False)
entry_box = tk.Entry(main_frame, textvariable=real_time_var, font=font_medium, width=44, 
                    relief=tk.FLAT, bg='#EFE3AE', highlightthickness=1, highlightcolor='#000000')
entry_box.pack(pady=(0, 2))
entry_box.focus_set()
entry_box.bind("<KeyPress>", on_key_press)
display_frame = tk.Frame(main_frame, bg=bg_color)
display_frame.pack(fill=tk.X)
display_frame.bind("<ButtonPress-1>", start_drag)
display_frame.bind("<B1-Motion>", do_drag)
first_chars_label = tk.Label(display_frame, text="", font=font_medium, bg=label_bg, 
                            relief=tk.RAISED, bd=1, padx=2, pady=2, width=0, anchor='w')
first_chars_label.pack(fill=tk.X, pady=(0, 2))
first_chars_label.bind("<ButtonPress-1>", start_drag)
first_chars_label.bind("<B1-Motion>", do_drag)
current_part_label = tk.Label(display_frame, text="", font=font_medium, bg=label_bg, 
                             relief=tk.RAISED, bd=1, padx=2, pady=2, width=0, anchor='w')
current_part_label.pack(fill=tk.X, pady=(0, 2))
current_part_label.bind("<ButtonPress-1>", start_drag)
current_part_label.bind("<B1-Motion>", do_drag)
page_label = tk.Label(display_frame, text="", font=font_small, bg=bg_color, 
                     fg='#666666', padx=0, pady=0)
page_label.pack(fill=tk.X)
page_label.bind("<ButtonPress-1>", start_drag)
page_label.bind("<B1-Motion>", do_drag)
main_status_frame = tk.Frame(window, bg='#FFF3C7', padx=2, pady=2)
main_status_frame.pack(fill=tk.BOTH, expand=False)
settings_frame = tk.Frame(main_status_frame, bg='#FFF3C7')
settings_frame.pack(fill=tk.X, pady=(0, 2))
auto_commit_var = tk.StringVar(value=xrze)
def toggle_auto_commit():
    global xrze
    if auto_commit_var.get() == "1":
        xrze = "1"
        auto_commit_label.config(text="自动上字", fg='#006600')
    else:
        xrze = ""
        auto_commit_label.config(text="自动上字", fg='#990000')
auto_commit_label = tk.Label(settings_frame, text="自动上字", 
                            font=("楷体", 14), bg='#FFF3C7',
                            fg='#006600' if xrze == '1' else '#990000',
                            cursor="hand2")
auto_commit_label.pack(side=tk.LEFT, padx=(0, 10))
def toggle_auto_commit_click(event):
    global xrze
    xrze = "1" if xrze != "1" else ""
    auto_commit_label.config(fg='#006600' if xrze == '1' else '#990000')
    auto_commit_var.set(xrze)

auto_commit_label.bind("<Button-1>", toggle_auto_commit_click)
phrase_commit_var = tk.StringVar(value=phrase_commit)
def toggle_phrase_commit():
    global phrase_commit
    if phrase_commit_var.get() == "1":
        phrase_commit = "1"
        phrase_commit_label.config(text="优先上词", fg='#006600')
    else:
        phrase_commit = ""
        phrase_commit_label.config(text="优先上词", fg='#990000')
phrase_commit_label = tk.Label(settings_frame, text="优先上词", 
                               font=("楷体", 14), bg='#FFF3C7',
                               fg='#006600' if phrase_commit == '1' else '#990000',
                               cursor="hand2")
phrase_commit_label.pack(side=tk.LEFT, padx=(0, 10))
def toggle_phrase_commit_click(event):
    global phrase_commit
    phrase_commit = "1" if phrase_commit != "1" else ""
    phrase_commit_label.config(fg='#006600' if phrase_commit == '1' else '#990000')
    phrase_commit_var.set(phrase_commit)
phrase_commit_label.bind("<Button-1>", toggle_phrase_commit_click)
radical_table_var = tk.BooleanVar(value=False)
radical_table_frame = tk.Frame(main_status_frame, bg='#FFF3C7', relief=tk.SUNKEN, bd=1)
radical_table_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 2))
radical_table_frame.pack_forget()  
radical_table_data = {
    "a(副)": "丶一丨丿乙乛𠃌乚𡿨",
    "b": "宀阝冫贝疒白卜八匕癶",
    "c": "车艹厂凵寸卄屮",
    "d": "刀歹大亠冖丷斗豆",
    "f": "风方父缶臼辰非",
    "g": "工古广弓光囗革戈瓜艮谷骨",
    "h": "火户禾⺌羊虍黑",
    "i": "虫页雨弋彐彑臣赤",
    "j": "金巾廴冂几𠘨卩己见斤㫐祭",
    "k": "口又舌用角",
    "l": "娄云勹力龙老卤里",
    "m": "木彡釆马门皿毛目矛米麦",
    "n": "女牛鸟耒齿",
    "o": "耳匚二儿㔾",
    "p": "攴片殳丬皮髟㐅",
    "q": "气犬豸欠青其",
    "r": "人肉入日リ",
    "s": "示丝石尸十厶巳",
    "t": "土彳幺夕田",
    "u": "攵水矢手食山士豕身",
    "v": "乑争舟止爪鬼支",
    "w": "王网瓦韦隹文",
    "x": "穴𰃮心西小巛血辛",
    "y": "言酉月鱼衣尢聿业羽黾音夗",
    "z": "辶竹足子自走",
    "0-9": "口丨一八㐅中大厂乙复"
}
def create_radical_table():
    for widget in radical_table_frame.winfo_children():
        widget.destroy()
    title_frame = tk.Frame(radical_table_frame, bg='#FFF3C7')
    title_frame.pack(fill=tk.X, pady=(2, 2))
    tk.Label(title_frame, text="部首码", font=("华文中宋", 11), 
            bg='#FFF3C7', fg='#000000', width=8, anchor='w').pack(side=tk.LEFT, padx=(2, 0))
    tk.Label(title_frame, text="对应部首", font=("华文中宋", 11), 
            bg='#FFF3C7', fg='#000000', anchor='w').pack(side=tk.LEFT, padx=(10, 0))
    separator = tk.Frame(radical_table_frame, height=1, bg='#000000')
    separator.pack(fill=tk.X, pady=2)
    table_container = tk.Frame(radical_table_frame, bg='#FFF3C7')
    table_container.pack(fill=tk.BOTH, expand=False)
    canvas = tk.Canvas(table_container, bg='#FFF3C7', highlightthickness=0)
    scrollable_frame = tk.Frame(canvas, bg='#FFF3C7')
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 60)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    scrollable_frame.bind("<MouseWheel>", on_mousewheel)
    def unbind_mousewheel(event=None):
        canvas.unbind_all("<MouseWheel>")
    radical_table_frame.bind("<Unmap>", unbind_mousewheel)
    canvas.pack(side="left", fill="both")
    for i, (letter, radicals) in enumerate(radical_table_data.items()):
        row_frame = tk.Frame(scrollable_frame, bg='#FFF3C7')
        row_frame.pack(fill=tk.X, pady=1)
        letter_label = tk.Label(row_frame, text=letter, font=("华文中宋", 11), 
                               bg='#FFF3C7', fg='#3232BE', width=8, anchor='w')
        letter_label.pack(side=tk.LEFT, padx=(2, 0))
        radical_label = tk.Label(row_frame, text=radicals, font=("华文中宋", 11), 
                                bg='#FFF3C7', fg='#000000', anchor='w')
        radical_label.pack(side=tk.LEFT, padx=(2, 0))
        if i % 2 == 0:
            letter_label.config(bg='#EFE3AE')
            radical_label.config(bg='#EFE3AE')
            row_frame.config(bg='#EFE3AE')
create_radical_table()
def toggle_radical_table():
    if radical_table_var.get():
        radical_table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        radical_table_label.config(text="部首表", fg='#006600')
        window.geometry("600x565")
        create_radical_table()
    else:
        radical_table_frame.pack_forget()
        radical_table_label.config(text="部首表", fg='#990000')
        window.geometry("600x215")
radical_table_label = tk.Label(settings_frame, text="部首表", 
                              font=("楷体", 14), bg='#FFF3C7', 
                              fg='#006600' if radical_table_var.get() else '#990000',
                              cursor="hand2")
radical_table_label.pack(side=tk.LEFT, padx=(0, 10))
def toggle_radical_table_click(event):
    current_state = radical_table_var.get()
    radical_table_var.set(not current_state)
    radical_table_label.config(fg='#006600' if radical_table_var.get() else '#990000')
    toggle_radical_table()  
radical_table_label.bind("<Button-1>", toggle_radical_table_click)
def update_entry_count():
    return get_entry_count()
entry_count_var = tk.StringVar()
entry_count_var.set(f"{update_entry_count()}")
entry_count_label = tk.Label(settings_frame, textvariable=entry_count_var, 
                           font=("华文中宋", 14), bg='#FFF3C7', fg='#000000')
entry_count_label.pack(side=tk.LEFT, padx=(0, 2))
def on_main_window_close():
    window.destroy()
window.protocol("WM_DELETE_WINDOW", on_main_window_close)
window.mainloop()
