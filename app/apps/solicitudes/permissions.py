from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from rest_framework.permissions import BasePermission

from apps.users.permissions import GRUPO_ENLACE, GRUPO_OPERADOR, user_is_director, user_is_operador, user_is_enlace


User = get_user_model()


def puede_dar_seguimiento(user, follow_up_group):
    status_enlace = follow_up_group.status_enlace
    status_operador = follow_up_group.status_operador
    if (follow_up_group.enlace_user_that_traking==user or follow_up_group.enlace_user_that_traking==None or user_is_operador(user) or user_is_director(user)) and not status_enlace.is_end and not status_operador.is_end:
        return True
    return False


def puede_canalizar_a_nuevo_enlace(user, follow_up_group):
    return puede_finalizar_seguimiento(user, follow_up_group) and (user_is_director(user) or user_is_operador(user))


def puede_canalizar_a_direccion(user, follow_up_group):
    if user_is_enlace(user) and follow_up_group.enlace_user_that_traking==user and puede_dar_seguimiento(user, follow_up_group) and user.enlace_institucional.enlace_institucional.all().count() > 1:
        return True
    return False


def puede_finalizar_seguimiento(user, follow_up_group):
    status_enlace = follow_up_group.status_enlace
    status_operador = follow_up_group.status_operador

    if user_is_enlace(user) and follow_up_group.enlace_user_that_traking==user:
        return True # if not status_enlace.is_end and not status_operador.is_end else False
    elif user_is_operador(user) or user_is_director(user):
        return True # if status_enlace.is_end and not status_operador.is_end else False
    return False


class UserCanCreatePeticion(BasePermission):
    message = 'No tiene permiso para crear una Petición.'
    permission = 'solicitudes.add_solicitud'

    def has_permission(self, request, view):
        auth_user = request.user
        return (user_is_director(auth_user) or user_is_operador(auth_user)) and self.permission in auth_user.get_all_permissions()


class UserCanListPetition(BasePermission):
    message = 'No tiene permisos para ver Peticiones'
    permission = 'solicitudes.list_solicitud'

    def has_permission(self, request, view):
        auth_user = request.user
        return self.permission in auth_user.get_all_permissions()


class UserCanShowMainInfoPetition(BasePermission):
    message = 'No tiene permisos para ver la Petición'
    permission = 'solicitudes.view_solicitud'

    def has_permission(self, request, view):
        auth_user = request.user
        return self.permission in auth_user.get_all_permissions()

    def has_object_permission(self, request, view, obj):
        auth_user = request.user
        if user_is_enlace(auth_user):
            total_groups = obj.grupo_seguimiento_set.filter(
                    Q(enlace_user_that_traking=auth_user) | Q(enlace_user_that_traking=None),
                    Q(enlace_institucional=auth_user.enlace_institucional)
                ).count()
            return total_groups > 0
        return True if user_is_operador(auth_user) or user_is_director(auth_user) else False


class UserCanShowFollowUpGroup(BasePermission):
    message = 'No tiene permisos para ver la Petición'
    permission = 'solicitudes.view_solicitud'

    def has_permission(self, request, view):
        auth_user = request.user
        return self.permission in auth_user.get_all_permissions()

    def has_object_permission(self, request, view, obj):
        auth_user = request.user
        if user_is_enlace(auth_user):
            return True if (obj.enlace_user_that_traking==auth_user or obj.enlace_user_that_traking==None) and obj.enlace_institucional==auth_user.enlace_institucional else False
        return True if user_is_operador(auth_user) or user_is_director(auth_user) else False


class UserCanCreateFollowUp(BasePermission):
    message = 'No tiene permiso para dar segumiento a la Petición.'
    permission = 'solicitudes.add_seguimiento'

    def has_permission(self, request, view):
        auth_user = request.user
        return (user_is_enlace(auth_user) or user_is_director(auth_user) or user_is_operador(auth_user)) and self.permission in auth_user.get_all_permissions()


class UserCanPipeAnotherDirection(BasePermission):
    message = 'No tiene permiso para dar segumiento a la Petición.'

    def has_permission(self, request, view):
        auth_user = request.user
        return user_is_enlace(auth_user)

    def has_object_permission(self, request, view, obj):
        auth_user = request.user
        new_user = request.data['enlace_user_that_traking']
        return puede_canalizar_a_direccion(auth_user, obj) and auth_user.enlace_institucional.enlace_institucional.filter(pk=new_user).count() == 1


class UserCanPipeAnotherDependency(BasePermission):
    message = 'No tiene permiso para dar segumiento a la Petición.'

    def has_permission(self, request, view):
        auth_user = request.user
        return user_is_director(auth_user) or user_is_operador(auth_user)


class UserCanFinishedFollowUp(BasePermission):
    message = 'No tiene permiso para finalizar el seguimiento.'
    permission = 'solicitudes.change_grupo_seguimiento'

    def has_permission(self, request, view):
        auth_user = request.user
        return (user_is_enlace(auth_user) or user_is_director(auth_user) or user_is_operador(auth_user)) and self.permission in auth_user.get_all_permissions()

    def has_object_permission(self, request, view, obj):
        auth_user = request.user
        new_status = request.data['status']
        current_status = None

        if user_is_enlace(auth_user):
            current_status=obj.status_enlace
        if user_is_operador(auth_user) or user_is_director(auth_user):
            current_status=obj.status_operador

        if current_status==None:
            return False

        return puede_finalizar_seguimiento(auth_user, obj) and current_status.main_status.filter(change_status=new_status, belongs_to__in=auth_user.groups.all()).count()==1


class UserCanDownloadOficio(BasePermission):
    message = 'No tiene permiso para descargar el oficio.'
    permission = 'solicitudes.download_oficio_solicitud'

    def has_permission(self, request, view):
        auth_user = request.user
        return (user_is_enlace(auth_user) or user_is_director(auth_user) or user_is_operador(auth_user)) and self.permission in auth_user.get_all_permissions()
