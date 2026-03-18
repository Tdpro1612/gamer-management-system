import pytest
import sys
import os
from httpx import AsyncClient, ASGITransport
from main import app  # Import app từ file main.py của bạn

# Mock dữ liệu để test
USER_LOGIN = {"username": "admin", "password": "nguyen123@"}
SEARCH_QUERY = "202268274002174" # Thay bằng một ID có thật trong DB của bạn
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.mark.asyncio
async def test_full_workflow():
    # 1. Khởi tạo Transport cho FastAPI app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        # --- TEST 1: LOGIN ---
        print("\n>>> Testing Login...")
        login_response = await ac.post("/login", data=USER_LOGIN)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful!")

        # --- TEST 2: SEARCH USER (Authenticated) ---
        print(">>> Testing Search User...")
        search_res = await ac.get(f"/search-user?user_id={SEARCH_QUERY}", headers=headers)
        assert search_res.status_code == 200
        assert "data" in search_res.json()
        print(f"Search User successful: {search_res.json()['data']}")

        # --- TEST 3: SEARCH USER (Unauthenticated) ---
        print(">>> Testing Unauthorized Access...")
        fail_res = await ac.get(f"/search-user?user_id={SEARCH_QUERY}")
        assert fail_res.status_code == 401
        assert fail_res.json()["detail"] == "Not authenticated"
        print("Unauthorized check passed!")

        # --- TEST 4: SEARCH TRANSACTIONS ---
        print(">>> Testing Search Transactions...")
        tx_res = await ac.get(f"/search-transactions?user_id={SEARCH_QUERY}", headers=headers)
        assert tx_res.status_code == 200
        # Kiểm tra xem có bị trùng dữ liệu không (bill_id duy nhất)
        data = tx_res.json()["data"]
        bill_ids = [t["bill_id"] for t in data]
        if len(bill_ids) != len(set(bill_ids)):
            print("WARNING: Dữ liệu vẫn bị trùng lặp (Double data detected)!")
        else:
            print("Transactions data is clean!")

        # --- TEST 5: UPDATE USER (Quyền Admin) ---
        print(">>> Testing Update User (Admin)...")
        update_res = await ac.put(
            f"/update-user/{SEARCH_QUERY}?new_phone=0999888777", 
            headers=headers
        )
        assert update_res.status_code == 200
        print("Update successful!")

@pytest.mark.asyncio
async def test_login_fail():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/login", data={"username": "wrong", "password": "wrong"})
        assert res.status_code == 400
        print("\n>>> Wrong password check passed!")