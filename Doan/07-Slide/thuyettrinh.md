# Kịch bản thuyết trình (15 phút) – Chương 1 & Chương 2

- **Đề tài:** Xây dựng ứng dụng kết xuất ảnh với góc nhìn tùy ý dựa vào ảnh 2D cho trước – Tìm hiểu mô hình NeRF và NeRF cải tiến
- **Giảng viên hướng dẫn:** PGS.TS Lý Quốc Ngọc
- **Thành viên:** Bùi Văn Thiên (24120138) – Nguyễn Minh Khoa (24120073)
- **Tài liệu đối chiếu:** `07-Slide/slide.pptx` (17 slide) và `06-BaoCao/bao-cao.docx` (Chương 1, Chương 2)
- **Thời lượng mục tiêu:** 15 phút 00 giây (~2.050 từ, tốc độ nói ~135–140 từ/phút)

---

## Bảng phân bổ thời gian

| Phần | Slide | Thời lượng | Mốc thời gian |
|---|---|---:|---|
| Mở đầu & mục lục | Slide 1 – 2 | 1 phút 00 giây | `00:00 – 01:00` |
| Phần I: Giới thiệu đề tài (Chương 1) | Slide 3 – 7 | 5 phút 20 giây | `01:00 – 06:20` |
| Phần II: Công trình nghiên cứu liên quan (Chương 2) | Slide 8 – 13 | 6 phút 30 giây | `06:20 – 12:50` |
| Phần III: Đánh giá định lượng & lựa chọn phương pháp | Slide 14 – 16 | 2 phút 00 giây | `12:50 – 14:50` |
| Kết thúc & cảm ơn | Slide 17 | 0 phút 10 giây | `14:50 – 15:00` |

> **Quy ước đọc kịch bản:** Câu **in đậm** ở cuối mỗi slide là câu chốt làm tín hiệu để bấm chuyển sang slide tiếp theo ngay tại dòng `> [BẤM CHUYỂN SANG SLIDE X]`.

---

## Nội dung thuyết trình chi tiết

### SLIDE 1 – Trang bìa *(00:00 – 00:30 | 30 giây)*

Em xin kính chào thầy Lý Quốc Ngọc và toàn thể các bạn. Hôm nay, nhóm em gồm hai thành viên là Bùi Văn Thiên và Nguyễn Minh Khoa xin đại diện trình bày báo cáo đồ án môn học Đồ họa Máy tính với đề tài: *"Xây dựng ứng dụng kết xuất ảnh với góc nhìn tùy ý dựa vào ảnh 2D cho trước – Tìm hiểu mô hình NeRF và các mô hình NeRF cải tiến"*. **Sau đây em xin điểm qua cấu trúc chính của bài trình bày hôm nay.**

> **[BẤM CHUYỂN SANG SLIDE 2 – Nội dung báo cáo]**

---

### SLIDE 2 – Nội dung báo cáo *(00:30 – 01:00 | 30 giây)*

Nội dung thuyết trình của nhóm được tổ chức thành ba phần chính. Phần thứ nhất, chúng em giới thiệu tổng quan đề tài, ý nghĩa khoa học, thực tiễn và phát biểu bài toán theo khung bốn công đoạn. Phần thứ hai trình bày các công trình nghiên cứu liên quan, đi từ các phương pháp trước NeRF, nguyên lý và hạn chế của NeRF gốc cho đến các hướng cải tiến nổi bật. Phần thứ ba là so sánh định lượng và lý do nhóm lựa chọn mô hình khảo sát cho đồ án. **Đầu tiên, mời thầy và các bạn bước vào phần một: Giới thiệu đề tài.**

> **[BẤM CHUYỂN SANG SLIDE 3 – I. Giới thiệu đề tài]**

---

### SLIDE 3 – I. Giới thiệu đề tài *(01:00 – 01:10 | 10 giây)*

**Trong phần đầu tiên này, nhóm sẽ làm rõ vì sao bài toán tổng hợp góc nhìn mới lại quan trọng cả về mặt học thuật lẫn ứng dụng thực tế.**

