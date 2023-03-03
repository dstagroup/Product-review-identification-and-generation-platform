# main.py

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Body, Response, Request
import hashlib
from fastapi.encoders import jsonable_encoder
import pipeline

from elasticsearch import Elasticsearch
import preprocess
import elasticSearchApi

import pipeline



# from database import SessionLocal
import models
import jwt
import json

from typing import Optional, Union, List

from pydantic import BaseModel # 引入BaseModel

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:8085"
]

SECERT_KEY = "my_secret_key"
ALGORITHM ="HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 800

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# db = SessionLocal()



class NewUser(BaseModel):
    username: str
    password: str

class Query(BaseModel):
    userid: str
    profile: str

# class Cd(BaseModel):
#     reviews_detail: str
#
#
# class ProductDetail(BaseModel):
#     brand: str
#     title: str
#     description: str
#     feature_bullets: List[str]
#
# class PositiveReviews(BaseModel):
#     title: str
#     review: str
#     rating: int
#
# class NegativeReviews(BaseModel):
#     title: str
#     review: str
#     rating: int
#
# class Reviews(BaseModel):
#     positive_reviews: List[PositiveReviews]
#     negative_reviews: List[NegativeReviews]
#
# class OneReviews(BaseModel):
#     asin: str
#     product_detail: ProductDetail
#     reviews: Reviews
#
# class ReviewsDetail(BaseModel):
#     reviews_detail: List[OneReviews]
class GetAsins(BaseModel):
    username: str
    profile: str
    asins: List[str]

class Review(BaseModel):
    title: str
    review: str
    rating: int

class ProductReview(BaseModel):
    asin: str
    reviews: List[Review]

# class Reviews(BaseModel):
#     reviews_detail: List[ProductReview]

# # Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()



@app.post('/login')
def login(user: NewUser):
    data = jsonable_encoder(user)

    username = user.username
    password = user.password

    es = elasticSearchApi.LoginEsConnect()
    es.CreateIndex("account_info")
    result = es.CheckPwd(username, password, "account_info")
    if result['statue'] == 12:
        # encoded_jwt = jwt.encode(data, SECERT_KEY, algorithm=ALGORITHM)
        encoded_jwt = "sssssssss"
        return {
            'token': encoded_jwt
        }
    if result['statue'] == 13:
        return {"code": "0002", "message": "wrong username or password"}


    # db_user = models.User()
    # db_user.password = hashlib.new('md5', user.password.encode()).hexdigest()
    # print(db_user.password)
    # db_user.username = user.username
    # user = db.query(models.User).filter(models.User.username == user.username, models.User.password == db_user.password).first()
    # print(user)
    # if user == None:
    #     return {"code": "0002", "message": "wrong username or password"}
    # else:
    #     encoded_jwt = jwt.encode(data, SECERT_KEY, algorithm=ALGORITHM)
    #     return{'token': encoded_jwt}


# def create_user(user: NewUser, db: Session = Depends(get_db)):

@app.post('/register')
async def create_user(user: NewUser):
    try:


        username = user.username
        password = user.password

        print(username)
        print(password)
        es = elasticSearchApi.LoginEsConnect()
        # es.CreateIndex("account_info")
        es.AddUser(username, password, "account_info")

        # print("aaaaa")
        # db_user = models.User()
        # print(user.password)
        # db_user.password = hashlib.new('md5', user.password.encode()).hexdigest()
        # db_user.username = user.username
        # db.add(db_user)
        # db.commit()
        # db.refresh(db_user)
    except ArithmeticError:
        return {"code": "0002", "message": "failed"}

    return {"code": "0000", "message": "success"}

# @app.put('/reviews')
# async def get_reviews(reviews_detail: ReviewsDetail):
#
#     print(reviews_detail)
#
#     if reviews_detail:
#         return {"code": "0000", "message": "success"}
#     else:
#         return {"code": "0002", "message": "failed"}


@app.put('/reviews')
async def get_reviews(request: Request):

    data = await request.json()
    # asin = data.get('reviews_detail')[0].get('asin')
    # s = json.loads(data);
    # print(s)

    print(data)
    profile = data[0]['profile']
    username = data[0]['username']
    print(profile, username)
    # profiles = [profile]

    es = elasticSearchApi.UsrTableEsConnect()
    # es.CreateIndex('usr_profile_info')
    # result = es.AddUserProfile(username, profile,'usr_profile_info')
    # print(result)
    #
    # if result["statue"] == 14 or result["statue"] == 10:
        # es = elasticSearchApi.CommodityEsConnect()
    for item in data:

        print(item)
        result_add_commodity = pipeline.Pipeline(item)
        print(result_add_commodity)
        if result_add_commodity['statue'] != 20:
            return {"code": "0002", "message": "failed"}

    print("success")
    return {"code": "0000", "message": "success"}
    # else:
    #     return {"code": "0002", "message": "failed"}

    # if data:
    #     return return_json
    # else:
    #     return return_json


# http://localhost:8895/get_asins?username=abc&profile=cms595619877227

@app.get('/get_asins')
async def get_analysis(username: str, profile: str):
    es = elasticSearchApi.CommodityEsConnect()
    # username = 'abc'
    # profile = 'cms595619877227'
    result = es.GetAsins(username, profile)
    print(result)
    return result

