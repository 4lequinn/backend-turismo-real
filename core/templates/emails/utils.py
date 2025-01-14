from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives,get_connection
from django.conf import settings
from apps.base.models.db_models import Reserva as Booking, Persona as Client, Servicio as Service, DetServMov as Mov, DetProyecto, Empleado, Recepcionista, Vivienda
from apps.users.models import User
import threading
from core.settings.base import TURISMO_REAL_URI, DEFAULT_DOMAIN
from apps.base.models.db_models import Reserva, CheckIn, CheckOut, Servicio, Compra, DetServMov, TransporteIda, TransporteVuelta, Tour
from datetime import datetime, date
from apps.locations.models import Countries, States, Cities


def get_booking_dict(booking_id:int) -> dict:
    booking = Reserva.objects.filter(id=booking_id).first()
    client = booking.id_cli.id
    checkin = CheckIn.objects.get(id_res=booking)
    checkout = CheckOut.objects.get(id_res=booking)
    checkout.total_multa = 0 if (checkout.total_multa is None) or (checkout.total_multa < 0) else checkout.total_multa
    services = Servicio.objects.filter(id_reserva=booking.id)
    services_formatted = []
    for service in services:
        data = get_service(service)
        services_formatted.append(data)
    user = User.objects.get(person=client)
    dwelling = booking.id_viv
    nights = (booking.fecha_termino - booking.fecha_inicio).days 
    purchase = Compra.objects.get(id_reserva=booking)
    paid_out = True if booking.total_pago == booking.monto_pagado else False
    now = datetime.now()
    client_address = f'{Cities.objects.get(id=client.id_ciu).name}, {States.objects.get(id=client.id_est).name}, {Countries.objects.get(id=client.id_pai).name}.'
    context = {
        'booking': booking,
        'checkin': checkin,
        'checkout': checkout,
        'client': client,
        'client_address': client_address,
        'dwelling': dwelling,
        'services': services_formatted,
        'user': user,
        'nights': nights,
        'purchase': purchase,
        'paid_out': paid_out,
        'created_at': now,
        'STATIC_ROOT': settings.STATIC_ROOT
    }
    return context


def get_service(instance):
    data = {
        'id' : instance.id,
        'tipo_id' : instance.id_tip.id,
        'tipo_servicio' : instance.id_tip.descripcion,
        'precio' : instance.precio
    }

    cant_pasajeros = 0
    if instance.id_tip.id in(1,2):
        detail = DetServMov.objects.get(id_mov__id = instance.id)
        cant_pasajeros = detail.cant_pasajeros
        data['fecha_inicio'] = detail.fecha_inicio
        data['fecha_termino'] = detail.fecha_termino
        data['hora_inicio'] = detail.hora_inicio
        data['hora_termino'] = detail.hora_termino
        data['pasajeros'] = detail.cant_pasajeros
        driver = {
            'id' : detail.id_con.id.id.id,
            'run' : detail.id_con.id.id.run,
            'nombre' : detail.id_con.id.id.nombre + ' ' + detail.id_con.id.id.ap_paterno + ' ' + detail.id_con.id.id.ap_materno,
            'telefono' : detail.id_con.id.id.telefono,
            'vehiculo' : {
                'patente' : detail.id_con.id_veh.patente,
                'modelo' : detail.id_con.id_veh.id_mod.nombre,
                'marca' : detail.id_con.id_veh.id_mar.nombre,
                'color' : detail.id_con.id_veh.id_col.nombre
            }
        }
        data['conductor'] = driver 

    if instance.id_tip.id == 1:
        transporte = None
        try:
            transporte = TransporteIda.objects.get(id_trans = instance.id)
            data['tipo_tranporte'] = 'transporte de ida'
            data['valida_tipo'] = 1
        except:
            pass

        try: 
            transporte = TransporteVuelta.objects.get(id_trans = instance.id)
            data['tipo_tranporte'] = 'transporte de vuelta'
            data['valida_tipo'] = 2
        except:
            pass

        data['nombre'] = transporte.id_ub_trans.nombre 
        data['descripcion'] = transporte.id_ub_trans.id_tip.descripcion
        data['precio'] = transporte.id_ub_trans.precio 

    elif instance.id_tip.id == 2: 
        tour = Tour.objects.filter(id=instance.id).first() 
        data['nombre'] = tour.id_ub_trans.nombre
        data['descripcion'] = tour.id_ub_trans.descripcion
        data['precio'] = instance.precio
    return data

