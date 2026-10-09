<!-- BÁO CÁO ĐỒ ÁN - FILE CHÍNH
     Viết dần theo dàn ý tại 06-BaoCao/dan-y-bao-cao.md
     Trình bày theo 06-BaoCao/quy-dinh-trinh-bay.md (rút từ Thesis_Template.pdf)
     Xuất .docx bằng script md2docx
     Trạng thái: đang viết Phần Mở Đầu -->

# ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH

## TRƯỜNG ĐẠI HỌC KHOA HỌC TỰ NHIÊN

### KHOA CÔNG NGHỆ THÔNG TIN

Bùi Văn Thiên (trưởng nhóm) - Nguyễn Minh Khoa

# XÂY DỰNG ỨNG DỤNG KẾT XUẤT ẢNH VỚI GÓC NHÌN TÙY Ý DỰA VÀO DÃY ẢNH 2D CHO TRƯỚC

## Tìm hiểu mô hình NeRF và NeRF cải tiến

ĐỒ ÁN MÔN HỌC ĐỒ HỌA MÁY TÍNH

Thành phố Hồ Chí Minh, năm 2026

---

# ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH

## TRƯỜNG ĐẠI HỌC KHOA HỌC TỰ NHIÊN

### KHOA CÔNG NGHỆ THÔNG TIN

Bùi Văn Thiên (trưởng nhóm) - 24120138

Nguyễn Minh Khoa - 24120073

# XÂY DỰNG ỨNG DỤNG KẾT XUẤT ẢNH VỚI GÓC NHÌN TÙY Ý DỰA VÀO DÃY ẢNH 2D CHO TRƯỚC

## Tìm hiểu mô hình NeRF và NeRF cải tiến

ĐỒ ÁN MÔN HỌC ĐỒ HỌA MÁY TÍNH

Giảng viên hướng dẫn: PGS.TS Lý Quốc Ngọc

Lớp: Đồ Họa Máy Tính CQ2024/23

Thành phố Hồ Chí Minh, năm 2026

---

# LỜI CẢM ƠN

Nhóm xin gửi lời cảm ơn tới PGS.TS Lý Quốc Ngọc, giảng viên hướng dẫn môn Đồ Họa Máy Tính. Thầy đã giao đề tài, cung cấp tài liệu hướng dẫn về cách trình bày báo cáo cũng như quy trình thực hiện đồ án, và chỉ ra những lỗi thường gặp mà sinh viên hay mắc phải khi làm nghiên cứu ứng dụng. Phần hướng dẫn về các lỗi thường gặp giúp nhóm xác định được trục tổ chức của báo cáo ngay từ đầu, thay vì viết xong mới phát hiện thiếu sót.

Nhóm cũng cảm ơn các tác giả của những công trình được khảo sát trong báo cáo này. Toàn bộ nội dung kỹ thuật được trình bày đều dựa trên các bài báo đã công bố tại những hội nghị và tạp chí chuyên ngành, và phần lớn các nhóm tác giả đều công khai mã nguồn cùng dữ liệu thử nghiệm. Nếu không có sự chia sẻ đó, việc cài đặt lại và kiểm chứng kết quả trong Chương 4 sẽ không thực hiện được trong khuôn khổ một đồ án môn học.

Do hạn chế về thời gian và kinh nghiệm, báo cáo chắc chắn còn thiếu sót. Nhóm mong nhận được góp ý của thầy để hoàn thiện.

---

# ĐỀ CƯƠNG CHI TIẾT

**Tên đề tài:** XÂY DỰNG ỨNG DỤNG KẾT XUẤT ẢNH VỚI GÓC NHÌN TÙY Ý DỰA VÀO DÃY ẢNH 2D CHO TRƯỚC

**Giảng viên hướng dẫn:** PGS.TS Lý Quốc Ngọc

**Sinh viên thực hiện:** Bùi Văn Thiên - 24120138 (trưởng nhóm), Nguyễn Minh Khoa - 24120073

