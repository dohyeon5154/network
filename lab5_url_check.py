"""
5교시 실습 — 가장 약한 고리는 사람
=====================================
STEP 1  주소에서 '진짜 주인'을 뽑아내는 함수를 만든다
STEP 2  수상한 신호를 자동으로 찾아낸다
STEP 3  10문제로 내 눈을 시험한다
STEP 4  메일 헤더에서 SPF·DKIM·DMARC 결과를 읽는다

여기 나오는 가짜 주소는 전부 실습용으로 지어낸 것이며,
실제로 접속하지 마세요. 문자열만 분석합니다.
"""
import re
from urllib.parse import urlparse
from _width import pad

# 두 조각이 통째로 최상위 구실을 하는 경우 (co.kr 처럼)
TWO_LEVEL = {
    "co.kr", "or.kr", "ne.kr", "go.kr", "re.kr", "pe.kr", "ac.kr",
    "co.uk", "org.uk", "ac.uk", "com.au", "co.jp", "com.cn",
}

# 사칭에 자주 쓰이는 이름들
BRANDS = ["naver", "kakao", "google", "apple", "paypal", "kbstar",
          "shinhan", "wooribank", "nhbank", "toss", "coupang", "amazon"]


# ── STEP 1 : 진짜 주인 뽑아내기 ────────────────────────────────────
def registrable_domain(host):
    """
    호스트에서 '진짜 주인'을 뽑는다.
    규칙은 간단하다 — 점으로 자른 뒤 뒤에서부터 두 조각.
    단 co.kr 처럼 두 조각이 통째로 꼬리인 경우에는 세 조각.
    """
    parts = host.lower().strip(".").split(".")
    if len(parts) < 2:
        return host.lower()
    tail2 = ".".join(parts[-2:])
    if tail2 in TWO_LEVEL and len(parts) >= 3:
        return ".".join(parts[-3:])
    return tail2


def dissect(url):
    """주소를 조각내어 돌려준다."""
    u = urlparse(url if "//" in url else "http://" + url)
    host = u.hostname or ""
    own = registrable_domain(host)
    front = host[: -len(own)].rstrip(".") if host.endswith(own) else host
    return {"scheme": u.scheme, "host": host, "front": front,
            "owner": own, "path": u.path or "/"}


# ── STEP 2 : 수상한 신호 찾기 ──────────────────────────────────────
def suspicious(url):
    """자동으로 걸러낼 수 있는 신호들을 모은다."""
    d = dissect(url)
    flags = []
    if d["scheme"] != "https":
        flags.append("https가 아님 — 내용이 봉해지지 않습니다")
    if "xn--" in d["host"]:
        flags.append("퓨니코드 — 한글·키릴 문자를 섞어 눈속임한 주소일 수 있음")
    for b in BRANDS:
        if b in d["host"] and b not in d["owner"]:
            flags.append(f"'{b}'이(가) 주소에 있지만 진짜 주인은 {d['owner']}")
            break
    label = d["owner"].split(".")[0]
    look = label.replace("1", "l").replace("0", "o").replace("rn", "m").replace("vv", "w")
    if look != label and look in BRANDS:
        flags.append(f"글자 모양 눈속임 — '{label}'은 '{look}'을 흉내 낸 것")
    if d["owner"].count("-") >= 1 and any(b in d["owner"] for b in BRANDS):
        flags.append("회사 이름을 붙임표로 이어 붙인 도메인")
    if d["host"].count(".") >= 4:
        flags.append("점이 지나치게 많음 — 앞을 길게 늘여 뒤를 가리는 수법")
    return d, flags


def explain(url):
    d, flags = suspicious(url)
    print(f"\n  {url}")
    print("  " + pad("프로토콜", 12) + d["scheme"])
    print("  " + pad("호스트", 12) + d["host"])
    print("  " + pad("앞 이름표", 12) + (d["front"] or "(없음)") + "   ← 누구나 붙일 수 있음")
    print("  " + pad("진짜 주인", 12) + d["owner"].upper() + "   ← 여기가 전부")
    print("  " + pad("경로", 12) + d["path"] + "   ← 주인과 무관")
    if flags:
        print("  수상한 신호:")
        for f in flags:
            print("    · " + f)
    else:
        print("  수상한 신호: 없음")
    return d, flags


