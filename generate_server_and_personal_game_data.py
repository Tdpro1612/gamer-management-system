from datetime import datetime, timedelta
import json
import os
import random
import re
import pandas as pd

GAMES = {
    "Cửu Long Tranh Bá": {"launch": datetime(2024, 5, 1)},
    "Hiệp Khách Vô Song": {"launch": datetime(2024, 10, 1)},
    "Tình Kiếm": {"launch": datetime(2025, 3, 1)},
    "Thanh Vân Kiếm": {"launch": datetime(2025, 8, 1)},
    "Tiên Kiếm Kỳ Hiệp": {"launch": datetime(2025, 11, 1)},
}
game_names_list = list(GAMES.keys())
sorted_game_names = sorted(game_names_list, key=lambda x: GAMES[x]["launch"])

current_date = datetime.now()

PERSONA_CONFIG = {
    "WHALE":   {"weight": 0.05,   "vip_range": (10, 15), "jump_prob": 0},
    "DOLPHIN": {"weight": 0.1,  "vip_range": (5, 9),   "jump_prob": 0.001},
    "MINNOW":  {"weight": 5,  "vip_range": (1, 4),   "jump_prob": 0.01},
    "F2P":     {"weight": 90,  "vip_range": (0, 0),   "jump_prob": 0.001},
    "HOPPER":  {"weight": 2,  "vip_range": (3, 8),   "jump_prob": 0.55} 
}

PERSONA_KEYS = list(PERSONA_CONFIG.keys())
PERSONA_WEIGHTS = [v["weight"] for v in PERSONA_CONFIG.values()]

def assign_persona_with_job(job, sid_num):
    high_income_jobs = ["Giám đốc", "Bác sĩ", "Kinh doanh tự do", "Lập trình viên", 
                        "Chuyên viên nhân sự", "Kỹ thuật viên", "Luật sư", "Kỹ sư"]
    
    # Tất cả các pool nên có đầy đủ các loại Persona
    persona_pool = ["WHALE", "DOLPHIN", "MINNOW", "F2P", "HOPPER"]

    if job in high_income_jobs:
        # Nhóm thu nhập cao: Vẫn có F2P nhưng tỷ lệ Whale/Dolphin nhỉnh hơn chút
        # Tỷ lệ nạp tiền khoảng 15-20%
        weights = [2, 8, 10, 75, 5] 
    else:
        # Nhóm phổ thông: F2P chiếm tuyệt đối
        # Tỷ lệ nạp tiền khoảng 3-5%
        weights = [0.1, 0.9, 4, 90, 5]
        
    # Điều chỉnh thêm theo Server (Ưu tiên Whale ở các server đầu nhưng không quá lố)
    if sid_num <= 10:
        # Tăng nhẹ tỷ lệ nạp ở server đầu (tầm 25-30% nạp là cao rồi)
        if job in high_income_jobs:
            weights = [5, 10, 15, 65, 5]
        else:
            weights = [0.5, 2, 8, 80, 9.5]
        
    return random.choices(persona_pool, weights=weights, k=1)[0]

def generate_ultimate_ingame_name(user_info):
    username = user_info.get('username', 'User')
    email_prefix = user_info.get('email', 'email').split('@')[0]
    birth_date = user_info.get('birthday', '1990-01-01')
    year_short = birth_date[:4][-2:]
    day_month = birth_date[5:7] + birth_date[8:10]

    # Trích xuất phần chữ, nếu rỗng thì lấy 3 ký tự đầu username
    base_name = re.sub(r'\d+', '', username).strip('_').strip('.')
    if len(base_name) < 3:
        base_name = re.sub(r'\d+', '', email_prefix).strip('_').strip('.')
    if not base_name: 
        base_name = username[:3]

    base_name = base_name.capitalize()[:8] # Giới hạn base để dành chỗ cho hậu tố

    styles = ["Classic_KiemHiep", "Modern", "Personal", "Hardcore"]
    chosen_style = random.choice(styles)

    if chosen_style == "Classic_KiemHiep":
        prefixes = ["ĐộcCô", "Lăng", "MộDung", "Tuyết", "Thanh", "Vân", "Minh", "Kiếm", "Hàn", "Phượng", "Long", "Tiêu", "Diệp", "Sở", "ÂuDương", "TưMã"]
        name = f"{random.choice(prefixes)}{base_name}"
    
    elif chosen_style == "Modern":
        mods = ["Shadow", "Dark", "Ace", "Legend", "Solo", "King", "Pro", "Neo", "God", "Z", "X", "Alpha"]
        sep = random.choice(["_", ".", ""])
        name = f"{random.choice(mods)}{sep}{base_name}"
    
    elif chosen_style == "Hardcore":
        # Style này cực khó trùng: Thêm ký tự đặc biệt bao quanh
        brackets = [("[", "]"), ("x", "x"), ("-", "-"), ("_", "_")]
        b = random.choice(brackets)
        name = f"{b[0]}{base_name}{b[1]}"

    else:
        # Style cá nhân kèm số ngẫu nhiên để chống trùng ngay từ đầu
        suffix = random.choice([year_short, day_month, str(random.randint(100, 999))])
        name = f"{base_name}{suffix}"

    # QUAN TRỌNG: Giới hạn 24 ký tự (cho đủ độ dài) 
    return name[:24]

