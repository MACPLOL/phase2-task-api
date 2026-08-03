def test_list_tasks_when_database_is_empty(client, auth_headers):
    response = client.get(
        "/tasks",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_create_task(client, auth_headers):
    response = client.post(
        "/tasks",
        json={
            "text": "Temporary test task",
            "priority": "medium",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["text"] == "Temporary test task"
    assert data["priority"] == "medium"
    assert data["completed"] is False


def test_create_task_requires_authentication(client):
    response = client.post(
        "/tasks",
        json={
            "text": "Unauthorized task",
            "priority": "medium",
        },
    )

    assert response.status_code in (401, 403)


def test_list_tasks_returns_tasks_in_ascending_id_order(client, auth_headers):
    client.post(
        "/tasks",
        json={"text": "Task A", "priority": "low"},
        headers=auth_headers,
    )
    client.post(
        "/tasks",
        json={"text": "Task B", "priority": "medium"},
        headers=auth_headers,
    )

    response = client.get(
        "/tasks",
        headers=auth_headers,
    )
    data = response.json()

    assert response.status_code == 200
    assert data[0]["text"] == "Task A"
    assert data[1]["text"] == "Task B"


def test_list_tasks_returns_tasks_in_descending_id_order(client, auth_headers):
    client.post(
        "/tasks",
        json={"text": "Task A", "priority": "low"},
        headers=auth_headers,
    )
    client.post(
        "/tasks",
        json={"text": "Task B", "priority": "medium"},
        headers=auth_headers,
    )

    response = client.get(
        "/tasks?sort_order=desc",
        headers=auth_headers,
    )
    data = response.json()

    assert response.status_code == 200
    assert data[0]["text"] == "Task B"
    assert data[1]["text"] == "Task A"


def test_list_tasks_rejects_invalid_sort_order(client, auth_headers):
    response = client.get(
        "/tasks?sort_order=random",
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_list_tasks_rejects_invalid_priority(client, auth_headers):
    response = client.get(
        "/tasks?priority=banana",
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_list_tasks_rejects_limit_below_one(client, auth_headers):
    response = client.get(
        "/tasks?limit=0",
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_list_tasks_rejects_negative_offset(client, auth_headers):
    response = client.get(
        "/tasks?offset=-1",
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_list_tasks_applies_limit_and_offset(client, auth_headers):
    client.post(
        "/tasks",
        json={"text": "Task A"},
        headers=auth_headers,
    )
    client.post(
        "/tasks",
        json={"text": "Task B"},
        headers=auth_headers,
    )
    client.post(
        "/tasks",
        json={"text": "Task C"},
        headers=auth_headers,
    )

    response = client.get(
        "/tasks?limit=1&offset=1",
        headers=auth_headers,
    )
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["text"] == "Task B"


def test_list_tasks_filters_by_priority(client, auth_headers):
    client.post(
        "/tasks",
        json={"text": "Task A", "priority": "low"},
        headers=auth_headers,
    )
    client.post(
        "/tasks",
        json={"text": "Task B", "priority": "medium"},
        headers=auth_headers,
    )
    client.post(
        "/tasks",
        json={"text": "Task C", "priority": "low"},
        headers=auth_headers,
    )

    response = client.get(
        "/tasks?priority=low",
        headers=auth_headers,
    )
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["text"] == "Task A"
    assert data[1]["text"] == "Task C"


def test_list_tasks_filters_by_completed_status(client, auth_headers):
    client.post(
        "/tasks",
        json={"text": "Task A", "priority": "low"},
        headers=auth_headers,
    )

    task_b_response = client.post(
        "/tasks",
        json={"text": "Task B", "priority": "medium"},
        headers=auth_headers,
    )
    task_b_id = task_b_response.json()["id"]

    client.patch(
        f"/tasks/{task_b_id}",
        json={"completed": True},
        headers=auth_headers,
)

    response = client.get(
        "/tasks?completed=true",
        headers=auth_headers,
    )
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["text"] == "Task B"
    assert data[0]["completed"] is True


def test_list_tasks_combines_priority_and_completed_filters(
    client,
    auth_headers,
):
    client.post(
        "/tasks",
        json={"text": "Task A", "priority": "low"},
        headers=auth_headers,
    )

    task_b_response = client.post(
        "/tasks",
        json={"text": "Task B", "priority": "medium"},
        headers=auth_headers,
    )
    task_b_id = task_b_response.json()["id"]

    client.patch(
        f"/tasks/{task_b_id}",
        json={"completed": True},
        headers=auth_headers,
    )

    client.post(
        "/tasks",
        json={
            "text": "Task C",
            "priority": "medium",
        },
        headers=auth_headers,
    )

    response = client.get(
        "/tasks?priority=medium&completed=false",
        headers=auth_headers,
    )
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["text"] == "Task C"
    assert data[0]["completed"] is False
    assert data[0]["priority"] == "medium"


def test_list_tasks_combines_everything(client, auth_headers):
    client.post(
        "/tasks",
        json={"text": "Task A", "priority": "low"},
        headers=auth_headers,
    )

    client.post(
        "/tasks",
        json={"text": "Task B", "priority": "medium"},
        headers=auth_headers,
    )

    task_c_response = client.post(
        "/tasks",
        json={"text": "Task C", "priority": "medium"},
        headers=auth_headers,
    )
    task_c_id = task_c_response.json()["id"]

    client.patch(
        f"/tasks/{task_c_id}",
        json={"completed": True},
        headers=auth_headers,
    )

    client.post(
        "/tasks",
        json={"text": "Task D", "priority": "medium"},
        headers=auth_headers,
    )

    response = client.get(
        "/tasks?priority=medium&completed=false"
        "&sort_order=desc&offset=1&limit=1",
        headers=auth_headers,
    )
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["text"] == "Task B"


def test_get_task_by_id_returns_existing_task(client, auth_headers):
    create_response = client.post(
        "/tasks",
        json={"text": "Task A"},
        headers=auth_headers,
    )
    task_a_id = create_response.json()["id"]

    response = client.get(
        f"/tasks/{task_a_id}",
        headers=auth_headers,
    )
    data = response.json()

    assert response.status_code == 200
    assert data["text"] == "Task A"


def test_delete_task_returns_404_when_missing(client, auth_headers):
    response = client.delete(
        "/tasks/999999",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_update_task_marks_existing_task_completed(client, auth_headers):
    create_response = client.post(
        "/tasks",
        json={"text": "Task A"},
        headers=auth_headers,
    )
    task_a_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_a_id}",
        json={"completed": True},
        headers=auth_headers,
    )

    data = response.json()

    assert response.status_code == 200
    assert data["completed"] is True


def test_update_task_returns_404_when_missing(client, auth_headers):
    response = client.patch(
        "/tasks/99999999",
        json={"completed": True},
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_create_task_returns_422_when_text_is_missing(client, auth_headers):
    response = client.post(
        "/tasks",
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 422

def test_delete_task_removes_existing_task(client, auth_headers):
    create_response = client.post(
        "/tasks",
        json={"text": "Task A"},
        headers=auth_headers,
    )

    task_a_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/tasks/{task_a_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 200

    get_response = client.get(
        f"/tasks/{task_a_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404

def test_user_cannot_read_another_users_task(client):
    # Register user A
    client.post(
        "/users",
        json={
            "email": "usera@example.com",
            "password": "Mauro123!",
        },
    )

    # Log in as user A
    login_a = client.post(
        "/login",
        json={
            "email": "usera@example.com",
            "password": "Mauro123!",
        },
    )
    token_a = login_a.json()["access_token"]
    headers_a = {
        "Authorization": f"Bearer {token_a}",
    }

    # User A creates a task
    create_response = client.post(
        "/tasks",
        json={"text": "User A private task"},
        headers=headers_a,
    )
    task_id = create_response.json()["id"]

    # Register user B
    client.post(
        "/users",
        json={
            "email": "userb@example.com",
            "password": "Mauro123!",
        },
    )

    # Log in as user B
    login_b = client.post(
        "/login",
        json={
            "email": "userb@example.com",
            "password": "Mauro123!",
        },
    )
    token_b = login_b.json()["access_token"]
    headers_b = {
        "Authorization": f"Bearer {token_b}",
    }

    # User B tries to read user A's task
    response = client.get(
        f"/tasks/{task_id}",
        headers=headers_b,
    )

    assert response.status_code == 404

def test_user_cannot_update_another_users_task(client):
    # Register user A
    client.post(
        "/users",
        json={
            "email": "usera@example.com",
            "password": "Mauro123!",
        },
    )

    # Log in as user A
    login_a = client.post(
        "/login",
        json={
            "email": "usera@example.com",
            "password": "Mauro123!",
        },
    )
    token_a = login_a.json()["access_token"]
    headers_a = {
        "Authorization": f"Bearer {token_a}",
    }

    # User A creates a task
    create_response = client.post(
        "/tasks",
        json={"text": "User A private task"},
        headers=headers_a,
    )
    task_id = create_response.json()["id"]

    # Register user B
    client.post(
        "/users",
        json={
            "email": "userb@example.com",
            "password": "Mauro123!",
        },
    )

    # Log in as user B
    login_b = client.post(
        "/login",
        json={
            "email": "userb@example.com",
            "password": "Mauro123!",
        },
    )
    token_b = login_b.json()["access_token"]
    headers_b = {
        "Authorization": f"Bearer {token_b}",
    }

    response = client.patch(
        f"/tasks/{task_id}",
        json={"completed": True},
        headers=headers_b,
    )

    assert response.status_code == 404

def test_user_cannot_delete_another_users_task(client):
    # Register user A
    client.post(
        "/users",
        json={
            "email": "usera@example.com",
            "password": "Mauro123!",
        },
    )

    # Log in as user A
    login_a = client.post(
        "/login",
        json={
            "email": "usera@example.com",
            "password": "Mauro123!",
        },
    )
    token_a = login_a.json()["access_token"]
    headers_a = {
        "Authorization": f"Bearer {token_a}",
    }

    # User A creates a task
    create_response = client.post(
        "/tasks",
        json={"text": "User A private task"},
        headers=headers_a,
    )
    task_id = create_response.json()["id"]

    # Register user B
    client.post(
        "/users",
        json={
            "email": "userb@example.com",
            "password": "Mauro123!",
        },
    )

    # Log in as user B
    login_b = client.post(
        "/login",
        json={
            "email": "userb@example.com",
            "password": "Mauro123!",
        },
    )
    token_b = login_b.json()["access_token"]
    headers_b = {
        "Authorization": f"Bearer {token_b}",
    }

    response = client.delete(
        f"/tasks/{task_id}",
        headers=headers_b,
    )

    assert response.status_code == 404