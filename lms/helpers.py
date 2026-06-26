from ninja.errors import HttpError
from django.http import JsonResponse

def success_response(message, data=None, status=200):
    return JsonResponse(
        {
            "success": True,
            "message": message,
            "data": data or {}
        },
        status=status
    )


def error_response(message, status=400, errors=None):
    return JsonResponse(
        {
            "success": False,
            "message": message,
            "errors": errors or {}
        },
        status=status
    )

def get_object_or_404(model, **kwargs):
    """
    Mengambil object dari database.
    Jika tidak ditemukan akan return 404.
    """

    try:
        return model.objects.get(**kwargs)

    except model.DoesNotExist:
        raise HttpError(
            404,
            f"{model.__name__} tidak ditemukan"
        )
    
def success_response(message, data=None):
    return {
        "success": True,
        "message": message,
        "data": data,
    }

