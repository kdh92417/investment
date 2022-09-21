# User Investment API

1. [프로젝트 내용](#프로젝트-내용)

   - [주요 사항](#주요-사항)

2. [개발 기간](#개발-기간)

3. [기술 스택](#기술-스택)

4. [API Endpoints](#api-endpoints)

5. [ERD](#erd)

6. [Reference Docs](#reference-docs)

<br>

## 프로젝트 내용

> 고객의 투자 데이터를 응답하는 API 개발

<br>

### 주요사항

- `Django Rest Framework`를 이용한 RESTFul API 개발
  - 화면 API 
    - 투자화면 
    - 투자상세화면
    - 보유종목 화면
  - 투자금 입금 API
    - 입금거래 정보 등록
    - 입금거래 검증 및 자산 업데이트

- `django-apscheduler` 를 이용한 매일 아침 6시 csv 데이터셋 업로드


## 개발 기간
- 요구사항 개발 및 문서작업: 2022.09.16 ~ 2022.09.21

## 기술 스택
- Backend: `Django Rest Framework`
- DB: `MySQL`
- Tool: `Github`

## API Endpoints

| **Endpoints**         	| **Method** 	| **기능** 	|
|-----------------------	|:----------:	|----------	|
| api/v1/investments/:id        	|     GET    	|  투자 화면 데이터 응답     	|
| api/v1/investments/detail/:id 	|     GET    	|  투자 상세화면 데이터 응답        	|
| api/v1/users/:id/holdings  	|     GET    	|  보유 종목화면 데이터 응답       	|
| api/v1/investments/deposit   	|    POST    	|  입금 거래정보 등록       	|
| api/v1/investments/deposit   	|     PUT    	|  거래정보 검증 및 자산업데이트       	|


## ERD
![investment](https://user-images.githubusercontent.com/58774316/191425222-7b7594ff-5c06-47ce-9594-436d02594c57.png)


## Reference Docs
- [Postman Docs](https://documenter.getpostman.com/view/11682851/2s7Z7VJuWf)
