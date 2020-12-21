# CreditCard-Company-Search

(CreditCard_Korea.py)국내 카드사 지원 : UnionPay, 국내 전용 카드, 직불성 카드, Masestro,   
(VISA, 기타 등등... 추가 예정 중)

(CreditCard_World.py)국외 카드사 지원 : Maestro, Visa, Mastercard, Amex, JCB, Discover, Diners, Union, UATP, Paypal, Interpayment...

설치 해야할 모듈   :  xlrd, PyPDF2  

---
## How To?

카드 번호만으로 카드사 명 조회 간단히 조회 할 수 있도록 제작
ex) 카드 번호 필터 123**56726236 기능 


python3 CreditCard_Korea.py -i (카드번호 데이터.txt) -m (카드번호 데이터 위치)

---

**지원하는 파일 리스트:**
* txt
* csv
* xls   --> Using xlrd
* xlsx  --> Using xlrd
* rtf
* xml
* html
* json
* zip
* pdf

**지원하지 않는 파일 리스트:**
* doc
* docx
* pptx
* jpg
* gif
* png
* mp3
* mp4
* wav
