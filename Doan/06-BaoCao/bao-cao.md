<!-- BÁO CÁO ĐỒ ÁN - FILE CHÍNH
     Viết dần theo dàn ý tại 06-BaoCao/dan-y-bao-cao.md
     Xuất .docx bằng script md2docx
     Trạng thái: đang viết Phần Mở Đầu -->

# ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH

## TRƯỜNG ĐẠI HỌC [TÊN TRƯỜNG]

### KHOA [TÊN KHOA]

<br>

# ĐỒ ÁN MÔN HỌC ĐỒ HỌA MÁY TÍNH

<br>

# XÂY DỰNG ỨNG DỤNG KẾT XUẤT ẢNH VỚI GÓC NHÌN TÙY Ý DỰA VÀO DÃY ẢNH 2D CHO TRƯỚC

## Tìm hiểu mô hình NeRF và NeRF cải tiến

<br>

**Giảng viên hướng dẫn:** PGS.TS Lý Quốc Ngọc

**Lớp:** Đồ Họa Máy Tính CQ2024/23

**Nhóm thực hiện:**

| Họ và tên | MSSV |
|---|---|
| Bùi Văn Thiên | 24120138 |
| Nguyễn Minh Khoa | 24120073 |

<br>

**Thành phố Hồ Chí Minh, năm 2026**

---

# LỜI CẢM ƠN

Nhóm xin gửi lời cảm ơn tới PGS.TS Lý Quốc Ngọc, giảng viên hướng dẫn môn Đồ Họa Máy Tính. Thầy đã giao đề tài, cung cấp tài liệu hướng dẫn về cách trình bày báo cáo cũng như quy trình thực hiện đồ án, và chỉ ra những lỗi thường gặp mà sinh viên hay mắc phải khi làm nghiên cứu ứng dụng. Phần hướng dẫn về các lỗi thường gặp giúp nhóm xác định được trục tổ chức của báo cáo ngay từ đầu, thay vì viết xong mới phát hiện thiếu sót.

Nhóm cũng cảm ơn các tác giả của những công trình được khảo sát trong báo cáo này. Toàn bộ nội dung kỹ thuật được trình bày đều dựa trên các bài báo đã công bố tại những hội nghị và tạp chí chuyên ngành, và phần lớn các nhóm tác giả đều công khai mã nguồn cùng dữ liệu thử nghiệm. Nếu không có sự chia sẻ đó, việc cài đặt lại và kiểm chứng kết quả trong Chương 4 sẽ không thực hiện được trong khuôn khổ một đồ án môn học.

Do hạn chế về thời gian và kinh nghiệm, báo cáo chắc chắn còn thiếu sót. Nhóm mong nhận được góp ý của thầy để hoàn thiện.

---

# MỤC LỤC

> Sinh tự động sau khi hoàn thành nội dung, hiển thị tới mục cấp ba.

---

# DANH MỤC HÌNH

> Lập sau khi hoàn thành nội dung. Hình đánh số theo chương, ví dụ Hình 3.1.

---

# DANH MỤC BẢNG

> Lập sau khi hoàn thành nội dung. Bảng đánh số theo chương, ví dụ Bảng 2.1.

---

# DANH MỤC TỪ VIẾT TẮT