def get_vip(persona):
    v_min, v_max = PERSONA_CONFIG[persona]["vip_range"]
    if v_min == v_max:
        return v_min
    
    # Tạo danh sách các mức VIP
    vips = list(range(v_min, v_max + 1))
    
    # Trọng số: VIP càng cao, trọng số càng giảm theo cấp số nhân (1/2, 1/4, 1/8...)
    weights = [1 / (2**i) for i in range(len(vips))]
    
    # Chọn dựa trên trọng số
    return random.choices(vips, weights=weights, k=1)[0]


print("\n>>> Đọc dữ liệu user info và dữ liệu game_data chưa có server và personal!")
# Đọc dữ liệu user info data
with open("data/user_info.json", "r", encoding="utf-8") as file:
    user_info = json.load(file)
# Đọc dữ liệu game data
with open("data/game_database.json", "r", encoding="utf-8") as file:
    game_data = json.load(file)
print("\n>>> Hoàn thành việc đọc dữ liệu user info và dữ liệu game_data chưa có server và personal!")
# Tạo DataFrame để lưu kết quả
results = []
all_game_user_records = []
print("\n>>> Bắt đầu tổng hợp dữ liệu game và user info để chuẩn bị cho bước gán Server Open Date và Join Date!")
for game_name in sorted_game_names:
    user_id_list = game_data.get(game_name, [])
    launch_date = GAMES[game_name].get("launch") 
    
    for user_id in user_id_list:
        info = user_info.get(str(user_id), {})
        if info:
            all_game_user_records.append({
                "user_id": user_id,
                "game_name": game_name,
                "job": info.get("job", "Unknown"),
                "launch_date": launch_date,
                "created_at": info.get("created_at")
            })

# Tạo DataFrame tổng
df_all = pd.DataFrame(all_game_user_records)

# Chuyển đổi kiểu dữ liệu datetime để tính toán chính xác
df_all['created_at'] = pd.to_datetime(df_all['created_at'])
df_all['launch_date'] = pd.to_datetime(df_all['launch_date'])
print("\n>>> Hoàn thành tổng hợp dữ liệu game và user info để chuẩn bị cho bước gán Server Open Date và Join Date!")

# Cấu hình 
FULL_NUMBER = 1000  
LEAK_RATE = 0.03    
REFILL_SIZE = 2000  

