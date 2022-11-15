from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status

from .serializers import Solicitante, VerSolicitanteSerializer
from .serializers import Municipio, SolicitantesGetMunicipiosSerializer
from .serializers import Genero, SolicitantesGetGenerosSerializer
from .serializers import Medios_Captacion, SolicitantesGetMediosCaptacionSerializer
from .serializers import Canalizaciones, SolicitantesGetCanalizacionesSerializer
from .serializers import CrearSolicitanteSerializer


class SolicitanteListView(generics.ListAPIView):
    serializer_class = VerSolicitanteSerializer
    queryset = Solicitante.objects.all()


class SolicitanteGetMediosCaptacion(generics.ListAPIView):
    serializer_class = SolicitantesGetMediosCaptacionSerializer
    queryset = Medios_Captacion.objects.all()
    pagination_class = None


class SolicitanteGetMunicipios(generics.ListAPIView):
    serializer_class = SolicitantesGetMunicipiosSerializer
    queryset = Municipio.objects.all()
    pagination_class = None


class SolicitanteGetGenero(generics.ListAPIView):
    serializer_class = SolicitantesGetGenerosSerializer
    queryset = Genero.objects.all()
    pagination_class = None


class SolicitanteGetCanalizacion(generics.ListAPIView):
    serializer_class = SolicitantesGetCanalizacionesSerializer
    queryset = Canalizaciones.objects
    pagination_class = None

    def get_queryset(self):
        if "lugarAtencionId" in self.kwargs:
            medio_capacitacion = get_object_or_404(Medios_Captacion, pk=self.kwargs['lugarAtencionId'])
            return medio_capacitacion.canalizaciones_set.all()
        else:
            return self.queryset.all()


class SolicitanteGetCatalogos(APIView):
    def get(self, request, format=None):
        medios_captacion_list = SolicitanteGetMediosCaptacion.as_view()(request=request._request).data
        generos_list = SolicitanteGetGenero.as_view()(request=request._request).data
        municipios_list = SolicitanteGetMunicipios.as_view()(request=request._request).data

        return Response(
            {
                "medios_captacion": medios_captacion_list,
                "generos": generos_list,
                "municipios": municipios_list,
                "canalizaciones": [],
            }
        )


class SolicitanteGetCanalizaciones(APIView):
    def get(slef, request, *args, **kwargs):
        canalizaciones_list = SolicitanteGetCanalizacion.as_view()(request=request._request, *args, **kwargs).data
        return Response(
            {
                "canalizaciones": canalizaciones_list,
            }
        )


class CrearSolicitud(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        serializer = CrearSolicitanteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        solicitante = serializer.save()
        return Response(
            {
                "message": "¡La solicitud se creo correctamente!"
            },
            status=status.HTTP_201_CREATED
        )
