import random
import json
import unicodedata
from datetime import date, timedelta, datetime
from faker import Faker

fake = Faker('vi_VN')

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

# Xóa dấu tiếng Việt
def remove_accents(text):
    """Chuyển tiếng Việt có dấu thành không dấu"""
    return "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower()

# Tạo username theo nhiều kiểu dựa trên tên và ngày sinh
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

# tạo email ngẫu nhiên
def generate_random_email(full_name):
    """Tạo email hỗn hợp: Nickname, Random ký tự, hoặc biến thể Tên"""
    name_no_accent = remove_accents(full_name).replace(" ", "")
    nicknames = ['baby', 'boy', 'girl', 'langtu', 'xinh', 'hacker', 'pro', 'knight', 'shadow', 'cool']
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

# generate sdt
def generate_random_phone():
    prefixes = ['090', '091', '098', '032', '035', '070', '086']
    return random.choice(prefixes) + str(random.randint(1000000, 9999999))

# Chọn ngẫu nhiên một tỉnh từ danh sách trên
def get_random_province():
    return random.choice(PROVINCES)
# hàm generate gender
def generate_gender():
    return random.choice(['Male', 'Female'])

# Sửa lại hàm CCCD: truyền trực tiếp province_code vào
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

# Tạo địa chỉ khớp với tỉnh
def generate_address_by_province(province_name):
    return f"{fake.street_address()}, {province_name}"

# Tạo danh sách user hoàn chỉnh với các thông tin chi tiết
def create_final_user_list(total_count):
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
        birth_date = date.today() - timedelta(days=(min_age * 365 + random.randint(0, (max_age-min_age)*365)))
        
        # 3. Tên & Username & Email
        full_name = fake.name()
        username = generate_username_style(full_name, birth_date)
        email = generate_random_email(full_name)
        
        # 4. Số điện thoại
        prefixes = ['090', '091', '098', '032', '035', '070', '086']
        phone = random.choice(prefixes) + str(random.randint(1000000, 9999999))
        # 5 address and cccd
        province = get_random_province()
        address = generate_address_by_province(province['name'])
        gender = generate_gender()
        cccd = generate_cccd(gender, province['code'], birth_date)
        if (username in used_usernames) or (email in used_emails) or (phone in used_phones) or (cccd in used_cccds):
            continue

        users.append({
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "birthday": birth_date.strftime("%d/%m/%Y"),
            "gender": gender,
            "age_group": f"{min_age}-{max_age}",
            "phone": phone,
            "email": email,
            "address": address,
            "job": fake.job(),
            "cccd": cccd,
            "created_at": (datetime.now() - timedelta(days=random.randint(0, 730))).strftime("%d/%m/%Y %H:%M:%S")
        })
        
        used_user_ids.add(user_id); used_usernames.add(username); used_emails.add(email); used_phones.add(phone); used_cccds.add(cccd)
    
    return users

# Thực thi
data = create_final_user_list(1000)
with open('users_game_ready.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

# In thử mẫu 10 user để xem sự khác biệt
print(f"{'ID':<12} | {'USERNAME':<15} | {'EMAIL':<25} | {'TUỔI'}")
print("-" * 70)
for u in data[:10]:
    print(f"{u['user_id']:<12} | {u['username']:<15} | {u['email']:<25} | {u['age_group']}")