> **[BẤM CHUYỂN SANG SLIDE 4 – Ý nghĩa khoa học]**

---

### SLIDE 4 – Ý nghĩa khoa học *(01:10 – 02:25 | 1 phút 15 giây)*

Về mặt khoa học, con người chỉ cần nhìn một vật thể từ vài góc độ khác nhau là đã có thể hình dung được hình dạng ba chiều của nó. Tuy nhiên, với máy tính, đây là bài toán rất khó vì ảnh chụp hai chiều đã làm mất thông tin độ sâu: một điểm ảnh trên hình chiếu có thể tương ứng với vô số điểm ba chiều nằm dọc theo tia nhìn. Bài toán tổng hợp góc nhìn mới ra đời nhằm khôi phục khả năng hiểu không gian ba chiều đó cho máy tính.

Trước đây, các hướng tiếp cận truyền thống như Light Field, lưới tam giác, voxel hay hàm khoảng cách có dấu đều gặp rào cản riêng về số lượng ảnh, dung lượng bộ nhớ hoặc yêu cầu có sẵn dữ liệu hình học 3D chuẩn. Năm 2020, mô hình NeRF ra đời đã giải quyết đồng thời các rào cản này: mô hình học tự giám sát chỉ từ ảnh màu 2D kèm tư thế camera, nén toàn bộ cảnh 3D xuống chỉ khoảng 5 megabyte trọng số mạng nơ-ron, nhỏ hơn tới 3.000 lần so với lưới voxel của phương pháp LLFF cho cùng một cảnh, nhưng vẫn tạo ra ảnh góc nhìn mới chân thực ở độ phân giải cao. Bước đột phá đó đã tạo ra làn sóng nghiên cứu bùng nổ với hơn 1.300 trích dẫn và trên 150 công trình kế thừa chỉ sau hai năm công bố. **Không chỉ có ý nghĩa lớn về khoa học, khả năng tái tạo 3D từ ảnh chụp thông thường còn mở ra rất nhiều ứng dụng thực tiễn.**

> **[BẤM CHUYỂN SANG SLIDE 5 – Ý nghĩa thực tiễn]**

---

### SLIDE 5 – Ý nghĩa thực tiễn *(02:25 – 03:40 | 1 phút 15 giây)*

Điểm hấp dẫn nhất của NeRF trong thực tế là người dùng không cần tới các thiết bị quét laser hay máy quét 3D đắt tiền mà vẫn dựng lại được không gian ba chiều chân thực. Trên slide là bốn nhóm ứng dụng tiêu biểu mà nhóm đã tổng hợp từ các nghiên cứu công bố.

Thứ nhất, trong thực tế ảo VR và thực tế tăng cường AR, NeRF giúp tạo môi trường 3D trực tiếp từ ảnh chụp thay vì phải dựng hình thủ công tốn nhiều công sức. Thứ hai, trong số hóa di sản và bảo tồn hiện vật, nghiên cứu của Croce và cộng sự trên các hiện vật như bức tượng Terpsichore cho thấy khi không được phép tiếp xúc trực tiếp hoặc số ảnh chụp bị hạn chế, NeRF giữ được độ hoàn chỉnh bề mặt và vật liệu tốt hơn so với đo ảnh truyền thống. Thứ ba, ở mảng thương mại điện tử, bất động sản và du lịch, các mô hình như Mega-NeRF đã tái tạo toàn bộ tòa nhà hay khu phố từ ảnh drone; điển hình nhất ngoài thực tế là tính năng Immersive View của Google Maps ứng dụng NeRF để dựng mô hình 3D tại năm thành phố lớn như London, New York và Tokyo từ đầu năm 2023. Cuối cùng, trong robot học và kỹ xảo điện ảnh, NeRF hỗ trợ dựng bản đồ môi trường bằng camera chi phí thấp và đã được tích hợp vào các công cụ sản xuất ảo như Unreal Engine. **Để giải quyết các ứng dụng này một cách có hệ thống, chúng ta cần phát biểu chặt chẽ bài toán dưới góc độ kỹ thuật.**

> **[BẤM CHUYỂN SANG SLIDE 6 – Phát biểu bài toán]**

