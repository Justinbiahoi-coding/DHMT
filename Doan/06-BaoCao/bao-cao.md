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

# TÓM TẮT

> Viết sau cùng, khoảng 200 từ, theo bốn ý: bối cảnh bài toán, khoảng trống nghiên cứu, việc nhóm đã thực hiện, kết quả cụ thể đạt được.

---

---

# CHƯƠNG 1. GIỚI THIỆU

## 1.1. Ý nghĩa khoa học của chủ đề

Con người chỉ cần nhìn một vật từ vài góc là hình dung được hình dạng ba chiều
của nó, trong khi máy tính gặp khó khăn vì ảnh hai chiều đã mất thông tin độ
sâu: mỗi điểm ảnh tương ứng với vô số điểm ba chiều khả dĩ. Bài toán tổng hợp
góc nhìn mới chính là khôi phục khả năng này cho máy tính.

Các hướng tiếp cận trước NeRF đều vướng một rào cản riêng. Nội suy light field
tái tạo được ảnh chân thực, nhưng chỉ khi có một lượng ảnh lấy mẫu rất dày làm
đầu vào. Biểu diễn lưới tam giác có thể tối ưu bằng rasterizer khả vi, nhưng
việc tối ưu dựa trên tái chiếu ảnh thường rơi vào cực tiểu địa phương, và còn
đòi hỏi một lưới mẫu có sẵn với tô pô cố định, thứ thường không có sẵn với
cảnh thật không ràng buộc. Biểu diễn lưới voxel tránh được vấn đề đó nhưng chi
phí lưu trữ tăng theo lập phương của độ phân giải: nếu mỗi chiều chia thành N
ô thì tổng số voxel là N³, nên muốn ảnh nét hơn thì bộ nhớ cần tăng rất nhanh.
Biểu diễn bề mặt ẩn dưới dạng hàm khoảng cách có dấu tránh được cả hai vấn đề
trên, nhưng lại bị giới hạn bởi yêu cầu có sẵn dữ liệu hình học ba chiều xác
thực để huấn luyện, thứ hiếm khi có đối với cảnh thật.

NeRF khắc phục đồng thời các hạn chế trên. Mô hình tự giám sát, chỉ cần ảnh
màu thông thường kèm tư thế camera để huấn luyện, không đòi hỏi dữ liệu ba
chiều xác thực. Biểu diễn ẩn dưới dạng trọng số mạng nơ-ron nén toàn cảnh
xuống còn khoảng 5 megabyte, nhỏ hơn 3000 lần so với dung lượng lưới voxel của
phương pháp LLFF cho cùng một cảnh. Và đây là phương pháp đầu tiên tạo ra ảnh
tổng hợp góc nhìn mới với độ phân giải cao, đạt chất lượng ảnh chân thực cho
cảnh thật chụp ngoài đời.

NeRF mở ra một nhánh nghiên cứu phát triển nhanh. Tính tới tháng 10 năm 2022,
paper gốc đã có hơn 1300 trích dẫn, với hơn 150 công trình kế thừa công bố
trong hai năm. Nhánh nghiên cứu này tiếp tục phát triển cho tới khi 3D
Gaussian Splatting xuất hiện năm 2023, trở thành một hướng cạnh tranh trực
tiếp dựa trên biểu diễn tường minh thay vì mạng nơ-ron ẩn.

## 1.2. Ý nghĩa ứng dụng của chủ đề

<!-- Ba nguồn mới dùng trong mục này (Croce và cộng sự 2024, Mega-NeRF 2022,
     Vachha 2024) chưa có file PDF trong 03-Reference/. Quyết định tải về hay
     giữ nguyên dạng trích tên tác giả vẫn đang chờ. -->

Khả năng dựng lại cảnh ba chiều chỉ từ ảnh chụp thông thường, không cần thiết
bị quét ba chiều chuyên dụng, khiến NeRF được ứng dụng trong nhiều lĩnh vực.
Nghiên cứu của Gao và cộng sự ghi nhận NeRF đã tìm được chỗ đứng trong robot
học, lập bản đồ đô thị, điều hướng tự động và thực tế ảo, thực tế tăng cường.

Dựng môi trường ba chiều cho thực tế ảo và thực tế tăng cường bằng phương
pháp thủ công tốn nhiều công sức của người dựng mô hình. Nghiên cứu của Gao
và cộng sự xác nhận đây là một trong những lĩnh vực NeRF đã được ứng dụng,
nhờ khả năng tạo nội dung ba chiều trực tiếp từ ảnh chụp mà không cần mô hình
hóa tay.

Nhiều hiện vật và di tích trong công tác số hóa di sản không được phép tiếp
xúc trực tiếp hoặc chỉ chụp được số lượng ảnh hạn chế, vì nguy cơ hư hại.
Nghiên cứu của Croce và cộng sự so sánh NeRF với phương pháp đo ảnh truyền
thống trên ba hiện vật di sản, trong đó có bức tượng Terpsichore, cho thấy
khi dữ liệu đầu vào ít hoặc độ phân giải thấp, NeRF giữ được độ hoàn chỉnh và
mô tả vật liệu tốt hơn.

