from import_export import resources
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'nombre_empresa', 'cargo', 'is_staff', 'is_active', 'is_superuser')
