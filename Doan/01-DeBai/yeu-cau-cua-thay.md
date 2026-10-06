# TOÀN BỘ YÊU CẦU CỦA GIẢNG VIÊN

> File này tổng hợp nguyên văn nội dung 4 file `.rtf` của thầy (PGS.TS Lý Quốc Ngọc) sang dạng markdown để tiện tra cứu trong suốt quá trình làm đồ án.
> **Mọi quyết định về nội dung báo cáo phải đối chiếu lại file này.**

Nguồn: `de.rtf`, `huongdantrinhbay.rtf`, `phuongphap.rtf`, `motsoluuyloi.rtf`

---

## 1. ĐỀ TÀI (`de.rtf`)

> Đồ án: Xây dựng ứng dụng kết xuất ảnh (rendering) với góc nhìn tùy ý dựa vào dãy ảnh 2D cho trước (Tìm hiểu mô hình NERF và NERF cải tiến)

---

## 2. CẤU TRÚC BÁO CÁO (`huongdantrinhbay.rtf`)

### Chương 1. Giới thiệu
- **1.1.** Ý nghĩa về khoa học của chủ đề
- **1.2.** Ý nghĩa về ứng dụng của chủ đề
- **1.3.** Phát biểu bài toán
  - Input, Output của hệ thống là gì
  - Framework chung của hệ thống gồm các công đoạn chính nào (**chưa đi vào pp cụ thể**)
- **1.4.** Đóng góp, Báo cáo được khảo sát nhằm đóng góp nội dung gì

### Chương 2. Các công trình nghiên cứu liên quan
- Chọn lọc các công trình liên quan đến chủ đề
- Trình bày quá trình phát triển của các giải pháp liên quan đến chủ đề
- Lập bảng so sánh các giải pháp dựa trên một số tiêu chí tự chọn
- Nhằm trả lời được 2 câu hỏi: **Người ta đã làm gì rồi** và **mình muốn làm gì**

### Chương 3. Phương pháp
- Chọn lấy **một** giải pháp tiên tiến để trình bày

### Chương 4. Cài đặt và thử nghiệm
- Tận dụng source code có sẵn **và tự viết** để minh họa giải pháp ở chương 3

### Chương 5. Kết luận và hướng phát triển

---

## 3. QUY TRÌNH LÀM ĐỒ ÁN (`phuongphap.rtf`)

### Mục đích & Yêu cầu
- Giúp SV có trải nghiệm thực tế trong nghiên cứu ứng dụng và làm việc nhóm
- **SV chỉ cần đọc, hiểu, cài đặt lại. Chưa đòi hỏi đề xuất giải pháp mới.**

### Các bước cần tiến hành

| Bước | Nội dung |
|---|---|
| 2.1 | Đọc kỹ tên đề tài |
| 2.2 | Xác định các từ khóa (keyword) để tìm tài liệu |
| 2.3 | Tích cực tìm kiếm tài liệu & đọc hiểu, ưu tiên hội nghị/tạp chí uy tín (CVPR, ICCV, IJCV...), luận văn Th.S, luận án TS. Dùng từ khóa *Survey / Overview / Literature Review / Comprehensive Study* + chủ đề. Hoặc "paper with codes" |
| 2.4 | **Phát biểu bài toán:** Input, Output là gì? Các tác vụ cần thực hiện là gì? Tập dữ liệu thử nghiệm (standard dataset) |
| 2.5 | **Khảo sát tổng quan:** trả lời 2 câu hỏi: Người ta đã làm gì rồi? Đồ án muốn làm gì tiếp? |
| 2.6 | **Giải pháp:** chọn phương pháp tiên tiến đã công bố để trình bày lại. Trình tự theo mạch logic: **nguyên lý -> phương pháp -> giải thuật -> CT minh họa** |
| 2.7 | **Cài đặt:** môi trường cài đặt (phần cứng, phần mềm); tập dữ liệu thử nghiệm; bảng kết quả thử nghiệm; đánh giá kết quả |
| 2.8 | Viết báo cáo (Doc, Slide) |
| 2.9 | **Phân công:** lập bảng phân công công việc cho từng thành viên với các cột mốc thời gian cụ thể |

---

## 4. TÁM LỖI THƯỜNG GẶP CẦN TRÁNH (`motsoluuyloi.rtf`)

