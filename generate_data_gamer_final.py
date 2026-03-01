import random
import unicodedata
import pandas as pd
from datetime import date, timedelta, datetime
from faker import Faker

fake = Faker('vi_VN')

# --- CONFIG ---
GAMES = {
    "Cửu Long Tranh Bá": {"launch": datetime(2024, 5, 1)},
    "Hiệp Khách Vô Song": {"launch": datetime(2024, 10, 1)},
    "Tình Kiếm": {"launch": datetime(2025, 3, 1)},
    "Thanh Vân Kiếm": {"launch": datetime(2025, 8, 1)},
    "Tiên Kiếm Kỳ Hiệp": {"launch": datetime(2025, 11, 1)},
}
VIP_MILESTONES = {i: v for i, v in zip(range(0, 16), [0, 10000, 20000, 50000, 100000, 200000, 500000, 1000000, 2000000, 5000000, 10000000, 20000000, 50000000, 100000000, 200000000, 500000000])}

# --- HELPERS ---
def remove_accents(text):
    return "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower()

## Generate random 1000 users with profiles clude : user_id, username, full_name, phone, email, job, address, cccd
### generate date of birth
def generate_birth_date(min_age, max_age):
    """Tạo ngày sinh ngẫu nhiên trong khoảng tuổi cụ thể"""
    today = date.today()
    # Xử lý trường hợp 36+ (giả sử tối đa là 60 tuổi)
    if max_age is None: max_age = 60
    
    start_date = date(today.year - max_age, 1, 1)
    end_date = date(today.year - min_age, today.month, today.day)
    
    days_between = (end_date - start_date).days
    # Đảm bảo days_between luôn dương
    days_between = max(1, days_between)
    
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)
### generate email
def generate_random_email(full_name):
    """Tạo email ngẫu nhiên dựa trên tên hoặc nickname"""
    name_no_accent = remove_accents(full_name).replace(" ", "")
    nicks = ['baby', 'langtu', 'boy', 'hacker', 'knight', 'shadow', 'kute', 'pro', 'abcxyz', 'phongba']
    domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'vnn.vn']
    
    mode = random.choice(['nick', 'name', 'rand'])
    if mode == 'nick':
        prefix = f"{random.choice(nicks)}{random.randint(10, 999)}"
    elif mode == 'name':
        prefix = f"{name_no_accent[:random.randint(4, 7)]}{random.randint(10, 999)}"
    else:
        prefix = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=5)) + str(random.randint(100, 999))
    return f"{prefix}@{random.choice(domains)}"
# generate user profiles
def generate_full_user_data(min_age, max_age):
    today = date.today()
    
    # 1. Logic Ngày sinh
    start_date = date(today.year - max_age, 1, 1)
    end_date = date(today.year - min_age, today.month, today.day)
    days_between = (end_date - start_date).days
    birth_date_obj = start_date + timedelta(days=random.randrange(days_between))
    
    birth_date_str = birth_date_obj.strftime("%d/%m/%Y")
    year_suffix = birth_date_obj.strftime("%y") # Lấy 2 số cuối năm sinh (ví dụ: 95)

    # 2. Logic Số điện thoại Việt Nam (các đầu số phổ biến)
    prefixes = ['090', '091', '098', '032', '035', '070', '086']
    phone = random.choice(prefixes) + str(random.randint(1000000, 9999999))

    # 3. Logic Số CCCD (Giả lập cấu trúc thực tế)
    # Mã tỉnh (001-096), Giới tính (Nam: 0, 2, 4...; Nữ: 1, 3, 5...), Năm sinh, Số ngẫu nhiên
    province_code = str(random.randint(1, 96)).zfill(3)
    gender_code = random.choice(['0', '1']) # 0 cho Nam, 1 cho Nữ (thế kỷ 20)
    cccd = f"{province_code}{gender_code}{year_suffix}{random.randint(100000, 999999)}"

    return {
        "full_name": fake.name(),
        "birthday": birth_date_str,
        "gender": "Nam" if gender_code == '0' else "Nữ",
        "cccd": cccd,
        "phone": phone,
        "email": fake.free_email(),
        "address": fake.address().replace('\n', ', '),
        "job": fake.job()
    }

def create_user_list(count, min_age, max_age):
    return [generate_full_user_data(min_age, max_age) for _ in range(count)]

