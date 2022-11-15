
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.forms import model_to_dict

from datetime import datetime, date
from rest_framework import serializers

from apps.solicitudes.permissions import GRUPO_ENLACE, GRUPO_OPERADOR, user_is_director, user_is_operador, user_is_enlace, \
                                            puede_dar_seguimiento, puede_finalizar_seguimiento, puede_canalizar_a_nuevo_enlace, puede_canalizar_a_direccion
from apps.users.api.serializers import User, DropdownUserSerializer
from apps.solicitantes.api.serializers import VerSolicitanteSerializer, SolicitantesGetCanalizacionesSerializer, SolicitantesGetMediosCaptacionSerializer
from apps.solicitudes.models import Solicitud, Beneficiario, Archivo, \
                                    Grupo_Seguimiento, Grupo_Seguimiento_Children, Status_Seguimiento, Change_Status_Seguimiento, Seguimiento, Seguimiento_Archivo, \
                                    Medios_Captacion, Canalizaciones


class CrearArchivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archivo
        fields = (
            'archivo',
            'descripcion',
        )


class CrearBeneficiarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiario
        fields = (
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'curp',
        )


class CrearSolicitudSerializer(serializers.ModelSerializer):
    # numero_turno_solicitud = serializers.CharField(source='numero_turno')
    asunto_solicitud = serializers.CharField(source='asunto')
    medios_captacion_solicitud = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Medios_Captacion.objects.all(), source='medios_captacion')
    # lugar_expedicion_solicitud = serializers.CharField(source='lugar_expedicion')
    # prioridad_urgente_solicitud = serializers.CharField(source='prioridad_urgente')
    canalizacion_solicitud = serializers.PrimaryKeyRelatedField(many=True, write_only=True, queryset=Canalizaciones.objects.all(), source='canalizacion')
    # requiere_audiencia_solicitud = serializers.CharField(source='requiere_audiencia')
    descripcion_solicitud = serializers.CharField(source='descripcion')
    beneficiarios = CrearBeneficiarioSerializer(many=True, write_only=True, required=False)
    archivos = CrearArchivoSerializer(many=True, write_only=True)

    class Meta:
        model = Solicitud
        fields = (
            # 'numero_turno_solicitud',
            'asunto_solicitud',
            'fecha_solicitud',
            'medios_captacion_solicitud',
            # 'lugar_expedicion_solicitud',
            # 'prioridad_urgente_solicitud',
            'canalizacion_solicitud',
            # 'requiere_audiencia_solicitud',
            'descripcion_solicitud',
            'solicitante',
            'beneficiarios',
            'archivos',
            'created_by',
            'updated_by',
            'nombre_servidor_publico',
            'apellido_parterno_servidor_publico',
            'apelliod_materno_servidor_publico',
            'cargo_servidor_publico',
            'area_servidor_publico',
        )

    def create_folio(self, nomenclatura, total_petitions):
        year = datetime.now().strftime('%Y')
        total_petitions = str(total_petitions+1).zfill(4)

        return "%s/%s/%s" % (nomenclatura, total_petitions, year)

    def set_folio(self, data):
        now_start = datetime.now().strftime('%Y-01-01 00:00:00')
        now_end = datetime.now().strftime('%Y-12-31 23:59:59')
        total_solicitudes = Solicitud.objects.filter(created_at__gte=now_start, created_at__lte=now_end).count()
        folio = self.create_folio(data['medios_captacion'].nomenclatura, total_solicitudes)
        data['folio'] = folio

        return data

    def set_status_grupo_seguimiento(self, data):
        data['status_enlace'] = Status_Seguimiento.objects.filter(is_main=True, main_status__belongs_to__name=GRUPO_ENLACE)[:1][0]
        data['status_operador'] = Status_Seguimiento.objects.filter(is_main=True, main_status__belongs_to__name=GRUPO_OPERADOR)[:1][0]
        return data

    def set_status_solicitud(self, data):
        data['status'] = Status_Seguimiento.objects.filter(is_main=True, main_status__belongs_to__name=GRUPO_OPERADOR)[:1][0]
        return data

    def create(self, validated_data):
        beneficiarios = validated_data.pop('beneficiarios', [])
        canalizaciones = validated_data.pop('canalizacion')
        archivos = validated_data.pop('archivos', [])

        validated_data = self.set_folio(validated_data)
        validated_data = self.set_status_solicitud(validated_data)

        instance = Solicitud.objects.create(**validated_data)
        instance.canalizacion.set(canalizaciones)

        grupo_seguimiento = {'solicitud': instance, 'created_by': validated_data['created_by'], 'updated_by': validated_data['created_by'], 'enlace_institucional': 0, 'is_main': True}
        for canalizacion in canalizaciones:
            grupo_seguimiento['enlace_institucional'] = canalizacion
            grupo_seguimiento = self.set_status_grupo_seguimiento(grupo_seguimiento)
            grupo = Grupo_Seguimiento.objects.create(**grupo_seguimiento)
            Grupo_Seguimiento_Children.objects.create(**{'main_grupo': grupo, 'children_grupo': grupo})

        for beneficiario in beneficiarios:
            beneficiario['solicitud'] = instance
            Beneficiario.objects.create(**beneficiario)

        if archivos:
            for archivo in archivos:
                archivo['solicitud'] = instance
                Archivo.objects.create(**archivo)

        return instance


class ListarSolicitudSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()

    class Meta:
        model = Solicitud
        fields = (
            'pk',
            'folio',
            'status',
            'status_color',
            'fecha_solicitud',
            'asunto',
            'canalizacion',
        )

    def get_status(self, instance):
        auth_user = self.context['request'].user
        if user_is_enlace(auth_user):
            grupo_seguimiento = Grupo_Seguimiento.objects.filter(
                Q(solicitud=instance), Q(enlace_institucional=auth_user.enlace_institucional),
                Q(enlace_user_that_traking=auth_user) | Q(enlace_user_that_traking=None)
            ).order_by('-created_at')[:1][0]
            return grupo_seguimiento.status_enlace.status
        return instance.status.status

    def get_status_color(self, instance):
        auth_user = self.context['request'].user
        if user_is_enlace(auth_user):
            grupo_seguimiento = Grupo_Seguimiento.objects.filter(
                Q(solicitud=instance), Q(enlace_institucional=auth_user.enlace_institucional),
                Q(enlace_user_that_traking=auth_user) | Q(enlace_user_that_traking=None)
            ).order_by('-created_at')[:1][0]
            return grupo_seguimiento.status_enlace.color
        return instance.status.color


class GetFiltrosListarSolicitudSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Solicitud
        fields = (
            'status'
        )

    def get_status(self, instance):
        auth_user = self.context['request'].user

        change_status = Change_Status_Seguimiento.objects.filter(belongs_to__in=auth_user.groups.all())
        print(change_status)
        # if user_is_enlace(auth_user):
        #     grupo_seguimiento = Grupo_Seguimiento.objects.filter(
        #         Q(solicitud=instance), Q(enlace_institucional=auth_user.enlace_institucional),
        #         Q(enlace_user_that_traking=auth_user) | Q(enlace_user_that_traking=None)
        #     ).order_by('-created_at')[:1][0]
        #     return grupo_seguimiento.status_enlace.status
        # return instance.status.status


class BeneficiariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiario
        fields = '__all__'


class ArchivosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archivo
        fields = '__all__'


class VerSolicitudSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='solicitante.id')
    solicitante = VerSolicitanteSerializer(read_only=True)
    canalizacion = SolicitantesGetCanalizacionesSerializer(many=True, read_only=True)
    medios_captacion = SolicitantesGetMediosCaptacionSerializer(read_only=True)
    fecha_captura = serializers.DateTimeField(format="%Y-%m-%d")
    beneficiario_set = BeneficiariosSerializer(many=True, read_only=True)
    archivo_set = ArchivosSerializer(many=True, read_only=True)

    class Meta:
        model = Solicitud
        fields = '__all__'


class StatusSeguimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status_Seguimiento
        fields = ('status', 'color')


class StatusSeguimientoDropdownSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='id')
    label = serializers.CharField(source='status')

    class Meta:
        model = Status_Seguimiento
        fields = ('value', 'label')