---

### SLIDE 6 – Phát biểu bài toán *(03:40 – 04:40 | 1 phút 00 giây)*

Bài toán tổng hợp góc nhìn mới được phát biểu cụ thể qua đầu vào, quá trình xử lý và đầu ra như sau.

Đầu vào của hệ thống là một tập ảnh màu 2D, thường từ 20 đến 100 ảnh, thỏa mãn hai ràng buộc quan trọng. Ràng buộc thứ nhất là cảnh phải tĩnh trong suốt quá trình chụp, vật thể không dịch chuyển và ánh sáng không đổi, bởi hệ thống sẽ rất khó phân biệt giữa chuyển động của vật thể với chuyển động của camera. Ràng buộc thứ hai là các ảnh phải có vùng nội dung trùng lặp đủ lớn để tìm được cùng một điểm vật lý trên nhiều khung hình, làm cơ sở suy ra vị trí camera.

Từ tập ảnh đầu vào này, hệ thống trải qua một quy trình xử lý gồm bốn công đoạn nối tiếp để học biểu diễn của cảnh. Đầu ra thu được là ảnh màu kết xuất tại một góc nhìn tùy ý do người dùng chọn, kể cả những góc chưa từng xuất hiện khi chụp; từ đó có thể ghép chuỗi ảnh liên tiếp thành video quay quanh cảnh hoặc trích xuất thành lưới tam giác 3D. **Vậy cụ thể bốn công đoạn trong quy trình này thực hiện nhiệm vụ gì và giải ẩn số nào? Mời thầy và các bạn xem slide tiếp theo.**

> **[BẤM CHUYỂN SANG SLIDE 7 – Quy trình tổng hợp góc nhìn mới]**

---

### SLIDE 7 – Quy trình tổng hợp góc nhìn mới *(04:40 – 06:20 | 1 phút 40 giây)*

Ở mức tổng quát, mọi phương pháp giải bài toán tổng hợp góc nhìn mới đều bám theo khung bốn công đoạn, và mỗi công đoạn gắn với một ẩn số cần tìm riêng biệt.

Ở Công đoạn 1, ước lượng tham số camera: từ tập ảnh 2D đầu vào, hệ thống xác định vị trí, hướng nhìn và thông số ống kính của từng ảnh, tức là tìm ba ẩn số gồm ma trận nội tại $K_i$, ma trận xoay $R_i$ và tâm camera $C_i$. Ràng buộc dùng để giải là cùng một điểm 3D khi chiếu lên nhiều ảnh phải khớp vị trí quan sát, hay nói cách khác là tối thiểu hóa sai số tái chiếu, thường thực hiện bằng Structure-from-Motion.

Ở Công đoạn 2, biểu diễn cảnh 3D: hệ thống lựa chọn một cấu trúc dữ liệu hoặc hàm số để mô tả cảnh trong không gian, có thể là biểu diễn tường minh như lưới tam giác, voxel, Gaussian hoặc biểu diễn ẩn như mạng MLP, hash grid, tensor. Ẩn số cần tìm ở đây chính là bộ tham số $\Theta$ của biểu diễn đó.

Ở Công đoạn 3, kết xuất ảnh: từ biểu diễn cảnh cùng một tư thế camera cho trước, hệ thống tạo ra ảnh 2D tương ứng thông qua các kỹ thuật như ray marching kết hợp volume rendering hoặc splatting. Công đoạn này không học thêm ẩn số mới mà cần lựa chọn thuật toán kết xuất phù hợp, đặc biệt phải có tính khả vi theo tham số $\Theta$ để truyền ngược sai số.

Cuối cùng ở Công đoạn 4, tối ưu hóa: hệ thống so sánh ảnh kết xuất với ảnh thật cùng góc nhìn bằng hàm mất mát, tính đạo hàm ngược và dùng Gradient Descent để cập nhật bộ tham số $\Theta$. Như vậy, Công đoạn 2 và Công đoạn 4 liên hệ rất chặt chẽ: Công đoạn 2 định nghĩa ẩn số $\Theta$, còn Công đoạn 4 chính là nơi đi giải tìm $\Theta$ tối ưu qua vòng lặp kết xuất và cập nhật. **Dựa trên khung bốn công đoạn này, nhóm xin chuyển sang phần hai: Khảo sát các công trình nghiên cứu liên quan.**

