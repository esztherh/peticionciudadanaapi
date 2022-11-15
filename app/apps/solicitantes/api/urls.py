from django.urls import path

from .api import SolicitanteListView, CrearSolicitud, SolicitanteGetCatalogos, SolicitanteGetCanalizaciones, SolicitanteGetCanalizacion
# from .api import SolicitanteGetMunicipios, SolicitanteGetGenero


urlpatterns = [
    path('', SolicitanteListView.as_view(), name='solicitantes'),
    # path('get_municipios', SolicitanteGetMunicipios.as_view(), name='solicitantes_get_municipios'),
    # path('get_generos', SolicitanteGetGenero.as_view(), name='solicitantes_get_generos'),
    path('get_catalogos', SolicitanteGetCatalogos.as_view(), name='solicitantes_get_catalogos'),
    path('get_canalizaciones/<int:lugarAtencionId>', SolicitanteGetCanalizaciones.as_view(), name='solicitantes_get_canalizaciones'),
    path('peticion/create', CrearSolicitud.as_view(), name='solicitantes_crear'),
]