def send_email(subject:str,mail_to:str,template:str,data:dict,account:int=1):
    """Send email function
    Args: 
        subject (str): Email subject
        mail_to (str): Person who receives the mail
        template (str): File name
        data (dict): Information to show in the email
        account (int): Type email sender (TURISMO_REAL OR BANK BV LATAM)
    """

    sender = settings.EMAIL_HOST_USER
    connection = get_connection() # uses SMTP server specified in settings.py
    if account == 2:
        sender = settings.BANK_EMAIL_HOST_USER
        my_host = settings.BANK_EMAIL_HOST
        my_port = settings.BANK_EMAIL_PORT
        my_username = sender
        my_password = settings.BANK_EMAIL_HOST_PASSWORD
        my_use_tls = settings.BANK_EMAIL_USE_TLS
        connection = get_connection(host=my_host, 
                            port=my_port, 
                            username=my_username, 
                            password=my_password, 
                            use_tls=my_use_tls) 
    
    connection.open()
    context = data
    template = get_template(template)
    content = template.render(context)
    message = EmailMultiAlternatives(subject,sender,sender,[mail_to],connection=connection)
    message.attach_alternative(content, 'text/html')
    message.send()
    connection.close()
    

def generate_notice(email_type:str,page:int,client:Client=None,booking:Booking=None,amount:int=None):
    """Generic send an email to users 
    Args: 
        email_type (str): Dict key for business area involved
        page (int): Dict key for page template
        client (Persona): Client data
        booking (Reserva): Booking data
    Returns:
        string (str): State of the process
    """
    # Filter with email type
    options = {
        'service':{
                1 :{'template':['emails/service/client_notice.html','emails/services/driver_notice.html'],'subject':['[Turismo Real] ¡Servicio de Transporte contratado!','[Turismo Real] Servicio solicitado']}, # TRANSPORTE
                2 :{'template':['emails/service/client_notice.html','emails/services/driver_notice.html'],'subject':['[Turismo Real] ¡Servicio de Tour contratado!','[Turismo Real] Servicio solicitado']} # TOUR
            }, 
        'booking':{
                1 :{'template':['emails/booking/booking.html','emails/booking/receptionist_notice.html'],'subject':['Estimado Jorge, su reserva esta lista','[Turismo Real] Reserva creada']}, # RESERVA
            }, 
        'client':{
            1:{'template':'emails/create_account/create-account.html','subject':'[Turismo Real] ¡Bienvenido!'}, # Registro
            2:{'template':'emails/change_password/change-password.html','subject':'[Turismo Real] Contraseña cambiada'}, # Cambio de password
            3:{'template':'emails/payment/bank.html','subject':'[Banco BV LATAM] Se ha realizado un cargo a su tarjeta'}, # Cargo en la tarjeta
            4:{'template':'emails/booking/checkin.html','subject':'[Turismo Real] Seguimiento Check IN'}, # Cambio estado Checkin
            5:{'template':'emails/booking/checkout.html','subject':'[Turismo Real] Seguimiento Check OUT'}, # Cambio estado Checkout
        }
    }

    if not options:
        return f"The operation '{email_type}' is not supported!"
    if email_type == 'client':
        if page == 3:
            notice_client(client,options.get(email_type)[page]['subject'],options.get(email_type)[page]['template'],2,amount)
        elif page in(4,5):
            notice_client(client,options.get(email_type)[page]['subject'],options.get(email_type)[page]['template'],1,booking=booking)
        else:
            notice_client(client,options.get(email_type)[page]['subject'],options.get(email_type)[page]['template'],1)
    if email_type == 'booking':
        notice_booking(booking,options,page)
        
    return 'Mail sent successfully.'