> **[BẤM CHUYỂN SANG SLIDE 8 – II. Các công trình nghiên cứu liên quan]**

---

### SLIDE 8 – II. Các công trình nghiên cứu liên quan *(06:20 – 06:30 | 10 giây)*

**Trong phần hai, chúng em sẽ lần lượt đi qua các bộ dữ liệu chuẩn dùng để đánh giá, các phương pháp trước NeRF, mô hình NeRF gốc và các hướng cải tiến giai đoạn 2020–2024.**

> **[BẤM CHUYỂN SANG SLIDE 9 – Các bộ dữ liệu đánh giá]**

---

### SLIDE 9 – Các bộ dữ liệu đánh giá *(06:30 – 07:30 | 1 phút 00 giây)*

Trước khi so sánh các thuật toán, cần nhìn vào ba bộ dữ liệu chuẩn phổ biến nhất mà cộng đồng dùng để kiểm chứng bài toán này.

Đầu tiên là bộ NeRF-Synthetic hay còn gọi là Blender dataset gồm 8 cảnh vật thể tổng hợp quay 360 độ như Chair, Lego hay Ship. Tuy là dữ liệu tổng hợp nhưng bộ này thử thách mô hình ở vật liệu phản chiếu phi Lambert và các chi tiết hình học mảnh như dây hay bánh răng. Tiếp theo là bộ Real Forward-Facing gồm 8 cảnh chụp thực tế với góc nhìn chủ yếu hướng về phía trước, mang theo nhiễu ảnh thực, vùng che khuất và chiều sâu kéo dài từ gần tới xa. Khó nhất là bộ Mip-NeRF 360 gồm 9 cảnh thực, với 5 cảnh ngoài trời và 4 cảnh trong nhà. Đây là các cảnh 360 độ không giới hạn với nền trải dài tới chân trời, chứa chi tiết đa tỉ lệ, ánh sáng ngoài trời biến đổi và nhiều vùng ít góc quan sát. **Trên nền các bài toán dữ liệu như vậy, các phương pháp trước khi NeRF xuất hiện đã tiếp cận như thế nào?**

> **[BẤM CHUYỂN SANG SLIDE 10 – Các phương pháp trước NeRF]**

---

### SLIDE 10 – Các phương pháp trước NeRF *(07:30 – 08:50 | 1 phút 20 giây)*

Nhóm phân các phương pháp trước NeRF thành bốn hướng chính.

Hướng thứ nhất là Light Field, lưu trữ trực tiếp ánh sáng dưới dạng hàm bốn chiều từ tập ảnh đã chụp rồi nội suy ra góc nhìn mới. Cách này cho ảnh mượt nhưng đòi hỏi dữ liệu lấy mẫu phải rất dày; nếu góc nhìn mới nằm ngoài vùng bao phủ hoặc ảnh chụp thưa thì chất lượng giảm mạnh.

Hướng thứ hai là biểu diễn bằng lưới tam giác, kết hợp SfM và Multi-View Stereo để dựng bề mặt gồm đỉnh, cạnh, mặt rồi chiếu lên ảnh. Điểm yếu là kết quả phụ thuộc hoàn toàn vào chất lượng tái tạo hình học ban đầu; nếu thiếu góc chụp sẽ dễ bị thủng bề mặt, mất chi tiết hoặc rơi vào cực tiểu địa phương khi tối ưu.

Hướng thứ ba là lưới Voxel, chia không gian 3D thành các ô nhỏ lưu màu sắc và mật độ rồi kết xuất thể tích. Dù tránh được ràng buộc topo của lưới tam giác, chi phí bộ nhớ của voxel lại tăng theo lập phương $N^3$ khi nâng độ phân giải, khiến việc lưu giữ chi tiết nhỏ trở nên cực kỳ tốn kém.

