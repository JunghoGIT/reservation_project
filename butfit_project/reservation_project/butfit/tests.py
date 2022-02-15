from django.test import TestCase
from rest_framework.test import APITestCase
from .models import Lesson, Reservation, CanceledReservation
from django.shortcuts import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import Credit
from django.utils import timezone


def create_user_and_credit(credit,set_timedelta=None):
    """
    유저와 Credit 데이터를 생성하기 위한 함수

    인자
        - credit : 구매할 크레딧 액수
        - set_timedelta : 유효성 체크를 위한 유효기간 일 수
    """

    user = get_user_model().objects.create(phone_number='01012345678',
                                           name='테스트',
                                           email='test@naver.com',
                                           password='123456789')
    if set_timedelta is None:
        Credit.objects.create(user=user,
                              credit=credit,
                              expiration_date=timezone.localdate() + timezone.timedelta(days=3))
    else:
        Credit.objects.create(user=user,
                              credit=credit,
                              expiration_date=timezone.localdate() - timezone.timedelta(days=set_timedelta))

    return user


def create_lesson(credit,capacity, set_timedelta=None):
    """
    수업 모델 데이터를 생성하기 위한 함수

    인자
        - credit : 수업의 가격
        - capacity : 수업의 최대 정원
        - set_timedelta : 수업 날짜 조정
    """

    if set_timedelta is None:
        lesson = Lesson.objects.create(location='서울',
                                       category='어깨',
                                       credit_price=credit,
                                       capacity=capacity,
                                       date=timezone.localdate(),
                                       start_at=timezone.localtime(),
                                       finish_at=timezone.localtime())
    else:
        lesson = Lesson.objects.create(location='서울',
                                       category='어깨',
                                       credit_price=credit,
                                       capacity=capacity,
                                       date=timezone.localdate()-timezone.timedelta(days=set_timedelta),
                                       start_at=timezone.localtime(),
                                       finish_at=timezone.localtime())

    return lesson


def create_reservation(user,lesson):
    """
    예약 생성을 위한 함수
    인자
        - user : User queryset
        - lesson : Lesson queryset
    """
    reservations = Reservation.objects.create(user=user,
                                              lesson=lesson,
                                              payed_credit= lesson.credit_price,
                                              remained_credit = 10)
    return reservations


def create_lesson_second(remained=10,timedelta=3):
    """
    수업 모델 데이터를 생성하기 위한 함수

    인자
        - remained : 수업의 예약 가능 수
        - set_timedelta : 수업 날짜 조정
    """
    lesson = Lesson.objects.create(location='서울',
                                   category='어깨',
                                   credit_price=30000,
                                   capacity=10,
                                   reserved=0,
                                   remained=remained,
                                   date=timezone.localdate() + timezone.timedelta(days=timedelta),
                                   start_at=timezone.localtime(),
                                   finish_at=timezone.localtime())
    return lesson

class ReservationApiTest(APITestCase):
    data = {
        'user': 1,
        'lesson': 1
    }

    def test_api_reservation_validate_exist(self) :
        """
        중복 예약 방지 유효성 테스트
        """
        user = create_user_and_credit(100000)
        lesson = create_lesson(50000,10)
        create_reservation(user, lesson)

        url = reverse('butfit:reservation')
        response = self.client.post(url, self.data, format='json')
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_reservation_validate_lack_credit(self):
        """
        Creidt 보유 여부 유효성 테스트
        """
        create_user_and_credit(60000)
        create_lesson(70000, 10)
        url = reverse('butfit:reservation')
        response = self.client.post(url, self.data, format='json')
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_reservation_validate_period_class(self):
        """
        날짜가 지난 수업에 대한 예약 유효성 테스트
        """
        create_user_and_credit(60000)
        create_lesson(50000, 10, 1)
        url = reverse('butfit:reservation')
        response = self.client.post(url, self.data, format='json')
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_reservation_validate_period_credit(self):
        """
        유저의 Credit 사용 가능 기한 유효성 테스트
        """
        create_user_and_credit(60000,1)
        create_lesson(50000, 10)
        url = reverse('butfit:reservation')
        response = self.client.post(url, self.data, format='json')
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_reservation_validate_remain_number(self):
        """
        수업의 예약 가능 인원 유효성 테스트
        """
        create_user_and_credit(60000)
        create_lesson_second(0)
        url = reverse('butfit:reservation')
        response = self.client.post(url, self.data, format='json')
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_reservation_create(self):
        """
        예약 생성 API 테스트
        """
        create_user_and_credit(60000)
        create_lesson_second(10)
        url = reverse('butfit:reservation')
        response = self.client.post(url, self.data, format='json')
        credit = Credit.objects.get(pk=1)
        lesson = Lesson.objects.get(pk=1)
        # print(credit.credit)
        # print(lesson.remained)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_api_reservation_cancel(self):
        """
        예약 취소 API 테스트
        """
        create_user_and_credit(60000)
        create_lesson_second(10, 2)
        url_reserve = reverse('butfit:reservation')
        self.client.post(url_reserve, self.data, format='json')
        url_cancel = reverse('butfit:cancel_reservation', args=[1])
        response = self.client.delete(url_cancel)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_api_reservation_list(self):
        """
        유저의 예약 및 예약 취소 내역 조회 API 테스트
        """
        create_user_and_credit(60000)
        create_lesson_second(10, 2)
        url_reserve = reverse('butfit:reservation')
        self.client.post(url_reserve, self.data, format='json')
        url_cancel = reverse('butfit:cancel_reservation', args=[1])
        self.client.delete(url_cancel)
        url_list = reverse('butfit:user_reservation_list', args=['01012345678'])
        response = self.client.get(url_list)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_api_reservation_list_multiple(self):
        """
        유저의 예약 및 예약 취소 내역 조회 API 다수 데이터 직렬화 테스트
        """
        user = create_user_and_credit(60000)
        lesson = create_lesson_second(10, 2)
        CanceledReservation.objects.create(user=user,
                                           lesson=lesson,
                                           refund_credit=10000,
                                           remained_credit=10)
        url_reserve = reverse('butfit:reservation')
        self.client.post(url_reserve, self.data, format='json')
        url_cancel = reverse('butfit:cancel_reservation', args=[1])
        self.client.delete(url_cancel)
        url_list = reverse('butfit:user_reservation_list', args=['01012345678'])
        response = self.client.get(url_list)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_create_lesson(self):
        """
        수업 생성 API 테스트
        """
        data ={
            'location': '서울',
            'category': '다이어트',
            'credit_price': 30000,
            'capacity': 20,
            'date': '2022-01-02',
            'start_at': '18:00',
            'finish_at': '20:00',
        }
        url = reverse('butfit:create_lesson')
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

