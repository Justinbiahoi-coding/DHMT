# Quy trình viết báo cáo

File này mô tả cách làm việc với báo cáo, áp dụng cho cả hai thành viên và cho mọi phiên làm việc với Claude Code.

## Nguyên tắc nền

File `bao-cao.md` là bản gốc duy nhất. File `bao-cao.docx` chỉ dùng để đọc, không sửa trực tiếp vào đó. Mọi thay đổi nội dung phải thực hiện trên `.md` rồi xuất lại `.docx`.

Lý do chọn markdown làm bản gốc thay vì viết thẳng vào Word: cuối kỳ cần chuyển báo cáo sang LaTeX. Đường `markdown sang LaTeX` giữ gần như trọn vẹn tiêu đề, bảng, công thức và trích dẫn, trong khi `docx sang LaTeX` thường ra mã rối và bảng vỡ. Ngoài ra git so sánh được hai phiên bản `.md` nên theo dõi được lịch sử sửa đổi, còn `.docx` thì không.

## Bốn bước bắt buộc

Mỗi lần viết hoặc sửa bất kỳ phần nào của báo cáo, chạy đủ bốn bước theo thứ tự.

### Bước 1. Soạn nội dung

Dùng skill `research-paper-writing-skill`. Skill này yêu cầu:

- Dựng dàn ý nhỏ từ ba tới bảy ý trước khi viết thành văn
- Mỗi mục con nêu rõ động cơ, thiết kế và ưu điểm kỹ thuật khi phù hợp
- Mỗi đoạn chỉ mang một thông điệp, nêu ngay ở câu đầu
- Giữ thuật ngữ nhất quán trong toàn báo cáo
- Mọi khẳng định phải có bằng chứng hỗ trợ. Nếu chưa có kết quả thì làm nhẹ hoặc bỏ khẳng định đó
- Sau khi viết xong mỗi mục, đọc ngược dàn ý: liệt kê câu chủ đề từng đoạn rồi kiểm tra chúng có ánh xạ đúng về luận điểm chính của mục không

### Bước 2. Rà văn phong

Dùng skill `humanizer`. Skill dò 26 mẫu đặc trưng của văn do máy sinh, lấy từ hướng dẫn "Signs of AI writing" của Wikipedia. Các mẫu hay gặp nhất trong báo cáo tiếng Việt:

| Mẫu | Ví dụ cần tránh | Cách sửa |
|---|---|---|
| Gạch ngang dài làm đầu nối vạn năng | "Kết quả tốt hơn, nhờ cơ chế mới" viết bằng dấu gạch ngang | Chọn dấu phẩy, hai chấm hoặc tách câu tùy quan hệ hai vế |
| Không X mà Y | "không chỉ nêu số lượng mà phải nêu thách thức" | Nêu thẳng: "ngoài số lượng, phải nêu thách thức" |
| Câu kết một dòng | Đoạn một câu lặp lại ý đoạn trước | Cắt bỏ, hoặc gộp vào đoạn trước nếu mang thông tin mới |
| Bộ ba gượng ép | Ba ví dụ song song khi chỉ cần một | Giữ ba mục khi cả ba thật sự khác nhau |
| Ngôn ngữ thổi phồng | cốt lõi, then chốt, quan trọng nhất, có giá trị cao | Nêu thẳng lý do thay vì báo hiệu tầm quan trọng |
| Nhãn in đậm trang trí | Mọi mục trong danh sách đều có nhãn in đậm kèm hai chấm | Chuyển thành văn xuôi khi nhãn không mang thông tin riêng |

### Bước 3. Xuất file Word

```bash
cd Doan/06-BaoCao
NODE_PATH=$(npm root -g) node md2docx.js bao-cao.md bao-cao.docx
```

Bộ chuyển đổi xử lý được: tiêu đề bốn cấp, bảng, danh sách lồng hai cấp, liên kết, ảnh nhúng, khối mã, khối trích dẫn, in đậm và in nghiêng lồng nhau. Nó cảnh báo khi gặp thẻ HTML chưa xử lý hoặc không tìm thấy file ảnh.

### Bước 4. Kiểm tra không mất nội dung

```bash
python3 kiem-tra-chuyen-doi.py bao-cao.md bao-cao.docx
```

Script đối chiếu từng dòng nội dung giữa hai file, đếm số bảng và số hình, dò thẻ HTML bị in thành chữ, và dò dấu hiệu văn AI còn sót. Phải ra dòng "Đạt. Không phát hiện mất mát nội dung." thì mới coi là xong bước xuất file.

## Ba quy tắc về định dạng

**Không dùng thẻ HTML trong file markdown**, kể cả `<br>`. Dùng dòng trống để ngắt đoạn. Thẻ HTML từng bị in thành chữ trong file Word, và cũng gây rối khi chuyển sang LaTeX.

**Không dùng gạch ngang dài** (`—` hoặc `–`). Đây vừa là quy tắc của bước rà văn phong, vừa tránh lỗi mã hóa khi chuyển định dạng.

**Đặt tên hình và bảng theo chương.** Hình 3.1, Bảng 2.1. Đánh số liên tục trong từng chương để lập danh mục ở phần mở đầu.

## Công cụ cần cài

| Công cụ | Dùng cho | Cài bằng |
|---|---|---|
| Node.js và gói `docx` | Xuất file Word | `npm install -g docx` |
| Python 3 | Script kiểm tra | Có sẵn trên macOS |
| `pandoc` | Chuyển sang LaTeX ở khâu cuối | `brew install pandoc`, chưa cần cài ngay |

## Tài liệu liên quan

| File | Nội dung |
|---|---|
| `dan-y-bao-cao.md` | Dàn ý chi tiết năm chương, kèm bảng kiểm đối chiếu tám lưu ý của giảng viên |
| `../01-DeBai/yeu-cau-cua-thay.md` | Toàn bộ yêu cầu của giảng viên, kèm bảng kiểm 13 mục trước khi nộp |
| `bao-cao.md` | Bản gốc của báo cáo |
| `md2docx.js` | Bộ chuyển đổi markdown sang Word |
| `kiem-tra-chuyen-doi.py` | Script kiểm tra không mất nội dung |
