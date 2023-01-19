from string import ascii_letters
from random import choice

def string_repeater(s: str):
    while True:
        for ch in s:
            yield ch

def shift_str(s: str, num: int) -> str:
    num %= len(s)
    if num == 0:
        return s
    return s[-num:] + s[:len(s)-num]

def generate_password():
    chars = ascii_letters + '0123456789'
    return ''.join([choice(chars) for _ in range(15)])