> Đây là tài liệu quan trọng nhất. Thầy liệt kê chính xác những lỗi sẽ bị trừ điểm. Mỗi mục gồm *yêu cầu* và *lỗi thường gặp*.

### Lưu ý 1. Framework chung phải tổng quát

**Yêu cầu:** Trong phát biểu bài toán, cần xác định framework chung cho hệ thống, gồm các công đoạn chính nào (chưa đi vào phương pháp cụ thể).

**Lỗi thường gặp:** Xác định luôn phương pháp cụ thể trong framework. Làm như vậy sẽ không thấy được nhiều giải pháp có thể có trong các công đoạn, hạn chế sự sáng tạo.

-> Áp dụng: framework chỉ nêu "ước lượng tham số camera", KHÔNG được viết "dùng COLMAP". Chỉ nêu "biểu diễn cảnh", KHÔNG viết "dùng MLP".

---

### Lưu ý 2. Phải xác định ẩn số trong từng công đoạn

**Yêu cầu:** Trong phát biểu bài toán, cần xác định được **các ẩn số phải tìm** trong các công đoạn.

**Lỗi thường gặp:** Không xác định được các ẩn số phải tìm trong các công đoạn. Làm như vậy sẽ không hiểu được các giải pháp đã được công bố.

-> Áp dụng: mỗi công đoạn phải nêu rõ: **biết gì (đã cho)** và **cần tìm gì (ẩn số)**.

---

### Lưu ý 3. Related works so sánh theo CÙNG cột tiêu chí, ỨNG VỚI các công đoạn

**Yêu cầu:** Trong related works, cần nêu được các giải pháp SOTA và so sánh chúng với **cùng các cột tiêu chí theo các công đoạn** đã nêu trong phát biểu bài toán.

**Lỗi thường gặp:**
- Mỗi giải pháp được trình bày với dàn bài khác nhau -> rất khó so sánh giải pháp này với giải pháp khác
- Không trình bày các giải pháp ứng với các công đoạn ở mục phát biểu bài toán -> khó nhận biết các giải pháp đã đóng góp thế nào trong các công đoạn

-> Áp dụng: bảng so sánh phải có **cột = công đoạn**, hàng = phương pháp. Mỗi phương pháp mô tả theo **cùng một khuôn** bám theo công đoạn.

---

### Lưu ý 4. Giai đoạn học: ground truth, đánh nhãn, loss function

**Yêu cầu:** Trong giai đoạn học, cần nêu rõ **input, output xác thực (groundtruth)** là gì, **được đánh nhãn như thế nào**, và **loss function** là gì nhằm tối ưu các thông số của mạng.

**Lỗi thường gặp:** Không đá động gì đến output xác thực, và được dùng như thế nào trong giai đoạn học.

-> Áp dụng: phải nói rõ với NeRF thì ground truth chính là **màu pixel của ảnh đã chụp:** tức dữ liệu **tự giám sát (self-supervised)**, không cần đánh nhãn thủ công. Đây là đặc điểm quan trọng phải nêu.

---

### Lưu ý 5. Trình bày rõ tiến trình giai đoạn học VÀ giai đoạn kiểm thử

**Yêu cầu:** Trong giai đoạn học và giai đoạn kiểm thử, cần trình bày rõ **tiến trình hoạt động của hệ thống** để ra được kết quả mong muốn.

**Lỗi thường gặp:** Không cho thấy được hệ thống hoạt động như thế nào để ra được kết quả.

-> Áp dụng: tách rõ **2 sơ đồ**: sơ đồ giai đoạn học (có backpropagation, có ground truth) và sơ đồ giai đoạn kiểm thử (chỉ forward, không có ground truth).

---

### Lưu ý 6. Độ đo phải có CẢ độ chính xác LẪN độ phức tạp tính toán

**Yêu cầu:** Trong giai đoạn đánh giá hiệu suất (performance), cần xác định độ đo đánh giá về **độ chính xác** và **cả độ phức tạp tính toán**.

**Lỗi thường gặp:**
- Không hiểu về độ đo đánh giá, độ phức tạp tính toán
- **Không hiểu loss function có liên quan gì đến độ đo đánh giá** -> có thể dẫn đến tình trạng **"học một đằng, đánh giá một nẻo"**

