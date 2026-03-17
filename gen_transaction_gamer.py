import uuid
import random
import pandas as pd
from datetime import datetime, timedelta

# Cấu hình mệnh giá và kênh nạp
import pandas as pd
import random
import numpy as np
from datetime import datetime, timedelta

# mốc nạp đạt vip level, dựa trên tổng nạp (VIP Points)
vip_thresholds = {
    1: 20000, 2: 50000, 3: 150000, 4: 500000, 5: 1500000,
    6: 4500000, 7: 12000000, 8: 35000000, 9: 100000000, 10: 300000000,
    11: 700000000, 12: 1000000000, 13: 3000000000, 14: 7000000000, 15: 10000000000
}
# Gói nạp cơ bản
base_pkgs = [5000000, 2000000, 1000000, 500000, 200000, 100000, 50000, 20000, 10000]
# Gói event
event_7days = [19200000, 9600000, 4800000, 2400000, 1200000, 600000, 300000]
event_monthly = [1200000, 900000, 600000, 300000]
event_nap_dau = [10000000, 5000000, 2000000, 1000000, 500000, 200000, 100000]

event_duatop = [50000000, 30000000, 20000000, 10000000, 5000000, 2000000, 1000000]

CHANNELS = ["Banking", "Momo", "In-app"]

def calculate_paid_amount(original_amount, channel):
    """Tính số tiền thực tế user phải trả sau chiết khấu"""
    if channel == "In-app":
        return original_amount # In-app thường không chiết khấu
    
    # Logic chiết khấu theo yêu cầu của bạn
    discount = 0.15 if original_amount >= 500000 else 0.1
    return int(original_amount * (1 - discount))

def get_random_time_in_day(base_date):
    """
    Phân bổ giờ nạp theo tỷ lệ: Tối (40%), Trưa (20%), Sáng (15%), Chiều (15%), Đêm (10%)
    """
    rand = random.random()
    if rand < 0.40: # Tối 20h-23h
        hour = random.randint(20, 22)
    elif rand < 0.60: # Trưa 11h-13h
        hour = random.randint(11, 13)
    elif rand < 0.75: # Sáng 08h-10h
        hour = random.randint(8, 10)
    elif rand < 0.90: # Chiều 17h-19h
        hour = random.randint(17, 19)
    else: # Đêm 00h-02h
        hour = random.randint(0, 2)
        
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    # Kết hợp với ngày join server
    return datetime.combine(base_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute, seconds=second)

def create_bill_dict(uid, g_name, ingame_name, server_id, vip_level, pkg, bill_ts, count):
    """Hàm tạo bản ghi Bill để code chính gọn gàng hơn"""
    return {
        'bill_id': f"B{uid}{int(bill_ts.timestamp())}{count}",
        'user_id': uid,
        'vip_level': vip_level,
        'ingame_name': ingame_name,
        'game_name': g_name,
        'server_id': server_id,
        'original_amount': pkg,
        'paid_amount': calculate_paid_amount(pkg, random.choice(CHANNELS)),
        'channel': random.choice(CHANNELS),
        'created_at': bill_ts.strftime('%Y-%m-%d %H:%M:%S')
    }

