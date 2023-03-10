from string import ascii_letters
from random import choices
from enum import Enum
import hashlib


SYM_forw: list[str] = ['o', 'D', '+', '0', 'w', 's', '1', '8', '@', 'H', 't', 
            'l', ']', 'Y', '}', '(', '[', 'X', '{', '\\', 'W', '^', 
            'c', 'J', '_', '>', 'Z', '&', '<', '5', 'V', '2', 'U', '=', 'O', ';', 
            '7', 'k', "'", '#', 'g', ' ', '/', 'A', '%', '$', 'C', 'M', 'r', 
            'L', 'x', 'y', 'S', '"', 'E', 'u', '?', ',', 'b', 'R', ')', 'e', 
            '6', 'v', 'Q', 'd', '!', '3', 'h', 'q', '4', 'G', ':', '*', 
            'F', 'z', 'K', '-', 'n', 'I', '9', 'f', '|', 'm', '.', 'P', 
            'p', 'N', 'T', 'i', 'j', 'B', 'a']

SYM_backw = {ch: i for i, ch in enumerate(SYM_forw)}


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


def hashf(s: str):
    return hashlib.sha256(s.encode()).hexdigest()
