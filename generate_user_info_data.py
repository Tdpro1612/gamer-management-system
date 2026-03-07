import json
import random
import unicodedata
import pandas as pd
from datetime import date, timedelta, datetime

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
# Đưa danh sách ra ngoài làm Global Constants
EMAIL_NICKNAMES = ['baby', 'boy', 'girl', 'langtu', 'xinh', 'hacker', 'pro', 'knight', 'shadow', 'cool', 'warrior', 'titan', 'gladiator', 'viking', 'samurai', 'ninja', 'assassin', 'sniper', 'hunter', 'slayer', 'hero', 'legend', 'myth', 'phantom', 'ghost', 'spirit', 'demon', 'angel', 'king', 'queen', 'lord', 'prince', 'duke', 'marshal', 'boss', 'fire', 'ice', 'thunder', 'storm', 'wind', 'water', 'earth', 'lava', 'magma', 'frost', 'flame', 'blaze', 'flare', 'spark', 'bolt', 'void', 'dark', 'light', 'solar', 'lunar', 'star', 'galaxy', 'cosmos', 'nebula', 'nova', 'dragon', 'phoenix', 'wolf', 'tiger', 'lion', 'eagle', 'hawk', 'falcon', 'cobra', 'viper', 'shark', 'kraken', 'bear', 'panther', 'jaguar', 'raven', 'crow', 'owl', 'bat', 'spider', 'cyber', 'matrix', 'pixel', 'bit', 'code', 'glitch', 'error', 'system', 'logic', 'vector', 'alpha', 'beta', 'omega', 'delta', 'gamma', 'zeta', 'binary', 'data', 'bot', 'droid', 'silent', 'deadly', 'fast', 'slow', 'crazy', 'mad', 'wild', 'savage', 'brutal', 'toxic', 'noble', 'brave', 'loyal', 'hidden', 'mystic', 'magic', 'ancient', 'future', 'retro', 'urban', 'dark_knight', 'shadow_walker', 'ice_queen', 'fire_dragon', 'neon_hacker', 'iron_man', 'steel_fist', 'gold_leaf', 'silver_bullet', 'blue_ocean', 'red_blood', 'black_hole', 'white_star', 'green_forest', 'purple_haze', 'kiemthe', 'vlam', 'tlbb', 'game_thu', 'dai_ca', 'thieu_gia', 'cong_chua', 'be_yeu', 'ga_con', 'vit_bau', 'trum_cuoi', 'sat_thu', 'vo_song', 'thien_ha', 'doc_co', 'viper', 'zenith', 'apex', 'orbit', 'pulse', 'echo', 'rhythm', 'chaos', 'havoc', 'zen', 'karma', 'destiny', 'fate', 'doom', 'eternal', 'infinite', 'omega', 'prime', 'ultra', 'super', 'mega', 'hyper', 'turbo', 'sonic', 'flash', 'velocity', 'impact', 'shatter', 'crush', 'strike', 'edge', 'fury', 'wrath', 'rage', 'venom', 'stinger', 'claw', 'fang', 'blade', 'sword']
EMAIL_DOMAINS = ['gmail.com', 'yahoo.com', 'outlook.com', 'fpt.edu.vn', 'vnn.vn']

def generate_random_email(full_name, username):
    """Tạo email dựa trên tên và username, không dùng Faker"""
    name_no_accent = remove_accents(full_name).replace(" ", "")
    
    # Random mode để đa dạng hóa
    mode = random.randint(1, 4)
    
    if mode == 1:
        # Kiểu nickname (langtu99@...)
        prefix = f"{random.choice(EMAIL_NICKNAMES)}{random.randint(10, 999)}"
    elif mode == 2:
        # Kiểu dùng chính username (tuan_kiet92@...) - Đây là kiểu phổ biến nhất
        prefix = username
    elif mode == 3:
        # Kiểu viết tắt tên + số ngẫu nhiên (nguyenanhtuan -> natuan88@...)
        prefix = f"{name_no_accent[:random.randint(4, 7)]}{random.randint(10, 999)}"
    else:
        # Kiểu random chuỗi ký tự ngắn
        random_chars = "abcdefghijklmnopqrstuvwxyz"
        prefix = f"{''.join(random.choices(random_chars, k=5))}{random.randint(100, 999)}"
        
    return f"{prefix}@{random.choice(EMAIL_DOMAINS)}"

