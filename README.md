# Ứng dụng Tách Nền Ảnh bằng Streamlit

Ứng dụng cho phép bạn tải lên ảnh (PNG/JPG/WEBP), tự động tách nền và xuất ảnh PNG nền trong suốt.

## Cách chạy (Windows)

1. Mở PowerShell tại thư mục dự án.
2. Tạo môi trường ảo:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

3. Cài dependencies:

```powershell
pip install -r requirements.txt
```

Ghi chú: `requirements.txt` đã dùng `rembg[cpu]` để chắc chắn có backend `onnxruntime` trên máy không dùng CUDA.

4. Chạy Streamlit:

```powershell
streamlit run app.py
```

## Ghi chú

- Lần chạy đầu tiên có thể chậm vì `rembg` cần tải model.
- Ảnh đầu ra được tải về dưới dạng `output.png` (PNG có kênh alpha).

