from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, abort
import os
import vgli

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

DATA_FILE = "dictionary.txt"

symbol_map = {
    '0': '˙',
    '1': 'ˉ',
    '2': 'ˊ',
    '3': 'ˇ',
    '4': 'ˋ'
}

def check_second_char(char):
    special_chars = "acegijmnopqrsuvwxyz;"
    return char in special_chars

def process_string(s):
    if len(s) < 3:
        return s
    
    chars = list(s)
    
    if len(s) >= 3 and check_second_char(chars[1]) and chars[2] in symbol_map:
        chars[2] = symbol_map[chars[2]]
    
    if len(s) >= 5:
        chars[4] = f'<sup>{chars[4]}</sup>'
    
    return ''.join(chars)

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

def add_entry(char, code):
    ensure_data_file()
    entries = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            entries = f.readlines()
    new_entries = []
    found = False
    for entry in entries:
        if entry.strip().endswith(f" {code}"):
            new_entry = f"{char} {code}\n"
            new_entries.append(new_entry)
            found = True
        else:
            new_entries.append(entry)
    if not found:
        new_entry = f"{char} {code}\n"
        new_entries.append(new_entry)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_entries)
    return f"{char} {code}"

def update_or_delete_entry(char, code):
    ensure_data_file()
    entries = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            entries = f.readlines()
    
    new_entries = []
    found = False
    
    # 如果是删除操作 (code == 'x')
    if code == 'x':
        for entry in entries:
            parts = entry.strip().split(' ', 1)
            if len(parts) == 2 and parts[0] == char:
                found = True  # 找到并标记为删除
            else:
                new_entries.append(entry)
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_entries)
        
        if found:
            return f"已删除汉字 '{char}' 的所有编码"
        else:
            return f"汉字 '{char}' 不存在，无法删除"
    
    # 如果是更新/添加操作
    for entry in entries:
        parts = entry.strip().split(' ', 1)
        if len(parts) == 2 and parts[0] == char:
            # 替换现有编码
            new_entries.append(f"{char} {code}\n")
            found = True
        else:
            new_entries.append(entry)
    
    # 如果没找到，添加新条目
    if not found:
        new_entries.append(f"{char} {code}\n")
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_entries)
    
    return f"{'更新' if found else '添加'}成功: {char} {code}"

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
    return results

def list_help_files():
    help_dir = "help"
    if not os.path.exists(help_dir):
        os.makedirs(help_dir)
        return []
    
    files = []
    for filename in os.listdir(help_dir):
        if os.path.isfile(os.path.join(help_dir, filename)):
            files.append(filename)
    
    return sorted(files)

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
    return parts

@app.route('/')
def index():
    entry_count = get_entry_count()
    return render_template('index.html', entry_count=entry_count)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    message = ""
    if request.method == 'POST':
        entries_text = request.form.get('entries', '').strip()
        
        if entries_text:
            lines = entries_text.split('\n')
            results = []
            error_lines = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split(' ', 1)
                if len(parts) < 2:
                    error_lines.append(f"第{i}行: '{line}' - 格式错误，应为'汉字 编码'")
                    continue
                    
                char = parts[0].strip()
                code = parts[1].strip()
                
                if not char or not code:
                    error_lines.append(f"第{i}行: '{line}' - 汉字或编码为空")
                    continue
                    
                result = add_entry(char, code)
                results.append(result)
            
            if error_lines:
                message = f"部分条目格式错误:\n" + "\n".join(error_lines)
            elif results:
                try:
                    vgli.process_file(DATA_FILE, DATA_FILE)
                    message = f"成功保存并排序 {len(results)} 个编码"
                except Exception as e:
                    message = f"保存成功，但排序失败: {str(e)}"
            else:
                message = "没有有效的编码可保存"
    
    entry_count = get_entry_count()
    return render_template('edit.html', message=message, entry_count=entry_count)

