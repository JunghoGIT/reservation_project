from rest_framework import serializers
from .models import Reservation, Lesson, CanceledReservation
from accounts.models import Credit
from django.utils import timezone
from django.contrib.auth import get_user_model


class ReservationSerializer(serializers.ModelSerializer):

    def validate(self, data):
        user_credit = Credit.objects.get(user=data['user'])
        lesson = Lesson.objects.get(pk=data['lesson'].pk)
        try:
            Reservation.objects.get(lesson=data['lesson'], user=data['user'])
            raise serializers.ValidationError({'reservation': '해당 예약이 존재합니다.'})
        except Reservation.DoesNotExist:
            if lesson.date < timezone.localdate():  # 지난 수업에 대한 예약 유효성 체크
                raise serializers.ValidationError({'lesson': '지난 수업입니다.'})
            if user_credit.credit <= lesson.credit_price:  # credit 보유 여부 체크
                raise serializers.ValidationError({'credit': '보유 Credit이 부족합니다.'})
            if user_credit.expiration_date < timezone.localdate():  # credit 사용 가능 기한 체크
                raise serializers.ValidationError({'credit': 'credit 사용 가능 기한이 지났습니다.'})
            if lesson.remained - 1 < 0:  # 수업 정원 초과 체크
                raise serializers.ValidationError({'reservation': '예약 가능 인원을 초과했습니다.'})
        return data

    class Meta:
        model = Reservation
        fields = [
            'pk',
            'user',
            'lesson',
            'payed_credit',
            'remained_credit',
        ]


class CanceledReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CanceledReservation
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'pk',
            'location',
            'category',
            'credit_price',
            'capacity',
            'reserved',
            'remained',
            'date',
            'start_at',
            'finish_at',
        ]