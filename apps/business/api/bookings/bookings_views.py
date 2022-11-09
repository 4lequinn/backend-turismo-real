from apps.base.models.db_models import Reserva, Servicio, Movilizacion, DetServMov, DetProyecto, CheckIn, CheckOut, Recepcionista
from apps.business.api.general_filters import BookingFilter
from apps.business.api.bookings.bookings_serializers import BookingDatesSerializer, BookingDetailSerializer, BookingListSerializer, BookingReceptionistSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from apps.base.stored_procedures import genericDelete
from db_routers.permissions.db_connection import oracle_connection
from rest_framework.decorators import action

class BookingViewSet(viewsets.GenericViewSet):
    #authentication_classes = ()
    #permission_classes = ()
    serializer_class = BookingListSerializer
    filterset_class  = BookingFilter
    search_fields = ['id_cli__id__id']
    ordering_fields = ['id', 'id_cli__id__id'] 
    ordering = ['id']

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return BookingDetailSerializer
        elif self.action in ["list"]:
            return BookingListSerializer
        return self.serializer_class

    def get_queryset(self, pk = None):
        if pk is None:
            return self.get_serializer().Meta.model.objects.filter(estado = 'ACTIVO')
        return self.get_serializer().Meta.model.objects.filter(id = pk, estado = 'ACTIVO').first()

    def list(self, request):
        # with filter
        queryset = self.filter_queryset(self.get_queryset())

        # pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk = None):
        queryset = Reserva.objects.filter(estado = 'ACTIVO')
        booking = get_object_or_404(queryset, pk=pk)
        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data)

    @action(methods=['GET'],detail=False, url_path = 'search-dates')
    def search_dates(self,request):
        # Recibimos el query param de la petición GET
        pk = request.query_params.get('pk','')
        booking = Reserva.objects.filter(id_viv__id__iexact = pk, estado = 'ACTIVO')
        if booking:
            serializer = BookingDatesSerializer(booking, many = True)
            return Response(serializer.data,status = status.HTTP_200_OK)
        return Response(
            {
                'message':'No hay fechas.'
            },
            status = status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        booking = self.get_queryset().filter(id = pk).update(estado = 'INACTIVO')
        try:
            services = Servicio.objects.filter(id_reserva = pk)
            id_list = []
            for service in services:
                id_list.append(service.id)
            DetServMov.objects.filter(id_mov__in = id_list).update(estado = 'INACTIVO')
        except Exception as e:
            print(e)    
            pass
        if booking:
            return Response(
                {'message':'¡Reserva eliminada!.','value' : 1}, status = status.HTTP_200_OK)
        return Response(
            {
                'message':'¡La reserva no se pudo eliminar!',
                'value' : 0
            },
            status = status.HTTP_400_BAD_REQUEST) 

    @action(methods=['GET'], detail=False, url_path='booking-receptionist')
    def get_booking_receptionist(self,request):
        pk = request.query_params.get('pk','')
        if pk == '':
            return Response( {'message' : 'Debe mandar un pk.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            project_detail = DetProyecto.objects.filter(id_emp = pk).first()
            receptionist = Recepcionista.objects.get(id = project_detail.id_emp)
            bookings = Reserva.objects.filter(id_viv = project_detail.id_viv, estado = 'ACTIVO')
        except: 
            return Response({'message' : 'No se encuentra un proyecto asociado a dicho recepcionista.'})
        
        receptionist_list = []
        
        for booking in bookings:
            check_in, check_out = CheckIn(), CheckOut()
            try:
                check_in = CheckIn.objects.get(id_res = booking.id)
            except:
                pass

            try: 
                check_out = CheckOut.objects.get(id_res = booking.id)
            except:
                pass

            if check_in.estado_checkin in('PENDIENTE''PAGADO') and check_out.estado_checkout == 'PENDIENTE':
                receptionist_list.append(booking)
        serializer = BookingReceptionistSerializer(receptionist_list, many = True)
        
        return Response(serializer.data,status = status.HTTP_200_OK)

