# Quy định trình bày báo cáo

Rút từ hai tài liệu của Trường Đại học Khoa học Tự nhiên, Khoa Công nghệ Thông tin:

| Tài liệu | Vai trò |
|---|---|
| `CLC_Mau-quy-dinh-trinh-bay-KLTN.pdf` | Bản quy định chính thức của Khoa. Khi hai tài liệu chênh nhau thì theo bản này |
| `Thesis_Template.pdf` | Template LaTeX kèm hướng dẫn. Bổ sung chi tiết mà bản quy định không nói |

Đồ án này là đồ án môn học chứ không phải khóa luận tốt nghiệp, nên phần quy định
về nộp bài (hai cuốn bìa mềm, đĩa CD, bìa cứng in nhũ, chữ ký giảng viên phản biện)
không áp dụng. Phần hình thức trình bày thì áp dụng đầy đủ.

## 1. Định dạng trang

| Thông số | Quy định |
|---|---|
| Khổ giấy | A4, 210 mm x 297 mm |
| Lề trên | 3 cm |
| Lề dưới | 3,5 cm |
| Lề trái | 3,5 cm |
| Lề phải | 2 cm |
| Font chữ | Times New Roman, bảng mã Unicode |
| Cỡ chữ | 13 pt hoặc 14 pt |
| Giãn dòng | 1,5 lines |
| Số trang | Đặt ở giữa, phía dưới trang |

Lề trái rộng hơn lề phải vì mép trái bị đóng gáy che mất.

Hai tài liệu chênh nhau ở lề dưới và lề trái: bản quy định ghi 3,5 cm cho cả hai,
template ghi 2,5 cm và 3 cm. Bảng trên theo bản quy định. Nếu thầy yêu cầu khác
thì sửa lại trong `md2docx.js`, biến `margin` của mục `sections`.

## 2. Độ dài

Phần nội dung tối thiểu 50 trang A4, không nên vượt quá 100 trang. Con số này
không tính trang bìa, lời cảm ơn, mục lục và tài liệu tham khảo.

Phụ lục không được dày hơn phần chính của báo cáo.

## 3. Đánh số chương mục

Dùng hệ thống số Ả-rập, không dùng số La Mã. Mục và tiểu mục đánh số bằng nhóm
hai hoặc ba chữ số cách nhau một dấu chấm: số thứ nhất chỉ chương, số thứ hai chỉ
mục, số thứ ba chỉ tiểu mục.

```
Chương 3 ...
    3.1. ...
        3.1.1. ...
        3.1.2. ...
    3.2. ...
```

Phụ lục đánh theo chữ cái và gọi là chương: Chương A, Chương B.

## 4. Thứ tự các phần

### Phần đầu

| Thứ tự | Thành phần | Ghi chú |
|---|---|---|
| 1 | Bìa chính | Tên trường, khoa, tên sinh viên, tên đề tài, loại báo cáo, địa điểm và năm |
| 2 | Trang phụ bìa | Như bìa chính, bổ sung mã số sinh viên và tên giảng viên hướng dẫn |
| 3 | Lời cảm ơn | |
| 4 | Đề cương chi tiết | Phải có chữ ký của giảng viên hướng dẫn. Xem mẫu ở mục 9 |
| 5 | Mục lục | Hiển thị tới mục cấp ba |
| 6 | Bảng các hình vẽ, ký hiệu, chữ viết tắt | Xếp theo thứ tự bảng chữ cái |
| 7 | Tóm tắt | Nêu vấn đề nghiên cứu, các hướng tiếp cận, cách giải quyết và một số kết quả đạt được |
| 8 | Nội dung | |

Lưu ý thứ tự: tóm tắt đứng sau các bảng danh mục, không đứng trước.

### Phần nội dung

