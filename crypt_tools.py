from utils import *


class VigenereCipher:
    def __init__(self) -> None:
        # SYM = ascii_lowercase + ascii_uppercase + '0123456789' + '!@#$%^&*()_+=-][}{\';":,./|\\'
        self.SYM_forw: list[str] = ['o', 'D', '+', '0', 'w', 's', '1', '8', '@', 'H', 't', 
            'l', ']', 'Y', '}', '(', '[', 'X', '{', '\\', 'W', '^', 
            'c', 'J', '_', '>', 'Z', '&', '<', '5', 'V', '2', 'U', '=', 'O', ';', 
            '7', 'k', "'", '#', 'g', ' ', '/', 'A', '%', '$', 'C', 'M', 'r', 
            'L', 'x', 'y', 'S', '"', 'E', 'u', '?', ',', 'b', 'R', ')', 'e', 
            '6', 'v', 'Q', 'd', '!', '3', 'h', 'q', '4', 'G', ':', '*', 
            'F', 'z', 'K', '-', 'n', 'I', '9', 'f', '|', 'm', '.', 'P', 
            'p', 'N', 'T', 'i', 'j', 'B', 'a']
        self.SYM_backw = {ch: i for i, ch in enumerate(self.SYM_forw)}

    def forw(self, ind: int):
        return self.SYM_forw[ind]
    
    def backw(self, ch: str):
        if ch not in self.SYM_backw:
            raise KeyError(f'Character {ch} is unknown')
        return self.SYM_backw[ch]

    def encrypt(self, s, key):
        pr = string_repeater(key)
        res = ''
        for ch in s:
            res += self.forw((self.backw(ch) + self.backw(next(pr))) % len(self.SYM_forw))
        return res

    def decrypt(self, s, key):
        pr = string_repeater(key)
        res = ''
        for ch in s:
            res += self.forw((self.backw(ch) - self.backw(next(pr))) % len(self.SYM_forw))
        return res



class VigenereIterShiftCifer:
    def __init__(self, iterations=10) -> None:
        self.iterations = iterations

    def encrypt(self, s, key):
        tmp = s
        cifer = VigenereCipher()
        for i in range(self.iterations):
            tmp = cifer.encrypt(tmp, shift_str(key, i))
        return tmp
    
    def decrypt(self, s, key):
        tmp = s
        cifer = VigenereCipher()
        for i in reversed(range(self.iterations)):
            tmp = cifer.decrypt(tmp, shift_str(key, i))
        return tmp


class VigenereKeySplitCifer:
    def __init__(self, iterations=10) -> None:
        self.iterations = iterations

    @staticmethod
    def split_key_2(key) -> list[str]:
        if len(key) < 4:
            return [key]
        mid = len(key) // 2
        extra = ''
        if len(key) % 2 == 0:
            extra = key[1]
        return [key[:mid+1], key[mid+1:] + extra]

    def encrypt(self, s: str, key: str) -> str:
        keys = VigenereKeySplitCifer.split_key_2(key)
        tmp = s
        cifer = VigenereIterShiftCifer(self.iterations)
        for k in keys:
            tmp = cifer.encrypt(tmp, k)
        return tmp

    def decrypt(self, s: str, key: str) -> str:
        keys = VigenereKeySplitCifer.split_key_2(key)
        tmp = s
        cifer = VigenereIterShiftCifer(self.iterations)
        for k in reversed(keys):
            tmp = cifer.decrypt(tmp, k)
        return tmp