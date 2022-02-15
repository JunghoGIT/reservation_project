from django.shortcuts import redirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import logout as auth_logout
from .models import Credit
from .serializers import CreditSerializer, UserSerializer
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from django.contrib.auth import get_user_model


class UserCreate(generics.CreateAPIView):
    """
    회원 가입 API

    # Data
    {
        "phone_number": "특수기호를 제외한 전화번호",
        "email": "이메일",
        "name": "이름",
        "password": "비밀번호"
    }
    """
    permission_classes = [AllowAny]
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


def get_expiration_date(serializer):
    """
    Credit 금액에 따라 사용 가능 기간을 반환하는 함수
    인자 : Credit Serializer 인스턴스
    """
    now = timezone.localdate()
    if serializer.validated_data['credit'] < 100000 :
        return now + timedelta(days=30)
    elif serializer.validated_data['credit'] < 200000 :
        return now + timedelta(days=60)
    elif serializer.validated_data['credit'] < 300000 :
        return now + timedelta(days=90)
    else :
        return now + timedelta(days=120)


@swagger_auto_schema(methods=['POST'], request_body=CreditSerializer)
@api_view(['GET', 'POST'])
def credit(request):
    """
    Credit 생성 및 전체 조회 API

    # 생성 [POST]
    # Data
    {
        "user": 유저Pk,
        "credit": 구매할 Credit 수량,
    }
    """
    # 조회
    if request.method == 'GET' :
        queryset = Credit.objects.all()
        serializer = CreditSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    # 생성
    elif request.method == 'POST':
        serializer = CreditSerializer(data=request.data)
        if serializer.is_valid():
            # 해당 유저의 Credit이 존재할 경우 생성이 아닌 수정임으로 'POST' 보다는 'PUT'이나 'PATCH'가 적절한 method라고 판단
            try :
                Credit.objects.get(user_id = serializer.validated_data['user'])
                return Response({'fail': '유저의 credit이 존재합니다. PUT method를 사용해주세요.'},status=status.HTTP_400_BAD_REQUEST)

            except Credit.DoesNotExist :
                date_time = get_expiration_date(serializer) # 사용 가능 기간 구하기
                serializer.save(expiration_date=date_time)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else :
            return Response({'fail': f'{serializer.errors}'}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(methods=['PUT'], request_body=CreditSerializer)
@api_view(['GET','PUT'])
def credit_detail(request,user_pk):
    """
    Credit 조회 및 수정(추가 구매) API

    # 수정 [PUT]
    ## Data
    {
        "user": 유저Pk,
        "credit": 구매할 Credit 수량,
    }
    ## URL parameter: User PK
    """
    try:
        credit = Credit.objects.get(user=user_pk)
        if request.method == 'PUT':
            serializer = CreditSerializer(credit, data=request.data)
            if serializer.is_valid():
                serializer.validated_data['credit'] += credit.credit
                serializer.validated_data['expiration_date'] = get_expiration_date(serializer)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else :
                return Response({'fail': f'{serializer.errors}'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'GET':
            serializer = CreditSerializer(credit)
            return Response(serializer.data, status=status.HTTP_200_OK)

    except Credit.DoesNotExist:
        return Response({'fail': 'Credit이 존재하지 않습니다.'},status=status.HTTP_404_NOT_FOUND)



def logout(request):
    auth_logout(request)
    return redirect('schema-swagger-ui')