class ListarGrupoSeguimientoSerializer(serializers.ModelSerializer):
    enlace_institucional = serializers.CharField(source='enlace_institucional.dependencia')
    status = serializers.SerializerMethodField()
    main_grupo = serializers.SerializerMethodField()

    class Meta:
        model = Grupo_Seguimiento
        fields = (
            'id',
            'enlace_institucional',
            'status',
            'main_grupo',
        )

    def get_auth_user(self):
        return self.context['auth_user'] if 'auth_user' in self.context else self.context['request'].user

    def get_status(self, instance):
        status = None
        if user_is_enlace(self.get_auth_user()):
            status = instance.status_enlace
        else:
            status = instance.status_operador
            if instance.status_operador.is_end:
                status = instance.status_operador
            elif instance.status_enlace.is_end:
                status = instance.status_enlace
        return StatusSeguimientoSerializer(status, read_only=True).data

    def get_main_grupo(self, instance):
        group = Grupo_Seguimiento_Children.objects.filter(children_grupo=instance.pk).values('main_grupo')[:1]
        return group[0]['main_grupo']


class VerInfoPrincipalSegimientoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='solicitante.id')
    grupos_seguimientos = serializers.SerializerMethodField()

    class Meta:
        model = Solicitud
        fields = (
            'id',
            'folio',
            'grupos_seguimientos',
        )

    def get_grupos_seguimientos(self, instance):
        auth_user = self.context['request'].user
        current_groups = []
        main_groups = instance.grupo_seguimiento_set.filter(is_main=True)

        if user_is_enlace(auth_user):
            all_groups = Grupo_Seguimiento_Children.objects.filter(main_grupo__in=main_groups).values_list('children_grupo', flat=True)
            current_groups = instance.grupo_seguimiento_set.filter(
                Q(pk__in=all_groups),
                Q(enlace_institucional=auth_user.enlace_institucional),
                Q(enlace_user_that_traking=auth_user) | Q(enlace_user_that_traking=None)
            ).order_by('-created_at')[:1]
        else:
            current_groups_ids = []
            for main_group in main_groups:
                current_group = main_group.main_grupo.order_by('-created_at')[:1].values('children_grupo')
                if (len(current_group) > 0):
                    current_groups_ids.append(current_group[0]['children_grupo'])

            current_groups = instance.grupo_seguimiento_set.filter(pk__in=current_groups_ids)

        return ListarGrupoSeguimientoSerializer(current_groups, context={'auth_user':auth_user}, many=True, read_only=True).data


class ListarSolicitudSeguimientoArchivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seguimiento_Archivo
        fields = '__all__'


class ListarSeguimientoSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d")
    seguimiento_archivo_set = ListarSolicitudSeguimientoArchivoSerializer(many=True, read_only=True)
    created_by = serializers.CharField(max_length=50, source='created_by.username')

    class Meta:
        model = Seguimiento
        fields = '__all__'

    # def get_created_by(self, instance):
    #     print('-----------------------------')
    #     auth_user = self.context['request'].user
    #     print(instance.created_by.user)
    #     print('-----------------------------')
    #     return auth_user


