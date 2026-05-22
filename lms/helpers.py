from ninja.errors import HttpError


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