Trong thương mại điện tử, người mua muốn xem sản phẩm từ mọi góc trước khi
quyết định mua, nhưng quét ba chiều từng sản phẩm bằng thiết bị chuyên dụng
không khả thi ở quy mô lớn. Theo một bài phân tích công nghệ trên Unite.AI,
một số nền tảng thương mại điện tử đã thử nghiệm NeRF để dựng mô hình xem từ
mọi góc chỉ từ vài ảnh chụp sản phẩm, dù bài viết cũng lưu ý thời gian kết
xuất thời gian thực vẫn là rào cản với ứng dụng cần phản hồi tức thì.

Khách hàng bất động sản và du lịch ở xa cần hình dung không gian thật trước
khi tới tận nơi, đôi khi với quy mô lớn như toàn bộ tòa nhà hay một khu phố.
Nghiên cứu Mega-NeRF của Turki, Ramanan và Satyanarayanan xây dựng NeRF cho
cảnh quy mô tòa nhà và khu phố từ ảnh chụp bằng drone, cho phép bay lượn
tương tác qua không gian ba chiều được dựng lại.

Việc dựng bản đồ ba chiều môi trường xung quanh cho robot và xe tự hành
thường dựa vào cảm biến LiDAR có giá thành cao. Gao và cộng sự xác nhận robot
học và điều hướng tự động nằm trong số những lĩnh vực NeRF đã được ứng dụng,
hướng tới dựng bản đồ từ camera rẻ hơn, dù NeRF chưa thay thế hoàn toàn LiDAR
ở ứng dụng đòi hỏi độ chính xác cao.

Chèn vật thể ảo vào cảnh quay thật cho điện ảnh và kỹ xảo đòi hỏi mô hình ba
chiều của bối cảnh kèm thông tin ánh sáng thật tại hiện trường. Theo khảo sát
của Vachha về việc dùng NeRF trong kỹ xảo, các công cụ như Nerfstudio và
Instant-NGP đã giúp NeRF dễ tiếp cận hơn với người làm kỹ xảo, và một số công
ty tích hợp NeRF vào Unreal Engine để kết xuất thời gian thực trong sản xuất
ảo.

Một ví dụ triển khai thực tế là tính năng Immersive View của Google Maps,
dùng NeRF để dựng mô hình ba chiều của địa điểm từ ảnh Street View và ảnh
chụp trên không, chính thức ra mắt tại năm thành phố lớn vào tháng 2 năm 2023
gồm London, Los Angeles, New York, San Francisco và Tokyo.

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

Bảy bộ dữ liệu ở Bảng 1.3 là các chuẩn phổ biến nhất để thử nghiệm bài toán
tổng hợp góc nhìn mới, xếp theo mức độ phức tạp tăng dần: từ vật thể tổng hợp
hình học đơn giản, tới cảnh thật có giới hạn, tới cảnh thật không giới hạn.
Mỗi bộ khác nhau về số lượng cảnh và về loại thách thức mà phương pháp phải
xử lý được.

**Bảng 1.3. Các bộ dữ liệu chuẩn của bài toán**

| Bộ dữ liệu | Số cảnh | Loại | Thách thức chứa trong dữ liệu |
|---|---|---|---|
| DeepVoxels (Sitzmann và cộng sự, 2019) | 4 vật thể | Tổng hợp, quan sát 360° có giới hạn | Hình học đơn giản, phản xạ khuếch tán hoàn toàn, dùng làm đối chứng dễ để kiểm tra khả năng cơ bản trước khi thử cảnh phức tạp hơn |
| Realistic Synthetic 360°, còn gọi là Blender dataset (Mildenhall và cộng sự, 2020) | 8 vật thể | Tổng hợp, quan sát 360° có giới hạn | Vật liệu phản chiếu không tuân theo mô hình Lambert, hình học phức tạp như dây chằng tàu thủy ở cảnh Ship và bánh răng ở cảnh Lego |
| DTU (Gao và cộng sự, 2022) | 80 cảnh | Thật, chụp bằng robot công nghiệp, quan sát 360° có giới hạn | Điều kiện ánh sáng thay đổi giữa bảy mức chiếu sáng, một số vùng bị che khuất khiến hình học tham chiếu không đầy đủ |
| Real Forward-Facing (Mildenhall và cộng sự, 2020, trong đó 5 trên 8 cảnh kế thừa từ Mildenhall và cộng sự, 2019) | 8 cảnh | Thật, góc nhìn hướng về phía trước | Nhiễu ảnh thật, nội dung trải từ gần tới xa, vùng bị che khuất một phần |
| Tanks and Temples (Knapitsch và cộng sự, 2017) | 21 cảnh, các paper NeRF thường chỉ dùng một vài cảnh trích ra | Thật, quy mô lớn, trong nhà lẫn ngoài trời | Không gian trải rộng, hình học tham chiếu đối chiếu bằng máy quét laser công nghiệp |
| Deep Blending (Hedman và cộng sự, 2018) | 2 cảnh thường dùng trong các paper NeRF | Thật, trong nhà | Hình học và vật liệu phức tạp, từng là thách thức cho các phương pháp kết xuất dựa trên ảnh trước NeRF |
| Mip-NeRF 360 (Barron và cộng sự, 2022) | 9 cảnh, gồm 5 ngoài trời và 4 trong nhà | Thật, quan sát 360° không giới hạn | Nội dung tồn tại ở khoảng cách bất kỳ, chênh lệch tỉ lệ lớn giữa vật thể gần và nền xa, một số vùng chỉ được quan sát bởi rất ít ảnh |