**Lớp:** Đồ Họa Máy Tính CQ2024/23

**Thể loại:** Nghiên cứu, có ứng dụng demo

**Thời gian thực hiện:** [điền ngày bắt đầu] tới [điền ngày kết thúc]

**Nội dung đề tài:**

> Viết sau khi chốt phạm vi: mô tả bài toán, mục tiêu, phương pháp chọn trình bày
> là Mip-NeRF 360, cách tiếp cận và kết quả mong đợi.

**Các mốc thời gian nghiên cứu và phân công:**

Nguyên tắc chia việc là hai hướng song song, gồm hướng lý thuyết và viết báo cáo, và hướng cài đặt và thực nghiệm. Chương 3 là trọng tâm nên cả hai thành viên cùng tham gia.

| Tuần | Bùi Văn Thiên - 24120138 (trưởng nhóm) | Nguyễn Minh Khoa - 24120073 | Mốc kiểm tra |
|---|---|---|---|
| 1 | Đọc ba survey, viết mục 1.3 gồm framework và ẩn số từng công đoạn | Dựng môi trường Colab, chạy thử bộ dữ liệu mẫu | Phải có ảnh kết xuất đầu tiên |
| 2 | Viết Chương 2 mục 2.1 đến 2.3 theo khuôn bốn công đoạn | Chạy thành công TN1 trên bộ dữ liệu chuẩn | Có kết quả TN1 |
| 3 | Viết mục 2.4 và 2.5 gồm bảng so sánh theo công đoạn và bảng khuyết điểm tồn đọng, kèm Chương 1 | Đọc công trình Mip-NeRF 2021, viết mục 3.2 | Nộp giảng viên duyệt dàn ý và Chương 1, 2 |
| 4 | Viết Chương 3 mục 3.0 và 3.1 | Chụp dữ liệu thật, chạy COLMAP | Có bộ dữ liệu tự chụp đã xử lý |
| 5 | Viết tiếp mục 3.1 | Huấn luyện TN2 trên bộ dữ liệu tự chụp | Có kết quả TN2 |
| 6 | Viết mục 3.3 | Chạy TN3 so sánh với phương pháp đối chứng | Xong bản nháp Chương 3 |
| 7 | Viết mục 3.4 gồm hai sơ đồ học và kiểm thử, kèm mục 3.5 | Chạy TN4 nghiên cứu loại trừ, dựng video minh họa | Đủ dữ liệu cho Chương 4 |
| 8 | Viết Chương 4 mục 4.1 đến 4.3 | Tổng hợp bảng kết quả, chuẩn bị hình ảnh so sánh | Xong nửa đầu Chương 4 |
| 9 | Viết mục 4.4 gồm độ đo và quan hệ mất mát với độ đo, kèm mục 4.5 đến 4.7 | Hỗ trợ phân tích kết quả, viết mục 4.6.3 | Xong Chương 4 |
| 10 | Viết Chương 5, phần mở đầu và tài liệu tham khảo | Làm slide, chuẩn bị phụ lục | Bản báo cáo đầy đủ |
| 11 | Rà soát báo cáo theo bảng kiểm trước khi nộp | Hoàn thiện slide, tập thuyết trình | Bản hoàn chỉnh |
| 12 | Dự phòng, sửa theo góp ý | Dự phòng, tập thuyết trình | Nộp và bảo vệ |

**Ý kiến của giảng viên hướng dẫn:**

**Chữ ký của giảng viên hướng dẫn:**

**Chữ ký của sinh viên:**

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

<!-- RÀ LẠI TRƯỚC KHI NỘP: quy định của Khoa (mục 2.4) nhắc hai lần là không
     được lạm dụng viết tắt, chỉ giữ những từ thực sự xuất hiện nhiều lần.
     Sau khi viết xong toàn bộ nội dung, đếm số lần xuất hiện của từng mục
     dưới đây; mục nào dùng dưới khoảng năm lần thì bỏ khỏi bảng và viết
     đầy đủ trong thân bài. Các mục nghi ngờ: NDC, PE, SDF, SH, TPU, MSE,
     và nhóm tên hội nghị CVPR, ECCV, ICCV, SIGGRAPH. -->

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

