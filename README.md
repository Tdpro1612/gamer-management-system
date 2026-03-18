# 📜 Tài liệu Tư duy & Logic:

## 📜 Tài liệu Tư duy & Logic (Phần 1) : Hệ thống Giả lập Dữ liệu Người dùng (User Info Generator)
### 1. Tổng quan Tư duy (Philosophical Approach)
Mục tiêu của hệ thống này không chỉ là tạo ra dữ liệu "đầy đủ các cột", mà là tạo ra Dữ liệu có ý nghĩa (Meaningful Data). Tư duy chủ đạo dựa trên 3 trụ cột:

+ Tính thực tế (Realism): Dữ liệu phải phản ánh đúng đặc điểm nhân khẩu học của game thủ Việt Nam (họ, tên đệm, tỉ lệ giới tính, phân bổ vùng miền).

+ Tính nhất quán (Consistency): Các trường thông tin phải có mối liên hệ logic (Ví dụ: Số CCCD phải khớp với giới tính, năm sinh và tỉnh thành).

+ Tính duy nhất (Uniqueness): Đảm bảo không trùng lặp các trường định danh (Email, Phone, CCCD, UserID) để có thể nạp thẳng vào Database làm Khóa chính (Primary Key).

### 2. Logic triển khai chi tiết
#### A. Nhân khẩu học & Tên gọi (Naming Logic)
Hệ thống không sử dụng thư viện Faker thông thường nhằm tránh tạo ra các tên "vô nghĩa". Thay vào đó, nó sử dụng Trọng số thực tế:

+ Họ (Surnames): Áp dụng tỉ lệ phân bổ họ tại Việt Nam (Nguyễn ~38%, Trần ~12%,...). Có cơ chế xử lý nhóm họ hiếm (Quách, Tiêu, Doãn...) để tăng độ đa dạng.

+ Tên đệm & Tên chính: Phân tách theo giới tính (Male/Female).

+ Username & Email: Được sinh ra từ chính tên thật không dấu, kết hợp với năm sinh hoặc nickname đặc trưng của game thủ (ví dụ: langtu, pro, knight), mô phỏng hành vi đặt tên tài khoản thực tế.
#### B. Logic định danh CCCD (CCCD Integrity)
Đây là phần logic phức tạp nhất, tuân thủ theo quy định của pháp luật Việt Nam:

+ 3 số đầu: Mã tỉnh thành (khớp với trường province).

+ Số thứ 4: Mã giới tính kết hợp thế kỷ sinh (19xx: Nam 0, Nữ 1; 20xx: Nam 2, Nữ 3).

+ 2 số tiếp theo: 2 số cuối của năm sinh (khớp với trường birthday).

+ 6 số cuối: Số ngẫu nhiên duy nhất.

#### C. Phân bổ Nhóm tuổi & Nghề nghiệp (Age & Job Distribution)

Hệ thống sử dụng Trọng số phân cụm (Weighted Clustering):

+ Độ tuổi: Tập trung mạnh vào nhóm 26-30 (40%) và 20-25 (20%) - đây là "độ tuổi vàng" của người chơi game có khả năng tài chính.

+ Nghề nghiệp: Gắn liền với độ tuổi. Nếu age <= 22, hệ thống ưu tiên gán nhãn "Sinh viên". Các nghề nghiệp khác được gán dựa trên trọng số phổ biến (Nhân viên văn phòng, Kinh doanh tự do chiếm tỉ lệ cao).

#### D. Logic địa lý (Location Logic)

Sử dụng danh sách 63 tỉnh thành Việt Nam làm gốc.

+ Địa chỉ: Được kết hợp giữa số nhà ngẫu nhiên + Tên đường phổ biến (Lê Lợi, Nguyễn Huệ...) + Tên tỉnh đã chọn, tạo cảm giác địa chỉ thực.

### 3. Quy trình xử lý dữ liệu (Data Pipeline)