## 1.4. Đóng góp của báo cáo

> Chưa viết. Trạng thái `[Một phần]` trong dàn ý, viết sau khi hoàn thành
> Chương 3 và Chương 4 để liệt kê đóng góp đúng với những gì thực sự làm được.

## 1.5. Bố cục báo cáo

> Chưa viết. Trạng thái `[Chưa có]` trong dàn ý, viết sau cùng khi đã chốt số
> trang thật của từng chương.

---

# CHƯƠNG 2. CÁC CÔNG TRÌNH NGHIÊN CỨU LIÊN QUAN

<!-- Nội dung chương này dựa trên bản nháp của Nguyễn Minh Khoa (report.docx,
     nhánh report trên remote), đã sửa các lỗi phát hiện khi rà soát: lỗi gõ
     "Min-NeRF 360", ký hiệu Theta bị dán lặp dạng LaTeX, một câu sai sự thật
     về phạm vi của NeRF gốc, gạch ngang dài thay bằng dấu hai chấm, và thêm
     trích dẫn cho từng phương pháp. Số liệu Bảng 2.4 đã đối chiếu khớp với
     Bảng 1 của paper Mip-NeRF 360 (2022). -->

## 2.1. Các nhóm phương pháp trước NeRF

Trước khi NeRF ra đời, bài toán tổng hợp hình ảnh từ các góc nhìn mới đã được nghiên cứu thông qua nhiều phương pháp khác nhau. Các phương pháp này sử dụng những cách biểu diễn cảnh và kỹ thuật kết xuất khác nhau, từ lưu trữ thông tin ánh sáng, xây dựng hình học ba chiều, tới học biểu diễn bằng mạng nơ-ron. Khảo sát các phương pháp này giúp làm rõ những hạn chế còn tồn đọng mà NeRF hướng đến để giải quyết.

Light field sử dụng một tập ảnh được chụp từ nhiều góc nhìn khác nhau, với vị trí camera đã biết hoặc được xác định trước. Thay vì xây dựng mô hình hình học ba chiều tường minh, phương pháp lưu trữ thông tin ánh sáng thông qua các mẫu ảnh tại những vị trí và hướng nhìn khác nhau, thường được biểu diễn bằng một hàm bốn chiều. Khi cần tạo ảnh tại một góc nhìn mới, hệ thống lấy mẫu và nội suy thông tin ánh sáng để xác định màu sắc của các pixel trong ảnh đầu ra. Theo Mildenhall và cộng sự, hạn chế chính của phương pháp này là cần các mẫu ảnh đủ dày để tái tạo góc nhìn mới chính xác.

Biểu diễn bằng lưới tam giác thường kết hợp các kỹ thuật tái tạo hình học từ nhiều ảnh, chẳng hạn Structure from Motion và Multi-View Stereo. Hệ thống ước lượng tư thế camera và cấu trúc ba chiều ban đầu, sau đó xây dựng mô hình bề mặt gồm các đỉnh, cạnh và mặt tam giác. Khi kết xuất, các tam giác được chiếu lên mặt phẳng ảnh, kết hợp với thông tin vật liệu, kết cấu và ánh sáng để xác định màu sắc từng pixel. Mildenhall và cộng sự chỉ ra rằng việc tối ưu lưới dựa trên tái chiếu ảnh thường rơi vào cực tiểu địa phương, và còn đòi hỏi một lưới mẫu có sẵn với tô pô cố định, thứ thường không có sẵn với cảnh thật không ràng buộc.

Lưới voxel chia không gian ba chiều thành các ô nhỏ theo ba trục x, y, z. Mỗi voxel lưu trữ thông tin mô tả vùng không gian tương ứng, chẳng hạn màu sắc, mật độ hoặc các đặc trưng phục vụ kết xuất. Khi cần tạo ảnh từ một góc nhìn mới, hệ thống chiếu các tia sáng xuất phát từ camera, lấy mẫu dọc theo từng tia và truy vấn thông tin trong lưới voxel. Hạn chế của phương pháp này là nhu cầu bộ nhớ lớn khi tăng độ phân giải: nếu mỗi chiều có N ô thì tổng số voxel là N³, khiến chi phí lưu trữ và tính toán tăng nhanh.

