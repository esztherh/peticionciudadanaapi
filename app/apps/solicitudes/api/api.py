import json

from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.template.loader import render_to_string
from django.template.loader import get_template
from django.http import HttpResponse
# from django.conf.settings import ROOT_DIR
from django.conf import settings

from datetime import datetime, date
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from weasyprint import HTML, CSS

from apps.solicitudes.permissions import GRUPO_OPERADOR, user_is_director, user_is_operador, user_is_enlace, \
                                        puede_dar_seguimiento, puede_canalizar_a_nuevo_enlace, \
                                        UserCanCreatePeticion, UserCanListPetition, UserCanShowMainInfoPetition, UserCanShowFollowUpGroup, UserCanCreateFollowUp, UserCanPipeAnotherDirection, UserCanFinishedFollowUp, UserCanPipeAnotherDependency, UserCanDownloadOficio
from apps.solicitantes.api.serializers import CrearSolicitanteSerializer
from apps.solicitantes.api.api import SolicitanteGetMediosCaptacion, SolicitanteGetGenero, SolicitanteGetMunicipios, SolicitanteGetCanalizacion
from apps.solicitudes.api.serializers import Solicitud, CrearSolicitudSerializer

from apps.solicitudes.api.serializers import Solicitud, Grupo_Seguimiento, Grupo_Seguimiento_Children, Seguimiento, Status_Seguimiento, Change_Status_Seguimiento, \
                                            CrearSolicitudSerializer, ListarSolicitudSerializer, StatusSeguimientoDropdownSerializer, VerSolicitudSerializer, CrearSeguimientoSolicitudSerializer, ListarSeguimientoSerializer, \
                                            GetGrupoSeguimientosSerializer, \
                                            VerInfoPrincipalSegimientoSerializer, \
                                            CrearCanalizacionSolicitudSerializer, \
                                            CanalizacionDireccionGrupoSeguimientoSerializer, \
                                            FinalizarSeguimientoSolicitudSerializer, \
                                            VerInfoPrincipalHistorySegimientoSerializer, ListarGrupoSeguimientoSerializer
from apps.solicitudes.reports_xlsx.reports import xlsx_solicitudes


class CrearSolicitud(generics.CreateAPIView):
    permission_classes = [IsAuthenticated,UserCanCreatePeticion]
    serializer_class = CrearSolicitudSerializer

    def get_files(self, request):
        request._mutable = True
        files = request.pop('archivos', [])
        request._mutable = False
        return files

    def get_data(self, data):
        return json.loads(data['data'])

    def set_files_in_data(self, data, files):
        data['archivos'] = [{'archivo': file, 'descripcion': data['archivos'][index]['descripcion']} for index, file in enumerate(files)]
        return data

    def create(self, request, *args, **kwargs):
        request_tmp = request.data

        files = self.get_files(request_tmp)
        data = self.get_data(request_tmp)
        data = self.set_files_in_data(data, files)

        serializer = CrearSolicitanteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        solicitante = serializer.save()

        data['solicitante'] = solicitante.pk
        data['created_by'] = request.user.id
        data['updated_by'] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()

        return Response(
            {"message": "¡La solicitud se creo correctamente!"}
        )


