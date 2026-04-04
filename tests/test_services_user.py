from services.user import authenticate_user, get_user


def test_get_user(session, test_user):
    user = get_user(session, test_user.username)
    
    assert user is not None
    assert user.username == "TestName"


def test_authenticate_user(session, test_user):
    result = authenticate_user(session, test_user.username, "testpassword")

    assert result is not False
    assert result.username == "TestName"

def test_authenticate_user_no_user(session, test_user):
    result = authenticate_user(session, "None", "testpassword")

    assert result is False

def test_authenticate_user_no_password(session, test_user):
    result = authenticate_user(session, test_user.username, "None")

    assert result is False



