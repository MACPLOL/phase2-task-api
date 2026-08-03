def test_user_registration_succeeds(client):
    response = client.post("/users",
                           json={
                               "email": "mauro@example.com",
                               "password": "Mauro123!",
                           }, )
    data = response.json()


    assert response.status_code==201
    assert data["email"]== "mauro@example.com"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data

def test_user_duplicate_email_registered(client):
    response = client.post("/users",
                           json={
                               "email": "mauro@example.com",
                               "password": "Mauro123!",
                           },
                           )

    second_response= client.post("/users",
                                 json={
                                     "email":"mauro@example.com",
                                     "password": "Mauro123!",
                                 },
                                 )
    second_data= second_response.json()

    assert second_response.status_code ==409
    assert second_data["detail"] == "Email already registered"


def test_user_login_succeeds(client):
    client.post("/users",json={
                            "email": "mauro@example.com",
                            "password": "Mauro123!",
                           }, )

    response = client.post("/login",json={"email": "mauro@example.com",
                            "password": "Mauro123!",
                           }, )
    data = response.json()

    assert response.status_code == 200
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert data["access_token"]
    assert data["token_type"] == "bearer"

def test_user_login_wrong_password(client):
    client.post("/users",json={
                        "email": "mauro@example.com",
                        "password": "Mauro123!",
                        }, )
    response= client.post("/login",json={
                    "email": "mauro@example.com",
                    "password": "wrong_password",
                    }, )
    data= response.json()

    assert response.status_code == 401
    assert data["detail"] == "Invalid email or password"

def test_user_missing_email(client):
    response= client.post("/login",json={
                "email": "mauro@example.com",
                "password": "wrong_password",
                }, )

    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Invalid email or password"

def test_users_me_returns_current_user(client):
    client.post(
        "/users",
        json={
            "email": "mauro@example.com",
            "password": "Mauro123!",
        },
    )

    login_response = client.post(
        "/login",
        json={
            "email": "mauro@example.com",
            "password": "Mauro123!",
        },
    )

    access_token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["email"] == "mauro@example.com"
    assert "id" in data

def test_users_me_rejects_missing_token(client):
    response = client.get("/users/me")

    assert response.status_code in (401, 403)

def test_users_me_rejects_invalid_token(client):
    response = client.get(
        "/users/me",
        headers={
            "Authorization": "Bearer fake-token",
        },
    )

    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Invalid authentication credentials"

