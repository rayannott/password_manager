from string import ascii_letters
from random import choices
from enum import Enum
from dataclasses import dataclass


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
