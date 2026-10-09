# DÀN Ý CHI TIẾT BÁO CÁO ĐỒ ÁN

**Đề tài:** Xây dựng ứng dụng kết xuất ảnh (rendering) với góc nhìn tùy ý dựa vào dãy ảnh 2D cho trước (Tìm hiểu mô hình NeRF và NeRF cải tiến)

**Nhóm thực hiện:**

| Thành viên | MSSV | Vai trò |
|---|---|---|
| Bùi Văn Thiên | 24120138 | Trưởng nhóm |
| Nguyễn Minh Khoa | 24120073 | Thành viên |

**Lớp:** Đồ Họa Máy Tính CQ2024/23
**Giảng viên hướng dẫn:** PGS.TS Lý Quốc Ngọc
**Phương pháp chọn trình bày:** Mip-NeRF 360 (Barron và cộng sự, CVPR 2022)
**Độ dài dự kiến:** 51 trang phần nội dung, cộng phần đầu và tài liệu tham khảo.
Quy định của Khoa (`06-BaoCao/quy-dinh-trinh-bay.md`, mục 2) buộc phần nội dung
tối thiểu 50 trang và không quá 100 trang, không tính trang bìa, lời cảm ơn,
mục lục và tài liệu tham khảo. Tổng ước lượng theo chương bên dưới là
4 + 7 + 11 + 15 + 11 + 3 = 51 trang, vừa đủ ngưỡng nên không được cắt bớt.

Dàn ý này được xây dựng bám sát `01-DeBai/yeu-cau-cua-thay.md`, đặc biệt là tám lỗi thường gặp nêu trong `motsoluuyloi.rtf`. Mỗi vị trí có liên quan đều ghi chú "Lưu ý n" để tiện đối chiếu.

**Quy ước trạng thái nguyên liệu:** `[Sẵn sàng]` viết được ngay · `[Một phần]` có nguyên liệu nhưng chưa đủ · `[Chưa có]` phải làm từ đầu.

---

## PHẦN A. NGUYÊN TẮC XUYÊN SUỐT

### A.1. Trục tổ chức: bốn công đoạn

Toàn bộ báo cáo xoay quanh bốn công đoạn được định nghĩa tại mục 1.3. Giảng viên nhấn mạnh yêu cầu này ở các Lưu ý 1, 2, 3 và 8.

```
[CĐ1] Ước lượng      [CĐ2] Biểu diễn      [CĐ3] Kết xuất      [CĐ4] Tối ưu hóa
      tham số camera         cảnh 3D              ảnh                biểu diễn
```

Mỗi chương dùng bốn công đoạn này theo một cách khác nhau:

| Chương | Vai trò của bốn công đoạn |
|---|---|
| 1 | Định nghĩa bốn công đoạn và ẩn số cần tìm trong mỗi công đoạn |
| 2 | So sánh các phương pháp theo đúng bốn công đoạn; chỉ ra khuyết điểm tồn đọng ở từng công đoạn |
| 3 | Trình bày Mip-NeRF 360 theo đúng bốn công đoạn |
| 4 | Đánh giá kết quả thực nghiệm gắn với từng công đoạn |

Cách tổ chức này cho phép người đọc đối chiếu trực tiếp: cùng một công đoạn, phương pháp A làm thế nào và phương pháp B làm thế nào.

### A.2. Sáu nguyên tắc trình bày rút từ các công trình hàng đầu

Sáu nguyên tắc dưới đây rút ra từ cách NeRF (ECCV 2020), Mip-NeRF 360 (CVPR 2022) và Instant-NGP (SIGGRAPH 2022) tổ chức nội dung.

1. **Nêu vấn đề trước, trình bày giải pháp sau.** Mip-NeRF 360 tuyên bố ba vấn đề cần giải quyết (Parameterization, Efficiency, Ambiguity) rồi dành mỗi mục cho một vấn đề.
2. **Có mục kiến thức nền (Preliminaries).** Tóm tắt phương pháp nền trước khi trình bày phần cải tiến, để người đọc phân biệt được đâu là đóng góp mới.
3. **Mỗi công thức kèm bảng ký hiệu.** Định nghĩa mọi ký hiệu ngay lần đầu xuất hiện.
4. **Kết quả gồm cả định lượng và định tính.** Bảng số chứng minh mức độ cải thiện; ảnh đặt cạnh nhau chứng minh cải thiện ở đâu.
5. **Có nghiên cứu loại trừ (Ablation Study).** Tắt từng thành phần rồi đo lại để chứng minh thành phần đó thực sự cần thiết.
6. **Trung thực về hạn chế.** Mọi công trình hàng đầu đều có mục Limitations.

### A.3. Quy ước thuật ngữ

Giữ thống nhất các thuật ngữ sau trong toàn báo cáo:

| Thuật ngữ | Định nghĩa dùng trong báo cáo |
|---|---|
| Công đoạn | Một trong bốn giai đoạn của framework tổng quát ở mục 1.3.2 |
| Ẩn số | Đại lượng chưa biết cần tìm trong một công đoạn |
| Độ chính xác | Nhóm độ đo phản ánh chất lượng ảnh (PSNR, SSIM, LPIPS) |
| Độ phức tạp tính toán | Nhóm độ đo phản ánh chi phí (thời gian, bộ nhớ, số truy vấn mạng) |
| Giai đoạn học | Quá trình tối ưu tham số, có lan truyền ngược |
| Giai đoạn kiểm thử | Quá trình sinh ảnh từ tham số đã học, không lan truyền ngược |
| Biểu diễn ẩn | Thông tin cảnh nằm trong tham số của một hàm, không lưu tường minh |
| Biểu diễn tường minh | Thông tin cảnh lưu trực tiếp dưới dạng điểm, mặt, ô lưới |

---

## PHẦN MỞ ĐẦU (khoảng 4 trang)

| Thành phần | Nội dung |
|---|---|
| Bìa chính | Trường, khoa, tên sinh viên, tên đồ án, loại báo cáo, năm |
| Trang phụ bìa | Như bìa chính, thêm mã số sinh viên và giảng viên hướng dẫn |
| Lời cảm ơn | Khoảng nửa trang |
| Đề cương chi tiết | Tên đề tài, GVHD, phân công từng thành viên theo mốc thời gian, có chữ ký GVHD |
| Mục lục | Tự động sinh, tới mục cấp ba |
| Danh mục hình, danh mục bảng | Đánh số theo chương, ví dụ Hình 3.1, Bảng 2.1 |
| Danh mục từ viết tắt | NeRF, MLP, SfM, COLMAP, PSNR, SSIM, LPIPS, IPE, PE, NDC, SH, 3DGS, GPU, TPU, CUDA, SDF, FPS |
| Danh mục ký hiệu | x (vị trí 3D), d (hướng nhìn), o (gốc tia), t (tham số tia), sigma (density), c (màu), T (transmittance), alpha (opacity), gamma (positional encoding), mu và Sigma (mean và covariance), Theta (trọng số mạng), K, R, C (nội tại, xoay, tâm camera) |
| Tóm tắt | Khoảng 200 từ, bốn câu theo trình tự: bối cảnh, khoảng trống nghiên cứu, việc đã thực hiện, kết quả cụ thể đạt được |

Thứ tự tám dòng trên theo đúng `quy-dinh-trinh-bay.md` mục 4: tóm tắt đặt sau các
bảng danh mục, không đặt trước. Phần đề cương chi tiết viết trước khi bắt tay vào
Chương 1, vì cột phân công buộc phải chốt việc của từng người ngay từ đầu.

---

## CHƯƠNG 1. GIỚI THIỆU (khoảng 7 trang)

### 1.1. Ý nghĩa khoa học của chủ đề `[Một phần]` (khoảng 1 trang)

**Đoạn 1 (đặt vấn đề).** Con người chỉ cần nhìn một vật từ vài góc là hình dung được hình dạng ba chiều của nó, trong khi máy tính gặp khó khăn vì ảnh hai chiều đã mất thông tin độ sâu: mỗi điểm ảnh tương ứng với vô số điểm ba chiều khả dĩ. Bài toán tổng hợp góc nhìn mới (novel view synthesis) chính là khôi phục khả năng này cho máy tính.

**Đoạn 2 (quá trình phát triển trước NeRF).** Các hướng tiếp cận trước đó đều vướng một rào cản cơ bản: nội suy light field đòi hỏi ảnh lấy mẫu rất dày; biểu diễn lưới tam giác khó tối ưu và cần mô hình mẫu có sẵn; lưới voxel tiêu tốn bộ nhớ tăng theo lũy thừa của độ phân giải; biểu diễn bề mặt ẩn cần dữ liệu ba chiều xác thực làm đầu vào huấn luyện.

