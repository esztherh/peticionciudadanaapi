from django.contrib.auth import get_user_model


User = get_user_model()
GRUPO_DIRECTOR='Director'
GRUPO_OPERADOR='Operador'
GRUPO_ENLACE='Enlace Institucional'


def user_is_director(user):
    return User.objects.filter(pk=user.pk, groups__name=GRUPO_DIRECTOR).exists()

def user_is_operador(user):
    return User.objects.filter(pk=user.pk, groups__name=GRUPO_OPERADOR).exists()

def user_is_enlace(user):
    return User.objects.filter(pk=user.pk, groups__name=GRUPO_ENLACE).exists()