Hướng thứ tư là Neural SDF, dùng mạng nơ-ron dự đoán khoảng cách có dấu tới bề mặt. Tuy nhỏ gọn hơn voxel, hướng này vẫn gặp khó với các chi tiết rất mỏng, vùng che khuất hoặc bề mặt phản chiếu phức tạp, và thường đòi hỏi chất lượng ảnh cùng độ chính xác camera rất cao. **Chính những giới hạn này đã mở đường cho sự ra đời của NeRF vào năm 2020.**

> **[BẤM CHUYỂN SANG SLIDE 11 – Nguyên lý hoạt động của NeRF]**

---

### SLIDE 11 – Nguyên lý hoạt động của NeRF *(08:50 – 10:10 | 1 phút 20 giây)*

Đặt vào khung bốn công đoạn, NeRF hoạt động theo một mạch rất nhất quán. Sau khi có tư thế camera từ Công đoạn 1, ở Công đoạn 2, thay vì dựng lưới hay lưu voxel, NeRF biểu diễn toàn bộ cảnh bằng một trường bức xạ liên tục học bởi mạng MLP 8 lớp ẩn. Mạng nhận vào tọa độ điểm 3D $X = (x, y, z)$ và hướng nhìn $d$. Trước khi đưa qua MLP, đầu vào được ánh xạ qua hàm Positional Encoding để mạng học được các chi tiết tần số cao sắc nét. Đầu ra của mạng là mật độ thể tích $\sigma$ và màu sắc phát xạ $c$ phụ thuộc góc nhìn.

Sang Công đoạn 3, với mỗi pixel cần vẽ, hệ thống phóng một tia từ tâm camera, lấy mẫu nhiều điểm dọc tia từ cận gần $t_n$ đến cận xa $t_f$ rồi dùng công thức Volume Rendering cộng dồn màu sắc theo độ chặn sáng của các điểm phía trước. Đặc biệt, NeRF gốc dùng lấy mẫu phân cấp gồm hai mạng: mạng thô Coarse lấy 64 điểm để xác định vùng có vật thể, sau đó mạng tinh Fine lấy thêm 128 điểm tập trung vào vùng đó, tổng cộng 192 điểm.

Cuối cùng ở Công đoạn 4, ảnh kết xuất được so với ảnh thật bằng hàm mất mát MSE, lan truyền ngược qua quy trình kết xuất khả vi và tối ưu trọng số mạng bằng Adam. Khi học xong, trọng số được giữ cố định để tổng hợp bất kỳ góc nhìn mới nào. **Tuy tạo ra bước nhảy vọt về chất lượng, bản thân NeRF gốc vẫn tồn tại năm hạn chế lớn.**

> **[BẤM CHUYỂN SANG SLIDE 12 – Hạn chế của NeRF]**

---

### SLIDE 12 – Hạn chế của NeRF *(10:10 – 11:25 | 1 phút 15 giây)*

Bảng trên slide tóm tắt năm hạn chế lớn của NeRF gắn với nguyên nhân kỹ thuật ở từng công đoạn.

Hai hạn chế rõ rệt nhất nằm ở chi phí tính toán. Thứ nhất là huấn luyện rất chậm, thường mất từ 1 đến 2 ngày cho một cảnh, do mạng MLP phải tính toán và lan truyền ngược qua hàng loạt điểm mẫu trong hàng trăm nghìn vòng lặp. Thứ hai là kết xuất ảnh chậm, chưa đạt thời gian thực, bởi mỗi tia pixel phải đánh giá qua hai mạng Coarse và Fine với tổng cộng 64 cộng 192 bằng 256 lượt truy vấn MLP.

Hai hạn chế tiếp theo thuộc về chất lượng biểu diễn không gian. Thứ ba là hiện tượng răng cưa hoặc nhòe khi đổi độ phân giải hay khoảng cách quan sát, vì NeRF mô hình hóa mỗi pixel như một tia mảnh không có bề rộng thay vì một vùng không gian thực tế. Thứ tư là kém hiệu quả với cảnh 360 độ không giới hạn do cách tham số hóa và lấy mẫu chưa phân bổ tốt cho cả tiền cảnh gần lẫn hậu cảnh trải rất xa.

