import logging
from collections import namedtuple

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response

from cs_clips.exceptions.error_response_serializer import ErrorResponseSerializer

logger = logging.getLogger("exception_handler")
ErrorInfo = namedtuple("ErrorInfo", ["code", "status"])

# Mappa delle eccezioni
ERROR_MAP = {
    ValidationError: ErrorInfo("ValidationError", status.HTTP_400_BAD_REQUEST),
    NotAuthenticated: ErrorInfo("NotAuthenticated", status.HTTP_401_UNAUTHORIZED),
    PermissionDenied: ErrorInfo("PermissionDenied", status.HTTP_403_FORBIDDEN),
    NotFound: ErrorInfo("NotFound", status.HTTP_404_NOT_FOUND),
    Http404: ErrorInfo("NotFound", status.HTTP_404_NOT_FOUND),
    ObjectDoesNotExist: ErrorInfo("NotFound", status.HTTP_404_NOT_FOUND),
    IntegrityError: ErrorInfo("Conflict", status.HTTP_409_CONFLICT),
}


def handle_exception_with_serializer(exc, context=None):
    """
    Gestisce le eccezioni restituendo una risposta JSON coerente
    e strutturata per il frontend.
    """
    view_name = ""
    if context and "view" in context:
        view_name = context["view"].__class__.__name__
    logger.exception(
        "[error_handler] %s in %s: %s",
        exc.__class__.__name__,
        view_name or "unknown",
        exc,
    )

    # Valori di default
    code = exc.__class__.__name__
    detail_message = str(exc)
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    # Cerca nella mappa delle eccezioni
    for exc_type, info in ERROR_MAP.items():
        if isinstance(exc, exc_type):
            code = info.code
            status_code = info.status
            break

    # Gestione approfondita per ValidationError
    if isinstance(exc, ValidationError) and hasattr(exc, "detail"):
        if isinstance(exc.detail, dict):
            # Mostra tutti i campi con errori
            messages = []
            # Itera sui campi e i loro errori
            for field, field_errors in exc.detail.items():
                # Controlla se 'field_errors' è una lista o una singola stringa
                if isinstance(field_errors, list):
                    # Se è una lista, unisci i messaggi di errore
                    error_text = ", ".join(map(str, field_errors))
                else:
                    # Se è una singola stringa, usala direttamente
                    error_text = str(field_errors)

                messages.append(f"Campo '{field}': {error_text}")

            detail_message = " | ".join(messages)
        elif isinstance(exc.detail, list):
            detail_message = "; ".join([str(error) for error in exc.detail])

    # Gestione generica per APIException (non mappata sopra)
    elif isinstance(exc, APIException):
        status_code = getattr(exc, "status_code", status_code)
        code = getattr(exc, "default_code", code)
        detail_message = getattr(exc, "detail", detail_message)

    # Serializzazione della risposta di errore
    error_serializer = ErrorResponseSerializer({"code": code, "detail": detail_message})

    return Response(error_serializer.data, status=status_code)
