# Secure-Remote-Snapshot-API

Xây dựng hệ thống giám sát từ xa tích hợp cơ chế kiểm soát truy cập dựa trên API Token. Dự án mô phỏng cách thức các thiết bị IoT xác thực và giao tiếp qua giao thức HTTP/HTTPS.

## Kỹ năng thể hiện

- **Web Security:** Hiểu và áp dụng cơ chế xác thực API Key, xử lý HTTP status code (`403 Forbidden`) cho truy cập trái phép.
- **Hardware Integration:** Điều khiển camera cục bộ và xử lý ảnh qua OpenCV.
- **Network Exposure:** Public dịch vụ nội bộ ra Internet an toàn bằng tunneling (Ngrok) để demo HTTPS.
- **Security Logging:** Ghi nhật ký mọi lần truy cập vào `security.log` để audit hành vi thành công/thất bại.

## Kiến trúc nhanh

- Endpoint: `GET /snapshot`
- Cơ chế auth: Query `?key=...` hoặc header `X-API-Key`
- Ảnh chụp: lưu vào thư mục `snapshots/`
- Log truy cập: `security.log`

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
python app.py
```

Ứng dụng chạy tại `http://127.0.0.1:5000`.

## Public HTTPS bằng Ngrok

1. Cài `ngrok` từ https://ngrok.com/
2. Mở terminal mới và chạy:

```bash
ngrok http 5000
```

Ngrok trả về URL kiểu `https://xxxx-xxxx.ngrok-free.app`.

## Demo bảo mật

- Truy cập **không có key** hoặc key sai:
  - `GET /snapshot`
  - Kết quả: `403 Forbidden`
- Truy cập **key hợp lệ**:
  - `GET /snapshot?key=supersecret123`
  - Kết quả: chụp ảnh và lưu file thành công

Ví dụ với URL ngrok:

- `https://xxxx.ngrok-free.app/snapshot` → `403`
- `https://xxxx.ngrok-free.app/snapshot?key=supersecret123` → `200`

## Biến môi trường (khuyến nghị)

- `SNAPSHOT_API_KEY`: API Key bảo vệ endpoint (mặc định: `supersecret123`)
- `SNAPSHOT_DIR`: thư mục lưu ảnh (mặc định: `snapshots`)
- `SECURITY_LOG_FILE`: file log (mặc định: `security.log`)

Ví dụ:

```bash
export SNAPSHOT_API_KEY="my_strong_key"
python app.py
```

## Kiểm thử

```bash
python -m unittest discover -s tests -p "test_*.py"
```