Hạn chế thứ năm nằm ngay ở Công đoạn 1: chất lượng tái tạo phụ thuộc mạnh vào độ chính xác của tư thế camera; chỉ cần ước lượng vị trí hoặc góc xoay sai lệch, các tia sẽ không giao đúng điểm vật lý và làm mờ ảnh. **Để khắc phục năm nhóm hạn chế này, rất nhiều mô hình cải tiến đã lần lượt ra đời.**

> **[BẤM CHUYỂN SANG SLIDE 13 – Các phương pháp cải tiến từ NeRF]**

---

### SLIDE 13 – Các phương pháp cải tiến từ NeRF *(11:25 – 12:50 | 1 phút 25 giây)*

Nhóm tổng hợp bảy công trình tiêu biểu nhất phát triển từ nền tảng NeRF, có thể chia thành ba hướng cải tiến rõ rệt theo công đoạn tác động.

Nhóm thứ nhất tập trung nâng cao chất lượng hình ảnh và xử lý cảnh không giới hạn. Mip-NeRF năm 2021 thay tia mảnh bằng hình nón cụt và dùng Integrated Positional Encoding để khử răng cưa. NeRF++ tách cảnh thành vùng tiền cảnh trong khối cầu và vùng nền bên ngoài để xử lý cảnh 360 độ. Kết hợp cả hai hướng này, Mip-NeRF 360 năm 2022 dùng tham số hóa phi tuyến scene contraction, mạng đề xuất proposal cùng hai hàm mất mát bổ sung là interlevel loss và distortion loss để xử lý tốt cảnh 360 độ không giới hạn.

Nhóm thứ hai đánh thẳng vào nút thắt tốc độ huấn luyện và kết xuất. Plenoxels bỏ hẳn mạng MLP, lưu trực tiếp mật độ và hệ số điều hòa cầu trên lưới voxel thưa. TensoRF phân rã lưới đặc trưng 3D thành các thành phần tensor hạng thấp để giảm mạnh bộ nhớ và thời gian học. Nổi bật trong nhánh này là Instant-NGP tại SIGGRAPH 2022, thay Positional Encoding bằng bảng băm đa độ phân giải kết hợp MLP rất nhỏ ở Công đoạn 2, đồng thời dùng Occupancy Grid bỏ qua vùng không gian trống ở Công đoạn 3.

Nhóm thứ ba là bước rẽ sang biểu diễn tường minh với 3D Gaussian Splatting năm 2023, biểu diễn cảnh bằng các Gaussian 3D và dùng thuật toán splatting để chiếu trực tiếp lên ảnh, đạt tốc độ kết xuất rất nhanh. **Từ bức tranh tổng quan này, nhóm tiến hành đối chiếu số liệu định lượng để chọn mô hình trọng tâm cho đồ án.**

> **[BẤM CHUYỂN SANG SLIDE 14 – III. Đánh giá thực nghiệm và lựa chọn phương pháp]**

---

### SLIDE 14 – III. Đánh giá thực nghiệm và lựa chọn phương pháp *(12:50 – 13:00 | 10 giây)*

**Sau đây là phần ba: đối chiếu định lượng giữa các phương pháp và quyết định lựa chọn mô hình nghiên cứu, cài đặt.**

> **[BẤM CHUYỂN SANG SLIDE 15 – So sánh định lượng các phương pháp]**

---

### SLIDE 15 – So sánh định lượng các phương pháp *(13:00 – 14:10 | 1 phút 10 giây)*

Bảng trên slide trích kết quả so sánh định lượng trên bộ dữ liệu chuẩn NeRF-Synthetic gồm 8 cảnh Blender, lấy từ công trình gốc Instant-NGP năm 2022, chạy trên GPU RTX 3090 với thư viện `tiny-cuda-nn`.