# ── STEP 3 : 눈 시험 ───────────────────────────────────────────────
QUIZ = [
    ("https://www.naver.com/login", True),
    ("https://naver.com.login-page.xyz/verify", False),
    ("https://accounts.google.com/signin", True),
    ("https://www.paypa1.com/account", False),
    ("https://kakao-support.help/reset", False),
    ("https://banking.kbstar.com/login", True),
    ("https://mail.naver.com.session-check.top/", False),
    ("https://www.gov.kr/portal/main", True),
    ("http://toss-refund.co.kr.secure-pay.net/claim", False),
    ("https://cs.coupang.com/announce", True),
]


def quiz():
    print("\nSTEP 3  열 문제입니다. 진짜면 y, 가짜면 n 을 입력하세요.\n")
    score = 0
    for i, (url, real) in enumerate(QUIZ, 1):
        print(f"[{i}/10]  {url}")
        ans = input("       진짜입니까? (y/n) ").strip().lower().startswith("y")
        d = dissect(url)
        ok = ans == real
        score += ok
        print(f"       {'맞았습니다' if ok else '틀렸습니다'} — "
              f"{'진짜' if real else '가짜'}. 진짜 주인은 {d['owner'].upper()}\n")
    print(f"최종 {score} / 10")
    if score < 8:
        print("눈으로만 보면 누구나 틀립니다. 그래서 규칙이 필요합니다 —")
        print("  '첫 번째 단독 슬래시 앞까지가 호스트, 그 마지막 두 조각이 주인'")
    return score


# ── STEP 4 : 메일 헤더 읽기 ────────────────────────────────────────
def read_headers(text):
    """붙여넣은 메일 헤더에서 판단에 필요한 줄만 뽑는다."""
    def find(pattern):
        m = re.search(pattern, text, re.I | re.M)
        return m.group(1).strip() if m else "(없음)"

    frm = find(r"^From:\s*(.+)$")
    ret = find(r"^Return-Path:\s*(.+)$")
    spf = find(r"Received-SPF:\s*(\w+)")
    dkim = find(r"dkim=(\w+)")
    dmarc = find(r"dmarc=(\w+)")
    disp = re.search(r'"?([^"<]*)"?\s*<([^>]+)>', frm)
    name = disp.group(1).strip() if disp else "(없음)"
    addr = disp.group(2).strip() if disp else frm
    domain = addr.split("@")[-1]

    print("  " + pad("표시 이름", 14) + name + "   ← 아무나 적을 수 있음")
    print("  " + pad("실제 주소", 14) + addr)
    print("  " + pad("실제 도메인", 14) + domain + "   ← 여기를 보세요")
    print("  " + pad("Return-Path", 14) + ret)
    print("  " + pad("검사 결과", 14) +
          f"SPF={spf.upper()}  DKIM={dkim.upper()}  DMARC={dmarc.upper()}")
    fails = [k for k, v in (("SPF", spf), ("DKIM", dkim), ("DMARC", dmarc))
             if v.lower() != "pass"]
    if fails:
        print(f"  판정: 주의 — {', '.join(fails)} 실패. 사칭 가능성이 있습니다.")
    else:
        print("  판정: 세 검사 통과. 다만 링크를 누르기보다 앱을 직접 열어 확인하세요.")
    return fails


def read_sample_file(path="sample_headers.txt"):
    print("\nSTEP 4  메일 헤더 세 통을 읽어 봅니다")
    try:
        raw = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        print(f"  {path} 파일이 같은 폴더에 없습니다.")
        return
    for block in raw.split("=== "):
        block = block.strip()
        if not block:
            continue
        title, _, body = block.partition("\n")
        print(f"\n[{title}]")
        read_headers(body)


if __name__ == "__main__":
    print(__doc__)
    print("STEP 1~2  주소 조각내기")
    for u in ["https://www.naver.com/login",
              "https://naver.com.login-page.xyz/verify",
              "http://toss-refund.co.kr.secure-pay.net/claim"]:
        explain(u)
    read_sample_file()
    quiz()