# CHƯƠNG 1. GIỚI THIỆU

## 1.1. Ý nghĩa khoa học của chủ đề

> Chưa viết. Trạng thái `[Một phần]` trong dàn ý, cần đọc thêm ba khảo sát ở
> `03-Reference/Survey/` trước khi viết.

## 1.2. Ý nghĩa ứng dụng của chủ đề

> Chưa viết. Trạng thái `[Chưa có]` trong dàn ý.

## 1.3. Phát biểu bài toán

<!-- Trích dẫn trong mục này tạm ghi dạng (Tác giả, năm). Chuyển sang số hiệu
     ngoặc vuông sau khi lập xong DANH MỤC TÀI LIỆU THAM KHẢO ở cuối báo cáo. -->

Bài toán đặt ra trong đồ án là tổng hợp góc nhìn mới: cho trước một tập ảnh hai
chiều chụp một cảnh tĩnh từ nhiều vị trí camera khác nhau, cần xây dựng một hệ
thống tính toán được ảnh của cảnh đó tại một góc nhìn bất kỳ, kể cả góc nhìn
không xuất hiện trong tập ảnh ban đầu. Nói cách khác, hệ thống phải học được
một biểu diễn của cảnh từ các ảnh quan sát được, rồi dùng biểu diễn đó để suy
ra nội dung hình ảnh tại những vị trí camera chưa từng quan sát.

Mục này trình bày phát biểu trên theo năm nội dung cụ thể: đầu vào và đầu ra
của hệ thống, khung xử lý chung gồm bốn công đoạn, ẩn số cần tìm trong từng
công đoạn, các tác vụ thực thi được, và tập dữ liệu dùng để thử nghiệm.

### 1.3.1. Đầu vào và đầu ra của hệ thống

Đầu vào là tập ảnh màu hai chiều `{I_1, I_2, ..., I_N}`, với N thường trong
khoảng 20 tới 100 ảnh. Tập ảnh này phải thỏa hai ràng buộc. Thứ nhất, cảnh phải
tĩnh trong suốt quá trình chụp: vật thể không di chuyển và điều kiện ánh sáng
không đổi giữa các ảnh, vì hệ thống không có cơ chế tách biệt chuyển động của
vật thể khỏi chuyển động của camera. Thứ hai, các ảnh liên tiếp phải có độ
chồng lấp đủ lớn, vì bước ước lượng tham số camera ở công đoạn 1 cần nhận diện
cùng một điểm vật lý xuất hiện trên nhiều ảnh khác nhau.

Đầu ra là ảnh màu được kết xuất tại một tư thế camera tùy ý, kể cả tư thế không
xuất hiện trong tập đầu vào. Hai dạng đầu ra mở rộng thường gặp là chuỗi ảnh
liên tiếp ghép thành video quay quanh cảnh, và mô hình hình học ba chiều dạng
lưới tam giác trích xuất từ biểu diễn đã học.

### 1.3.2. Khung xử lý chung gồm bốn công đoạn

Mọi phương pháp giải bài toán này, bất kể lựa chọn kỹ thuật cụ thể, đều đi qua
bốn công đoạn xử lý theo trình tự sau.

```
                         +------------------------------------+
                         |                                    |
   Tập ảnh 2D            v                                    |
       |          +-------------+    +-------------+    +-----+----+
       +--------->| CD1: Uoc    |--->| CD2: Bieu   |--->| CD3: Ket |---> Anh goc
                  | luong tham  |    | dien canh   |    | xuat anh |     nhin moi
                  | so camera   |    | 3D          |    +-----+----+
                  +-------------+    +-------------+          |
                                            ^                  |
                                            |     +------------v-------+
                                            +-----+ CD4: Toi uu hoa    |
                                                  | bieu dien          |
                                                  +--------------------+
```

