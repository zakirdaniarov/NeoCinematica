from rest_framework import generics
from rest_framework.views import Response, status, APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from .models import *
from .serializers import *


class MovieAPIList(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticated]


class CinemaAPI(generics.ListAPIView):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer
    permission_classes = [IsAuthenticated]


class RoomAPI(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]


class ShowtimeListAPI(generics.ListAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeSerializer
    permission_classes = [IsAuthenticated]


class ShowtimeDetailAPI(APIView):
    serializer_class = ShowtimeSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            showtime = Showtime.objects.all().get(id=kwargs["id"])
        except:
            return Response({'data': 'Page not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(showtime)
        feedbacks = showtime.feedbacks.all()
        feedbacks_api = FeedbackListSerializer(feedbacks, many=True)
        content = {"Showtime Info": serializer.data,
                   "Reviews": feedbacks_api.data}

        return Response(content, status=status.HTTP_200_OK)


class ShowtimeTicketsAPI(APIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            showtime = Showtime.objects.get(id=kwargs["id"])
        except Showtime.DoesNotExist:
            return Response({'error': 'Showtime not found'}, status=status.HTTP_404_NOT_FOUND)

        available_tickets = Ticket.objects.filter(show=showtime, is_reserved=False)
        serializer = self.serializer_class(available_tickets, many=True)

        content = {"Available Tickets": serializer.data}

        return Response(content, status=status.HTTP_200_OK)


class SeatAPI(generics.ListAPIView):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [IsAuthenticated]


class TicketAPI(generics.ListCreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]


class ReservationCreateAPI(APIView):
    serializer_class = ReservationCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            showtime = Showtime.objects.get(id=kwargs["id"])
        except Showtime.DoesNotExist:
            return Response({'error': 'Showtime not found'}, status=status.HTTP_404_NOT_FOUND)

        available_seats = Seat.objects.filter(room=showtime.room, ticket__is_reserved=False)

        serializer = self.serializer_class(data=request.data, context={'available_seats': available_seats})
        if serializer.is_valid():
            selected_tickets = serializer.validated_data.get('tickets')
            # Calculate total price based on the selected tickets
            if all(ticket.seat in available_seats for ticket in selected_tickets):
                # Calculate total price
                total_price = sum(ticket.price for ticket in selected_tickets)
                # Apply discount
                total_price *= 0.97

                # Create reservation
                reservation = serializer.save(user=request.user, total_price=total_price)

                # Update tickets to mark them as reserved
                for ticket in selected_tickets:
                    ticket.is_reserved = True
                    ticket.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'One or more selected tickets are not available'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedbackCreateAPI(APIView):
    serializer_class = FeedbackCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract the show ID from the URL kwargs
        show_id = kwargs.get('id')
        print(show_id)
        try:
            # Retrieve the Showtime instance
            showtime = Showtime.objects.get(id=show_id)
        except Showtime.DoesNotExist:
            return Response({'error': 'Showtime not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data, context={'user': request.user, 'show': showtime})

        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Feedback has been submitted successfully!"},
                            status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors, "message": "There is an error"},
                        status=status.HTTP_400_BAD_REQUEST)