**Đoạn 3 (vì sao NeRF là bước ngoặt).** NeRF khắc phục đồng thời ba hạn chế trên: chuyển từ biểu diễn tường minh sang biểu diễn ẩn nên nén được toàn cảnh vào vài megabyte trọng số; chỉ cần ảnh màu thông thường mà không cần dữ liệu ba chiều xác thực; và lần đầu đạt chất lượng ảnh gần với ảnh chụp thật.

**Đoạn 4 (vị trí trong bức tranh nghiên cứu hiện nay).** NeRF mở ra nhánh nghiên cứu neural rendering với số lượng công trình kế thừa tăng nhanh từ năm 2020, dẫn tới sự xuất hiện của 3D Gaussian Splatting năm 2023.

*Hình 1.1:* minh họa bài toán: một số ảnh đầu vào ở các góc khác nhau, dẫn tới ảnh đầu ra ở góc chưa từng chụp.

*Nguồn trích dẫn:* `Survey/2022 Advances in Neural Rendering`, `Survey/2022 CVM Review`, `Selected/2020 NeRF`.

### 1.2. Ý nghĩa ứng dụng của chủ đề `[Chưa có]` (khoảng 1 trang)

Mỗi lĩnh vực viết một đoạn, nêu rõ lý do NeRF phù hợp thay vì chỉ liệt kê tên lĩnh vực.

| Lĩnh vực | Lý do NeRF phù hợp |
|---|---|
| Thực tế ảo và tăng cường | Dựng môi trường ba chiều chân thực nhanh, thay cho việc mô hình hóa thủ công kéo dài hàng tháng |
| Số hóa di sản | Bảo tồn hiện vật không thể tiếp xúc trực tiếp, chỉ cần ảnh chụp thông thường |
| Thương mại điện tử | Cho phép xem sản phẩm từ mọi góc và thử sản phẩm ảo |
| Bất động sản và du lịch | Tham quan ảo không gian thật |
| Robot và xe tự hành | Dựng bản đồ ba chiều từ camera giá rẻ thay cho cảm biến LiDAR đắt tiền |
| Điện ảnh và kỹ xảo | Dựng cảnh từ cảnh quay thật, chèn vật thể ảo khớp điều kiện ánh sáng |

Nên nêu một đến hai ví dụ triển khai thực tế, chẳng hạn tính năng Immersive View của Google Maps, để tăng tính thuyết phục.

### 1.3. Phát biểu bài toán `[Sẵn sàng]` (khoảng 3,5 trang)

Mục này định nghĩa trục tổ chức cho toàn bộ báo cáo.

**Lưu ý 1:** framework chỉ mô tả công đoạn ở mức tổng quát, không được nhắc tên phương pháp cụ thể như COLMAP hay MLP.
**Lưu ý 2:** mỗi công đoạn phải nêu rõ dữ kiện đã cho và ẩn số cần tìm.

#### 1.3.1. Đầu vào và đầu ra của hệ thống

**Đầu vào** là tập ảnh màu hai chiều `{I_1, I_2, ..., I_N}` với N khoảng 20 đến 100 ảnh. Hai ràng buộc bắt buộc: cảnh phải tĩnh trong suốt quá trình chụp, nghĩa là vật thể và điều kiện ánh sáng không đổi giữa các ảnh; và các ảnh liên tiếp phải có độ chồng lấp đủ lớn.

**Đầu ra** là ảnh màu được kết xuất tại một tư thế camera tùy ý không có trong tập đầu vào. Đầu ra mở rộng gồm chuỗi ảnh tạo thành video quay quanh cảnh, hoặc mô hình ba chiều dạng lưới tam giác.

#### 1.3.2. Framework chung gồm bốn công đoạn

```
                         ┌──────────────────────────────────┐
                         │                                  │
   Tập ảnh 2D            ▼                                  │
       │          ┌─────────────┐    ┌─────────────┐   ┌────┴────┐
       └─────────►│ CĐ1: Ước    │───►│ CĐ2: Biểu   │──►│ CĐ3: Kết│──► Ảnh góc
                  │ lượng tham  │    │ diễn cảnh   │   │ xuất ảnh│    nhìn mới
                  │ số camera   │    │ 3D          │   └────┬────┘
                  └─────────────┘    └─────────────┘        │
                                            ▲                │
                                            │     ┌──────────▼────────┐
                                            └─────┤ CĐ4: Tối ưu hóa   │
                                                  │ biểu diễn         │
                                                  └───────────────────┘
```

*Hình 1.2:* sơ đồ framework bốn công đoạn, vẽ lại bằng công cụ đồ họa.

**Bảng 1.1. Mô tả bốn công đoạn ở mức tổng quát**

| Công đoạn | Nhiệm vụ | Các hướng giải pháp khả dĩ |
|---|---|---|
| CĐ1 | Xác định mỗi ảnh được chụp từ vị trí nào, hướng nào, với thông số ống kính ra sao | Structure-from-Motion, SLAM, cảm biến gắn kèm, hoặc tư thế có sẵn với dữ liệu tổng hợp |
| CĐ2 | Xây dựng cấu trúc dữ liệu hoặc hàm số mô tả cảnh, truy vấn được tại điểm bất kỳ | Biểu diễn tường minh (lưới tam giác, voxel, đám mây điểm, Gaussian) hoặc biểu diễn ẩn (mạng nơ-ron, hàm liên tục) |
| CĐ3 | Từ biểu diễn và một góc nhìn, sinh ra ảnh hai chiều | Rasterization, ray tracing, ray marching kết hợp volume rendering, splatting |
| CĐ4 | Điều chỉnh tham số của biểu diễn để ảnh sinh ra khớp với ảnh quan sát | Hạ gradient khi quy trình khả vi, tối ưu phi tuyến, hoặc lấp đầy trực tiếp |

#### 1.3.3. Ẩn số cần tìm trong từng công đoạn

Giảng viên nhấn mạnh đây là nội dung thường bị bỏ sót (Lưu ý 2), do đó cần trình bày rõ ràng bằng bảng.

**Bảng 1.2. Dữ kiện đã cho và ẩn số cần tìm**

| Công đoạn | Dữ kiện đã cho | Ẩn số cần tìm | Ràng buộc dùng để giải |
|---|---|---|---|
| CĐ1 | Tập ảnh `{I_1..I_N}` | Với mỗi ảnh i: ma trận nội tại `K_i`, ma trận xoay `R_i`, tâm camera `C_i`; kèm tập điểm ba chiều thưa `{X_j}` | Cùng một điểm vật lý xuất hiện trên nhiều ảnh phải chiếu về đúng vị trí quan sát được, tức sai số tái chiếu nhỏ nhất |
| CĐ2 | Phạm vi không gian cảnh; dạng biểu diễn đã chọn | Tham số `Theta` của biểu diễn. Tùy dạng biểu diễn mà `Theta` là trọng số mạng, giá trị trên lưới voxel, hoặc tập tham số của các primitive | `Theta` phải sinh ra ảnh khớp với mọi ảnh quan sát được |
| CĐ3 | Biểu diễn `Theta` và tư thế camera cần kết xuất | Không có ẩn số phải học. Ẩn số thiết kế gồm: chọn thuật toán kết xuất nào, lấy bao nhiêu điểm mẫu | Quy trình phải khả vi nếu muốn dùng hạ gradient ở CĐ4 |
| CĐ4 | Ảnh kết xuất và ảnh thật tương ứng | `Theta` tối ưu, chính là ẩn số của CĐ2 được giải tại đây | Tối thiểu hóa hàm mất mát giữa ảnh kết xuất và ảnh thật |

Hai công đoạn CĐ2 và CĐ4 gắn chặt với nhau: CĐ2 quyết định dạng của ẩn số `Theta`, còn CĐ4 quyết định cách tìm ra `Theta`. Việc chọn dạng biểu diễn ở CĐ2 do đó ràng buộc luôn phương pháp tối ưu khả dụng ở CĐ4. Đây cũng là nơi các phương pháp khác nhau nhiều nhất, sẽ khảo sát ở Chương 2.

#### 1.3.4. Các tác vụ cần thực hiện

Cụ thể hóa bốn công đoạn thành danh sách tác vụ thực thi được, theo yêu cầu tại `phuongphap.rtf` mục 2.4.