Bề mặt ẩn biểu diễn bằng mạng nơ-ron sử dụng một hàm được học bởi mạng nơ-ron để mô tả hình học ba chiều. Với các phương pháp dựa trên hàm khoảng cách có dấu, mạng nhận tọa độ một điểm trong không gian và dự đoán khoảng cách có dấu từ điểm đó đến bề mặt, bề mặt được xác định bởi tập hợp các điểm có giá trị bằng không. Theo Mildenhall và cộng sự, hạn chế của hướng tiếp cận này là yêu cầu có sẵn dữ liệu hình học ba chiều xác thực để huấn luyện, thứ hiếm khi có đối với cảnh thật.

NeRF, công bố năm 2020, mở ra một hướng tiếp cận khác cho bài toán tổng hợp góc nhìn mới. Thay vì nội suy trực tiếp các ảnh đã chụp hoặc xây dựng lưới bề mặt tường minh, NeRF dùng mạng nơ-ron để biểu diễn một trường bức xạ liên tục trong không gian ba chiều. Mạng nhận tọa độ không gian và hướng nhìn, dự đoán mật độ thể tích và bức xạ theo hướng tương ứng, rồi đưa các giá trị này vào thuật toán kết xuất thể tích khả vi để tạo ảnh dự đoán. Sai số giữa ảnh dự đoán và ảnh thật được dùng để tối ưu tham số mạng.

Nhờ kết hợp biểu diễn liên tục với kết xuất khả vi, NeRF tổng hợp được các góc nhìn mới với chất lượng cao trong nhiều điều kiện thực nghiệm. Tuy nhiên, phương pháp này không loại bỏ hoàn toàn hạn chế của các hướng tiếp cận trước đó: chi phí huấn luyện và kết xuất vẫn lớn, chất lượng ảnh phụ thuộc vào dữ liệu đầu vào, và biểu diễn mật độ không phải lúc nào cũng cho phép khôi phục hình học bề mặt chính xác. Những hạn chế này tiếp tục thúc đẩy sự phát triển của các mô hình cải tiến như Mip-NeRF và Mip-NeRF 360.

## 2.2. Mô hình NeRF và những hạn chế còn tồn đọng

### 2.2.1. Ánh xạ NeRF vào bốn công đoạn

NeRF thực hiện bài toán tổng hợp góc nhìn mới thông qua bốn công đoạn: ước lượng tham số camera, xây dựng biểu diễn cảnh ba chiều, kết xuất ảnh và tối ưu hóa biểu diễn. Bốn công đoạn này liên hệ chặt chẽ với nhau, trong đó kết quả kết xuất ở công đoạn 3 được dùng để đánh giá và cập nhật biểu diễn ở công đoạn 4.

Công đoạn 1, ước lượng tham số camera: từ tập ảnh hai chiều đầu vào, hệ thống xác định vị trí và hướng nhìn của camera tương ứng với từng ảnh. Với dữ liệu chưa có thông tin camera, NeRF dùng Structure from Motion để tìm các điểm đặc trưng tương ứng giữa các ảnh, ước lượng tham số camera và tái tạo tập điểm ba chiều thưa. Kết quả gồm ma trận nội tại K_i, ma trận xoay R_i, tâm camera C_i và thông tin hình học ban đầu của cảnh.

Công đoạn 2, xây dựng biểu diễn cảnh ba chiều: NeRF biểu diễn cảnh bằng một trường bức xạ liên tục mô hình hóa qua mạng MLP. Mạng nhận tọa độ không gian x = (x, y, z) và hướng nhìn d, sau khi mã hóa vị trí bằng positional encoding, để dự đoán màu sắc c và mật độ thể tích σ. Toàn bộ trọng số mạng ký hiệu là Θ. Khác với phương pháp lưới tam giác cần xây dựng bề mặt tường minh, NeRF học một hàm biểu diễn cảnh và dùng hàm đó để cung cấp thông tin tại các vị trí được truy vấn trong không gian.

Công đoạn 3, kết xuất ảnh: với một tư thế camera xác định, hệ thống tạo các tia sáng tương ứng với từng pixel của ảnh cần kết xuất. Trên mỗi tia, NeRF lấy mẫu nhiều điểm trong khoảng từ mặt phẳng gần t_n đến mặt phẳng xa t_f, đưa các điểm này qua mạng để dự đoán màu sắc và mật độ thể tích, rồi dùng thuật toán kết xuất thể tích kết hợp các giá trị dự đoán dọc theo tia để tính màu cho pixel. NeRF gốc còn dùng lấy mẫu phân cấp: mạng thô xác định phân phối trọng số dọc theo tia, từ đó chọn thêm điểm mẫu cho mạng tinh để cải thiện chất lượng kết xuất.

