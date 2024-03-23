from django.db import models
from authorization.models import User
from django.utils import timezone

# Create your models here.


class Movie(models.Model):
    movie_name = models.CharField(max_length=300)
    release_date = models.DateField(auto_now_add=True)
    genre = models.CharField(max_length=200)
    duration = models.PositiveIntegerField()

    def __str__(self):
        return self.movie_name


class Cinema(models.Model):
    cinema_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    start_time = models.TimeField(auto_now_add=False)
    end_time = models.TimeField(auto_now_add=False)
    contacts = models.CharField(max_length=300)

    def __str__(self):
        return self.cinema_name


class Room(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)
    room_name = models.CharField(max_length=200)
    room_capacity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.cinema}-{self.room_name}'


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    showtime_date = models.DateTimeField(verbose_name='Show time', default=timezone.now)

    def __str__(self):
        return f'{self.movie} in room {self.room} at {self.showtime_date} '


class Seat(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    seat_row = models.PositiveIntegerField()
    seat_column = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.room}, row: {self.seat_row}, place: {self.seat_column}'


class Ticket(models.Model):
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    show = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    is_reserved = models.BooleanField(default=False)

    def __str__(self):
        return f"Ticket in {self.seat} for {self.show} is {self.price} som and is reversed is {self.is_reserved} "


class Reservation(models.Model):
    CATEGORY_PRODUCT = (
        ('credit card', 'credit card'),
        ('bank transfer', 'bank transfer'),
        ('cash', 'cash'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations")
    tickets = models.ManyToManyField(Ticket, related_name="reservations")
    payment_way = models.CharField(max_length=200, choices=CATEGORY_PRODUCT)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.PositiveIntegerField()

    def __str__(self):
        return f"Reservation {self.id} by {self.user.username} at {self.created_at}"


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    show = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name="feedbacks")
    feedback = models.TextField(max_length=1000)
    created_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Feedback from {self.user.username} for show {self.show}'

