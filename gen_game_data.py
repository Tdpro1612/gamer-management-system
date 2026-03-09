from datetime import datetime, timedelta
import json
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
weights_choice_games = []

for game_info in GAMES.values():
    launch_date = game_info["launch"]
    # Tính số tháng hoạt động, tối thiểu là 1
    months_active = (current_date.year - launch_date.year) * 12 + (current_date.month - launch_date.month)
    weights_choice_games.append(max(1, months_active) ** 2)

def assign_game():
    """Hàm thuần túy, chạy nhanh hơn gọi qua Class"""
    return random.choice(list(GAMES.keys()))

# Đọc dữ liệu user info data
with open("user_info.json", "r", encoding="utf-8") as file:
    user_info = json.load(file)

print(f"Đã đọc dữ liệu người dùng, tổng số user: {len(user_info)}. Bắt đầu phân bổ dữ liệu user vào các game...")
game_data = {}
for user in user_info:
    # Bốc số lượng game mà user sẽ chơi, tối đa là 5 game, nhưng không được vượt quá số lượng game hiện có
    nums_games = random.randint(1, 5)
    nums_games = min(nums_games, len(game_names_list))
    
    # Sử dụng tập hợp để tránh trùng lặp khi bốc bằng choices
    selected_games = set()
    while len(selected_games) < nums_games:
        # Bốc 1 game dựa trên trọng số tháng hoạt động
        game = random.choices(game_names_list, weights=weights_choice_games, k=1)[0]
        selected_games.add(game)
    
    # Gán user id vào các game đã chọn
    for game in selected_games:
        if game not in game_data:
            game_data[game] = []
        game_data[game].append(user["user_id"])

# Lưu dữ liệu game vào file JSON
with open("game_database.json", "w", encoding="utf-8") as file:
    json.dump(game_data, file, ensure_ascii=False, indent=4)


for game in game_data:
    print(f"game {game} có số lượng người chơi là {len(game_data[game])} người chơi.")