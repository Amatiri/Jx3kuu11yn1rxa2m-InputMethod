import os

# 项目根目录（本文件所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据文件路径
DATA_FILE = os.path.join(BASE_DIR, "dictionary.txt")
DATA_NO_NUMBER_FILE = os.path.join(BASE_DIR, "dictionary_no_number.txt")
CIYU_FILE = os.path.join(BASE_DIR, "ciyu.txt")

# 编码相关常量
CODE_CHARS = "1234567890qwertyuiopasdfghjklzxcvbnm;'."
SURROUND_CHARS = "1234567890qwertyuiopasdfghjklzxcvbnm;'.-= "
SELECTION_SYMBOLS = ["!", "@", "#", "$", "%"]
SYMBOL_TO_INDEX = {"!": 0, "@": 1, "#": 2, "$": 3, "%": 4}