class ListarSolicitud(generics.ListAPIView):
    permission_classes = [IsAuthenticated,UserCanListPetition]
    queryset = Solicitud.objects.order_by('-fecha_captura')
    serializer_class = ListarSolicitudSerializer

    def search_filter(self, queryset):
        search = self.request.GET.get('buscador')
        return queryset.filter(Q(folio__contains=search) | Q(asunto__contains=search)) if search else queryset

    def start_date_filter(self, queryset):
        date = self.request.GET.get('fecha_inicio')
        return queryset.filter(Q(fecha_solicitud__gte=date)) if date else queryset

    def end_date_filter(self, queryset):
        date = self.request.GET.get('fecha_fin')
        return queryset.filter(Q(fecha_solicitud__lte=date)) if date else queryset

    def status_filter(self, queryset, auth_user):
        status = self.request.GET.get('status')
        if not status:
            return queryset

        query_last_groups = """SELECT id, children_grupo_id
            FROM `solicitudes_grupo_seguimiento_children` AS gsc1
            WHERE created_at = (
                SELECT MAX(created_at)
                FROM `solicitudes_grupo_seguimiento_children` AS gsc2
                WHERE gsc2.main_grupo_id=gsc1.main_grupo_id {0}
            )"""

        if user_is_enlace(auth_user):
            grupos_seguimientos = Grupo_Seguimiento.objects.filter(
                Q(enlace_user_that_traking=auth_user) | Q(enlace_user_that_traking=None),
                Q(enlace_institucional=auth_user.enlace_institucional)
            ).values('pk').distinct()

            subquery = " AND gsc2.children_grupo_id IN ({0})".format(grupos_seguimientos.query)
            g1 = Grupo_Seguimiento_Children.objects.raw(query_last_groups.format(subquery))

            groups_ids = [g.children_grupo_id for g in g1]

            return queryset.filter(grupo_seguimiento__in=groups_ids, grupo_seguimiento__status_enlace=status)

        g1 = Grupo_Seguimiento_Children.objects.raw(query_last_groups.format(""))
        groups_ids = [g.children_grupo_id for g in g1]

        return queryset.filter(status=status)

    def dependencia_filter(self, queryset):
        dependencia = self.request.GET.get('dependencia')
        return queryset.filter(Q(canalizacion=dependencia)) if dependencia else queryset

    def medio_capacitacion_filter(self, queryset):
        medio_capacitacion = self.request.GET.get('medio_capacitacion')
        return queryset.filter(Q(medios_captacion=medio_capacitacion)) if medio_capacitacion else queryset

    def filter_list(self, queryset, auth_user):
        queryset = self.search_filter(queryset)
        queryset = self.start_date_filter(queryset)
        queryset = self.end_date_filter(queryset)
        queryset = self.status_filter(queryset, auth_user)
        queryset = self.dependencia_filter(queryset)
        queryset = self.medio_capacitacion_filter(queryset)
        return queryset

    def get_queryset(self):
        auth_user = self.request.user
        queryset = self.queryset
        queryset = self.filter_list(queryset, auth_user)

        if user_is_enlace(auth_user):
            # queryset = queryset.filter(
            #     Q(grupo_seguimiento__enlace_user_that_traking=auth_user) | Q(grupo_seguimiento__enlace_user_that_traking=None),
            #     Q(grupo_seguimiento__enlace_institucional=auth_user.enlace_institucional)
            # )
            grupos_seguimientos = Grupo_Seguimiento.objects.filter(
                Q(enlace_user_that_traking=auth_user) | Q(enlace_user_that_traking=None),
                Q(enlace_institucional=auth_user.enlace_institucional)
            ).values_list('solicitud', flat = True).annotate(Count('solicitud'))
            queryset = queryset.filter(pk__in=list(grupos_seguimientos))
            return queryset
        return queryset


class GetFiltrosListarSolicitud(APIView):
    permission_classes = [IsAuthenticated,UserCanListPetition]

    def get(self, request, format=None):
        auth_user = self.request.user

        data = {}

        if user_is_director(auth_user) or user_is_operador(auth_user):
            data['medios_captacion'] = SolicitanteGetMediosCaptacion.as_view()(request=request._request).data
            data['dependencias'] = SolicitanteGetCanalizacion.as_view()(request=request._request).data

        status = Status_Seguimiento.objects.filter(belongs_to__in=auth_user.groups.all())
        data['status'] = StatusSeguimientoDropdownSerializer(status, many=True, read_only=True).data

        return Response(data)


class VerInfoPrincipalSegimiento(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated,UserCanShowMainInfoPetition]
    queryset = Solicitud.objects.all()
    serializer_class = VerInfoPrincipalSegimientoSerializer
    lookup_field = 'solicitante'


class VerSolicitud(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated,UserCanShowMainInfoPetition]
    queryset = Solicitud.objects.all()
    serializer_class = VerSolicitudSerializer
    lookup_url_kwarg = 'solicitud_id'


class _ListarSeguimientoSolicitud(generics.ListAPIView):
    queryset = Seguimiento.objects.order_by('-created_at')
    serializer_class = ListarSeguimientoSerializer
    pagination_class = None

    def get_queryset(self):
        return self.queryset.filter(grupo_seguimiento=self.kwargs['grupo_seguimiento'])


class GetGrupoSeguimientos(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated,UserCanShowFollowUpGroup]
    queryset = Grupo_Seguimiento.objects.all()
    serializer_class = GetGrupoSeguimientosSerializer
    lookup_url_kwarg = 'grupo_seguimiento'

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        data = serializer.data
        data['seguimientos'] = _ListarSeguimientoSolicitud.as_view()(request=request._request, *args, **kwargs).data
        return Response(data)