def generate_bills_for_user(uid, g_name, ingame_name, server_id, vip_level, start_date, end_date):
    user_bills = []
    days_diff = max(0, (end_date - start_date).days)
    
    # Xác định Target Money
    min_money = vip_thresholds.get(vip_level, 0)
    max_money = vip_thresholds.get(vip_level + 1) - 10000 if vip_level < 15 else min_money * 1.1
    target_money = round(random.randint(min_money, int(max_money)) / 10000) * 10000

    current_money = 0
    bill_timestamps_set = set() # Bộ nhớ tạm để kiểm tra trùng cho User này
    
    available_nap_dau = set(event_nap_dau)
    history_monthly = {}
    history_7days = {}

    # --- HÀM KIỂM TRA TRÙNG LẶP NỘI BỘ ---
    def get_final_unique_ts(target_date):
        # Gọi hàm của bạn để lấy giờ phút giây theo tỷ lệ
        ts = get_random_time_in_day(target_date)
        
        # Nếu trùng (xác suất thấp nhưng vẫn có), cộng thêm 1 giây đến khi hết trùng
        while ts.strftime('%Y-%m-%d %H:%M:%S') in bill_timestamps_set:
            ts += timedelta(seconds=1)
            
        bill_timestamps_set.add(ts.strftime('%Y-%m-%d %H:%M:%S'))
        return ts

    # --- GIAI ĐOẠN 1: 3 NGÀY ĐẦU (BOOM) ---
    boom_days = min(3, days_diff)
    
    # 1.1. Ưu tiên nạp sạch Gói Nạp Đầu
    for pkg in sorted(list(available_nap_dau), reverse=True):
        if current_money + pkg <= target_money:
            unique_ts = get_final_unique_ts(start_date + timedelta(days=random.randint(0, boom_days)))
            user_bills.append(create_bill_dict(uid, g_name, ingame_name, server_id, vip_level, pkg, unique_ts, len(user_bills)))
            current_money += pkg
            available_nap_dau.remove(pkg)

    # 1.2. Đua Top sớm (Chỉ VIP cao - Nạp xả 60% target ngay lúc đầu bằng gói to)
    if vip_level >= 10:
        boom_target = target_money * 0.6 
        while current_money < boom_target:
            # Ưu tiên bốc gói Đua Top to nhất có thể
            affordable = [p for p in event_duatop if current_money + p <= target_money]
            if not affordable: break
            pkg = random.choice(affordable[:2]) # Lấy 1 trong 2 gói to nhất
            unique_ts = get_final_unique_ts(start_date + timedelta(days=random.randint(0, boom_days)))
            user_bills.append(create_bill_dict(uid, g_name, ingame_name, server_id, vip_level, pkg, unique_ts, len(user_bills)))
            current_money += pkg

    # --- GIAI ĐOẠN 2: DUY TRÌ (Chu kỳ Tuần & Tháng) ---
    for d in range(days_diff + 1):
        if current_money >= target_money: break
        curr_date = start_date + timedelta(days=d)

        for p in event_monthly:
            if current_money + p <= target_money:
                if p not in history_monthly or (curr_date - history_monthly[p]).days >= 30:
                    unique_ts = get_final_unique_ts(curr_date)
                    user_bills.append(create_bill_dict(uid, g_name, ingame_name, server_id, vip_level, p, unique_ts, len(user_bills)))
                    current_money += p
                    history_monthly[p] = curr_date

        for p in event_7days:
            if current_money + p <= target_money:
                if p not in history_7days or (curr_date - history_7days[p]).days >= 7:
                    unique_ts = get_final_unique_ts(curr_date)
                    user_bills.append(create_bill_dict(uid, g_name, ingame_name, server_id, vip_level, p, unique_ts, len(user_bills)))
                    current_money += p
                    history_7days[p] = curr_date

    # --- GIAI ĐOẠN 3: LẤP ĐẦY (Ưu tiên gói to cho VIP cao) ---
    while current_money < target_money:
        remaining = target_money - current_money
        selected_pkg = None

        # Nếu là VIP cao, tiếp tục vét gói Đua Top thay vì gói Base
        if vip_level >= 10:
            affordable_dua_top = [p for p in event_duatop if p <= remaining]
            if affordable_dua_top:
                selected_pkg = random.choice(affordable_dua_top[:2])

        # Nếu không có gói Đua Top nào vừa, hoặc không phải VIP cao
        if not selected_pkg:
            possible_base = [p for p in base_pkgs if p <= remaining]
            selected_pkg = random.choice(possible_base) if possible_base else remaining
        
        # Random ngày nạp bù rải rác trong suốt quá trình chơi
        unique_ts = get_final_unique_ts(start_date + timedelta(days=random.randint(0, days_diff)))
        user_bills.append(create_bill_dict(uid, g_name, ingame_name, server_id, vip_level, selected_pkg, unique_ts, len(user_bills)))
        current_money += selected_pkg
        
        if len(user_bills) > 2000: break # Giới hạn bill để data không bị rác

    return user_bills

