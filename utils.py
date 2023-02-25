from string import ascii_letters
from random import choices
from enum import Enum


SYM_forw: list[str] = ['o', 'D', '+', '0', 'w', 's', '1', '8', '@', 'H', 't', 
            'l', ']', 'Y', '}', '(', '[', 'X', '{', '\\', 'W', '^', 
            'c', 'J', '_', '>', 'Z', '&', '<', '5', 'V', '2', 'U', '=', 'O', ';', 
            '7', 'k', "'", '#', 'g', ' ', '/', 'A', '%', '$', 'C', 'M', 'r', 
            'L', 'x', 'y', 'S', '"', 'E', 'u', '?', ',', 'b', 'R', ')', 'e', 
            '6', 'v', 'Q', 'd', '!', '3', 'h', 'q', '4', 'G', ':', '*', 
            'F', 'z', 'K', '-', 'n', 'I', '9', 'f', '|', 'm', '.', 'P', 
            'p', 'N', 'T', 'i', 'j', 'B', 'a']

SYM_backw = {ch: i for i, ch in enumerate(SYM_forw)}


class MsgType(Enum):
    ERROR = 'error'
    MSG = 'message'


class Message:
    def __init__(self, message: str, type: MsgType = MsgType.MSG) -> None:
        self.message = message
        self.type = type
    
    def __str__(self) -> str:
        return ('' if self.type == MsgType.MSG else 'ERROR: ') + self.message
    

MessagesList = list[Message]


def string_repeater(s: str):
    while True:
        for ch in s:
            yield ch


def shift_str(s: str, num: int) -> str:
    num %= len(s)
    if num == 0:
        return s
    return s[-num:] + s[:len(s)-num]


def generate_password(length):
    chars = ascii_letters + '0123456789-!_'
    return ''.join(choices(chars, k=length))


char_func = SYM_backw.get
def hashf(s: str):
        a = 1234627; b = 8935573; c = 12507347
        res = sum(map(char_func, s))**2 + 1
        for i, ch in enumerate(s, 1):
            this_idx = char_func(ch)
            res = ((res + i) * (this_idx + i) * a) % b
            res = ((res + i) * (this_idx + 2*i) * b) % c
            res = ((res + i) * (this_idx + 3*i + 1) * c) % 2147483647
        return res
