def test_list_tasks_when_database_is_empty(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_create_task(client):
    response = client.post(
        "/tasks",
        json={
            "text": "Temporary test task",
            "priority": "medium",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["text"] == "Temporary test task"
    assert data["priority"] == "medium"
    assert data["completed"] is False


def test_list_tasks_returns_tasks_in_ascending_id_order(client):
    client.post(
        "/tasks",
        json={"text": "Task A", "priority": "low"},
    )
    client.post(
        "/tasks",
        json={"text": "Task B", "priority": "medium"},
    )

    response = client.get("/tasks")
    data = response.json()

    assert response.status_code == 200
    assert data[0]["text"] == "Task A"
    assert data[1]["text"] == "Task B"


def test_list_tasks_returns_tasks_in_descending_id_order(client):
    client.post(
        "/tasks",
        json={"text": "Task A", "priority": "low"},
    )
    client.post(
        "/tasks",
        json={"text": "Task B", "priority": "medium"},
    )

    response = client.get("/tasks?sort_order=desc")
    data = response.json()

    assert response.status_code == 200
    assert data[0]["text"] == "Task B"
    assert data[1]["text"] == "Task A"

def test_list_tasks_rejects_invalid_sort_order(client):
    response = client.get("/tasks?sort_order=random")

    assert response.status_code == 422

def test_list_tasks_rejects_invalid_priority(client):
    response = client.get("/tasks?priority=banana")

    assert response.status_code == 422

def test_list_tasks_rejects_limit_below_one(client):
    response = client.get("/tasks?limit=0")

    assert response.status_code == 422

def test_list_tasks_rejects_negative_offset(client):
    response = client.get("/tasks?offset=-1")

    assert response.status_code == 422

def test_list_tasks_applies_limit_and_offset(client):
    client.post(
        "/tasks",
        json={"text": "Task A"},
    )
    client.post(
        "/tasks",
        json={"text": "Task B"},
    )
    client.post(
        "/tasks",
        json={"text": "Task C"},
    )

    response = client.get("/tasks?limit=1&offset=1")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["text"] == "Task B"

def test_list_tasks_filters_by_priority(client):
    client.post(
        "/tasks",
        json={"text": "Task A", "priority": "low"},
    )
    client.post(
        "/tasks",
        json={"text": "Task B", "priority": "medium"},
    )
    client.post(
        "/tasks",
        json={"text": "Task C", "priority": "low"},
    )

    response = client.get("/tasks?priority=low")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["text"] == "Task A"
    assert data[1]["text"] == "Task C"

def test_list_tasks_filters_by_completed_status(client):
    client.post(
        "/tasks",
        json={"text": "Task A", "priority": "low"},
    )

    task_b_response = client.post(
        "/tasks",
        json={"text": "Task B", "priority": "medium"},
    )
    task_b_id = task_b_response.json()["id"]

    client.patch(
        f"/tasks/{task_b_id}",
        json={"completed": True},
    )

    response = client.get("/tasks?completed=true")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["text"] == "Task B"
    assert data[0]["completed"] is True

def test_list_tasks_combines_priority_and_completed_filters(client):
    client.post(
        "/tasks",
        json={"text": "Task A", "priority": "low"},
    )

    task_b_response = client.post(
        "/tasks",
        json={"text": "Task B", "priority": "medium"},
    )
    task_b_id = task_b_response.json()["id"]

    client.patch(
        f"/tasks/{task_b_id}",
        json={"completed": True},
    )
    client.post(
        "/tasks",
        json={"text": "Task C", "priority": "medium", "complete": False},
    )
    response = client.get("/tasks?priority=medium&completed=false")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["text"] == "Task C"
    assert data[0]["completed"] is False
    assert data[0]["priority"] == "medium"


def test_list_tasks_combines_everything(client):
    client.post(
        "/tasks",
        json={"text": "Task A", "priority": "low"},
    )

    client.post(
        "/tasks",
        json={"text": "Task B", "priority": "medium"},
    )

    task_c_response = client.post(
        "/tasks",
        json={"text": "Task C", "priority": "medium"},
    )
    task_c_id = task_c_response.json()["id"]
    client.patch(
        f"/tasks/{task_c_id}",
        json={"completed": True},
    )
    client.post(
        "/tasks",
        json={"text": "Task D", "priority": "medium"},
    )
    response = client.get(
    "/tasks?priority=medium&completed=false"
    "&sort_order=desc&offset=1&limit=1"
)
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["text"] == "Task B"
