from django.contrib import admin
from .models import *


admin.site.register(Movie)
admin.site.register(Cinema)
admin.site.register(Room)
admin.site.register(Seat)
admin.site.register(Showtime)
admin.site.register(Reservation)
admin.site.register(Feedback)
admin.site.register(Ticket)