# Dictionary để lưu ngày mở của từng Server ID (phục vụ cho logic rò rỉ)
print("\n>>> Bắt đầu thêm Server Open Date và Join Date!")
for game_name, group_df in df_all.groupby('game_name'):
    print(f"\n>>> Đang xử lý Game: {game_name}")
    
    current_sid = 1
    group_df = group_df.sort_values("created_at")
    launch_date = pd.to_datetime(GAMES[game_name].get("launch"))
    
    current_server_open_date = launch_date
    
    df_early_birds = group_df[group_df["created_at"] <= launch_date].copy()
    df_after_launch = group_df[group_df["created_at"] > launch_date].copy()
    
    active_buffer = df_early_birds.copy()
    pointer = 0
    opened_sids = []
    game_results = []
    server_open_registry = {}

    while pointer < len(df_after_launch) or len(active_buffer) > 0:
        
        # Bước A: Nạp thêm người vào Buffer
        if len(active_buffer) < FULL_NUMBER and pointer < len(df_after_launch):
            next_chunk = df_after_launch.iloc[pointer : pointer + REFILL_SIZE]
            active_buffer = pd.concat([active_buffer, next_chunk])
            pointer += REFILL_SIZE
            active_buffer = active_buffer.sample(frac=1).reset_index(drop=True)

        if len(active_buffer) == 0:
            break

        current_sid_name = f"S{current_sid}"
        leak_df = pd.DataFrame()
        
        # Bước B: Xử lý rò rỉ 3% (Vào các server cũ)
        if len(opened_sids) > 0:
            num_leak = int(len(active_buffer) * LEAK_RATE)
            if num_leak > 0:
                leak_df = active_buffer.iloc[:num_leak].copy()
                leak_df['server_id'] = [random.choice(opened_sids) for _ in range(len(leak_df))]
                
                # Gán ngày mở server cũ từ registry
                leak_df['server_open_date'] = leak_df['server_id'].map(server_open_registry)
                
                # Ngày join của khách vãng lai chính là ngày họ tạo acc
                leak_df['join_date'] = leak_df['created_at']
                leak_df['persona'] = leak_df.apply(
                        lambda row: assign_persona_with_job(row['job'], current_sid), 
                        axis=1
                    )
                leak_df['vip_level'] = leak_df['persona'].apply(get_vip)
                active_buffer = active_buffer.iloc[num_leak:].reset_index(drop=True)

        # Bước C: Bổ đủ người cho Server hiện tại (Mới mở)
        take_count = min(len(active_buffer), FULL_NUMBER)
        server_df = active_buffer.iloc[:take_count].copy()
        
        # Tính ngày mở server mới
        batch_max_date = server_df['created_at'].max()
        current_server_open_date = max(current_server_open_date, batch_max_date)
        
        server_df['server_id'] = current_sid_name
        server_df['server_open_date'] = current_server_open_date
        server_df['persona'] = server_df.apply(
                        lambda row: assign_persona_with_job(row['job'], current_sid), 
                        axis=1
                    )
        server_df['vip_level'] = server_df['persona'].apply(get_vip)
        # Với server mới mở, ngày Join thường là ngày Server Open 
        # (hoặc lấy max của created_at và server_open_date để chính xác tuyệt đối)
        server_df['join_date'] = server_df[['created_at', 'server_open_date']].max(axis=1)
        
        # Lưu vào registry để các đợt leak sau có data tham chiếu
        server_open_registry[current_sid_name] = current_server_open_date
        
        active_buffer = active_buffer.iloc[take_count:].reset_index(drop=True)

        # Bước D: Hợp nhất và xuất file
        final_batch = pd.concat([server_df, leak_df]) if not leak_df.empty else server_df
        game_results.append(final_batch)
        
        opened_sids.append(current_sid_name)
        current_sid += 1

        if len(game_results) > 50:
            pd.concat(game_results).to_csv("data/game_data_full.csv", mode='a', index=False, 
                                          header=not os.path.exists("data/game_data_full.csv"))
            game_results = []

    if game_results:
        pd.concat(game_results).to_csv("data/game_data_full.csv", mode='a', index=False, 
                                      header=not os.path.exists("data/game_data_full.csv"))
    registry_df = pd.DataFrame(list(server_open_registry.items()), columns=['server_id', 'server_open_date'])
    registry_df['game_name'] = game_name
    registry_df.to_csv("data/server_master_registry.csv", mode='a', index=False, 
                    header=not os.path.exists("data/server_master_registry.csv"))

    # Reset registry cho game tiếp theo
    server_open_registry = {}

print("\n>>> Hoàn thành với đầy đủ Server Open Date và Join Date!")


# Đọc dữ liệu gốc và master registry
df_main = pd.read_csv("data/game_data_full.csv")
df_registry = pd.read_csv("data/server_master_registry.csv")
registry_dict = {
    (row.game_name, row.server_id): pd.to_datetime(row.server_open_date).date() 
    for row in df_registry.itertuples()
}

output_file = "data/game_data_final.csv"
# Xóa file cũ nếu tồn tại để bắt đầu ghi mới
if os.path.exists(output_file):
    os.remove(output_file)
print("\n>>> Bắt đầu đọc dữ liệu server và data game để gán Persona và xử lý bản ghi nhảy server!")
# ghi vào dữ liệu gốc
df_main.to_csv(output_file, index=False)
print("\n>>> Hoàn thành đọc dữ liệu gốc ")