## # generate sdt
prefixes_phone = ['090', '091', '098', '032', '035', '070', '086']
def generate_random_phone():
    
    return random.choice(prefixes_phone) + str(random.randint(1000000, 9999999))

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
STREET_NAMES = [
        "Lê Lợi", "Nguyễn Huệ", "Lê Duẩn", "Cách Mạng Tháng 8", "Phan Chu Trinh", "Nam Kỳ Khởi Nghĩa", 
        "Đồng Khởi", "Hàm Nghi", "Trần Hưng Đạo", "Nguyễn Trãi", "Lê Lai", "Nguyễn Thị Minh Khai", 
        "Võ Văn Tần", "Trương Định", "Bà Huyện Thanh Quan", "Nguyễn Đình Chiểu", "Lý Tự Trọng", 
        "Hai Bà Trưng", "Phạm Ngũ Lão", "Bùi Viện", "Đề Thám", "Cô Giang", "Cô Bắc", "Nguyễn Thái Học", 
        "Trần Phú", "Lý Thường Kiệt", "Trần Cao Vân", "Mạc Đĩnh Chi", "Phan Kế Bính", "Nguyễn Bỉnh Khiêm", 
        "Điện Biên Phủ", "Võ Thị Sáu", "Tú Xương", "Đinh Tiên Hoàng", "Nguyễn Du", "Lê Thánh Tôn", 
        "Lý Thái Tổ", "Trần Quang Khải", "Nguyễn Hữu Cảnh", "Kim Mã", "Giải Phóng", "Đại Cồ Việt", 
        "Xã Đàn", "Khâm Thiên", "Đội Cấn", "Liễu Giai", "Cầu Giấy", "Xuân Thủy", "Láng Hạ", "Thái Hà", 
        "Chùa Bộc", "Phạm Ngọc Thạch", "Tôn Đức Thắng", "Hùng Vương", "Hoàng Văn Thụ", "Cộng Hòa", 
        "Phan Đăng Lưu", "Bạch Đằng", "Phan Xích Long", "Lê Quang Định", "Nơ Trang Long", "Kha Vạn Cân", 
        "Độc Lập", "Thống Nhất", "Tân Kỳ Tân Quý", "Âu Cơ", "Lạc Long Quân", "Lý Thái Tổ", "Nguyễn Tất Thành", 
        "Lê Hồng Phong", "Trần Bình Trọng", "Võ Văn Kiệt", "Kinh Dương Vương", "An Dương Vương", "Hùng Vương", 
        "Đường số 1", "Đường số 2", "Đường số 5", "Đường số 7", "Đường số 10", "Phan Huy Ích", "Quang Trung", 
        "Nguyễn Oanh", "Nguyễn Kiệm", "Phạm Văn Đồng", "Tô Ngọc Vân", "Hà Huy Giáp", "Vườn Lài", 
        "Trần Não", "Lương Định Của", "Song Hành", "Nguyễn Duy Trinh", "Nguyễn Xiển", "Đỗ Xuân Hợp", 
        "Huỳnh Tấn Phát", "Nguyễn Văn Linh", "Phạm Hùng", "Nguyễn Văn Cừ", "Trần Xuân Soạn"
    ]
def generate_address_by_province(province_name):
    return f"{random.randint(1, 1000)} {random.choice(STREET_NAMES)}, {province_name}"


## Hàm hỗ trợ generate full name theo giới tính
### gen last name theo tỉ lệ thực tế, có xử lý nhóm "Khác" để tăng tính đa dạng
surnames = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Võ", "Đặng", 
    "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Khác"
]

