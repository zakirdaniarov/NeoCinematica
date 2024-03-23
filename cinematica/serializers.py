from rest_framework import serializers
from .models import *


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"


class CinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class ShowtimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Showtime
        fields = '__all__'


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'


class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["feedback"]

    def create(self, validated_data):
        user = self.context['user']
        show = self.context['show']
        feedback = Feedback.objects.create(user=user, show=show, **validated_data)
        return feedback


class FeedbackListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


#used in my-page endpoint in authorization
class ReservationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'


class ReservationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['tickets', 'payment_way']

    def __init__(self, *args, **kwargs):
        # Get available seats from context
        available_seats = kwargs.pop('available_seats', None)
        super(ReservationCreateSerializer, self).__init__(*args, **kwargs)

        # Dynamically set seat choices based on available seats
        if available_seats:
            self.fields['tickets'].queryset = Ticket.objects.filter(seat__in=available_seats, is_reserved=False)
