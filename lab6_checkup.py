"""
6교시 실습 — 내 환경 점검 리포트 만들기
==========================================
3교시(인증서)와 4교시(포트)에서 만든 것을 합쳐
'내 컴퓨터 보안 점검 리포트' 한 장을 뽑아냅니다.

STEP 1  자주 쓰는 사이트의 인증서를 한 번에 확인한다
STEP 2  내 컴퓨터에 열린 문을 확인한다
STEP 3  12항목 체크리스트에 답한다
STEP 4  security_report.txt 파일로 저장한다

새로 배우는 것은 없습니다. 앞에서 만든 함수를 불러 쓰기만 합니다.
그게 이 시간의 요점입니다 — 보안은 특별한 도구가 아니라 습관입니다.
"""
from datetime import datetime
from _width import pad
from lab3_tls_check import get_cert, field, days_left
from lab4_ports import PORTS, knock, assert_allowed

MY_SITES = ["www.naver.com", "www.google.com", "github.com"]

CHECKLIST = [
    ("공유기 관리자 비밀번호를 기본값에서 바꿨다", "admin/admin을 그대로 쓰는 집이 아직 많습니다"),
    ("공유기 펌웨어를 최신으로 올렸다", "제조사 앱이나 관리 페이지에서 확인"),
    ("와이파이 암호화가 WPA2 이상이다", "WEP·개방형이면 즉시 변경"),
    ("공유기 원격관리(외부 접속)를 껐다", "밖에서 관리할 일이 없다면 끄는 게 정답"),
    ("불필요한 포트포워딩·UPnP를 껐다", "4교시에서 본 그 설정입니다"),
    ("손님용 게스트 와이파이를 분리했다", "손님 기기가 집 안 기기에 닿지 않게"),
    ("OS 자동 업데이트가 켜져 있다", "가장 값싸고 효과 큰 한 가지"),
    ("브라우저를 최신 버전으로 쓴다", "대부분의 공격이 브라우저를 거칩니다"),
    ("주요 계정에 2단계 인증을 켰다", "메일 계정부터. 다른 계정 복구의 관문입니다"),
    ("비밀번호를 사이트마다 다르게 쓴다", "외우기 어렵다면 비밀번호 관리자를 쓰세요"),
    ("중요한 파일을 백업해 둔다", "랜섬웨어에 대한 사실상 유일한 대비책"),
    ("공용 와이파이에서 금융·로그인을 피한다", "3교시에서 본 그 상황입니다"),
]


def section_certs(lines):
    lines.append("[1] 자주 쓰는 사이트 인증서")
    issuers = set()
    for host in MY_SITES:
        try:
            cert, ver = get_cert(host)
            issuer = field(cert["issuer"], "organizationName")
            left = days_left(cert["notAfter"])
            issuers.add(issuer)
            mark = "  ← 곧 만료" if left <= 30 else ""
            lines.append(f"    {pad(host, 22)}{pad(ver, 9)}{pad(issuer[:22], 24)}{left}일{mark}")
        except Exception as e:
            lines.append(f"    {pad(host, 22)}조회 실패 ({type(e).__name__})")
    if len(issuers) == 1 and issuers:
        lines.append(f"    * 모든 인증서를 같은 곳({list(issuers)[0]})이 발급했습니다.")
        lines.append("      지금 쓰는 네트워크가 통신을 중간에서 열어 보고 있다는 뜻입니다.")
        lines.append("      회사·학교망이라면 정상 정책일 수 있으나, 카페라면 위험 신호입니다.")
    lines.append("")


def section_ports(lines):
    lines.append("[2] 내 컴퓨터에 열린 문")
    assert_allowed("127.0.0.1")
    opened = [p for p in sorted(PORTS) if knock("127.0.0.1", p)]
    if not opened:
        lines.append("    열린 문 없음 — 밖에서 두드릴 문이 하나도 없습니다. 좋습니다.")
        score = 0
    else:
        score = sum(PORTS[p][1] for p in opened)
        for p in opened:
            name, risk, can = PORTS[p]
            lines.append(f"    {pad(p, 6)}{pad(name, 24)}위험도 {risk}  ← {can}")
        lines.append(f"    공격면 점수 {score}")
    lines.append("")
    return score


def section_checklist(lines):
    lines.append("[3] 체크리스트")
    print("\nSTEP 3  12항목입니다. 해당하면 y, 아니면 n 을 입력하세요.\n")
    answers = []
    for i, (item, tip) in enumerate(CHECKLIST, 1):
        print(f"  [{i:>2}/12] {item}")
        print(f"         {tip}")
        ans = input("         (y/n) ").strip().lower().startswith("y")
        answers.append(ans)
        lines.append(f"    [{'v' if ans else ' '}] {item}")
    done = sum(answers)
    if done <= 3:
        grade = "위험"
    elif done <= 7:
        grade = "미흡"
    elif done <= 10:
        grade = "양호"
    else:
        grade = "우수"
    lines.append(f"    → {done} / 12  ({grade})")
    # 효과 대비 비용이 가장 좋은 항목부터 권한다
    PRIORITY = [6, 8, 10, 4, 0]     # 자동 업데이트, 2단계 인증, 백업, 포트포워딩, 공유기 비번
    todo = [i for i in PRIORITY if not answers[i]] or [i for i in range(12) if not answers[i]]
    if todo:
        lines.append("    먼저 할 것: " + CHECKLIST[todo[0]][0])
    lines.append("")
    return done, grade


def main():
    print(__doc__)
    lines = ["=" * 66,
             f"  보안 점검 리포트   {datetime.now():%Y-%m-%d %H:%M}",
             "=" * 66, ""]
    print("STEP 1  인증서 확인 중...")
    section_certs(lines)
    print("STEP 2  열린 문 확인 중...")
    port_score = section_ports(lines)
    done, grade = section_checklist(lines)

    lines.append("[4] 요약")
    lines.append(f"    체크리스트 {done}/12 ({grade}) · 공격면 점수 {port_score}")
    lines.append("    가장 값싸고 효과 큰 세 가지:")
    lines.append("      1) OS 자동 업데이트 켜기")
    lines.append("      2) 주요 계정 2단계 인증 켜기")
    lines.append("      3) 안 쓰는 문(포트)·포트포워딩 닫기")
    lines.append("")
    lines.append("    이상 징후가 보이면 순서는 이것입니다:")
    lines.append("      1 격리(랜선·와이파이 끄기) → 2 기록(화면 사진) → 3 신고(118) → 4 복구(백업)")
    lines.append("=" * 66)

    report = "\n".join(lines)
    print("\n" + report)
    with open("security_report.txt", "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print("\nsecurity_report.txt 파일로 저장했습니다.")


if __name__ == "__main__":
    main()