*Hình 1.2. Khung xử lý chung gồm bốn công đoạn, mũi tên nét liền chỉ luồng dữ
liệu thuận, mũi tên hồi tiếp chỉ vòng lặp tối ưu ở công đoạn 4.*

Bảng 1.1 mô tả nhiệm vụ của từng công đoạn ở mức tổng quát, chưa gắn với một kỹ
thuật cụ thể nào. Việc giữ mức mô tả tổng quát ở đây có chủ đích: Chương 2 sẽ
khảo sát nhiều kỹ thuật khác nhau cho cùng một công đoạn, nên khung xử lý dùng
làm trục so sánh phải trung lập với lựa chọn kỹ thuật.

**Bảng 1.1. Mô tả bốn công đoạn ở mức tổng quát**

| Công đoạn | Nhiệm vụ | Các hướng giải pháp khả dĩ |
|---|---|---|
| CĐ1 | Xác định mỗi ảnh được chụp từ vị trí nào, hướng nào, với thông số ống kính ra sao | Structure-from-Motion, SLAM, cảm biến gắn kèm, hoặc tư thế có sẵn kèm theo dữ liệu tổng hợp |
| CĐ2 | Xây dựng cấu trúc dữ liệu hoặc hàm số mô tả cảnh, truy vấn được tại một điểm bất kỳ trong không gian | Biểu diễn tường minh như lưới tam giác, voxel, đám mây điểm, Gaussian; hoặc biểu diễn ẩn như mạng nơ-ron |
| CĐ3 | Từ biểu diễn và một góc nhìn cho trước, sinh ra ảnh hai chiều | Rasterization, ray tracing, ray marching kết hợp volume rendering, splatting |
| CĐ4 | Điều chỉnh tham số của biểu diễn sao cho ảnh sinh ra khớp với ảnh quan sát được | Hạ gradient khi quy trình khả vi, tối ưu phi tuyến, hoặc lấp đầy trực tiếp từ dữ liệu quan sát |

### 1.3.3. Ẩn số cần tìm trong từng công đoạn

Mỗi công đoạn ở Bảng 1.1 nhận một số dữ kiện làm đầu vào và phải giải ra một ẩn
số cụ thể. Bảng 1.2 liệt kê rõ dữ kiện đã cho, ẩn số cần tìm, và ràng buộc dùng
để giải ra ẩn số đó trong từng công đoạn.

**Bảng 1.2. Dữ kiện đã cho và ẩn số cần tìm**

| Công đoạn | Dữ kiện đã cho | Ẩn số cần tìm | Ràng buộc dùng để giải |
|---|---|---|---|
| CĐ1 | Tập ảnh `{I_1, ..., I_N}` | Với mỗi ảnh i: ma trận nội tại K_i, ma trận xoay R_i, tâm camera C_i; kèm tập điểm ba chiều thưa `{X_j}` | Cùng một điểm vật lý xuất hiện trên nhiều ảnh phải chiếu về đúng vị trí quan sát được, tức sai số tái chiếu nhỏ nhất |
| CĐ2 | Phạm vi không gian của cảnh; dạng biểu diễn đã chọn | Tham số Theta của biểu diễn. Tùy dạng biểu diễn, Theta là trọng số mạng, giá trị trên lưới voxel, hoặc tập tham số của các primitive | Theta phải sinh ra ảnh khớp với mọi ảnh quan sát được trong tập huấn luyện |
| CĐ3 | Biểu diễn đã có tham số Theta và tư thế camera cần kết xuất | Không có ẩn số phải học ở công đoạn này. Ẩn số mang tính thiết kế gồm chọn thuật toán kết xuất nào và lấy bao nhiêu điểm mẫu | Quy trình kết xuất phải khả vi nếu công đoạn 4 dùng hạ gradient |
| CĐ4 | Cặp ảnh kết xuất và ảnh thật tương ứng | Tham số Theta tối ưu, chính là ẩn số của CĐ2 được giải tại đây | Tối thiểu hóa hàm mất mát giữa ảnh kết xuất và ảnh thật |