#### 1.3.5. Tập dữ liệu thử nghiệm chuẩn

**Lưu ý 7:** ngoài số lượng mẫu, phải nêu rõ dữ liệu chứa thách thức gì.

**Bảng 1.3. Các bộ dữ liệu chuẩn của bài toán**

| Bộ dữ liệu | Số cảnh | Loại | Thách thức chứa trong dữ liệu |
|---|---|---|---|
| Blender Synthetic | 8 vật thể | Tổng hợp, 360 độ | Vật liệu phản chiếu không tuân theo mô hình Lambert, hình học phức tạp như dây chằng tàu thủy và bánh răng |
| LLFF | 8 cảnh | Thật, hướng về phía trước | Nhiễu ảnh thật, nội dung trải từ gần tới vô cực, vùng bị che khuất một phần |
| Mip-NeRF 360 | 9 cảnh, gồm 5 ngoài trời và 4 trong nhà | Thật, 360 độ không giới hạn | Cảnh không giới hạn với nền trải tới chân trời, chi tiết ở nhiều tỉ lệ khác nhau, ánh sáng ngoài trời thay đổi, vùng có ít ảnh quan sát |

### 1.4. Đóng góp của báo cáo `[Một phần]` (khoảng 0,75 trang)

1. Khảo sát có hệ thống các phương pháp radiance field giai đoạn 2020 đến 2024, so sánh theo đúng bốn công đoạn của framework và chỉ ra khuyết điểm tồn đọng ở từng công đoạn.
2. Trình bày chi tiết Mip-NeRF 360 trong mạch kế thừa NeRF, Mip-NeRF và Mip-NeRF 360, làm rõ mỗi cải tiến tác động vào công đoạn nào.
3. Cài đặt thử nghiệm trên dữ liệu chuẩn và dữ liệu tự thu thập, đánh giá cả độ chính xác lẫn độ phức tạp tính toán.
4. Phân tích hạn chế của phương pháp qua quan sát thực nghiệm và đối chiếu với các hướng phát triển mới nhất.

Giảng viên ghi rõ tại `phuongphap.rtf` rằng sinh viên chỉ cần đọc, hiểu và cài đặt lại, chưa yêu cầu đề xuất giải pháp mới. Do đó không viết đóng góp theo kiểu đề xuất phương pháp mới.

### 1.5. Bố cục báo cáo `[Chưa có]` (khoảng 0,25 trang)

---

## CHƯƠNG 2. CÁC CÔNG TRÌNH NGHIÊN CỨU LIÊN QUAN (khoảng 11 trang)

Chương này trả lời hai câu hỏi giảng viên yêu cầu: người ta đã làm gì rồi (mục 2.1 đến 2.4) và mình muốn làm gì (mục 2.5).

**Lưu ý 3:** mọi giải pháp trình bày theo cùng một khuôn, bám theo bốn công đoạn ở mục 1.3.2.
**Lưu ý 8:** phải chỉ ra khuyết điểm tồn đọng theo từng công đoạn và phân loại thuộc độ chính xác hay độ phức tạp tính toán.

### 2.1. Các phương pháp trước NeRF `[Một phần]` (khoảng 1,5 trang)

Trình bày theo công đoạn để thấy rõ mỗi hướng vướng rào cản ở đâu.

**Bảng 2.1. Các phương pháp trước NeRF, đối chiếu theo công đoạn**

| Nhóm phương pháp | CĐ2: Biểu diễn | CĐ3: Kết xuất | Rào cản chính |
|---|---|---|---|
| Light field và image-based rendering | Tập ảnh gốc kèm thông tin độ sâu thô | Nội suy giữa các ảnh | Đòi hỏi lấy mẫu rất dày |
| Lưới tam giác | Lưới tam giác | Rasterization hoặc path tracing | Tối ưu khó hội tụ, cần mô hình mẫu |
| Lưới voxel | Lưới ba chiều rời rạc | Ray marching | Bộ nhớ tăng theo lũy thừa độ phân giải |
| Bề mặt ẩn neural | Hàm khoảng cách có dấu hoặc hàm chiếm chỗ | Tìm giao điểm với bề mặt | Cần dữ liệu ba chiều xác thực, kết quả bị mờ |

### 2.2. NeRF và các hạn chế `[Sẵn sàng]` (khoảng 2 trang)

#### 2.2.1. Ánh xạ NeRF vào bốn công đoạn

Mục này thiết lập khuôn chuẩn áp dụng cho mọi phương pháp trình bày sau đó.

**Bảng 2.2. NeRF theo bốn công đoạn**

| Công đoạn | Cách NeRF giải quyết |
|---|---|
| CĐ1 | Dùng Structure-from-Motion, cụ thể là COLMAP, để ước lượng `K`, `R`, `C` |
| CĐ2 | Hàm liên tục `F_Theta(x, d)` trả về màu và density, cài đặt bằng MLP 8 lớp 256 kênh |
| CĐ3 | Ray marching kết hợp volume rendering, lấy 192 điểm mẫu mỗi tia, chia hai lượt thô và tinh |
| CĐ4 | Hạ gradient bằng thuật toán Adam trên hàm mất mát bình phương trung bình |

#### 2.2.2. Năm hạn chế của NeRF

Mỗi hạn chế được gắn với công đoạn tương ứng và phân loại theo yêu cầu của Lưu ý 8.

**Bảng 2.3. Hạn chế của NeRF theo công đoạn**

| Số | Hạn chế | Công đoạn | Loại khuyết điểm | Nguyên nhân kỹ thuật |
|---|---|---|---|---|
| 1 | Huấn luyện chậm, mất một đến hai ngày cho mỗi cảnh | CĐ2 và CĐ4 | Độ phức tạp tính toán | Mỗi điểm mẫu phải đi qua MLP 8 lớp 256 kênh, với hàng trăm nghìn điểm mỗi batch |
| 2 | Kết xuất chậm, không đạt thời gian thực | CĐ3 | Độ phức tạp tính toán | Mỗi điểm ảnh cần 192 lần truy vấn mạng |
| 3 | Răng cưa khi thay đổi tỉ lệ hoặc khoảng cách | CĐ3 | Độ chính xác | Tia mảnh không biểu diễn được vùng không gian mà điểm ảnh thực sự bao phủ |
| 4 | Kém hiệu quả với cảnh 360 độ không giới hạn | CĐ2 và CĐ3 | Độ chính xác | Lấy mẫu tuyến tính theo tham số tia; phép biến đổi NDC chỉ áp dụng được cho cảnh hướng về phía trước |
| 5 | Phụ thuộc vào độ chính xác của tư thế camera | CĐ1 | Độ chính xác | Tư thế sai làm các tia không giao đúng vị trí, dẫn tới hình học bị nhòe |

### 2.3. Các giải pháp tiên tiến `[Sẵn sàng]` (khoảng 4 trang)

**Lưu ý 3:** mỗi phương pháp trình bày theo cùng một khuôn năm mục gồm khuyết điểm được giải quyết, công đoạn tác động, ý tưởng chính, kết quả đạt được, hạn chế còn lại. Mỗi phương pháp viết khoảng nửa trang.

**Bảng 2.4. Tám phương pháp tiên tiến và phạm vi tác động**

| Mục | Phương pháp | Khuyết điểm được giải quyết | Công đoạn tác động |
|---|---|---|---|
| 2.3.1 | Instant-NGP, SIGGRAPH 2022 | Số 1, huấn luyện chậm | CĐ2 qua hash encoding thay positional encoding và MLP thu nhỏ; CĐ3 qua lưới chiếm chỗ bỏ qua vùng trống |
| 2.3.2 | Plenoxels, CVPR 2022 | Số 1, huấn luyện chậm | CĐ2, bỏ hẳn mạng nơ-ron, dùng voxel thưa kèm hệ số Spherical Harmonics |
| 2.3.3 | TensoRF, ECCV 2022 | Số 1, huấn luyện chậm | CĐ2, phân rã tensor bậc thấp |
| 2.3.4 | Mip-NeRF, ICCV 2021 | Số 3, răng cưa | CĐ3 qua hình nón cụt thay tia mảnh; CĐ2 qua Integrated Positional Encoding |
| 2.3.5 | NeRF++, 2020 | Số 4, cảnh không giới hạn | CĐ2, tách hai mạng cho vùng trong và ngoài khối cầu đơn vị |
| 2.3.6 | Mip-NeRF 360, CVPR 2022 | Số 3 và số 4 | CĐ2 qua scene contraction; CĐ3 qua lấy mẫu theo disparity; CĐ4 qua proposal network và distortion loss |
| 2.3.7 | 3D Gaussian Splatting, SIGGRAPH 2023 | Số 2, kết xuất chậm | CĐ2 qua biểu diễn Gaussian tường minh; CĐ3 qua rasterization thay ray marching |
| 2.3.8 | Zip-NeRF, ICCV 2023 | Số 1, số 3 và số 4 | Kết hợp Mip-NeRF 360 ở CĐ2, CĐ3, CĐ4 với hash grid của Instant-NGP ở CĐ2 |

