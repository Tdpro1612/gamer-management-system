import sqlite3
import pandas as pd
# Giả sử bạn dùng hàm build_and_export ở trên để có 3 list: users_table, user_games_table, txns_table

def save_to_sqlite(users_path, user_games_path, txns_path):
    conn = sqlite3.connect('game_data.db')
    
    # 1. Nạp các bảng nhỏ (Dùng replace để luôn làm mới dữ liệu)
    pd.read_csv(users_path).to_sql('Users', conn, if_exists='replace', index=False)
    pd.read_csv(user_games_path).to_sql('User_Games', conn, if_exists='replace', index=False)
    
    # 2. Xử lý bảng Transactions (Bảng lớn)
    # Cách an toàn nhất: Dùng một cờ hiệu (flag) để replace lần đầu, sau đó mới append
    first_chunk = True
    for chunk in pd.read_csv(txns_path, chunksize=50000):
        if first_chunk:
            # Chunk đầu tiên sẽ xóa bảng cũ và tạo bảng mới
            chunk.to_sql('Transactions', conn, if_exists='replace', index=False)
            first_chunk = False
        else:
            # Các chunk tiếp theo nối tiếp vào bảng vừa tạo
            chunk.to_sql('Transactions', conn, if_exists='append', index=False)

    # 3. Tạo Index (Phần này giữ nguyên vì Index chỉ được tạo 1 lần sau khi có data)
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_search ON Users(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_games_user ON User_Games(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_txns_composite ON Transactions(user_id, game_name, created_at)")

    # 4. Bảng Accounts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Accounts (
            acc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            full_name TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO Accounts (username, password, role) VALUES ('admin', 'nguyen123@', 'admin')")

    conn.commit()
    conn.close()
    print("🚀 Đã làm sạch và nạp mới dữ liệu game_data.db thành công!")

# Gọi hàm này sau khi bạn đã có dữ liệu từ các bước trước
save_to_sqlite(
    "data/users_game_clean.csv", 
    "data/game_data_final.csv", 
    "data/transaction_gamer.csv"
)