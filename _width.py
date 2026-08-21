"""한글이 섞인 표를 가지런히 출력하기 위한 도우미. (한글은 화면에서 2칸을 차지합니다)"""
import unicodedata

def w(s):
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in str(s))

def pad(s, n, right=False):
    s = str(s)
    gap = " " * max(0, n - w(s))
    return gap + s if right else s + gap