weights = [
    0.384, 0.121, 0.095, 0.070, 0.051, 0.045, 0.020, 0.019, 0.021, 
    0.014, 0.013, 0.013, 0.010, 0.005, 0.005, 0.114
]
def get_random_last_name():
    # k=1 nghĩa là bốc 1 cái, kết quả trả về là 1 list nên cần lấy phần tử [0]
    last_name = random.choices(surnames, weights=weights, k=1)[0]
    
    # Xử lý trường hợp rơi vào nhóm "Khác" (11.4%)
    if last_name == "Khác":
        rare_surnames = ["Âu", "Mạc", "Biện", "Doãn", "Khổng", "Quách", "Tiêu", "Trịnh", "Tạ", "Mai"]
        return random.choice(rare_surnames)
        
    return last_name

### gen middle name theo giới tính, có nhóm chung và nhóm riêng cho nam/nữ
MIDDLE_NAMES_MALE = [
        # Nhóm Kinh điển & Phổ biến (Dành cho F2P, Minnow - chiếm tỷ lệ cao)
        "Văn", "Hữu", "Đình", "Đức", "Minh", "Anh", "Quang", "Thành", "Trọng", "Quốc", 
        
        # Nhóm Mạnh mẽ & Khí phách (Hợp cho các chiến thần, top server)
        "Uy", "Mạnh", "Tiến", "Hoàng", "Hùng", "Chấn", "Sỹ", "Thế", "Vương", "Bá",
        
        # Nhóm Hán Việt Sang trọng (Hợp cho Tiên hiệp/Kiếm hiệp)
        "Thiên", "Trường", "Vân", "Nhật", "Thanh", "Khánh", "Phúc", "Khôi", "Tùng", "Hải",
        
        # Nhóm Hiện đại & Độc đáo
        "Gia", "Bảo", "Khải", "Kiến", "Duy", "Lâm", "Sơn", "Việt", "Nam", "Phú",
        
        # Nhóm Tên đệm 1 chữ (Gọn gàng, hiện đại)
        "Tử", "Mạc", "Vĩnh", "Thái", "Phi", "Đăng", "Tường", "Thịnh", "Kiên", "Vũ"
    ]
MIDDLE_NAMES_FEMALE = [
    "Thị", "Ngọc", "Thảo", "Quỳnh", "Hương", "Tuyết", "Minh", "Thu", "Hồng", "Mai",
    "Bảo", "Diệu", "Phương", "Bích", "Ánh", "Trúc", "Kim", "Hải", "Như", "Cát",
    "Thanh", "Mỹ", "Kiều", "Hoàng", "Diễm", "Tâm", "Tố", "Thục", "Nhã", "Linh",
    "Đan", "Băng", "Trâm", "Diệp", "Hà", "Yến", "An", "Khánh", "Gia", "Tường",
    "Thiên", "Vy", "Nguyệt", "Uyên", "Thúy", "Lệ", "Vân", "Mộc", "Thùy", "Khê"
    ]
def get_random_middle_name(gender):
    if gender == "Male":
        return random.choice(MIDDLE_NAMES_MALE)
    else:
        return random.choice(MIDDLE_NAMES_FEMALE)