class GetGrupoSeguimientosSerializer(serializers.ModelSerializer):
    change_status = serializers.SerializerMethodField()
    puede_finalizar_seguimiento = serializers.SerializerMethodField()
    puede_dar_seguimiento = serializers.SerializerMethodField()
    puede_canalizar_a_nuevo_enlace = serializers.SerializerMethodField()
    canalizar_a_enlaces = serializers.SerializerMethodField()
    puede_canalizar_a_direccion = serializers.SerializerMethodField()
    canalizar_a_direccion = serializers.SerializerMethodField()

    User = None

    class Meta:
        model = Grupo_Seguimiento
        fields = (
            'id',
            'puede_finalizar_seguimiento',
            'change_status',
            'puede_dar_seguimiento',
            'puede_canalizar_a_nuevo_enlace',
            'canalizar_a_enlaces',
            'puede_canalizar_a_direccion',
            'canalizar_a_direccion',
        )

    def _get_auth_user(self):
        if self.User==None:
            self.User = self.context['request'].user
        return self.User

    def get_change_status(self, instance):
        if not puede_finalizar_seguimiento(self._get_auth_user(), instance):
            return []

        main_status = instance.status_enlace if user_is_enlace(self._get_auth_user()) else instance.status_operador
        change_status = main_status.main_status.all().values_list('change_status')
        status = Status_Seguimiento.objects.filter(pk__in=change_status, system_status=False)

        return StatusSeguimientoDropdownSerializer(status, many=True, read_only=True).data

    def get_puede_finalizar_seguimiento(self, instance):
        return puede_finalizar_seguimiento(self._get_auth_user(), instance)

    def get_puede_dar_seguimiento(self, instance):
        return puede_dar_seguimiento(self._get_auth_user(), instance)

    def get_puede_canalizar_a_nuevo_enlace(self, instance):
        return puede_canalizar_a_nuevo_enlace(self._get_auth_user(), instance)

    def get_canalizar_a_enlaces(self, instance):
        if not puede_canalizar_a_nuevo_enlace(self._get_auth_user(), instance):
            return []
        canalizaciones = Canalizaciones.objects.all()
        return SolicitantesGetCanalizacionesSerializer(canalizaciones, many=True, read_only=True).data

    def get_puede_canalizar_a_direccion(self, instance):
        return puede_canalizar_a_direccion(self._get_auth_user(), instance)

    def get_canalizar_a_direccion(self,instance):
        if not puede_canalizar_a_direccion(self._get_auth_user(), instance):
            return []
        users = self._get_auth_user().enlace_institucional.enlace_institucional.filter(groups__name=GRUPO_ENLACE).exclude(pk=self._get_auth_user().pk)
        return DropdownUserSerializer(users, many=True, read_only=True).data


class CrearSolicitudSeguimientoArchivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seguimiento_Archivo
        fields = (
            'archivo',
            'descripcion',
        )


class CrearSeguimientoSolicitudSerializer(serializers.ModelSerializer):
    archivos = CrearSolicitudSeguimientoArchivoSerializer(many=True, write_only=True)
    enlace_user_that_traking = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Seguimiento
        fields = (
            'observaciones',
            'grupo_seguimiento',
            'created_by',
            'archivos',
            'enlace_user_that_traking',
        )

    def create(self, validated_data):
        auth_user = self.context['request'].user

        archivos = validated_data.pop('archivos', [])
        enlace_user_that_traking = validated_data.pop('enlace_user_that_traking', None)

        instance = Seguimiento.objects.create(**validated_data)

        if enlace_user_that_traking != None:
            grupo_seguimiento = get_object_or_404(Grupo_Seguimiento, pk=validated_data['grupo_seguimiento'].pk)
            grupo_seguimiento.enlace_user_that_traking = auth_user
            grupo_seguimiento.save()

        for archivo in archivos:
            archivo['solicitud_seguimiento'] = instance
            Seguimiento_Archivo.objects.create(**archivo)

        return instance


class CrearCanalizacionSolicitudSerializer(serializers.ModelSerializer):
    grupo = serializers.IntegerField(write_only=True)

    Observacion = "El seguimiento se ha canalizado al enlace \"%s\" por el usuario \"%s\" (Observación del Sistema)"

    class Meta:
        model=Grupo_Seguimiento
        fields=('solicitud', 'enlace_institucional', 'created_by', 'grupo',)

    def set_status_initial(self, data):
        data['status_enlace'] = Status_Seguimiento.objects.filter(is_main=True, main_status__belongs_to__name=GRUPO_ENLACE)[:1][0]
        data['status_operador'] = Status_Seguimiento.objects.filter(is_main=True, main_status__belongs_to__name=GRUPO_OPERADOR)[:1][0]
        return data

    def create(self, validated_data):
        auth_user = self.context['request'].user
        observacion = self.Observacion % (validated_data.get('enlace_institucional').dependencia, auth_user.username)

        grupo_seguimiento = get_object_or_404(Grupo_Seguimiento, pk=validated_data.pop('grupo'))
        grupo_seguimiento.status_operador = Status_Seguimiento.objects.get(status='Canalizado a Enlace')
        grupo_seguimiento.save()

        Seguimiento.objects.create(**{"observaciones": observacion, "grupo_seguimiento": grupo_seguimiento, "created_by": auth_user})

        validated_data['updated_by'] = validated_data['created_by']
        validated_data['is_main'] = False
        validated_data = self.set_status_initial(validated_data)

        grupo_seguimiento_children = grupo_seguimiento.children_grupo.all()
        new_group = Grupo_Seguimiento.objects.create(**validated_data)
        Grupo_Seguimiento_Children.objects.create(**{'main_grupo': grupo_seguimiento_children[0].main_grupo, 'children_grupo': new_group})

        return new_group


