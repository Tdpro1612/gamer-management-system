from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import sqlite3

app = FastAPI(title="Game Management System API")

# 1. CẤU HÌNH BẢO MẬT
# pwd_context dùng để mã hóa và kiểm tra mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    conn = sqlite3.connect('game_data.db')
    conn.row_factory = sqlite3.Row
    return conn

# 2. HÀM KIỂM TRA QUYỀN TRUY CẬP
def get_current_account(token: str = Depends(oauth2_scheme)):
    conn = get_db()
    # Ở bản demo này, ta coi token chính là username để đơn giản hóa
    acc = conn.execute("SELECT * FROM Accounts WHERE username = ?", (token,)).fetchone()
    if not acc:
        raise HTTPException(status_code=401, detail="Tài khoản không hợp lệ")
    return dict(acc)

# 3. API ĐĂNG NHẬP (Lấy vé thông hành)
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db()
    acc = conn.execute("SELECT * FROM Accounts WHERE username = ?", (form_data.username,)).fetchone()
    
    # Kiểm tra user và mật khẩu (Nếu bạn chưa hash thì so sánh trực tiếp)
    if not acc or form_data.password != acc['password']:
        raise HTTPException(status_code=400, detail="Sai tài khoản hoặc mật khẩu")
    
    return {"access_token": acc['username'], "token_type": "bearer"}

# 4. API SEARCH (All-in-one) - Staff & Admin đều dùng được
@app.get("/search-user")
def search_user(q: str, current_acc: dict = Depends(get_current_account)):
    conn = get_db()
    # Tìm kiếm theo ID, Username, SĐT hoặc email (Dùng Index đã tạo hôm qua)
    query = """
        SELECT * FROM Users 
        WHERE user_id = ? OR username = ? OR phone = ? OR email = ?
    """
    user = conn.execute(query, (q, q, q, q)).fetchone()
    
    if not user:
        return {"msg": "Không tìm thấy người chơi này"}
    
    return {
        "search_by": current_acc['full_name'],
        "data": dict(user)
    }

# 5. API THAY ĐỔI THÔNG TIN - Chỉ Admin mới được phép
@app.put("/update-user/{user_id}")
def update_user(user_id: str, new_phone: str, current_acc: dict = Depends(get_current_account)):
    if current_acc['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có quyền sửa dữ liệu!")
    
    conn = get_db()
    conn.execute("UPDATE Users SET phone = ? WHERE user_id = ?", (new_phone, user_id))
    conn.commit()
    return {"msg": f"Account {current_acc['username']} đã cập nhật SĐT cho user {user_id}"}

# search transactions by user_id, game, server - Staff & Admin đều dùng được
@app.get("/search-transactions")
def search_transactions(user_id: str, game: str = None, server: str = None, current_acc: dict = Depends(get_current_account)):
    conn = get_db()
    # Tìm kiếm giao dịch theo user_id
    query = """
        SELECT * FROM Transactions 
        WHERE user_id = ?
        game = COALESCE(?, game)
    """
    txns = conn.execute(query, (user_id,)).fetchall()
    
    if not txns:
        return {"msg": f"Không tìm thấy giao dịch nào cho người chơi ID {user_id}"}
    
    return {
        "search_by": current_acc['full_name'],
        "data": [dict(txn) for txn in txns]
    }