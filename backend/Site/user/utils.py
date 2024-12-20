'''from .models import VerificationCode


def verify_email(email, verification_code):
    try:
        code_entry = VerificationCode.objects.get(email=email)

        if code_entry.code == verification_code and code_entry.is_valid():
            return True
    except VerificationCode.DoesNotExist:
        return False

    return False'''