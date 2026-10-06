# Đồ án: Kết xuất ảnh với góc nhìn tùy ý từ dãy ảnh 2D (NeRF)

Môn Đồ Họa Máy Tính, tìm hiểu mô hình **NeRF (Neural Radiance Fields)** và các biến thể cải tiến.

**Phương pháp chọn trình bày (Chương 3):** Mip-NeRF 360 (Barron et al., CVPR 2022)

## Cấu trúc thư mục

```
Doan/
├── 01-DeBai/          Đề bài + hướng dẫn của giảng viên
├── 02-TaiLieuHoc/     Ghi chú tự biên soạn (để học, không trích dẫn)
├── 03-Reference/      16 paper gốc, nguồn trích dẫn hợp lệ
│   ├── Selected/      3 paper cho Chương 3 (NeRF → Mip-NeRF → Mip-NeRF 360)
│   ├── Survey/        3 survey cho Chương 2
│   ├── Foundation/    3 paper nền tảng (COLMAP, LLFF, volume rendering)
│   └── Related/       7 hướng cải tiến khác
├── 04-Code/           Mã nguồn thử nghiệm (Chương 4)
├── 05-Data/           Dataset ảnh + kết quả COLMAP
├── 06-BaoCao/         File báo cáo
└── 07-Slide/          Slide thuyết trình
```

Chi tiết danh mục paper: xem [`03-Reference/README.md`](03-Reference/README.md)

## Tiến độ

| Chương | Trạng thái | Ghi chú |
|---|---|---|
| 1. Giới thiệu | Chưa viết | Nguyên liệu có trong `02-TaiLieuHoc/lythuyet_NeRF.md` |
| 2. Công trình liên quan | Chưa viết | Cần đọc 3 survey + tổng hợp bảng so sánh |
| 3. Phương pháp | Nguyên liệu sẵn sàng | `02-TaiLieuHoc/pipeline_MipNeRF360.md` (1.615 dòng, đã verify với paper) |
| 4. Cài đặt & thử nghiệm | **Chưa bắt đầu** | Rủi ro cao nhất, xem mục bên dưới |
| 5. Kết luận | Chưa viết | Phụ thuộc kết quả Chương 4 |

## Lưu ý quan trọng về Chương 4

Máy làm đồ án là **MacBook Apple M2 Pro, không có GPU NVIDIA/CUDA**, trong khi `nerfstudio`, `instant-ngp`, `multinerf` đều yêu cầu CUDA (phần hash encoding `tiny-cuda-nn` là CUDA kernel, không chạy trên Apple Silicon).

**Phương án:** dùng Google Colab hoặc Kaggle (GPU NVIDIA miễn phí), chạy model `nerfacto` của nerfstudio, kế thừa scene contraction + proposal network của Mip-NeRF 360, thay encoding bằng hash grid để khả thi về tài nguyên.

**Khuyến nghị:** dựng môi trường và train thử dataset mẫu **sớm**, không để tới cuối kỳ. Lỗi môi trường (CUDA version, dependency conflict, hết VRAM) thường ngốn 2-3 tuần nếu phát hiện muộn.

## Tài liệu gốc của giảng viên

- `01-DeBai/de.rtf`: đề tài
- `01-DeBai/huongdantrinhbay.rtf`: cấu trúc 5 chương bắt buộc
- `01-DeBai/phuongphap.rtf`: quy trình làm đồ án (9 bước)