### 2.4. Bảng so sánh các giải pháp theo công đoạn `[Một phần]` (khoảng 2 trang)

Đây là bảng giảng viên yêu cầu tại Lưu ý 3, với cột ứng với các công đoạn và hàng là phương pháp.

**Bảng 2.5. So sánh tám phương pháp theo bốn công đoạn**

| Phương pháp | CĐ1: Ước lượng tư thế | CĐ2: Biểu diễn cảnh | CĐ3: Kết xuất | CĐ4: Tối ưu |
|---|---|---|---|---|
| NeRF | Structure-from-Motion | MLP 8 lớp 256 kênh, positional encoding | Ray marching, 192 mẫu mỗi tia, hai lượt thô và tinh | Mất mát bình phương trung bình, Adam |
| NeRF++ | Structure-from-Motion | Hai MLP cho trong và ngoài khối cầu, tham số hóa nghịch đảo bán kính | Ray marching hai đoạn, ghép transmittance | Mất mát bình phương trung bình |
| Mip-NeRF | Structure-from-Motion | Một MLP, Integrated Positional Encoding mã hóa vùng | Hình nón cụt thay tia mảnh | Mất mát bình phương trung bình, giám sát đa tỉ lệ |
| Plenoxels | Structure-from-Motion | Voxel thưa kèm hệ số Spherical Harmonics, không dùng mạng | Ray marching kết hợp nội suy tam tuyến tính | Gradient trực tiếp lên voxel, kèm chính quy hóa biến phân toàn phần |
| Instant-NGP | Structure-from-Motion | Hash grid đa độ phân giải kết hợp MLP nhỏ | Ray marching kết hợp lưới chiếm chỗ | Mất mát bình phương trung bình, Adam với epsilon rất nhỏ |
| TensoRF | Structure-from-Motion | Tensor phân rã bậc thấp | Ray marching | Mất mát bình phương trung bình kèm chính quy hóa |
| Mip-NeRF 360 | Structure-from-Motion | Scene contraction, MLP 8 lớp 1024 kênh, off-axis IPE | Lấy mẫu đều theo disparity, hình nón cụt | Mất mát tái tạo, mất mát distillation, mất mát distortion |
| 3D Gaussian Splatting | Structure-from-Motion, dùng thêm đám mây điểm thưa | Hàng triệu Gaussian ba chiều tường minh | Rasterization theo kiểu splatting | Mất mát L1 kết hợp D-SSIM, điều khiển mật độ thích ứng |

**Bảng 2.6. So sánh hiệu năng theo hai nhóm độ đo**

Lưu ý 6 yêu cầu có cả độ chính xác lẫn độ phức tạp tính toán.

| Phương pháp | PSNR | SSIM | LPIPS | Thời gian huấn luyện | Tốc độ kết xuất | Bộ nhớ | Số truy vấn mạng mỗi tia |
|---|---|---|---|---|---|---|---|

Ba quy tắc bắt buộc khi lập hai bảng trên. Thứ nhất, mỗi con số phải ghi rõ nguồn gồm tên công trình và số hiệu bảng, đặt ở chú thích dưới bảng. Thứ hai, phải ghi rõ điều kiện đo gồm phần cứng và bộ dữ liệu, vì các công trình đo trên cấu hình khác nhau. Thứ ba, ưu tiên lấy số liệu từ một nguồn đo chung, chẳng hạn Bảng 1 của `Selected/2022 Mip-NeRF 360` có đo nhiều phương pháp trên cùng bộ dữ liệu, vì đây là so sánh công bằng nhất.

### 2.5. Khuyết điểm tồn đọng và định hướng của đồ án `[Chưa có]` (khoảng 1,5 trang)

Mục này đáp ứng Lưu ý 8, yêu cầu nhìn ra khuyết điểm còn tồn đọng cần giải quyết trong các công đoạn.

**Bảng 2.7. Khuyết điểm tồn đọng theo từng công đoạn**

| Công đoạn | Khuyết điểm còn tồn đọng | Loại | Mức độ đã được giải quyết |
|---|---|---|---|
| CĐ1 | Phụ thuộc hoàn toàn vào chất lượng Structure-from-Motion; thất bại với cảnh ít kết cấu hoặc bề mặt phản chiếu; chưa xử lý được cảnh động | Độ chính xác | Hướng NeRF không cần tư thế như BARF và NeRF-- còn chưa trưởng thành |
| CĐ2 | Đánh đổi giữa dung lượng và chất lượng chưa được giải quyết triệt để: biểu diễn ẩn gọn nhưng chậm, biểu diễn tường minh nhanh nhưng nặng hàng trăm megabyte | Cả hai | Zip-NeRF dung hòa được một phần nhưng vẫn chưa đạt thời gian thực như 3D Gaussian Splatting |
| CĐ3 | Ray marching vẫn tốn nhiều lần truy vấn; rasterization nhanh nhưng mất tính liên tục và khó biểu diễn hiệu ứng trong suốt hoặc khúc xạ | Độ phức tạp tính toán | 3D Gaussian Splatting đạt thời gian thực nhưng đánh đổi dung lượng |
| CĐ4 | Cần nhiều ảnh đầu vào, khoảng 20 đến 100; chất lượng giảm nhanh khi ít ảnh; xuất hiện vật thể ảo lơ lửng ở vùng ít quan sát | Độ chính xác | Mất mát distortion của Mip-NeRF 360 giảm được vật thể ảo; hướng NeRF ít ảnh còn đang mở |

**Định hướng của đồ án.** Mip-NeRF 360 được chọn vì ba lý do. Thứ nhất, nó giải quyết đồng thời hai khuyết điểm là răng cưa ở CĐ3 và cảnh không giới hạn ở CĐ2 cùng CĐ3. Thứ hai, nó tác động vào cả ba công đoạn CĐ2, CĐ3 và CĐ4, nên trình bày được đầy đủ hơn so với các phương pháp chỉ tác động một công đoạn. Thứ ba, nó nằm trong mạch kế thừa rõ ràng từ NeRF qua Mip-NeRF, thuận lợi cho việc trình bày có hệ thống. Phạm vi đồ án giới hạn ở đọc hiểu, trình bày lại và cài đặt thử nghiệm, không đề xuất phương pháp mới.

---

## CHƯƠNG 3. PHƯƠNG PHÁP MIP-NERF 360 (khoảng 15 trang)

Chương này là trọng tâm của báo cáo, trình bày theo mạch logic mà `phuongphap.rtf` mục 2.6 yêu cầu: nguyên lý, phương pháp, giải thuật, chương trình minh họa.

**Lưu ý 4 và 5:** phải nêu rõ dữ liệu xác thực, cách đánh nhãn, hàm mất mát; và phải có sơ đồ riêng cho giai đoạn học và giai đoạn kiểm thử.

### 3.0. Ba vấn đề Mip-NeRF 360 giải quyết `[Sẵn sàng]` (khoảng 0,5 trang)

Đặt khung cho toàn chương, theo đúng cách công trình gốc tổ chức nội dung.

**Bảng 3.1. Ba vấn đề và vị trí giải quyết**

| Vấn đề | Mô tả | Công đoạn | Giải quyết tại mục |
|---|---|---|---|
| Parameterization | Cảnh 360 độ trải tới vô cực nên không lấy mẫu tuyến tính được | CĐ2 và CĐ3 | 3.3.1 |
| Efficiency | Cảnh lớn cần mạng dung lượng lớn, nhưng truy vấn dày đặc mạng lớn thì quá tốn kém | CĐ3 và CĐ4 | 3.3.2 |
| Ambiguity | Nội dung cảnh có thể nằm ở bất kỳ độ sâu nào, cộng với ít ảnh quan sát, dẫn tới hiện tượng nhiễu hình học | CĐ4 | 3.3.3 |

### 3.1. Nguyên lý: nền tảng NeRF `[Sẵn sàng]` (khoảng 4 trang)