-> Áp dụng: phải phân tích mối liên hệ giữa loss (MSE) và độ đo (PSNR có quan hệ trực tiếp với MSE; SSIM/LPIPS thì KHÔNG được tối ưu trực tiếp). Phải nêu độ phức tạp tính toán: số phép truy vấn mạng/tia, thời gian train, thời gian render, bộ nhớ.

---

### Lưu ý 7. Mô tả tập dữ liệu phải nêu được THÁCH THỨC

**Yêu cầu:** Cần chú ý nhiều hơn trong mô tả **tập dữ liệu học**, **tập dữ liệu kiểm thử**: công tác đánh nhãn như thế nào, **số lượng mẫu**, **tính đa dạng của mẫu**, **tiêu chí xây dựng tập mẫu**.

**Lỗi thường gặp:**
- Không cho thấy tập dữ liệu chứa các **thách thức** gì. Nếu tập dữ liệu không chứa các thách thức của bài toán thì **dù hệ thống đạt performance rất cao cũng không thể khẳng định đây là giải pháp tốt**
- Không hiểu được cách đánh nhãn dữ liệu như thế nào

-> Áp dụng: với mỗi dataset phải nêu rõ nó chứa thách thức gì (cảnh unbounded, vật thể mảnh, bề mặt phản chiếu, ánh sáng thay đổi, vùng ít ảnh quan sát...).

---

### Lưu ý 8. Related works phải chỉ ra khuyết điểm tồn đọng THEO CÔNG ĐOẠN

**Yêu cầu:** Trong related works, cần **nhìn ra các khuyết điểm còn tồn đọng cần giải quyết trong các công đoạn**.

**Lỗi thường gặp:**
- Chưa nhìn ra được cần cải tiến nội dung gì trong các công đoạn
- Cần cải tiến **độ chính xác** hay **độ phức tạp tính toán**

-> Áp dụng: cuối Chương 2 phải có bảng: mỗi công đoạn còn khuyết điểm gì, thuộc loại *độ chính xác* hay *độ phức tạp tính toán*, và phương pháp nào đang giải quyết tới đâu.

---

## 5. BẢNG KIỂM TRA NHANH TRƯỚC KHI NỘP

Đối chiếu báo cáo với 8 lưu ý, đánh dấu khi đã đạt:

- [ ] **Lưu ý 1:** Framework ở mục 1.3 chỉ nêu công đoạn tổng quát, không nhắc tên phương pháp cụ thể
- [ ] **Lưu ý 2:** Mỗi công đoạn có nêu rõ: đã cho gì, ẩn số cần tìm là gì
- [ ] **Lưu ý 3:** Bảng so sánh ở Chương 2 có cột ứng với các công đoạn; mọi phương pháp mô tả theo cùng một khuôn
- [ ] **Lưu ý 4:** Có nêu rõ ground truth là gì, cách "đánh nhãn", loss function
- [ ] **Lưu ý 5:** Có 2 sơ đồ riêng cho giai đoạn học và giai đoạn kiểm thử
- [ ] **Lưu ý 6:** Có cả độ đo chính xác lẫn độ phức tạp tính toán; có phân tích quan hệ loss ↔ độ đo
- [ ] **Lưu ý 7:** Mô tả dataset có nêu thách thức, số mẫu, tính đa dạng, tiêu chí xây dựng
- [ ] **Lưu ý 8:** Cuối Chương 2 có bảng khuyết điểm tồn đọng theo từng công đoạn, phân loại độ chính xác / độ phức tạp
- [ ] **phuongphap.rtf 2.6:** Chương 3 trình bày theo mạch: nguyên lý -> phương pháp -> giải thuật -> CT minh họa
- [ ] **phuongphap.rtf 2.7:** Chương 4 có đủ: môi trường (phần cứng + phần mềm), dataset, bảng kết quả, đánh giá
- [ ] **phuongphap.rtf 2.9:** Có bảng phân công theo mốc thời gian
- [ ] **huongdantrinhbay:** Chương 4 có cả code tận dụng sẵn **và code tự viết**
- [ ] **Phạm vi:** Không tuyên bố "đề xuất phương pháp mới" (thầy ghi rõ chưa yêu cầu)
