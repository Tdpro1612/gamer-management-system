import json
import random
import unicodedata
import pandas as pd
from datetime import date, timedelta, datetime
from faker import Faker

fake = Faker('vi_VN')

# --- CONFIG ---
## Danh sách game và ngày ra mắt (giả sử) để tạo logic chơi và nạp tiền
GAMES = {
    "Cửu Long Tranh Bá": {"launch": datetime(2024, 5, 1)},
    "Hiệp Khách Vô Song": {"launch": datetime(2024, 10, 1)},
    "Tình Kiếm": {"launch": datetime(2025, 3, 1)},
    "Thanh Vân Kiếm": {"launch": datetime(2025, 8, 1)},
    "Tiên Kiếm Kỳ Hiệp": {"launch": datetime(2025, 11, 1)},
}

## Mốc VIP (tổng nạp) để phân loại người chơi theo VIP level, có thể điều chỉnh theo thực tế hoặc mong muốn
VIP_MILESTONES = {i: v for i, v in zip(range(0, 16), [0, 10000, 20000, 50000, 100000, 200000, 500000, 1000000, 2000000, 5000000, 10000000, 20000000, 50000000, 100000000, 200000000, 500000000])}

## code province list for CCCD generation (same as in user data generation, can be reused)
PROVINCES = [
    {"code": "001", "name": "Hà Nội"},
    {"code": "002", "name": "Hà Giang"},
    {"code": "004", "name": "Cao Bằng"},
    {"code": "006", "name": "Bắc Kạn"},
    {"code": "008", "name": "Tuyên Quang"},
    {"code": "010", "name": "Lào Cai"},
    {"code": "011", "name": "Điện Biên"},
    {"code": "012", "name": "Lai Châu"},
    {"code": "014", "name": "Sơn La"},
    {"code": "015", "name": "Yên Bái"},
    {"code": "017", "name": "Hòa Bình"},
    {"code": "019", "name": "Thái Nguyên"},
    {"code": "020", "name": "Lạng Sơn"},
    {"code": "022", "name": "Quảng Ninh"},
    {"code": "024", "name": "Bắc Giang"},
    {"code": "025", "name": "Phú Thọ"},
    {"code": "026", "name": "Vĩnh Phúc"},
    {"code": "027", "name": "Bắc Ninh"},
    {"code": "030", "name": "Hải Dương"},
    {"code": "031", "name": "Hải Phòng"},
    {"code": "033", "name": "Hưng Yên"},
    {"code": "034", "name": "Thái Bình"},
    {"code": "035", "name": "Hà Nam"},
    {"code": "036", "name": "Nam Định"},
    {"code": "037", "name": "Ninh Bình"},
    {"code": "038", "name": "Thanh Hóa"},
    {"code": "040", "name": "Nghệ An"},
    {"code": "042", "name": "Hà Tĩnh"},
    {"code": "044", "name": "Quảng Bình"},
    {"code": "045", "name": "Quảng Trị"},
    {"code": "046", "name": "Thừa Thiên Huế"},
    {"code": "048", "name": "Đà Nẵng"},
    {"code": "049", "name": "Quảng Nam"},
    {"code": "051", "name": "Quảng Ngãi"},
    {"code": "052", "name": "Bình Định"},
    {"code": "054", "name": "Phú Yên"},
    {"code": "056", "name": "Khánh Hòa"},
    {"code": "058", "name": "Ninh Thuận"},
    {"code": "060", "name": "Bình Thuận"},
    {"code": "062", "name": "Kon Tum"},
    {"code": "064", "name": "Gia Lai"},
    {"code": "066", "name": "Đắk Lắk"},
    {"code": "067", "name": "Đắk Nông"},
    {"code": "068", "name": "Lâm Đồng"},
    {"code": "070", "name": "Bình Phước"},
    {"code": "072", "name": "Tây Ninh"},
    {"code": "074", "name": "Bình Dương"},
    {"code": "075", "name": "Đồng Nai"},
    {"code": "077", "name": "Bà Rịa - Vũng Tàu"},
    {"code": "079", "name": "Hồ Chí Minh"},
    {"code": "080", "name": "Long An"},
    {"code": "082", "name": "Tiền Giang"},
    {"code": "083", "name": "Bến Tre"},
    {"code": "084", "name": "Trà Vinh"},
    {"code": "086", "name": "Vĩnh Long"},
    {"code": "087", "name": "Đồng Tháp"},
    {"code": "089", "name": "An Giang"},
    {"code": "091", "name": "Kiên Giang"},
    {"code": "092", "name": "Cần Thơ"},
    {"code": "093", "name": "Hậu Giang"},
    {"code": "094", "name": "Sóc Trăng"},
    {"code": "095", "name": "Bạc Liêu"},
    {"code": "096", "name": "Cà Mau"}
]

