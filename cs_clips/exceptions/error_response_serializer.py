# DTOs for the error response
from rest_framework import serializers



# Error response serializer
class ErrorResponseSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="Codice di errore", required=False)
    detail = serializers.CharField(help_text="Descrizione dell'errore")