class CanalizacionDireccionGrupoSeguimientoSerializer(serializers.ModelSerializer):
    Observacion = "El seguimiento se ha canalizado al usuario \"%s\" por el usuario \"%s\" (Observación del Sistema)"

    class Meta:
        model=Grupo_Seguimiento
        fields = ('enlace_user_that_traking', 'updated_by')

    def update(self, instance, validated_data):
        new_group = get_object_or_404(Grupo_Seguimiento, pk=instance.pk)
        new_group = {
            "solicitud": instance.solicitud,
            "created_by": validated_data.get('updated_by', instance.updated_by),
            "updated_by": validated_data.get('updated_by', instance.updated_by),
            "enlace_institucional": instance.enlace_institucional,
            "status_enlace": instance.status_enlace,
            "status_operador": instance.status_operador,
            "enlace_user_that_traking": validated_data.get('enlace_user_that_traking', None),
        }
        new_group = Grupo_Seguimiento.objects.create(**new_group)

        grupo_seguimiento_children = Grupo_Seguimiento_Children.objects.filter(children_grupo=instance.pk)[:1][0]
        Grupo_Seguimiento_Children.objects.create(**{'main_grupo': grupo_seguimiento_children.main_grupo, 'children_grupo': new_group})

        canalizacion_usuario = get_object_or_404(User, pk=new_group.enlace_user_that_traking.pk)
        auth_user = self.context['request'].user
        observacion = self.Observacion % (canalizacion_usuario.username, auth_user.username)

        instance.observacion = observacion
        instance.status_enlace = Status_Seguimiento.objects.get(status='Canalizado a Dirección')
        instance.updated_by = validated_data.get('updated_by', instance.updated_by)
        instance.save()

        Seguimiento.objects.create(**{"observaciones": observacion, "grupo_seguimiento": new_group, "created_by": auth_user})
        Seguimiento.objects.create(**{"observaciones": observacion, "grupo_seguimiento": instance, "created_by": auth_user})

        return instance


class FinalizarSeguimientoSolicitudSerializer(serializers.ModelSerializer):
    status = serializers.IntegerField(write_only=True)

    Observacion = "El seguimiento finaliza por parte de \"%s\" con el estatus \"%s\" (Observación del Sistema)"

    class Meta:
        model = Grupo_Seguimiento
        fields = ('status',)

    def update(self, instance, validated_data):
        auth_user = self.context['request'].user

        status_id = validated_data.get('status', 0)
        status = get_object_or_404(Status_Seguimiento, pk=status_id)

        if user_is_enlace(auth_user):
            instance.status_enlace = status
        else:
            instance.status_operador = status

        instance.observacion = self.Observacion % (auth_user.username, status.status)
        instance.updated_by = auth_user
        instance.save()

        if not user_is_enlace(auth_user):
            main_groups = instance.solicitud.grupo_seguimiento_set.filter(is_main=True)
            all_groups_are_ended = True
            for main_group in main_groups:
                last_group = Grupo_Seguimiento_Children.objects.filter(main_grupo=main_group).order_by('-created_at')[:1][0]
                if not last_group.children_grupo.status_operador.is_end:
                    all_groups_are_ended = False
            if all_groups_are_ended:
                instance.solicitud.status = status
                instance.solicitud.save()

        Seguimiento.objects.create(**{"observaciones": instance.observacion, "grupo_seguimiento": instance, "created_by": auth_user})

        return instance


class VerInfoPrincipalHistorySegimientoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='solicitante.id')
    grupos_seguimientos = serializers.SerializerMethodField()

    class Meta:
        model = Solicitud
        fields = (
            'id',
            'folio',
            'grupos_seguimientos',
        )

    def get_grupos_seguimientos(self, instance):
        main_groups = instance.grupo_seguimiento_set.filter(is_main=True)
        return ListarGrupoSeguimientoSerializer(main_groups, context={'auth_user':self.context['request'].user}, many=True, read_only=True).data