- **3.1.1.** Biểu diễn cảnh bằng trường bức xạ năm chiều `F_Theta(x, d)`. Giải thích khái niệm trường theo nghĩa vật lý, lý do gọi là biểu diễn ẩn, và định lý xấp xỉ phổ quát. Kèm Bảng 3.2 chú thích ký hiệu.
- **3.1.2.** Mô hình camera lỗ kim và phép chiếu phối cảnh dựa trên tam giác đồng dạng. Ma trận nội tại `K`, ma trận xoay `R`, tâm camera `C`, công thức tia `r(t) = o + t*d`. Kèm Hình 3.1.
- **3.1.3.** Lấy mẫu phân tầng và lý do không dùng lưới điểm cố định.
- **3.1.4.** Positional encoding, hiện tượng thiên lệch phổ (spectral bias), và hai giá trị L bằng 10 cho vị trí tạo 60 chiều, L bằng 4 cho hướng tạo 24 chiều.
- **3.1.5.** Kiến trúc MLP 8 lớp 256 kênh và kết nối tắt. Density chỉ phụ thuộc vị trí trong khi màu phụ thuộc cả hướng nhìn, nhờ đó vừa đảm bảo nhất quán đa góc nhìn vừa mô phỏng được hiệu ứng phụ thuộc góc nhìn. Kèm Hình 3.2.
- **3.1.6.** Volume rendering. Định nghĩa chính xác density là xác suất vi phân, công thức tích phân liên tục, cách dẫn hàm transmittance từ phương trình vi phân theo định luật Beer-Lambert, và chứng minh công thức rời rạc là tổng Riemann xấp xỉ tích phân. Kèm Bảng 3.3 và một ví dụ số với ba điểm mẫu minh họa hiện tượng che khuất.
- **3.1.7.** Lấy mẫu phân cấp với trọng số, phương pháp inverse transform sampling, và hàm mất mát cộng gộp cả hai nhánh.

*Nguyên liệu:* `02-TaiLieuHoc/pipeline_NeRF.md`, `lythuyet_NeRF.md`. *Trích dẫn:* `Selected/2020 NeRF`, `Foundation/1995 Optical Models`.

### 3.2. Kiến thức nền: Mip-NeRF và vấn đề răng cưa `[Một phần]` (khoảng 2,5 trang)

- **3.2.1.** Vấn đề răng cưa, xuất phát từ việc điểm ảnh là một vùng chứ không phải một điểm. Kèm Hình 3.3 so sánh tia mảnh với hình nón.
- **3.2.2.** Hình nón cụt và phép xấp xỉ bằng phân phối Gaussian đa biến với tham số `mu` và `Sigma`. Kèm Bảng 3.4.
- **3.2.3.** Integrated Positional Encoding, định nghĩa là kỳ vọng của positional encoding trên phân phối Gaussian. Dạng đóng cho thấy biên độ bị nhân với hệ số suy giảm phụ thuộc phương sai. Trực giác quan trọng: thành phần tần số cao tự động bị triệt tiêu khi vùng không gian quá lớn, nhờ đó chống răng cưa có cơ sở toán học thay vì xử lý hậu kỳ.
- **3.2.4.** Gộp hai mạng thô và tinh thành một mạng duy nhất, nhưng vẫn giám sát đa tỉ lệ bằng mất mát ảnh với hệ số nhỏ cho nhánh thô. Chi tiết này quan trọng vì chính nó là thành phần mà Mip-NeRF 360 loại bỏ.

*Trích dẫn:* `Selected/2021 Mip-NeRF`. Cần đọc công trình này để bổ sung các nội dung hiện chưa xác minh được trong `pipeline_MipNeRF360.md`.

### 3.3. Phương pháp Mip-NeRF 360 `[Sẵn sàng]` (khoảng 5 trang)

#### 3.3.1. Giải quyết Parameterization bằng Scene Contraction (khoảng 1,75 trang)

Tác động vào CĐ2 và CĐ3. Nội dung gồm: công thức phép co không gian, lưu ý bán kính được đo từ gốc tọa độ thế giới chứ không phải từ camera; đóng góp chính là áp phép co lên cả phân phối Gaussian theo kiểu bộ lọc Kalman mở rộng chứ không chỉ lên điểm; cách tham số hóa lại tia để lấy mẫu đều theo disparity, nhờ đó cận xa vô hạn trở nên hợp lệ; và off-axis IPE là nâng cấp bắt buộc vì phép co sinh ra Gaussian rất dị hướng. Kèm Hình 3.4 và Bảng 3.5.

#### 3.3.2. Giải quyết Efficiency bằng Proposal Network (khoảng 1,75 trang)

Tác động vào CĐ3 và CĐ4.

**Bảng 3.6. So sánh hai mạng trong kiến trúc**

| Thuộc tính | Proposal MLP | NeRF MLP |
|---|---|---|
| Nhiệm vụ | Chỉ dự đoán density để hướng dẫn lấy mẫu | Dự đoán cả density và màu để kết xuất |
| Kích thước | 4 lớp, 256 kênh | 8 lớp, 1024 kênh |
| Số mẫu | Hai lượt, mỗi lượt 64 | 32 |

Khác biệt căn bản so với cơ chế thô và tinh của NeRF: proposal network không dự đoán màu và không được giám sát bằng mất mát ảnh. Cơ chế huấn luyện là online distillation, trong đó histogram density của proposal phải bao trọn histogram của NeRF MLP, sử dụng kỹ thuật dừng gradient và một hàm mất mát dạng chặn trên một phía bất đối xứng. Kết quả là tăng tốc huấn luyện khoảng ba lần. Kèm Hình 3.5.

#### 3.3.3. Giải quyết Ambiguity bằng Distortion Loss (khoảng 1,5 trang)

Tác động vào CĐ4. Hai hiện tượng nhiễu có tên riêng là floaters, tức vật thể ảo lơ lửng, và background collapse, tức nền bị sụp vào gần. Hàm mất mát distortion phạt phân phối trọng số bị phân tán dọc tia, khuyến khích dồn gọn tại một vị trí, phù hợp với bản chất bề mặt là một lớp mỏng. Chi tiết cần nêu: hàm này tính trên không gian đã tham số hóa lại chứ không trên tham số tia gốc.

Một phát hiện quan trọng từ nghiên cứu loại trừ của công trình gốc: bỏ mất mát distortion không làm xấu các chỉ số PSNR, SSIM và LPIPS, thậm chí PSNR còn nhỉnh hơn, nhưng lại sinh ra vật thể ảo nhìn thấy được trên bản đồ độ sâu. Do đó không được viết rằng mất mát distortion cải thiện PSNR. Kèm Hình 3.6.

### 3.4. Giải thuật: tiến trình hoạt động của hệ thống `[Sẵn sàng]` (khoảng 2,5 trang)

Lưu ý 5 yêu cầu trình bày rõ tiến trình của cả giai đoạn học lẫn giai đoạn kiểm thử, do đó tách thành hai mục với hai sơ đồ riêng.

#### 3.4.1. Giai đoạn học

Lưu ý 4 yêu cầu nêu rõ đầu vào, dữ liệu xác thực, cách đánh nhãn và hàm mất mát.

**Bảng 3.7. Đặc tả giai đoạn học**

| Thành phần | Nội dung |
|---|---|
| Đầu vào | Tập ảnh kèm tư thế camera thu được từ CĐ1 |
| Dữ liệu xác thực | Màu của từng điểm ảnh trong các ảnh đã chụp |
| Cách đánh nhãn | Không cần đánh nhãn thủ công. Bản thân ảnh chụp chính là nhãn: mỗi điểm ảnh tương ứng một tia, và màu điểm ảnh đó là giá trị đích mà tia phải kết xuất ra. Đây là bài toán tự giám sát, khác với các bài toán thị giác máy tính cần người gán nhãn |
| Hàm mất mát | Tổng của ba thành phần: mất mát tái tạo dạng bình phương trung bình, mất mát distillation cho proposal network, và mất mát distortion |
| Tham số được tối ưu | Trọng số của NeRF MLP và Proposal MLP |
| Thuật toán tối ưu | Adam với tốc độ học giảm dần theo lịch |

*Hình 3.7. Sơ đồ giai đoạn học*

```
Ảnh và tư thế → chọn batch tia → lấy mẫu → Proposal MLP
    → lấy mẫu lại → NeRF MLP → volume rendering → ảnh kết xuất
                                                       │
         Màu điểm ảnh thật ───────────────────────────► So sánh → Mất mát
                                                                    │
                                                  Lan truyền ngược  ▼
                                                      Cập nhật tham số ──┐
                                                                         │
                                   (lặp N vòng) ◄─────────────────────────┘
```