| Viết tắt | Tên đầy đủ | Nghĩa tiếng Việt |
|---|---|---|
| 3DGS | 3D Gaussian Splatting | Phương pháp biểu diễn cảnh bằng các Gaussian ba chiều |
| COLMAP | (tên phần mềm) | Phần mềm mã nguồn mở thực hiện Structure-from-Motion và Multi-View Stereo |
| CUDA | Compute Unified Device Architecture | Nền tảng tính toán song song của NVIDIA |
| CVPR | Conference on Computer Vision and Pattern Recognition | Hội nghị quốc tế về thị giác máy tính và nhận dạng mẫu |
| ECCV | European Conference on Computer Vision | Hội nghị thị giác máy tính châu Âu |
| FPS | Frames Per Second | Số khung hình trên giây |
| GPU | Graphics Processing Unit | Bộ xử lý đồ họa |
| ICCV | International Conference on Computer Vision | Hội nghị quốc tế về thị giác máy tính |
| IPE | Integrated Positional Encoding | Mã hóa vị trí tích hợp, mã hóa cả một vùng thay vì một điểm |
| LPIPS | Learned Perceptual Image Patch Similarity | Độ đo khác biệt ảnh theo cảm nhận thị giác, tính bằng mạng học sẵn |
| MLP | Multi-Layer Perceptron | Mạng nơ-ron nhiều lớp kết nối đầy đủ |
| MSE | Mean Squared Error | Sai số bình phương trung bình |
| NDC | Normalized Device Coordinates | Hệ tọa độ thiết bị chuẩn hóa |
| NeRF | Neural Radiance Fields | Trường bức xạ nơ-ron |
| PE | Positional Encoding | Mã hóa vị trí |
| PSNR | Peak Signal-to-Noise Ratio | Tỉ số tín hiệu cực đại trên nhiễu |
| SDF | Signed Distance Function | Hàm khoảng cách có dấu |
| SfM | Structure-from-Motion | Khôi phục cấu trúc ba chiều từ chuyển động của camera |
| SH | Spherical Harmonics | Hàm điều hòa cầu |
| SIGGRAPH | Special Interest Group on Computer Graphics | Hội nghị quốc tế về đồ họa máy tính |
| SSIM | Structural Similarity Index Measure | Độ đo tương đồng cấu trúc giữa hai ảnh |
| TPU | Tensor Processing Unit | Bộ xử lý chuyên dụng cho tính toán tensor của Google |

---

# DANH MỤC KÝ HIỆU

| Ký hiệu | Ý nghĩa |
|---|---|
| **x** | Vị trí một điểm trong không gian ba chiều, viết đầy đủ là (x, y, z) |
| **d** | Vector đơn vị chỉ hướng nhìn, tương đương cặp góc (theta, phi) |
| **o** | Gốc tia, trùng với tâm camera trong hệ tọa độ thế giới |
| t | Tham số thực xác định vị trí trên tia theo công thức r(t) = o + t·d |
| t_n, t_f | Cận gần và cận xa của đoạn tia được lấy mẫu |
| r(t) | Điểm trên tia ứng với tham số t |
| sigma | Density, hiểu là xác suất vi phân để tia kết thúc tại điểm đang xét |
| **c** | Màu phát xạ tại một điểm, gồm ba thành phần đỏ, lục, lam |
| T(t) | Transmittance tích lũy, xác suất tia đi từ cận gần tới t mà không bị hấp thụ |
| alpha_i | Độ chặn sáng của đoạn thứ i trên tia |
| delta_i | Khoảng cách giữa hai điểm mẫu liên tiếp |
| gamma(·) | Hàm positional encoding |
| L | Số mức tần số dùng trong positional encoding |
| mu, Sigma | Trung bình và ma trận hiệp phương sai của phân phối Gaussian xấp xỉ hình nón cụt |
| Theta | Toàn bộ tham số của mạng nơ-ron, được tối ưu trong giai đoạn học |
| **K** | Ma trận nội tại của camera, kích thước 3x3, chứa tiêu cự và điểm chính |
| **R** | Ma trận xoay của camera, kích thước 3x3 |
| **C** | Tọa độ tâm camera trong hệ tọa độ thế giới |
| f_x, f_y | Tiêu cự theo trục ngang và trục dọc, tính bằng đơn vị điểm ảnh |
| c_x, c_y | Tọa độ điểm chính trên mặt phẳng ảnh |
| C(r) | Màu kết xuất của tia r |
| L_recon | Thành phần mất mát tái tạo, so sánh màu kết xuất với màu thật |

> Quy ước: ký hiệu in đậm là đại lượng vector hoặc ma trận, ký hiệu thường là đại lượng vô hướng.

---

# TÓM TẮT

> Viết sau cùng, khoảng 200 từ, theo bốn ý: bối cảnh bài toán, khoảng trống nghiên cứu, việc nhóm đã thực hiện, kết quả cụ thể đạt được.

---
