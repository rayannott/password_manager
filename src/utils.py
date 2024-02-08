from string import ascii_letters, ascii_lowercase, ascii_uppercase
from random import choices
from math import sqrt
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

def check_reliable(key: str) -> float:
    # checks if the key is a reliable password and returns a score from [0, 1]
    if len(key) < 8:
        return 0.0
    LC = set(ascii_lowercase)
    UC = set(ascii_uppercase)
    lc_count, uc_count, spec_count = 0, 0, 0

    for ch in key:
        if ch in LC:
            lc_count += 1
        elif ch in UC:
            uc_count += 1
        elif ch in SYM_forw:
            spec_count += 1
        else:
            raise KeyError(f'Character {ch} cannot be used as a key in this storage. Try the <allowed> command to see the list of allowed characters')
    score = sqrt((lc_count/14)**2 + (uc_count/10)**2 + (spec_count/8)**2)
    if not (lc_count and uc_count and spec_count):
        score = min(score, 0.8)
    return min(score, 1.0)
    

