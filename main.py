from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import sqlite3
from typing import Optional

app = FastAPI(title="Game Management System API")

# 1. CẤU HÌNH BẢO MẬT
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    conn = sqlite3.connect('game_data.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# 2. HÀM KIỂM TRA QUYỀN TRUY CẬP
def get_current_account(token: str = Depends(oauth2_scheme), db: sqlite3.Connection = Depends(get_db)):
    # Ở bản demo này, ta coi token chính là username
    acc = db.execute("SELECT * FROM Accounts WHERE username = ?", (token,)).fetchone()
    if not acc:
        raise HTTPException(status_code=401, detail="Tài khoản không hợp lệ")
    return dict(acc)

# 3. API ĐĂNG NHẬP
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: sqlite3.Connection = Depends(get_db)):
    acc = db.execute("SELECT * FROM Accounts WHERE username = ?", (form_data.username,)).fetchone()
    
    # Kiểm tra user và mật khẩu (So sánh trực tiếp nếu bạn chưa hash trong DB)
    if not acc or form_data.password != acc['password']:
        raise HTTPException(status_code=400, detail="Sai tài khoản hoặc mật khẩu")
    
    return {"access_token": acc['username'], "token_type": "bearer"}

# 4. API SEARCH USER
@app.get("/search-user")
def search_user(
    user_id: Optional[str] = None, 
    username: Optional[str] = None, 
    phone: Optional[str] = None, 
    email: Optional[str] = None,
    current_acc: dict = Depends(get_current_account), 
    db: sqlite3.Connection = Depends(get_db)
):
    # Xây dựng câu lệnh SQL động dựa trên việc ô nào có dữ liệu
    # Dùng logic WHERE 1=1 để dễ dàng nối thêm các điều kiện AND
    query = "SELECT * FROM Users WHERE 1=1"
    params = []

    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    if username:
        query += " AND username = ?"
        params.append(username)
    if phone:
        query += " AND phone = ?"
        params.append(phone)
    if email:
        query += " AND email = ?"
        params.append(email)

    # Nếu không nhập ô nào cả
    if not params:
        raise HTTPException(status_code=400, detail="Vui lòng nhập ít nhất một thông tin tìm kiếm")

    user = db.execute(query, params).fetchone()
    
    if not user:
        return {"msg": "Không tìm thấy người chơi phù hợp với các tiêu chí trên"}
    
    return {
        "search_by": current_acc['full_name'] or current_acc['username'],
        "data": dict(user)
    }
# 5. API THAY ĐỔI THÔNG TIN - Chỉ Admin
@app.put("/update-user/{user_id}")
def update_user(user_id: str, new_phone: str, current_acc: dict = Depends(get_current_account), db: sqlite3.Connection = Depends(get_db)):
    if current_acc['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có quyền sửa dữ liệu!")
    
    db.execute("UPDATE Users SET phone = ? WHERE user_id = ?", (new_phone, user_id))
    db.commit()
    return {"msg": f"Account {current_acc['username']} đã cập nhật SĐT cho user {user_id}"}

# 6. API SEARCH TRANSACTIONS - Sửa lỗi logic SQL và tham số
@app.get("/search-transactions")
def search_transactions(
    user_id: str, 
    game: Optional[str] = None, 
    server: Optional[str] = None, 
    limit: int = 50,
    current_acc: dict = Depends(get_current_account), 
    db: sqlite3.Connection = Depends(get_db)
):
    # Sử dụng COALESCE hoặc logic OR để handle tham số Optional
    # Lưu ý: Tên cột phải khớp với transaction_gamer.csv (game_name, server_id)
    query = """
        SELECT * FROM Transactions 
        WHERE user_id = ? 
        AND (game_name = ? OR ? IS NULL)
        AND (server_id = ? OR ? IS NULL)
        ORDER BY created_at DESC
        LIMIT ?
    """
    txns = db.execute(query, (user_id, game, game, server, server, limit)).fetchall()
    
    if not txns:
        return {"msg": f"Không tìm thấy giao dịch nào phù hợp cho ID {user_id}"}
    
    return {
        "search_by": current_acc['full_name'] or current_acc['username'],
        "count": len(txns),
        "data": [dict(txn) for txn in txns]
    }