class CrearSeguimientoSolicitud(generics.CreateAPIView):
    permission_classes = [IsAuthenticated,UserCanCreateFollowUp]
    serializer_class = CrearSeguimientoSolicitudSerializer

    def get_files(self, request):
        request._mutable = True
        files = request.pop('archivos', [])
        request._mutable = False
        return files

    def get_data(self, request_data):
        data = request_data['data']
        return json.loads(data)

    def set_files_in_data(self, data, files):
        arr_files = [{'archivo': file, 'descripcion': data['archivos'][index]['descripcion']} for index, file in enumerate(files)]
        data['archivos'] = arr_files
        return data

    def create(self, request, *args, **kwargs):
        auth_user = request.user
        request_tmp = request.data
        data = self.get_data(request_tmp)

        grupo_seguimiento = get_object_or_404(Grupo_Seguimiento, pk=data['grupo_seguimiento'])
        if not puede_dar_seguimiento(auth_user, grupo_seguimiento):
            return Response(
                {"message": "¡No se ha podido crear el seguimiento!"}
            )

        files = self.get_files(request_tmp)
        data = self.set_files_in_data(data, files)
        data['created_by'] = auth_user.pk
        data['enlace_user_that_traking'] = auth_user.pk
        if grupo_seguimiento.enlace_user_that_traking != None or not user_is_enlace(auth_user):
            del data['enlace_user_that_traking']

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()

        return Response(
            {"message": "¡El seguimiento se ha creado correctamente!"},
            status=status.HTTP_201_CREATED
        )


class CrearCanalizacionSolicitud(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, UserCanPipeAnotherDependency]
    serializer_class = CrearCanalizacionSolicitudSerializer

    def create(self, request, *args, **kwargs):
        auth_user = request.user
        data = request.data

        grupo_seguimiento_last = get_object_or_404(Grupo_Seguimiento, pk=data['grupo'])
        if not puede_canalizar_a_nuevo_enlace(auth_user, grupo_seguimiento_last):
            return Response(
                {"message": "¡No puede canalizar a un nuevo enlace!"},
            )

        data['created_by'] = auth_user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()

        return Response(
            {"message": "¡El seguimiento se ha canalizado correctamente!"},
        )