new_batch = []
chunk_size = 50000  # Cứ 50k bản ghi mới thì ghi xuống file một lần
user_count = 0
total_users = len(df_main)
total_new_records = 0
current_date_limit = datetime.now().date()


for row in df_main.itertuples(index=False):
    user_count += 1
    
    if user_count % 10000 == 0:
        print(f">>> Đã quét: {user_count}/{total_users} users | Tổng bản ghi nhảy đã tạo: {total_new_records}")

    curr_persona = row.persona
    curr_sid_num = int(row.server_id.replace('S', ''))
    curr_join_date = pd.to_datetime(row.join_date).date()
    curr_vip = row.vip_level

    while True:
        config = PERSONA_CONFIG[curr_persona]
        if random.random() > config["jump_prob"]:
            break
            
        jump_distance = random.randint(1, 15)
        target_sid = f"S{curr_sid_num + jump_distance}"
        
        target_key = (row.game_name, target_sid)
        if target_key not in registry_dict:
            break 
            
        open_date = registry_dict[target_key]
        new_join_date = max(curr_join_date + pd.Timedelta(days=2), open_date)
        if isinstance(new_join_date, pd.Timestamp):
            new_join_date = new_join_date.date()

        if new_join_date > current_date_limit:
            break
            
        # Tạo record mới
        new_entry = row._asdict()
        new_entry.update({
            'server_id': target_sid,
            'server_open_date': open_date,
            'join_date': new_join_date,
            'persona': curr_persona,
            'vip_level': curr_vip
        })
        
        if random.random() < 0.15:
            new_persona = assign_persona_with_job(row.job, int(target_sid.replace('S','')))
            new_entry['persona'] = new_persona
            new_entry['vip_level'] = get_vip(new_persona)
            curr_persona = new_persona
            curr_vip = new_entry['vip_level']

        new_batch.append(new_entry)
        total_new_records += 1
        
        # Cập nhật trạng thái cho vòng lặp sau
        curr_sid_num = int(target_sid.replace('S',''))
        curr_join_date = new_join_date

        # KIỂM TRA CHUNK: Nếu batch đủ lớn thì ghi xuống file và giải phóng RAM
        if len(new_batch) >= chunk_size:
            pd.DataFrame(new_batch).to_csv(output_file, mode='a', index=False, header=False)
            new_batch = [] # Giải phóng bộ nhớ ngay lập tức

# Ghi nốt những bản ghi còn sót lại
if new_batch:
    pd.DataFrame(new_batch).to_csv(output_file, mode='a', index=False, header=False)

print(f"\n>>> HOÀN THÀNH! Tổng cộng đã thêm {total_new_records} bản ghi nhảy.")

with open("data/user_info.json", "r", encoding="utf-8") as file:
    user_info = json.load(file)
df = pd.read_csv("data/game_data_final.csv")
print("\n>>> Bắt đầu gán Ultimate In-game Name cho tất cả người chơi!")
ingame_name = []
set_name = set()
idx = 1
for row in df.itertuples(index=False):
    if idx % 10000 == 0:
        print(f">>> Đã gán In-game Name cho {idx}/{len(df)} users")
    idx += 1
    name_ingame = generate_ultimate_ingame_name(user_info.get(str(row.user_id), {}))
    # Đảm bảo không trùng lặp tên ingame
    while name_ingame in set_name:
        name_ingame = name_ingame[:10] + str(random.randint(0, 999999999999))   # Thêm số ngẫu nhiên vào cuối để tránh trùng lặp
    set_name.add(name_ingame)
    ingame_name.append(name_ingame)
df['ingame_name'] = ingame_name
print(f">>> Kiểm tra phân bổ vip level: {df['vip_level'].value_counts()} bản ghi.")
df.to_csv("data/game_data_final.csv", index=False)
print("\n>>> Hoàn thành gán Ultimate In-game Name cho tất cả người chơi!")

# reformat datetime
df['join_date'] = pd.to_datetime(df['join_date'], format="mixed")
df['server_open_date'] = pd.to_datetime(df['server_open_date'], format="mixed")
df['created_at'] = pd.to_datetime(df['created_at'], format="mixed")
df['join_date'] = df['join_date'].dt.strftime('%Y-%m-%d')
df['server_open_date'] = df['server_open_date'].dt.strftime('%Y-%m-%d')
df['created_at'] = df['created_at'].dt.strftime('%Y-%m-%d')
df.to_csv("data/game_data_final.csv", index=False)