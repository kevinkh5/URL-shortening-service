import random
import string
# 랜덤으로 길이 7 글자 생성(BASE 62)

# short_key 생성함수
def generate_random_string(length=7):
    characters = string.ascii_letters + string.digits  # 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    random_string = ''.join(random.choices(characters, k=length))
    return random_string


class URLService:
    def __init__(self):
        self.ltos = {}
        self.stol = {}
        self.COUNTER = 100000000000
        self.elements = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def long_to_short(self, url):
        short_key = self.base10_to_base62(self.COUNTER)
        # self.ltos[url] = self.COUNTER
        self.stol[self.COUNTER] = url
        self.COUNTER += 1
        return short_key

    def short_to_long(self, short_key):
        n = self.base62_to_base10(short_key)
        return self.stol.get(n)

    def base62_to_base10(self, s):
        n = 0
        for char in s:
            n = n * 62 + self.convert(char)
        return n

    def convert(self, c):
        if '0' <= c <= '9':
            return ord(c) - ord('0')
        if 'a' <= c <= 'z':
            return ord(c) - ord('a') + 10
        if 'A' <= c <= 'Z':
            return ord(c) - ord('A') + 36
        return -1

    def base10_to_base62(self, n):
        sb = []
        while n != 0:
            sb.insert(0, self.elements[n % 62])
            n //= 62
        while len(sb) != 7:
            sb.insert(0, '0')
        return ''.join(sb)


if __name__ == "__main__":
    print("---Random_Generate---") # 랜덤하게 short key 생성
    random_string = generate_random_string()
    print(random_string)
    print()

    print("---Base_Conversion_Generate---") # 카운트가 증가함에 따라 유니크한 Short key를 생성
    service = URLService()
    print(service.long_to_short("https://www.example.com"))
    print(service.short_to_long("1L9zO9O"))