import pytest
from datetime import datetime
import pandas as pd
# Import các hàm từ file sinh dữ liệu của bạn
# Giả sử file sinh dữ liệu của bạn tên là data_gen.py
from gen_transaction_gamer import calculate_paid_amount, generate_bills_for_user, vip_thresholds

def test_calculate_paid_amount():
    print("\n>>> Testing calculate_paid_amount function...")
    # Test Banking/Momo >= 500k (giảm 15%)
    assert calculate_paid_amount(1000000, "Banking") == 850000
    print(f"\nBanking/Momo >= 500k test passed!")
    # Test Banking/Momo < 500k (giảm 10%)
    assert calculate_paid_amount(100000, "Momo") == 90000
    print(f"\nBanking/Momo < 500k test passed!")
    # Test In-app (giữ nguyên)
    assert calculate_paid_amount(500000, "In-app") == 500000
    print(f"\nIn-app test passed!")

def test_vip_threshold_logic():
    print("\n>>> Testing VIP threshold logic...")
    # Giả lập 1 user VIP 3
    uid = 12345
    vip_level = 3
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 2, 1)
    
    bills = generate_bills_for_user(uid, "Game Test", "Hero1", "S1", vip_level, start_date, end_date)
    
    # Tính tổng tiền gốc (original_amount) để check mốc VIP
    total_original = sum(b['original_amount'] for b in bills)
    
    # Tổng nạp phải >= ngưỡng VIP 3 (150,000)
    assert total_original >= vip_thresholds[vip_level]
    print(f"\nTotal original amount: {total_original} - meets VIP {vip_level} threshold!")
    # Và phải < ngưỡng VIP 4 (500,000)
    assert total_original < vip_thresholds[vip_level + 1]
    print(f"\nTotal original amount: {total_original} - below VIP {vip_level + 1} threshold!")

def test_unique_bill_constraints():
    print("\n>>> Testing unique bill constraints...")
    uid = 999
    vip_level = 5
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 1, 10)
    
    bills = generate_bills_for_user(uid, "Game Test", "Hero1", "S1", vip_level, start_date, end_date)
    
    # 1. Kiểm tra trùng ID hóa đơn
    bill_ids = [b['bill_id'] for b in bills]
    assert len(bill_ids) == len(set(bill_ids)), "Phát hiện trùng lặp bill_id!"
    print(f"\nUnique bill IDs: {len(bill_ids)}")

    # 2. Kiểm tra trùng thời gian nạp (created_at) cho cùng 1 user
    timestamps = [b['created_at'] for b in bills]
    assert len(timestamps) == len(set(timestamps)), "Phát hiện trùng lặp thời gian nạp (created_at)!"
    print(f"\nUnique timestamps: {len(timestamps)}")

def test_boom_phase_logic():
    # Test xem VIP cao có nạp nhiều gói to ở giai đoạn đầu không
    uid = 888
    vip_level = 12 # VIP rất cao
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 3, 1)
    
    bills = generate_bills_for_user(uid, "Game Test", "Whale", "S1", vip_level, start_date, end_date)
    
    # Kiểm tra xem có gói "Đua Top" (>= 1,000,000) nào được sử dụng không
    big_packets = [b for b in bills if b['original_amount'] >= 1000000]
    assert len(big_packets) > 0, "VIP cao nhưng không thấy nạp các gói lớn!"

def test_event_cycle_constraint():
    # Test gói tháng không được nạp quá gần nhau
    uid = 777
    vip_level = 2
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 4, 1) # 3 tháng
    
    bills = generate_bills_for_user(uid, "Game Test", "User", "S1", vip_level, start_date, end_date)
    
    # Lọc các gói 1.2M (thuộc event_monthly)
    monthly_bills = [b for b in bills if b['original_amount'] == 1200000]
    
    if len(monthly_bills) > 1:
        # Sắp xếp theo thời gian
        monthly_bills.sort(key=lambda x: x['created_at'])
        ts1 = datetime.strptime(monthly_bills[0]['created_at'], '%Y-%m-%d %H:%M:%S')
        ts2 = datetime.strptime(monthly_bills[1]['created_at'], '%Y-%m-%d %H:%M:%S')
        
        # Khoảng cách phải ít nhất 30 ngày (theo logic của bạn)
        assert (ts2 - ts1).days >= 30