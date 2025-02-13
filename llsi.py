from log_colorizer import make_colored_stream_handler
from logging import getLogger
from pathlib import Path
from typing import List
from enum import Enum
from pprint import pprint


SPEC_WORDS = (
    # 运算
    "加",
    "减",
    "乘",
    "除",
    "取余",
    # 判断
    "小于",
    "大于",
    "等于",
    "不等于",
    "不大于",  # >=
    "不小于",  # <=
    "且",
    "或",
    "不",
    # 控制
    "如果",
    "否则",
    "循环",     # while
    "遍历",     # for
    "中的每一个" # in
    # 定义
    "为",  # =
    "变量",
    "函数",
    # 其他
    "返回",
    "导入",
)

BRACKETS = (
    "（",
    "）",
    "【",
    "】",
    "{",
    "}",
)

TYPES = (
    "整数类型",
    "字符串类型",
    "浮点数类型",
    "布尔类型",
    "空类型",
)

BUILD_IN_FUNCS = (
    "输出",
    "获取输入",
)

logger = getLogger("吉吉解释器")
logger.setLevel("DEBUG")
logger.addHandler(make_colored_stream_handler())


class LiteralTypes(Enum):
    int    = 0
    string = 1
    float  = 2
    bool   = 3
    null   = 4


class TokenTypes(Enum):
    spec    = 0
    bracket = 1
    type    = 2
    buildin = 3
    literal = 4
    var     = 5
    func    = 6


class Literal:
    def __init__(self, type: LiteralTypes, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Literal(type={self.type}, value={self.value})"


class Token:
    def __init__(self, type: TokenTypes, value: str):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value})"


class Sentence:
    def __init__(self):
        self.tokens = []

    def __repr__(self):
        return f"Sentence(tokens={self.tokens})"

    def append(self, token: Token):
        self.tokens.append(token)


def error(msg: str, line: int, column: int):
    logger.error(f"{msg} at line {line}, column {column}")


def main():
    code = get_code(Path(f"main.吉吉"))
    code = preprocessing(code)
    #code_struct = [t for t in [s.tokens for s in code]]
    #pprint(code_struct)
    pprint(code)


def get_code(path: Path) -> str:
    # TODO: support other file extensions
    if path.suffix not in (".吉吉", ".lls"):
        raise ValueError(f"Unsupported file extension: {path.suffix}")
    elif not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    elif not path.is_file():
        raise ValueError(f"Not a file: {path}")
    else:
        return path.read_text(encoding="utf-8")


def new_token(word: str) -> Token:
    # 关键字
    if word in SPEC_WORDS:
        tok = Token(TokenTypes.spec, word)
    # 括号
    elif word in BRACKETS:
        tok = Token(TokenTypes.bracket, word)
    # 类型
    elif word in TYPES:
        tok = Token(TokenTypes.type, word)
    # 内置函数
    elif word in BUILD_IN_FUNCS:
        tok = Token(TokenTypes.buildin, word)
    # 布尔值
    elif word == "真":
        val = Literal(LiteralTypes.bool, True)
        tok = Token(TokenTypes.literal, val)
    elif word == "假":
        val = Literal(LiteralTypes.bool, False)
        tok = Token(TokenTypes.literal, val)
    elif word == "空":
        val = Literal(LiteralTypes.null, None)
        tok = Token(TokenTypes.literal, val)
    # 整型
    elif word.isdecimal():
        val = Literal(LiteralTypes.int, int(word))
        tok = Token(TokenTypes.literal, val)
    # 浮点型
    elif word.replace(".", "", 1).isdecimal():
        val = Literal(LiteralTypes.float, float(word))
        tok = Token(TokenTypes.literal, val)
    # 字符串不在这里处理
    # 变量
    else:
        tok = Token(TokenTypes.var, word)
    return tok


# 我为下面的多层缩进道歉……
def preprocessing(code: str) -> List[Sentence]:
    code = code.split("\n")
    code = [line.strip() for line in code]
    logger.debug(f"Preprocessing code: {code}")
    result = []

    # 逐行处理
    for line_code, line in enumerate(code, 1):
        logger.debug(f"Processing line {line_code}: {line}")
        # 空行或注释，直接跳过
        if line == "" or line.startswith("#"):
            code.remove(line)
            continue

        sen = Sentence()
        last_word = ""
        in_string = False

        # 逐字符处理
        for char in line:
            # 字符串内
            if in_string:
                # 字符串结束
                if char == "”":
                    tok = Token(TokenTypes.literal, Literal(LiteralTypes.string, last_word[1:])) # 去掉开头的 “
                    sen.append(tok)
                    last_word = ""
                    in_string = False
                    continue
                # 直接到最后 last_word += char
                # TODO: 处理转义字符
            # 识别单词
            elif char.isspace():
                if last_word != "":
                    tok = new_token(last_word)
                    sen.append(tok)
                    last_word = ""
                continue
            # 识别括号
            elif char in "（）【】":
                if last_word != "":
                    sen.append(new_token(last_word))
                sen.append(new_token(char))
                last_word = ""
                continue
            # 识别字符串
            elif char == "“":
                in_string = True
            # 在单词内
            last_word += char

        # 最后一个字符
        if last_word != "":
            sen.append(new_token(last_word))
        result.append(sen)
    return result


if __name__ == "__main__":
    logger.debug("Strat main()!")
    main()
    logger.debug("End main()!")