# Receptionist for booking
def search_receptionist(dwelling_id):
    queryset =  DetProyecto.objects.filter(id_viv = dwelling_id)
    response = None

    for index in range(len(queryset)):
        if queryset[index].id_emp.id_car.id == 3:
            # Obtenemos la instancia de empleado y luego de recepcionista
            employee = Empleado.objects.get(id = queryset[index].id_emp.id)
            receptionist = Recepcionista.objects.get(id = employee)
            response = receptionist
            break
    return response

# Services and drivers for booking
def list_services(services):
    service_list = []
    for x in range(len(services)):
        detail_service = Mov.objects.filter(id_mov = services[x].id).first()
        data = {
            'id_service' : detail_service.id_mov,
            'driver' : detail_service.id_con,
            'start_date' : detail_service.fecha_inicio,
            'start_time' : detail_service.hora_inicio,
            'end_date' : detail_service.fecha_termino,
            'end_time' : detail_service.hora_termino,
            'passengers' : detail_service.cant_pasajeros
        }
        service_list.append(data)
    return service_list



# Clients module
def notice_client(client,subject,template,account,amount=0,booking=None):
    checkin,checkout=None,None
    if booking:
        checkin = CheckIn.objects.get(id_res=booking)
        checkout = CheckOut.objects.get(id_res=booking)
    user = User.objects.filter(person = client).first()
    now = datetime.now()
    today = date.today()
    send_email(
            mail_to=user.email,
            subject=subject,
            template=template,
            data={
                'amount': amount,
                'comission': settings.COMISSION,
                'today': today,
                'created_at':now,
                'client': client,
                'total':amount+settings.COMISSION,
                'checkin':checkin,
                'checkout':checkout,
                'TURISMO_REAL_URI' : TURISMO_REAL_URI,
            },
            account=account
        )


def notice_booking(booking:Booking, options, page):
    context = get_booking_dict(booking.id)

    #######################
    ## Send Emails
    #######################

    ## Client
    send_email(
        mail_to=context['user'].email,
        subject='Estimad@ {}, ¡su reserva ha sido confirmada con éxito!'.format(context['client'].nombre),
        template=options.get('booking')[page]['template'][0],
        data=context
        )
    receptionist = search_receptionist(booking.id_viv.id)
    ## Receptionist
    user = User.objects.filter(person = receptionist.id.id.id).first() 
    context['receptionist'] = receptionist.id.id
    context['user'] = user
    send_email(
        mail_to=user.email,
        subject=options.get('booking')[page]['subject'][1],
        template=options.get('booking')[page]['template'][1],
        data=context
    )

    services = context['services']
    
    if page == 1 and services:
        ## Drivers
        for x in range(len(services)):
            user = User.objects.filter(person = services[x].get('conductor')['id']).first()
            context['user'] = user
            context['service'] = get_service(Service.objects.filter(id=services[x]['id']).first())
            send_email(
                mail_to=user.email,
                subject=options.get('service')[1]['subject'][1],
                template=options.get('service')[1]['template'][1],
                data=context
            )
## DECORATOR
def prefix_decorator(email_type:str, page:int, client:Client = None, booking:Booking = None,amount:int=None):
    def decorator_function(original_function):

        # Función decorada
        def wrapper_function(*args, **kwargs):
            result = original_function(*args, **kwargs)

            # Enviamos un correo al finalizar la operacion
            thread = threading.Thread(target=generate_notice,kwargs={
                    'email_type': email_type,
                    'page' : page,
                    'client' : client,
                    'booking' : booking,
                    'amount' : amount,
                })
            thread.start()
            return result

        return wrapper_function
    return decorator_function