Kèm mã giả mô tả đầy đủ một vòng lặp huấn luyện.

#### 3.4.2. Giai đoạn kiểm thử

**Bảng 3.8. Đặc tả giai đoạn kiểm thử**

| Thành phần | Nội dung |
|---|---|
| Đầu vào | Tham số đã học, giữ cố định, kèm tư thế camera mới do người dùng chọn |
| Dữ liệu xác thực | Không có, vì đây là góc nhìn chưa từng chụp. Riêng khi đánh giá trên tập kiểm thử thì có, do tập này được giữ lại từ đầu |
| Đầu ra | Ảnh màu hoàn chỉnh ở góc nhìn mới |
| Lan truyền ngược | Không có, chỉ chạy một chiều thuận |

*Hình 3.8. Sơ đồ giai đoạn kiểm thử*

```
Tư thế mới → với MỖI điểm ảnh:
                sinh tia → lấy mẫu → Proposal MLP → lấy mẫu lại
                → NeRF MLP → volume rendering → một màu điểm ảnh
            → ghép toàn bộ điểm ảnh → ẢNH ĐẦU RA
```

Khác biệt giữa hai giai đoạn không chỉ nằm ở việc có hay không lan truyền ngược. Giai đoạn học lấy ngẫu nhiên một batch tia từ nhiều ảnh khác nhau, trong khi giai đoạn kiểm thử phải chạy toàn bộ điểm ảnh của một ảnh theo đúng thứ tự.

#### 3.4.3. Bảng siêu tham số

Trích đầy đủ từ công trình gốc: số vòng lặp, kích thước batch, tốc độ học và lịch giảm, hệ số của từng thành phần mất mát, kích thước mạng, số mẫu mỗi lượt.

### 3.5. Tổng hợp những thay đổi so với NeRF `[Sẵn sàng]` (khoảng 1 trang)

**Bảng 3.9. Đối chiếu Mip-NeRF 360 với NeRF theo công đoạn**

| Thành phần | Công đoạn | NeRF, 2020 | Mip-NeRF 360, 2022 | Nguồn cải tiến | Lý do | Hệ quả |
|---|---|---|---|---|---|---|
| Đơn vị lấy mẫu | CĐ3 | Tia mảnh | Hình nón cụt xấp xỉ bằng Gaussian | Mip-NeRF 2021 | Điểm ảnh là một vùng | Khử được răng cưa |
| Mã hóa đầu vào | CĐ2 | Positional encoding của điểm | Off-axis IPE của vùng | Mip-NeRF kết hợp phần mới của bản 360 | Phép co sinh Gaussian dị hướng | SSIM tăng từ 0,664 lên 0,687 |
| Không gian | CĐ2 | Tọa độ gốc | Scene contraction | Mới ở bản 360 | Nén vô cực vào miền hữu hạn | Hỗ trợ cảnh 360 độ |
| Lấy mẫu trên tia | CĐ3 | Tuyến tính theo tham số tia | Đều theo disparity | Mới ở bản 360 | Phân bổ mẫu hợp lý theo độ sâu | Cận xa vô hạn trở nên hợp lệ |
| Mạng dẫn đường | CĐ3 và CĐ4 | Mạng thô, dự đoán cả màu | Proposal MLP, chỉ dự đoán density | Mới ở bản 360 | Tách bạch vai trò | Huấn luyện nhanh khoảng ba lần |
| Chính quy hóa | CĐ4 | Không có | Distortion loss | Mới ở bản 360 | Chống vật thể ảo lơ lửng | Bản đồ độ sâu sạch hơn |

*Nguyên liệu:* `02-TaiLieuHoc/pipeline_MipNeRF360.md`, 1615 dòng, đã đối chiếu trực tiếp với công trình gốc.

---

## CHƯƠNG 4. CÀI ĐẶT VÀ THỬ NGHIỆM (khoảng 11 trang)

Chương này đáp ứng `phuongphap.rtf` mục 2.7, gồm môi trường cài đặt, tập dữ liệu, bảng kết quả và đánh giá.

**Lưu ý 6:** độ đo phải gồm cả độ chính xác lẫn độ phức tạp tính toán, và phải phân tích quan hệ giữa hàm mất mát với độ đo.
**Lưu ý 7:** mô tả tập dữ liệu phải nêu thách thức, số lượng mẫu, tính đa dạng và tiêu chí xây dựng.

### 4.1. Môi trường cài đặt (khoảng 1 trang)

#### 4.1.1. Ràng buộc phần cứng và cách xử lý

Máy cá nhân dùng chip Apple M2 Pro với 16 GB bộ nhớ, không có GPU NVIDIA và không hỗ trợ CUDA. Thư viện `tiny-cuda-nn` được viết bằng CUDA kernel nên không chạy được trên kiến trúc Apple Silicon. Giải pháp là dùng Google Colab hoặc Kaggle, nơi cung cấp GPU NVIDIA miễn phí.

**Bảng 4.1. Đối chiếu phần cứng**

| Nền tảng | Bộ xử lý | Bộ nhớ | Ghi chú |
|---|---|---|---|
| Máy cá nhân | Apple M2 Pro | 16 GB | Không chạy được CUDA |
| Google Colab | GPU NVIDIA được cấp | Tùy phiên | Ghi rõ model GPU thực tế nhận được |
| Công trình gốc | TPU v2, 32 nhân | | Phần cứng chuyên dụng của Google |

Bảng này giải thích trước mọi khác biệt về thời gian và kết quả sẽ xuất hiện tại mục 4.6.

#### 4.1.2. Phần mềm

Lập bảng liệt kê phiên bản Python, PyTorch, CUDA, nerfstudio và COLMAP, để người đọc tái lập được thử nghiệm.

### 4.2. Lựa chọn và điều chỉnh mã nguồn (khoảng 1 trang)

#### 4.2.1. Mã nguồn sử dụng

Bản triển khai gốc của nhóm tác giả là `multinerf`, viết bằng JAX. Báo cáo không dùng trực tiếp bản này vì nó yêu cầu TPU và thời gian huấn luyện vượt quá khuôn khổ đồ án. Bản được dùng thực tế là `nerfacto` của nerfstudio.

#### 4.2.2. Mức độ kế thừa của nerfacto

**Bảng 4.2. nerfacto kế thừa gì từ Mip-NeRF 360**

| Thành phần của Mip-NeRF 360 | nerfacto có kế thừa | Ghi chú |
|---|---|---|
| Scene contraction | Có | Giữ nguyên |
| Proposal network và online distillation | Có | Giữ nguyên |
| Distortion loss | Có | Giữ nguyên |
| Off-axis IPE | Không, thay bằng hash encoding | Đánh đổi để tăng tốc |
| MLP 8 lớp 1024 kênh | Không, thay bằng MLP nhỏ kết hợp hash grid | Đánh đổi để tăng tốc |

Nội dung bảng này bắt buộc phải trình bày trong báo cáo. Nếu giấu đi mà bị hỏi thì sẽ bị đánh giá thấp, trong khi trình bày trung thực kèm lý do lại cho thấy hiểu rõ cả hai phương pháp.

#### 4.2.3. Phần tự viết

Giảng viên yêu cầu tận dụng mã nguồn có sẵn và tự viết thêm. Phần tự viết gồm: script tiền xử lý dữ liệu tự chụp để lọc ảnh mờ, đổi kích thước và chuẩn hóa tên; script chạy COLMAP tự động kèm kiểm tra chất lượng tư thế; script đánh giá tính các chỉ số, đo thời gian, đếm số truy vấn mạng và xuất bảng; notebook tổng hợp để tái lập toàn bộ thử nghiệm; và script dựng video minh họa.

### 4.3. Tập dữ liệu (khoảng 2 trang)

#### 4.3.1. Tiêu chí xây dựng tập mẫu

Dữ liệu được chọn theo nguyên tắc phải chứa đúng thách thức mà phương pháp nhắm giải quyết, cụ thể là cảnh không giới hạn và chi tiết ở nhiều tỉ lệ khác nhau.

#### 4.3.2. Bộ dữ liệu chuẩn

Chọn một đến hai cảnh từ bộ Mip-NeRF 360.

**Bảng 4.3. Mô tả bộ dữ liệu chuẩn**

