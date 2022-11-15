from django.urls import path

from .api import CrearSolicitud, ListarSolicitud, GetFiltrosListarSolicitud, VerSolicitud, GetGrupoSeguimientos, CrearSeguimientoSolicitud, CrearCanalizacionSolicitud, FinalizarSeguimientoSolicitud, CanalizacionDireccionGrupoSeguimiento, GetMainGruposSeguimientos, GetHistoryGruposSeguimientos, GetStatisticsSeguimientos
from .api import VerInfoPrincipalSegimiento
from .api import GenerarOficio, ExportPetitions


urlpatterns = [
    path('crear', CrearSolicitud.as_view(), name='crear_solicitud'),
    path('list', ListarSolicitud.as_view(), name='listar_solicitud'),
    path('list-get-filter', GetFiltrosListarSolicitud.as_view(), name='obtener_filtros_listar_solicitud'),
    path('ver/<int:solicitud_id>', VerSolicitud.as_view(), name='ver_solicitud'),
    path('export', ExportPetitions.as_view(), name='exportar_peticiones'),

    path('seguimientos/<int:solicitante>', VerInfoPrincipalSegimiento.as_view(), name='ver_info_principal_seguimiento'),
    path('seguimientos/grupo_seguimiento/<int:grupo_seguimiento>', GetGrupoSeguimientos.as_view(), name='obtener_grupo_seguimientos'),
    path('seguimientos/crear', CrearSeguimientoSolicitud.as_view(), name='crear_seguimiento_solicitud'),
    path('seguimientos/grupo_seguimiento/crear', CrearCanalizacionSolicitud.as_view(), name='crear_grupo_seguimiento_solicitud'),
    path('seguimientos/grupo_seguimiento/actualizar_direccion/<int:grupo_seguimiento>', CanalizacionDireccionGrupoSeguimiento.as_view(), name='actualizar_direccion_grupo_seguimiento_solicitud'),
    path('seguimientos/finalizar/<int:grupo_seguimiento>', FinalizarSeguimientoSolicitud.as_view(), name='finalizar_seguimiento'),

    path('seguimientos/main_grupo_seguimiento/<int:solicitante>', GetMainGruposSeguimientos.as_view(), name='obtener_main_grupos_seguimientos'),
    path('seguimientos/grupos_seguimientos/history/<int:grupo_seguimiento>', GetHistoryGruposSeguimientos.as_view(), name='obtener_main_grupos_seguimientos'),

    path('seguimientos/grupo_seguimiento/download/<int:grupo_seguimiento>', GenerarOficio.as_view(), name='download_pdf'),

    path('seguimientos/total', GetStatisticsSeguimientos.as_view(), name='obtener_stadisticas_seguimientos'),
]
