"""
3교시 실습 — 그 길 위에서 내 데이터는 다 보인다
==================================================
STEP 1  http로 보내는 요청이 실제로 어떤 글자인지 눈으로 본다
STEP 2  https 인증서를 열어 '누가 보증했는지'와 '언제까지인지'를 확인한다
STEP 3  여러 사이트의 인증서를 한 번에 조회해 표로 만든다
STEP 4  이름이 다른 곳에 접속하면 어떻게 되는지 확인한다

표준 라이브러리만 씁니다. 설치할 것이 없습니다.
"""
import socket
import ssl
from datetime import datetime, timezone
from _width import pad

SITES = [
    "www.naver.com",
    "www.google.com",
    "github.com",
    "www.kbstar.com",
]


# ── STEP 1 : http는 봉투가 없다 ────────────────────────────────────
def raw_http_demo(host="example.com"):
    """평문(http)으로 보낼 때 회선에 실제로 흘러가는 글자를 그대로 보여준다."""
    print("STEP 1  http로 보내면 회선에 이런 글자가 그대로 흘러갑니다\n")
    body = "id=hong&pw=mypass123"
    request = (
        f"POST /login HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"\r\n"
        f"{body}"
    )
    print("-" * 62)
    print(request)
    print("-" * 62)
    print("  이 글자가 우리 집 공유기 → 통신사 → 백본을 그대로 지나갑니다.")
    print("  지나는 자리에 앉은 사람은 특별한 기술 없이 읽을 수 있습니다.\n")


# ── STEP 2~3 : 인증서 열어 보기 ────────────────────────────────────
def get_cert(host, port=443, timeout=5):
    """서버가 내미는 인증서를 가져온다."""
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as tls:
            return tls.getpeercert(), tls.version()


def field(entries, key):
    """인증서 안의 이름 항목에서 원하는 값을 꺼낸다."""
    for part in entries:
        for k, v in part:
            if k == key:
                return v
    return "-"


def days_left(not_after):
    exp = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    return (exp - datetime.now(timezone.utc)).days


def check_sites(sites):
    print("STEP 2~3  인증서 조회 — '누가 보증했나'와 '언제까지인가'\n")
    print(pad("사이트", 24) + pad("TLS", 9, True) + pad("발급한 곳", 26, True) + pad("만료까지", 12, True))
    print("-" * 71)
    rows = []
    for host in sites:
        try:
            cert, ver = get_cert(host)
            issuer = field(cert["issuer"], "organizationName")
            left = days_left(cert["notAfter"])
            rows.append((host, ver, issuer, left))
            print(pad(host, 24) + pad(ver, 9, True) + pad(issuer[:24], 26, True) + pad(f"{left}일", 12, True))
        except Exception as e:
            print(pad(host, 24) + pad("실패", 9, True) + pad(type(e).__name__[:24], 26, True) + pad("-", 12, True))
    print("-" * 71)
    print("  발급한 곳이 모두 같은 회사 이름(예: 학교·회사 이름)이라면,")
    print("  그 조직이 내 통신을 중간에서 열어 보고 다시 봉하고 있다는 뜻입니다.")
    print("  기업망에서는 흔한 설정이지만, 카페 와이파이에서 이러면 공격입니다.\n")
    return rows


# ── STEP 4 : 이름이 다르면 어떻게 되나 ────────────────────────────
def hostname_mismatch_demo(host="www.naver.com", fake="not-a-real-site.example.com"):
    print("STEP 4  같은 서버에 '다른 이름'으로 접속해 봅니다\n")
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((host, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=fake):
                print(f"  통과했습니다. 중간에서 인증서를 바꿔치기하는 장비가")
                print(f"  있을 때 이런 결과가 나옵니다. (회사·학교망에서 흔함)\n")
    except ssl.SSLCertVerificationError as e:
        print(f"  차단됨 → {e.verify_message}")
        print(f"  서버가 내민 증명서의 이름이 '{fake}' 과 달라서 연결을 끊었습니다.")
        print("  공격자는 내용을 봉하는 흉내는 내도, '내가 그 사이트다'라는")
        print("  증명서는 위조하지 못합니다. 이것이 자물쇠가 하는 일입니다.\n")
    except Exception as e:
        print(f"  오류: {type(e).__name__} {e}\n")


if __name__ == "__main__":
    raw_http_demo()
    check_sites(SITES)
    hostname_mismatch_demo()
    print("생각해 볼 것")
    print("  1. 만료까지 30일 이하인 사이트가 있었나요? 만료되면 무슨 일이 생길까요?")
    print("  2. 발급한 곳이 전부 같았나요? 그렇다면 그 이유는 무엇일까요?")
    print("  3. STEP 1의 글자를 보고도 공용 와이파이에서 http 사이트에 로그인하겠습니까?")
