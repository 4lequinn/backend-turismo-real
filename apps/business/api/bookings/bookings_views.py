from apps.base.models.db_models import Reserva, Servicio, Movilizacion, DetServMov, DetProyecto, CheckIn, CheckOut, Recepcionista
from apps.business.api.general_filters import BookingFilter, CardFilter
from apps.business.api.bookings.bookings_serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from apps.base.stored_procedures import genericDelete, generate_fine
from db_routers.permissions.db_connection import oracle_connection
from rest_framework.decorators import action
from apps.users.models import User


class BookingViewSet(viewsets.GenericViewSet):
    #authentication_classes = ()
    #permission_classes = ()
    serializer_class = BookingListSerializer
    filterset_class  = BookingFilter
    search_fields = ['id_cli__id__id']
    ordering_fields = ['id', 'id_cli__id__id'] 
    ordering = ['-id']

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return BookingDetailSerializer
        elif self.action in ["list"]:
            return BookingListSerializer
        return self.serializer_class

    def get_queryset(self, pk = None):
        if pk is None:
            return self.get_serializer().Meta.model.objects.filter()
        return self.get_serializer().Meta.model.objects.filter(id = pk).first()

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
        queryset = Reserva.objects.filter()
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

    def delete_booking(self, pk = None, state = 'CANCELADO'):
        booking = self.get_queryset().filter(id = pk).update(estado = 'INACTIVO')
        try:
            services = Servicio.objects.filter(id_reserva = pk)
            id_list = []
            for service in services:
                id_list.append(service.id)
            DetServMov.objects.filter(id_mov__in = id_list).update(estado = 'INACTIVO')
            checkout = CheckOut.objects.filter(id_res = pk).first()
            checkout.estado_checkout = state
            checkout.save()

        except Exception as e:
            print(e)    
        return booking

    def destroy(self, request, pk=None):
        booking = self.delete_booking(pk)
        if booking:
            # Cancelamos Checkin
            checkin = CheckIn.objects.filter(id_res = pk).first()
            checkin.estado_checkin = 'CANCELADO'
            checkin.save()
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
            bookings = Reserva.objects.filter(id_viv = project_detail.id_viv, estado = 'ACTIVO').order_by('-id')
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

            if check_in.estado_checkin in('PENDIENTE','COMPLETADO') and check_out.estado_checkout == 'PENDIENTE':
                receptionist_list.append(booking)
        serializer = BookingDetailSerializer(receptionist_list, many = True)
        
        return Response(serializer.data,status = status.HTTP_200_OK)

    @action(methods=['PUT'],detail=True, url_path='change-checkin')
    def change_check_in(self,request, pk = None):
        if pk is None:
            return Response({'message':'Debe enviar un pk'}, status = status.HTTP_400_BAD_REQUEST)
        
        checkin, reserva = None, None
        try:
            reserva = Reserva.objects.get(id = pk)
            checkin = CheckIn.objects.get(id_res = reserva.id) 
            persona = Persona.objects.get(id = reserva.id_cli.id.id)    
        except:
            pass

        if not checkin:
            return Response({'message':'No existe el Check IN'}, status = status.HTTP_400_BAD_REQUEST)
        
        check_in_serializer = CheckinSerializer(data = request.data)
        
        if check_in_serializer.is_valid():
            checkin.estado_checkin = check_in_serializer.validated_data['estado']
            checkin.save()
            if  check_in_serializer.validated_data['estado'] == 'CANCELADO':
                # Se libera la fecha     
                self.delete_booking(reserva.id)
            booking = checkin.id_res
            @prefix_decorator(email_type='client',page=4,client=persona,booking=booking)
            def change_state():
                print(check_in_serializer.validated_data['estado'])
            change_state()
            return Response({'message' : 'Estado del checkin actualizado con exito!'}, status = status.HTTP_200_OK)
        return Response({'message' : 'No se pudo actualizar el estado del CheckIn!', 'error' : check_in_serializer.errors}, status = status.HTTP_400_BAD_REQUEST)

    @action(methods=['PUT'], detail=True, url_path='change-checkout')
    def change_check_out(self,request, pk):
        if pk is None:
            return Response({'message':'Debe enviar un pk'}, status = status.HTTP_400_BAD_REQUEST)
        
        checkout, reserva, persona, usuario = None, None, None, None
        try:
            reserva = Reserva.objects.get(id = pk)
            checkout = CheckOut.objects.get(id_res = reserva.id)
            persona = Persona.objects.get(id = reserva.id_cli.id.id)  
            usuario = User.objects.get(person = persona)  
        except:
            pass

        if not checkout:
            return Response({'message':'No existe el Check out'}, status = status.HTTP_400_BAD_REQUEST)
        
        data = {
            'id' : pk,
            'estado' : request.data['estado'],
            'monto' : request.data.get('monto')
        }

        check_out_serializer = CheckoutSerializer(data = data, context = data)
        
        if check_out_serializer.is_valid():
            checkout.estado_checkout = check_out_serializer.validated_data['estado']
            checkout.save()

            if check_out_serializer.validated_data['estado'] in ('COMPLETADO','CANCELADO'):
                self.delete_booking(reserva.id, check_out_serializer.validated_data['estado'])
            
            booking = checkout.id_res
            @prefix_decorator(email_type='client',page=5,client=persona,booking=booking)
            def change_state():
                print(check_out_serializer.validated_data['estado'])
            change_state()
            return Response({'message' : 'Estado del checkout actualizado con exito!'}, status = status.HTTP_200_OK)
        return Response({'message' : 'No se pudo actualizar el estado del CheckOut!', 'error' : check_out_serializer.errors}, status = status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET','POST'], detail=False, url_path='products-details')
    def product_list(self, request):
        if request.method == 'POST':
            serializer = UpdateCheckListProductSerializer(request.data ,data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                {'message' : 'Estados de productos Actualizados con exito!'},
                status = status.HTTP_201_CREATED)
            return Response({'error': serializer.errors}, status = status.HTTP_400_BAD_REQUEST)
        else:
            pk = request.query_params.get('pk','')
            
            if pk == '':
                return Response({'message' : 'Debe enviar un pk vivienda.'}, status = status.HTTP_400_BAD_REQUEST)

            serializer = ListCheckListProductSerializer(data = {'pk' : pk})

            if serializer.is_valid():
                serializer = ListCheckListProductSerializer(pk, many = True)
                return Response(serializer.data[0])
            return Response({'message' : serializer.errors}, status = status.HTTP_400_BAD_REQUEST)
            

    @action(methods=['GET'], detail=True, url_path='fine')
    def fine(self, request, pk = None):
        if pk is None:
            return Response({'message' : 'Debe enviar un pk.'}, status = status.HTTP_400_BAD_REQUEST)
        exists = CheckOut.objects.filter(id = pk).exists()
        if exists:
            generate_fine('turismo_real',pk)
            return Response({'message':'Multa generada con éxito!'})
        return Response({'message' : 'No se pudo generar la multa para el checkout id ' + pk })



class CardViewSet(viewsets.ModelViewSet):
    #authentication_classes = ()
    #permission_classes = ()
    serializer_class = CardSerializer
    filterset_class  = CardFilter
    search_fields = ['nombre_titular','fecha_expiracion']
    ordering_fields = ['id','nombre_titular'] 
    ordering = ['id']

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return CardSerializer
        elif self.action in ["list"]:
            return CardSerializer
        elif self.action in ["create"]:
            return CardSerializer
        elif self.action in ["update"]:
            return CardSerializer
        return self.serializer_class

    def get_queryset(self, pk = None):
        if pk is None:
            return self.get_serializer().Meta.model.objects.filter()
        return self.get_serializer().Meta.model.objects.filter(id = pk).first()

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
        queryset = CuentaBancaria.objects.filter()
        card = get_object_or_404(queryset, pk=pk)
        serializer = CardSerializer(card)
        return Response(serializer.data)
