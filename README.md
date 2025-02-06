# txtMerge

<br>

### 위메이드 확률테이블 병합 자동화 프로그램
> 1. 테스트 결과물로 생성되는 수십개의 txt파일들을 엑셀로 병합해왔음.
>
> 2. '자동화 프로그램을 만들어보자' 라는 의견 도출.
>
> 3. 프로그램 제작.

<br>
🚩 프로젝트 기간
2025년 2월 4일 ~ 2월 6일 (총 3일)

<사용된 기술 스택>
- python
- tkinter
- pandas
- sqlite

<br>

<실행파일 생성법> 실행 파일 최적화 (필수 파일만 포함)
pyinstaller --onefile --clean --noconsole main.py
<폴더구조>
📂 folder
 ├── 📂 txtPlz (자동 생성됨)
 │     └── 📂 resultDesu (자동 생성됨)
 └── 📄 main.exe
<사용방법>
1. main.exe 실행
2. "작업시작" 버튼 클릭
2-1. txtPlz 폴더로 txt파일들을 이동
3. txtPlz->resultDesu 폴더 안의 merge_result.txt파일 확인

<버전관리>

- Git / Github

