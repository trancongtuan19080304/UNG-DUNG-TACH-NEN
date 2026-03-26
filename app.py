import io

import streamlit as st
from PIL import Image

try:
    from rembg import remove
except ModuleNotFoundError:
    st.error(
        "Thiếu thư viện `rembg` trong môi trường Python hiện tại. "
        "Hãy cài bằng lệnh: `pip install -r requirements.txt` (hoặc `pip install \"rembg[cpu]\"`)."
    )
    st.stop()


st.set_page_config(page_title="Tách Nền Ảnh", page_icon="🖼️", layout="centered")
st.title("Tách Nền Ảnh (Background Removal)")
st.caption("Tải ảnh lên và ứng dụng tự động tách nền, xuất PNG nền trong suốt.")


def _resize_keep_aspect(img: Image.Image, max_side: int) -> Image.Image:
    """Resize ảnh sao cho cạnh dài nhất <= max_side (giữ tỉ lệ)."""
    if max_side <= 0:
        return img

    w, h = img.size
    long_side = max(w, h)
    if long_side <= max_side:
        return img

    scale = max_side / long_side
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    return img.resize((new_w, new_h), Image.LANCZOS)


def _center_crop_square(img: Image.Image) -> Image.Image:
    """Cắt giữa thành hình vuông (giữ tỉ lệ, không méo)."""
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def _resize_exact(img: Image.Image, size: int) -> Image.Image:
    """Resize đúng WxH = size x size."""
    return img.resize((size, size), Image.LANCZOS)


@st.cache_data(show_spinner=False)
def process_image(image_bytes: bytes, resize_mode: str, max_side: int, square_size: int) -> bytes:
    """
    Trả về bytes PNG (nền trong suốt).

    Lưu ý: rembg có thể tải model lần đầu, nên lần đầu chạy có thể chậm.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    if resize_mode == "Giữ tỉ lệ":
        img = _resize_keep_aspect(img, max_side=max_side)
    elif resize_mode == "Ảnh vuông 1000×1000 (cắt giữa)":
        img = _center_crop_square(img)
        img = _resize_exact(img, size=square_size)

    # rembg cần bytes ảnh đã được encode (thường là PNG/JPG), không phải raw RGBA.
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    input_png_bytes = buf.getvalue()

    # Output là bytes PNG có alpha (nền trong suốt).
    return remove(input_png_bytes)


with st.sidebar:
    st.header("Tùy chọn")
    resize_mode = st.selectbox(
        "Kiểu kích thước",
        options=["Giữ tỉ lệ", "Ảnh vuông 1000×1000 (cắt giữa)"],
        index=0,
    )

    size_mode = st.selectbox(
        "Kích thước xử lý (cạnh dài nhất)",
        options=[
            "Giữ nguyên",
            "512 px",
            "768 px",
            "1024 px",
            "1600 px (khuyên dùng)",
            "2048 px",
            "Tự nhập...",
        ],
        index=4,
        help="Chỉ áp dụng khi chọn “Giữ tỉ lệ”.",
    )

    preset_map = {
        "Giữ nguyên": 4000,
        "512 px": 512,
        "768 px": 768,
        "1024 px": 1024,
        "1600 px (khuyên dùng)": 1600,
        "2048 px": 2048,
    }

    if size_mode == "Tự nhập...":
        max_side = st.number_input(
            "Nhập cạnh dài nhất (px)",
            min_value=256,
            max_value=4000,
            value=1600,
            step=64,
        )
    else:
        max_side = preset_map[size_mode]

    square_size = 1000


uploaded = st.file_uploader(
    "Chọn ảnh",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=False,
)

if not uploaded:
    st.info("Hãy tải một ảnh lên để bắt đầu tách nền.")
    st.stop()

input_bytes = uploaded.read()

try:
    with st.spinner("Đang tách nền..."):
        output_bytes = process_image(
            input_bytes, resize_mode=resize_mode, max_side=int(max_side), square_size=int(square_size)
        )

    original_img = Image.open(io.BytesIO(input_bytes)).convert("RGBA")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ảnh gốc")
        st.image(original_img, use_container_width=True)
    with col2:
        st.subheader("Ảnh sau khi tách nền")
        st.image(Image.open(io.BytesIO(output_bytes)), use_container_width=True)

    st.download_button(
        label="Tải PNG nền trong suốt",
        data=output_bytes,
        file_name="output.png",
        mime="image/png",
    )
except Exception as e:
    st.error("Không thể tách nền. Vui lòng thử lại với ảnh khác.")
    st.exception(e)