# --- HÀM HỖ TRỢ ---
## Xóa dấu tiếng Việt
def remove_accents(text):
    return "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower()

## generate date of birth
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

## Tạo username theo nhiều kiểu dựa trên tên và ngày sinh
def generate_username_style(full_name, birth_date_obj):
    name_no_accent = remove_accents(full_name)
    parts = name_no_accent.split()
    if len(parts) < 2: return name_no_accent + str(random.randint(10, 99))

    firstname = parts[-1] 
    initials = "".join([p[0] for p in parts])
    d, m, y2, y4 = birth_date_obj.strftime("%d"), birth_date_obj.strftime("%m"), birth_date_obj.strftime("%y"), birth_date_obj.strftime("%Y")
    
    styles = [
        f"{initials}{d}{m}{y2}", f"{initials}{firstname}{y2}", 
        f"{firstname}{d}{m}", f"{parts[0]}{firstname}{y2}",
        f"{initials}{y4}", f"{firstname}{random.randint(100, 999)}"
    ]
    return random.choice(styles)

## generate email
def generate_random_email(full_name):
    """Tạo email hỗn hợp: Nickname, Random ký tự, hoặc biến thể Tên"""
    name_no_accent = remove_accents(full_name).replace(" ", "")
    nicknames = ['baby', 'boy', 'girl', 'langtu', 'xinh', 'hacker', 'pro', 'knight', 'shadow', 'cool', 'warrior', 'titan', 'gladiator', 'viking', 'samurai', 'ninja', 'assassin', 'sniper', 'hunter', 'slayer', 'hero', 'legend', 'myth', 'phantom', 'ghost', 'spirit', 'demon', 'angel', 'king', 'queen', 'lord', 'prince', 'duke', 'marshal', 'boss,fire', 'ice', 'thunder', 'storm', 'wind', 'water', 'earth', 'lava', 'magma', 'frost', 'flame', 'blaze', 'flare', 'spark', 'bolt', 'void', 'dark', 'light', 'solar', 'lunar', 'star', 'galaxy', 'cosmos', 'nebula', 'nova', 'dragon', 'phoenix', 'wolf', 'tiger', 'lion', 'eagle', 'hawk', 'falcon', 'cobra', 'viper', 'shark', 'kraken', 'bear', 'panther', 'jaguar', 'raven', 'crow', 'owl', 'bat', 'spider,cyber', 'matrix', 'pixel', 'bit', 'code', 'glitch', 'error', 'system', 'logic', 'vector', 'alpha', 'beta', 'omega', 'delta', 'gamma', 'zeta', 'binary', 'data', 'bot', 'droid', 'silent', 'deadly', 'fast', 'slow', 'crazy', 'mad', 'wild', 'savage', 'brutal', 'toxic', 'noble', 'brave', 'loyal', 'hidden', 'mystic', 'magic', 'ancient', 'future', 'retro', 'urban', 'dark_knight', 'shadow_walker', 'ice_queen', 'fire_dragon', 'neon_hacker', 'iron_man', 'steel_fist', 'gold_leaf', 'silver_bullet', 'blue_ocean', 'red_blood', 'black_hole', 'white_star', 'green_forest', 'purple_haze', 'kiemthe', 'vlam', 'tlbb', 'game_thu', 'dai_ca', 'thieu_gia', 'cong_chua', 'be_yeu', 'ga_con', 'vit_bau', 'trum_cuoi', 'sat_thu', 'vo_song', 'thien_ha', 'doc_co', 'viper', 'zenith', 'apex', 'orbit', 'pulse', 'echo', 'rhythm', 'chaos', 'havoc', 'zen', 'karma', 'destiny', 'fate', 'doom', 'eternal', 'infinite', 'omega', 'prime', 'ultra', 'super', 'mega', 'hyper', 'turbo', 'sonic', 'flash', 'velocity', 'impact', 'shatter', 'crush', 'strike', 'edge', 'fury', 'wrath', 'rage', 'venom', 'stinger', 'claw', 'fang', 'blade', 'sword']

    random_chars = "abcdefghijklmnopqrstuvwxyz"
    domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'fpt.edu.vn', 'vnn.vn']
    
    # Chọn ngẫu nhiên 1 trong 4 kiểu email
    mode = random.choice(['nickname', 'random_str','fakename', 'name_variant'])
    
    if mode == 'nickname':
        prefix = f"{random.choice(nicknames)}{random.randint(10, 9999)}"
    elif mode == 'random_str':
        prefix = f"{''.join(random.choices(random_chars, k=random.randint(4, 7)))}{random.randint(100, 999)}"
    elif mode == 'fakename':
        prefix = f"{fake.email().split('@')[0]}"
    else:
        prefix = f"{name_no_accent[:random.randint(3, 6)]}{random.randint(10, 999)}"
        
    return f"{prefix}@{random.choice(domains)}"