![Sơ đồ Pipeline xử lý dữ liệu](https://raw.githubusercontent.com/Tdpro1612/gamer-management-system/main/data/icon/pipeline_processingdata.jpg)

+ Giai đoạn Khởi tạo (Generation): Sử dụng vòng lặp while kết hợp với các bộ lưu trữ tạm (set) để kiểm tra trùng lặp ngay lập tức (used_emails, used_phones,...).

+ Giai đoạn Làm sạch (Cleaning):

Sử dụng pandas để gộp các phần dữ liệu (Part 1, Part 2).

Thực hiện drop_duplicates trên 5 lớp định danh khác nhau.

Chuẩn hóa định dạng (Padding số 0 cho Phone đủ 10 số, CCCD đủ 12 số).

+ Giai đoạn Lưu trữ (Storage):

Xuất file .csv để phân tích dữ liệu lớn.

Xuất file .json với cấu trúc Key-Value (Key là user_id) để tối ưu hóa việc truy xuất (Look-up) cho các module khác trong hệ thống CSKH.

### 4. Thông số kỹ thuật
+ Ngôn ngữ: Python 3.x

+ Thư viện chính: pandas, random, unicodedata, json.

+ Cấu trúc ID: 20226 + 10 số ngẫu nhiên (Mô phỏng ID hệ thống quản lý tập trung).

+ Email Domains: Hỗ trợ đa dạng từ quốc tế (Gmail, Yahoo) đến nội địa (vnn.vn, fpt.edu.vn).

### 5. Kết luận

Bộ generator này không chỉ tạo ra các dòng dữ liệu phẳng, mà nó tạo ra một Hệ sinh thái người dùng có mối liên kết logic chặt chẽ, phục vụ tốt cho việc kiểm thử các tính năng tìm kiếm, phân loại VIP và truy vết thông tin trong hệ thống Game Management.


---

## 🎮 Tài liệu Tư duy & Logic (Phần 2): Hệ thống Phân bổ Người chơi (Game Database Generator)

### 1. Tổng quan Tư duy
Sau khi đã có bộ dữ liệu người dùng (User Info) chất lượng, bước tiếp theo là giả lập hành vi tham gia vào các sản phẩm game. Tư duy chủ đạo của module này là **"Tình trạng vận hành thực tế" (Market Dynamics)**:
* **Game cũ (Long-standing):** Có thời gian tích lũy người chơi lâu hơn, tập khách hàng lớn hơn.
* **Game mới (New Release):** Đang trong giai đoạn thu hút, lượng người chơi có thể thấp hơn nhưng vẫn phải có tỷ lệ xuất hiện nhất định.
* **Hành vi đa nền tảng (Multi-gaming):** Một người dùng không chỉ chơi một game duy nhất mà có thể trải nghiệm nhiều sản phẩm trong cùng một hệ sinh thái.

---

### 2. Logic triển khai chi tiết

#### A. Trọng số theo thời gian vận hành (Time-based Weighting)
Hệ thống không phân bổ người dùng đồng đều (50/50) mà sử dụng công thức **Linear Weighting** dựa trên số tháng hoạt động:
* **Công thức:** $Weight = \max(1, Months\_Active) + 5$
* **Giải thích:** * `Months_Active`: Game ra mắt càng lâu thì trọng số càng cao, phản ánh khả năng tích lũy user theo thời gian.
    * `+ 5 (Base Weight)`: Đảm bảo các game vừa ra mắt (0 tháng) vẫn có một mức trọng số cơ bản để không bị "trống" người chơi.

#### B. Phân bổ số lượng Game mỗi User (Game Count Distribution)
Mô phỏng hành vi trung thành của người chơi thông qua danh sách trọng số `game_count_weights`:
* **1 Game (80%):** Đại đa số người chơi chỉ tập trung vào một sản phẩm duy nhất.
* **2-3 Games (19%):** Nhóm người chơi thích trải nghiệm hoặc chuyển đổi giữa các game cùng nhà phát hành.
* **4-5 Games (1%):** Nhóm "Hardcore fan" hoặc các tài khoản đặc biệt trải nghiệm toàn bộ hệ sinh thái.

#### C. Cơ chế bốc thăm không trùng lặp (Unique Allocation)
Sử dụng cấu trúc dữ liệu `set()` trong quá trình bốc thăm cho mỗi User:
1. Xác định số lượng game user đó sẽ chơi ($N$).
2. Dùng `random.choices` kết hợp với trọng số thời gian để chọn game.
3. Nếu game đã tồn tại trong `set`, tiếp tục bốc cho đến khi đủ $N$ game duy nhất.
4. Điều này đảm bảo một người dùng không bao giờ bị trùng lặp trong danh sách người chơi của cùng một game.

---

### 3. Quy trình xử lý dữ liệu (Workflow)

1. **Load Data:** Đọc file `user_info.json` (Danh sách định danh người dùng duy nhất).
2. **Calculate Weights:** Quét danh sách `GAMES` để tính toán độ phủ dựa trên ngày `launch`.
3. **Loop & Assign:** * Duyệt qua từng User.
    * Quyết định số lượng game sẽ chơi.
    * Bốc thăm các game tương ứng.
4. **Pivot Data:** Chuyển đổi từ cấu trúc "User-centric" (User có những game nào) sang "Game-centric" (Game có những user nào).
5. **Export:** Lưu trữ vào `game_database.json` để phục vụ cho các module quản lý nạp thẻ và hỗ trợ khách hàng (CSKH).

---

### 4. Cấu trúc dữ liệu đầu ra
Dữ liệu được tổ chức theo dạng Dictionary để tối ưu hóa việc truy vấn theo Game ID:
```json
{
  "Cửu Long Tranh Bá": ["202260000000001", "202260000000005", ...],
  "Hiệp Khách Vô Song": ["202260000000001", "202260000000009", ...],
  ...
}
```

### 5. Ý nghĩa đối với hệ thống CSKH
* **Kiểm tra chéo (Cross-check):** Cho phép nhân viên CSKH biết một User ID đang hoạt động ở những game nào.
* **Phân tích hành vi:** Giúp hệ thống AI nhận diện được tệp khách hàng VIP chơi nhiều game (Whales) để có chế độ chăm sóc đặc biệt.


---

## 🎭 Tài liệu Tư duy & Logic (Phần 3): Hệ thống Persona & Vận hành Server

### 1. Hệ thống Phân lớp Người dùng (Persona & VIP Logic)
Thay vì gán VIP ngẫu nhiên, hệ thống sử dụng **Persona-based Modeling** để mô phỏng chính xác "túi tiền" và thói quen nạp tiền của game thủ:

| Persona | Ý nghĩa | Tỉ lệ mặc định | VIP Range | Đặc điểm hành vi |
| :--- | :--- | :--- | :--- | :--- |
| **WHALE** | Đại gia (Cá voi) | 0.05% | 10 - 15 | Nạp cực nhiều, thường ở các server đầu. |
| **DOLPHIN** | Người nạp khá | 0.1% | 5 - 9 | Nạp đều tay, có đầu tư. |
| **MINNOW** | Người nạp ít | 5% | 1 - 4 | Nạp các gói tháng hoặc gói ưu đãi nhỏ. |
| **F2P** | Người chơi miễn phí | 90% | 0 | Lực lượng đông đảo nhất, giữ nhiệt cho game. |
| **HOPPER** | Dân cày server mới | 2% | 3 - 8 | Nạp khá nhưng không ở lại lâu, thích đi "đua top" server mới. |

#### Logic gán Persona dựa trên Nghề nghiệp & Server:
* **Tương quan thu nhập:** Các nghề nghiệp như *Giám đốc, Bác sĩ, Lập trình viên* có xác suất trở thành **Whale/Dolphin** cao hơn (tỉ lệ nạp ~20%) so với nhóm phổ thông (~5%).
* **Ưu tiên Server đầu:** Các server từ S1 - S10 được cấu hình có tỉ lệ Whale cao hơn để mô phỏng hiệu ứng "hào quang" của những ngày đầu ra mắt game.

---

### 2. Logic Vận hành Server (Server Lifecycle & Buffer)
Để tạo ra ngày mở server (`server_open_date`) và ngày tham gia (`join_date`) thực tế, hệ thống sử dụng cơ chế **Active Buffer**:

1.  **Cụm Server (Filling Strategy):** Mỗi server được mặc định lấp đầy bởi `1000` người chơi (`FULL_NUMBER`).
2.  **Cơ chế rò rỉ (Leakage Rate - 3%):** Mô phỏng việc người chơi mới nhưng lại chọn vào các server cũ (do bạn bè rủ rê hoặc chọn nhầm). Những người này có thể sẽ có `join_date` muộn hơn rất nhiều so với `server_open_date`.
3.  **Ngày mở Server tịnh tiến:** Server $S_{n+1}$ chỉ mở khi Server $S_n$ đã đủ người. Ngày mở server mới sẽ bằng ngày của người chơi cuối cùng nạp vào buffer, đảm bảo tính tuần tự về thời gian.


---

### 3. Logic Nhảy Server (Server Hopping)
Đây là đặc trưng của thị trường game MMORPG Việt Nam. Một người chơi không chỉ đứng yên một chỗ:

* **Xác suất nhảy (Jump Probability):** Đặc biệt cao ở nhóm **HOPPER** (55%).
* **Khoảng cách nhảy:** Người chơi thường nhảy sang các server mới mở sau đó từ 1 - 15 server.
* **Biến biến Persona:** Khi nhảy sang server mới, có 15% xác suất người chơi thay đổi thói quen nạp tiền (Persona và VIP Level được tính toán lại) để mô phỏng việc "làm lại cuộc đời" trong game.
* **Tính nhất quán thời gian:** `Join_date` ở server mới luôn phải lớn hơn `Join_date` ở server cũ và không được vượt quá ngày hiện tại.

---

### 4. Hệ thống Tên In-game (Ultimate Name Generator)
Hệ thống tạo tên (IGN) được thiết kế để chống trùng lặp tuyệt đối và mang đậm phong cách Game thủ:

* **Classic Kiếm Hiệp:** Kết hợp tiền tố (Độc Cô, Mộ Dung...) với tên thật (Ví dụ: `ĐộcCôKhoa`).
* **Modern Style:** Sử dụng các từ khóa hiện đại (Shadow, Legend, Ace...) kèm ký tự ngăn cách (Ví dụ: `Shadow_Khoa`).
* **Hardcore Style:** Sử dụng các ký hiệu bao quanh mô phỏng các Clan/Bang hội (Ví dụ: `[Khoa]`, `xKhoax`).
* **Chống trùng lặp (Uniqueness):** Nếu tên bị trùng, hệ thống tự động thêm hậu tố số ngẫu nhiên dài để đảm bảo `ingame_name` là duy nhất trên toàn bộ hệ thống (Unique Key).

---

### 5. Quy trình xử lý dữ liệu lớn (Big Data Optimization)
Do dữ liệu có thể lên tới hàng triệu bản ghi (sau khi tính toán nhảy server), code được tối ưu hóa:
* **Chunk Processing:** Ghi dữ liệu xuống file CSV theo từng đợt (50,000 dòng/lần) để tránh tràn RAM.
* **Registry Dictionary:** Lưu trữ thông tin server vào bộ nhớ tạm (Dict) để truy xuất (Lookup) cực nhanh khi tính toán ngày nhảy server.
* **Mixed Date Parsing:** Xử lý linh hoạt các định dạng ngày tháng trước khi chuẩn hóa về định dạng cuối cùng `%Y-%m-%d`.

---
**Kết quả cuối cùng:** Bạn nhận được file `game_data_final.csv` chứa đựng một lịch sử vận hành game sống động, sẵn sàng cho các bài toán phân tích hành vi, dự đoán rời bỏ (Churn prediction) hoặc tối ưu hóa doanh thu.


---

## 💸 Tài liệu Tư duy & Logic (Phần 4): Hệ thống Giả lập Giao dịch (Billing System)

### 1. Logic Phân phối Gói nạp (Package Strategy)
Hệ thống không nạp tiền một cách ngẫu nhiên mà tuân theo **Danh mục sản phẩm (Product Catalog)** thực tế của một nhà phát hành game:

* **Gói Cơ bản (Base Packages):** Các mốc nạp từ 10k đến 5M VNĐ.
* **Gói Đặc quyền (Event-based):** * *Nạp đầu (First Purchase):* Gói kích cầu bắt buộc phải có cho mọi User có nạp.
    * *Chu kỳ (Weekly/Monthly):* Các gói tối ưu hóa (Subscription-like) chỉ xuất hiện 1 lần mỗi tuần hoặc mỗi tháng.
    * *Đua Top (High-value):* Các gói mệnh giá cực lớn (lên tới 50M VNĐ) dành riêng cho nhóm VIP cao để bứt phá lực chiến.

### 2. Logic "Target Money" & Ngưỡng VIP (VIP Thresholds)
Mỗi User được sinh ra với một `vip_level` mục tiêu từ module trước. Hệ thống Billing sẽ "ngược dòng" thời gian để khớp con số này:
* **Xác định Target:** Số tiền nạp phải nằm trong khoảng $[Threshold_{current}, Threshold_{next} - 10,000]$.
* **Chiến thuật nạp (Staged Pacing):** * **Giai đoạn Boom (3 ngày đầu):** Mô phỏng tâm lý hào hứng khi mới chơi. User sẽ nạp "xả láng" các gói nạp đầu và gói đua top (chiếm đến 60% tổng tiền đối với VIP cao).
    * **Giai đoạn Duy trì:** Rải các gói tuần, gói tháng theo đúng chu kỳ thời gian.
    * **Giai đoạn Lấp đầy:** Nạp bù các gói cơ bản vào các ngày ngẫu nhiên để đạt đủ mốc VIP mục tiêu.



### 3. Phân bổ Thời gian thực tế (Time Distribution)
Để dữ liệu trông như thật trên các biểu đồ Real-time Dashboard, giờ nạp tiền (`created_at`) được phân bổ theo thói quen sinh hoạt:
* **Giờ vàng (20h - 23h):** 40% giao dịch (Thời gian rảnh buổi tối).
* **Nghỉ trưa (11h - 13h):** 20% giao dịch.
* **Còn lại:** Rải đều vào sáng, chiều và một ít vào ban đêm.
* **Anti-Duplicate:** Cơ chế tự động cộng thêm giây nếu có hai giao dịch của cùng một User bị trùng timestamp.

---

### 4. Logic Chiết khấu & Kênh thanh toán (Channels & Discounts)
Hệ thống mô phỏng sự khác biệt giữa các kênh nạp tiền để phân tích hiệu quả doanh thu:
* **In-app Purchase (Apple/Google):** Giữ nguyên giá (`original_amount`), nhà phát hành thường mất 30% phí nhưng User không được chiết khấu.
* **Banking/Momo:** Kênh trực tiếp của nhà phát hành.
    * Nạp dưới 500k: Chiết khấu 10%.
    * Nạp trên 500k: Chiết khấu 15%.
* **Paid Amount:** Là số tiền thực tế ghi nhận vào dòng tiền (Cash flow) sau khi trừ chiết khấu.

---

### 5. Cấu trúc dữ liệu Giao dịch
Mỗi bản ghi trong `transaction_gamer.csv` đại diện cho một hóa đơn thanh toán thành công:

| Trường dữ liệu | Giải thích |
| :--- | :--- |
| `bill_id` | Mã hóa đơn duy nhất (Kết hợp từ UID + Timestamp). |
| `original_amount` | Giá trị gói nạp hiển thị trong game. |
| `paid_amount` | Số tiền thực tế User bỏ ra (Sau chiết khấu). |
| `channel` | Kênh nạp (Banking, Momo, In-app). |
| `created_at` | Thời điểm phát sinh giao dịch (Y-m-d H:M:S). |

---

### 6. Khả năng Phân tích (Analytics Potential)
Dữ liệu sinh ra từ module này cho phép thực hiện các báo cáo chuyên sâu:
1.  **ARPPU (Average Revenue Per Paying User):** Doanh thu trung bình trên mỗi người nạp.
2.  **Whale Analysis:** Theo dõi hành vi nạp của nhóm 5% người chơi đóng góp 80% doanh thu.
3.  **Revenue by Channel:** Đánh giá kênh nạp nào đang mang lại nhiều tiền thực tế nhất.
4.  **Hourly Heatmap:** Xác định khung giờ cao điểm để đẩy các sự kiện khuyến mãi.

---
**Hoàn tất bộ dữ liệu!** Hiện tại bạn đã có một "Vũ trụ Game" thu nhỏ với đầy đủ: User, Game, Server, Hành vi nhảy server và Lịch sử nạp tiền.


---

## 🗄️ Tài liệu Tư duy & Logic (Phần 5): Lưu trữ & Tối ưu hóa Database (SQLite)

### 1. Kiến trúc Schema (Relational Mapping)
Hệ thống chuyển đổi dữ liệu từ dạng CSV sang mô hình quan hệ (Relational Model) để đảm bảo tính toàn vẹn và khả năng truy vấn phức tạp:

* **Users Table:** Lưu trữ thông tin định danh gốc (Họ tên, ngày sinh, nghề nghiệp).
* **User_Games Table:** Bảng trung gian thể hiện mối quan hệ *Many-to-Many* (Một người chơi nhiều game, một game có nhiều người). Lưu trữ thông tin Server, In-game Name và VIP Level.
* **Transactions Table:** Bảng dữ liệu lớn (Fact Table) chứa toàn bộ lịch sử nạp tiền.
* **Accounts Table:** Bảng phân quyền (RBAC) dành cho hệ thống quản trị (Admin/Staff).

### 2. Chiến lược nạp dữ liệu lớn (Big Data Ingestion)
Để tránh tình trạng tràn bộ nhớ (Out of Memory) khi xử lý hàng triệu bản ghi giao dịch, mã nguồn áp dụng kỹ thuật **Chunking**:

* **Logic `chunksize`:** Thay vì đọc toàn bộ file `transaction_gamer.csv` (có thể nặng vài GB), dữ liệu được chia nhỏ thành từng khối `50,000` dòng.
* **Cơ chế `if_exists` thông minh:**
    * Sử dụng `replace` cho các bảng cấu hình nhỏ để luôn cập nhật dữ liệu mới nhất.
    * Sử dụng cờ hiệu (`first_chunk`) để `replace` lần đầu (làm sạch bảng cũ) và `append` cho các khối tiếp theo nhằm tối ưu hóa hiệu năng ghi.

### 3. Tối ưu hóa hiệu năng (Indexing Strategy)
Truy vấn trên hàng triệu bản ghi sẽ cực kỳ chậm nếu không có Index. Hệ thống được thiết lập các bộ chỉ mục chiến lược:

* **`idx_users_search`:** Tối ưu hóa việc tìm kiếm thông tin khách hàng theo ID.
* **`idx_user_games_user`:** Tăng tốc độ hiển thị danh sách các game mà một User đang chơi.
* **`idx_txns_composite` (Composite Index):** Đây là Index quan trọng nhất, kết hợp `(user_id, game_name, created_at)`. 
    * Hỗ trợ lọc nhanh lịch sử nạp của 1 user trong 1 game cụ thể.
    * Hỗ trợ sắp xếp theo thời gian nạp mà không cần quét toàn bộ bảng.



### 4. Quản lý bảo mật & Phân quyền
Khác với dữ liệu thô, cơ sở dữ liệu SQLite được tích hợp sẵn hệ thống tài khoản quản trị:
* **Khởi tạo mặc định:** Tự động tạo tài khoản `admin` với mật khẩu mã hóa (nếu chưa tồn tại).
* **Sẵn sàng cho ứng dụng:** Cấu trúc bảng `Accounts` cho phép mở rộng thêm các tính năng như đăng nhập, phân quyền xem báo cáo (chỉ xem được game mình quản lý) hoặc quyền xuất dữ liệu.

---

### 5. Hướng dẫn sử dụng nhanh
Sau khi chạy script này, bạn sẽ nhận được file `game_data.db`. Bạn có thể sử dụng các công cụ như **DB Browser for SQLite** hoặc **DBeaver** để:
1.  **Chạy SQL Report:** Tính tổng doanh thu theo tháng của từng game.
2.  **Truy vết (Audit):** Tìm kiếm toàn bộ hành vi của một "Whale" từ lúc tạo tài khoản đến khi nhảy server và nạp gói Đua Top cuối cùng.

---
## 🏁 Kết thúc chuỗi Pipeline Dữ liệu
Bạn đã hoàn thành hệ thống từ **Sinh dữ liệu userinfo -> Phân bổ user vào game-> Gán Persona -> Phân bổ Server -> Giả lập Giao dịch -> Đóng gói Database**. 


---

## 🚀 Tài liệu Tư duy & Logic (Phần 6): Hệ thống API Chăm sóc khách hàng (CSKH)

### 1. Kiến trúc Hệ thống API
Thay vì truy cập trực tiếp vào Database, bộ phận vận hành sẽ sử dụng lớp **FastAPI Middleware**. Điều này đảm bảo:
* **Bảo mật:** Chỉ những người có tài khoản mới được truy vấn.
* **Kiểm soát (Audit):** Mọi hành động tìm kiếm đều ghi nhận lại danh tính người thực hiện (`search_by`).
* **Hiệu năng:** Các câu lệnh SQL được tối ưu hóa thông qua cơ chế `Index` đã tạo ở bước trước.



---

### 2. Cơ chế Bảo mật & Phân quyền (Security & RBAC)
Hệ thống áp dụng chuẩn **OAuth2 với Bearer Token**:
* **Authentication:** API kiểm tra `access_token` (trong bản demo là username) để xác minh danh tính.
* **Role-Based Access Control (RBAC):**
    * **Staff (Nhân viên):** Có quyền tra cứu thông tin người dùng và lịch sử nạp tiền.
    * **Admin (Quản trị):** Có thêm quyền thay đổi dữ liệu (ví dụ: cập nhật số điện thoại khách hàng khi có sai sót).

---

### 3. Logic Tìm kiếm Thông minh (Dynamic Search)
Module `search-user` sử dụng tư duy **SQL Động (Dynamic Query Construction)**:
* **Logic "1=1":** Cho phép nối thêm các điều kiện `AND` một cách linh hoạt mà không lo về cú pháp SQL.
* **Tiêu chí đa dạng:** Nhân viên có thể tìm khách hàng bằng bất cứ thông tin nào họ có: `user_id`, `username`, `phone`, hoặc `email`.
* **Validation:** API bắt buộc phải có ít nhất một thông tin tìm kiếm để tránh việc quét toàn bộ bảng (Full Table Scan), gây quá tải hệ thống.

---

### 4. Logic Tra cứu Giao dịch (Transaction Lookup)
Module `search-transactions` được thiết kế để xử lý các khiếu nại về nạp thẻ:
* **Lọc đa tầng:** Hỗ trợ lọc theo `game_name` và `server_id`. Nếu không truyền vào (Optional), hệ thống sẽ trả về toàn bộ lịch sử nạp của User đó.
* **Tối ưu hóa hiển thị:** * Sử dụng `ORDER BY created_at DESC` để đưa những giao dịch mới nhất lên đầu (thường là giao dịch khách hàng đang cần hỗ trợ).
    * Sử dụng `LIMIT` để tránh việc trả về quá nhiều dữ liệu cùng lúc, giúp ứng dụng phía Client (Web/Mobile) load nhanh hơn.

---

### 5. Quy trình Xử lý Dữ liệu (Backend Workflow)
1.  **Request:** Client gửi yêu cầu kèm Token.
2.  **Dependency Injection (`get_db`):** FastAPI tự động mở kết nối SQLite và đảm bảo đóng kết nối (`close`) sau khi hoàn tất để tránh rò rỉ bộ nhớ.
3.  **Permission Check:** Kiểm tra quyền của người dùng hiện tại thông qua `get_current_account`.
4.  **SQL Execution:** Thực thi câu lệnh với `params` để chống tấn công **SQL Injection**.
5.  **Response:** Trả về dữ liệu dạng JSON chuẩn hóa, dễ dàng tích hợp với các giao diện hiện đại.

---

### 6. Các điểm cuối (Endpoints) chính

| Method | Endpoint | Mô tả | Quyền hạn |
| :--- | :--- | :--- | :--- |
| `POST` | `/login` | Đăng nhập và nhận Token truy cập. | Public |
| `GET` | `/search-user` | Tìm kiếm thông tin chi tiết của một người chơi. | Staff/Admin |
| `GET` | `/search-transactions` | Tra cứu lịch sử nạp tiền (có lọc theo Game/Server). | Staff/Admin |
| `PUT` | `/update-user/{id}` | Cập nhật thông tin nhạy cảm (SĐT) của khách hàng. | **Admin Only** |

---
**Hệ thống đã sẵn sàng vận hành!** Với bộ API này, bạn đã biến "Dữ liệu thô" thành một "Công cụ vận hành" thực thụ cho doanh nghiệp.
