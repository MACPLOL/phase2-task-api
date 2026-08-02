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
    assert data["email"] == "mauro@example.com"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data

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

