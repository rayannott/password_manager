from utils import *



class VigenereCipher:
    def _forw(self, ind: int):
        return SYM_forw[ind]
    
    def _backw(self, ch: str):
        if ch not in SYM_backw:
            raise KeyError(f'Character {ch} is unknown')
        return SYM_backw[ch]

    def encrypt(self, s, key):
        pr = string_repeater(key)
        res = ''
        for ch in s:
            res += self._forw((self._backw(ch) + self._backw(next(pr))) % len(SYM_forw))
        return res

    def decrypt(self, s, key):
        pr = string_repeater(key)
        res = ''
        for ch in s:
            res += self._forw((self._backw(ch) - self._backw(next(pr))) % len(SYM_forw))
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