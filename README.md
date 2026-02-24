# 📊 Chatbot Trợ Lý AI Chứng Khoán

Chatbot là một ứng dụng trợ lý AI cho phép người dùng hỏi – đáp trực tiếp về chứng khoán Việt Nam, hiển thị dữ liệu thị trường, phân tích giá và báo cáo tài chính, được xây dựng bằng Streamlit với khả năng gọi các hàm hỗ trợ từ mô hình AI Gemini của Google.

# 🚀 Mục tiêu

Dự án này được thiết kế để:

- 💬 Cho phép người dùng tương tác với trợ lý AI bằng giọng văn tự nhiên.

- 📈 Trả lời các câu hỏi về chứng khoán/cổ phiếu và dữ liệu thị trường.

- 📊 Phân tích dữ liệu tài chính, hiển thị biểu đồ, và truy xuất dữ liệu lịch sử.

- 🧠 Tích hợp mô hình ngôn ngữ Gemini để xử lý ngôn ngữ tự nhiên và gọi các hàm phân tích dữ liệu thực tế.

# 💡 Tính năng chính

- ✔️ Giao diện chat đơn giản với Streamlit
- ✔️ Phân tích dữ liệu chứng khoán theo yêu cầu người dùng
- ✔️ Trả lời câu hỏi liên quan đến:
    - Giá giao dịch hiện tại và lịch sử
    - Chỉ số kỹ thuật (RSI, MACD, v.v.)
    - Báo cáo tài chính theo quý và theo năm
- ✔️ Tự động gọi hàm (function calling) từ chatbot để truy xuất dữ liệu thật và tạo phân tích chính xác.

# 🧰 Công nghệ sử dụng

- Python

- Streamlit – giao diện người dùng

- Google Gemini API – mô hình AI xử lý hội thoại và logic function calling

- vnstock – lấy dữ liệu thị trường chứng khoán

- Plotly – vẽ biểu đồ phân tích

- SQLite/PostgreSQL/MySQL – lưu dữ liệu chứng khoán (qua SQLAlchemy/Engine)

- Các hàm utility nằm trong utils/ dùng để fetch và xử lý dữ liệu.

# 📦 Cấu trúc dự án
```
chatbot/
├── README.md
├── app.py                 # Giao diện trò chuyện chính
├── get_data.py            # Lấy và lưu dữ liệu chứng khoán
├── requirements.txt       # Thư viện phụ thuộc
├── utils/
│   ├── chatbot.py         # Lớp chatbot và logic function calling
│   ├── plotly_chart.py    # Vẽ biểu đồ dữ liệu
│   ├── query.py           # Hàm lấy dữ liệu từ DB
│   └── connection.py      # Kết nối database
```
# 🛠 Cách cài đặt & chạy

1. Clone repo
``
git clone https://github.com/NguyenGiaHuy2710/chatbot.git
cd chatbot
``
2. Cài phụ thuộc
``
pip install -r requirements.txt
``
3. Thiết lập biến môi trường

Tạo file .env chứa:
``
GOOGLE_API_KEY=YOUR_GOOGLE_GENAI_KEY
``
4. Chạy ứng dụng
``
streamlit run app.py
``
Mở trình duyệt tại http://localhost:8501 để bắt đầu chat với trợ lý AI chứng khoán.

# 💬 Ví dụ hỏi – đáp

- ✏️ “Giá cổ phiếu FPT hôm nay là bao nhiêu?”
- ✏️ “Phân tích kỹ thuật mã VNM trong 3 tháng qua”
- ✏️ “Xu hướng tài chính theo quý của MSN”

Bạn chỉ cần nhập câu hỏi tự nhiên, chatbot sẽ gọi các hàm truy xuất dữ liệu và trả lời ngay lập tức.

# 📌 Ghi chú

Chatbot không chỉ trả lời bằng văn bản mà còn tích hợp function calling để lấy dữ liệu thật từ API/Database.

Mục tiêu là phân tích chứng khoán Việt Nam – nên các dữ liệu và hàm đều tập trung vào thị trường Việt.