| Phần | Nội dung bắt buộc |
|---|---|
| Mở đầu | Lý do chọn đề tài, mục đích, đối tượng và phạm vi nghiên cứu |
| Tổng quan | Phân tích đánh giá các hướng nghiên cứu đã có của các tác giả trong và ngoài nước liên quan đến đề tài. Nêu những vấn đề còn tồn tại. Chỉ ra vấn đề mà đề tài cần tập trung giải quyết |
| Nghiên cứu thực nghiệm hoặc lý thuyết | Cơ sở lý thuyết, lý luận, giả thiết khoa học và phương pháp nghiên cứu đã sử dụng |
| Trình bày, đánh giá bàn luận về các kết quả | Mô tả ngắn gọn công việc nghiên cứu đã tiến hành, các kết quả nghiên cứu hoặc kết quả thực nghiệm. Với đề tài ứng dụng có kết quả là sản phẩm phần mềm, phải có hồ sơ thiết kế và cài đặt theo các mô hình đã học |
| Kết luận | Những kết quả đạt được, những đóng góp mới và những đề xuất mới. Viết ngắn gọn, không có lời bàn và bình luận thêm |
| Hướng phát triển | Kiến nghị về những hướng nghiên cứu tiếp theo |

Hướng dẫn riêng của giảng viên (`01-DeBai/huongdantrinhbay.rtf`) gộp kết luận và
hướng phát triển thành một chương. Theo hướng dẫn của giảng viên.

### Phần cuối

Danh mục tài liệu tham khảo, rồi phụ lục.

## 5. Bảng biểu và hình vẽ

**Vị trí đầu đề khác nhau giữa bảng và hình.** Đầu đề của bảng ghi phía trên bảng.
Đầu đề của hình ghi phía dưới hình.

**Đánh số gắn với chương.** Hình 3.4 là hình thứ tư trong Chương 3. Bảng 2.1 là
bảng thứ nhất trong Chương 2.

**Khi nhắc tới phải nêu rõ số hiệu.** Viết "được nêu trong Bảng 4.1" hoặc
"xem Hình 3.2". Không viết "được nêu trong bảng dưới đây".

**Vị trí đặt.** Bảng ngắn và đồ thị phải đi liền với phần nội dung nhắc tới chúng
lần đầu. Bảng dài có thể để trang riêng nhưng phải ngay sau phần nội dung nhắc tới
lần đầu. Bảng trình bày theo chiều ngang khổ giấy thì đầu bảng quay về lề trái của
trang.

**Trích dẫn nguồn.** Mọi đồ thị, bảng biểu, hình vẽ lấy từ nguồn khác phải trích
dẫn đầy đủ.

**Chất lượng hình.** Hình vẽ phải sạch sẽ, dùng mực đen để sao chụp lại được. Cỡ
chữ trong hình bằng cỡ chữ dùng trong báo cáo.

## 6. Phương trình toán học

**Mọi phương trình phải được đánh số.** Số để trong ngoặc đơn, đặt bên phía lề
phải, ví dụ (3.1). Nếu một nhóm phương trình mang cùng một số thì đánh (5.1.1),
(5.1.2), (5.1.3).

**Ký hiệu xuất hiện lần đầu phải giải thích ngay, kèm đơn vị tính.**

**Thống nhất cách trình bày trong toàn báo cáo.** Chọn trình bày phương trình trên
một dòng đơn hoặc dòng kép, rồi giữ nguyên lựa chọn đó.

## 7. Viết tắt

Cả hai tài liệu đều nhắc không được lạm dụng viết tắt, và template kết luận: nếu
có thể thì hạn chế hoàn toàn việc dùng viết tắt. Lý do là khi gặp từ viết tắt,
người đọc phải lật lại những phần đã đọc để tra nghĩa.

Bốn quy tắc cụ thể:

1. Chỉ viết tắt những từ, cụm từ hoặc thuật ngữ dùng nhiều lần trong báo cáo
2. Không viết tắt cụm từ dài, mệnh đề, hoặc cụm từ ít xuất hiện
3. Không viết tắt các từ tiếng Anh thông dụng
4. Viết tắt sau lần viết đầy đủ thứ nhất, kèm chữ viết tắt trong ngoặc đơn

Bảng danh mục chữ viết tắt xếp theo thứ tự bảng chữ cái, đặt ở phần đầu.

## 8. Trích dẫn tài liệu tham khảo

**Nguyên tắc viết câu có trích dẫn:** bỏ phần trong ngoặc vuông đi thì câu vẫn
phải đầy đủ ý nghĩa.

