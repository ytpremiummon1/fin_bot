# Financial Analysis Tools

Bộ công cụ phân tích tài chính sử dụng AI, bao gồm hai module chính:
1. Financial Query Agent (ReAct pattern)
2. Tools-enabled Financial Chatbot

## Tính năng

### 1. Financial Query Agent (`ai_query_exp.py`)
- Sử dụng ReAct Agent pattern với Claude 3.5
- Tự động chuyển đổi câu hỏi tiếng Việt thành truy vấn SQL
- Phân tích dữ liệu tài chính: ROE, ROA, lợi nhuận, so sánh ngành...
- Kết nối trực tiếp với MySQL database

### 2. Tools-enabled Chatbot (`tools_summ_mem.py`)
- Chatbot đa năng với khả năng sử dụng nhiều công cụ
- Hỗ trợ nhiều mô hình LLM (Claude và GPT)
- Có bộ nhớ lưu trữ lịch sử hội thoại
- Giao diện tương tác qua terminal

## Cài đặt

### Yêu cầu
- Python 3.11+
- MySQL Server
- Pipenv

### Các bước cài đặt

1. Clone repository:
```bash
git clone https://github.com/hungson175/shared_fin_bot
cd shared_fin_bot
```

2. Cài đặt dependencies:
```bash
pipenv install
```

3. Tạo file .env từ .env.sample và cập nhật các giá trị:
```bash
cp .env.sample .env
```

4. Cấu hình database:
- Tạo database MySQL mới
- Cập nhật thông tin kết nối trong file .env

## Sử dụng

### 1. Financial Query Agent:
```bash
pipenv run python ai_query_exp.py
```

### 2. Tools-enabled Chatbot:
```bash
pipenv run python tools_summ_mem.py
```

## Biến môi trường

Xem file `.env.sample` để biết các biến môi trường cần thiết.