## # generate sdt
def generate_random_phone():
    prefixes = ['090', '091', '098', '032', '035', '070', '086']
    return random.choice(prefixes) + str(random.randint(1000000, 9999999))

## Chọn ngẫu nhiên một tỉnh từ danh sách trên
def get_random_province():
    return random.choice(PROVINCES)
## hàm generate gender
def generate_gender():
    return random.choice(['Male', 'Female'])

## Sửa lại hàm CCCD: truyền trực tiếp province_code vào
def generate_cccd(gender, province_code, birth_date_obj):
    # Thế kỷ 20 (1900-1999): Nam 0, Nữ 1
    # Thế kỷ 21 (2000-2099): Nam 2, Nữ 3
    year_born = birth_date_obj.year
    
    if year_born < 2000:
        g_code = '0' if gender == 'Male' else '1'
    else:
        g_code = '2' if gender == 'Male' else '3'
        
    year_suffix = birth_date_obj.strftime("%y")
    random_suffix = str(random.randint(100000, 999999))
    
    return f"{province_code}{g_code}{year_suffix}{random_suffix}"

## Tạo địa chỉ khớp với tỉnh
def generate_address_by_province(province_name):
    return f"{fake.street_address()}, {province_name}"

# Thực thi tạo user data
## Hàm hỗ trợ generate user data
def create_final_user_list(total_count, numsday_at_create=730):
    users = []
    used_emails, used_phones, used_usernames, used_user_ids, used_cccds = set(), set(), set(), set(), set()
    
    # Định nghĩa nhóm tuổi: (min, max, trọng số %)
    # Nhóm < 20 đổi thành 16-19
    age_groups = [(16, 19, 10), (20, 25, 20), (26, 30, 40), (31, 35, 20), (36, 60, 10)]
    groups = [(g[0], g[1]) for g in age_groups]
    weights = [g[2] for g in age_groups]

    while len(users) < total_count:
        # 1. Smart ID (202 + 26 + 5 số)
        user_id = f"20226{str(random.randint(0, 99999)).zfill(5)}"
        if user_id in used_user_ids: continue

        # 2. Tuổi & Ngày sinh
        min_age, max_age = random.choices(groups, weights=weights, k=1)[0]
        birth_date = generate_birth_date(min_age, max_age)
        
        # 3. Tên & Username & Email
        gender = generate_gender() # Trả về 'Male' hoặc 'Female'
        if gender == 'Male':
            full_name = fake.name_male()
        else:
            full_name = fake.name_female()

        username = generate_username_style(full_name, birth_date)
        email = generate_random_email(full_name)
        
        # 4. Số điện thoại
        phone = generate_random_phone()
        # 5 address and cccd
        province = get_random_province()
        address = generate_address_by_province(province['name'])
        cccd = generate_cccd(gender, province['code'], birth_date)
        if (username in used_usernames) or (email in used_emails) or (phone in used_phones) or (cccd in used_cccds):
            continue

        users.append({
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "birthday": birth_date.strftime("%Y-%m-%d"),
            "gender": gender,
            "age_group": f"{min_age}-{max_age}",
            "phone": phone,
            "email": email,
            "address": address,
            "job": fake.job(),
            "cccd": cccd,
            "created_at": (datetime.now() - timedelta(days=random.randint(0, numsday_at_create))).strftime("%Y-%m-%d %H:%M:%S")
        })
        
        used_user_ids.add(user_id); used_usernames.add(username); used_emails.add(email); used_phones.add(phone); used_cccds.add(cccd)
    
    return users

## Thực thi tạo user data
data = create_final_user_list(1000)
with open('users_game_ready.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

    
# --- THỰC THI ---


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