from src.lab_server import create_app


def test_health_endpoint_is_available():
    client = create_app().test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_lab_service_never_executes_or_reflects_payload():
    client = create_app().test_client()

    response = client.get("/search?q=%3Cscript%3Ealert(1)%3C/script%3E")

    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == "request reached the lab service"
    assert "<script>" not in response.get_data(as_text=True)

