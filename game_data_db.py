import sqlite3
import pandas as pd
# Giả sử bạn dùng hàm build_and_export ở trên để có 3 list: users_table, user_games_table, txns_table

def save_to_sqlite(users, user_games, txns):
    # Kết nối (hoặc tạo mới) file database
    conn = sqlite3.connect('game_data.db')
    
    # Dùng pandas để đẩy data vào SQL cực nhanh
    pd.DataFrame(users).to_sql('Users', conn, if_exists='replace', index=False)
    pd.DataFrame(user_games).to_sql('User_Games', conn, if_exists='replace', index=False)
    pd.DataFrame(txns).to_sql('Transactions', conn, if_exists='replace', index=False)
    
    # 2. Tạo Index ngay sau khi nạp xong dữ liệu
    cursor = conn.cursor()
    # Index cho bảng Users để tìm kiếm thông tin nhanh
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_search ON Users(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_phone ON Users(phone)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON Users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON Users(email)")
    # Index cho bảng User_Games để tìm nhanh game của user
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_games_user ON User_Games(user_id)")
    # Index cho bảng Transactions để tìm giao dịch nhanh
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_txns_user_game_date ON Transactions(user_id, game, date)")


    # Thêm lệnh tạo bảng Accounts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Accounts (
            acc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            full_name TEXT
        )
    """)

    # Kiểm tra nếu chưa có admin thì mới tạo để tránh lỗi trùng lặp (Unique)
    cursor.execute("INSERT OR IGNORE INTO Accounts (username, password, role) VALUES ('admin', 'nguyen123@', 'admin')")

    conn.commit()
    conn.close()
    print("🚀 Đã tạo xong file game_data.db!")

# Gọi hàm này sau khi bạn đã có dữ liệu từ các bước trước
save_to_sqlite(pd.read_csv("sql_users.csv"), pd.read_csv("sql_user_games.csv"), pd.read_csv("sql_transactions.csv"))