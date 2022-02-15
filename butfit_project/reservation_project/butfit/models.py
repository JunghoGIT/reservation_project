from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

class Lesson(models.Model):
    location = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    credit_price = models.IntegerField()
    capacity = models.IntegerField()  # 수업 예약 최대 정원
    reserved = models.IntegerField(blank=True, null=True)  # 현재 예약 수
    remained = models.IntegerField(blank=True, null=True)  # 잔여 예약
    date = models.DateField()
    start_at = models.TimeField()
    finish_at = models.TimeField()


class Reservation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    payed_credit = models.IntegerField(blank=True)  # 지불한 credit 차감 내역 표현을 위해 view에서 음수로 레코드에 저장
    reserved_at = models.DateField(auto_now_add=True,)
    remained_credit = models.IntegerField(blank=True, null=True)


class CanceledReservation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    refund_credit = models.IntegerField(blank=True)  # 환불된 credit 내역
    canceled_at = models.DateField(auto_now_add=True,)
    remained_credit = models.IntegerField(blank=True, null=True)