class CanalizacionDireccionGrupoSeguimiento(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated,UserCanPipeAnotherDirection]
    queryset = Grupo_Seguimiento.objects.all()
    serializer_class = CanalizacionDireccionGrupoSeguimientoSerializer
    lookup_url_kwarg = 'grupo_seguimiento'

    def update(self, request, *args, **kwargs):
        data = request.data
        data['updated_by'] = request.user.id
        serializer = self.get_serializer(self.get_object(), data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()
        return Response(
            {"message": "¡El seguimiento se ha canalizado correctamente!"},
        )


class FinalizarSeguimientoSolicitud(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated,UserCanFinishedFollowUp]
    queryset = Grupo_Seguimiento.objects.all()
    serializer_class = FinalizarSeguimientoSolicitudSerializer
    lookup_url_kwarg = 'grupo_seguimiento'

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()
        return Response(
            {"message": "¡El seguimiento se ha cerrado correctamente!"},
        )


class GetMainGruposSeguimientos(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated,UserCanShowMainInfoPetition]
    queryset = Solicitud.objects.all()
    serializer_class = VerInfoPrincipalHistorySegimientoSerializer
    lookup_field = 'solicitante'


class GetHistoryGruposSeguimientos(generics.ListAPIView):
    permission_classes = [IsAuthenticated,UserCanShowMainInfoPetition]
    queryset = Grupo_Seguimiento.objects.all()
    serializer_class = ListarGrupoSeguimientoSerializer
    pagination_class = None

    def get_queryset(self):
        return self.queryset.filter(pk__in=Grupo_Seguimiento_Children.objects.filter(main_grupo=self.kwargs['grupo_seguimiento']).values('children_grupo'))

class GenerarOficio(APIView):
    permission_classes = [IsAuthenticated, UserCanDownloadOficio]

    def get(self, request, grupo_seguimiento):
        grupo_seguimiento = get_object_or_404(Grupo_Seguimiento, pk=grupo_seguimiento)
        solicitante = grupo_seguimiento.solicitud.solicitante

        context = {
            'fecha_oficio': grupo_seguimiento.solicitud.fecha_captura,
            'numero_seguimiento': grupo_seguimiento.solicitud.folio,
            'nombre_peticionario': "%s %s %s" % (solicitante.nombre, solicitante.apellido_paterno, solicitante.apellido_materno),
            'fecha_de_escrito': grupo_seguimiento.solicitud.fecha_solicitud,
            'dependencia': grupo_seguimiento.enlace_institucional
        }

        html_template = render_to_string('pdf_html/test.html', context)
        pdf_file = HTML(string=html_template).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment'
        return response


class GetStatisticsSeguimientos(APIView):
    permission_classes = [IsAuthenticated]

    def card(self, name, total, color, icono='#'):
        return {
            "nombre": name,
            "total": total,
            "color": color,
            "icono": icono
        }

    def get(self, request):
        total_solicitudes = Solicitud.objects.all().count()
        solicitudes_atendidas = Solicitud.objects.filter(status=Status_Seguimiento.objects.filter(is_end=True, system_status=False, change_status__belongs_to__name=GRUPO_OPERADOR)[:1][0]).count()
        solicitudes_pendientes = Solicitud.objects.filter(status=Status_Seguimiento.objects.filter(is_main=True, main_status__belongs_to__name=GRUPO_OPERADOR)[:1][0]).count()
        return Response(
            [
                self.card("Total de Solicitudes", total_solicitudes, 'info', 'ion-filing'),
                self.card("Solicitudes Atendidas", solicitudes_atendidas, 'success', 'ion-android-done'),
                self.card("Solicitudes Pendientes", solicitudes_pendientes, 'warning', 'ion-android-warning')
            ]
        )


class ExportPetitions(APIView):
    permission_classes = [IsAuthenticated, UserCanDownloadOficio]

    def search_filter(self, queryset):
        search = self.request.GET.get('buscador')
        return queryset.filter(Q(folio__contains=search) | Q(asunto__contains=search)) if search else queryset

    def start_date_filter(self, queryset):
        date = self.request.GET.get('fecha_inicio')
        return queryset.filter(Q(fecha_solicitud__gte=date)) if date else queryset

    def end_date_filter(self, queryset):
        date = self.request.GET.get('fecha_fin')
        return queryset.filter(Q(fecha_solicitud__lte=date)) if date else queryset

    def status_filter(self, queryset, auth_user):
        status = self.request.GET.get('status')
        if not status:
            return queryset

        query_last_groups = """SELECT id, children_grupo_id
            FROM `solicitudes_grupo_seguimiento_children` AS gsc1
            WHERE created_at = (
                SELECT MAX(created_at)
                FROM `solicitudes_grupo_seguimiento_children` AS gsc2
                WHERE gsc2.main_grupo_id=gsc1.main_grupo_id {0}
            )"""

        if user_is_enlace(auth_user):
            grupos_seguimientos = Grupo_Seguimiento.objects.filter(
                Q(enlace_user_that_traking=auth_user) | Q(enlace_user_that_traking=None),
                Q(enlace_institucional=auth_user.enlace_institucional)
            ).values('pk').distinct()

            subquery = " AND gsc2.children_grupo_id IN ({0})".format(grupos_seguimientos.query)
            g1 = Grupo_Seguimiento_Children.objects.raw(query_last_groups.format(subquery))

            groups_ids = [g.children_grupo_id for g in g1]

            return queryset.filter(grupo_seguimiento__in=groups_ids, grupo_seguimiento__status_enlace=status)

        g1 = Grupo_Seguimiento_Children.objects.raw(query_last_groups.format(""))
        groups_ids = [g.children_grupo_id for g in g1]

        return queryset.filter(status=status)

    def dependencia_filter(self, queryset):
        dependencia = self.request.GET.get('dependencia')
        return queryset.filter(Q(canalizacion=dependencia)) if dependencia else queryset

    def medio_capacitacion_filter(self, queryset):
        medio_capacitacion = self.request.GET.get('medio_capacitacion')
        return queryset.filter(Q(medios_captacion=medio_capacitacion)) if medio_capacitacion else queryset

    def filter_list(self, queryset, auth_user):
        queryset = self.search_filter(queryset)
        queryset = self.start_date_filter(queryset)
        queryset = self.end_date_filter(queryset)
        queryset = self.status_filter(queryset, auth_user)
        queryset = self.dependencia_filter(queryset)
        queryset = self.medio_capacitacion_filter(queryset)
        return queryset

    def get(self, request):
        auth_user = self.request.user
        queryset = Solicitud.objects.order_by('-fecha_captura')
        queryset = self.filter_list(queryset, auth_user)

        if user_is_enlace(auth_user):
            grupos_seguimientos = Grupo_Seguimiento.objects.filter(
                Q(enlace_user_that_traking=auth_user) | Q(enlace_user_that_traking=None),
                Q(enlace_institucional=auth_user.enlace_institucional)
            ).values_list('solicitud', flat = True).annotate(Count('solicitud'))
            queryset = queryset.filter(pk__in=list(grupos_seguimientos))

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = "attachment; filename=test.xlsx"
        xlsx_solicitudes(response, queryset)
        return response