# --- THỰC THI ---
quantity = 5
min_a, max_a = 22, 35
user_list = create_user_list(quantity, min_a, max_a)


def generate_ign(full_name, server_id):
    """Tạo tên nhân vật dựa trên tên thật và server"""
    nicks = ['KiemThan', 'BaChu', 'DocCo', 'AcMa', 'ThienSu', 'LanhLung', 'VoSong']
    name_part = remove_accents(full_name.split()[-1]).capitalize()
    return f"{random.choice(nicks)}_{name_part}{server_id}"

def generate_transactions_v2(total_amount, start_date, end_limit, user_id, game_name, server_name):
    txns = []
    remaining = total_amount
    curr = start_date
    today = end_limit if end_limit else datetime.now()
    if remaining <= 0: return []

    while remaining > 0 and curr < today:
        if curr.day in range(1, 6) or curr.weekday() >= 4:
            # Chọn mức nạp ngẫu nhiên nhưng không vượt quá số còn lại
            possible_amts = [v for v in VIP_MILESTONES.values() if 0 < v <= remaining]
            amt = random.choice(possible_amts) if possible_amts else remaining
            
            txn_t = curr.replace(hour=random.randint(8, 22), minute=random.randint(0, 59))
            
            txns.append({
                "txn_id": f"BILL{txn_t.strftime('%y%m%d%H%M%S')}{random.randint(10,99)}",
                "user_id": user_id,
                "game": game_name,
                "server": server_name, 
                "date": txn_t.strftime("%d/%m/%Y %H:%M:%S"),
                "amount": amt,
                "method": random.choice(["momo", "banking", "inapp"]),
            })
            remaining -= amt
        curr += timedelta(days=random.randint(1, 5))
    return txns

# --- MAIN PROCESS ---
def build_and_export(user_count=1000):
    users_table, user_games_table, txns_table = [], [], []
    
    for _ in range(user_count):
        fname = fake.name()
        uid = f"20226{str(random.randint(0, 99999)).zfill(5)}"
        uname = remove_accents(fname).replace(" ","") + str(random.randint(10,99))
        
        # Thêm User với Email ngẫu nhiên
        users_table.append({
            "user_id": uid, 
            "username": uname, 
            "full_name": fname, 
            "phone": f"09{random.randint(10000000, 99999999)}",
            "email": generate_random_email(fname) # Đã gọi lại hàm email ở đây
        })

        # Một người có thể chơi từ 1 đến 2 game
        played_games = random.sample(list(GAMES.keys()), k=random.randint(1, 2))
        
        for gname in played_games:
            # Một người có thể chơi từ 1 đến 3 server trong 1 game
            num_servers = random.choices([1, 2, 3], weights=[70, 20, 10])[0]
            server_ids = sorted(random.sample(range(1, 21), k=num_servers))
            
            last_vip_level = 0
            for s_id in server_ids:
                server_name = f"S{s_id}"
                # Logic: Server sau nạp >= server trước (nhảy server để đua top)
                current_vip_level = random.choice([v for v in [0, 5, 10, 15] if v >= last_vip_level])
                ign = generate_ign(fname, s_id)
                
                user_games_table.append({
                    "user_id": uid, 
                    "game": gname, 
                    "server": server_name, 
                    "ign": ign, 
                    "vip": current_vip_level
                })
                
                if current_vip_level > 0:
                    # Ngày bắt đầu chơi server này (server càng mới chơi càng muộn)
                    join_date = GAMES[gname]["launch"] + timedelta(days=s_id * 3) 
                    history = generate_transactions_v2(
                        VIP_MILESTONES[current_vip_level], join_date, datetime.now(), uid, gname, server_name
                    )
                    txns_table.extend(history)
                
                last_vip_level = current_vip_level

    # Xuất dữ liệu ra CSV
    pd.DataFrame(users_table).to_csv("sql_users.csv", index=False)
    pd.DataFrame(user_games_table).to_csv("sql_user_games.csv", index=False)
    pd.DataFrame(txns_table).to_csv("sql_transactions.csv", index=False)
    
    print(f"✅ Đã tạo {len(users_table)} Users (kèm Email)")
    print(f"✅ Đã tạo {len(user_games_table)} Bản ghi nhân vật (User_Games)")
    print(f"✅ Đã tạo {len(txns_table)} Giao dịch (Transactions khớp Server)")

build_and_export(1000)