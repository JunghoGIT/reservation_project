# DRF를 이용한 수업 예약 관리 API 서버



> 수업 예약관리 사이트 구축 & 배포



## 테스트 환경 설정



### 접속 주소



> 배포 중단



### 관리자 계정



### API 테스트 환경

- **Swagger**

  - 편의성을 위해 Swagger 로그인 설정을 변경하여 Swagger 페이지에서 django 로그인, 로그아웃을 할 수 있도록 설정

    

![swagger](https://user-images.githubusercontent.com/86980966/154006985-8782a0cc-ca41-4b77-bff5-aa9a203b6353.JPG)



## API 명세서





| Index | Method | URI                              | Description                    |
| ----- | ------ | -------------------------------- | ------------------------------ |
| 1     | POST   | /acccounts/                      | 회원 가입 API                  |
| 2     | GET    | /accounts/credit                 | Credit 생성 API                |
| 3     | POST   | /accounts/credit                 | Credit 전체 조회 API           |
| 4     | GET    | /accounts/credit/{user_pk}       | 유저 Credit 조회 API           |
| 5     | PUT    | /accounts/credit/{user_pk}       | 유저 Crdit 수정(추가 구매) API |
| 6     | POST   | /lesson                          | 수업 생성 API                  |
| 7     | POST   | /reservation                     | 예약 생성 API                  |
| 8     | DELETE | /reservation/{id}                | 예약 취소 API                  |
| 9     | GET    | /reservation/list/{phone_number} | 유저의 전체 예약 정보 조회 API |
| 10    | GET    | /swagger                         | swagger API page               |



## 배포



- server : Nginx
- wsgi : gunicorn
- container : docker-compose
- cloud  : AWS EC2



## 기능 별 개발 개요





### 유저 네임 수정

- 기존 ID를 의미하는 username 대신 휴대폰 번호 사용
- 정규식 유효성 검사를 통해 유효한 휴대폰 번호 확인



### 관리자 페이지에서 모든 데이터를 등록/수정/삭제 가능



- ModelAdmin을 통해 관리자 페이지 구축



### 수업 셋팅



- Lesson 모델
  - 장소, 수업 종류, 수업 가격, 수업 정원, 현재 예약 인원, 잔여 예약, 수업 날짜, 수업 시작/종료 시간
- IsAdminUser permisson 설정으로 관리자만 생성 가능



### 크레딧 구매



- Credit 모델
  - 유저, 크레딧, 사용 가능 기간
- 사용 가능 기간 셋팅
  1. serializer 인스턴스를 파라미터로 받아 사능 가능 기간 산출 함수 셋팅
  2. 셋팅한 함수를 View에서 사용하여 값 부여 후 저장
- 유효성 
  - Credit 중복 방지
    - 환불이나 지불 로직을 생각했을 때에 유저와 1:1로 관계가 효율적일거라고 판단
    - View에서 try except 문법을 이용하여 'get or create' 구현



### 수업 예약



- Reservation 모델
  - 유저, 수업, 지불 크레딧, 지불 후 유저의 크레딧, 예약한 날짜
- 유효성 : ModelSerializer에서 validate를 통해 구현
  - 중복 예약 불가
    - serializer에서 유저와 수업 값을 추출하여 해당 데이터가 존재하는지 확인
  - 수업 날짜가 지난 수업 예약 불가
    - 수업 날짜와 예약 하는 시점 (timezone.localdate) 을 비교하여 유효성 체크
  - 크레딧 보유 여부 확인
    - 예약 유저가 보유한 크레딧과 수업의 가격을 비교하여 유효성 체크
  - 크레딧 사용 가능 기한 확인
    - 예약 유저의 크레딧 사용 가능 기한과 예약 하는 시점을 비교하여 유효성 체크
  - 수업 정원 초과 체크
    - 수업의 잔여 예약 칼럼을 사용하여 예약 가능 여부 체크
- 관계 데이터 수정
  - 예약 시 예약 유저 크레딧 감소
  - 수업의 잔여 인원과 예약 인원 수정



### 예약 취소



- CanceledReservation 모델
  - 유저, 수업, 환불 크레딧, 환불 받은 후 유저의 크레딧, 취소 날짜
- 환불 금액 산출
  - Reservation queryset을 parameter로 받은 후 관계된 Lesson의 수업 날짜를 참조하여 환불 금액을 계산 하는 함수 셋팅
  - View에서 해당 함수를 사용하여 환불 금액 산출 및 저장
- 관계 데이터 수정
  - 예약 취소시 해당 예약 데이터 삭제
  - 환불의 경우 유저의 크레딧 수정
- 유효성
  - 수업 당일 취소
    - 환불 금액 산출에서 false를 반환하여 400 Status code 응답



### 수업 예약 리스트 



- url parameter를 통해 전달 받은 유저 휴대폰 번호로 모든 예약과 예약 취소 queryset 추출
- 예약과 예약 취소 queryset를 parameter로 받아 queryset을 dictionary형태로 직렬화 해주는 함수(serializer) 셋팅
- 셋팅한 함수를 사용하여 json 형태의 데이터 생성
- 데이터에 유저의 보유 크레딧 정보 추가



### 관리자 페이지에서 수업 예약 현황 보기



- 'rangefilter' 패키지를 통해 날짜 범위로 Lesson 모델 검색 기능 추가
- Admin 필드에 Profit 필드 추가
  - 해당 Lesson에 관계된 모든 예약과 예약 취소 데이터의 지불, 환불 금액으로 최종 이익 산출
- 레코드별 관계된 예약, 예약 취소 데이터 확인
  -  모델 상세 페이지에서 하단에 관계 된 예약, 예약 취소 데이터 정보 전달
    - TabularInline 클래스 사용



![admin_1](https://user-images.githubusercontent.com/86980966/154006870-7b7d267a-2f99-490d-8b2d-5cf834edfa6b.JPG)



![admin_2](https://user-images.githubusercontent.com/86980966/154007031-0f1b78b8-e269-40ac-b524-6a4c995c70a2.JPG)
