from security import hash_password
from security import verify_password


def test_hash_password_does_not_return_plain_password():
    plain_password = "Mauro123!"

    hashed_password = hash_password(plain_password)

    assert hashed_password != plain_password

def test_verify_password_returns_true_for_correct_password():
    plain_password = "Mauro123!"

    hashed_password = hash_password(plain_password)

    result = verify_password(plain_password, hashed_password)

    assert result is True

def test_verify_password_returns_false_for_wrong_password():
    plain_password = "Mauro123!"
    wrong_password = "WrongPassword"

    hashed_password = hash_password(plain_password)

    result = verify_password(wrong_password, hashed_password)

    assert result is False