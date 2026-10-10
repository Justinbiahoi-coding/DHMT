# Quy trình viết báo cáo

File này mô tả cách làm việc với báo cáo, áp dụng cho cả hai thành viên và cho mọi phiên làm việc với Claude Code.

## Nguyên tắc nền

File `bao-cao.md` là bản gốc duy nhất. File `bao-cao.docx` chỉ dùng để đọc, không sửa trực tiếp vào đó. Mọi thay đổi nội dung phải thực hiện trên `.md` rồi xuất lại `.docx`.

Lý do chọn markdown làm bản gốc thay vì viết thẳng vào Word: cuối kỳ cần chuyển báo cáo sang LaTeX. Đường `markdown sang LaTeX` giữ gần như trọn vẹn tiêu đề, bảng, công thức và trích dẫn, trong khi `docx sang LaTeX` thường ra mã rối và bảng vỡ. Ngoài ra git so sánh được hai phiên bản `.md` nên theo dõi được lịch sử sửa đổi, còn `.docx` thì không.

## Luật duyệt trước khi ghi

**Bắt buộc gọi công cụ Skill cho `research-paper-writing-skill` ở Bước 1 và cho
`humanizer` ở Bước 3, mỗi lần soạn nội dung mới.** Không được chỉ nhớ lại
nguyên tắc của hai skill này mà bỏ qua việc gọi thật. Từng có lần bỏ qua, chỉ
bị phát hiện khi người dùng hỏi lại, nên đây không phải gợi ý mà là điều kiện
bắt buộc trước khi ghi file.

Trước khi ghi bất kỳ đoạn nội dung mới nào vào `bao-cao.md`, phải in toàn bộ
đoạn đó ra ngay trong khung trả lời, dạng chữ đọc được bình thường, không giấu
trong lệnh Bash hay file tạm. Chỉ ghi vào `.md` sau khi người dùng xác nhận
duyệt. Nếu người dùng yêu cầu sửa thì sửa bản nháp và in lại, lặp lại tới khi
được duyệt rồi mới ghi.

Lý do: những lần trước, nội dung từng được ghi thẳng vào file qua lệnh Bash,
người dùng không có bản để đọc trước khi nó đã nằm trong báo cáo.

## Năm bước bắt buộc

Mỗi lần viết hoặc sửa bất kỳ phần nào của báo cáo, chạy đủ năm bước theo thứ tự.

### Bước 1. Soạn nội dung

Dùng skill `research-paper-writing-skill`. Skill này yêu cầu:

- Dựng dàn ý nhỏ từ ba tới bảy ý trước khi viết thành văn
- Mỗi mục con nêu rõ động cơ, thiết kế và ưu điểm kỹ thuật khi phù hợp
- Mỗi đoạn chỉ mang một thông điệp, nêu ngay ở câu đầu
- Giữ thuật ngữ nhất quán trong toàn báo cáo
- Mọi khẳng định phải có bằng chứng hỗ trợ. Nếu chưa có kết quả thì làm nhẹ hoặc bỏ khẳng định đó
- Sau khi viết xong mỗi mục, đọc ngược dàn ý: liệt kê câu chủ đề từng đoạn rồi kiểm tra chúng có ánh xạ đúng về luận điểm chính của mục không

### Bước 2. In bản nháp ra chat, chờ duyệt

Dán nguyên văn đoạn vừa soạn vào khung trả lời. Dừng lại chờ người dùng đọc và
xác nhận trước khi sang bước tiếp theo.

### Bước 3. Rà văn phong

Dùng skill `humanizer`. Skill dò 26 mẫu đặc trưng của văn do máy sinh, lấy từ hướng dẫn "Signs of AI writing" của Wikipedia. Các mẫu hay gặp nhất trong báo cáo tiếng Việt:

| Mẫu | Ví dụ cần tránh | Cách sửa |
|---|---|---|
| Gạch ngang dài làm đầu nối vạn năng | "Kết quả tốt hơn, nhờ cơ chế mới" viết bằng dấu gạch ngang | Chọn dấu phẩy, hai chấm hoặc tách câu tùy quan hệ hai vế |
| Không X mà Y | "không chỉ nêu số lượng mà phải nêu thách thức" | Nêu thẳng: "ngoài số lượng, phải nêu thách thức" |
| Câu kết một dòng | Đoạn một câu lặp lại ý đoạn trước | Cắt bỏ, hoặc gộp vào đoạn trước nếu mang thông tin mới |
| Bộ ba gượng ép | Ba ví dụ song song khi chỉ cần một | Giữ ba mục khi cả ba thật sự khác nhau |
| Ngôn ngữ thổi phồng | cốt lõi, then chốt, quan trọng nhất, có giá trị cao | Nêu thẳng lý do thay vì báo hiệu tầm quan trọng |
| Nhãn in đậm trang trí | Mọi mục trong danh sách đều có nhãn in đậm kèm hai chấm | Chuyển thành văn xuôi khi nhãn không mang thông tin riêng |

### Bước 4. Xuất file Word

```bash
cd Doan/06-BaoCao
NODE_PATH=$(npm root -g) node md2docx.js bao-cao.md bao-cao.docx
```

