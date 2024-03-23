from .views import *
from django.urls import path, include

urlpatterns = [

    path('movies/', MovieAPIList.as_view(), name='movie-list'),
    path('cinemas/', CinemaAPI.as_view(), name='cinema-list'),
    path('rooms/', RoomAPI.as_view(), name='room-list'),
    path('showtimes/', ShowtimeListAPI.as_view(), name='showtime-list'),
    path('showtimes/<int:id>/', ShowtimeDetailAPI.as_view(), name='showtime-detail'),
    path('showtimes/<int:id>/available-tickets/', ShowtimeTicketsAPI.as_view(), name='showtime-tickets'),
    path('seats/', SeatAPI.as_view(), name='seat-list'),
    path('tickets/', TicketAPI.as_view(), name='ticket-list'),
    path('showtimes/<int:id>/reservation_create/', ReservationCreateAPI.as_view(), name='reservation-create'),
    path('showtimes/<int:id>/feedback/', FeedbackCreateAPI.as_view(), name='create-feedback'),
]