record_bill = []
batch_size = 10000

df = pd.read_csv("data/game_data_final.csv")
print(f">>> Đã tải dữ liệu gốc với {df['vip_level'].value_counts()} bản ghi.")
print(f">>> Tìm thấy {len(df)} users ...")
output_file = "data/transaction_gamer.csv"


# print(">>> Đang phân cụm User...")
df_reccheck_vip = df[df['vip_level'] > 0]
print(f">>> Đã lọc được {len(df_reccheck_vip)} users có VIP level > 0. Bắt đầu phân cụm...")
df_sorted = df_reccheck_vip.sort_values(['user_id', 'join_date'])
user_groups = dict(list(df_sorted.groupby('user_id')))
all_uids = list(user_groups.keys())

print(f">>> Tìm thấy {len(all_uids)} users duy nhất. Bắt đầu sinh Bill...")
idx = 0
for uid in all_uids:
    idx += 1
    user_df = user_groups.get(uid)
    user_bills = []
    for g_name, game_group in user_df.groupby('game_name'):
        records = game_group.to_dict('records')
        num_records = len(records)
        
        for i in range(num_records):
            row = records[i]
            vip_level = row['vip_level']
            
            if vip_level == 0:
                continue
                
            # Lấy thông tin cơ bản
            ingame_name = row['ingame_name']
            server_id = row['server_id']
            
            # Xử lý ngày tháng
            start_date = pd.to_datetime(row['join_date'])
            
            if i + 1 < num_records:
                # Nếu có server tiếp theo trong cùng game
                end_date = pd.to_datetime(records[i+1]['join_date'])
            else:
                # Nếu là server cuối cùng của game đó
                end_date = datetime.now()
            
            # Sinh bill và thêm vào danh sách
            bill_total = generate_bills_for_user(uid, g_name, ingame_name, server_id, vip_level, start_date, end_date)
            user_bills.extend(bill_total)
    record_bill.extend(user_bills)
    if (idx) % batch_size == 0 or (idx) == len(all_uids):
        if record_bill:
            # Chuyển list các dict thành DataFrame
            print(f">>> Số lượng bill là {len(record_bill)}")
            df_batch = pd.DataFrame(record_bill)
            # Ghi nối (append) vào file đã tạo
            df_batch.to_csv(output_file, mode='a', index=False, header=False)
            
            # Xóa list tạm để giải phóng bộ nhớ
            record_bill = []
            print(f">>> Đã ghi xong {idx}/{len(all_uids)} users...")
            

print(f">>> Hoàn tất! Dữ liệu đã được lưu tại {output_file}")

df = pd.read_csv("data/transaction_gamer.csv")
df.columns = ['bill_id', 'user_id', 'vip_level', 'ingame_name', 'game_name', 'server_id', 'original_amount', 'paid_amount', 'channel', 'created_at']
df.to_csv("data/transaction_gamer.csv", index=False)
# Xem nhanh dữ liệu và thông tin bộ nhớ
print(">>> Cấu trúc dữ liệu:")
print(df.info()) 
print("\n>>> 5 dòng đầu tiên:")
print(df.head())
# Đếm số lượng bill và tổng tiền theo từng Persona
persona_stats = df.groupby('vip_level').agg(
    total_bills=('bill_id', 'count'),          # Đếm số lượng bill
    unique_users=('user_id', 'nunique'),       # Đếm số user duy nhất
    total_revenue=('paid_amount', 'sum')       # Tổng tiền thực thu
).sort_values(by='total_revenue', ascending=False)

# Tính trung bình mỗi người nạp bao nhiêu lần
persona_stats['bills_per_user'] = persona_stats['total_bills'] / persona_stats['unique_users']

print(">>> Thống kê theo Persona:")
print(persona_stats)