| Cách viết | Đánh giá |
|---|---|
| "Nghiên cứu [9] chỉ ra rằng ..." | Sai |
| "Nghiên cứu của Zhang [9] chỉ ra rằng ..." | Đúng |
| "... như trong công trình nghiên cứu [4]." | Sai |
| "... như trong công trình nghiên cứu của Cavnar và Trenkle [4]." | Đúng |

**Phạm vi trích dẫn.** Danh mục chỉ bao gồm những tài liệu được trích dẫn, sử dụng
hoặc đề cập tới để bàn luận trong báo cáo. Mọi ý kiến và khái niệm không phải của
riêng tác giả đều phải trích dẫn và chỉ rõ nguồn. Không trích dẫn những kiến thức
phổ biến mà mọi người đều biết.

**Trích dẫn gián tiếp.** Nếu không tiếp cận được tài liệu gốc mà phải trích dẫn
thông qua một tài liệu khác thì phải nêu rõ điều này, và tài liệu gốc đó không
được liệt kê trong danh mục tài liệu tham khảo.

**Quy ước ghi từng loại tài liệu:**

| Loại | Thứ tự các thành phần |
|---|---|
| Bài đăng tạp chí | Tên tác giả, tên bài báo, tên tạp chí, tập, số, năm, các trang |
| Bài báo cáo hội nghị | Tên tác giả, tên bài báo, tên hội nghị, tên tuyển tập các báo cáo, nơi và thời gian tổ chức |
| Sách | Tên tác giả, tên sách, lần xuất bản, nhà xuất bản, nơi xuất bản, năm xuất bản |

Ví dụ áp dụng cho tài liệu của đồ án này:

```
[1]  B. Mildenhall, P. P. Srinivasan, M. Tancik, J. T. Barron, R. Ramamoorthi,
     R. Ng, NeRF: Representing Scenes as Neural Radiance Fields for View
     Synthesis, Proceedings of the European Conference on Computer Vision
     (ECCV), Glasgow, UK, Aug. 23-28, 2020.

[2]  J. T. Barron, B. Mildenhall, D. Verbin, P. P. Srinivasan, P. Hedman,
     Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields, Proceedings
     of the IEEE/CVF Conference on Computer Vision and Pattern Recognition
     (CVPR), New Orleans, LA, USA, Jun. 18-24, 2022.

[3]  T. Muller, A. Evans, C. Schied, A. Keller, Instant Neural Graphics
     Primitives with a Multiresolution Hash Encoding, ACM Transactions on
     Graphics, 41 (4), 2022, pp. 1-15.
```

Template LaTeX chia danh mục thành hai nhóm Tiếng Việt và Tiếng Anh, nhóm tiếng
Việt đặt trước. Bản quy định không nói tới việc chia nhóm. Đồ án này gần như chỉ
trích dẫn tài liệu tiếng Anh nên không cần chia.

Khi làm bản LaTeX, dùng file BIB. LaTeX tự thêm vào danh mục những tài liệu được
`\cite`.

## 9. Mẫu đề cương chi tiết

Đề cương chi tiết phải có chữ ký của giảng viên hướng dẫn và của sinh viên thực
hiện. Các mục bắt buộc:

| Mục | Nội dung |
|---|---|
| Tên đề tài | Viết in hoa, đầy đủ |
| Họ tên và chức danh giảng viên hướng dẫn | |
| Sinh viên | Họ tên kèm mã số sinh viên của từng người |
| Thể loại | Nghiên cứu, hoặc công nghệ có hay không có ứng dụng demo |
| Thời gian thực hiện | Từ ngày tới ngày |
| Nội dung | Mô tả chi tiết những gì đang làm hoặc học được trong đề tài, phạm vi, mục tiêu, phương pháp hay cách tiếp cận, kết quả mong đợi |
| Các mốc thời gian nghiên cứu | Kế hoạch thực hiện và nhiệm vụ được giao cho từng sinh viên |

Mục cuối buộc phải phân công rõ việc của từng thành viên, nên viết trước khi bắt
tay vào các chương.

## 10. Yêu cầu chung

Báo cáo phải trình bày ngắn gọn, rõ ràng, mạch lạc, sạch sẽ, không tẩy xóa, có
đánh số trang, đánh số bảng biểu, hình vẽ và đồ thị.