| Thuộc tính | Nội dung |
|---|---|
| Số lượng mẫu | Số ảnh huấn luyện và số ảnh kiểm thử |
| Độ phân giải | |
| Cách chia tập | Theo quy ước của công trình gốc, giữ lại mỗi ảnh thứ tám làm tập kiểm thử |
| Cách đánh nhãn | Tự giám sát, ảnh chụp chính là nhãn, không có khâu gán nhãn thủ công |
| Tính đa dạng | Gồm cả cảnh trong nhà và ngoài trời, có vật thể gần và nền xa |
| Thách thức chứa trong dữ liệu | Cảnh không giới hạn với nền trải tới chân trời, chi tiết ở nhiều tỉ lệ từ lá cây mảnh tới toàn cảnh, bề mặt phản chiếu, ánh sáng ngoài trời thay đổi giữa các ảnh, và vùng có ít ảnh quan sát |

#### 4.3.3. Bộ dữ liệu tự thu thập

Mô tả quy trình chụp gồm thiết bị, số lượng ảnh, cách di chuyển camera và điều kiện ánh sáng. Cảnh được chọn có chủ đích chứa cả vật thể gần lẫn nền xa và có bề mặt phản chiếu, nhằm kiểm chứng đúng khả năng mà Mip-NeRF 360 tuyên bố. Kèm Hình 4.1 giới thiệu một số ảnh mẫu, và phần ghi nhận các lỗi gặp phải khi chụp cùng cách khắc phục.

#### 4.3.4. Tiền xử lý bằng COLMAP

Bước này ứng với CĐ1. Quy trình gồm trích đặc trưng, khớp đặc trưng, tái tạo thưa và xuất tư thế camera. Kèm Hình 4.2 thể hiện đám mây điểm thưa và vị trí các camera. Cần ghi nhận số liệu chất lượng của CĐ1 gồm: số ảnh đăng ký thành công trên tổng số ảnh, số điểm ba chiều thu được, và sai số tái chiếu trung bình.

### 4.4. Độ đo đánh giá (khoảng 1,5 trang)

#### 4.4.1. Nhóm độ đo độ chính xác

**Bảng 4.4. Ba độ đo chất lượng ảnh**

| Độ đo | Đo đại lượng gì | Chiều tốt | Đặc điểm |
|---|---|---|---|
| PSNR | Sai khác điểm ảnh theo nghĩa số học, dẫn từ sai số bình phương trung bình | Càng cao càng tốt | Dễ tính nhưng không phản ánh cảm nhận thị giác |
| SSIM | Tương đồng về cấu trúc gồm độ sáng, tương phản và cấu trúc cục bộ | Càng cao càng tốt | Gần cảm nhận người hơn PSNR |
| LPIPS | Khác biệt theo cảm nhận, đo bằng đặc trưng của mạng đã huấn luyện sẵn | Càng thấp càng tốt | Gần cảm nhận người nhất |

#### 4.4.2. Nhóm độ đo độ phức tạp tính toán

**Bảng 4.5. Năm độ đo chi phí**

| Độ đo | Ý nghĩa |
|---|---|
| Thời gian huấn luyện | Số giờ cho mỗi cảnh, trên phần cứng cụ thể |
| Thời gian kết xuất | Số giây cho mỗi ảnh, hoặc số khung hình mỗi giây |
| Số lần truy vấn mạng mỗi tia | Độ phức tạp thuật toán, không phụ thuộc phần cứng |
| Số tham số mô hình | Dung lượng lưu trữ |
| Bộ nhớ GPU tiêu thụ khi huấn luyện | Ràng buộc khi triển khai thực tế |

Trong năm độ đo trên, số lần truy vấn mạng mỗi tia không phụ thuộc phần cứng, nên so sánh được giữa các công trình đo trên cấu hình khác nhau.

#### 4.4.3. Quan hệ giữa hàm mất mát và độ đo đánh giá

Giảng viên cảnh báo lỗi học một đằng đánh giá một nẻo tại Lưu ý 6. Mục này phân tích trực tiếp vấn đề đó.

**Bảng 4.6. Mức độ liên hệ giữa hàm mất mát và từng độ đo**

| Độ đo | Có được tối ưu trực tiếp không | Phân tích |
|---|---|---|
| PSNR | Có, quan hệ trực tiếp | Mất mát tái tạo là bình phương trung bình, trong khi PSNR được tính bằng logarit của tỉ số giữa giá trị cực đại và bình phương trung bình. Giảm bình phương trung bình tương đương tăng PSNR |
| SSIM | Không | Mô hình không tối ưu cấu trúc cục bộ. SSIM cải thiện chỉ là hệ quả gián tiếp |
| LPIPS | Không | Mô hình không tối ưu đặc trưng tri giác |

Ba hệ quả cần nêu. Thứ nhất, vì chỉ bình phương trung bình được tối ưu, mô hình có xu hướng cho ảnh hơi mờ, bởi ảnh mờ đều cho sai số bình phương thấp hơn ảnh sắc nét nhưng lệch chi tiết. Điều này giải thích vì sao PSNR cao mà LPIPS vẫn có thể kém. Thứ hai, nghiên cứu loại trừ của công trình gốc cho thấy bỏ mất mát distortion làm PSNR tăng nhẹ nhưng sinh ra vật thể ảo, minh chứng rằng tối ưu đúng độ đo chưa chắc cho kết quả tốt về mặt thị giác. Thứ ba, có thể đối chiếu với 3D Gaussian Splatting, phương pháp này dùng mất mát kết hợp L1 với D-SSIM, tức có tối ưu SSIM trực tiếp, khác với NeRF.

### 4.5. Kịch bản thử nghiệm (khoảng 0,5 trang)

**Bảng 4.7. Bốn kịch bản thử nghiệm**

| Mã | Mục đích | Dữ liệu | Cấu hình |
|---|---|---|---|
| TN1 | Đối chiếu với số liệu công bố | Một đến hai cảnh của bộ dữ liệu chuẩn | nerfacto mặc định |
| TN2 | Kiểm chứng trên dữ liệu tự thu thập | Bộ dữ liệu tự chụp | nerfacto mặc định |
| TN3 | So sánh với phương pháp đối chứng | Cùng dữ liệu TN2 | nerfacto so với instant-ngp |
| TN4 | Nghiên cứu loại trừ | Cùng dữ liệu TN2 | Bật và tắt distortion loss, thay đổi số mẫu proposal |

Mọi công trình hàng đầu đều có nghiên cứu loại trừ, nên TN4 đáng làm. Chỉ cần thực hiện một đến hai cấu hình là đủ chứng minh nhóm hiểu cơ chế chứ không chỉ chạy lệnh có sẵn.

### 4.6. Kết quả (khoảng 3 trang)

#### 4.6.1. Kết quả định lượng

Bảng 4.8 trình bày kết quả TN1, đối chiếu kết quả thu được với số liệu công bố trên cùng cảnh, gồm các cột PSNR, SSIM, LPIPS, thời gian huấn luyện và số vòng lặp. Bảng 4.9 trình bày kết quả TN2 và TN3, so sánh các phương pháp trên dữ liệu tự chụp, có kèm các cột về độ phức tạp tính toán gồm thời gian, tốc độ khung hình, số tham số và bộ nhớ tiêu thụ.

#### 4.6.2. Kết quả định tính

Hình 4.3 đặt cạnh nhau ba ảnh gồm ảnh thật, kết quả thu được và kết quả của phương pháp đối chứng, kèm khung phóng to vùng chi tiết. Hình 4.4 trình bày bản đồ độ sâu để kiểm tra hình học học được có sạch không và có vật thể ảo không. Hình 4.5 trích một số khung hình từ video quay camera quanh cảnh.

#### 4.6.3. Nghiên cứu loại trừ

**Bảng 4.10. Kết quả nghiên cứu loại trừ**

| Cấu hình | PSNR | SSIM | LPIPS | Thời gian | Quan sát định tính |
|---|---|---|---|---|---|
| Đầy đủ | | | | | |
| Bỏ distortion loss | | | | | Dự kiến các chỉ số không xấu đi nhiều nhưng bản đồ độ sâu xuất hiện vật thể ảo |
| Giảm số mẫu proposal | | | | | |

Nếu kết quả trùng với phát hiện của công trình gốc, cụ thể là bỏ distortion loss không làm PSNR xấu đi, thì đây là điểm mạnh của báo cáo vì nó chứng minh nhóm tái lập được đúng hành vi mà công trình mô tả, đồng thời minh họa trực tiếp cho phân tích tại mục 4.4.3.

