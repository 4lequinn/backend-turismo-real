from re import I
from rest_framework import serializers
from apps.base.models.db_models import Comentario, DetalleProducto, DetalleSala, EstadoProducto, GaleriaExterior, GaleriaInterior, Inventario, Producto, Sala, Vivienda


class DeptoSerializer(serializers.ModelSerializer):
    # Se definen los atributos
    class Meta:
        model = Vivienda
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id' : instance.id,
            'nombre' : instance.nombre,
            'descripcion' : instance.descripcion,
            'direccion' : instance.direccion,
            'slug' : instance.slug,
            'latitud' : instance.latitud,
            'longitud' : instance.longitud,
            'estrellas' : instance.estrellas,
            'disponibilidad' : {
                'id' : instance.id_dis.id,
                'descripcion' : instance.id_dis.descripcion
            },
            'valor_noche' : instance.valor_noche,
            'abono_base' : instance.abono_base,
            'ciudad' : {
                'id' : instance.id_ciu.id,
                'nombre' : instance.id_ciu.nombre,
                'estado' : {
                    'id' : instance.id_ciu.id_est.id,
                    'nombre' : instance.id_ciu.id_est.nombre,
                    'pais' : {
                        'id' : instance.id_ciu.id_est.id_pai.id,
                        'nombre' : instance.id_ciu.id_est.id_pai.nombre
                    }
                }
            },
            'capacidad' : instance.capacidad,
            'internet' : instance.internet,
            'agua' : instance.agua,
            'luz' : instance.luz,
            'gas' : instance.gas,
            'tipo_vivienda' : {
                'id' : instance.id_tip.id,
                'descripcion' : instance.id_tip.descripcion
            }
        }

class InteriorGalerySerializer(serializers.ModelSerializer):
    class Meta:
        model = GaleriaInterior
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id' : instance.id,
            'imagen' : instance.imagen
        }

class ExteriorGalerySerializer(serializers.ModelSerializer):
    class Meta:
        model = GaleriaExterior
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id' : instance.id,
            'imagen' : instance.imagen
        }


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentario
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id' : instance.id,
            'comentario' : instance.descripcion,
            'cliente': {
                'id' : instance.id_cli.id_cli.id.id,
                'nombre' : instance.id_cli.id_cli.id.nombre + ' ' + instance.id_cli.id_cli.id.ap_paterno + ' ' + instance.id_cli.id_cli.id.ap_materno
            },
            'id_vivienda' : instance.id_cli.id_viv.id
        }

class ProductStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoProducto
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id' : instance.id,
            'descripcion' : instance.descripcion
        }

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id' : instance.id,
            'descripcion' : instance.descripcion
        }

class InventoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventario
        fields = 'id'
    
    def getProducts(self,p_id_det):
        p_queryset = DetalleProducto.objects.filter(id_det = p_id_det)
        products = []
        for index in range(len(p_queryset)):
            data = {
                'nombre' : p_queryset[index].id_pro.nombre,
                'precio' : p_queryset[index].id_pro.precio
            }

            products.append(data)
        return products
                


    def to_representation(self, instance):
        r_queryset = DetalleSala.objects.filter(id_inv = instance.id)
        rooms = []

        for x in range(len(r_queryset)):

            data = {
                'id' : r_queryset[x].id,
                'id_sala' : r_queryset[x].id_sal.id,
                'nombre' : r_queryset[x].id_sal.descripcion,
                'imagen' : 'No tiene en la bbd aún',
                'productos' : self.getProducts(r_queryset[x].id) 
            }
            
            rooms.append(data)
    

        return {
            'id_vivienda' : instance.id_viv.id,
            'salas' : rooms
        }

    