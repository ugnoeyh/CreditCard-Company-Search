# CreditCard-Company-Search

(CreditCard_Korea.py)
국내 카드사 지원 : UnionPay, 국내 전용 카드, 직불성 카드, Masestro, JCB, American Express, Diners  
- 카드사 (법인포함) : KB, 신한, BC, 롯데, 현대, 삼성, 외한, 하나(외한), 씨티, 수협, 제주, 농협   
  
  
(CreditCard_World.py)
국외 카드사 지원 : Maestro, Visa, Mastercard, Amex, JCB, Discover, Diners, Union, UATP, Paypal, Interpayment...

설치 해야할 모듈   :  xlrd, PyPDF2  

---
## How To?

카드 번호만으로 카드사 명 조회 간단히 조회 할 수 있도록 제작

---  
## 사용법  

#### 1. 모듈 설치
pip install -r requirements.txt
  
#### 2. 국내카드 조회시
python3 CreditCard_Korea.py -i (카드번호 데이터.txt) [ -m (카드번호 데이터 위치) ] 선택

#### 3. 국외카드 조회시
python3 CreditCard_World.py -i (카드번호 데이터.txt) [ -m (카드번호 데이터 위치) ] 선택
  
---  
## 파일 지원    
  
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