### 4.7. Đánh giá và thảo luận (khoảng 2 trang)

Mục này trả lời bốn câu hỏi.

**Câu hỏi 1: kết quả có đạt như công bố không.** Nếu thấp hơn, phân tích các nguyên nhân gồm khác biệt phần cứng, khác biệt giữa nerfacto và bản triển khai gốc, số vòng lặp ít hơn, và độ khó của dữ liệu tự chụp.

**Câu hỏi 2: đánh giá theo từng công đoạn.** Mục này gắn kết quả thực nghiệm trở lại trục công đoạn xuyên suốt báo cáo.

**Bảng 4.11. Quan sát thực nghiệm theo công đoạn**

| Công đoạn | Nội dung cần ghi nhận |
|---|---|
| CĐ1 | Tỉ lệ ảnh được COLMAP đăng ký thành công, sai số tái chiếu, nguyên nhân các ảnh thất bại |
| CĐ2 | Dung lượng mô hình, mức độ đủ để biểu diễn chi tiết |
| CĐ3 | Thời gian kết xuất mỗi ảnh, số mẫu thực tế trên mỗi tia |
| CĐ4 | Dạng hội tụ của hàm mất mát, có xuất hiện vật thể ảo không, số vòng lặp cần thiết |

**Câu hỏi 3: nhiễu hình học quan sát được.** Ghi nhận vật thể ảo xuất hiện ở đâu, vùng nào bị mờ, rồi đối chiếu với các hạn chế mà công trình gốc tự nêu.

**Câu hỏi 4: hạn chế của chính quá trình thử nghiệm.** Gồm số cảnh ít, chưa chạy đủ số vòng lặp, và giới hạn thời gian phiên làm việc của Colab.

---

## CHƯƠNG 5. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN (khoảng 3 trang)

### 5.1. Kết luận (khoảng 1 trang)

Tóm tắt những việc đã thực hiện: khảo sát các phương pháp theo bốn công đoạn, trình bày chi tiết Mip-NeRF 360, cài đặt và thử nghiệm trên dữ liệu chuẩn cùng dữ liệu tự thu thập. Nêu kết quả chính kèm số liệu cụ thể. Cuối cùng là bài học rút ra, gồm bài học kỹ thuật về việc cơ chế nào thực sự quan trọng, và bài học quy trình về tầm quan trọng của việc dựng môi trường sớm cũng như đọc trực tiếp công trình gốc thay vì tài liệu thứ cấp.

### 5.2. Hạn chế của đồ án (khoảng 0,75 trang)

Trình bày trung thực theo ba nhóm. Hạn chế phần cứng gồm việc không có GPU riêng và phụ thuộc vào Colab với giới hạn thời gian phiên cũng như loại GPU được cấp. Hạn chế cài đặt là việc dùng nerfacto thay cho bản triển khai gốc, nên không tái lập chính xác hoàn toàn kết quả công bố. Hạn chế phạm vi gồm số cảnh thử nghiệm ít, chưa thử hết các cấu hình, và chưa so sánh được với toàn bộ phương pháp đã khảo sát ở Chương 2.

### 5.3. Hướng phát triển (khoảng 1,25 trang)

#### 5.3.1. Hướng kỹ thuật

Mỗi hướng viết một đoạn, nêu rõ nó giải quyết khuyết điểm nào ở công đoạn nào theo Bảng 2.7.

Zip-NeRF công bố tại ICCV 2023 kết hợp scene contraction và IPE ở CĐ2 cùng CĐ3 với hash grid ở CĐ2, qua đó khắc phục đúng khuyết điểm về độ phức tạp tính toán mà đồ án gặp phải. 3D Gaussian Splatting công bố tại SIGGRAPH 2023 chuyển CĐ3 sang rasterization để đạt thời gian thực. Mip-Splatting công bố tại CVPR 2024 mang cơ chế chống răng cưa sang 3D Gaussian Splatting. Hướng NeRF không cần tư thế nhắm giải quyết khuyết điểm ở CĐ1 là sự phụ thuộc vào chất lượng Structure-from-Motion.

#### 5.3.2. Hướng ứng dụng

Gồm số hóa một không gian cụ thể, tích hợp vào ứng dụng web xem ba chiều, và tối ưu để chạy trên thiết bị di động.

---

## TÀI LIỆU THAM KHẢO (khoảng 2 trang)

Gồm 16 tài liệu hiện có trong `03-Reference/`. Thống nhất dùng chuẩn IEEE, trích dẫn trong bài theo dạng số thứ tự trong ngoặc vuông.

## PHỤ LỤC

| Mã | Nội dung |
|---|---|
| PL A | Mã nguồn các script tự viết |
| PL B | Hướng dẫn tái lập thử nghiệm trên Colab |
| PL C | Bảng phân công công việc chi tiết |
| PL D | Ảnh và video kết quả bổ sung |

---

## BẢNG PHÂN CÔNG CÔNG VIỆC

Đáp ứng yêu cầu tại `phuongphap.rtf` mục 2.9. Nguyên tắc chia việc là hai hướng song song, gồm hướng lý thuyết và viết báo cáo, và hướng cài đặt và thực nghiệm. Chương 3 là trọng tâm nên cả hai thành viên cùng tham gia.

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
| 11 | Rà soát theo bảng kiểm 13 mục trong `yeu-cau-cua-thay.md` | Hoàn thiện slide, tập thuyết trình | Bản hoàn chỉnh |
| 12 | Dự phòng, sửa theo góp ý | Dự phòng, tập thuyết trình | Nộp và bảo vệ |

Rủi ro lớn nhất của đồ án là khâu dựng môi trường cài đặt ở Chương 4, do đó việc này được xếp vào tuần 1 thay vì tuần 8. Nếu hết tuần 2 vẫn chưa huấn luyện được bộ dữ liệu mẫu thì phải chuyển phương án ngay, chẳng hạn thuê GPU đám mây hoặc mượn máy có GPU NVIDIA.

---

## VIỆC CẦN LÀM NGAY

| Thứ tự | Việc | Lý do ưu tiên |
|---|---|---|
| 1 | Dựng môi trường Colab và huấn luyện thử bộ dữ liệu mẫu | Gỡ rủi ro lớn nhất, vì toàn bộ Chương 4 phụ thuộc vào khâu này |
| 2 | Gửi dàn ý cho giảng viên duyệt | Chi phí sửa hướng ở giai đoạn này là thấp nhất |
| 3 | Đọc ba survey để viết Chương 2 | Nguyên liệu đã sẵn, thực hiện được ngay, không phụ thuộc khâu khác |
| 4 | Đọc công trình Mip-NeRF 2021 | Bổ sung các nội dung chưa xác minh được tại mục 3.2 |

---

## BẢNG KIỂM ĐỐI CHIẾU TÁM LƯU Ý CỦA GIẢNG VIÊN

| Lưu ý | Yêu cầu | Vị trí đáp ứng trong dàn ý |
|---|---|---|
| 1 | Framework tổng quát, không nhắc phương pháp cụ thể | Mục 1.3.2, Bảng 1.1 chỉ nêu các hướng giải pháp khả dĩ |
| 2 | Xác định ẩn số từng công đoạn | Mục 1.3.3, Bảng 1.2 gồm dữ kiện đã cho, ẩn số, ràng buộc |
| 3 | So sánh theo cùng cột tiêu chí ứng với công đoạn | Mục 2.3 dùng khuôn năm mục chung, mục 2.4 Bảng 2.5 có cột là công đoạn |
| 4 | Dữ liệu xác thực, cách đánh nhãn, hàm mất mát | Mục 3.4.1, Bảng 3.7, nhấn mạnh tính tự giám sát |
| 5 | Tiến trình giai đoạn học và giai đoạn kiểm thử | Mục 3.4.1 và 3.4.2, hai sơ đồ riêng là Hình 3.7 và Hình 3.8 |
| 6 | Độ chính xác, độ phức tạp tính toán, quan hệ mất mát với độ đo | Mục 4.4 gồm ba mục con, trong đó 4.4.3 phân tích hiện tượng học một đằng đánh giá một nẻo |
| 7 | Tập dữ liệu: đánh nhãn, số mẫu, đa dạng, thách thức | Mục 1.3.5 Bảng 1.3 và mục 4.3 Bảng 4.3 |
| 8 | Khuyết điểm tồn đọng theo công đoạn | Mục 2.2.2 Bảng 2.3 và mục 2.5 Bảng 2.7 |
