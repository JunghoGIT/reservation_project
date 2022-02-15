from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from .serializers import ReservationSerializer, CanceledReservationSerializer as CancelSerializer, LessonSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Reservation, Lesson, CanceledReservation
from accounts.models import Credit
from django.utils import timezone
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema


def get_refund_credit(reservation):
    """
    환불 가능 및 금액 계산

    인자 : 예약 Queryset
    """
    refund_credit = 0
    date = reservation.lesson.date
    if timezone.localdate() <= date - timezone.timedelta(days=3):
        refund_credit += reservation.payed_credit
        return refund_credit
    if timezone.localdate() <= date - timezone.timedelta(days=1):
        refund_credit += reservation.payed_credit *0.5
        return refund_credit
    if timezone.localdate() <= date:
        return False


def reservation_list_to_dict(reservations, canceled_reservations):
    """
    예약 및 예약 취소 내역 직렬화

    인자 : 예약 Queryset, 예약 취소 Queryset
    """
    dict = {}
    reservation_list = []
    canceled_reservation_list = []
    for reservation in reservations:
        reservation_list.append({
            'PK': f'{reservation.pk}',
            'Lesson': f'{reservation.lesson.pk}',
            '지불_Credit': f'{reservation.payed_credit}',
            '예약이후_Credit': f'{reservation.remained_credit}'
        })
    for canceled_reservation in canceled_reservations:
        canceled_reservation_list.append({
            'PK': f'{canceled_reservation.pk}',
            'Lesson': f'{canceled_reservation.lesson.pk}',
            '환불_Credit': f'{canceled_reservation.refund_credit}',
            '취소이후_Credit': f'{canceled_reservation.remained_credit}'
        })
    dict['예약'] = reservation_list
    dict['취소'] = canceled_reservation_list

    return dict


@swagger_auto_schema(methods=['POST'], request_body=ReservationSerializer)
@api_view(['POST'])
def create_reservation(request):
    """
    예약 생성 API

    # Data
    {
        "user": 예약 유저 PK,
        "lesson": 예약 수업 PK
    }
    """
    if request.method == 'POST':
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            lesson = Lesson.objects.get(pk=serializer.validated_data['lesson'].pk)
            lesson.remained -= 1
            lesson.reserved += 1
            lesson.save()
            user_credit = Credit.objects.get(user=serializer.validated_data['user'])
            user_credit.credit -= lesson.credit_price
            serializer.save(payed_credit=lesson.credit_price,
                            remained_credit=user_credit.credit)
            if user_credit.credit == 0:
                user_credit.delete()
            else:
                user_credit.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else :
            return Response({'fail':f'{serializer.errors}'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE'])
def cancel_reservation(request, pk):
    """
    예약 취소 API


    ## url parameter : 예약 PK
    """
    if request.method == 'DELETE':
        reservation = Reservation.objects.get(pk=pk)
        refund_credit = get_refund_credit(reservation)
        if refund_credit:
            user_credit = Credit.objects.get(user=reservation.user)
            user_credit.credit += refund_credit
            user_credit.save()
            canceled_reservation = CanceledReservation.objects.create(user=reservation.user,
                                                                      lesson=reservation.lesson,
                                                                      refund_credit=refund_credit,
                                                                      remained_credit=user_credit.credit)
            lesson = Lesson.objects.get(pk=reservation.lesson.pk)
            lesson.remained += 1
            lesson.reserved -= 1
            lesson.save()
            canceled_reservation.save()
            reservation.delete()
            serializer = CancelSerializer(canceled_reservation)
            return Response(serializer.data, status.HTTP_201_CREATED)
        else:
            return Response({'fail': '당일 취소는 불가능합니다.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_reservation_list(request, phone_number):
    """
    유저 예약 List API

    ## url parameter : 유저 Phone Number
    """
    if request.method == 'GET':
        user = get_user_model().objects.get(phone_number=phone_number)
        reservations = Reservation.objects.filter(user=user)
        canceled_reservations= CanceledReservation.objects.filter(user=user)
        data = reservation_list_to_dict(reservations,canceled_reservations)
        data['User'] = {
            '보유_Credit' : f'{user.credit_set.get(user=user).credit}'
        }
        return Response(data, status=status.HTTP_200_OK)


@swagger_auto_schema(methods=['POST'], request_body=LessonSerializer)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_lesson(request):
    """
    수업 생성 API

    # Data
    {
        "location": "장소",
        "category": "주제",
        "credit_price": "가격",
        "capacity": "수업 정원",
        "date": "2022-01-01" 형식의 수업 날짜,
        "start_at": "18:00" 형식의 수업 시작 시간,
        "finish_at": "19:00" 형식의 수업 종료 시간,
    }
    """
    if request.method == 'POST':
        serializer = LessonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(remained=serializer.validated_data['capacity'],reserved=0)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else :
            return Response({'fail': f'{serializer.errors}'}, status=status.HTTP_400_BAD_REQUEST)
