import pytest

def test_health_check(client):
    """Testa l'endpoint di health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_register_user(client):
    """Testa la registrazione di un nuovo utente."""
    response = client.post(
        "/api/auth/register",
        json={"username": "newuser", "password": "newpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    
    # Test registrazione duplicata
    response = client.post(
        "/api/auth/register",
        json={"username": "newuser", "password": "newpassword"}
    )
    assert response.status_code == 400

def test_login_user(client):
    """Testa il login di un utente esistente (testuser creato nel conftest)."""
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_user(client):
    """Testa login con credenziali sbagliate."""
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    
    response = client.post(
        "/api/auth/login",
        json={"username": "notexist", "password": "password"}
    )
    assert response.status_code == 401

def test_get_threads_authenticated(client):
    """Testa l'accesso ad un endpoint protetto usando il token JWT."""
    # 1. Ottieni il token
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # 2. Usa il token per ottenere l'utente corrente
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/chat/threads", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_threads_unauthenticated(client):
    """Testa accesso senza token."""
    response = client.get("/api/chat/threads")
    assert response.status_code == 401