Công đoạn 4, tối ưu hóa biểu diễn: ảnh kết xuất được so sánh với ảnh thật tương ứng trong tập huấn luyện bằng hàm mất mát, thường là sai số bình phương trung bình giữa các giá trị RGB. Qua kết xuất khả vi, sai số được lan truyền ngược để tính gradient theo tham số mạng Θ, và thuật toán Adam dùng gradient đó để cập nhật trọng số. Quá trình kết xuất, tính mất mát và cập nhật tham số lặp lại nhiều lần cho tới khi đạt điều kiện dừng.

Sau khi huấn luyện, tham số mạng được giữ cố định. Hệ thống nhận một tư thế camera mới, tạo các tia tương ứng và kết xuất để tổng hợp ảnh từ góc nhìn chưa xuất hiện trong tập huấn luyện, đây chính là mục tiêu của NeRF trong bài toán tổng hợp góc nhìn mới.

### 2.2.2. Hạn chế của NeRF

Bảng 2.1 nêu những hạn chế còn tồn đọng của NeRF, xác định rõ hạn chế nằm ở công đoạn nào và nguyên nhân kỹ thuật dẫn tới hạn chế đó.

**Bảng 2.1. Hạn chế của mô hình NeRF**

| Hạn chế | Công đoạn | Nguyên nhân kỹ thuật |
|---|---|---|
| Huấn luyện chậm, mất 1 tới 2 ngày cho mỗi cảnh | CĐ2, CĐ3, CĐ4 | Mạng MLP phải xử lý nhiều điểm mẫu trên mỗi tia camera, huấn luyện còn phải tính gradient và cập nhật trọng số qua nhiều vòng lặp |
| Kết xuất ảnh chậm, chưa đáp ứng thời gian thực | CĐ3 | Mạng thô xử lý 64 điểm mẫu mỗi tia, mạng tinh xử lý 192 điểm gồm 64 điểm thô và 128 điểm bổ sung, tổng cộng 256 lượt đánh giá qua hai mạng trên mỗi tia |
| Xuất hiện răng cưa khi đổi độ phân giải hoặc tỉ lệ quan sát | CĐ3 | NeRF dùng một tia lý tưởng cho mỗi pixel, chưa mô hình hóa vùng không gian mà pixel thực tế bao phủ |
| Kém hiệu quả khi biểu diễn cảnh 360 độ không giới hạn | CĐ2, CĐ3 | Cách tham số hóa không gian và lấy mẫu của NeRF gốc chưa phân bổ hiệu quả cho cảnh trải dài từ gần đến rất xa |
| Phụ thuộc độ chính xác của tư thế camera | CĐ1 | Nếu vị trí hoặc hướng camera bị ước lượng sai, các tia có thể không khớp với nội dung ảnh quan sát, làm giảm chất lượng tái tạo |

Về hạn chế thứ tư, cần nói rõ hơn phạm vi áp dụng của NeRF gốc. NeRF giải quyết được hai dạng cảnh: cảnh vật thể quan sát 360 độ trong phạm vi giới hạn, và cảnh hướng về phía trước thông qua biến đổi tọa độ NDC. Điều NeRF chưa giải quyết được là cảnh 360 độ không giới hạn, nơi camera có thể hướng theo bất kỳ phương nào và nội dung tồn tại ở khoảng cách bất kỳ, đúng như vấn đề mà Mip-NeRF 360 đặt ra.

## 2.3. Các giải pháp tiên tiến

Bảng 2.2 tổng hợp các phương pháp tiêu biểu phát triển từ nền tảng của NeRF, đồng thời chỉ ra hạn chế của NeRF mà từng phương pháp hướng tới giải quyết. Các phương pháp được phân tích theo bốn công đoạn: ước lượng tham số camera, xây dựng biểu diễn cảnh, kết xuất ảnh và tối ưu hóa.

**Bảng 2.2. Các phương pháp tiên tiến và phạm vi tác động**

