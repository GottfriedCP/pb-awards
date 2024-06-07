from django.core.exceptions import ValidationError


def filesize_validator(value):
    filesize = value.size

    if filesize > 2621440:
        raise ValidationError("Ukuran maksimum file adalah 2 MB")
    else:
        return value
