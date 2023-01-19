# CL password manager
A simple command line application for storing passwords with encryption written entirely in python.

## How to try
Run the <code>main.py</code> script; no external packages needed. I provided a password storage for testing purposes: <code>test_storage.pass</code>. To start, type the <code>help</code> command.

## How the encryption is executed
The main encryption algorithm is a modified **Vigenere cifer** (which is a polyalphabetic form of a well-known Caesar cifer).

The <code>crypt_tools.py</code> file contains three cifers. The allowed characters as well as the main encryption logic is set in the <code>VigenereCifer</code> class. <code>VigenereIterShiftCifer</code> cifer applies the Vigenere cifer iteratively, each time with a shifted key string.

The following block of code explains the idea behind the iterative-shift Vigenere cifer:\
<code>
message = 'hello'; key = 'a1b2c3d'\
result1 = VigenereIterShiftCifer(iterations=3).encrypt(message, key)\
tmp = VigenereCipher().encrypt(message, 'a1b2c3d')\
tmp = VigenereCipher().encrypt(tmp, 'da1b2c3')\
result2 = VigenereCipher().encrypt(tmp, '3da1b2c')\
print(result1 == result2) # True
</code>

The <code>VigenereKeySplitCifer</code> takes it one step further. It is equivalent to the <code>VigenereIterShiftCifer</code> if length of the key is less than 4. Otherwise, it splits the key into two keys $k_1,\;k_2$ in such a way that $\gcd(\text{len}(k_1), \text{len}(k_2)) = 1$, then uses these keys in sequence applying the <code>VigenereIterShiftCifer</code> to the input string. The split is increasing the effective length of the key (if the initial length is $L$, then new effective length would be approximately equal to $L^2/4$).



<code></code>