### gen first name theo giới tính, có nhóm chung và nhóm riêng cho nam/nữ, có xử lý tên ngắn 1-2 chữ để tăng tính đa dạng
MALE_NAMES = [
        # Vần A-B-C
        "An", "Anh", "Ân", "Ẩn", "Bắc", "Bạch", "Bảo", "Bằng", "Bình", "Bửu", "Biên", "Cảnh", "Cường", "Công", "Chính", "Chương", "Chấn", "Chiến",
        # Vần D-Đ
        "Danh", "Dân", "Duy", "Dương", "Dũng", "Đạo", "Đạt", "Điền", "Đăng", "Đại", "Đoàn", "Đình", "Đông", "Đức", "Định",
        # Vần G-H
        "Gia", "Giàu", "Giáp", "Hà", "Hải", "Hảo", "Hào", "Hậu", "Hiếu", "Hiền", "Hiệp", "Hùng", "Huy", "Huyền", "Huỳnh", "Hưng", "Hạnh", "Hoàng", "Hữu", "Hội",
        # Vần K-L
        "Kha", "Khang", "Khánh", "Khoa", "Khôi", "Khương", "Khải", "Khiêm", "Kiên", "Kiệt", "Kiều", "Kỳ", "Lam", "Lâm", "Lân", "Lập", "Lộc", "Lợi", "Long", "Luân", "Lương", "Lĩnh",
        # Vần M-N
        "Mạnh", "Mẫn", "Minh", "Nam", "Nghĩa", "Nghị", "Nguyên", "Nhân", "Nhật", "Ninh", "Nội",
        # Vần P-Q
        "Phi", "Phong", "Phú", "Phúc", "Phước", "Phương", "Pháp", "Phát", "Quân", "Quang", "Quốc", "Quý", "Quyết", "Quyền",
        # Vần S-T
        "Sáng", "Sơn", "Song", "Sỹ", "Tài", "Tân", "Tấn", "Tùng", "Tú", "Tường", "Thạch", "Thái", "Thắng", "Thành", "Thanh", "Thảo", "Thế", "Thiên", "Thiện", "Thiết", "Thịnh", "Thông", "Thụ", "Thuận", "Thực",
        # Vần U-V-X
        "Uy", "Văn", "Vân", "Việt", "Vinh", "Vĩnh", "Vũ", "Vương", "Vượng", "Xuân"
    ]
FEMALE_NAMES = [
        # Vần A-B-C
        "An", "Anh", "Ái", "Ân", "Bích", "Bình", "Băng", "Bảo", "Cát", "Cầm", "Chi", "Châu", "Cúc",
        # Vần D-Đ
        "Diệp", "Diễm", "Dung", "Dương", "Duyên", "Đan", "Đào", "Đoan", "Đài",
        # Vần G-H
        "Giang", "Giao", "Hà", "Hạ", "Hải", "Hân", "Hằng", "Hậu", "Hiền", "Hoa", "Hoà", "Hoài", "Hương", "Hường", "Huyền", "Hạnh",
        # Vần K-L
        "Kha", "Khánh", "Khuê", "Kiều", "Kim", "Lam", "Lan", "Linh", "Liên", "Liễu", "Loan", "Lộc", "Ly", "Lệ",
        # Vần M-N
        "Mai", "Mi", "Minh", "Mỹ", "Nga", "Ngân", "Nghi", "Ngọc", "Nguyệt", "Nhi", "Nhung", "Nương", "Nương", "Nữ",
        # Vần O-P-Q
        "Oanh", "Phượng", "Phương", "Phụng", "Quế", "Quỳnh", "Quyên",
        # Vần S-T
        "Sa", "San", "Sương", "Thanh", "Thảo", "Thoa", "Thu", "Thuần", "Thủy", "Thúy", "Thùy", "Thơ", "Tiên", "Trâm", "Trang", "Trinh", "Trúc", "Tú", "Tuyết", "Tuyền",
        # Vần U-V-X
        "Uyên", "Uyển", "Vân", "Vi", "Vy", "Việt", "Xuân", "Yến"
    ]

def get_random_first_name(gender):
    if gender == "Male":
        return random.choice(MALE_NAMES)
    else:        
        return random.choice(FEMALE_NAMES)
    
def generate_full_name(gender):
    # Tách riêng để đưa vào hàm random.choices
    last_name = get_random_last_name()
    first_name = get_random_first_name(gender)
    # tỷ lệ không có tên đệm là 10%, có tên đệm là 90% (để tạo sự đa dạng, cũng như phù hợp với thực tế hơn)
    has_middle_name = random.random() < 0.9
    if has_middle_name:
        middle_name = get_random_middle_name(gender)
        full_name = f"{last_name} {middle_name} {first_name}"
    else:
        middle_name = "" # Để trống để sau này lưu vào DB
        full_name = f"{last_name} {first_name}"

    return full_name

