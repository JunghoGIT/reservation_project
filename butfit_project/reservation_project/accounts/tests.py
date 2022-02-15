from django.test import TestCase
from django.http import HttpRequest
from rest_framework.test import APIRequestFactory
from .views import credit, get_expiration_date
import json
from rest_framework.test import APITestCase
from .serializers import CreditSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from rest_framework import status
from .models import Credit
from django.utils import timezone


# class CreditApiTest(TestCase):
"""
테스트를 위한 테스트
"""
#
#     def test_api_method_get(self):
#         factory = APIRequestFactory()
#         request = factory.get('accounts/credit')
#         response = credit(request)
#         self.assertIn(b'hello world', response.content)
#
#
#     def test_api_method_post(self):
#         factory = APIRequestFactory()
#         request = factory.post('accounts/credit', json.dumps({'test': 'test'}), content_type='application/json' )
#         response = credit(request)
#         self.assertIn(b'test', response.content,)


def create_user_and_credit():
    """
    빠른 테스트를 위한 User 및 Credit 데이터 생성
    """

    user = get_user_model().objects.create(phone_number='01011112222', email='abc@naver.com', password='123456789')
    Credit.objects.create(user=user, credit=120000, expiration_date=timezone.localdate())

    return user




class CreditApiTest(APITestCase):

    def test_get_expiration_date(self):
        """
        Credit 사용 기한 생성 함수 테스트
        """
        user = get_user_model().objects.create(phone_number='01011112222', email='abc@naver.com', password='123456789')
        data = {
            'user' : user.id,
            'credit' : 110000
        }
        credit = CreditSerializer(data=data)
        if credit.is_valid():
            date = get_expiration_date(credit)
            print(date)
        else :
            print(credit.errors)

    def test_api_create_credit(self):
        """
        Credit 생성 API 테스트
        """
        user = get_user_model().objects.create(phone_number='01011112222', email='abc@naver.com', password='123456789')
        url = reverse('accounts:credit')
        data = {
            'user' : user.id,
            'credit' : 110000
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Credit.objects.count(), 1)

    def test_api_create_credit_exist(self):
        """
        유저의 Credit이 존재 할 때 PUT(추가 구매)으로 유도하는 view 분기 테스트
        """
        user = create_user_and_credit()
        url = reverse('accounts:credit')
        data = {
            'user' : user.id,
            'credit' : 110000
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_get_credit(self):
        """
        Credit 조회 api 테스트
        """
        url = reverse('accounts:credit')
        create_user_and_credit()
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreditDetailApiTest(APITestCase):

    def test_api_get_credit_detail(self):
        """
        Credit 조회 api 테스트
        """
        create_user_and_credit()
        url = reverse('accounts:credit_detail', args=[1])
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_put_credit_detail(self):
        """
        Credit 수정(추가 구매) api 테스트
        """
        user = create_user_and_credit()
        data = {
            'user' : user.id,
            'credit' : 100000
        }
        url = reverse('accounts:credit_detail', args=[1])
        response = self.client.put(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_api_except_credit_detail(self):
        """
        존재 하지 않는 Credit에 대한 URL parameter 예외처리 테스트
        """
        url = reverse('accounts:credit_detail', args=[3])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)