@app.get('/get_username')
async def get_analysis_by_profile_userid():
    es2 = elasticSearchApi.UsrTableEsConnect()
    result = es2.GetUsrProfile('abc', 'usr_profile_info')
    print(result)
    return result[1]


@app.get('/get_one_asin')
async def get_one_asin(profile: str, username: str, asin: str, property: str):
    es = elasticSearchApi.CommodityEsConnect()
    result = es.QueryCommodity(username, profile, asin, property, -1)
    print(result)
    return result

# request: Request
# (profile: str, username: str, asins: List[str])

@app.put('/get_analysis_by_profile_userid')
async def get_analysis_by_profile_userid(request: Request):
    data = await request.json()
    print(data)
    profile = data['profile']
    username = data['username']
    asins = data['asins']
    es = elasticSearchApi.CommodityEsConnect()

    result_asins = []

    for asin in asins:
        all_asins = es.QueryCommodities(username, profile)
        print("ssssssssss", all_asins)
        for all_asin in all_asins:
            all_asin['reviews'] = es.QueryCommodityByAsin(username, profile, asin)
            all_rating = 0
            post_rating = all_asin['posrating']

            for k, v in post_rating.items():
                all_rating = all_rating + post_rating[k]
            all_asin['all_rating'] = all_rating
            print(all_rating)
            result_asins.append(all_asin)

    for i in range(len(result_asins)):
        for j in range(i + 1, len(result_asins)):
            if result_asins[i]['all_rating'] < result_asins[j]['all_rating']:
                result_asins[i], result_asins[j] = result_asins[j], result_asins[i]
    print(result_asins)

    return json.dumps(result_asins)

# @app.put('/get_analysis_by_profile_userid/{profile}')
# async def get_analysis_by_profile_userid(profile: str, username: str, asins: List[str]):
#     es = elasticSearchApi.CommodityEsConnect()
#     print("sss", profile)
#     print("hhh", username)
#
#
#     result_asins = []
#
#     for asin in asins:
#         es.QueryCommodityByAsin(username, profile, asin)
#         all_asins = es.QueryCommodities(username, profile)
#         for all_asin in all_asins:
#             all_asin['reviews'] = es.QueryCommodityByAsin(username, profile, asin)
#
#         all_rating = 0
#         post_rating = all_asin['posrating']
#         for k, v in post_rating.items():
#             all_rating = all_rating + post_rating[k]
#         all_asin['all_rating'] = all_rating
#         print(all_rating)
#         result_asins.append(all_asin)
#
#     indexx = 'abc_cms595619877227_B0BSHDVBXZ'
#     es = elasticSearchApi.CommodityEsConnect()
#     result = es.QueryCommodities('abc', 'cms595619877227', 'B0BSHDVBXZ')
#
#     print(result_asins)
#
#     return json.dumps(result_asins)


    # es = elasticSearchApi.CommodityEsConnect()
    #
    # for asin in asins:
    #     es.QueryCommodityByAsin(username, profile)
    #     all_asins = es.QueryCommodity(username, profile)
    #     for all_asin in all_asins:
    #         all_asin['reviews'] = es.QueryCommodityByAsin(username, profile, asin)
    #
    # return all_asin

# @app.put('/get_analysis_by_profile_userid/{profile}')
# async def get_analysis_by_profile_userid(profile: str, username: str):
#     es = elasticSearchApi.CommodityEsConnect()
#     es2 = elasticSearchApi.UsrTableEsConnect()
#     profiles = es2.GetUsrProfile(username, 'usr_profile_info')
#     for profile in profiles[1]:
#         es.QueryCommodity(username, profile, )
#     es.QueryCommodity()

@app.get('/asss')
async def get_revisews():
    asins = ['B0BSHDVBXZ']
    username = 'abc'
    profile = 'cms595619877227'
    es = elasticSearchApi.CommodityEsConnect()

    result_asins = []

    for asin in asins:
        es.QueryCommodityByAsin(username, profile, asin)
        all_asins = es.QueryCommodities(username, profile)
        for all_asin in all_asins:
            all_asin['reviews'] = es.QueryCommodityByAsin(username, profile, asin)


        all_rating = 0
        post_rating = all_asin['posrating']
        for k,v in post_rating.items():
            all_rating = all_rating + post_rating[k]
        all_asin['all_rating'] = all_rating
        print(all_rating)
        result_asins.append(all_asin)

    #
    # indexx = 'abc_cms595619877227_B0BSHDVBXZ'
    # es = elasticSearchApi.CommodityEsConnect()
    # result = es.QueryCommodities('abc', 'cms595619877227', 'B0BSHDVBXZ')

    for i in range(len(result_asins)):
        for j in range(i + 1, len(result_asins)):
            if result_asins[i]['all_rating'] > result_asins[j]['all_rating']:
                result_asins[i], result_asins[j] = result_asins[j], result_asins[i]

    print(result_asins)

    return json.dumps(result_asins)




@app.put('/product_reviews')
async def get_reviews(productReview: List[ProductReview]):

    print(productReview)

    if productReview:
        return {"code": "0000", "message": "success"}
    else:
        return {"code": "0002", "message": "failed"}