## Hàm hỗ trợ generate job cho người chơi game, có thể điều chỉnh danh sách và trọng số cho phù hợp với thực tế hơn
def generate_user_job():
    JOBS_LIST = [
        "Sinh viên", "Nhân viên văn phòng", "Lập trình viên", "Kế toán", 
        "Kinh doanh tự do", "Tài xế công nghệ", "Công nhân", "Giáo viên", 
        "Kỹ sư", "Nhân viên bán hàng", "Marketing", "Thiết kế đồ họa", 
        "Bác sĩ", "Luật sư", "Đầu bếp", "Dược sĩ", "Kiến trúc sư", 
        "Nội trợ", "Quản lý cửa hàng", "Giao hàng (Shipper)", "Freelancer",
        "Chuyên viên nhân sự", "Kỹ thuật viên", "Giao dịch viên", "Môi giới BĐS"
    ]

    # Nếu muốn gán trọng số cho thực tế hơn:
    JOB_WEIGHTS = [
        20, 15, 8, 5,  # Sinh viên (20%), Văn phòng (15%)...
        10, 8, 7, 4,   # Tự do (10%), Tài xế (8%)...
        3, 5, 4, 2, 
        1, 1, 1, 1, 1, # Các nhóm chuyên gia để 1%
        1, 1, 1, 1,
        0.5, 0.5, 0.5, 0.5 # Các nhóm hiếm để 0.5%
    ]
    job = random.choices(JOBS_LIST, weights=JOB_WEIGHTS, k=1)[0]
    return job

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
        user_id = f"20226{str(random.randint(0, 9999999999)).zfill(10)}"
        if user_id in used_user_ids: continue

        # 2. Tuổi & Ngày sinh
        min_age, max_age = random.choices(groups, weights=weights, k=1)[0]
        birth_date = generate_birth_date(min_age, max_age)
        age = (date.today() - birth_date).days // 365
        # 3. Tên & Username & Email
        gender = generate_gender() # Trả về 'Male' hoặc 'Female'
        full_name = generate_full_name(gender) # Tên đầy đủ có dấu, dùng để tạo username và email
        username = generate_username_style(full_name, birth_date)
        email = generate_random_email(full_name, username)
        
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
            "age": age,
            "gender": gender,
            "age_group": f"{min_age}-{max_age}",
            "phone": phone,
            "email": email,
            "address": address,
            "job": "Sinh viên" if age < 23 else generate_user_job(), # Nhóm tuổi lớn hơn 30 sẽ có job là Sinh viên để phù hợp với thực tế (có thể điều chỉnh logic này nếu muốn)
            "cccd": cccd,
            # "created_at": (datetime.now() - timedelta(days=random.randint(0, numsday_at_create))).strftime("%Y-%m-%d %H:%M:%S")
            "created_at": (datetime.now() - timedelta(days=random.randint(0, numsday_at_create))).strftime("%Y-%m-%d %H:%M:%S")
        })
        
        used_user_ids.add(user_id); used_usernames.add(username); used_emails.add(email); used_phones.add(phone); used_cccds.add(cccd)
    
    return users

## Thực thi tạo user data
number_of_gamer = 120000
print(f"🚀 Đang tạo dữ liệu người chơi game... {number_of_gamer} người chơi")
data = create_final_user_list(number_of_gamer)
print(f"hoàn thành việc tạo dữ liệu người chơi game... {len(data)} bản ghi")
df = pd.DataFrame(data)
df.to_csv('users_game_part2.csv', index=False, encoding='utf-8')    
# with open('users_game_part1.json', 'w', encoding='utf-8') as f:
#     json.dump(data, f, ensure_ascii=False, indent=4)

