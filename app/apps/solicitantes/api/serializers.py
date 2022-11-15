from rest_framework import serializers

from apps.solicitantes.models import Solicitante, Municipio, Genero
from apps.catalogos.models import Medios_Captacion, Canalizaciones


class GenerosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = '__all__'


class MunicipiosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipio
        fields = '__all__'


class VerSolicitanteSerializer(serializers.ModelSerializer):
    municipio = MunicipiosSerializer(read_only=True)
    genero_id = GenerosSerializer(read_only=True)

    class Meta:
        model = Solicitante
        fields = '__all__'


class SolicitantesGetMunicipiosSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='id')
    label = serializers.CharField(source='municipio')

    class Meta:
        model = Municipio
        fields = ('value', 'label')


class SolicitantesGetGenerosSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='id')
    label = serializers.CharField(source='genero')

    class Meta:
        model = Genero
        fields = ('value', 'label')


class SolicitantesGetMediosCaptacionSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='id')
    label = serializers.CharField(source='medio_captacion')

    class Meta:
        model = Medios_Captacion
        fields = ('value', 'label')


class SolicitantesGetCanalizacionesSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='id')
    label = serializers.CharField(source='dependencia')

    class Meta:
        model = Canalizaciones
        fields = ('value', 'label',)


class CrearSolicitanteSerializer(serializers.ModelSerializer):
    # curp_solicitante = serializers.CharField(source='curp')
    clave_elector_solicitante = serializers.CharField(source='clave_lector', allow_blank=True, required=False)
    # rfc_solicitante = serializers.CharField(source='rfc', allow_blank=True, required=False)
    telefono_solicitante = serializers.IntegerField(source='telefono')
    nombre_solicitante = serializers.CharField(source='nombre')
    apellido_paterno_solicitante = serializers.CharField(source='apellido_paterno')
    apellido_materno_solicitante = serializers.CharField(source='apellido_materno')
    # organizacion_solicitante = serializers.CharField(source='organizacion', allow_blank=True, required=False)
    # puesto_organizacion_solicitante = serializers.CharField(source='puesto_organizacion', allow_blank=True, required=False)
    correo_solicitante = serializers.EmailField(source='correo_electronico', allow_blank=True, required=False)
    calle_solicitante = serializers.CharField(source='calle')
    numero_exterior_solicitante = serializers.CharField(source='numero_exterior')
    numero_interior_solicitante = serializers.CharField(source='numero_interior', allow_blank=True, required=False)
    codigo_postal_solicitante = serializers.IntegerField(source='codigo_postal')
    # estado_solicitante = serializers.CharField(source='estado')
    municipio_solicitante = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Municipio.objects.all(), source='municipio')
    colonia_solicitante = serializers.CharField(source='colonia')
    fecha_nacimiento_solicitante = serializers.DateField(source='fecha_nacimiento')
    genero_solicitante = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Genero.objects.all(), source='genero_id')

    class Meta:
        model = Solicitante
        fields = (
            # 'curp_solicitante',
            'clave_elector_solicitante',
            # 'rfc_solicitante',
            'telefono_solicitante',
            'nombre_solicitante',
            'apellido_paterno_solicitante',
            'apellido_materno_solicitante',
            # 'organizacion_solicitante',
            # 'puesto_organizacion_solicitante',
            'correo_solicitante',
            'calle_solicitante',
            'numero_exterior_solicitante',
            'numero_interior_solicitante',
            'codigo_postal_solicitante',
            # 'estado_solicitante',
            'municipio_solicitante',
            'colonia_solicitante',
            'fecha_nacimiento_solicitante',
            'genero_solicitante',
        )
