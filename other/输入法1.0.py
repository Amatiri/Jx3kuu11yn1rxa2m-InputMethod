import tkinter as t
import os
DATA_FILE = "dictionary.txt"
表1="1234567890qwertyuiopasdfghjklzxcvbnm;'."
表2 = "1234567890qwertyuiopasdfghjklzxcvbnm;'.-= "
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
def 处理(取):
    
    得=""
    for 每 in 取:
        if 每 in 表1:
            得+=每
    return 得

def 替换(内容,处理后):  
    出 = ""
    
    for 每 in 内容:
        if 每 not in 表2:
            出 += 每
    出 += 处理后
    输入框.delete(0, t.END)  
    输入框.insert(0, 出)  

def 要分开(原):
    分开=原.split("'")
    还能再分 = True
    while 还能再分:
        还能再分 = False
        新分开= []
        for 部分 in 分开:
            条件1 = False
            条件2 = False
            位置 = []
            if not any(字.isdigit() for 字 in 部分) and len(部分) > 2:
                条件1 = True
            for 索引, 字 in enumerate(部分):
                if 字.isdigit() and 索引 > 2 and not 部分[索引-1].isdigit():
                    条件2 = True
                    位置.append(索引)
            if 条件1:
                新部分 = "'".join([部分[i:i+2] for i in range(0, len(部分), 2)])
                新分开.extend(新部分.split("'"))
                还能再分 = True
            elif 条件2:
                新部分 = 部分
                for 位 in sorted(位置, reverse=True):
                    新部分 = 新部分[:位-2] + "'" + 新部分[位-2:]
                新分开.extend(新部分.split("'"))
                还能再分 = True
            else:
                新分开.append(部分)
        分开 = 新分开
    分开 = [每 for 每 in 分开 if 每 != '']
    合并=""
    for 部分 in 分开:
        合并=合并+部分+"'"
    合并=合并[:-1]
    return 合并
def 单字查询(分后):
    初步候选=query_by_prefix(分后)[:5]
    if 初步候选:
        候选 = "/".join(初步候选)
        return 候选
    else:
        return ""
def 多字查询(分后):
    字列=分后.split("'")
    首字=''
    for 每编 in 字列:
        每候选 = query_by_prefix(每编)
        if 每候选:
            每首字 = 每候选[0][0]
            首字+=每首字
    return 首字

def 汉字清屏(取):
    判断=True
    for i in 取:
        if i in 表1:
            判断=False
    if 判断==True:
        显示.config(text='')
        多选.config(text='')

def 主功能(*args):
    取=实时.get()
    得=处理(取)
    分后=要分开(得)
    上屏=''
    候选=''
    首字=''
    if 分后 != "" and ' ' not in 分后:
        if "'" not in 分后:
            候选=单字查询(分后)
            显示.config(text=候选)
            多选.config(text='')
            if 候选 != '':
                if "/" in 候选:
                    上屏=候选.split("/")[0][0]
                else:
                    上屏=候选[0]
        else:
            首字=多字查询(分后)
            显示.config(text='')
            if 首字 != '':
                多选.config(text=首字)
            else:
                多选.config(text='')
            上屏=首字      
    if 取=="":
        显示.config(text='')
        多选.config(text='')
    if " " in 取:
        替换(取,上屏)
        显示.config(text='')
        多选.config(text='')
    if "-" in 取 or "=" in 取:
        替换(取,得)
    汉字清屏(取)
窗口=t.Tk()
实时=t.StringVar()
实时.trace("w",主功能)
注意=t.Label(text="当前不支持选字")
注意.pack()
输入框=t.Entry(textvariable=实时)
输入框.pack()
多选=t.Label(text="")
多选.pack()
显示=t.Label(text="")
显示.pack()
条目=t.Label(text=f"条目数{get_entry_count()}")
条目.pack()
窗口.mainloop()