Bộ chuyển đổi xử lý được: tiêu đề bốn cấp, bảng, danh sách lồng hai cấp, liên kết, ảnh nhúng, khối mã, khối trích dẫn, in đậm và in nghiêng lồng nhau. Nó cảnh báo khi gặp thẻ HTML chưa xử lý hoặc không tìm thấy file ảnh.

### Bước 5. Kiểm tra không mất nội dung

```bash
python3 kiem-tra-chuyen-doi.py bao-cao.md bao-cao.docx
```

Script đối chiếu từng dòng nội dung giữa hai file, đếm số bảng và số hình, dò thẻ HTML bị in thành chữ, và dò dấu hiệu văn AI còn sót. Phải ra dòng "Đạt. Không phát hiện mất mát nội dung." thì mới coi là xong bước xuất file.

## Quy định trình bày của Khoa

Toàn bộ quy định rút từ `CLC_Mau-quy-dinh-trinh-bay-KLTN.pdf` (bản chính thức của
Khoa) và `Thesis_Template.pdf` nằm ở `quy-dinh-trinh-bay.md`. Đọc file đó trước
khi viết bất kỳ chương nào. Tám điều hay quên nhất:

| Điều | Nội dung |
|---|---|
| Độ dài | Phần nội dung tối thiểu 50 trang, không quá 100 trang |
| Đầu đề | Đầu đề bảng đặt phía trên bảng, đầu đề hình đặt phía dưới hình |
| Nhắc tới hình và bảng | Phải nêu số hiệu: "xem Hình 3.2". Không viết "hình dưới đây" |
| Phương trình | Mọi phương trình phải đánh số trong ngoặc đơn, đặt sát lề phải |
| Ký hiệu | Giải thích ngay lần xuất hiện đầu tiên, kèm đơn vị tính |
| Trích dẫn | Bỏ phần trong ngoặc vuông đi thì câu vẫn đủ nghĩa. Viết "Nghiên cứu của Barron và cộng sự [3] cho thấy", không viết "Nghiên cứu [3] cho thấy" |
| Viết tắt | Không lạm dụng. Chỉ giữ từ xuất hiện nhiều lần, viết đầy đủ ở lần đầu kèm chữ viết tắt trong ngoặc |
| Đề cương chi tiết | Bắt buộc có, đặt ngay sau lời cảm ơn, phải có chữ ký giảng viên hướng dẫn và bảng phân công từng thành viên |

Script `md2docx.js` đã cấu hình sẵn khổ A4, lề trên 3cm, lề dưới 3,5cm, lề trái
3,5cm, lề phải 2cm, Times New Roman 13pt, giãn dòng 1,5 và số trang đặt giữa phía
dưới. Không cần chỉnh tay trong Word.

Hai việc script chưa làm được, để lại cho khâu chuyển sang LaTeX:

1. Đánh số trang La Mã thường cho phần đầu rồi đổi sang số Ả-rập từ phần nội dung
2. Đánh số phương trình tự động ở lề phải

## Hai quy tắc về nguồn

**Không dùng thẻ HTML trong file markdown**, kể cả `<br>`. Dùng dòng trống để
ngắt đoạn. Thẻ HTML từng bị in thành chữ trong file Word, và cũng gây rối khi
chuyển sang LaTeX. Riêng chú thích `<!-- -->` thì được, vì bộ chuyển đổi bỏ hẳn
chúng trước khi xuất.

**Không dùng gạch ngang dài** (`—` hoặc `–`). Đây vừa là quy tắc của bước rà văn
phong, vừa tránh lỗi mã hóa khi chuyển định dạng.

## Công cụ cần cài

| Công cụ | Dùng cho | Cài bằng |
|---|---|---|
| Node.js và gói `docx` | Xuất file Word | `npm install -g docx` |
| Python 3 | Script kiểm tra | Có sẵn trên macOS |
| `pandoc` | Chuyển sang LaTeX ở khâu cuối | `brew install pandoc`, chưa cần cài ngay |

## Tài liệu liên quan

| File | Nội dung |
|---|---|
| `quy-dinh-trinh-bay.md` | Quy định trình bày đầy đủ, rút từ hai file PDF bên dưới |
| `CLC_Mau-quy-dinh-trinh-bay-KLTN.pdf` | Bản quy định chính thức của Khoa Công nghệ Thông tin |
| `Thesis_Template.pdf` | Template LaTeX kèm hướng dẫn, bổ sung chi tiết bản quy định không nói |
| `dan-y-bao-cao.md` | Dàn ý chi tiết năm chương, kèm bảng kiểm đối chiếu tám lưu ý của giảng viên |
| `../01-DeBai/yeu-cau-cua-thay.md` | Toàn bộ yêu cầu của giảng viên, kèm bảng kiểm 13 mục trước khi nộp |
| `bao-cao.md` | Bản gốc của báo cáo |
| `md2docx.js` | Bộ chuyển đổi markdown sang Word |
| `kiem-tra-chuyen-doi.py` | Script kiểm tra không mất nội dung |
