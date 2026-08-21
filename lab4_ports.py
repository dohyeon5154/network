"""
4교시 실습 — 문은 몇 개나 열려 있나
======================================
STEP 1  안전 규칙을 확인한다  (이 스크립트가 강제로 막습니다)
STEP 2  내 PC 자신(127.0.0.1)의 문을 두드려 본다
STEP 3  공격면 점수를 계산한다
STEP 4  우리 집 공유기의 문을 확인한다  (본인 소유 장비만)

⚠ 매우 중요
  포트 확인은 '내 소유 기기'에만 허용됩니다.
  남의 서버·회사망·공용 와이파이 장비를 대상으로 하면
  정보통신망법 위반이며 처벌 대상입니다.
  이 스크립트는 허용되지 않은 대상을 입력하면 즉시 종료됩니다.
"""
import socket
import ipaddress
import sys
from _width import pad

# 포트 번호 : (용도, 위험도 1~5, 열려 있으면 가능한 일)
PORTS = {
    22:   ("원격 접속 (SSH)",      4, "명령어로 컴퓨터 전체를 조작"),
    80:   ("웹 (HTTP)",            2, "평문 웹 요청 수신"),
    139:  ("파일 공유 (NetBIOS)",  4, "공유 폴더 목록 열람"),
    443:  ("웹 (HTTPS)",           1, "암호화된 웹 요청 수신"),
    445:  ("파일 공유 (SMB)",      5, "파일 열람·암호화 (랜섬웨어 단골 통로)"),
    554:  ("CCTV 영상 (RTSP)",     4, "집 안 카메라 영상 실시간 열람"),
    3389: ("원격 데스크톱 (RDP)",  5, "내 화면을 그대로 조작"),
    5900: ("화면 공유 (VNC)",      4, "화면 실시간 열람·조작"),
    8080: ("웹 관리 화면",         3, "관리자 페이지 접근"),
    9100: ("네트워크 프린터",      2, "임의 문서 출력·인쇄 기록 열람"),
}


# ── STEP 1 : 안전 장치 ─────────────────────────────────────────────
def assert_allowed(target):
    """내 소유로 볼 수 있는 대상만 통과시킨다. 아니면 프로그램을 끝낸다."""
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(target))
    except Exception:
        sys.exit(f"[중단] 주소를 확인할 수 없습니다: {target}")

    if ip.is_loopback:
        return str(ip), "내 컴퓨터 자신"
    if ip.is_private:
        return str(ip), "우리 집 내부 장비"

    sys.exit(
        "\n[중단] 허용되지 않은 대상입니다: " + str(ip) + "\n"
        "  이 실습은 127.0.0.1(내 PC)과 우리 집 내부 장비(192.168.x.x 등)에만\n"
        "  허용됩니다. 외부 주소를 대상으로 포트를 확인하는 행위는\n"
        "  정보통신망법 위반이며 처벌 대상입니다.\n"
    )


# ── STEP 2 : 문 두드리기 ───────────────────────────────────────────
def knock(host, port, timeout=0.6):
    """문이 열려 있는지 확인한다. 연결만 해보고 바로 끊는다."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def scan(target):
    ip, kind = assert_allowed(target)
    print(f"\n대상: {target} ({ip}) — {kind}")
    print(pad("포트", 6, True) + "  " + pad("용도", 24) + pad("상태", 8) + pad("위험도", 8, True))
    print("-" * 48)
    opened = []
    for port in sorted(PORTS):
        name, risk, _ = PORTS[port]
        is_open = knock(ip, port)
        if is_open:
            opened.append(port)
        print(pad(port, 6, True) + "  " + pad(name, 24) +
              pad("열림" if is_open else "닫힘", 8) + pad(risk, 8, True))
    print("-" * 48)
    return opened


# ── STEP 3 : 공격면 점수 ───────────────────────────────────────────
def attack_surface(opened, exposed_to_internet=False):
    score = sum(PORTS[p][1] for p in opened) * (2 if exposed_to_internet else 1)
    if score == 0:
        grade = "안전 — 밖에서 두드릴 문이 없습니다"
    elif score <= 8:
        grade = "주의 — 정말 필요한 문인지 확인하세요"
    elif score <= 20:
        grade = "위험 — 고위험 문이 열려 있습니다"
    else:
        grade = "매우 위험 — 사실상 공개된 상태"
    print(f"열린 문 {len(opened)}개 · 공격면 점수 {score} → {grade}")
    for p in opened:
        name, risk, can = PORTS[p]
        print("   " + pad(p, 5, True) + "  " + pad(name, 24) + "← " + can)
    if not opened:
        print("   일반 가정용 PC는 밖에서 들어오는 문이 하나도 필요 없습니다.")
        print("   웹 서핑·유튜브·게임은 모두 내가 먼저 나가서 가져오는 방식입니다.")
    return score


if __name__ == "__main__":
    print(__doc__)
    input("위 내용을 읽었으면 엔터를 누르세요. ")

    print("\nSTEP 2  내 컴퓨터 자신의 문 확인")
    opened = scan("127.0.0.1")

    print("\nSTEP 3  공격면 점수")
    attack_surface(opened)

    print("\nSTEP 4  우리 집 공유기 확인 (건너뛰려면 그냥 엔터)")
    print("  1교시에서 적어 둔 '기본 게이트웨이' 주소를 입력하세요.")
    gw = input("  게이트웨이 IP: ").strip()
    if gw:
        gwo = scan(gw)
        attack_surface(gwo, exposed_to_internet=False)
        print("\n  공유기에서 '포트포워딩'을 켜면 위 문들이 인터넷 전체에 공개되어")
        print("  점수가 두 배가 됩니다. 지금 관리 페이지에서 확인해 보세요.")