Công đoạn 2 và công đoạn 4 gắn chặt với nhau theo hai chiều: công đoạn 2 quyết
định dạng của ẩn số Theta, còn công đoạn 4 quyết định cách tìm ra giá trị đó.
Chọn dạng biểu diễn ở công đoạn 2 vì vậy luôn ràng buộc luôn phương pháp tối ưu
khả dụng ở công đoạn 4. Đây cũng là chỗ các phương pháp khảo sát ở Chương 2
khác nhau nhiều nhất.

### 1.3.4. Các tác vụ cần thực hiện

Bốn công đoạn ở trên cụ thể hóa thành bốn tác vụ tính toán nối tiếp nhau. Tác vụ
thứ nhất nhận tập ảnh đầu vào và trả về tham số camera K_i, R_i, C_i cho từng
ảnh cùng một tập điểm ba chiều thưa. Tác vụ thứ hai khởi tạo một biểu diễn cảnh
ba chiều có phạm vi không gian bao trùm tập điểm thưa vừa thu được. Tác vụ thứ
ba, với biểu diễn đã khởi tạo và một tư thế camera bất kỳ, tính ra ảnh hai chiều
tương ứng. Tác vụ thứ tư so sánh ảnh tính được ở tác vụ ba với ảnh thật tại cùng
tư thế, rồi cập nhật tham số của biểu diễn; tác vụ ba và tác vụ tư lặp lại nhiều
vòng cho tới khi sai số đủ nhỏ.

### 1.3.5. Tập dữ liệu thử nghiệm chuẩn

Ba bộ dữ liệu ở Bảng 1.3 được dùng phổ biến nhất để thử nghiệm bài toán này.
Mỗi bộ khác nhau về số lượng cảnh và về loại thách thức mà phương pháp phải xử
lý được.

**Bảng 1.3. Các bộ dữ liệu chuẩn của bài toán**

| Bộ dữ liệu | Số cảnh | Loại | Thách thức chứa trong dữ liệu |
|---|---|---|---|
| Realistic Synthetic 360°, còn gọi là Blender dataset (Mildenhall và cộng sự, 2020) | 8 vật thể | Tổng hợp, quan sát 360 độ | Vật liệu phản chiếu không tuân theo mô hình Lambert, hình học phức tạp như dây chằng tàu thủy ở cảnh Ship và bánh răng ở cảnh Lego |
| Real Forward-Facing (Mildenhall và cộng sự, 2020, trong đó 5 trên 8 cảnh kế thừa từ Mildenhall và cộng sự, 2019) | 8 cảnh | Thật, hướng về phía trước | Nhiễu ảnh thật, nội dung trải từ gần tới xa, vùng bị che khuất một phần |
| Mip-NeRF 360 (Barron và cộng sự, 2022) | 9 cảnh, gồm 5 ngoài trời và 4 trong nhà | Thật, quan sát 360 độ không giới hạn | Nội dung tồn tại ở khoảng cách bất kỳ, chênh lệch tỉ lệ lớn giữa vật thể gần và nền xa, một số vùng chỉ được quan sát bởi rất ít ảnh |

## 1.4. Đóng góp của báo cáo

> Chưa viết. Trạng thái `[Một phần]` trong dàn ý, viết sau khi hoàn thành
> Chương 3 và Chương 4 để liệt kê đóng góp đúng với những gì thực sự làm được.

## 1.5. Bố cục báo cáo

> Chưa viết. Trạng thái `[Chưa có]` trong dàn ý, viết sau cùng khi đã chốt số
> trang thật của từng chương.

---

# TÓM TẮT

> Viết sau cùng, khoảng 200 từ, theo bốn ý: bối cảnh bài toán, khoảng trống nghiên cứu, việc nhóm đã thực hiện, kết quả cụ thể đạt được.

---
