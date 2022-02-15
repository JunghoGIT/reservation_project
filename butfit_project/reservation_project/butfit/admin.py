from django.contrib import admin
from .models import Lesson, Reservation,CanceledReservation
from rangefilter.filter import DateRangeFilter


class ReservationInline(admin.TabularInline):
    model = Reservation
    exclude =[
        'remained_credit'
    ]
    readonly_fields = ('reserved_at',)


class CanceledReservationnInline(admin.TabularInline):
    model = CanceledReservation
    exclude =[
        'remained_credit'
    ]
    readonly_fields = ('canceled_at',)


@admin.register(Lesson)
class LessonClassAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'location',
        'category',
        'credit_price',
        'capacity',
        'reserved',
        'remained',
        'date',
        'profit',
    ]
    list_filter = [('date', DateRangeFilter)]
    search_fields = ['date']
    inlines = [ReservationInline,CanceledReservationnInline]

    def profit(self,lesson):
        profit = 0
        reservation_qs = Reservation.objects.filter(lesson=lesson)
        canceled_qs = CanceledReservation.objects.filter(lesson=lesson)
        for reservation in reservation_qs:
            profit += reservation.payed_credit
        for canceled in canceled_qs:
            profit += lesson.credit_price - canceled.refund_credit
        return profit


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'lesson',
    ]


@admin.register(CanceledReservation)
class CanceledReservationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'lesson',
    ]


