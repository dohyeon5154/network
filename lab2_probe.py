"""
2교시 실습 — 거리와 지연의 관계를 숫자로 확인하기
==================================================
터미널에서 tracert / traceroute 로 '홉 수'를 세어 본 뒤,
이 스크립트로 '이름 → IP 변환'과 '응답 시간'을 한 번에 모읍니다.

표준 라이브러리만 씁니다. 어느 OS에서나 그대로 동작합니다.
"""
import socket
import time
import statistics

TARGETS = [
    ("네이버 (국내)",        "www.naver.com",      443),
    ("카카오 (국내)",        "www.kakaocorp.com",  443),
    ("구글 (글로벌 CDN)",    "www.google.com",     443),
    ("깃허브 (미국)",        "github.com",         443),
    ("호주 정부 (호주)",     "www.australia.gov.au", 443),
]


def resolve(host):
    """도메인 이름이 어떤 IP로 바뀌는지 확인합니다."""
    try:
        name, aliases, ips = socket.gethostbyname_ex(host)
        return ips
    except socket.gaierror:
        return []


def tcp_rtt(host, port, timeout=3.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    t0 = time.perf_counter()
    try:
        s.connect((host, port))
        return (time.perf_counter() - t0) * 1000
    except OSError:
        return None
    finally:
        s.close()


def measure(host, port, tries=3):
    samples = [r for r in (tcp_rtt(host, port) for _ in range(tries)) if r is not None]
    return round(statistics.median(samples), 1) if samples else None


if __name__ == "__main__":
    print(f"{'대상':<20}{'IP 개수':>8}{'대표 IP':>18}{'응답시간':>10}")
    print("-" * 58)
    results = []
    for label, host, port in TARGETS:
        ips = resolve(host)
        rtt = measure(host, port) if ips else None
        results.append((label, ips, rtt))
        print(f"{label:<20}{len(ips):>8}{(ips[0] if ips else '-'):>18}"
              f"{(f'{rtt} ms' if rtt else '실패'):>10}")
    print("-" * 58)
    ok = [(l, r) for l, i, r in results if r]
    if len(ok) >= 2:
        near = min(ok, key=lambda x: x[1])
        far = max(ok, key=lambda x: x[1])
        print(f"가장 가까운 곳 {near[0]} {near[1]}ms · "
              f"가장 먼 곳 {far[0]} {far[1]}ms · 차이 {far[1]-near[1]:.1f}ms")
    print("\n생각해 볼 것")
    print("  1. IP가 여러 개로 나오는 곳이 있습니다. 왜 하나가 아닐까요? (CDN)")
    print("  2. 같은 '해외'인데 응답 시간이 크게 다른 곳이 있습니다. 왜일까요?")
    print("  3. 터미널에서 센 홉 수와 이 응답 시간을 나란히 적어 비교해 보세요.")
