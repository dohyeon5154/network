# 네트워크와 보안 · 실습 코드

## 1. 준비 (수업 전에 미리)

1. Python 3.10 이상 설치 — https://www.python.org/downloads/
   Windows 설치 화면에서 **"Add Python to PATH"** 를 반드시 체크하세요.
2. 터미널을 열고 확인
   - Windows: `python --version`
   - Mac/Linux: `python3 --version`
3. 이 폴더를 통째로 바탕화면에 두고 터미널에서 그 폴더로 이동
   - Windows: `cd %USERPROFILE%\Desktop\netsec`
   - Mac/Linux: `cd ~/Desktop/netsec`

**설치할 라이브러리가 없습니다.** 전부 파이썬 기본 기능만 씁니다.

## 2. 파일

| 파일 | 교시 | 하는 일 |
|---|---|---|
| `lab2_probe.py` | 2교시 | 도메인 → IP 변환과 응답 시간 측정 |
| `lab3_tls_check.py` | 3교시 | 평문 요청 확인, 인증서 발급자·만료일 조회 |
| `lab4_ports.py` | 4교시 | 내 PC와 우리 집 공유기의 열린 문 확인 |
| `lab5_url_check.py` | 5교시 | 주소에서 진짜 주인 찾기, 메일 헤더 판독 |
| `lab6_checkup.py` | 6교시 | 3·4교시를 합쳐 점검 리포트 한 장 생성 |
| `sample_headers.txt` | 5교시 | 실습용 메일 헤더 예시 3통 |
| `_width.py` | 공통 | 한글 표 정렬 도우미 (직접 실행하지 않음) |

1교시는 코드 없이 **터미널 명령어만** 사용합니다.

## 3. 실행

```
python lab3_tls_check.py          (Windows)
python3 lab3_tls_check.py         (Mac/Linux)
```

파일은 **모두 같은 폴더**에 있어야 합니다. 다른 곳에 두면
`ModuleNotFoundError: No module named '_width'` 오류가 납니다.

## 4. ⚠ 반드시 지켜야 할 것

`lab4_ports.py`는 **내 소유 기기에만** 사용할 수 있습니다.

- 허용: `127.0.0.1`(내 컴퓨터), 우리 집 공유기와 내부 장비(192.168.x.x 등)
- 금지: 외부 서버, 회사·학교 네트워크, 공용 와이파이 장비

남의 장비를 대상으로 포트를 확인하는 행위는 **정보통신망법 위반**이며
처벌 대상입니다. 스크립트에 안전장치가 들어 있어 외부 주소를 넣으면
즉시 종료되지만, **장치를 우회하지 마세요.**

## 5. 잘 되는지 미리 확인

```
python lab5_url_check.py
```

주소가 조각나며 "진짜 주인"이 표시되면 준비 완료입니다.