Nhìn vào cột chất lượng PSNR trung bình và cột thời gian huấn luyện, chúng ta thấy một sự tương phản rất rõ ràng. Các phương pháp truyền thống như NeRF gốc đạt 31,005 dB, NSVF đạt 31,739 dB và Mip-NeRF đạt 33,090 dB, nhưng tất cả đều cần thời gian huấn luyện tính bằng nhiều giờ đồng hồ cho mỗi cảnh. Trong khi đó, Instant-NGP sử dụng Hash Encoding đạt PSNR cao nhất bảng là 33,176 dB mà chỉ mất đúng 5 phút huấn luyện.

Một điểm đối chứng rất đáng chú ý ở hai dòng cuối là giữa Instant-NGP dùng Frequency Encoding với Instant-NGP dùng Hash Encoding. Trong cùng điều kiện 5 phút huấn luyện, bản dùng Frequency chỉ đạt 30,056 dB, thấp hơn hơn 3 dB so với 33,176 dB của bản dùng Hash. Điều này chứng minh trực tiếp rằng cơ chế bảng băm đa độ phân giải đóng vai trò quyết định giúp mô hình hội tụ cực nhanh mà vẫn giữ độ sắc nét cao. **Từ kết quả đối chiếu này, nhóm đi đến lựa chọn mô hình cho phần tiếp theo của đồ án.**

> **[BẤM CHUYỂN SANG SLIDE 16 – Lựa chọn mô hình khảo sát]**

---

### SLIDE 16 – Lựa chọn mô hình khảo sát *(14:10 – 14:50 | 40 giây)*

Dựa trên khảo sát lý thuyết ở bốn công đoạn và kết quả thực nghiệm vừa trình bày, nhóm chọn **Instant-NGP** làm phương pháp trọng tâm để phân tích sâu và cài đặt thực nghiệm vì hai lý do chính.

Thứ nhất, Instant-NGP giải quyết trực tiếp bài toán hiệu năng vốn là rào cản lớn nhất của NeRF truyền thống, rút ngắn thời gian huấn luyện từ nhiều giờ xuống chỉ còn vài phút với chất lượng tái tạo cạnh tranh, rất phù hợp với điều kiện tài nguyên GPU hạn chế của đồ án. Thứ hai, ba kỹ thuật đặc trưng của Instant-NGP ánh xạ rất rõ ràng vào các công đoạn của quy trình: Multiresolution Hash Encoding tối ưu Công đoạn 2, Occupancy Grid giảm truy vấn vùng trống ở Công đoạn 3, và các kernel CUDA hợp nhất tăng tốc cả Công đoạn 3 lẫn Công đoạn 4. Tuy nhiên, nhóm cũng nhận thức rõ giới hạn của phương pháp: Instant-NGP tập trung tăng tốc biểu diễn và tính toán chứ không trực tiếp sửa sai số ước lượng tư thế camera tại Công đoạn 1. **Trên đây là toàn bộ nội dung phần trình bày Chương 1 và Chương 2 của nhóm.**

> **[BẤM CHUYỂN SANG SLIDE 17 – Cảm ơn]**

---

### SLIDE 17 – Cảm ơn *(14:50 – 15:00 | 10 giây)*

Em xin chân thành cảm ơn thầy và các bạn đã chú ý lắng nghe. Nhóm rất mong nhận được các câu hỏi và góp ý từ thầy và các bạn để hoàn thiện tốt hơn cho phần trình bày phương pháp và thực nghiệm tiếp theo ạ.

---

## Checklist sửa lỗi nhanh trên `07-Slide/slide.pptx` trước khi chiếu

- [ ] **Slide 4:** `độ sau` → `độ sâu`
- [ ] **Slide 5:** `tang cường ảo AR` → `tăng cường ảo AR`
- [ ] **Slide 7:** `Biển diễn cảnh 3D` → `Biểu diễn cảnh 3D`
- [ ] **Slide 10:** `Bộ nhớ tang theo .` → `Bộ nhớ tăng theo N³.` và xóa 1 bảng bị trùng lớp
- [ ] **Slide 11:** bổ sung ký hiệu $\sigma$ ở dòng `mật độ thể tích  và màu sắc c`
- [ ] **Slide 15:** `Thơi gian huấn luyện` → `Thời gian huấn luyện`