| Phương pháp | Hạn chế được giải quyết | Công đoạn tác động |
|---|---|---|
| Instant-NGP (Müller và cộng sự, SIGGRAPH 2022) | Giảm thời gian huấn luyện và kết xuất | CĐ2: thay positional encoding bằng hash encoding, cho phép dùng MLP nhỏ hơn. CĐ3: dùng occupancy grid để bỏ qua vùng không gian trống khi lấy mẫu tia |
| Plenoxels (Fridovich-Keil và cộng sự, CVPR 2022) | Tăng tốc huấn luyện | CĐ2: bỏ hẳn mạng nơ-ron, thay bằng lưới voxel thưa lưu mật độ và hệ số cầu điều hòa |
| TensoRF (Chen và cộng sự, ECCV 2022) | Tăng tốc huấn luyện | CĐ2: phân rã tensor biểu diễn cảnh thành các thành phần hạng thấp. CĐ3: kết hợp các thành phần tensor để truy vấn đặc trưng và kết xuất |
| Mip-NeRF (Barron và cộng sự, ICCV 2021) | Khắc phục hiện tượng răng cưa | CĐ2: dùng Integrated Positional Encoding, tích phân mã hóa vị trí trên phân phối Gaussian đại diện vùng không gian lấy mẫu. CĐ3: thay tia bằng hình nón cụt có xét vùng không gian pixel bao phủ |
| NeRF++ (Zhang và cộng sự, 2020) | Biểu diễn cảnh 360 độ không giới hạn | CĐ2: phân tách cảnh thành vùng tiền cảnh bên trong khối cầu đơn vị và vùng nền bên ngoài, dùng tham số hóa phù hợp cho vùng nền |
| Mip-NeRF 360 (Barron và cộng sự, CVPR 2022) | Khắc phục răng cưa và biểu diễn cảnh 360 độ không giới hạn | CĐ2: tham số hóa phi tuyến ánh xạ không gian không giới hạn vào miền hữu hạn. CĐ3: dùng mạng đề xuất hướng dẫn lấy mẫu phân cấp. CĐ4: dùng interlevel loss và distortion loss |
| 3D Gaussian Splatting (Kerbl và cộng sự, SIGGRAPH 2023) | Tăng tốc kết xuất | CĐ2: biểu diễn cảnh bằng Gaussian ba chiều tường minh. CĐ3: chiếu Gaussian lên mặt phẳng ảnh và dùng splatting thay cho truy vấn MLP dọc tia. CĐ4: tối ưu tham số Gaussian kèm cơ chế thêm, tách, loại bỏ Gaussian |

## 2.4. Bảng so sánh các giải pháp theo công đoạn

Bảng 2.3 so sánh các phương pháp theo đúng bốn công đoạn, làm rõ cách mỗi phương pháp tổ chức dữ liệu đầu vào, biểu diễn cảnh, kết xuất ảnh và cập nhật tham số.

**Bảng 2.3. So sánh các phương pháp theo bốn công đoạn**

| Phương pháp | CĐ1: Ước lượng tư thế | CĐ2: Biểu diễn cảnh | CĐ3: Kết xuất | CĐ4: Tối ưu |
|---|---|---|---|---|
| NeRF (2020) | Structure-from-Motion | MLP 8 lớp ẩn, 256 đơn vị mỗi lớp, positional encoding cho vị trí và hướng nhìn | Tạo tia camera, lấy mẫu phân cấp, kết xuất thể tích: 64 điểm thô, 192 điểm cho mạng tinh | Mất mát bình phương trung bình RGB, lan truyền ngược và Adam |
| NeRF++ (2020) | Structure-from-Motion | Hai MLP cho vùng trong và ngoài khối cầu, vùng ngoài dùng tham số hóa nghịch đảo bán kính | Kết xuất thể tích cho hai vùng, kết hợp đóng góp ánh sáng theo thứ tự dọc tia | Tối ưu bằng sai số tái tạo ảnh RGB |
| Mip-NeRF (2021) | Structure-from-Motion | MLP kết hợp Integrated Positional Encoding, biểu diễn vùng lấy mẫu bằng phân phối Gaussian | Kết xuất hình nón cụt thay tia mảnh, kết hợp lấy mẫu phân cấp | Tối ưu theo sai số RGB, huấn luyện đa tỉ lệ để giám sát đa tỉ lệ |
| Plenoxels (2022) | Structure-from-Motion | Lưới voxel thưa lưu mật độ và hệ số cầu điều hòa, không dùng MLP | Nội suy giá trị voxel và kết xuất thể tích dọc tia | Tối ưu trực tiếp giá trị voxel bằng gradient |
| Instant-NGP (2022) | Structure-from-Motion | Hash grid đa độ phân giải kết hợp MLP nhỏ | Kết xuất thể tích kết hợp occupancy grid bỏ qua vùng trống | Tối ưu đặc trưng hash và tham số MLP bằng Adam |
| TensoRF (2022) | Structure-from-Motion | Biểu diễn trường bức xạ bằng tensor đặc trưng, phân rã hạng thấp | Truy vấn đặc trưng từ các thành phần tensor, kết xuất thể tích | Tối ưu các thành phần tensor bằng mất mát tái tạo ảnh kèm chính quy hóa |
| Mip-NeRF 360 (2022) | Structure-from-Motion | Kế thừa IPE của Mip-NeRF, kết hợp scene contraction xử lý không gian không giới hạn | Kết xuất hình nón cụt, lấy mẫu phân cấp hướng dẫn bởi mạng đề xuất | Mất mát RGB, interlevel loss điều chỉnh lấy mẫu giữa các mạng, distortion loss chính quy hóa phân bố trọng số |
| 3D Gaussian Splatting (2023) | Structure-from-Motion, thêm đám mây điểm thưa | Biểu diễn tường minh bằng Gaussian ba chiều, có vị trí, hiệp phương sai, độ trong suốt, màu sắc | Chiếu Gaussian lên mặt phẳng ảnh, kết xuất bằng splatting | Mất mát L1 kết hợp D-SSIM, tối ưu Gaussian xen kẽ cơ chế thêm, tách, loại bỏ |