@app.route('/modify', methods=['POST'])
def modify():
    old_code = request.form.get('old_code', '').strip()
    new_code = request.form.get('new_code', '').strip()
    message = ""
    
    if not old_code or not new_code:
        message = "原编码和新编码都不能为空"
    else:
        # 检查原编码是否存在
        found = False
        entries = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                entries = f.readlines()
        
        new_entries = []
        for entry in entries:
            parts = entry.strip().split(' ', 1)
            if len(parts) == 2 and parts[1] == old_code:
                found = True
                if new_code.lower() != 'x':
                    # 修改编码
                    new_entries.append(f"{parts[0]} {new_code}\n")
                    message = f"成功将编码 '{old_code}' 修改为 '{new_code}'"
                # 如果新编码是x，则不添加这一行（即删除）
            else:
                new_entries.append(entry)
        
        if not found:
            message = f"原编码 '{old_code}' 不存在！"
        elif new_code.lower() == 'x':
            message = f"成功删除编码 '{old_code}'"
        
        # 如果有修改，写回文件
        if found:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                f.writelines(new_entries)
            # 重新排序
            try:
                vgli.process_file(DATA_FILE, DATA_FILE)
            except Exception as e:
                message += f"，但排序失败: {str(e)}"
    
    entry_count = get_entry_count()
    return render_template('edit.html', message=message, entry_count=entry_count)

@app.route('/query_char', methods=['GET', 'POST'])
def query_char():
    results = []
    result_str = ""  
    query_char = ""
    if request.method == 'POST':
        query_char = request.form.get('char', '').strip()
        if query_char:
            chars = []
            i = 0
            while i < len(query_char):
                if query_char[i] == '!' and i+1 < len(query_char) and query_char[i+1] == '!':
                    chars.append('!!')
                    i += 2   
                else:
                    chars.append(query_char[i])
                    i += 1
            
            char_results = []
            for char in chars:
                codes = query_by_char(char)
                if codes:
                    code_str = '/'.join(codes)
                    char_results.append(f"{char} {code_str}")
                    result_str += code_str + " "
                else:
                    char_results.append(f"{char} --")
                    result_str += "-- "
            
            result_str = result_str.strip()
            
            results = char_results
    
    entry_count = get_entry_count()
    return render_template('query_char.html', results=results, result_str=result_str, query_char=query_char, entry_count=entry_count)

@app.route('/query_prefix', methods=['GET', 'POST'])
def query_prefix():
    entry_count = get_entry_count()
    if request.method == 'POST':
        query_prefix_str = request.form.get('prefix', '').strip()
        if query_prefix_str:
            # 使用ffkl函数处理输入
            prefixes = ffkl(query_prefix_str)
            
            results = []
            for prefix in prefixes:
                if prefix:  # 跳过空字符串
                    prefix_results = query_by_prefix(prefix)
                    if prefix_results:
                        # 如果有多个前缀，只取第一个汉字
                        if len(prefixes) > 1:
                            # 提取第一个汉字
                            first_char = prefix_results[0][0]
                            # 存储完整结果用于展开
                            full_results = "/".join(prefix_results)
                            results.append({
                                'prefix': prefix,
                                'first_char': first_char,
                                'full_results': full_results
                            })
                        else:
                            # 单个前缀，返回所有结果
                            results.append("/".join(prefix_results))
                    else:
                        if len(prefixes) > 1:
                            results.append({
                                'prefix': prefix,
                                'first_char': '--',
                                'full_results': '--'
                            })
                        else:
                            results.append("--")
            
            # 根据前缀数量返回不同格式的结果
            if len(prefixes) > 1:
                return render_template('query_prefix.html', 
                                      multiple_results=results, 
                                      query_prefix=query_prefix_str, 
                                      entry_count=entry_count,
                                      is_multiple=True)
            else:
                return render_template('query_prefix.html', 
                                      result_str=results[0] if results else "--", 
                                      query_prefix=query_prefix_str, 
                                      entry_count=entry_count,
                                      is_multiple=False)
    
    return render_template('query_prefix.html', 
                          query_prefix="", 
                          entry_count=entry_count,
                          is_multiple=False)

@app.route('/help')
def help_files():
    files = list_help_files()
    entry_count = get_entry_count()
    return render_template('help.html', files=files, entry_count=entry_count)

@app.route('/download/<filename>')
def download_file(filename):
    help_dir = "help"
    if '..' in filename or filename.startswith('/'):
        abort(404)
    try:
        return send_from_directory(help_dir, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/writing')
def writing():
    return render_template('writing.html')

@app.route('/writing/process', methods=['POST'])
def process_writing():
    input_text = request.form.get('input_text', '')
    strings = input_text.split()
    
    processed_strings = [process_string(s) for s in strings]
    
    return jsonify({
        'original': strings,
        'processed': processed_strings
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1145)
