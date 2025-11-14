# NOF1 API Proxy Service

Một FastAPI service để proxy các cuộc gọi API đến NOF1, sử dụng `curl_cffi` để bỏ qua các biện pháp chống bot.

## Cài đặt

1. Cài đặt Python dependencies:
```bash
pip install -r requirements.txt
```

2. (Tùy chọn) Cấu hình environment variables trong file `.env`:
```
NOF1_BASE_URL=https://nof1.ai
REQUEST_TIMEOUT=30
PORT=8000
HOST=0.0.0.0
ENV=development
```

## Chạy Service

### Windows
```bash
start.bat
```

### Linux/macOS
```bash
chmod +x start.sh
./start.sh
```

### Hoặc chạy trực tiếp
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Health Check
- **GET** `/health`
- Kiểm tra trạng thái service

### Account Totals (Proxy NOF1 API)
- **GET** `/api/account-totals?marker=<số>`
- Proxy cho NOF1 account totals API
- Parameters:
  - `marker` (optional): Marker cho pagination

### Generic Proxy
- **GET** `/api/proxy?url=<url>&method=<method>`
- Proxy cho bất kỳ NOF1 API nào
- Parameters:
  - `url`: URL đầy đủ để proxy (phải bắt đầu bằng NOF1_BASE_URL)
  - `method`: HTTP method (mặc định GET)

## Tính năng

- ✅ Browser impersonation với Chrome 120
- ✅ Headers được tối ưu để giống browser thật
- ✅ Xử lý lỗi chi tiết
- ✅ Response format chuẩn hóa
- ✅ CORS support
- ✅ Health check endpoint
- ✅ Environment configuration
- ✅ Request/Response logging

## Response Format

Tất cả API endpoints trả về format chuẩn:

```json
{
  "success": true,
  "data": {
    // Dữ liệu thực tế từ NOF1 API
  },
  "error": null,
  "timestamp": "2025-11-14T10:30:00.000Z"
}
```

## Lỗi thường gặp

1. **Connection refused**: Đảm bảo service đã được start
2. **Import errors**: Chạy `pip install -r requirements.txt`
3. **Port đã được sử dụng**: Thay đổi PORT trong .env hoặc kill process đang sử dụng port 8000

## Tích hợp với TypeScript

Service này được thiết kế để tích hợp với `Nof1DataProvider` trong TypeScript codebase. TypeScript client sẽ gọi đến Python proxy service thay vì gọi trực tiếp NOF1 API.

## Bảo mật

- Service chỉ cho phép proxy đến các URL bắt đầu bằng `NOF1_BASE_URL`
- Không có authentication - phù hợp cho môi trường development local
- Nên thêm authentication nếu deploy lên production

## Development

Để development, đặt `ENV=development` trong `.env` để bật auto-reload mode.