Bảng 2.4 so sánh định lượng bảy trong tám phương pháp đã khảo sát ở Bảng 2.2 và 2.3, trên cùng bộ dữ liệu Mip-NeRF 360 đã giới thiệu ở Bảng 1.3, gồm chín cảnh thực với năm cảnh ngoài trời và bốn cảnh trong nhà.

Chất lượng kết xuất đánh giá bằng ba chỉ số: PSNR đo mức sai lệch pixel, giá trị càng cao càng tốt; SSIM đánh giá độ tương đồng cấu trúc, càng gần 1 càng tốt; LPIPS đo khoảng cách cảm nhận dựa trên đặc trưng học được từ mạng nơ-ron, càng thấp càng tốt. Thời gian huấn luyện tính bằng giờ, phản ánh thêm chi phí tính toán.

**Bảng 2.4. So sánh chất lượng của các phương pháp**

| Phương pháp | PSNR ↑ | SSIM ↑ | LPIPS ↓ | Thời gian huấn luyện | Tham số / bộ nhớ |
|---|---|---|---|---|---|
| NeRF | 23.85 | 0.605 | 0.451 | 4,16 giờ | 1,5 triệu tham số |
| Mip-NeRF | 24.04 | 0.616 | 0.441 | 3,17 giờ | 0,7 triệu tham số |
| NeRF++ | 25.11 | 0.676 | 0.375 | 9,45 giờ | 2,4 triệu tham số |
| Plenoxels | 23.08 | 0.626 | 0.463 | 0,43 giờ | 2,1 GB bộ nhớ |
| Instant-NGP | 25.30 | 0.671 | 0.371 | 0,09 giờ | 13 MB bộ nhớ |
| Mip-NeRF 360 | 27.69 | 0.792 | 0.237 | 6,89 giờ | 9,9 triệu tham số |
| 3D Gaussian Splatting | 27.21 | 0.815 | 0.214 | 0,69 giờ | 734 MB bộ nhớ |

Số liệu của NeRF, Mip-NeRF, NeRF++ và Mip-NeRF 360 lấy từ Bảng 1 trong paper gốc của Barron và cộng sự, huấn luyện 250.000 vòng lặp, batch size 2^14 tia camera, thuật toán Adam, learning rate giảm theo thang log từ 2×10⁻³ xuống 2×10⁻⁵ kèm 512 bước khởi động. Số liệu của Plenoxels và Instant-NGP lấy từ Bảng 1 trong paper của Kerbl và cộng sự, nơi nhóm tác giả tự chạy lại hai phương pháp này trên cùng bộ dữ liệu; dòng Mip-NeRF 360 trong bảng đó được xác nhận lấy nguyên từ paper gốc nên khớp với số liệu đã dùng ở đây. Số liệu của 3D Gaussian Splatting là kết quả tự báo cáo trong cùng paper, cấu hình 30 nghìn vòng lặp.

Cột cuối không cùng đơn vị cho mọi phương pháp. NeRF, Mip-NeRF, NeRF++ và Mip-NeRF 360 dùng mạng nơ-ron MLP nên đo được bằng số tham số mạng. Plenoxels và 3D Gaussian Splatting không dùng MLP, biểu diễn cảnh trực tiếp bằng lưới voxel hoặc tập hợp Gaussian, nên không có khái niệm tham số mạng tương đương, chỉ đo được bằng dung lượng lưu trữ mô hình.

TensoRF không xuất hiện trong Bảng 2.4. Paper gốc của TensoRF tự nêu phương pháp hiện chỉ hỗ trợ cảnh có giới hạn, chưa xử lý được cảnh không giới hạn với cả tiền cảnh lẫn hậu cảnh, nên phương pháp này chưa từng được chính tác giả đánh giá trên bộ dữ liệu 360 độ không giới hạn, không có số liệu hợp lệ để đưa vào so sánh.

Từ Bảng 2.4, Mip-NeRF 360 đạt PSNR và SSIM cao thứ nhì, chỉ sau 3D Gaussian Splatting ở SSIM và LPIPS, nhưng tốn thời gian huấn luyện và bộ nhớ lớn hơn hẳn các phương pháp dùng biểu diễn tường minh. Plenoxels và Instant-NGP huấn luyện nhanh hơn Mip-NeRF 360 hàng chục lần, nhưng PSNR thấp hơn khoảng hai tới bốn đơn vị decibel. 3D Gaussian Splatting đạt SSIM và LPIPS tốt nhất bảng, với thời gian huấn luyện chỉ bằng một phần mười Mip-NeRF 360.

Không thể đánh giá một phương pháp chỉ dựa trên một chỉ số riêng lẻ. PSNR, SSIM và LPIPS phản ánh các khía cạnh khác nhau của chất lượng ảnh, còn thời gian huấn luyện và tham số hoặc bộ nhớ phản ánh một phần chi phí tính toán. Trong phạm vi bộ dữ liệu Mip-NeRF 360, các phương pháp dùng biểu diễn tường minh như Plenoxels, Instant-NGP và 3D Gaussian Splatting đánh đổi một phần chất lượng để lấy tốc độ huấn luyện nhanh hơn nhiều lần so với các phương pháp dùng mạng nơ-ron ẩn như NeRF, Mip-NeRF và Mip-NeRF 360.

## 2.5. Khuyết điểm tồn đọng theo từng công đoạn

Dù các phương pháp phát triển từ NeRF đã cải thiện đáng kể chất lượng tổng hợp góc nhìn mới, bài toán này vẫn tồn tại hạn chế tại cả bốn công đoạn.

Ở công đoạn 1, ước lượng tham số camera, NeRF gốc phụ thuộc vào độ chính xác của thông tin camera, thường xác định bằng Structure from Motion. Với cảnh ít kết cấu, bề mặt phản chiếu hoặc ảnh có ít vùng nội dung trùng nhau, việc xác định điểm tương ứng và ước lượng tư thế camera có thể không chính xác, khiến tia sáng không đi qua đúng vị trí trong không gian và làm giảm chất lượng tái tạo. Một số phương pháp hướng tới tối ưu hoặc hiệu chỉnh tư thế camera ngay trong quá trình học, nhưng vẫn gặp khó khăn khi dữ liệu đầu vào thiếu thông tin.

Ở công đoạn 2, biểu diễn cảnh ba chiều, các phương pháp tồn tại sự đánh đổi giữa chất lượng biểu diễn, dung lượng bộ nhớ và tốc độ tính toán. NeRF dùng MLP để biểu diễn trường bức xạ liên tục nhưng cần nhiều phép tính khi truy vấn điểm trong không gian. Plenoxels, Instant-NGP và TensoRF cải thiện hiệu quả bằng lưới voxel thưa, hash grid đa độ phân giải hoặc phân rã tensor, nhưng mỗi cách biểu diễn vẫn có giới hạn riêng về bộ nhớ, độ phân giải và chi phí xử lý. Với cảnh 360 độ không giới hạn, biểu diễn đồng thời vùng gần và vùng xa vẫn là một thách thức.

Ở công đoạn 3, kết xuất ảnh, NeRF dùng kết xuất thể tích, yêu cầu truy vấn mạng nhiều lần dọc theo mỗi tia camera nên chi phí tính toán tương đối lớn. Việc coi mỗi pixel tương ứng với một tia lý tưởng chưa mô hình hóa đầy đủ vùng không gian mà pixel bao phủ, dẫn tới răng cưa hoặc mất chi tiết khi đổi độ phân giải và khoảng cách quan sát. Mip-NeRF cải thiện vấn đề này bằng hình nón cụt và Integrated Positional Encoding, còn 3D Gaussian Splatting tăng tốc kết xuất bằng cách chiếu Gaussian ba chiều lên mặt phẳng ảnh, dù vẫn có giới hạn riêng khi biểu diễn hiệu ứng ánh sáng phức tạp.

Ở công đoạn 4, tối ưu hóa, quá trình học phụ thuộc vào số lượng, chất lượng và mức độ bao phủ góc nhìn của ảnh huấn luyện. Khi dữ liệu quá thưa hoặc có nhiều vùng bị che khuất, mô hình có thể tạo bề mặt giả, mất chi tiết hoặc tái tạo không nhất quán ở góc nhìn chưa quan sát. Mip-NeRF 360 dùng thêm interlevel loss và distortion loss để cải thiện quá trình lấy mẫu và hạn chế một số sai lệch trong biểu diễn cảnh.

Từ những hạn chế trên, Mip-NeRF 360 được chọn làm phương pháp trình bày ở Chương 3, vì kế thừa cơ chế chống răng cưa của Mip-NeRF và mở rộng cho cảnh 360 độ không giới hạn. Mô hình kết hợp tham số hóa phi tuyến không gian, mạng đề xuất hướng dẫn lấy mẫu và các hàm mất mát bổ sung, tác động chủ yếu tới công đoạn 2, 3 và 4, tạo điều kiện phân tích mối liên hệ giữa biểu diễn cảnh, kết xuất và tối ưu hóa.

Quá trình phát triển từ NeRF qua Mip-NeRF tới Mip-NeRF 360 có tính kế thừa, thuận lợi cho việc trình bày công thức toán học và đánh giá hiệu quả của từng cải tiến. Đồ án vì vậy tập trung tìm hiểu lý thuyết, triển khai thực nghiệm trên bộ dữ liệu chuẩn và dữ liệu tự thu thập, so sánh chất lượng ảnh và chi phí tính toán, không đặt mục tiêu đề xuất phương pháp mới.
