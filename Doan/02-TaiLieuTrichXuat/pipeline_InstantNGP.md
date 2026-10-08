# Quy trình Đầy đủ Instant-NGP: Từ Ảnh Input đến Ảnh Output

*Tài liệu hệ thống hóa toàn bộ các sự kiện xảy ra khi dùng **Instant-NGP** (Instant Neural Graphics Primitives with a Multiresolution Hash Encoding) để tạo ra 1 ảnh output ở góc nhìn mới — từ lúc chỉ có 1 thư mục ảnh thô cho tới khi render ra ảnh hoàn chỉnh. Tài liệu này là **bản song song** với `pipeline_NeRF.md`: cùng chia 5 giai đoạn, cùng quy ước chú thích ký hiệu, nhưng ở mỗi giai đoạn luôn nêu rõ **NeRF gốc làm gì — Instant-NGP đổi thành gì — vì sao đổi — hệ quả ra sao**.*

> **NGUỒN & MỨC ĐỘ TIN CẬY.** Toàn bộ nội dung kỹ thuật, công thức và siêu tham số trong tài liệu này đã được **đối chiếu trực tiếp với paper gốc**:
>
> Thomas Müller, Alex Evans, Christoph Schied, Alexander Keller (NVIDIA). *"Instant Neural Graphics Primitives with a Multiresolution Hash Encoding."* ACM Transactions on Graphics (SIGGRAPH) 41(4), Article 102, July 2022. arXiv:2201.05989v2. DOI: 10.1145/3528223.3530127.
>
> Mỗi mục đều ghi rõ **vị trí tương ứng trong paper** (Section 3, Section 4, Section 5.4, Table 1–3, Figure 2–12, Appendix A–E). Các con số thực nghiệm (PSNR, thời gian train, siêu tham số) được trích **nguyên vẹn dưới dạng dữ kiện khoa học**, có ghi nguồn mục/bảng. Phần diễn giải, ví dụ số minh họa, và cách tổ chức trình bày là **do tài liệu này tự dựng lại bằng lời riêng**, không dịch nguyên văn paper.
>
> Lưu ý quan trọng về phạm vi: paper gốc là 1 paper về **input encoding tổng quát**, áp dụng cho **4 bài toán** (gigapixel image, SDF, neural radiance caching, NeRF). Tài liệu này chỉ tập trung vào **nhánh NeRF** (Section 5.4 + Appendix D, E của paper) cùng với phần **hash encoding cốt lõi** (Section 3, 4) dùng chung cho mọi bài toán. Những chi tiết chỉ liên quan tới 3 bài toán kia (one-blob encoding, MAPE loss, octree của NGLOD, stab rays...) chỉ được nhắc khi cần so sánh.
>
> Những chỗ bản thân paper **không nói rõ** hoặc tài liệu này **không chắc chắn hiểu đúng** đều được đánh dấu bằng khối **⚠️ GHI CHÚ KHÔNG CHẮC CHẮN**.

## Mục lục

1. **[Giai đoạn 1](#giai-đoạn-1--chuẩn-bị-dữ-liệu--camera-pose-không-thay-đổi-so-với-nerf-gốc)** — Chuẩn bị dữ liệu & Camera Pose *(không thay đổi so với NeRF gốc — viết ngắn)*
2. **[Giai đoạn 2](#giai-đoạn-2--multiresolution-hash-encoding-trọng-tâm-của-toàn-bộ-paper)** — **Multiresolution Hash Encoding** *(TRỌNG TÂM)*
3. **[Giai đoạn 3](#giai-đoạn-3--hai-mlp-nhỏ--volume-rendering)** — Hai MLP nhỏ & Volume Rendering
4. **[Giai đoạn 4](#giai-đoạn-4--ray-marching-tăng-tốc-occupancy-grid-loss--vòng-lặp-training)** — Ray Marching tăng tốc, Occupancy Grid, Loss & Vòng lặp Training
5. **[Giai đoạn 5](#giai-đoạn-5--inference-sơ-đồ-tổng-thể--bảng-tra-cứu-paper)** — Inference, Sơ đồ tổng thể & Bảng tra cứu paper
6. **[BẢNG TỔNG HỢP: Thay đổi gì so với NeRF gốc](#bảng-tổng-hợp--instant-ngp-thay-đổi-những-gì-so-với-nerf-gốc)** ← *phần quan trọng nhất để đưa vào báo cáo*
7. **[Kết quả thực nghiệm & Hạn chế](#kết-quả-thực-nghiệm-trích-từ-paper)**

**Quy ước xuyên suốt tài liệu:**
- Mỗi công thức/ký hiệu lần đầu xuất hiện đều có bảng **"Chú thích ký hiệu"** đi kèm, viết như thể người đọc chưa biết gì; khi nhắc lại ở phần sau chỉ lướt nhẹ ý nghĩa.
- Mọi điểm khác biệt so với NeRF gốc được đóng khung trong khối **🔄 KHÁC VỚI NeRF GỐC** để dễ tra khi viết báo cáo.
- Ký hiệu toán trong tài liệu này **giữ đúng ký hiệu của paper Instant-NGP** (ví dụ dùng `L` cho *số mức độ phân giải*, không phải cho *số mức tần số* như trong NeRF gốc). Những chỗ ký hiệu trùng tên nhưng khác nghĩa giữa 2 paper đều được cảnh báo rõ.

---

## Giai đoạn 1 — Chuẩn bị dữ liệu & Camera Pose *(không thay đổi so với NeRF gốc)*

### 1.1. Instant-NGP không sửa gì ở giai đoạn này

Instant-NGP **không đề xuất bất kỳ thay đổi nào** ở khâu chuẩn bị dữ liệu và ước lượng camera pose. Paper gốc nói rõ (Section 5.4): mô hình được huấn luyện **theo đúng cách của Mildenhall et al. 2020** — tức là lan truyền ngược (backpropagate) qua 1 bộ ray marcher khả vi, với dữ liệu đầu vào là **ảnh RGB 2D kèm camera pose đã biết trước**.

Vì vậy, toàn bộ nội dung sau đây **giữ nguyên y nguyên từ NeRF gốc**, xem chi tiết đầy đủ tại **`pipeline_NeRF.md` Giai đoạn 1**:

| Nội dung | Trạng thái trong Instant-NGP | Tham chiếu chi tiết |
|---|---|---|
| Yêu cầu dữ liệu (20–100 ảnh, cảnh tĩnh, overlap đủ lớn) | **Giữ nguyên** | `pipeline_NeRF.md` mục 1.1 |
| Định nghĩa pose = bộ ba **(R, C, K)**: ma trận xoay 3×3, tâm camera 3×1, ma trận nội tại 3×3 | **Giữ nguyên** | `pipeline_NeRF.md` mục 1.2 |
| Lý do bắt buộc phải có (R,C,K) chính xác | **Giữ nguyên** | `pipeline_NeRF.md` mục 1.3 |
| Quy trình COLMAP/SfM 7 bước (SIFT → Matching → RANSAC/Essential Matrix → phân tích (R,t) → Triangulation/DLT → Incremental SfM/P3P → Bundle Adjustment/Levenberg-Marquardt) | **Giữ nguyên — KHÔNG lặp lại ở đây** | `pipeline_NeRF.md` mục 1.4, Bước 1–7 |
| Sản phẩm phụ: sparse point cloud dùng ước lượng biên cảnh | **Giữ nguyên** | `pipeline_NeRF.md` mục 1.5 |

### 1.2. Hai chi tiết nhỏ ở giai đoạn này mà Instant-NGP CÓ quy định thêm

Dù không đổi thuật toán, paper có 2 quy ước về **chuẩn hóa dữ liệu** cần nêu vì chúng ảnh hưởng trực tiếp tới Giai đoạn 2:

**(a) Ánh xạ cảnh vào khối đơn vị.** Paper (Appendix E.1 và E.1 *Related work*) nói rõ: với các scene NeRF tổng hợp (synthetic), cảnh được **giới hạn vào khối lập phương đơn vị `[0,1]³`**. Với scene thật lớn hơn, tọa độ đầu vào được **ánh xạ tuyến tính (linear map) vào khối đơn vị** trước khi đưa vào hash encoding. Đây là điều kiện tiên quyết để công thức tính độ phân giải từng mức (Giai đoạn 2) có ý nghĩa.

> **🔄 KHÁC VỚI NeRF GỐC.** NeRF gốc (và Mip-NeRF 360, NeRF++, DONeRF) dùng kỹ thuật **"warp" không gian** — bẻ cong hệ tọa độ, co không gian xa về gần gốc — để xử lý cảnh rộng, và việc warp này làm **tia bị uốn cong (rays curve)**. Paper Instant-NGP báo cáo (Appendix E.1) rằng trong cài đặt của họ, tia bị uốn cong **làm chất lượng tái tạo kém đi**, nên họ **cố tình không warp**: chỉ ánh xạ tuyến tính vào khối đơn vị, rồi dựa vào chính **tính tăng trưởng hình học theo lũy thừa (exponential multiresolution growth)** của hash encoding để đạt độ phân giải cực đại N_max tỉ lệ với kích thước cảnh, với số mức L không đổi (hoặc tăng theo hàm logarit).

**(b) Ưu tiên dữ liệu HDR.** Paper (Section 5.4, *Model Architecture*) nêu: khi dữ liệu train có **dải động thấp (low dynamic-range, sRGB)** thì dùng hàm kích hoạt **sigmoid** ở đầu ra màu; khi dữ liệu có **dải động cao (high dynamic range, linear HDR)** thì dùng hàm kích hoạt **exponential**. Nhóm tác giả **ưu tiên dữ liệu HDR** vì nó gần hơn với bản chất vật lý của quá trình truyền sáng. Chi tiết xem Giai đoạn 3 mục 3.4.

### 1.3. Kết quả của Giai đoạn 1

Giống hệt NeRF gốc: với **mỗi ảnh** trong dataset, ta có bộ ba **(R, C, K)** trên 1 hệ tọa độ world duy nhất; thêm vào đó, toàn bộ cảnh đã được **ánh xạ tuyến tính vào khối đơn vị `[0,1]³`** (hoặc 1 bounding box đã biết kích thước), sẵn sàng cho Giai đoạn 2.

Điểm then chốt cần nhớ: **100% khác biệt giữa NeRF gốc và Instant-NGP nằm ở Giai đoạn 2, 3, 4 — không nằm ở Giai đoạn 1.** Nếu báo cáo đồ án đã trình bày COLMAP/SfM ở chương về NeRF gốc thì **không cần trình bày lại** ở chương Instant-NGP.

---

## Giai đoạn 2 — Multiresolution Hash Encoding *(TRỌNG TÂM của toàn bộ paper)*

Đây là **đóng góp khoa học chính** của paper, và cũng là chỗ Instant-NGP khác NeRF gốc một cách triệt để nhất. Tương ứng **Section 3 (Multiresolution Hash Encoding)** và **Section 4 (Implementation)** của paper gốc, cùng **Figure 3** (sơ đồ 5 bước) và **Table 1** (bảng siêu tham số).

### 2.0. Nhắc lại: NeRF gốc làm gì ở chỗ này, và 3 nhược điểm

Trong NeRF gốc (`pipeline_NeRF.md` Giai đoạn 2 mục 5), mỗi tọa độ vô hướng `p` được biến đổi bằng hàm **positional encoding** cố định:

```
γ(p) = ( sin(2⁰πp), cos(2⁰πp), sin(2¹πp), cos(2¹πp), ..., sin(2^(L_f−1)πp), cos(2^(L_f−1)πp) )
```

(Ở đây ký hiệu `L_f` thay cho `L` của NeRF gốc, để **tránh nhầm** với `L` = số mức độ phân giải của Instant-NGP sẽ dùng ngay bên dưới. NeRF gốc dùng `L_f = 10` cho vị trí → γ(x) có 60 chiều; `L_f = 4` cho hướng → γ(d) có 24 chiều.)

Paper Instant-NGP gọi họ các encoding kiểu này là **frequency encoding** (Section 2) và chỉ ra 3 nhược điểm:

| # | Nhược điểm của frequency encoding | Vì sao đó là vấn đề |
|---|---|---|
| **1** | **Hoàn toàn cố định, không có tham số học được.** γ(·) chỉ là 1 công thức sin/cos viết sẵn — không có 1 con số nào trong nó được cập nhật qua train. | Toàn bộ "gánh nặng học" (learning task) bị đẩy hết vào MLP. Muốn biểu diễn cảnh chi tiết thì buộc phải cho MLP to ra. |
| **2** | **Mọi điểm trong không gian dùng chung đúng 1 bộ tham số** (chính là toàn bộ trọng số MLP). | Mỗi bước cập nhật gradient phải **sửa toàn bộ** trọng số MLP, dù mẫu train đó chỉ liên quan tới 1 vùng nhỏ xíu của cảnh. Rất tốn tính toán. |
| **3** | **Không thích nghi (non-adaptive)** với mức độ chi tiết của từng vùng cảnh. | Vùng trống không khí và vùng bề mặt chi tiết đều được "đối xử" như nhau, không có cơ chế dồn tài nguyên vào chỗ cần. |

> **🔄 Ý TƯỞNG ĐẢO CHIỀU CỦA INSTANT-NGP.** Thay vì giữ encoding cố định + MLP lớn (NeRF gốc), Instant-NGP dùng **encoding có tham số học được (parametric / trainable encoding) + MLP cực nhỏ**. "Trí nhớ về cảnh" được chuyển phần lớn ra khỏi MLP, vào 1 cấu trúc dữ liệu tra cứu được. Hệ quả kép: (a) mỗi mẫu train chỉ cần sửa **một số rất ít** tham số (ở 3D: đúng 8 đỉnh lưới mỗi mức), thay vì sửa toàn bộ mạng; (b) MLP nhỏ đi hàng chục lần nên mỗi lần forward/backward rẻ hơn hẳn.

### 2.1. Vì sao không dùng lưới đặc (dense grid) — phổ các lựa chọn, theo Figure 2 của paper

Paper dựng 1 thí nghiệm rất rõ ràng (**Figure 2**): train cùng 1 scene NeRF trong **11 000 bước**, chỉ đổi kiểu encoding + kích thước MLP, giữ nguyên mọi thứ khác. Kết quả (trích đúng số liệu Figure 2):

| Phương án encoding | Tham số (MLP + encoding) | Thời gian train | PSNR |
|---|---|---|---|
| (a) Không encoding gì cả | 411 k + 0 | 11:28 | 18.56 dB |
| (b) **Frequency encoding** (= NeRF gốc), MLP 8 lớp × 256 kênh | 438 k + 0 | 12:45 | 22.90 dB |
| (c) Dense grid 1 độ phân giải (128³, feature 16 chiều) | 10 k + 33.6 M | 1:09 | 22.35 dB |
| (d) Dense grid **đa độ phân giải** (8 lưới, từ 16³ đến 173³, feature 2 chiều, nối lại thành 16 chiều) | 10 k + 16.3 M | 1:26 | 23.62 dB |
| (e) **Hash table (Instant-NGP)**, T = 2¹⁴ | 10 k + 494 k | 1:48 | 22.61 dB |
| (f) **Hash table (Instant-NGP)**, T = 2¹⁹ | 10 k + 12.6 M | 1:47 | 24.58 dB |

**Cách đọc bảng này (3 kết luận):**

1. **So (b) với (e):** cùng mức tổng tham số học được (438 k so với 504 k), nhưng (e) train **nhanh hơn hơn 8 lần** (1:48 so với 12:45) mà PSNR gần như không kém. Paper nêu đúng 2 nguyên nhân: **tính thưa thớt của việc cập nhật tham số (sparsity of updates)** và **MLP nhỏ hơn**.
2. **So (c) với (d):** cùng cho MLP 10 k, nhưng (d) dùng **ít hơn một nửa** số tham số encoding (16.3 M so với 33.6 M) mà chất lượng tương đương/nhỉnh hơn. → **đa độ phân giải (multiresolution) là 1 ý tưởng tốt độc lập**, vì cảnh tự nhiên có tính trơn (smoothness) nên phân tách theo nhiều tỉ lệ là hợp lý.
3. **So (d) với (f):** hash table đạt chất lượng ngang/hơn dense grid với **ít hơn khoảng 20 lần** số tham số (paper viết rõ: *"comparable to the dense grid encoding, despite having 20× fewer parameters"*). → **bảng hash là ý tưởng tốt thứ hai, độc lập với ý tưởng thứ nhất**.

**Vì sao dense grid lãng phí — paper nêu 2 lý do rất cụ thể (Section 2, *Sparse parametric encodings*):**

- **Lý do 1 — lãng phí theo bậc tăng trưởng.** Số tham số của 1 lưới đặc tăng theo **O(N³)** (N = độ phân giải mỗi chiều), trong khi **bề mặt** thật sự cần biểu diễn chỉ tăng theo **O(N²)**. Paper đưa 1 con số thực: với lưới 128³, **chỉ 53 807 ô (2.57%)** là có chạm vào bề mặt nhìn thấy được; **97.43% ô còn lại là không khí** nhưng vẫn chiếm bộ nhớ như nhau.
- **Lý do 2 — không thể "tỉa" trước** trong bối cảnh NeRF. Nếu đã biết trước bề mặt nằm ở đâu, có thể dùng octree hoặc sparse grid để cắt bỏ phần trống. **Nhưng trong NeRF, bề mặt chỉ "hiện ra" dần trong lúc train** — chưa biết trước. Các phương pháp như NSVF, DVGO, Plenoxels xử lý bằng chiến lược **nhiều pha, thô-đến-mịn (coarse-to-fine)**: định kỳ dừng lại, tinh chỉnh và tỉa bớt cấu trúc dữ liệu. Paper phê bình cách này là **làm quy trình train phức tạp lên**, và trên GPU thì việc đi theo con trỏ trong cây (pointer chasing) + rẽ nhánh điều khiển (control flow divergence) rất đắt.

> **🔄 ĐIỂM BÁN HÀNG CỐT LÕI.** Paper nhấn mạnh (Section 1, gạch đầu dòng *Adaptivity*): *"Unlike prior work, **no structural updates to the data structure are needed at any point during training**"* — không hề có bước tỉa/chia/gộp cấu trúc dữ liệu nào trong suốt quá trình train. Bảng hash có **kích thước cố định T từ đầu đến cuối**, layout bộ nhớ **biết trước và không phụ thuộc dữ liệu** (predictable memory layout) nên có thể tinh chỉnh cho vừa kích thước cache của GPU. Tra cứu là **O(1), không rẽ nhánh**, và **L mức có thể tra song song hoàn toàn**.
>
> Và điểm quan trọng về mặt sử dụng: paper tuyên bố encoding này **chỉ cần tinh chỉnh đúng 2 con số** — kích thước bảng hash **T** và độ phân giải mịn nhất **N_max** (Section 1 và chú thích Table 1). Mọi siêu tham số còn lại dùng chung cho cả 4 bài toán khác nhau.

### 2.2. Bảng siêu tham số chính thức (trích nguyên Table 1 của paper)

| Tham số | Ký hiệu | Giá trị trong paper |
|---|---|---|
| Số mức độ phân giải (number of levels) | **L** | **16** |
| Số entry tối đa mỗi mức = kích thước bảng hash | **T** | **2¹⁴ đến 2²⁴** |
| Số chiều feature vector mỗi entry | **F** | **2** |
| Độ phân giải thô nhất (coarsest resolution) | **N_min** | **16** |
| Độ phân giải mịn nhất (finest resolution) | **N_max** | **512 đến 524 288** |

Thêm 2 thông tin quan trọng không nằm trong Table 1 mà nằm ở Section 4 (*Architecture*) và Section 3:

- **Với NeRF (và SDF), `N_max` được đặt bằng `2048 × kích thước cảnh (scene size)`.** Tức với scene tổng hợp chuẩn hóa về khối đơn vị, N_max = 2048. (Với gigapixel image: N_max = một nửa chiều rộng ảnh; với radiance caching: N_max = 2¹⁹.)
- **Hệ số tăng trưởng `b` nằm trong khoảng `[1.26, 2]`** đối với các trường hợp sử dụng trong paper.
- Paper tuyên bố rõ (Section 3, *Performance vs. quality*, dựa trên **Figure 5**): cặp **(F = 2, L = 16)** là 1 **điểm tối ưu Pareto** cho **cả 4 bài toán**, nên được dùng làm giá trị mặc định khuyến nghị.

**Vì sao F = 2 chứ không phải 1 hay 4?** Paper giải thích ở 2 chỗ:
- Về chất lượng (Section 3, Figure 5): F=2, L=16 cho sự cân bằng tốt nhất giữa chất lượng và tốc độ.
- Về phần cứng (Section 4, *Performance considerations*): **F nhỏ** thì có lợi cho **tính cục bộ của cache (cache locality)** khi tra bảng theo kiểu streaming; **F lớn** thì có lợi cho **tính liên tục bộ nhớ (memory coherence)** vì cho phép dùng lệnh nạp vector rộng F phần tử. F=2 là điểm dung hòa. Paper còn nêu 1 chi tiết rất "phần cứng": **F = 1 lại chạy chậm** trên GPU RTX 3090 của họ, vì phép **cộng dồn nguyên tử ở độ chính xác nửa (atomic half-precision accumulation)** chỉ hiệu quả với vector 2 chiều, chứ không hiệu quả với số vô hướng.

### 2.3. Tổng quan 5 bước của hash encoding (theo Figure 3 của paper)

Trước khi đi vào chi tiết, đây là bức tranh toàn cảnh. Hàm encoding được ký hiệu `enc(x; θ)`.

#### Chú thích ký hiệu toàn cục của Giai đoạn 2

| Ký hiệu | Ý nghĩa |
|---|---|
| **x** | tọa độ điểm 3D cần mã hóa, `x ∈ ℝ^d`. Với NeRF thì `d = 3`. Đã được ánh xạ vào khối đơn vị ở Giai đoạn 1. |
| **d** | **số chiều không gian** của bài toán (d=2 cho ảnh, d=3 cho NeRF/SDF). ⚠️ Chú ý: ký hiệu `d` này **KHÁC** với `d` = vector hướng tia trong `pipeline_NeRF.md`. Trong tài liệu này, hướng tia sẽ luôn được viết là **`d_view`** để tránh nhầm. |
| **L** | số mức độ phân giải (số "tầng" lưới chồng lên nhau). L = 16. |
| **l** | chỉ số mức, `l = 0, 1, ..., L−1`. |
| **N_l** | độ phân giải (số ô theo mỗi chiều) của lưới ở mức `l`. |
| **T** | kích thước bảng hash của mỗi mức (số entry tối đa). Mọi mức dùng chung 1 giá trị T. |
| **F** | số chiều của mỗi feature vector lưu trong bảng. F = 2. |
| **θ** | **toàn bộ tham số học được của encoding** — tức tập hợp mọi feature vector trong mọi bảng hash. Đây là tham số **được train bằng gradient descent**, giống như trọng số mạng. |
| **θ_l** | bảng hash của riêng mức `l` (1 mảng gồm tối đa T phần tử, mỗi phần tử là 1 vector F chiều). |
| **Φ** | tập trọng số (weights) của mạng MLP — tách biệt hoàn toàn với θ. |
| **m(y; Φ)** | mạng MLP, nhận vector đã mã hóa `y` và dùng trọng số `Φ`. |
| **y** | vector kết quả của encoding, chính là input của MLP: `y = enc(x; θ)`. |
| **ξ** | các chiều input **phụ, không mang tính không gian** (auxiliary / non-spatial), `ξ ∈ ℝ^E`. Với NeRF, đây là **hướng nhìn đã mã hóa**. |
| **E** | số chiều của ξ. |
| **⌊·⌋, ⌈·⌉** | phép làm tròn xuống (floor) và làm tròn lên (ceiling). |
| **⊕** | phép **XOR theo bit (bit-wise exclusive OR)**. |
| **mod** | phép lấy phần dư của phép chia nguyên. |

#### Năm bước (Figure 3 của paper)

```
   x (1 điểm 3D)
    │
    ├──► [Bước 1] Với MỖI mức l = 0..L-1: xác định ô lưới (voxel) chứa x
    │              ở độ phân giải N_l, lấy ra 2^d = 8 đỉnh của ô đó
    │              (tọa độ nguyên trong ℤ³)
    │
    ├──► [Bước 2] HASH: biến tọa độ nguyên của mỗi đỉnh thành 1 chỉ số
    │              trong [0, T), rồi TRA CỨU (lookup) feature vector
    │              F chiều tương ứng trong bảng θ_l
    │
    ├──► [Bước 3] NỘI SUY: pha trộn 8 feature vector của 8 đỉnh thành
    │              1 feature vector F chiều duy nhất, theo vị trí tương
    │              đối của x trong ô lưới (d-linear interpolation)
    │
    ├──► [Bước 4] NỐI (concatenate): ghép L vector (mỗi mức 1 vector
    │              F chiều) + ξ ∈ ℝ^E  ──►  y ∈ ℝ^(L·F + E)
    │
    └──► [Bước 5] MLP m(y; Φ) ──► output (density, màu)

   Gradient của loss đi NGƯỢC lại: qua MLP (5) → qua phép nối (4)
   → qua phép nội suy (3) → CỘNG DỒN vào chính các feature vector
   đã tra cứu ở (2).  ← đây là cơ chế làm θ học được.
```

**Điểm then chốt cần hiểu ngay:** gradient không dừng ở MLP. Nó chảy ngược qua phép nội suy tuyến tính và **cộng dồn trực tiếp vào các entry của bảng hash**. Vì phép nội suy ở Bước 3 chỉ dùng đúng **8 entry mỗi mức** (tổng cộng 8×16 = 128 entry cho cả 16 mức), nên **một mẫu train chỉ "chạm" vào đúng 128 feature vector trong hàng triệu feature vector của θ** — đây chính là "tính thưa thớt của việc cập nhật" (sparsity of updates) mà paper nhắc nhiều lần, và là nguồn gốc của tốc độ.

> **🔄 KHÁC VỚI NeRF GỐC — ĐỊNH LƯỢNG.** Với NeRF gốc, mỗi mẫu train (mỗi điểm mẫu trên tia) khi backprop phải cập nhật **toàn bộ ~438 000 – 600 000 trọng số** của MLP. Với Instant-NGP, mỗi mẫu train cập nhật **~10 000 trọng số MLP** (nhỏ hơn ~44 lần) **cộng với đúng 128 feature vector** (256 số thực) trong bảng hash. Tổng số tham số của Instant-NGP **nhiều hơn** NeRF gốc rất nhiều (có thể tới hàng chục triệu), nhưng **số tham số thực sự phải sửa cho mỗi mẫu lại nhỏ hơn hẳn** — đây là nghịch lý cốt lõi giải thích vì sao nó nhanh. Paper nói đúng ý này ở Section 2 (*Parametric encodings*): *"although the total number of parameters is much higher for a parametric encoding than a fixed input encoding, the number of FLOPs and memory accesses required for the update during training is not increased significantly."*

### 2.4. Công thức độ phân giải của từng mức (Eq. 2 và Eq. 3 của paper)

Độ phân giải của L mức được chọn theo 1 **cấp số nhân (geometric progression)** giữa N_min và N_max:

```
N_l := ⌊ N_min · b^l ⌋                                   (Eq. 2)

b  := exp( (ln N_max − ln N_min) / (L − 1) )              (Eq. 3)
```

#### Chú thích ký hiệu

| Ký hiệu | Ý nghĩa |
|---|---|
| **N_l** | độ phân giải của lưới ở mức `l` — nghĩa là lưới đó chia mỗi chiều của khối đơn vị thành `N_l` ô bằng nhau (nên có `N_l + 1` đỉnh theo mỗi chiều) |
| **l** | chỉ số mức, chạy từ 0 (thô nhất) tới L−1 (mịn nhất) |
| **N_min** | độ phân giải mức thô nhất = 16 |
| **N_max** | độ phân giải mức mịn nhất (với NeRF: 2048 × kích thước cảnh) |
| **b** | **hệ số tăng trưởng (growth factor)** — tỉ số độ phân giải giữa 2 mức liền kề |
| **⌊·⌋** | làm tròn xuống về số nguyên (vì độ phân giải phải là số nguyên) |
| **ln** | logarit tự nhiên (cơ số e); **exp** = hàm e mũ |
| **L − 1** | ở mẫu số, không phải L — vì có L mức thì chỉ có **L−1 "bước nhảy"** giữa chúng |

#### Vì sao công thức Eq. 3 có dạng như vậy — dẫn từ đầu

Ta muốn: mức 0 có độ phân giải N_min, mức L−1 có độ phân giải N_max, và tỉ số giữa 2 mức liền kề luôn bằng nhau (= b). Viết điều kiện ở mức cuối:

```
N_min · b^(L−1) = N_max
```

Chia 2 vế cho N_min rồi lấy logarit tự nhiên:

```
(L−1) · ln b = ln N_max − ln N_min
⟹  ln b = (ln N_max − ln N_min) / (L−1)
⟹  b    = exp( (ln N_max − ln N_min) / (L−1) )     ✓ đúng Eq. 3
```

Vậy Eq. 3 **không phải công thức đặt tùy ý** — nó là nghiệm duy nhất của bài toán "chia khoảng [N_min, N_max] thành L mức theo cấp số nhân".

#### Vì sao chọn cấp số nhân (hình học) chứ không phải cấp số cộng

Paper nêu lý do ở Section 3 (*Implicit hash collision resolution*): tăng trưởng hình học cho phép **phủ toàn bộ dải tỉ lệ từ N_min tới N_max với chỉ `O(log(N_max/N_min))` mức**. Nhờ đó có thể chọn N_max **lớn một cách thoải mái/an toàn (conservatively large)** mà không làm số mức phình lên. Nếu dùng cấp số cộng (mỗi mức tăng thêm 1 lượng cố định), số mức cần thiết sẽ tăng **tuyến tính** theo N_max — không khả thi.

#### Kiểm chứng bằng số — bảng độ phân giải thực tế cho cấu hình NeRF của paper

Với **N_min = 16, N_max = 2048, L = 16** (đúng cấu hình NeRF của paper trên scene khối đơn vị):

```
b = exp( (ln 2048 − ln 16) / 15 ) = exp( (7.6246 − 2.7726) / 15 ) = exp(0.32347) ≈ 1.3819
```

| Mức `l` | `b^l` | `N_l = ⌊16·b^l⌋` | Số đỉnh lý thuyết `(N_l+1)³` | Kích thước 1 ô (so với khối đơn vị) |
|---:|---:|---:|---:|---:|
| 0 | 1.000 | **16** | 4 913 | 1/16 ≈ 0.0625 |
| 1 | 1.382 | 22 | 12 167 | ≈ 0.0455 |
| 2 | 1.910 | 30 | 29 791 | ≈ 0.0333 |
| 3 | 2.639 | 42 | 79 507 | ≈ 0.0238 |
| 4 | 3.647 | 58 | 205 379 | ≈ 0.0172 |
| 5 | 5.040 | 80 | 531 441 | ≈ 0.0125 |
| 6 | 6.965 | 111 | 1 404 928 | ≈ 0.0090 |
| 7 | 9.623 | 153 | 3 652 264 | ≈ 0.0065 |
| 8 | 13.298 | 212 | 9 663 597 | ≈ 0.0047 |
| 9 | 18.378 | 294 | 25 672 375 | ≈ 0.0034 |
| 10 | 25.399 | 406 | 67 419 143 | ≈ 0.0025 |
| 11 | 35.098 | 561 | 177 504 328 | ≈ 0.0018 |
| 12 | 48.502 | 776 | 469 097 433 | ≈ 0.0013 |
| 13 | 67.022 | 1 072 | 1 235 376 017 | ≈ 0.00093 |
| 14 | 92.622 | 1 482 | 3 261 545 587 | ≈ 0.00067 |
| 15 | 128.000 | **2 048** | 8 602 523 649 | ≈ 0.00049 |

**Hai quan sát quan trọng từ bảng này:**

1. **Mức mịn nhất là bất khả thi nếu lưu đặc.** Lưới 2048³ có **hơn 8,6 tỉ đỉnh (chính xác: 2 049³ = 8 602 523 649)**. Nếu mỗi đỉnh lưu 1 feature 2 chiều ở độ chính xác nửa (2 byte/số) thì cần **~34 GB chỉ cho 1 mức** — hoàn toàn không khả thi. Đây chính là động lực bắt buộc phải dùng bảng hash.
2. **Kiểm chứng với dải b của paper.** Paper nói `b ∈ [1.26, 2]`. Thử 2 đầu dải `N_max` trong Table 1: với N_max = 512 → `b = exp((ln512−ln16)/15) = 1.2599`; với N_max = 524 288 → `b = exp((ln524288−ln16)/15) = 2.0000`. **Khớp chính xác** 2 đầu khoảng [1.26, 2] mà paper công bố → xác nhận cách hiểu công thức là đúng.

### 2.5. Bước 1 — Xác định ô lưới và 2^d đỉnh của nó

Xét **riêng 1 mức `l`**. Tọa độ điểm `x` được **nhân với độ phân giải của mức đó**, rồi làm tròn xuống và làm tròn lên:

```
⌊x_l⌋ := ⌊ x · N_l ⌋          (làm tròn xuống từng thành phần)
⌈x_l⌉ := ⌈ x · N_l ⌉          (làm tròn lên từng thành phần)
```

| Ký hiệu | Ý nghĩa |
|---|---|
| **x_l** | viết tắt của `x · N_l` — tọa độ của x **đo theo đơn vị ô lưới của mức l** (thay vì theo đơn vị khối đơn vị) |
| **⌊x_l⌋** | vector tọa độ **nguyên** của đỉnh "góc dưới" của ô lưới chứa x |
| **⌈x_l⌉** | vector tọa độ **nguyên** của đỉnh "góc trên" của ô lưới chứa x |

Hai vector `⌊x_l⌋` và `⌈x_l⌉` **căng ra (span)** 1 ô lưới có **`2^d` đỉnh nguyên** trong `ℤ^d`. Với NeRF (d = 3): **2³ = 8 đỉnh** — đúng 8 góc của 1 hình lập phương.

**Ví dụ số cụ thể.** Lấy mức `l` có `N_l = 16`, điểm `x = (0.30, 0.60, 0.45)`:

```
x · N_l = (0.30·16, 0.60·16, 0.45·16) = (4.8, 9.6, 7.2)

⌊x_l⌋ = (4, 9, 7)        ⌈x_l⌉ = (5, 10, 8)
```

8 đỉnh của ô lưới là mọi tổ hợp lấy từng chiều một trong hai giá trị trên:

```
(4, 9, 7)   (5, 9, 7)   (4,10, 7)   (5,10, 7)
(4, 9, 8)   (5, 9, 8)   (4,10, 8)   (5,10, 8)
```

Quá trình này **chạy độc lập cho cả L = 16 mức** — ở mỗi mức, x nằm trong 1 ô lưới có kích thước khác nhau, nên 8 đỉnh thu được cũng khác nhau hoàn toàn.

> **🔄 KHÁC VỚI NeRF GỐC.** Ở NeRF gốc, tọa độ x được đưa qua công thức sin/cos và **không có khái niệm "ô lưới", "đỉnh", hay "tra cứu"** nào cả — chỉ là tính hàm số. Ở Instant-NGP, tọa độ x được dùng làm **địa chỉ (address)** để truy xuất dữ liệu đã học sẵn. Đây là chuyển đổi về bản chất: từ **"tính toán hàm"** sang **"tra cứu bảng + nội suy"** — và vì tra cứu bảng rẻ hơn tính hàm qua 8 lớp mạng rất nhiều, đây là nguồn tốc độ thứ hai.

### 2.6. Bước 2a — Ánh xạ đỉnh → entry: HAI chế độ khác nhau

Đây là chi tiết mà **rất nhiều tài liệu phổ thông trình bày sai hoặc thiếu**, nên cần nói thật rõ. Instant-NGP **không phải lúc nào cũng hash**. Paper (Section 3) quy định:

```
Nếu  (N_l + 1)^d  ≤  T    →  ánh xạ 1:1 (one-to-one), KHÔNG hash, KHÔNG có collision
Nếu  (N_l + 1)^d  >  T    →  dùng hàm hash h : ℤ^d → ℤ_T, coi mảng như 1 hash table
```

| Ký hiệu | Ý nghĩa |
|---|---|
| **(N_l + 1)^d** | **số đỉnh thật sự có** của lưới đặc ở mức `l` (vì N_l ô theo mỗi chiều thì có N_l+1 đỉnh theo mỗi chiều) |
| **T** | số entry của bảng mức đó |
| **ánh xạ 1:1** | mỗi đỉnh lưới có **đúng 1 entry riêng** của nó, không chia sẻ với đỉnh nào khác |
| **ℤ_T** | tập các số nguyên `{0, 1, ..., T−1}` — tức tập chỉ số hợp lệ của bảng |

Nói cách khác: **các mức thô hoạt động như lưới đặc (dense grid) thông thường; chỉ các mức mịn mới thực sự là hash table.**

#### Kiểm chứng bằng số — mức nào hash, mức nào không

Dùng chính bảng `N_l` ở mục 2.4:

| T | Các mức ánh xạ **1:1** (không collision) | Các mức dùng **hash** (có collision) | Tổng số entry | Số tham số θ (×F=2) |
|---|---|---|---|---|
| **2¹⁴** = 16 384 | l = 0, 1 | l = 2 … 15 (14 mức) | 246 456 | **492 912 ≈ 0.49 M** |
| **2¹⁹** = 524 288 | l = 0 … 4 | l = 5 … 15 (11 mức) | 6 098 925 | **12 197 850 ≈ 12.2 M** |
| **2²⁴** = 16 777 216 | l = 0 … 8 | l = 9 … 15 (7 mức) | 133 024 499 | **266 048 998 ≈ 266 M** |

> **✅ XÁC NHẬN CHÉO VỚI PAPER.** Figure 2(e) của paper ghi cấu hình `T = 2¹⁴` có **"10 k + 494 k"** tham số. Tính lại từ công thức trên: phần encoding = **492 912 ≈ 494 k** — **khớp**. Phần MLP = 10 k cũng khớp (xem Giai đoạn 3 mục 3.3 để thấy phép đếm 9 619 ≈ 10 k). Việc 2 con số độc lập đều khớp là bằng chứng mạnh cho thấy cách hiểu công thức Eq. 2/Eq. 3 và điều kiện `(N_l+1)^d ≤ T` trong tài liệu này là **đúng**.
>
> ⚠️ **GHI CHÚ KHÔNG CHẮC CHẮN:** với `T = 2¹⁹`, phép tính trên cho **12.20 M** còn Figure 2(f) của paper ghi **12.6 M**. Chênh ~3%. Khả năng cao do scene trong Figure 2 không chuẩn hóa đúng khối đơn vị nên `N_max` hơi khác 2048 (paper đặt `N_max = 2048 × scene size`), làm bảng `N_l` lệch nhẹ. Tài liệu này **không chắc** nguyên nhân chính xác; khi trích dẫn vào báo cáo nên dùng **con số của paper (12.6 M)**, không dùng con số tự tính.

#### Hệ quả quan trọng: encoding xét như 1 thể là ÁNH XẠ ĐƠN ÁNH (injective)

Paper nêu 1 lập luận rất quan trọng (Section 3, *Implicit hash collision resolution*): vì các **mức thô là ánh xạ 1:1**, nên **chúng hoàn toàn không có collision**, và do đó **toàn bộ encoding xét như 1 thể cũng là đơn ánh** — hai điểm khác nhau trong không gian **không thể** cho ra cùng 1 vector encoding y, vì dù chúng có đụng nhau ở các mức mịn thì các mức thô vẫn phân biệt được chúng.

Đây là mảnh ghép lý thuyết cuối cùng giải thích vì sao hash collision không phá hỏng mô hình — chi tiết đầy đủ ở mục 2.10.

### 2.7. Bước 2b — Hàm hash không gian (Eq. 4 của paper)

Khi cần hash, paper dùng **hàm hash không gian (spatial hash function)** theo Teschner et al. 2003:

```
h(x) = ( ⊕_{i=1}^{d}  x_i · π_i )  mod  T                       (Eq. 4)
```

Viết tường minh cho d = 3 (trường hợp NeRF):

```
h(x) = ( (x₁ · π₁)  XOR  (x₂ · π₂)  XOR  (x₃ · π₃) )  mod  T
```

#### Chú thích ký hiệu

| Ký hiệu | Ý nghĩa |
|---|---|
| **h(x)** | chỉ số entry (số nguyên trong `[0, T)`) ứng với **đỉnh lưới có tọa độ nguyên x** (ở đây x là tọa độ nguyên của đỉnh, không phải tọa độ thực của điểm cần mã hóa) |
| **x_i** | thành phần thứ `i` của tọa độ nguyên của đỉnh (ví dụ với đỉnh (4,9,7) thì x₁=4, x₂=9, x₃=7) |
| **π_i** | **số nguyên tố lớn, phân biệt nhau**, 1 số cho mỗi chiều — là hằng số cố định, không học |
| **⊕ / XOR** | phép **hoặc loại trừ theo bit**: so từng bit của 2 số, bit kết quả = 1 nếu 2 bit đầu vào **khác nhau**, = 0 nếu giống nhau. Ví dụ: `5 XOR 3` = `101₂ XOR 011₂` = `110₂` = 6. |
| **mod T** | lấy phần dư khi chia cho T — **ép** kết quả về đúng dải chỉ số hợp lệ `[0, T)` của bảng. Vì T luôn là lũy thừa của 2 trong paper (2¹⁴…2²⁴), phép này tương đương với "chỉ giữ lại một số bit thấp nhất", rất rẻ trên phần cứng. |

#### Giá trị cụ thể của π_i trong paper

Paper ghi nguyên văn 3 giá trị và **giải thích lý do chọn**:

```
π₁ := 1                    ← CỐ TÌNH đặt bằng 1
π₂ = 2 654 435 761
π₃ = 805 459 861
```

**Vì sao π₁ = 1 (nghe như "không hash chiều thứ nhất")?** Paper lập luận: để đạt tính **(giả) độc lập ((pseudo-)independence)** giữa các chiều, **chỉ cần hoán vị `d − 1` trong `d` chiều** là đủ — chiều còn lại có thể để nguyên. Nhóm tác giả dùng "bậc tự do" này để chọn `π₁ = 1` nhằm **tăng tính liên tục của cache (better cache coherence)**.

**Giải thích sâu hơn ý này (diễn giải của tài liệu này, không phải nguyên văn paper):** khi `π₁ = 1`, hai đỉnh **kề nhau theo chiều x₁** (ví dụ `(4,9,7)` và `(5,9,7)`) sẽ cho 2 chỉ số hash **chênh nhau rất ít** — thường là liền kề. Vì khi tra cứu, 8 đỉnh của 1 ô lưới gồm nhiều cặp chỉ khác nhau ở chiều x₁, việc 2 entry đó nằm sát nhau trong bộ nhớ nghĩa là chúng **cùng rơi vào 1 dòng cache (cache line)** → chỉ cần 1 lần nạp bộ nhớ thay vì 2. Trên GPU, chi phí truy cập bộ nhớ thường là nút thắt lớn hơn chi phí tính toán, nên tối ưu này đáng giá.

#### Vì sao công thức có dạng "nhân số nguyên tố rồi XOR" — ý nghĩa toán học

Paper diễn giải cơ chế: công thức này thực chất **XOR kết quả của d phép hoán vị tuyến tính đồng dư (linear congruential permutation) theo từng chiều** (kiểu sinh số giả ngẫu nhiên Lehmer 1951), nhằm **tách tương quan (decorrelate)** ảnh hưởng của từng chiều lên giá trị hash cuối cùng.

Diễn giải trực giác cho câu trên: phép `x_i · π_i` với π_i là số nguyên tố lớn sẽ "xáo" các giá trị `x_i` liên tiếp (0, 1, 2, 3...) thành 1 dãy số trông như ngẫu nhiên, rải khắp dải số nguyên 32 bit — đây đúng là nguyên lý của bộ sinh số giả ngẫu nhiên đồng dư tuyến tính. Dùng **số nguyên tố** (và **khác nhau cho từng chiều**) để tránh việc 2 chiều "cộng hưởng" với nhau tạo ra mẫu lặp. Sau đó XOR trộn 3 dãy giả ngẫu nhiên này lại; XOR được chọn thay vì phép cộng vì nó **không có nhớ (no carry propagation)**, nên trộn bit đều hơn và rẻ hơn trên phần cứng.

#### Ví dụ số cụ thể — tính hash cho 3 đỉnh

Lấy `T = 2¹⁴ = 16 384`, số học 32-bit không dấu (các tích đều lấy `mod 2³²` theo cách máy tính xử lý số nguyên 32 bit):

**Đỉnh A = (5, 3, 7):**

| Bước | Tính | Kết quả |
|---|---|---|
| `x₁·π₁` | 5 × 1 | 5 |
| `x₂·π₂` | 3 × 2 654 435 761 = 7 963 307 283, lấy mod 2³² | 3 668 339 987 |
| `x₃·π₃` | 7 × 805 459 861 = 5 638 219 027, lấy mod 2³² | 1 343 251 731 |
| XOR cả 3 | 5 ⊕ 3 668 339 987 ⊕ 1 343 251 731 | 2 327 185 413 |
| `mod T` | 2 327 185 413 mod 16 384 | **2 053** |

**Đỉnh B = (6, 3, 7)** (kề A theo chiều x₁ — chiều có π₁=1):

| Bước | Kết quả |
|---|---|
| `x₁·π₁` = 6×1 | 6 |
| 2 thành phần còn lại | giống hệt A |
| XOR | 2 327 185 414 |
| `mod T` | **2 054** |

**Đỉnh C = (5, 3, 8)** (kề A theo chiều x₃ — chiều có π₃ lớn):

| Bước | Kết quả |
|---|---|
| `x₃·π₃` = 8 × 805 459 861 = 6 443 678 888, mod 2³² | 2 148 711 592 |
| XOR cả 3 | 1 521 799 614 |
| `mod T` | **4 542** |

**Đọc kết quả — đây chính là minh họa trực tiếp cho lý lẽ "π₁ = 1 vì cache":**
- A → 2053, B → 2054: **liền kề nhau** trong bộ nhớ. Vì kề nhau theo chiều có π = 1.
- A → 2053, C → 4542: **cách nhau rất xa** (2489 entry). Vì kề nhau theo chiều có π lớn → bị "xáo" đi.

Nghĩa là hàm hash này **cố tình bất đối xứng**: giữ tính liên tục bộ nhớ theo 1 chiều (để tận dụng cache), và xáo trộn 2 chiều kia (để phân bố đều khắp bảng).

#### Paper đã thử 3 hàm hash khác và loại bỏ cả 3 (Section 6, *Choice of hash function*)

| Phương án đã thử | Kết quả báo cáo trong paper |
|---|---|
| **PCG32** — bộ sinh số giả ngẫu nhiên có tính chất thống kê tốt hơn | **Không** cho chất lượng tái tạo tốt hơn → chi phí tính toán cao hơn trở nên không đáng |
| **Sắp các bit thấp của ℤ^d theo đường cong lấp đầy không gian (space-filling curve), chỉ hash các bit cao** | Tra cứu liên tục hơn (tốt cho cache) **nhưng chất lượng tái tạo kém hơn**; mức tăng tốc chỉ nhỉnh hơn chút so với cách đặt `π₁ = 1`, nên không đáng |
| **Coi hàm hash như 1 phép xếp gạch không gian (tiling) thành các lưới đặc** | Tính liên tục còn tốt hơn nữa, nhưng **tăng tốc không nhiều trong thực tế mà chất lượng giảm đáng kể** |

Paper cũng gợi mở hướng tương lai: **tự học luôn cả hàm hash** (biến phương pháp thành học từ điển — dictionary learning), qua (1) 1 công thức đánh chỉ số liên tục có thể lấy đạo hàm giải tích, hoặc (2) thuật toán tối ưu tiến hóa (evolutionary optimization) để duyệt không gian hàm rời rạc.

### 2.8. Bước 3 — Nội suy d-tuyến tính (d-linear interpolation)

Sau Bước 2, ở mỗi mức ta có **8 feature vector** (mỗi vector F = 2 chiều), tương ứng 8 đỉnh của ô lưới chứa x. Bước 3 pha trộn chúng thành **đúng 1 vector F chiều**.

#### Trọng số nội suy

Paper định nghĩa gọn: trọng số nội suy là `w_l := x_l − ⌊x_l⌋`.

| Ký hiệu | Ý nghĩa |
|---|---|
| **w_l** | vector `d` chiều, mỗi thành phần nằm trong `[0,1)`, cho biết **vị trí tương đối của x bên trong ô lưới** ở mức `l`. Thành phần = 0 nghĩa là x nằm sát mặt "dưới" của ô theo chiều đó; = 0.5 là ở giữa; gần 1 là sát mặt "trên". |
| **x_l − ⌊x_l⌋** | chính là **phần thập phân (fractional part)** của `x · N_l` |

**Ví dụ:** với `x = (0.30, 0.60, 0.45)`, `N_l = 16`: `x·N_l = (4.8, 9.6, 7.2)`, `⌊x_l⌋ = (4,9,7)`, nên

```
w_l = (4.8 − 4,  9.6 − 9,  7.2 − 7) = (0.8, 0.6, 0.2)
```

#### Công thức đầy đủ của phép nội suy tam tuyến tính (d = 3)

Gọi 8 đỉnh được đánh chỉ số bằng 1 bộ 3 bit `(c₁, c₂, c₃)` với mỗi `c_i ∈ {0, 1}`: `c_i = 0` nghĩa là lấy `⌊x_l⌋_i`, `c_i = 1` nghĩa là lấy `⌈x_l⌉_i`. Khi đó:

```
f_l(x)  =  Σ_{c ∈ {0,1}³}   W(c) · v_c

với   W(c)  =  Π_{i=1}^{3}  [ c_i = 1 ? w_i : (1 − w_i) ]
```

| Ký hiệu | Ý nghĩa |
|---|---|
| **f_l(x)** | feature vector F chiều, kết quả nội suy tại mức `l` cho điểm x |
| **c = (c₁,c₂,c₃)** | "mã nhị phân" của 1 trong 8 đỉnh |
| **v_c** | feature vector F chiều **đã tra cứu được** ở đỉnh `c` (từ Bước 2) |
| **W(c)** | trọng số của đỉnh `c` — là **tích** của 3 trọng số 1 chiều |
| **w_i** | thành phần thứ `i` của `w_l` |
| **Π** | ký hiệu phép **nhân** liên tiếp (tương tự Σ là phép cộng liên tiếp) |

#### Vì sao công thức có dạng "tích của 3 trọng số 1 chiều" — dẫn từ nội suy 1 chiều

Bắt đầu từ **nội suy tuyến tính 1 chiều**: biết giá trị `v₀` tại vị trí 0 và `v₁` tại vị trí 1, muốn đoán giá trị tại vị trí `w ∈ [0,1]`:

```
lerp(v₀, v₁, w) = (1 − w)·v₀ + w·v₁
```

Kiểm tra: `w = 0` → ra `v₀` ✓; `w = 1` → ra `v₁` ✓; `w = 0.5` → ra trung bình ✓. Trọng số `(1−w)` và `w` luôn cộng lại bằng 1, nên kết quả luôn nằm giữa `v₀` và `v₁`.

**Mở sang 2 chiều (bilinear):** áp dụng lerp 2 lần — trước theo chiều 1 cho 2 cạnh của hình vuông, rồi lerp 2 kết quả đó theo chiều 2. Khai triển ra sẽ thấy 4 trọng số là `(1−w₁)(1−w₂)`, `w₁(1−w₂)`, `(1−w₁)w₂`, `w₁w₂` — đúng dạng **tích**.

**Mở sang 3 chiều (trilinear):** lặp thêm 1 lần nữa cho chiều 3 → 8 trọng số, mỗi trọng số là tích của 3 nhân tử. Tổng quát hóa cho `d` chiều thì có `2^d` trọng số, mỗi trọng số là tích của `d` nhân tử — đây là lý do paper gọi nó là **`d`-linear interpolation** chứ không chỉ "trilinear": cùng 1 công thức dùng được cho ảnh 2D (bilinear) và NeRF 3D (trilinear).

**Tính chất đáng chú ý:** tổng toàn bộ `2^d` trọng số **luôn bằng đúng 1**, bất kể `w` là gì. Chứng minh nhanh: `Σ_c Π_i [...] = Π_i [(1−w_i) + w_i] = Π_i 1 = 1` (phân phối tích thành tổng). Nghĩa là phép nội suy này là 1 **tổ hợp lồi (convex combination)** của 8 feature vector — kết quả luôn nằm trong "bao lồi" của 8 giá trị gốc, không bao giờ bị "bay" ra ngoài.

#### Ví dụ số đầy đủ

Tiếp tục ví dụ: `w = (0.8, 0.6, 0.2)`, F = 2. Giả sử 8 feature vector tra cứu được (đây là **giá trị giả định để minh họa** — trong thực tế chúng là tham số đã học):

| Đỉnh `c = (c₁,c₂,c₃)` | Trọng số `W(c)` | Phép tính trọng số | Feature `v_c` |
|---|---:|---|---|
| (0,0,0) | 0.064 | 0.2 × 0.4 × 0.8 | (0.10, −0.20) |
| (0,0,1) | 0.016 | 0.2 × 0.4 × 0.2 | (0.30, 0.00) |
| (0,1,0) | 0.096 | 0.2 × 0.6 × 0.8 | (−0.40, 0.10) |
| (0,1,1) | 0.024 | 0.2 × 0.6 × 0.2 | (0.60, −0.30) |
| (1,0,0) | 0.256 | 0.8 × 0.4 × 0.8 | (0.50, 0.30) |
| (1,0,1) | 0.064 | 0.8 × 0.4 × 0.2 | (−0.10, 0.40) |
| (1,1,0) | **0.384** | 0.8 × 0.6 × 0.8 | (0.20, 0.60) |
| (1,1,1) | 0.096 | 0.8 × 0.6 × 0.2 | (0.00, 0.50) |
| **Tổng** | **1.000** | ✓ (kiểm chứng tính chất trên) | |

Kết quả nội suy:

```
Thành phần 1: 0.064(0.10) + 0.016(0.30) + 0.096(−0.40) + 0.024(0.60)
            + 0.256(0.50) + 0.064(−0.10) + 0.384(0.20) + 0.096(0.00)
            = 0.1856

Thành phần 2: 0.064(−0.20) + 0.016(0.00) + 0.096(0.10) + 0.024(−0.30)
            + 0.256(0.30) + 0.064(0.40) + 0.384(0.60) + 0.096(0.50)
            = 0.3704

⟹  f_l(x) = (0.1856, 0.3704)
```

Lưu ý đỉnh `(1,1,0)` có trọng số lớn nhất (0.384) — hợp lý, vì `w = (0.8, 0.6, 0.2)` nghĩa là x nằm gần góc "cao" theo chiều 1 và 2, nhưng gần góc "thấp" theo chiều 3.

#### Vì sao BẮT BUỘC phải nội suy (không được lấy entry gần nhất)

Paper dành 1 đoạn riêng (Section 3, *d-linear interpolation*) để giải thích. Ba lý do, theo thứ tự quan trọng:

1. **Đảm bảo tính liên tục.** Nội suy làm cho hàm `enc(x; θ)` **liên tục**, và theo **quy tắc chuỗi (chain rule)**, hợp của nó với mạng — `m(enc(x; θ); Φ)` — cũng liên tục.
2. **Nếu không nội suy, ảnh sẽ bị "khối" (blocky).** Paper nói rõ: không nội suy thì output của mạng sẽ có **các điểm gián đoạn trùng khớp với lưới (grid-aligned discontinuities)**, cho ra hình ảnh trông như bị chia ô vuông — lỗi thị giác rất dễ thấy.
3. **Nội suy là thứ làm gradient chảy được vào bảng.** (Diễn giải của tài liệu này, suy từ Figure 3 của paper.) Vì `f_l(x)` là tổ hợp tuyến tính của 8 feature vector với trọng số `W(c)`, đạo hàm riêng `∂f_l/∂v_c = W(c)` — tức là **gradient được phân chia cho 8 đỉnh theo đúng tỉ lệ trọng số nội suy**: đỉnh nào gần x hơn (trọng số lớn hơn) thì nhận gradient nhiều hơn. Nếu chỉ lấy entry gần nhất (nearest lookup), đạo hàm theo `x` sẽ bằng 0 hầu khắp mọi nơi và không xác định tại biên ô — mô hình không thể học bằng gradient descent theo cách này.

> **🔄 KHÁC VỚI NeRF GỐC.** NeRF gốc **không có khái niệm nội suy** — hàm `sin`/`cos` đã trơn sẵn ở mọi nơi (khả vi vô hạn lần, `C^∞`). Instant-NGP phải **chủ động dựng lại tính trơn** bằng nội suy, và chỉ đạt được mức **`C⁰` (liên tục nhưng đạo hàm có bước nhảy tại biên ô lưới)**. Đây là 1 **điểm đánh đổi mà Instant-NGP kém hơn** NeRF gốc về mặt toán học, và nó có hậu quả thật — xem mục 2.9.

### 2.9. Tùy chọn nâng cao — nội suy trơn hơn bằng hàm smoothstep (Appendix A)

Paper dành **Appendix A** cho tình huống cần độ trơn cao hơn `C⁰`.

**Vấn đề:** nội suy `d`-tuyến tính cho hàm liên tục, nhưng **đạo hàm bị gián đoạn** tại biên các ô lưới. Với NeRF (dự đoán màu/density) thì thường không sao. Nhưng với các bài toán cần đạo hàm trơn — ví dụ **SDF**, nơi `∂m(enc(x;θ);Φ)/∂x` chính là **pháp tuyến bề mặt (surface normal)** — thì đạo hàm gián đoạn gây lỗi nhìn thấy được. Cần đạo hàm trơn cũng là yêu cầu khi xấp xỉ **phương trình vi phân riêng (partial differential equations)**.

**Giải pháp hiển nhiên nhưng đắt:** dùng nội suy `d`-bậc hai (`d`-quadratic) hoặc `d`-bậc ba (`d`-cubic). Paper chỉ ra chi phí: cần tra cứu **`3^d`** và **`4^d`** đỉnh thay vì `2^d`. Với d = 3: **27 và 64 đỉnh** thay vì 8 — đắt gấp 3.4 và 8 lần.

**Giải pháp rẻ mà paper khuyến nghị:** áp hàm **smoothstep** lên chính các trọng số nội suy, trước khi nội suy:

```
S₁(x) = x²(3 − 2x)                           (Eq. 5)

S₁′(x) = 6x(1 − x)                            (Eq. 6)
```

| Ký hiệu | Ý nghĩa |
|---|---|
| **S₁(x)** | hàm smoothstep bậc 1 — biến 1 trọng số `x ∈ [0,1]` thành 1 trọng số khác cũng trong `[0,1]`, nhưng "mượt hơn ở 2 đầu" |
| **S₁′(x)** | đạo hàm của S₁ |

**Cơ chế hoạt động — vì sao nó làm encoding trơn hơn:** Điểm then chốt mà paper nhấn mạnh là **đạo hàm `S₁′` triệt tiêu (bằng 0) tại cả x = 0 và x = 1**. Kiểm chứng: `S₁′(0) = 6·0·1 = 0` ✓, `S₁′(1) = 6·1·0 = 0` ✓. Vì vậy, theo **quy tắc chuỗi**, điểm gián đoạn trong đạo hàm của encoding (vốn xuất hiện đúng tại biên ô, tức đúng tại `w = 0` và `w = 1`) bị **nhân với 0 → triệt tiêu**. Encoding trở thành **`C¹`-trơn** (liên tục và có đạo hàm bậc 1 liên tục).

Kiểm tra thêm S₁ giữ đúng 2 đầu: `S₁(0) = 0` ✓, `S₁(1) = 1·(3−2) = 1` ✓ — nên không làm lệch kết quả tại các đỉnh lưới.

**Nhưng có 1 vấn đề phát sinh, và cách paper khắc phục:** mẹo trên thực chất **đổi "điểm gián đoạn" thành "điểm có đạo hàm bằng 0"** — chưa chắc dễ chịu hơn (vì đạo hàm bằng 0 nghĩa là mô hình "phẳng" tại đó, không học được biến thiên). Paper khắc phục bằng cách **dịch mỗi mức đi nửa kích thước ô của chính nó, tức `1/(2N_l)`**, để các điểm đạo hàm-bằng-0 của 16 mức **không trùng nhau**. Nhờ đó tại mọi vị trí `x`, luôn có ít nhất vài mức có đạo hàm khác 0, và encoding tổng thể vẫn học được đạo hàm trơn, khác 0 ở mọi nơi.

> **⚠️ ĐIỂM RẤT DỄ TRÍCH DẪN SAI — PAPER KHÔNG DÙNG SMOOTHSTEP TRONG CÁC KẾT QUẢ CÔNG BỐ.** Paper nói rõ ở 2 chỗ (Section 3 cuối mục *d-linear interpolation*, và Appendix A): *"we however do not employ [it] in any of our results due to a small decrease in reconstruction quality"*. Lý do: chi phí tính toán của S₁ thực ra **miễn phí** (bị che bởi nút thắt bộ nhớ), **nhưng chất lượng tái tạo lại giảm** khi dùng nội suy bậc cao hơn. Paper thừa nhận **chưa giải thích được vì sao chất lượng giảm** — cần nghiên cứu thêm. Vậy: smoothstep là **tùy chọn tắt theo mặc định**, không phải phần của Instant-NGP "chuẩn".

### 2.10. Bước 4 — Nối (concatenate) L mức, và vì sao không cộng

Sau Bước 3, ta có **L = 16 vector**, mỗi vector F = 2 chiều. Bước 4 **nối** chúng lại, kèm theo các chiều phụ `ξ ∈ ℝ^E`:

```
y  =  enc(x; θ)  =  [ f₀(x) ‖ f₁(x) ‖ ... ‖ f_{L−1}(x) ‖ ξ ]   ∈  ℝ^(L·F + E)
```

| Ký hiệu | Ý nghĩa |
|---|---|
| **‖** | phép **nối vector (concatenation)** — xếp các vector nối đuôi nhau thành 1 vector dài hơn, không trộn giá trị |
| **L·F** | số chiều đến từ phần không gian: 16 × 2 = **32 chiều** |
| **E** | số chiều phụ. Với NeRF, `ξ` = hướng nhìn đã mã hóa (16 chiều, xem mục 2.12) nhưng **được đưa vào MLP màu chứ không vào MLP density** — xem Giai đoạn 3 để thấy chi tiết. |

**Con số cụ thể cho NeRF:** phần vị trí cho `L·F = 16 × 2 = 32` chiều. Đây là input của **MLP density**.

> **🔄 KHÁC VỚI NeRF GỐC — ĐÂY LÀ MỘT CON SỐ RẤT ĐÁNG NHỚ.** NeRF gốc: `γ(x)` có **60 chiều** (L_f=10, 3 tọa độ × 2 hàm × 10 tần số). Instant-NGP: encoding vị trí có **32 chiều**. Tức là **input của mạng còn NHỎ HƠN gần một nửa**, trong khi chất lượng lại cao hơn. Điều này nhấn mạnh 1 điểm: cái làm nên sức mạnh **không phải số chiều của encoding**, mà là **việc encoding đó có tham số học được, mang thông tin riêng cho từng vùng không gian**. 60 chiều sin/cos của NeRF gốc chứa đúng 0 bit thông tin về cảnh cụ thể; 32 chiều của Instant-NGP chứa thông tin đã được chưng cất từ hàng triệu tham số bảng hash.

**Vì sao nối (concatenate) chứ không rút gọn (reduce, ví dụ cộng lại)?** Paper trả lời trong Section 6 (*Concatenation vs. reduction*), nêu đúng 2 lý do:

1. **Nối cho phép xử lý mỗi mức độc lập, song song hoàn toàn.** Không có bước nào phải chờ mức khác xong.
2. **Rút gọn từ `L·F` xuống `F` chiều thì quá ít thông tin.** Với F = 2, nếu cộng 16 mức lại thì chỉ còn **2 số** để mô tả toàn bộ thông tin đa tỉ lệ của 1 điểm — không đủ. Về nguyên tắc có thể tăng F lên để bù, nhưng như vậy **encoding sẽ đắt hơn nhiều** (mỗi lần tra cứu phải nạp F số).

Paper cũng rất cẩn trọng, không tuyệt đối hóa: họ nói đây là lựa chọn **mặc định, không phải quy tắc cứng**, và nêu rõ trường hợp ngược lại: nếu mạng nơ-ron **đắt hơn nhiều** so với encoding, thì chi phí tăng F trở nên không đáng kể và rút gọn có thể lại hay hơn. Trong các ứng dụng của paper, **nối + F = 2 luôn cho kết quả tốt vượt trội**.

Một chi tiết lịch sử thú vị liên quan (Appendix B): khi nhóm tác giả cài đặt lại **NGLOD** (phương pháp dùng octree, là đối thủ so sánh ở bài toán SDF) để so sánh công bằng, họ **đổi NGLOD từ "cộng" sang "nối"** các feature vector — và việc này **tình cờ (serendipitously) làm NGLOD tốt hơn** so với bản gốc dùng phép cộng, ở cùng số tham số. Tức bằng chứng ủng hộ "nối" không chỉ đến từ phương pháp của chính họ.

### 2.11. Hash collision — vì sao vẫn train tốt (lập luận chính xác theo paper)

Đây là câu hỏi hiển nhiên nhất và cũng là chỗ **dễ giải thích sai nhất**. Paper trả lời trong Section 3 (*Implicit hash collision resolution*), và lập luận gồm **4 mảnh ghép**, phải đủ cả 4 mới thành lập luận hoàn chỉnh.

#### Trước hết — định nghĩa chính xác "collision" ở đây là gì

Paper nói rõ 1 điều rất dễ nhầm: *"Nearby inputs with equal integer coordinates `⌊x_l⌋` are **not** considered a collision; a collision occurs when **different integer coordinates hash to the same index**."*

Dịch nghĩa: hai **điểm thực** `x` và `x′` gần nhau, rơi vào **cùng 1 ô lưới** (nên có cùng `⌊x_l⌋`) thì **KHÔNG phải collision** — đó là hành vi đúng và mong muốn của 1 lưới (chúng vốn nên chia sẻ cùng các đỉnh, chỉ khác trọng số nội suy). Collision là khi **hai đỉnh lưới có tọa độ nguyên khác nhau** lại cho ra **cùng 1 chỉ số hash**.

#### Mảnh 1 — Các mức thô hoàn toàn không có collision

Như đã nói ở mục 2.6: với mức `l` thỏa `(N_l+1)^d ≤ T`, ánh xạ là 1:1. Paper diễn đạt: các mức thô, *"and thus the encoding as a whole, are **injective** — that is, they suffer from no collisions at all"*. Nhưng chúng **chỉ biểu diễn được phiên bản độ phân giải thấp của cảnh**, vì feature được nội suy từ 1 lưới điểm thưa.

#### Mảnh 2 — Các mức mịn thì nhiều collision, nhưng collision được rải GIẢ NGẪU NHIÊN

Mức mịn bắt được chi tiết nhỏ nhờ lưới dày, nhưng **bị nhiều collision**. Điểm cứu nguy: nhờ hàm hash XOR-số-nguyên-tố, các collision được **rải giả ngẫu nhiên khắp không gian (pseudo-randomly scattered across space)**.

Hệ quả xác suất mà paper rút ra: với 1 cặp điểm cho trước, việc chúng **đồng thời collide ở TẤT CẢ các mức** là **cực kỳ khó xảy ra về mặt thống kê**.

**Minh họa định lượng (diễn giải/tính toán bổ sung của tài liệu này, không có trong paper):** giả sử mỗi mức mịn độc lập có xác suất collide của 1 cặp đỉnh cho trước là `p ≈ 1/T`. Với `T = 2¹⁹` và 11 mức mịn, xác suất collide **đồng thời ở cả 11 mức** xấp xỉ `(1/524288)^11 ≈ 10^(−62)` — bằng 0 trên thực tế. Nghĩa là **luôn còn ít nhất vài mức phân biệt được 2 điểm bất kỳ**. ⚠️ Giả định "độc lập" ở đây là xấp xỉ của tài liệu này để minh họa trực giác; paper chỉ nói "statistically unlikely" mà không đưa con số.

#### Mảnh 3 — Khi collide, gradient LẤY TRUNG BÌNH, và mẫu quan trọng ÁP ĐẢO

Đây là mảnh ghép hay nhất và cũng là chỗ bản sơ bộ thường nói chưa đúng cơ chế. Paper mô tả:

> Khi các mẫu train collide, **gradient của chúng được lấy trung bình (their gradients average)**. Nhưng **mức độ quan trọng của chúng với kết quả tái tạo cuối cùng thường KHÔNG bằng nhau**.

Và paper đưa ví dụ cực cụ thể cho trường hợp radiance field:

- 1 điểm **trên bề mặt nhìn thấy được**: nó đóng góp mạnh vào ảnh tái tạo, vì nó có **độ nhìn thấy cao (high visibility)** VÀ **density cao** — và paper nhấn mạnh **hai yếu tố này nhân với nhau (multiplicatively)** để quyết định độ lớn của gradient. (Đối chiếu `pipeline_NeRF.md` Giai đoạn 4 mục 2: đây chính là trọng số `w_i = T_i · α_i` — "visibility" là `T_i`, "density" phản ánh qua `α_i`.) → gây **thay đổi lớn** cho entry bảng.
- 1 điểm **trong không gian trống** tình cờ trỏ vào cùng entry đó: **trọng số nhỏ hơn rất nhiều** → gần như không làm entry đó dịch chuyển.

Kết luận của paper: *"the gradients of the more important samples **dominate the collision average** and the aliased table entry will naturally be optimized in such a way that it reflects the needs of the higher-weighted point."* — Tức bảng hash **tự động ưu tiên** vùng thưa có chi tiết tinh quan trọng nhất, **không cần ai lập trình quy tắc ưu tiên nào cả**.

> **💡 ĐÂY LÀ ĐIỂM TINH TẾ MÀ BẢN SƠ BỘ TRONG `nerf_cai_tien.md` NÓI CHƯA ĐÚNG.** Bản sơ bộ viết: *"các đỉnh va chạm **thường rơi vào vùng density thấp**"*. Điều này **không đúng** — hàm hash rải collision **giả ngẫu nhiên**, nên các cặp collide **không hề thiên về vùng density thấp**: nó ngẫu nhiên, nên 1 đỉnh bề mặt có thể collide với 1 đỉnh bề mặt khác. Lập luận **đúng** của paper không phải "collision tránh được vùng quan trọng", mà là: (a) collision xảy ra tràn lan nhưng **chỉ ở mức mịn**, (b) **mức thô vẫn phân biệt được**, và (c) khi collide thì **gradient lấy trung bình có trọng số thực tế** nên mẫu quan trọng thắng. Đây là khác biệt về bản chất lập luận, không chỉ là cách diễn đạt.

#### Mảnh 4 — Đa độ phân giải đảm bảo PHỦ ĐỦ mọi tỉ lệ có ý nghĩa

Paper tổng kết: cấu trúc đa mức phủ toàn bộ dải từ `N_min` (**được bảo đảm không có collision**) tới `N_max` (độ phân giải mà bài toán cần). Nhờ đó **bảo đảm mọi tỉ lệ (scale) mà việc học có thể diễn ra một cách có ý nghĩa đều được bao gồm, bất kể cảnh thưa thớt đến mức nào**.

#### Nhưng collision CÓ gây lỗi thấy được — paper không che giấu điều này

Paper thừa nhận rõ ràng (Section 5.2 và Section 6, *Microstructure due to hash collisions*):

- Lỗi đặc trưng của encoding này là 1 lượng nhỏ **"vi cấu trúc dạng hạt" (grainy microstructure)** — bề mặt trông lấm tấm/sần.
- Lỗi này **rõ nhất ở bài toán SDF** (Figure 1 và Figure 7), ở **đúng tỉ lệ của mức lưới mịn nhất**, và **không mất đi dù train lâu hơn**.
- Nhóm tác giả **gán nguyên nhân cho hash collision**, dựa trên 1 lập luận so sánh rất thuyết phục: **NGLOD về bản chất là phiên bản KHÔNG-collision tương đương với hash encoding** (dùng octree thay bảng hash), và **lỗi này vắng mặt hoàn toàn trong NGLOD** → nên nó phải do collision.
- Paper nói: *"Upon close inspection, similar microstructure can be seen in other neural graphics primitives, **although with significantly lower magnitude**."* → tức **NeRF cũng có, nhưng nhẹ hơn nhiều** so với SDF. (Lý do suy ra được: SDF được hiển thị bằng mô hình tô bóng (shading) phụ thuộc **pháp tuyến** = đạo hàm, nên cực kỳ nhạy với dao động nhỏ; còn NeRF dự đoán màu trực tiếp nên ít lộ hơn.)
- Hai hướng khắc phục paper đề xuất cho tương lai: **lọc (filter) kết quả tra cứu bảng hash**, hoặc **thêm 1 tiên nghiệm về độ trơn (smoothness prior) vào hàm loss**.

#### Và 1 lựa chọn thiết kế rất "ngược sách giáo khoa" cần nhấn mạnh

> **🔄 INSTANT-NGP CỐ TÌNH KHÔNG XỬ LÝ COLLISION THEO CÁCH TRUYỀN THỐNG.** Paper nêu rõ (Section 2 cuối): khác với các công trình trước dùng spatial hashing cho tái tạo 3D (ví dụ Voxel Hashing của Nießner et al. 2013), họ **không dùng bất kỳ kỹ thuật xử lý collision kinh điển nào — không probing, không bucketing, không chaining**. Thay vào đó họ **dựa vào chính mạng nơ-ron để tự học cách phân biệt (disambiguate) các collision**.
>
> Lý do là **thuần về hiệu năng GPU**: 3 kỹ thuật kinh điển kia đều đòi **rẽ nhánh điều khiển (control flow)** — tức các luồng (thread) trong cùng 1 warp phải đi những đường khác nhau, gây **phân kỳ thực thi (execution divergence)**, cực đắt trên GPU. Bỏ hẳn chúng cho 3 lợi ích paper liệt kê: **tránh phân kỳ, giảm độ phức tạp cài đặt, và tăng hiệu năng**.

### 2.12. Tính thích nghi trực tuyến (Online adaptivity) — 1 lợi ích "miễn phí"

Paper nêu 1 tính chất đẹp (Section 3, *Online adaptivity*): nếu **phân phối của input `x` thay đổi theo thời gian trong lúc train** — ví dụ chúng dồn lại vào 1 vùng nhỏ — thì **các mức lưới mịn sẽ tự nhiên gặp ÍT collision hơn** (vì ít đỉnh khác nhau được truy cập hơn), nên mô hình **học được hàm chính xác hơn ở vùng đó**.

Nói cách khác: multiresolution hash encoding **tự động thích nghi với phân phối dữ liệu train**, **thừa hưởng lợi ích của các encoding dựa trên cây (tree-based)** như NGLOD, **mà không cần bảo trì cấu trúc dữ liệu riêng cho từng bài toán** — và do đó **không gây ra các bước nhảy rời rạc (discrete jumps) trong lúc train** (vốn là hệ quả tất yếu của việc định kỳ tỉa/chia cây).

Lợi ích này được khai thác mạnh nhất ở bài toán **neural radiance caching** (Section 5.3), nơi mô hình phải liên tục thích nghi với **góc nhìn và nội dung 3D đang chuyển động**, với ngân sách train chỉ **1 mili-giây mỗi khung hình**.

⚠️ **Lưu ý khi áp dụng cho NeRF:** với NeRF train theo kiểu offline trên 1 tập ảnh cố định, phân phối input không thay đổi nhiều, nên lợi ích này **ít rõ rệt hơn**. Đây là lợi ích chủ yếu cho các kịch bản train trực tuyến.

### 2.13. Đếm tham số & bộ nhớ của encoding

Paper nêu: số tham số học được của encoding là **`O(T)`**, và **bị chặn trên bởi `T · L · F`**, trong trường hợp của họ luôn là `T · 16 · 2`.

| Đại lượng | Công thức | Ví dụ với T = 2¹⁹ |
|---|---|---|
| Chặn trên số tham số | `T · L · F` | 524 288 × 16 × 2 = **16 777 216 ≈ 16.8 M** |
| Số tham số **thực tế** | `F · Σ_l min( (N_l+1)^d , T )` | **≈ 12.2 M** (các mức thô nhỏ hơn T nên không dùng hết) |
| Bộ nhớ (lưu ở độ chính xác **nửa**, 2 byte/số) | `2 byte × số tham số` | ≈ **24.4 MB** |

Về bộ nhớ, paper ghi 2 chi tiết triển khai quan trọng (Section 4, *Performance considerations*):

1. **Entry bảng hash được lưu ở độ chính xác nửa (half precision, 2 byte/entry)** để tối ưu hiệu năng suy luận và lan truyền ngược.
2. Nhưng vẫn **giữ thêm 1 bản sao chủ (master copy) của tham số ở độ chính xác đầy đủ (full precision)** để việc cập nhật tham số kiểu **độ chính xác trộn (mixed-precision)** được ổn định (theo Micikevicius et al. 2018).

**Đánh đổi T — paper nói gọn và rõ:**

| Tăng T lên | Chất lượng | Hiệu năng | Bộ nhớ |
|---|---|---|---|
| Hướng thay đổi | **tăng** | **giảm** | **tăng** |
| Bậc tăng trưởng | dưới-tuyến tính (sub-linear) | dưới-tuyến tính | **tuyến tính theo T** |

Paper khuyến nghị người dùng **dùng chính T làm "cái núm" để điều chỉnh** encoding sao cho khớp với đặc tính hiệu năng mong muốn.

#### Và 1 "vách đá hiệu năng" rất cụ thể do kích thước cache GPU

Paper báo cáo 1 hiện tượng đo được (Section 4 + Figure 4): trên phần cứng của họ, hiệu năng của encoding **gần như không đổi khi `T ≤ 2¹⁹`**, nhưng **tụt mạnh khi vượt ngưỡng đó**. Nguyên nhân được giải thích bằng 1 phép tính rất tường minh: GPU **NVIDIA RTX 3090** có **L2 cache 6 MB**, và cache này trở nên quá nhỏ cho từng mức riêng lẻ khi

```
2 · T · F  >  6 · 2²⁰          (với số 2 đầu tiên = số byte của 1 entry half-precision)
```

Kiểm chứng: với `T = 2¹⁹`, `F = 2` → `2 · 524288 · 2 = 2 097 152` byte = 2 MB < 6 MB ✓ (vẫn vừa). Với `T = 2²¹` → `2 · 2097152 · 2 = 8 MB > 6 MB` ✗ (vỡ cache). → đúng khớp với "vách đá" quan sát được trong Figure 4 ở `T > 2¹⁹`.

Paper cũng mô tả **chiến lược tính toán** làm nên tính chất này: họ **đánh giá các bảng hash theo từng mức một (level by level)** — khi xử lý 1 lô (batch) các vị trí input, họ tra mức 0 cho **toàn bộ** input, rồi mức 1 cho **toàn bộ** input, v.v. Nhờ vậy, **ở mỗi thời điểm chỉ cần ít bảng hash liên tiếp nằm trong cache**, và cấu trúc tính toán này **tự động tận dụng tốt cache + tính song song cho 1 dải rộng giá trị T**.

### 2.14. Hướng nhìn: Spherical Harmonics thay cho γ(d) — chi tiết bị bỏ sót nhiều nhất

Multiresolution hash encoding chỉ dành cho **tọa độ không gian** `x`. Nhưng NeRF còn cần mã hóa **hướng nhìn**. Paper xử lý riêng (Section 4, *Non-spatial input dimensions ξ ∈ ℝ^E*; và Section 5.4):

Paper nói rõ lý do tách riêng: hash encoding **nhắm vào tọa độ không gian có số chiều tương đối thấp** (mọi thí nghiệm của họ chỉ 2D hoặc 3D). Với các chiều phụ, họ dùng các **kỹ thuật đã được thiết lập, có chi phí không tăng siêu-tuyến tính theo số chiều**:

| Bài toán | Encoding dùng cho chiều phụ `ξ` |
|---|---|
| Neural radiance caching | **one-blob encoding** (Müller et al. 2019) |
| **NeRF** | **cơ sở Spherical Harmonics (hàm điều hòa cầu)** |

Với NeRF, paper ghi rõ: hướng nhìn được **chiếu lên 16 hệ số đầu tiên của cơ sở spherical harmonics (tức tới bậc 4)**, và nhận xét đây là *"một frequency encoding tự nhiên trên các vector đơn vị"*. Paper cũng nêu đây là lựa chọn **tương tự các công trình đồng thời** (Ref-NeRF của Verbin et al. 2021, Plenoxels của Yu et al. 2021a).

| Ký hiệu | Ý nghĩa |
|---|---|
| **Spherical Harmonics (SH)** | một **họ hàm cơ sở trực giao định nghĩa trên mặt cầu** — đóng vai trò tương tự như hàm sin/cos trong khai triển Fourier, nhưng miền xác định là **mặt cầu** thay vì đường thẳng. Mỗi hàm SH ứng với 1 "tần số góc"; bậc càng cao thì mô tả được biến thiên theo hướng càng nhanh. |
| **bậc (degree / band) `ℓ`** | mức tần số của SH. Băng thứ `ℓ` có `2ℓ+1` hàm cơ sở. |
| **16 hệ số đầu tiên** | tổng số hàm cơ sở của các băng `ℓ = 0,1,2,3`: `1 + 3 + 5 + 7 = 16`. |

> **⚠️ GHI CHÚ KHÔNG CHẮC CHẮN VỀ CÁCH ĐẾM BẬC.** Paper viết *"the first 16 coefficients of the spherical harmonics basis (i.e. up to degree 4)"*. Con số **16 hệ số là rõ ràng và không gây tranh cãi**. Nhưng cụm "up to degree 4" thì **mơ hồ**: 16 hệ số tương ứng các băng `ℓ = 0, 1, 2, 3` — tức **4 băng**, nhưng **bậc cao nhất là ℓ = 3**, không phải 4. Cách hiểu hợp lý nhất là paper đang **đếm số băng (4 băng)** chứ không phải chỉ số bậc cao nhất. Khi trích vào báo cáo, **nên ghi "16 hệ số SH đầu tiên"** (dữ kiện chắc chắn) và tránh phát biểu về "bậc 4" nếu không giải thích kèm cách đếm.

> **🔄 KHÁC VỚI NeRF GỐC — BẢNG ĐỐI CHIẾU MÃ HÓA HƯỚNG NHÌN**
>
> | | NeRF gốc | Instant-NGP |
> |---|---|---|
> | Kỹ thuật | Positional encoding sin/cos, `L_f = 4` | **Cơ sở Spherical Harmonics**, 16 hệ số đầu |
> | Số chiều kết quả | 3 × 2 × 4 = **24 chiều** | **16 chiều** |
> | Miền xác định của hàm cơ sở | đường thẳng thực (áp riêng cho từng thành phần của d_view) | **mặt cầu** (áp cho cả vector đơn vị như 1 thể) |
> | Có tham số học được? | Không | Không (SH cũng là cơ sở cố định) |
> | **Lý do đổi** | — | SH là cơ sở **tự nhiên cho hàm trên mặt cầu**: hướng nhìn vốn **là** 1 điểm trên mặt cầu đơn vị, nên cơ sở SH tôn trọng đúng hình học của miền đó; còn việc áp sin/cos riêng cho từng thành phần x,y,z của d_view **không tôn trọng ràng buộc "vector đơn vị"**. Kèm theo lợi ích thực tiễn: **ít chiều hơn** (16 so với 24) nên MLP màu nhỏ hơn. |

### 2.15. Kết quả Giai đoạn 2 & bảng đối chiếu tổng kết

Sau Giai đoạn 2, với mỗi điểm mẫu 3D `x` trên tia, ta có:
- **32 số** (= L·F = 16×2) — kết quả của multiresolution hash encoding tại x, sẵn sàng đưa vào **MLP density**;
- **16 số** — hướng nhìn `d_view` đã chiếu lên cơ sở SH, sẽ được đưa vào **MLP màu** ở Giai đoạn 3.

#### BẢNG ĐỐI CHIẾU GIAI ĐOẠN 2 — NeRF gốc vs Instant-NGP

| Thành phần | NeRF gốc | Instant-NGP | Lý do đổi |
|---|---|---|---|
| Kiểu encoding vị trí | Frequency encoding (sin/cos) **cố định** | **Multiresolution hash encoding**, **có tham số học được** | Chuyển gánh nặng học ra khỏi MLP → cho phép MLP nhỏ đi hàng chục lần |
| Số chiều encoding vị trí | 60 | **32** | Thông tin nằm trong tham số bảng, không cần nhiều chiều |
| Số tham số của encoding | **0** | `O(T)`, chặn trên `T·L·F` (0.5 M – 266 M) | Đánh đổi bộ nhớ để lấy tốc độ train |
| Tham số phải cập nhật mỗi mẫu train | **Toàn bộ** MLP (~438 k) | ~10 k MLP + **đúng 128 feature vector** | "Tính thưa thớt của cập nhật" = nguồn tốc độ chính |
| Cấu trúc dữ liệu | không có | 16 bảng, mỗi bảng ≤ T entry × 2 chiều | — |
| Có cần cập nhật/tỉa cấu trúc trong lúc train? | — | **KHÔNG, không bao giờ** | Tránh pointer chasing + control flow divergence trên GPU; đơn giản hóa quy trình train |
| Tra cứu | — | **O(1), không rẽ nhánh, L mức song song** | Khớp kiến trúc GPU |
| Độ trơn của encoding | `C^∞` (sin/cos khả vi vô hạn) | **`C⁰`** (nội suy d-tuyến tính); có thể lên `C¹` bằng smoothstep nhưng **mặc định tắt vì giảm chất lượng** | Đánh đổi: Instant-NGP **kém hơn** ở khía cạnh này |
| Mã hóa hướng nhìn | sin/cos, `L_f=4` → 24 chiều | **Spherical Harmonics**, 16 hệ số → 16 chiều | Cơ sở tự nhiên cho hàm trên mặt cầu |
| Số siêu tham số cần tinh chỉnh | L_f cho vị trí và hướng | **chỉ 2: T và N_max** | Dùng chung cài đặt cho cả 4 bài toán khác nhau |

---

## Giai đoạn 3 — Hai MLP nhỏ & Volume Rendering

Tương ứng **Section 5.4 (*Model Architecture*)**, **Section 4 (*Architecture*, *Initialization*)**, **Figure 10** (ablation kích thước MLP) và **Figure 11** (ablation MLP vs lớp tuyến tính) của paper.

### 3.1. Kiến trúc: HAI MLP nối tiếp nhau, không phải một

Paper mở đầu phần này bằng 1 câu rất đáng chú ý: *"**Unlike the other three applications**, our NeRF model consists of **two concatenated MLPs**"*.

> **⚠️ ĐÂY LÀ CHỖ CỰC KỲ DỄ TRÍCH DẪN SAI.** Paper nêu ở Section 4 (*Architecture*): *"In all tasks, **except for NeRF which we will describe later**, we use an MLP with two hidden layers that have a width of 64 neurons"*. Tức **"2 lớp ẩn × 64 kênh" là cấu hình cho 3 bài toán KHÁC (gigapixel, SDF, NRC) — KHÔNG phải cấu hình NeRF.** Cấu hình NeRF là **hai MLP riêng biệt** với số lớp khác nhau, mô tả ở Section 5.4. Bất kỳ tài liệu nào nói "Instant-NGP dùng MLP 2 lớp 64 kênh cho NeRF" đều đang nói **thiếu/sai**.

#### MLP density (mạng mật độ)

| Thuộc tính | Giá trị theo paper |
|---|---|
| Input | `y = enc(x; θ)` — **32 chiều** (L·F = 16×2) |
| Số lớp ẩn | **1** |
| Độ rộng lớp ẩn | **64 neuron** |
| Activation lớp ẩn | **ReLU** |
| Output | **16 giá trị**, lớp output **tuyến tính** (không activation) |
| Ý nghĩa output | **giá trị đầu tiên trong 16** được coi là **density trong không gian logarit (log-space density)**; 15 giá trị còn lại là đặc trưng trung gian dùng cho MLP màu |

Sơ đồ:

```
enc(x;θ)  32 ──► [FC 32→64] + ReLU ──► 64 ──► [FC 64→16] (tuyến tính) ──► 16
                                                                          │
                                        ┌─────────────────────────────────┤
                                        │                                 │
                        giá trị [0] = log-density              cả 16 giá trị
                                        │                      đi tiếp sang MLP màu
                                        ▼
                              σ = exp( giá trị[0] )
```

#### MLP màu (mạng màu)

| Thuộc tính | Giá trị theo paper |
|---|---|
| Input | **nối (concatenate)** của: (a) **16 giá trị output của MLP density**, và (b) **hướng nhìn chiếu lên 16 hệ số SH đầu tiên** → tổng **32 chiều** |
| Số lớp ẩn | **2** |
| Độ rộng lớp ẩn | **64 neuron** |
| Activation lớp ẩn | **ReLU** |
| Output | **3 số (r, g, b)** |
| Activation lớp cuối | **sigmoid** nếu dữ liệu train là sRGB (dải động thấp); **exponential** nếu là linear HDR (dải động cao) |

Sơ đồ:

```
 [16 output MLP density ‖ 16 hệ số SH của hướng nhìn]  = 32
          │
          ▼
    [FC 32→64] + ReLU ──► [FC 64→64] + ReLU ──► [FC 64→3] ──► sigmoid hoặc exp ──► (r,g,b)
```

#### Cơ sở thực nghiệm cho việc chọn 1 lớp / 2 lớp / 64 neuron (Figure 10)

Paper không chọn tùy ý — họ quét tham số trên scene **Lego** với **31 000 bước train** (Figure 10). Nội dung Figure 10 theo paper:

- Mỗi đường cong trong đồ thị = 1 **độ sâu khác nhau của MLP màu** (`N_layers` = 1, 2, 3 lớp ẩn), còn **MLP density luôn giữ 1 lớp ẩn**.
- Lý do giữ MLP density ở 1 lớp: paper nói rõ *"we **do not observe an improvement** with deeper density MLPs"* — tăng độ sâu của MLP density **không** cải thiện gì.
- Các đường cong quét số neuron của lớp ẩn (dùng chung cho cả 2 MLP) **từ 16 tới 256**.
- Kết luận paper rút ra: *"Informed by this analysis, we choose `N_layers = 2` and `N_neurons = 64`."*
- Paper còn ghi thêm: *"Other scenes behave almost identically"* — nên cấu hình này không phải tối ưu riêng cho Lego.

### 3.2. So sánh trực tiếp với MLP 8 × 256 của NeRF gốc

> **🔄 KHÁC VỚI NeRF GỐC — BẢNG SO SÁNH KIẾN TRÚC MẠNG**
>
> | | NeRF gốc | Instant-NGP |
> |---|---|---|
> | Số mạng | **2 mạng riêng biệt**: coarse + fine, **mỗi mạng là 1 bản sao kiến trúc đầy đủ** | **2 MLP nối tiếp**: density + màu, **là 2 phần của cùng 1 mô hình** (không phải 2 bản sao) |
> | Nhánh density | 8 lớp ẩn × 256 kênh (+ skip connection tại lớp 5) | **1 lớp ẩn × 64 kênh** |
> | Nhánh màu | 1 lớp ẩn 128 kênh (sau khi nối γ(d) 24 chiều) | **2 lớp ẩn × 64 kênh** (sau khi nối 16 hệ số SH) |
> | Skip connection | **Có** — nối lại γ(x) 60 chiều vào output lớp 4 (theo code công bố của nhóm NeRF) | **Không có** — mạng quá nông (1–2 lớp) nên không cần |
> | Input nhánh density | γ(x), 60 chiều | enc(x;θ), **32 chiều** |
> | Input nhánh màu | 256 (đặc trưng) + 24 (γ(d)) = 280 chiều | 16 (output density MLP) + 16 (SH) = **32 chiều** |
> | Output density | 1 số, qua ReLU | **log-density** (lấy exp để ra σ) |
> | Output màu | 3 số qua sigmoid | 3 số qua **sigmoid HOẶC exponential** tùy dải động dữ liệu |
> | **Số tham số MLP** | **≈ 438 k** (theo Figure 2(b) của paper, bản tái cài đặt kiến trúc Mildenhall et al.) | **≈ 10 k** (theo Figure 2(e,f)) |
> | **Tỉ lệ thu nhỏ** | — | **nhỏ hơn khoảng 44 lần** |
>
> **Vì sao có thể thu nhỏ MLP tới 44 lần mà chất lượng không giảm?** Vì "trí nhớ về cảnh" đã được **chuyển ra bảng hash**. Trong NeRF gốc, toàn bộ hình học và màu sắc của cảnh phải **nén vào 438 k trọng số MLP** — mạng phải vừa "nhớ cảnh" vừa "tính toán". Trong Instant-NGP, bảng hash **nhớ cảnh** (0.5 M – 266 M tham số, nhưng tra cứu O(1)), MLP chỉ còn nhiệm vụ **giải nghĩa feature đã tra cứu** thành (density, màu) và **phân giải các collision** — một nhiệm vụ nhẹ hơn hẳn, nên 1–2 lớp là đủ.

### 3.3. Đếm tham số MLP — kiểm chứng con số "10 k" của paper

Dùng công thức số tham số của 1 lớp fully-connected: `số_tham_số = (số_kênh_vào × số_kênh_ra) + số_kênh_ra` (phần sau là bias).

**MLP density:**

| Lớp | Phép toán | Tham số |
|---|---|---|
| Lớp ẩn 1 | 32 → 64 | 32×64 + 64 = 2 112 |
| Lớp output | 64 → 16 | 64×16 + 16 = 1 040 |
| **Tổng** | | **3 152** |

**MLP màu:**

| Lớp | Phép toán | Tham số |
|---|---|---|
| Lớp ẩn 1 | 32 → 64 | 32×64 + 64 = 2 112 |
| Lớp ẩn 2 | 64 → 64 | 64×64 + 64 = 4 160 |
| Lớp output | 64 → 3 | 64×3 + 3 = 195 |
| **Tổng** | | **6 467** |

**TỔNG CỘNG: 3 152 + 6 467 = 9 619 ≈ 10 k tham số.**

> **✅ XÁC NHẬN CHÉO VỚI PAPER.** Figure 2 của paper ghi phần MLP là **"10 k"** cho mọi cấu hình hash encoding (e) và (f), và cũng 10 k cho các cấu hình dense grid (c), (d). Phép đếm độc lập ở trên cho **9 619**, làm tròn đúng **10 k**. Đây là bằng chứng mạnh cho thấy kiến trúc mô tả ở mục 3.1 là **đúng và đầy đủ** — nếu thiếu 1 lớp hay sai độ rộng thì con số sẽ lệch hẳn.

Để đối chiếu quy mô: `438 000 / 9 619 ≈ 45.5` lần. Và nếu so với con số hay được trích cho kiến trúc NeRF gốc chính xác theo code công bố (**≈ 594 k** tham số cho 1 mạng, nhân 2 vì có coarse + fine → **≈ 1.19 M**), thì tỉ lệ còn lớn hơn: **≈ 124 lần**.

⚠️ **Ghi chú về con số 438 k vs 594 k:** 438 k là con số **paper Instant-NGP tự báo cáo** cho bản tái cài đặt của họ (Figure 2(b): "8 hidden layers, each 256 wide"); 594 k là con số tính từ kiến trúc chính xác trong code công bố của nhóm NeRF (có thêm lớp feature 256→256 và skip connection). Khi viết báo cáo, nên dùng **438 k khi so sánh trong khuôn khổ Figure 2** (so sánh công bằng vì cùng 1 cài đặt), và ghi rõ nguồn.

### 3.4. Hai chi tiết tinh tế về đầu ra của mạng

#### (a) Density ở không gian logarit

Paper ghi: giá trị output đầu tiên của MLP density được **coi là log-space density**. Tức để có σ thật, phải lấy hàm e mũ:

```
σ = exp( output₀ )
```

| Lý do (diễn giải của tài liệu này) | Giải thích |
|---|---|
| σ **bắt buộc không âm** | `exp(·)` luôn cho giá trị dương với mọi input thực → **tự động** thỏa ràng buộc σ ≥ 0, không cần hàm chặn như ReLU |
| σ có **dải động rất rộng** | σ của không khí ≈ 0, σ của bề mặt đặc có thể rất lớn. Học trong không gian log biến "tỉ lệ nhân" thành "khoảng cách cộng" → mạng dễ biểu diễn dải rộng hơn |
| Gradient tốt hơn ReLU | ReLU có vùng gradient **bằng đúng 0** (khi input < 0) — neuron rơi vào đó có thể "chết". `exp` có gradient khác 0 ở mọi nơi |

> **🔄 KHÁC VỚI NeRF GỐC.** NeRF gốc cho σ qua **ReLU** (`σ = max(0, ·)`) để đảm bảo không âm. Instant-NGP đổi sang **tham số hóa log + exp**. ⚠️ **Lưu ý:** paper Instant-NGP **chỉ nêu dữ kiện** "giá trị đầu tiên được coi là log-space density" mà **không giải thích lý do**; phần bảng lý do ở trên là **suy luận của tài liệu này**, không phải nội dung paper — cần ghi rõ như vậy nếu trích vào báo cáo.

#### (b) Sigmoid hay Exponential cho màu — tùy dải động của dữ liệu

Paper ghi rõ:

| Loại dữ liệu train | Activation đầu ra màu | Ghi chú |
|---|---|---|
| **Dải động thấp (low dynamic-range, sRGB)** — ảnh JPEG/PNG thông thường | **sigmoid** | Giống NeRF gốc; ép màu vào (0,1) |
| **Dải động cao (high dynamic range, linear HDR)** | **exponential** | Màu có thể vượt 1, không bị cắt ngưỡng |

Paper nêu **ưu tiên của nhóm tác giả**: họ **thích dữ liệu HDR hơn** vì nó *"gần hơn với quá trình truyền sáng vật lý"*, và điều này mang lại **nhiều lợi thế** — như công trình đồng thời **NeRF in the Dark** (Mildenhall et al. 2021) cũng đã chỉ ra.

> **🔄 KHÁC VỚI NeRF GỐC.** NeRF gốc chỉ có **1 lựa chọn: sigmoid**, nên về bản chất **giả định dữ liệu là sRGB dải động thấp**. Instant-NGP mở đường cho **huấn luyện trực tiếp trên dữ liệu HDR** — một khả năng NeRF gốc không có.

### 3.5. Ablation quan trọng: có thực sự cần MLP không? (Figure 11)

Đây là 1 câu hỏi hợp lý: nếu bảng hash đã chứa gần hết thông tin, có thể **bỏ hẳn mạng nơ-ron** và chỉ dùng 1 phép nhân ma trận tuyến tính? Đó chính là triết lý của các công trình **đồng thời** không dùng mạng nơ-ron: **DVGO** (Sun et al. 2021) và **Plenoxels** (Yu et al. 2021a).

Paper làm thí nghiệm đúng điều này (**Figure 11**): thay **toàn bộ mạng nơ-ron bằng đúng 1 phép nhân ma trận tuyến tính duy nhất**, train 1 phút. Kết quả paper báo cáo:

| Quan sát | Kết luận paper ghi |
|---|---|
| Lớp tuyến tính **có** tái tạo được hiệu ứng phụ thuộc góc nhìn (view-dependent) | nhưng **chất lượng giảm đáng kể** |
| MLP **giỏi hơn** ở 2 việc cụ thể | (1) bắt được **hiệu ứng phản chiếu bóng (specular)**; (2) **phân giải các hash collision** trên các bảng hash đa độ phân giải đã nội suy — vốn biểu hiện ra ngoài dưới dạng **nhiễu/artifact tần số cao** |
| Chi phí của MLP | **chỉ đắt hơn lớp tuyến tính 15%** — nhờ kích thước nhỏ và cài đặt hiệu quả |
| Phán quyết | *"well worth the significantly improved quality"* — hoàn toàn đáng giá |

> **💡 Ý NGHĨA LÝ THUYẾT QUAN TRỌNG.** Thí nghiệm này xác nhận mảnh ghép cuối của lập luận về collision ở mục 2.11: **MLP không chỉ là "bộ giải nghĩa feature", nó thực sự đang làm công việc PHÂN GIẢI COLLISION**. Nếu bỏ MLP, collision biến thành nhiễu tần số cao nhìn thấy được. Đây là lý do Instant-NGP **giữ lại mạng nơ-ron** trong khi Plenoxels/DVGO bỏ hẳn — và cũng là điểm phân biệt triết lý giữa 2 nhóm phương pháp cùng ra đời năm 2021–2022.

### 3.6. Khởi tạo tham số (Section 4, *Initialization*)

| Đối tượng | Cách khởi tạo | Lý do paper nêu |
|---|---|---|
| Trọng số MLP (`Φ`) | **Glorot & Bengio (2010)** (còn gọi là Xavier initialization) | để "cung cấp 1 phép định tỉ lệ hợp lý cho các giá trị kích hoạt và gradient của chúng xuyên suốt các lớp mạng" |
| Entry bảng hash (`θ`) | **phân phối đều `U(−10⁻⁴, 10⁻⁴)`** | tạo **một chút ngẫu nhiên** (để phá đối xứng), đồng thời **khuyến khích các dự đoán ban đầu gần 0** |

Paper ghi thêm 1 nhận xét thực nghiệm đáng chú ý: họ **đã thử nhiều phân phối khác, kể cả khởi tạo bằng 0**, và **tất cả chỉ cho tốc độ hội tụ ban đầu hơi tệ hơn một chút**. Kết luận của họ: *"The hash table appears to be **robust to the initialization scheme**."* — bảng hash **không nhạy cảm với cách khởi tạo**. Đây là tin tốt cho ai muốn cài đặt lại.

### 3.7. Volume Rendering — gần như GIỮ NGUYÊN NeRF gốc

Paper nói ngắn gọn (Section 5.4): họ huấn luyện mô hình **theo đúng cách của Mildenhall et al.** — lan truyền ngược qua 1 **ray marcher khả vi (differentiable ray marcher)** điều khiển bởi ảnh RGB 2D từ các camera pose đã biết.

Do đó, **toàn bộ phần toán của volume rendering được giữ nguyên**, xem đầy đủ ở `pipeline_NeRF.md` Giai đoạn 3 mục 3.3:

| Nội dung | Trạng thái |
|---|---|
| Định nghĩa σ là xác suất vi phân tia bị hấp thụ | **Giữ nguyên** |
| Công thức tích phân liên tục `C(r) = ∫ T(t)·σ(r(t))·c(r(t),d_view) dt` | **Giữ nguyên** |
| Transmittance `T(t) = exp(−∫σ ds)` và cách dẫn từ phương trình vi phân | **Giữ nguyên** |
| Công thức rời rạc `Ĉ(r) = Σ T_i·α_i·c_i`, với `α_i = 1−exp(−σ_i δ_i)`, `T_i = exp(−Σ_{j<i} σ_j δ_j)` | **Giữ nguyên** |
| Cơ chế che khuất (occlusion) tự học được | **Giữ nguyên** |

> **🔄 KHÁC VỚI NeRF GỐC — 3 THAY ĐỔI Ở KHÂU RAY MARCHING (không phải ở công thức rendering)**
>
> Công thức tích phân thì giống, nhưng **cách chọn các điểm mẫu `t_i`** thì khác hoàn toàn:
>
> | | NeRF gốc | Instant-NGP |
> |---|---|---|
> | Cách chọn điểm mẫu | **Stratified sampling** (ngẫu nhiên trong N đoạn đều) + **Hierarchical sampling 2 lượt** (coarse 64 điểm → fine thêm 128 điểm) | **Bước đi cố định `Δt`** + **bỏ qua ô trống theo occupancy grid** + **bước đi tăng theo lũy thừa cho cảnh lớn** |
> | Số mạng cần train | **2** (coarse + fine) | **1** (không có coarse/fine) |
> | Số điểm mẫu / tia | **192** (64 + 128), **cố định** | **3.1 đến 25.7** (trung bình, **biến thiên theo tia và theo scene**) — Table 3 |
> | Điều kiện dừng sớm | Không có | **Có** — dừng khi transmittance `< 10⁻⁴` |
>
> Chi tiết đầy đủ về 3 thay đổi này ở **Giai đoạn 4 mục 4.1–4.3** — vì chúng gắn chặt với quy trình training.

### 3.8. Kết quả Giai đoạn 3

Với mỗi điểm mẫu trên tia, ta đã có `(σ, r, g, b)` — giống hệt đầu ra của NeRF gốc về mặt ngữ nghĩa, nhưng tính ra bằng **2 MLP nhỏ 10 k tham số** thay vì **MLP 438 k tham số**. Gộp các điểm mẫu trên 1 tia bằng công thức volume rendering rời rạc (y nguyên NeRF gốc) → ra màu pixel dự đoán.

---

## Giai đoạn 4 — Ray Marching tăng tốc, Occupancy Grid, Loss & Vòng lặp Training

Tương ứng **Section 4 (*Training*, *Performance considerations*)**, **Section 5.4 (*Accelerated ray marching*)**, **Table 2–3**, và **Appendix E (toàn bộ)** của paper.

> **📌 LƯU Ý QUAN TRỌNG VỀ CÁCH ĐỌC PHẦN NÀY.** Những kỹ thuật ở Giai đoạn 4 **không phải là đóng góp khoa học chính** của paper (đóng góp chính là hash encoding ở Giai đoạn 2) — chúng là **kỹ thuật cài đặt tăng tốc**. Nhưng paper rất thẳng thắn về điều này và còn **tự định lượng** phần đóng góp của từng nguồn tăng tốc (xem mục 4.9). Khi viết báo cáo đồ án, cần **tách bạch rõ**: tăng tốc đến từ (a) hash encoding + MLP nhỏ, (b) fully-fused CUDA kernel, (c) ray marching thông minh — đây là 3 nguồn độc lập.

### 4.1. Thay đổi lớn nhất ở giai đoạn này: BỎ HẲN cơ chế coarse/fine của NeRF gốc

Nhắc lại NeRF gốc (`pipeline_NeRF.md` Giai đoạn 4): để tránh lãng phí điểm mẫu vào vùng không khí, NeRF gốc dùng **hierarchical sampling**: train **2 mạng riêng biệt**, mạng coarse lấy 64 điểm đều để "dò đường" → tính trọng số `w_i = T_i·α_i` → dựng PDF → lấy thêm 128 điểm tập trung vào vùng `w` cao → mạng fine chạy trên cả 192 điểm. Hàm loss có **2 số hạng** (ép cả 2 mạng học tốt).

> **🔄 KHÁC VỚI NeRF GỐC — TOÀN BỘ CƠ CHẾ ĐÓ BỊ THAY THẾ.** Instant-NGP **không có mạng coarse, không có mạng fine, không có hierarchical sampling, không có PDF/CDF/inverse transform sampling, và loss chỉ có 1 số hạng**. Thay vào đó, bài toán "đừng lãng phí điểm mẫu vào không khí" được giải bằng 1 **cấu trúc dữ liệu riêng, độc lập với mạng**: **occupancy grid (lưới chiếm chỗ)**.
>
> **Vì sao đổi?** Paper nêu ưu điểm quyết định của occupancy grid so với cách coarse/fine (Appendix E.2, *Related work*): occupancy grid **độc lập với encoding đã học (independent from the learned encoding)**, nhờ đó (a) biểu diễn được **cực kỳ gọn — chỉ 1 bit/ô, dưới dạng trường bit (bitfield)**, (b) **độ phân giải của nó tách rời khỏi độ phân giải của encoding**, và (c) **dùng được cả cho các phương pháp không có encoding học được** — chính nhờ điểm (c) mà paper có thể so sánh công bằng với baseline "Ours: Frequency" ở Table 2.
>
> **Hệ quả:** Instant-NGP chỉ cần **1 lần forward MLP cho mỗi điểm mẫu**, không cần 2 lượt như NeRF gốc; và số điểm mẫu giảm từ **192 cố định** xuống **3.1–25.7 trung bình** (Table 3) — tức **giảm khoảng 7.5 đến 62 lần số lần gọi mạng**. Đây là 1 nguồn tăng tốc riêng, hoàn toàn độc lập với hash encoding.

### 4.2. Ba kỹ thuật ray marching (Appendix E, mở đầu)

Paper liệt kê đúng 3 kỹ thuật, với tuyên bố quan trọng kèm theo: chúng gây **sai số không thể nhận thấy được (imperceivable error)**.

| # | Kỹ thuật | Mục tiêu |
|---|---|---|
| **1** | **Bước đi tăng theo lũy thừa (exponential stepping)** cho cảnh lớn | chi phí tính toán chỉ tăng theo **logarit** của đường kính cảnh |
| **2** | **Bỏ qua không gian trống và vùng bị che khuất** (skipping of empty space and occluded regions) | không gọi MLP ở chỗ vô ích |
| **3** | **Dồn các mẫu vào bộ đệm đặc (compaction of samples into dense buffers)** | để GPU thực thi hiệu quả, không có luồng "rỗi" |

Mục tiêu chung paper phát biểu: đặt các điểm mẫu sao cho chúng **đóng góp tương đối đồng đều vào ảnh**, giảm thiểu tính toán bị bỏ phí.

### 4.3. Kỹ thuật 1 — Kích thước bước đi và điều kiện dừng (Appendix E.1)

#### Với cảnh NeRF tổng hợp (bị giới hạn vào khối đơn vị)

Paper dùng **bước đi cố định**:

```
Δt := √3 / 1024
```

| Ký hiệu | Ý nghĩa |
|---|---|
| **Δt** | khoảng cách giữa 2 điểm mẫu liên tiếp dọc tia, đo theo cùng đơn vị với tọa độ cảnh |
| **√3** | **độ dài đường chéo của khối lập phương đơn vị** (vì `√(1²+1²+1²) = √3 ≈ 1.732`) — paper ghi rõ ý nghĩa này |
| **1024** | số bước tối đa để đi hết đường chéo dài nhất có thể của cảnh |

**Kiểm chứng số:** `Δt = 1.7320508/1024 ≈ 0.0016915`. Số bước để đi hết đường chéo: `√3 / Δt = 1024` — đúng như thiết kế.

> **🔄 KHÁC VỚI NeRF GỐC.** NeRF gốc dùng **stratified sampling có yếu tố ngẫu nhiên**: `t_i = t_n + (i + ε_i)/N · (t_f − t_n)` với `ε_i ~ Uniform(0,1)` — mỗi lần train/render lại cho 1 tập điểm mẫu **khác nhau**, và `pipeline_NeRF.md` giải thích đây chính là cơ chế giúp NeRF biểu diễn hàm **liên tục** thay vì bị giới hạn ở N vị trí rời rạc. Instant-NGP dùng **lưới bước đi tất định (deterministic)** `Δt` cố định. Điều này **về nguyên tắc** là 1 bước lùi về mặt lý thuyết, nhưng trong thực tế không gây vấn đề vì (a) `Δt` cực nhỏ (1024 bước cho cả cảnh) nên lưới đã rất dày, và (b) tính liên tục của mô hình đã được đảm bảo bởi **phép nội suy d-tuyến tính trong encoding** (Giai đoạn 2 mục 2.8), chứ không còn phụ thuộc vào tính ngẫu nhiên của việc lấy mẫu. ⚠️ Nhận xét (b) này là **suy luận của tài liệu này**, paper không phát biểu tường minh như vậy.

#### Với mọi cảnh khác (cảnh thật, lớn) — bước đi tăng theo lũy thừa

```
Δt := t / 256 ,  bị kẹp (clamp) vào khoảng  [ √3/1024 ,  s · √3/1024 ]
```

| Ký hiệu | Ý nghĩa |
|---|---|
| **t** | khoảng cách hiện tại dọc tia (tham số t trong `r(t) = o + t·d_view`) |
| **s** | kích thước của **trục lớn nhất** của hộp bao (bounding box) của cảnh |
| **clamp vào [a,b]** | nếu giá trị nhỏ hơn a thì lấy a; lớn hơn b thì lấy b; nằm giữa thì giữ nguyên |

**Vì sao `Δt` tỉ lệ với `t`?** Paper nói dựa trên **định lý chắn (intercept theorem)**, và đưa chú thích chân trang giải thích ngay: *"Dáng vẻ của các vật thể giữ nguyên miễn là kích thước của chúng và khoảng cách tới người quan sát vẫn tỉ lệ với nhau."*

Diễn giải đầy đủ ý này: 1 vật thể ở xa camera gấp đôi thì chiếm **nửa số pixel theo mỗi chiều** trên ảnh. Vậy để mỗi điểm mẫu "chịu trách nhiệm" cho **cùng 1 lượng diện tích pixel**, bước đi cũng phải **dài gấp đôi** khi ở xa gấp đôi. Nếu dùng bước đi cố định như cảnh nhỏ, thì ở vùng xa sẽ **lấy mẫu quá dày một cách vô ích** (nhiều điểm mẫu dồn vào cùng 1 pixel).

**Hệ quả toán học mà paper nêu:** cách chọn bước đi này cho **tăng trưởng theo lũy thừa (exponential growth) theo t**, nghĩa là **chi phí tính toán chỉ tăng theo hàm LOGARIT của đường kính cảnh** — và paper khẳng định **không có mất mát chất lượng cảm nhận được (no perceivable loss of quality)**.

*(Chứng minh ngắn cho "exponential growth": nếu `Δt = t/256` thì `dt/dn = t/256` với n là số bước → `t(n) = t₀·exp(n/256)`. Tức vị trí tăng theo hàm e mũ của số bước, hay ngược lại số bước tăng theo logarit của khoảng cách.)*

#### Điều kiện dừng sớm (early stopping)

Paper ghi: *"we stop ray marching and set the remaining contribution to zero as soon as the **transmittance of the ray drops below a threshold**; in our case `ε = 10⁻⁴`."*

Diễn giải: nhắc lại từ `pipeline_NeRF.md` Giai đoạn 3, transmittance `T_i` là xác suất ánh sáng đi được tới điểm `i` mà chưa bị hấp thụ. Khi `T_i < 10⁻⁴`, tia đã bị chặn gần như hoàn toàn (99.99%), nên **mọi điểm phía sau chỉ đóng góp tối đa 0.01% vào màu pixel** → bỏ hết, gán đóng góp còn lại bằng 0.

> **🔄 KHÁC VỚI NeRF GỐC.** NeRF gốc **luôn chạy hết đủ 192 điểm mẫu cho mọi tia**, kể cả khi tia đã đụng vào 1 bề mặt rất đặc ngay từ điểm thứ 10. Instant-NGP **dừng ngay khi hết ý nghĩa** — tiết kiệm trực tiếp cho những tia chạm vào vật thể đặc, vốn là đa số tia hữu ích trong 1 cảnh.

#### Và 1 quyết định thiết kế đi NGƯỢC các công trình khác (rất đáng nêu trong báo cáo)

Paper nêu ở Appendix E.1 (*Related work*): nhiều phương pháp trước đó (NeRF gốc, **Mip-NeRF 360**, DONeRF) **"bóp méo" (warp) miền 3D của cảnh, co không gian về phía gốc tọa độ**, nhằm cải thiện tính chất số học của input encoding. Nhưng việc warp **làm tia bị uốn cong (causes rays to curve)**, và paper báo cáo: *"this leads to a **worse reconstruction** in our implementation."*

Thay vào đó, Instant-NGP **chỉ ánh xạ tuyến tính** input vào khối đơn vị và **dựa vào chính tính tăng trưởng đa độ phân giải theo lũy thừa của hash encoding** để đạt `N_max` tỉ lệ với kích thước cảnh — bằng 1 trong 2 cách: thay đổi `b` với số mức `L` cố định, hoặc giữ `b` cố định và cho `L` tăng theo **logarit**.

Paper cũng đối chiếu với **LLFF** (Mildenhall et al. 2019), vốn đề xuất lấy mẫu đều trong **không gian thị sai (disparity space)**: paper nhận xét cách đó **"quyết liệt hơn" (more aggressive)** so với bước đi lũy thừa của họ — ưu điểm là cần **số bước không đổi (constant)**, nhược điểm là **có thể mất độ chân thực (loss of fidelity)** so với bước đi lũy thừa, viện dẫn kết quả của DONeRF (Neff et al. 2021).

### 4.4. Kỹ thuật 2 — Occupancy Grid (Appendix E.2) — chi tiết đầy đủ

Đây là phần Giai đoạn 4 quan trọng nhất và cũng là phần **bị bỏ sót hoàn toàn trong bản sơ bộ** của `nerf_cai_tien.md`.

#### Cấu trúc dữ liệu

| Thuộc tính | Giá trị theo paper | Diễn giải |
|---|---|---|
| Số lưới trong **cascade** (xếp tầng) | **K** | `K = 1` cho **mọi** scene NeRF tổng hợp; `K ∈ [1, 5]` cho cảnh thật lớn hơn (tối đa 5 lưới, tùy kích thước cảnh) |
| Độ phân giải mỗi lưới | **128³** | cố định, **không phụ thuộc** vào độ phân giải của hash encoding |
| Miền không gian lưới thứ `k` phủ | **`[−2^(k−1) + 0.5 , 2^(k−1) + 0.5]³`** | mỗi lưới phủ miền **lớn gấp đôi** lưới trước, tất cả **tâm tại `(0.5, 0.5, 0.5)`** (tức tâm khối đơn vị) |
| Dung lượng mỗi ô | **đúng 1 bit** (chiếm chỗ / không chiếm chỗ) | cực gọn |
| Cách xếp các ô trong bộ nhớ | **thứ tự Morton (z-curve)** | để việc duyệt bằng **DDA** có tính liên tục bộ nhớ |

| Ký hiệu | Ý nghĩa |
|---|---|
| **thứ tự Morton / z-curve** | 1 cách "làm phẳng" tọa độ 3D thành 1 chỉ số 1 chiều bằng cách **trộn xen kẽ các bit** của x, y, z. Tính chất quan trọng: **hai ô gần nhau trong không gian 3D thì chỉ số cũng gần nhau** → khi duyệt tia, các ô liên tiếp hay nằm cùng dòng cache. |
| **DDA (digital differential analyzer)** | thuật toán kinh điển để **duyệt các ô lưới mà 1 tia đi qua**, chỉ dùng phép cộng số nguyên (không cần chia/nhân mỗi bước) — cực rẻ |

**Bộ nhớ:** 1 lưới 128³ ô × 1 bit = `2 097 152` bit = **256 KB**. Với `K = 5` lưới thì tổng chỉ **1.25 MB** — **không đáng kể** so với 12–266 MB của bảng hash. Đây chính là ưu điểm "biểu diễn gọn dưới dạng bitfield" mà paper nhấn mạnh.

#### Cách dùng khi ray marching

Paper mô tả 2 quy tắc:

1. **Quy tắc bỏ qua:** mỗi khi 1 điểm mẫu *sắp được đặt* theo kích thước bước `Δt` (mục 4.3), **nếu bit của ô lưới chứa nó bằng 0 (low) thì BỎ QUA điểm mẫu đó** — không gọi MLP.
2. **Quy tắc chọn lưới nào trong K lưới:** phụ thuộc **cả vị trí `x` lẫn kích thước bước `Δt`**. Cụ thể: trong số các lưới **phủ được `x`**, chọn lưới **mịn nhất mà có độ dài cạnh ô lớn hơn `Δt`**.

Diễn giải quy tắc 2: nó khớp **độ phân giải của việc bỏ qua** với **độ phân giải của việc lấy mẫu**. Nếu bước đi `Δt` đang rất dài (ở vùng xa), thì dùng 1 lưới thô là đủ — dùng lưới mịn hơn `Δt` sẽ vô nghĩa (ta nhảy qua nhiều ô mỗi bước). Ngược lại ở vùng gần (Δt nhỏ), dùng được lưới mịn để bỏ qua chính xác hơn.

#### Cách CẬP NHẬT occupancy grid trong lúc train

Đây là phần tinh tế nhất. Paper mô tả 1 quy trình rất cụ thể:

**Cấu trúc phụ:** ngoài tập lưới bit, họ **duy trì 1 tập lưới thứ hai cùng layout**, nhưng mỗi ô lưu **giá trị density số thực độ chính xác đầy đủ (full-precision floating point)** thay vì 1 bit.

**Chu kỳ cập nhật: cứ sau mỗi 16 vòng lặp train**, thực hiện 3 bước:

| Bước | Hành động | Con số cụ thể trong paper |
|---|---|---|
| **1** | **Suy giảm (decay)** giá trị density trong mỗi ô | nhân với hệ số **0.95** |
| **2** | **Lấy mẫu ngẫu nhiên `M` ô ứng viên**, đặt giá trị mới của chúng = **max(giá trị hiện tại, density của mô hình NeRF tại 1 vị trí ngẫu nhiên trong ô đó)** | xem bảng chiến lược lấy mẫu bên dưới |
| **3** | **Cập nhật các bit chiếm chỗ** bằng cách so density mỗi ô với ngưỡng | ngưỡng `t = 0.01 · 1024 / √3` |

**Vì sao mỗi bước lại như vậy — diễn giải:**

- **Bước 1 (decay 0.95):** đảm bảo thông tin cũ **"phai dần"**. Nếu không có bước này, 1 ô từng được đánh dấu chiếm chỗ do mô hình dự đoán sai ở giai đoạn đầu train sẽ **mắc kẹt mãi** ở trạng thái chiếm chỗ, làm mất hiệu quả bỏ qua. Hệ số 0.95 nghĩa là sau khoảng 14 lần cập nhật (`0.95^14 ≈ 0.49`) giá trị giảm nửa.
- **Bước 2 (lấy max, không phải lấy giá trị mới):** phép `max` làm occupancy grid **thiên về phía an toàn (conservative)**. Nếu 1 ô **từng** được quan sát là có density cao, nó **không bị xóa ngay** chỉ vì 1 lần lấy mẫu rơi vào góc trống của ô. Sai sót "đánh dấu chiếm chỗ nhầm" chỉ làm chậm (phải tính thêm điểm mẫu vô ích); còn sai sót "bỏ sót vùng thật có vật thể" sẽ **làm hỏng ảnh** — nên phải nghiêng về phía an toàn.
- **Bước 3 (ngưỡng):** paper giải thích chính xác ý nghĩa của con số: ngưỡng này **tương ứng với việc đặt ngưỡng cho độ cản sáng (opacity) của 1 bước ray marching nhỏ nhất ở mức `1 − exp(−0.01) ≈ 0.01`**.

> **✅ KIỂM CHỨNG SỐ CHO NGƯỠNG — rất đáng đưa vào báo cáo vì nó cho thấy con số không hề tùy ý:**
>
> ```
> Ngưỡng density:  t = 0.01 · 1024 / √3 = 10.24 / 1.7320508 ≈ 5.9121
>
> Opacity của 1 bước nhỏ nhất Δt = √3/1024 ≈ 0.0016915 tại density đó:
>     α = 1 − exp(−t · Δt) = 1 − exp(−5.9121 × 0.0016915)
>       = 1 − exp(−0.0100)  ≈  0.00995  ≈  1%
> ```
>
> **Khớp đúng** với phát biểu của paper. Nghĩa là quy tắc thực sự là: *"đánh dấu 1 ô là trống nếu, khi đi qua nó bằng 1 bước ray marching nhỏ nhất, ánh sáng bị chặn **ít hơn 1%**."* Đây là 1 tiêu chí **có ý nghĩa vật lý rõ ràng**, không phải 1 hằng số tinh chỉnh mù.

**Chiến lược lấy mẫu `M` ô ứng viên — thay đổi theo tiến độ train.** Paper nêu rõ lý do: *"occupancy grid does not store reliable information in early iterations"* — ở những vòng lặp đầu, lưới chưa có thông tin đáng tin.

| Giai đoạn train | Số ô lấy mẫu `M` | Cách lấy mẫu |
|---|---|---|
| **256 bước train đầu tiên** | `M = K · 128³` (**toàn bộ** ô) | lấy mẫu **đều, không lặp lại (uniformly without repetition)** — tức quét hết |
| **Các bước sau đó** | `M = K · 128³ / 2` (**một nửa** số ô) | **chia làm 2 phần bằng nhau:**<br>• `M/2` ô đầu: lấy mẫu **đều trên toàn bộ** các ô<br>• `M/2` ô còn lại: dùng **lấy mẫu loại bỏ (rejection sampling)** để **chỉ chọn trong các ô ĐANG được đánh dấu chiếm chỗ** |

**Vì sao chia 2 phần như vậy — diễn giải:** phần lấy mẫu đều toàn bộ đảm bảo **phát hiện được vật thể mới xuất hiện** ở vùng trước đó tưởng là trống (vì mô hình đang học, hình học đang "hiện ra" dần). Phần lấy mẫu tập trung vào ô đang chiếm chỗ đảm bảo **theo dõi kỹ và cập nhật chính xác** các vùng đã biết là quan trọng — nơi cần độ tin cậy cao nhất. Nếu chỉ làm phần 1 thì các vùng bề mặt (chiếm ~2.5% số ô) sẽ rất ít được ghé thăm.

#### So sánh với công trình liên quan (Appendix E.2, *Related work*)

Paper nêu công bằng: ý tưởng **giới hạn việc đánh giá MLP vào các ô có chiếm chỗ đã từng được dùng** trong các công trình trước về encoding học được theo ô: **NSVF** (Liu et al. 2020), **DVGO** (Sun et al. 2021), **Plenoxels** và **PlenOctrees** (Yu et al. 2021a,b).

**Khác biệt của Instant-NGP** (đã nêu ở mục 4.1, nhắc lại vì quan trọng): occupancy grid của họ **độc lập với encoding đã học**, nên gọn hơn (bitfield), độ phân giải tách rời, và dùng được cho cả baseline không có encoding học được.

Paper cũng nhắc hướng giải quyết thay thế: có thể bỏ qua không gian trống bằng **importance sampling phân phối độ sâu** — ví dụ **lấy mẫu lại kết quả của 1 dự đoán thô** (chính là cách của NeRF gốc!) hoặc qua **neural importance sampling** (Müller et al. 2019) như DONeRF làm.

### 4.5. Kỹ thuật 3 — Dồn mẫu vào bộ đệm đặc

Paper chỉ nêu 1 dòng trong danh sách 3 kỹ thuật (*"compaction of samples into dense buffers for efficient execution"*) mà **không mô tả chi tiết** ở bất kỳ đâu trong paper.

> **⚠️ GHI CHÚ KHÔNG CHẮC CHẮN.** Tài liệu này **chỉ có thể diễn giải trực giác**, không có chi tiết từ paper: sau khi occupancy grid loại bỏ phần lớn điểm mẫu, **số điểm mẫu còn lại trên mỗi tia khác nhau rất nhiều** (Table 3: 3.1 đến 25.7). Nếu để GPU xử lý "1 luồng = 1 tia", các luồng sẽ có khối lượng việc rất lệch nhau → nhiều luồng phải chờ (load imbalance). "Compaction" nghĩa là **gom tất cả điểm mẫu còn sống của mọi tia vào 1 mảng liên tục, không có khoảng trống**, rồi cho GPU xử lý "1 luồng = 1 điểm mẫu" — khi đó mọi luồng có đúng 1 đơn vị việc, tải cân bằng hoàn hảo. Đây là kỹ thuật tiêu chuẩn trong lập trình GPU (stream compaction), nhưng **chi tiết cài đặt cụ thể của paper thì không được công bố trong văn bản paper** — chỉ có trong code tại `github.com/nvlabs/instant-ngp`.

### 4.6. Hàm Loss

Paper nêu rất ngắn (Section 4, *Training*): *"When fitting gigapixel images or NeRFs, we use the **L2 loss**."*

```
L = Σ_{r ∈ R}  ‖ Ĉ(r) − C(r) ‖₂²
```

| Ký hiệu | Ý nghĩa |
|---|---|
| **L** | giá trị loss cần tối thiểu hóa |
| **R** | tập các tia trong batch hiện tại |
| **Ĉ(r)** | màu pixel **dự đoán** cho tia r (từ volume rendering, Giai đoạn 3) |
| **C(r)** | màu pixel **thật** (ground truth) từ ảnh train |
| **‖·‖₂²** | bình phương chuẩn Euclid — với vector màu: `(Δr)² + (Δg)² + (Δb)²` |

> **🔄 KHÁC VỚI NeRF GỐC — CHỈ CÒN 1 SỐ HẠNG.** NeRF gốc có loss **2 số hạng**: `L = Σ_r [ ‖Ĉ_c(r) − C(r)‖₂² + ‖Ĉ_f(r) − C(r)‖₂² ]`, buộc cả mạng coarse và mạng fine cùng học tốt (vì mạng coarse chịu trách nhiệm "dẫn đường" cho việc lấy mẫu của mạng fine). Instant-NGP **không có mạng coarse** nên loss chỉ còn **1 số hạng** — đơn giản hơn, và không phải "chia" tín hiệu học cho 2 mạng.

Để tham khảo đầy đủ, đây là loss của cả 4 bài toán trong paper (để thấy encoding là bất biến với bài toán):

| Bài toán | Loss |
|---|---|
| Gigapixel image | **L2** |
| **NeRF** | **L2** |
| SDF | **MAPE** (mean absolute percentage error): `|dự đoán − đích| / (|đích| + 0.01)` |
| Neural radiance caching | L2 **tương đối theo độ sáng (luminance-relative)** |

Paper cũng thêm 1 thành phần chính quy hóa (regularization) rất đáng chú ý:

> *"To prevent divergence after long training periods, we apply a **weak L2 regularization (factor 10⁻⁶) to the neural network weights, but NOT to the hash table entries**."*

**Vì sao chính quy hóa MLP mà không chính quy hóa bảng hash — diễn giải:** chính quy hóa L2 kéo tham số về 0. Với MLP, đây là biện pháp chuẩn chống phân kỳ/quá khớp. Nhưng với bảng hash, các entry **chính là nơi lưu trữ nội dung cảnh** — kéo chúng về 0 sẽ **xóa dần thông tin đã học**, đặc biệt ở các entry thuộc vùng ít được quan sát (gradient thưa, ít được "làm mới"). ⚠️ Lý do này là **suy luận của tài liệu này**; paper chỉ nêu dữ kiện mà không giải thích.

### 4.7. Bảng siêu tham số huấn luyện đầy đủ (Section 4 *Training*, Section 5.4, Table 3)

| Siêu tham số | Giá trị Instant-NGP (cho NeRF) | Giá trị NeRF gốc (đối chiếu) | Nguồn trong paper |
|---|---|---|---|
| Optimizer | **Adam** | Adam | Section 4 *Training* |
| **β₁** | **0.9** | 0.9 | Section 4 |
| **β₂** | **0.99** | **0.999** ← *khác!* | Section 4 |
| **ε** (Adam) | **10⁻¹⁵** | **10⁻⁷** ← *khác 8 bậc!* | Section 4 |
| Learning rate | **10⁻²** (cho NeRF và 2 bài toán khác; `10⁻⁴` riêng cho SDF) | 5×10⁻⁴ → 5×10⁻⁵ | Section 4 |
| Lịch giảm learning rate | nhân **0.33** sau **20 k** bước, rồi **lặp lại mỗi 10 k** bước | giảm theo hàm mũ | Section 5.4 (đoạn cuối, phần bàn về Table 2) |
| Chính quy hóa | **L2 yếu, hệ số 10⁻⁶, CHỈ áp cho trọng số MLP** | không nêu | Section 4 |
| **Batch size** | **2¹⁸ = 262 144** (`256 Ki`) **điểm mẫu** | 4 096 **tia** | Section 4 + Table 3 |
| Số tia / batch | **10 Ki đến 85 Ki** (biến thiên) | 4 096 (cố định) | **Table 3** |
| Số điểm mẫu / tia | **3.1 đến 25.7** (biến thiên) | 192 (= 64 + 128, cố định) | **Table 3** |
| Số bước train | **31 000** (trong các figure) / **~50 000** (sau 5 phút) | 100 000 – 300 000 | Figure 4, 5, 10 / Section 5.4 |
| Thời gian 1 bước train | **~6 ms** (bản hash); ~30 ms (bản frequency) | không nêu | Section 5.4 |
| Thời gian train 1 scene | **5 giây – 5 phút** | **~1–2 ngày** | Table 2 |
| GPU dùng trong paper | **NVIDIA RTX 3090** | NVIDIA V100 | Section 4, 5 |

> **🔄 BA KHÁC BIỆT VỀ SIÊU THAM SỐ ĐÁNG NÓI NHẤT**
>
> **(1) `ε = 10⁻¹⁵` thay vì `10⁻⁷` — và paper GIẢI THÍCH TẠI SAO.** Paper ghi: *"The choice of β₁ and β₂ makes only a small difference, but the **small value of ε = 10⁻¹⁵ can significantly accelerate the convergence of the hash table entries when their gradients are sparse and weak**."*
>
> Diễn giải: trong Adam, bước cập nhật có dạng `Δ ∝ m̂ / (√v̂ + ε)` với `v̂` là trung bình trượt của bình phương gradient. Với 1 entry bảng hash ở vùng ít được quan sát, gradient **thưa và yếu** → `v̂` rất nhỏ → nếu `ε` lớn (10⁻⁷) thì mẫu số bị `ε` chi phối, làm bước cập nhật **bị nén xuống gần 0** → entry đó gần như **không học được gì**. Hạ `ε` xuống 10⁻¹⁵ giải phóng ràng buộc này. **Đây là 1 siêu tham số được chọn ĐẶC THÙ cho cấu trúc bảng hash** — không phải chọn tùy ý, và không áp dụng được cho NeRF gốc (vốn không có tham số thưa).
>
> **(2) Learning rate lớn hơn 20 lần (10⁻² so với 5×10⁻⁴).** Paper không giải thích lý do. ⚠️ Suy luận của tài liệu này: mạng nhỏ hơn + encoding học được giúp mặt loss "dễ đi" hơn, cho phép bước lớn hơn — nhưng **đây không phải nội dung paper**.
>
> **(3) Batch size được định nghĩa theo ĐIỂM MẪU, không theo TIA.** Đây là 1 khác biệt về **khái niệm**, không chỉ về con số — xem mục 4.8.

### 4.8. Batch theo điểm mẫu chứ không theo tia (Appendix E.3) — 1 phát hiện thực nghiệm đáng chú ý

Paper dành riêng Appendix E.3 cho vấn đề này, và nêu 1 phát hiện cụ thể:

> *"We found that training from a **larger number of rays**, i.e. incorporating **more viewpoint variation** into the batch, converged to **lower error in fewer steps**."*

Vì trong cài đặt của họ, **số điểm mẫu mỗi tia là biến thiên** (do occupancy grid loại bỏ ngẫu nhiên nhiều điểm), họ đưa ra quyết định thiết kế:

> **Nhồi càng nhiều tia càng tốt vào 1 batch có KÍCH THƯỚC CỐ ĐỊNH (tính theo số điểm mẫu)**, thay vì dựng batch có kích thước biến thiên từ 1 số tia cố định.

**Trích Table 3 của paper (đầy đủ):**

| Phương pháp | Batch size | = Số điểm mẫu/tia | × Số tia/batch |
|---|---|---|---|
| **Ours: Hash** (Instant-NGP đầy đủ) | **256 Ki** | **3.1 → 25.7** | **10 Ki → 85 Ki** |
| **Ours: Freq.** (baseline frequency encoding của chính họ) | 256 Ki | 2.5 → 9 | 29 Ki → 105 Ki |
| **mip-NeRF** | 1 Mi | 128 coarse + 128 fine | 4 Ki |

(`Ki = 1024`, `Mi = 1 048 576`. Các khoảng giá trị là **min–max trên các scene tổng hợp** của Table 2.)

**Ba điều đọc ra từ Table 3:**

1. **Batch size của Instant-NGP nhỏ hơn mip-NeRF 4 lần** (256 Ki so với 1 Mi). Paper giải thích nguyên nhân khả dĩ: *"likely due to the larger number of samples each of their rays requires"*. Nhưng paper cũng **rất cẩn trọng**, ghi thêm: *"due to the myriad other differences across implementations, a more detailed study must be carried out to draw a definitive conclusion."*
2. **Số tia/batch của Instant-NGP lớn hơn mip-NeRF 2.5–21 lần** (10–85 Ki so với 4 Ki) → nhiều biến thiên góc nhìn hơn trong 1 bước cập nhật.
3. **Một quan sát ngược trực giác mà paper chỉ ra:** occupancy grid khi dùng với baseline frequency encoding lại **sinh ra ÍT điểm mẫu HƠN** (2.5–9) so với khi dùng với hash encoding (3.1–25.7). Paper giải thích: vì hash encoding **tái tạo chi tiết hơn một chút**; khi chi tiết đó **mịn hơn độ phân giải của occupancy grid (128³)**, thì **không gian trống quanh nó không thể bị tỉa bỏ hiệu quả** và phải đi qua bằng thêm các bước. → **Chất lượng cao hơn phải trả giá bằng thêm điểm mẫu** — một đánh đổi tinh tế.

### 4.9. Cài đặt: fully-fused CUDA kernel — và paper TỰ TÁCH BẠCH nguồn tăng tốc

Paper rất minh bạch về việc tốc độ đến từ đâu, đây là điểm cần làm rõ trong báo cáo đồ án vì **rất dễ gán sai công trạng**.

#### Cài đặt

| Hạng mục | Chi tiết theo paper |
|---|---|
| Ngôn ngữ/nền tảng | **CUDA**, tích hợp với **fully-fused MLP** của framework **tiny-cuda-nn** (Müller 2021) |
| Mã nguồn công bố | hash encoding: cập nhật vào tiny-cuda-nn; phần neural graphics primitives: `github.com/nvlabs/instant-ngp` |
| Có binding PyTorch? | **Có** — paper công bố PyTorch bindings cho cả hash encoding và fully-fused MLP, *"to permit their use in existing projects with little overhead"* |

| Ký hiệu | Ý nghĩa |
|---|---|
| **fully-fused kernel** | toàn bộ các lớp của MLP được **hợp nhất (fuse) vào 1 hàm GPU (kernel) duy nhất**, sao cho các giá trị trung gian giữa các lớp **nằm luôn trong thanh ghi / bộ nhớ chia sẻ (shared memory) trên chip**, **không phải ghi ra rồi đọc lại từ bộ nhớ toàn cục (global memory)**. Chỉ khả thi khi mạng đủ nhỏ để các giá trị trung gian vừa chỗ trên chip — đúng là trường hợp MLP 64 neuron của Instant-NGP. |

> **📌 ĐÂY LÀ MỐI QUAN HỆ NHÂN QUẢ QUAN TRỌNG CẦN HIỂU.** Fully-fused kernel **chỉ chạy được vì MLP nhỏ**; và MLP nhỏ được **chỉ vì có hash encoding học được**. Tức 2 nguồn tăng tốc này **không hoàn toàn độc lập** — hash encoding là điều kiện cho phép (enabler) của kỹ thuật fully-fused. Đây là lý do paper nhiều lần nhấn mạnh rằng "encoding + cài đặt hiệu quả" là 1 gói.

#### Paper tự định lượng từng nguồn tăng tốc

Đây là phần đáng tin nhất và nên trích nguyên vào báo cáo:

| Nguồn tăng tốc | Mức tăng tốc paper báo cáo | Vị trí trong paper |
|---|---|---|
| **Cài đặt CUDA fully-fused** so với 1 cài đặt Python "ngây thơ" (naïve) | **~10×** | Section 4, chú thích chân trang 1 |
| **Hash encoding + MLP nhỏ** (đã loại trừ phần đóng góp của cài đặt) | **20–60×** | Section 5.4, phân tích Table 2 |
| **Tổng thể so với NeRF gốc / mip-NeRF / NSVF** | *"several orders of magnitude"* (vài bậc độ lớn) | Abstract, Section 7 |

**Cách paper tách bạch con số 20–60× — phương pháp luận rất chặt, đáng học:** họ dựng 1 **phiên bản gần như y hệt (nearly identical)** cài đặt của chính mình, chỉ **thay hash encoding bằng frequency encoding** và **mở rộng MLP cho khớp kiến trúc Mildenhall et al.** Gọi đó là **"Ours: Frequency"** (chi tiết kiến trúc ở Appendix D). Vì cả 2 phiên bản dùng **cùng 1 cài đặt CUDA, cùng occupancy grid, cùng ray marching**, nên chênh lệch giữa chúng **chỉ còn do encoding + kích thước MLP**. Kết quả: bản frequency cần **~5 phút** để tiệm cận chất lượng NeRF, còn bản hash đạt mức tương đương chỉ sau **5–15 giây** → **20–60×**.

**Kiến trúc baseline "Ours: Frequency" cho NeRF (trích nguyên bảng ở Appendix D):**

| Thành phần | Số lớp ẩn | Số neuron | Số bậc tần số | Learning rate |
|---|---|---|---|---|
| **NeRF**: MLP density / MLP màu | **7 / 1** | **256 / 256** | **16 / 4** | **10⁻³** |

(Để đối chiếu: SDF baseline = 8 lớp, 128 neuron, 10 tần số, lr 3×10⁻⁴; NRC baseline = 3 lớp, 64 neuron, 10 tần số, lr 10⁻².)

Paper cũng rất thẳng thắn về giới hạn của phép so sánh này (Appendix D): dù các cấu hình baseline có **ít tham số hơn và chậm hơn** cấu hình hash, chúng vẫn **đại diện cho những đánh đổi hiệu năng–chất lượng có lợi**. Lý do: so sánh **ở cùng số tham số** sẽ làm MLP thuần **quá đắt** (vì MLP co giãn theo `O(n²)` trong khi encoding học được co giãn **dưới-tuyến tính**); còn so sánh **ở cùng thông lượng (throughput)** sẽ buộc MLP phải **nhỏ đến mức phi lý**, làm bán rẻ (undersell) khả năng thực của MLP thuần. Họ cũng nói đã thử **Fourier features** (Tancik et al. 2020) nhưng **không tốt hơn** frequency encoding theo trục.

#### Và paper tự nêu điểm còn thiếu trong phân tích của chính mình

Đáng chú ý, paper **tự thừa nhận 1 khoảng trống** (cuối Section 5.4):

> *"While we isolated the performance and convergence impact of our hash encoding and its small MLP, we believe an **additional study is required to quantify the impact of advanced ray marching schemes** (such as ours, coarse-fine [NeRF gốc], or DONeRF) independently from the encoding and network architecture."*

Tức **phần đóng góp riêng của occupancy grid + ray marching thông minh thì CHƯA được định lượng** trong paper. Họ chỉ cung cấp thêm thông tin ở Appendix E.3 (Table 3) để người khác làm phân tích đó.

> **⚠️ LƯU Ý KHI VIẾT BÁO CÁO ĐỒ ÁN.** Vì paper **không** định lượng riêng phần ray marching, **không nên** viết những câu kiểu "occupancy grid đóng góp X lần tăng tốc". Con số **đúng và an toàn** để trích là: **20–60× từ hash encoding + MLP nhỏ** (có bằng chứng thực nghiệm chặt chẽ ở Table 2), **~10× từ cài đặt fully-fused CUDA** (so với Python ngây thơ), và **"vài bậc độ lớn" cho tổng thể**. Con số "~1000 lần" tuy nghe hợp lý khi nhân ra, nhưng **không phải con số paper công bố** — nên nếu dùng, phải ghi rõ là **ước tính của người viết từ việc nhân 2 con số trên**, không phải trích dẫn.

### 4.10. Hai mẹo Adam rất cụ thể

Paper nêu thêm 1 tối ưu nhỏ nhưng thú vị (Section 4, *Training*):

> *"Lastly, we **skip Adam steps for hash table entries whose gradient is exactly 0**. This saves ∼10% performance when gradients are sparse, which is a common occurrence with `T ≫ BatchSize`. Even though **this heuristic violates some of the assumptions behind Adam**, we observe **no degradation in convergence**."*

| Chi tiết | Nội dung |
|---|---|
| Mẹo | **Bỏ qua bước cập nhật Adam** cho các entry bảng hash có gradient **đúng bằng 0** |
| Lợi ích | tiết kiệm **~10% hiệu năng** |
| Khi nào hiệu quả | khi gradient thưa — xảy ra phổ biến khi `T ≫ kích thước batch` |
| Nhược điểm được thừa nhận | **vi phạm 1 số giả định đằng sau Adam** (vì Adam có các bước trung bình trượt và hiệu chỉnh độ chệch theo thời gian — bỏ bước làm "đồng hồ" của các entry lệch nhau) |
| Kết quả thực nghiệm | **không thấy suy giảm độ hội tụ** |

Đây là ví dụ tốt về việc paper **không che giấu** những chỗ "làm tắt" mà chỉ có lý lẽ thực nghiệm chứ không có lý lẽ lý thuyết.

### 4.11. Toàn bộ 1 vòng lặp train — tóm tắt tuần tự

```
Lặp lại ~31 000 – 50 000 lần (tổng 5 giây – 5 phút trên RTX 3090):

 1. CHỌN TIA: nhồi tối đa số tia vào 1 batch cố định 2¹⁸ = 262 144 ĐIỂM MẪU
    (→ ra 10 Ki đến 85 Ki tia, tùy scene). Các tia đến từ nhiều ảnh khác nhau.
    ⟡ NeRF gốc: 4 096 tia cố định, mỗi tia luôn 192 điểm mẫu.

 2. RAY MARCHING CÓ OCCUPANCY GRID: với mỗi tia, đi từng bước Δt = √3/1024
    (hoặc Δt = t/256 có clamp, nếu cảnh lớn):
      - tra occupancy grid (chọn lưới mịn nhất có cạnh ô > Δt, trong các lưới phủ x)
      - nếu bit = 0 → BỎ QUA, không gọi mạng
      - nếu transmittance tích lũy < 10⁻⁴ → DỪNG tia này luôn
    ⟡ NeRF gốc: stratified sampling 64 điểm + hierarchical sampling thêm 128 điểm,
      KHÔNG bỏ qua gì, KHÔNG dừng sớm.

 3. DỒN MẪU: gom mọi điểm mẫu còn sống của mọi tia vào 1 bộ đệm đặc (compaction)
    → GPU xử lý 1 luồng / 1 điểm mẫu, tải cân bằng.
    ⟡ NeRF gốc: không có bước này.

 4. ENCODING: với mỗi điểm mẫu x, chạy multiresolution hash encoding
    (16 mức × tra 8 đỉnh × nội suy tam tuyến tính → nối) → 32 chiều.
    Thực hiện THEO TỪNG MỨC cho toàn bộ batch, để tối ưu cache.
    ⟡ NeRF gốc: tính sin/cos → γ(x) 60 chiều, không tra bảng.

 5. FORWARD: 32 chiều → MLP density (1 lớp ẩn × 64) → 16 giá trị
             → σ = exp(giá trị[0])
             16 giá trị ‖ 16 hệ số SH của hướng nhìn → MLP màu (2 lớp ẩn × 64)
             → (r,g,b) qua sigmoid (sRGB) hoặc exp (HDR)
    ⟡ NeRF gốc: γ(x) 60 → MLP 8 lớp × 256 (+ skip) → σ qua ReLU, và
      256 ‖ γ(d) 24 → 128 → (r,g,b) qua sigmoid. CHẠY 2 LẦN (coarse rồi fine).

 6. VOLUME RENDERING: Ĉ(r) = Σ T_i·α_i·c_i  (y nguyên công thức NeRF gốc)

 7. LOSS: L = Σ_r ‖Ĉ(r) − C(r)‖₂²   (1 số hạng)
    ⟡ NeRF gốc: 2 số hạng (coarse + fine).

 8. BACKPROP: gradient chảy qua MLP → qua phép nối → qua phép nội suy
    → CỘNG DỒN vào 128 feature vector đã tra cứu (8 đỉnh × 16 mức).
    Cập nhật bằng Adam (β₁=0.9, β₂=0.99, ε=10⁻¹⁵, lr=10⁻²);
    BỎ QUA bước Adam cho entry có gradient đúng bằng 0;
    áp L2 yếu 10⁻⁶ CHỈ cho trọng số MLP, KHÔNG cho bảng hash.
    ⟡ NeRF gốc: Adam β₂=0.999, ε=10⁻⁷, lr 5×10⁻⁴, cập nhật TOÀN BỘ 2 mạng.

 9. CỨ SAU MỖI 16 VÒNG LẶP: cập nhật occupancy grid
    (decay 0.95 → lấy mẫu M ô, lấy max với density mô hình → ngưỡng 0.01·1024/√3)
    ⟡ NeRF gốc: không có bước này.

10. GIẢM LEARNING RATE: nhân 0.33 sau bước 20 k, rồi lặp lại mỗi 10 k bước.
```

---

## Giai đoạn 5 — Inference, Sơ đồ tổng thể & Bảng tra cứu paper

### 5.1. Quy trình Inference

Sau khi train xong, ta có **2 tập tham số đã đóng băng**:

| Ký hiệu | Nội dung | Kích thước điển hình |
|---|---|---|
| **Φ** | trọng số của MLP density + MLP màu | ~10 k tham số |
| **θ** | toàn bộ feature vector trong 16 bảng hash | 0.5 M – 266 M tham số (half precision) |

> **🔄 KHÁC VỚI NeRF GỐC.** NeRF gốc chỉ có **1 tập tham số Θ** (trọng số của 2 mạng coarse + fine, ~1.19 M). Instant-NGP có **2 tập tham số bản chất khác nhau**: trọng số mạng (**Φ**) và **bảng tra cứu đã học (θ)**. Khi lưu mô hình ra file, phần lớn dung lượng là θ, không phải Φ — đảo ngược hoàn toàn so với NeRF gốc.

Ngoài ra, cần giữ thêm **occupancy grid** (tập K lưới bit 128³, ~256 KB mỗi lưới) để tăng tốc việc render.

#### Các bước render 1 ảnh ở góc nhìn mới

```
Bước 1 — Chọn camera pose mới (R, C): y nguyên như NeRF gốc
         (nội suy giữa các pose train, hoặc 1 pose hoàn toàn mới).

Bước 2 — Với mỗi pixel (u,v):
   (a) Tính hướng tia d_view từ (u,v) và (R,C,K)  — y nguyên công thức NeRF gốc
   (b) Dựng tia r(t) = o + t·d_view               — y nguyên NeRF gốc
   (c) Ray marching có occupancy grid:
         đi từng bước Δt, bỏ qua ô trống, dừng khi transmittance < 10⁻⁴
         ⟡ NeRF gốc: stratified 64 điểm → hierarchical thêm 128 điểm, 2 lượt mạng
   (d) Với mỗi điểm mẫu còn lại: hash encoding (θ cố định) → 32 chiều
   (e) MLP density (Φ cố định) → σ ; MLP màu (Φ cố định, + SH hướng nhìn) → (r,g,b)
   (f) Volume rendering Ĉ(r) = Σ T_i·α_i·c_i → ra 1 màu pixel

Bước 3 — Ghép toàn bộ pixel → ảnh 2D hoàn chỉnh.
```

#### Khác biệt train vs inference (giống NeRF gốc về nguyên tắc)

| | Train | Inference |
|---|---|---|
| Φ và θ | đang cập nhật mỗi vòng lặp | **cố định** |
| Ground truth C(r) | có | **không có** |
| Loss, backprop | có | **không có** |
| Occupancy grid | **được cập nhật mỗi 16 vòng lặp** | cố định, chỉ dùng để đọc |

### 5.2. Tốc độ render đạt được — con số cụ thể từ paper

| Chỉ số | Giá trị paper báo cáo | Vị trí |
|---|---|---|
| Thời gian render 1 ảnh | **hàng chục mili-giây** ở độ phân giải **1920×1080** | Abstract |
| Khung hình/giây ở độ phân giải HD | **60 FPS** | Section 5.4 |
| Render 1 ảnh 1080p với 128 mẫu/pixel (để tạo hiệu ứng xóa nhòe nền - defocus) | **5 giây** | Figure 12 (trái) |
| Phiên tương tác trên cảnh thật 360° lớn | **10 FPS** | Figure 12 (phải) |
| Render 1 ảnh 1024×1024 của mô hình mây (cloud) | **32 ms** với 2 mẫu/pixel | Figure 13 |

> **🔄 KHÁC VỚI NeRF GỐC — VÀ MỘT HỆ QUẢ RẤT ĐẸP.** NeRF gốc mất **nhiều giây tới vài phút** để render 1 ảnh. Instant-NGP đạt 60 FPS ở độ phân giải HD. Paper chỉ ra 1 hệ quả quan trọng của việc này: *"This high performance makes it **tractable to add effects such as anti-aliasing, motion blur and depth of field by brute-force tracing of multiple rays per pixel**"* (Figure 12).
>
> Nghĩa là: thay vì phải **phát minh ra kỹ thuật thông minh** để chống răng cưa (như Mip-NeRF làm với conical frustum và Integrated Positional Encoding — xem `nerf_cai_tien.md`), Instant-NGP có thể **chỉ cần bắn nhiều tia hơn cho mỗi pixel bằng vũ lực (brute force)** và lấy trung bình — vì mỗi tia đã quá rẻ. Đây là ví dụ kinh điển của "tối ưu tốc độ đủ nhiều thì các vấn đề khác tự giải quyết được bằng cách đơn giản".
>
> Paper cũng nhấn mạnh 1 điểm nữa: đạt được tốc độ này **"without the need of caching of the MLP outputs"** — tức **không cần** đến các kỹ thuật tiền tính toán/đệm kết quả mạng mà các phương pháp render nhanh khác phải dùng (FastNeRF của Garbin et al. 2021, NeX của Wizadwongsa et al. 2021, PlenOctrees của Yu et al. 2021b). Mô hình được **đánh giá trực tiếp (live)** ở mỗi khung hình.

### 5.3. Sơ đồ tổng thể toàn bộ Pipeline Instant-NGP

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  GIAI ĐOẠN 1 — Chuẩn bị dữ liệu & COLMAP/SfM     (GIỐNG HỆT NeRF GỐC)        │
│  Thư mục ảnh thô ──► SIFT + RANSAC + Triangulation + Bundle Adjustment        │
│  ──► pose (R,C,K) cho mỗi ảnh                                                │
│  ──► ÁNH XẠ TUYẾN TÍNH cảnh vào khối đơn vị [0,1]³   ◄── chi tiết thêm của NGP│
│      (KHÔNG warp/bẻ cong không gian — paper nói warp làm chất lượng kém đi)   │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                 │
                                 ▼
  ╔════════════════════════════════════════════════════════════════════════════╗
  ║  VÒNG LẶP TRAIN — lặp ~31 000–50 000 LẦN  (TỔNG: 5 GIÂY – 5 PHÚT)          ║
  ║  (NeRF gốc: 100 000–300 000 lần, tổng 1–2 NGÀY)                            ║
  ║  Mỗi lần: batch CỐ ĐỊNH 2¹⁸ = 262 144 ĐIỂM MẪU (từ 10 Ki–85 Ki tia)        ║
  ║  (NeRF gốc: 4 096 TIA × 192 điểm mẫu mỗi tia)                              ║
  ║                                                                             ║
  ║  ┌───────────────────────────────────────────────────────────────────┐     ║
  ║  │ GIAI ĐOẠN 4a — RAY MARCHING CÓ OCCUPANCY GRID                      │     ║
  ║  │ pixel(u,v) ──► d_view ──► r(t) = o + t·d_view                      │     ║
  ║  │ ──► đi từng bước Δt = √3/1024 (hoặc t/256 có clamp, cảnh lớn)       │     ║
  ║  │ ──► TRA occupancy grid (K lưới 128³, 1 bit/ô, Morton order, DDA)    │     ║
  ║  │     • bit = 0  ──► BỎ QUA điểm mẫu, KHÔNG gọi mạng                 │     ║
  ║  │     • transmittance < 10⁻⁴ ──► DỪNG tia                            │     ║
  ║  │ ──► DỒN MẪU vào bộ đệm đặc (compaction)                            │     ║
  ║  │ ⟡ THAY THẾ HOÀN TOÀN hierarchical sampling coarse/fine của NeRF gốc│     ║
  ║  │   Số điểm mẫu/tia: 3.1–25.7  (NeRF gốc: 192 cố định)               │     ║
  ║  └────────────────────────────┬──────────────────────────────────────┘     ║
  ║                               ▼                                            ║
  ║  ┌───────────────────────────────────────────────────────────────────┐     ║
  ║  │ GIAI ĐOẠN 2 — MULTIRESOLUTION HASH ENCODING  ★ TRỌNG TÂM ★         │     ║
  ║  │                                                                     │     ║
  ║  │  với MỖI điểm mẫu x, LẶP ĐỘC LẬP cho l = 0 … 15 (L = 16 mức):       │     ║
  ║  │                                                                     │     ║
  ║  │   N_l = ⌊16 · b^l⌋ ,  b = exp((ln N_max − ln 16)/15) ≈ 1.38         │     ║
  ║  │   (N_0=16, N_1=22, N_2=30, … N_15=2048)                            │     ║
  ║  │                                                                     │     ║
  ║  │   (1) ⌊x·N_l⌋, ⌈x·N_l⌉  ──► 8 đỉnh nguyên của ô lưới               │     ║
  ║  │   (2) mỗi đỉnh ──► chỉ số entry:                                   │     ║
  ║  │        • nếu (N_l+1)³ ≤ T  ──► ánh xạ 1:1, KHÔNG collision         │     ║
  ║  │        • ngược lại ──► h(x) = (⊕ᵢ xᵢ·πᵢ) mod T                     │     ║
  ║  │          π₁=1 (vì cache), π₂=2654435761, π₃=805459861              │     ║
  ║  │   (3) nội suy TAM TUYẾN TÍNH 8 feature (F=2) theo w = x·N_l−⌊x·N_l⌋ │     ║
  ║  │   (4) NỐI 16 vector × 2 chiều  ──►  y ∈ ℝ³²                        │     ║
  ║  │                                                                     │     ║
  ║  │  ⟡ THAY THẾ γ(x) 60 chiều sin/cos CỐ ĐỊNH của NeRF gốc             │     ║
  ║  │  ⟡ θ (các feature vector) LÀ THAM SỐ HỌC ĐƯỢC — NeRF gốc có 0      │     ║
  ║  └────────────────────────────┬──────────────────────────────────────┘     ║
  ║                               ▼                                            ║
  ║  ┌───────────────────────────────────────────────────────────────────┐     ║
  ║  │ GIAI ĐOẠN 3 — HAI MLP NHỎ (tổng ~10 k tham số) + VOLUME RENDERING   │     ║
  ║  │                                                                     │     ║
  ║  │  y(32) ──► MLP DENSITY: [32→64]+ReLU ──► [64→16] ──► 16 giá trị     │     ║
  ║  │                                   giá trị[0] = log σ ──► σ = exp(·) │     ║
  ║  │                                                                     │     ║
  ║  │  16 giá trị ‖ 16 hệ số SPHERICAL HARMONICS của d_view  = 32         │     ║
  ║  │        ──► MLP MÀU: [32→64]+ReLU ──► [64→64]+ReLU ──► [64→3]        │     ║
  ║  │        ──► sigmoid (sRGB) HOẶC exp (HDR) ──► (r,g,b)                │     ║
  ║  │                                                                     │     ║
  ║  │  ──► VOLUME RENDERING: Ĉ(r) = Σ T_i·α_i·c_i   (Y NGUYÊN NeRF GỐC)   │     ║
  ║  │                                                                     │     ║
  ║  │  ⟡ NeRF gốc: MLP 8 lớp × 256 kênh (~438 k) × 2 MẠNG (coarse+fine)  │     ║
  ║  │  ⟡ NeRF gốc: γ(d) sin/cos 24 chiều, KHÔNG dùng Spherical Harmonics │     ║
  ║  │  ⟡ NeRF gốc: σ qua ReLU, KHÔNG phải exp của log-density            │     ║
  ║  └────────────────────────────┬──────────────────────────────────────┘     ║
  ║                               ▼                                            ║
  ║  ┌───────────────────────────────────────────────────────────────────┐     ║
  ║  │ GIAI ĐOẠN 4b — LOSS + BACKPROP                                      │     ║
  ║  │  L = Σ_r ‖Ĉ(r) − C(r)‖₂²       ◄── CHỈ 1 SỐ HẠNG                   │     ║
  ║  │  (NeRF gốc: 2 số hạng ‖Ĉ_c−C‖² + ‖Ĉ_f−C‖², vì có 2 mạng)          │     ║
  ║  │                                                                     │     ║
  ║  │  gradient chảy ngược: MLP ──► phép nối ──► phép nội suy             │     ║
  ║  │       ──► CỘNG DỒN vào 128 feature vector (8 đỉnh × 16 mức)         │     ║
  ║  │       ◄── CHỈ 128 vector bị sửa, trong hàng triệu vector của θ!     │     ║
  ║  │                                                                     │     ║
  ║  │  Adam: β₁=0.9, β₂=0.99, ε=10⁻¹⁵ (!), lr=10⁻²                       │     ║
  ║  │  + BỎ QUA bước Adam cho entry có gradient = 0 (tiết kiệm ~10%)      │     ║
  ║  │  + L2 yếu 10⁻⁶ CHỈ cho Φ, KHÔNG cho θ                              │     ║
  ║  │  (NeRF gốc: β₂=0.999, ε=10⁻⁷, lr 5×10⁻⁴, cập nhật TOÀN BỘ 2 mạng)  │     ║
  ║  └────────────────────────────┬──────────────────────────────────────┘     ║
  ║                               │                                            ║
  ║     ┌─────────────────────────┴──────────────────────────┐                ║
  ║     │  CỨ SAU MỖI 16 VÒNG LẶP: CẬP NHẬT OCCUPANCY GRID   │                ║
  ║     │  (1) decay × 0.95                                   │                ║
  ║     │  (2) lấy mẫu M ô, giá trị = max(cũ, density mô hình)│                ║
  ║     │      M = K·128³ (256 bước đầu) / K·128³/2 (sau đó)  │                ║
  ║     │  (3) bit = (density > 0.01·1024/√3 ≈ 5.91)          │                ║
  ║     │  ⟡ NeRF gốc KHÔNG có cấu trúc này                   │                ║
  ║     └─────────────────────────┬──────────────────────────┘                ║
  ║                               │                                            ║
  ║                               └──── quay lại batch điểm mẫu MỚI ───────────╣
  ║  Giảm lr × 0.33 sau 20 k bước, rồi lặp lại mỗi 10 k bước                   ║
  ╚═══════════════════════════════╦════════════════════════════════════════════╝
                                   │  (Φ và θ cố định sau 5 giây – 5 phút)
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  GIAI ĐOẠN 5 — INFERENCE                                                     │
│  Φ (~10 k) + θ (0.5 M–266 M, half precision) + occupancy grid  —  CỐ ĐỊNH    │
│  Chọn (R,C) mới ──► mỗi pixel: ray march có occ.grid ──► hash enc            │
│  ──► 2 MLP nhỏ ──► volume rendering ──► ghép pixel ──► ẢNH OUTPUT            │
│  ⟡ 60 FPS ở độ phân giải HD, hàng chục ms ở 1920×1080                        │
│  ⟡ Đủ nhanh để chống răng cưa / motion blur / depth-of-field BẰNG VŨ LỰC     │
│    (bắn nhiều tia mỗi pixel) — không cần kỹ thuật đặc biệt như Mip-NeRF      │
│  ⟡ KHÔNG cần đệm (cache) output của MLP như FastNeRF/NeX/PlenOctrees         │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 5.4. Bảng tra cứu: Giai đoạn trong tài liệu này ↔ Mục trong paper gốc (arXiv:2201.05989)

| Giai đoạn / Mục | Nội dung | Vị trí tương ứng trong paper |
|---|---|---|
| **GĐ 1** | Dữ liệu, camera pose, COLMAP/SfM | **Không có trong paper** (paper chỉ nói "train theo cách của Mildenhall et al. 2020"). Chi tiết SfM phải lấy từ paper NeRF gốc / `pipeline_NeRF.md` |
| GĐ 1.2(a) | Ánh xạ cảnh vào khối đơn vị, không warp | **Appendix E.1** (đoạn *Related work* cuối, và trang 15 đầu) |
| GĐ 1.2(b) | sRGB vs HDR | **Section 5.4** (*Model Architecture*) |
| **GĐ 2.0** | Phê bình frequency encoding | **Section 2** (*Background and Related Work*), Eq. 1 |
| GĐ 2.1 | So sánh các kiểu encoding, vì sao không dùng dense grid | **Section 2** (*Sparse parametric encodings*) + **Figure 2** |
| GĐ 2.2 | Bảng siêu tham số L, T, F, N_min, N_max | **Table 1** + **Section 3** (*Performance vs. quality*) + **Figure 4, 5** |
| GĐ 2.3 | Sơ đồ 5 bước của encoding | **Figure 3** + **Section 3** (3 đoạn đầu) |
| GĐ 2.4 | Công thức N_l và b | **Section 3**, **Eq. 2** và **Eq. 3** |
| GĐ 2.5 | ⌊x_l⌋, ⌈x_l⌉, 2^d đỉnh | **Section 3** (đoạn *"Consider a single level l"*) |
| GĐ 2.6 | Điều kiện (N_l+1)^d ≤ T, ánh xạ 1:1 vs hash | **Section 3** (cùng đoạn trên) |
| GĐ 2.7 | Hàm hash, π₁=1, π₂, π₃ | **Section 3**, **Eq. 4** |
| GĐ 2.7 (cuối) | 3 hàm hash khác đã thử và loại | **Section 6** (*Choice of hash function*) |
| GĐ 2.8 | Nội suy d-tuyến tính, w_l | **Section 3** (đoạn *"Lastly, the feature vectors..."*) + **Section 3** (*d-linear interpolation*) |
| GĐ 2.9 | Smoothstep S₁, dịch mức 1/(2N_l) | **Appendix A**, **Eq. 5** và **Eq. 6** |
| GĐ 2.10 | Nối vs rút gọn | **Section 3** + **Section 6** (*Concatenation vs. reduction*) + **Appendix B** |
| GĐ 2.11 | Hash collision, gradient lấy trung bình | **Section 3** (*Implicit hash collision resolution*) + **Section 2** (cuối) |
| GĐ 2.11 (cuối) | Vi cấu trúc dạng hạt do collision | **Section 5.2** + **Section 6** (*Microstructure due to hash collisions*) + **Figure 1, 7** |
| GĐ 2.12 | Tính thích nghi trực tuyến | **Section 3** (*Online adaptivity*) |
| GĐ 2.13 | Đếm tham số, half precision, vách đá cache | **Section 3** (*Performance vs. quality*) + **Section 4** (*Performance considerations*) + **Figure 4** |
| GĐ 2.14 | Spherical Harmonics cho hướng nhìn | **Section 4** (*Non-spatial input dimensions ξ*) + **Section 5.4** |
| **GĐ 3.1** | Hai MLP: density 1 lớp, màu 2 lớp, 64 neuron | **Section 5.4** (*Model Architecture*) + **Section 4** (*Architecture*) |
| GĐ 3.1 (cuối) | Ablation độ sâu/độ rộng MLP | **Figure 10** |
| GĐ 3.4 | log-space density, sigmoid vs exponential | **Section 5.4** (*Model Architecture*) |
| GĐ 3.5 | Ablation MLP vs lớp tuyến tính | **Figure 11** + **Section 5.4** (*Comparison with direct voxel lookups*) |
| GĐ 3.6 | Khởi tạo Glorot / U(−10⁻⁴,10⁻⁴) | **Section 4** (*Initialization*) |
| GĐ 3.7 | Volume rendering giữ nguyên | **Section 5.4** (câu đầu) — paper chỉ dẫn chiếu, không nhắc lại công thức |
| **GĐ 4.1** | Bỏ coarse/fine | **Section 5.4** (*Accelerated ray marching*) + **Appendix E.2** (*Related work*) |
| GĐ 4.2 | Ba kỹ thuật ray marching | **Appendix E** (mở đầu) |
| GĐ 4.3 | Δt = √3/1024, Δt = t/256, dừng ở ε=10⁻⁴, không warp | **Appendix E.1** |
| GĐ 4.4 | Occupancy grid: cascade K, 128³, Morton/DDA, chu kỳ 16 bước, decay 0.95, ngưỡng 0.01·1024/√3, chiến lược lấy mẫu M | **Appendix E.2** |
| GĐ 4.5 | Dồn mẫu (compaction) | **Appendix E** (chỉ 1 dòng, không có chi tiết) |
| GĐ 4.6 | L2 loss, L2 reg 10⁻⁶ chỉ cho MLP | **Section 4** (*Training*) |
| GĐ 4.7 | Siêu tham số Adam, lr, lịch giảm lr | **Section 4** (*Training*) + **Section 5.4** (đoạn cuối) |
| GĐ 4.8 | Batch theo điểm mẫu, Table số tia/mẫu | **Appendix E.3** + **Table 3** |
| GĐ 4.9 | fully-fused CUDA, tách bạch nguồn tăng tốc, baseline "Ours: Frequency" | **Section 4** (mở đầu + chú thích 1) + **Section 5.4** + **Appendix D** + **Table 2** |
| GĐ 4.10 | Bỏ qua bước Adam khi gradient = 0 | **Section 4** (*Training*, đoạn cuối) |
| **GĐ 5.2** | Tốc độ render, 60 FPS, brute-force AA | **Abstract** + **Section 5.4** + **Figure 12, 13** |
| Kết quả | Bảng PSNR so với NeRF/mip-NeRF/NSVF | **Table 2** |
| Hạn chế | Microstructure, bối cảnh sinh (generative), hướng tương lai | **Section 6** + **Section 7** |

---

## BẢNG TỔNG HỢP — Instant-NGP thay đổi những gì so với NeRF gốc?

*Đây là bảng quan trọng nhất của tài liệu, dùng trực tiếp cho **Chương 2 (Các công trình liên quan)** và **Chương 3 (Phương pháp)** của báo cáo đồ án. Mỗi dòng gồm 5 cột: thành phần / NeRF gốc / Instant-NGP / lý do cải tiến / hệ quả.*

### A. Nhóm thay đổi về INPUT ENCODING (đóng góp khoa học chính)

| Thành phần | NeRF gốc làm gì | Instant-NGP làm gì | Lý do cải tiến | Hệ quả (tốc độ / chất lượng / bộ nhớ) |
|---|---|---|---|---|
| **Mã hóa vị trí x** | `γ(x)` = sin/cos ở `L_f=10` tần số → **60 chiều**, **cố định, 0 tham số học được** | **Multiresolution hash encoding**: 16 mức lưới, mỗi mức 1 bảng ≤ T entry × 2 chiều, nội suy tam tuyến tính, nối lại → **32 chiều**, **có tham số học được** | Đẩy "gánh nặng học" từ MLP sang 1 cấu trúc dữ liệu tra cứu được, để **mỗi mẫu train chỉ sửa rất ít tham số** | **Tốc độ: 20–60× nhanh hơn** (Table 2, đã tách riêng khỏi phần tăng tốc do cài đặt). **Chất lượng: tương đương hoặc hơn.** **Bộ nhớ: tăng mạnh** (0 → 0.5 M–266 M tham số) |
| **Số mức độ phân giải** | Có 10 mức **tần số** (sin/cos) nhưng chúng **không phải lưới**, không lưu dữ liệu | **L = 16 mức độ phân giải không gian thật**, từ `N_min=16` tới `N_max=2048` (với NeRF), theo cấp số nhân `b ≈ 1.38` | Cảnh tự nhiên có tính trơn → phân tách đa tỉ lệ là hợp lý; tăng trưởng hình học cho phép phủ dải rộng với chỉ `O(log(N_max/N_min))` mức | Figure 2 cho thấy đa độ phân giải riêng nó đã giúp **giảm hơn nửa số tham số** so với 1 độ phân giải, ở cùng chất lượng |
| **Cách lưu tham số encoding** | Không có | **Bảng hash kích thước T cố định** cho mỗi mức; mức thô (`(N_l+1)³ ≤ T`) thì ánh xạ **1:1 không collision**, mức mịn thì **hash** | Lưới đặc 2048³ có ~8,6 tỉ đỉnh (~34 GB) — bất khả thi. Và `O(N³)` tham số cho `O(N²)` bề mặt là lãng phí (chỉ 2.57% ô lưới 128³ chạm bề mặt) | Giảm **20×** số tham số so với dense grid ở cùng chất lượng (Figure 2 d vs f) |
| **Xử lý hash collision** | Không áp dụng | **CỐ TÌNH không xử lý** — không probing, không bucketing, không chaining. Dựa vào (a) mức thô không collision, (b) collision rải giả ngẫu nhiên, (c) **gradient lấy trung bình có trọng số thực tế** nên mẫu quan trọng áp đảo, (d) MLP tự học phân biệt | 3 kỹ thuật kinh điển đều cần **rẽ nhánh điều khiển** → **phân kỳ thực thi** trên GPU, rất đắt | **Tốc độ: tra cứu O(1), không rẽ nhánh, 16 mức song song.** **Chất lượng: trả giá bằng "vi cấu trúc dạng hạt"** — rõ ở SDF, nhẹ hơn nhiều ở NeRF (paper thừa nhận) |
| **Cập nhật cấu trúc dữ liệu trong lúc train** | Không áp dụng | **KHÔNG BAO GIỜ** — kích thước T cố định từ đầu đến cuối | Các phương pháp dùng octree/sparse grid (NSVF, DVGO, Plenoxels) phải định kỳ tỉa/chia → quy trình train phức tạp, gây **bước nhảy rời rạc** trong lúc train | **Đơn giản hóa quy trình train**; layout bộ nhớ **biết trước**, tinh chỉnh được cho cache GPU |
| **Độ trơn của encoding** | `C^∞` (sin/cos khả vi vô hạn lần) | **`C⁰`** (chỉ liên tục; đạo hàm gián đoạn tại biên ô lưới). Có thể lên `C¹` bằng smoothstep + dịch mức `1/(2N_l)` nhưng **mặc định TẮT vì làm giảm chất lượng** | Nội suy tuyến tính là lựa chọn rẻ nhất (`2^d`=8 đỉnh, so với `3^d`=27 hoặc `4^d`=64 cho bậc 2, bậc 3) | **Đây là chỗ Instant-NGP KÉM HƠN NeRF gốc.** Gây vấn đề thật ở SDF (pháp tuyến = đạo hàm); ít ảnh hưởng ở NeRF |
| **Số siêu tham số cần tinh chỉnh** | `L_f` cho vị trí + `L_f` cho hướng + kiến trúc MLP | **Chỉ 2: `T` và `N_max`** | Mục tiêu thiết kế có chủ đích: encoding **bất biến với bài toán (task-agnostic)** | Paper dùng **cùng 1 cài đặt + cùng siêu tham số cho cả 4 bài toán khác nhau**, chỉ đổi T |
| **Mã hóa hướng nhìn d_view** | `γ(d)` = sin/cos `L_f=4` → **24 chiều** | **Chiếu lên 16 hệ số đầu của cơ sở Spherical Harmonics** → **16 chiều** | SH là cơ sở **tự nhiên cho hàm trên mặt cầu**; hướng nhìn vốn là 1 điểm trên mặt cầu đơn vị. Áp sin/cos riêng cho từng thành phần x,y,z **không tôn trọng ràng buộc vector đơn vị** | Ít chiều hơn (16 so với 24) → MLP màu nhỏ hơn; biểu diễn phụ thuộc hướng đúng hình học hơn |

### B. Nhóm thay đổi về KIẾN TRÚC MẠNG

| Thành phần | NeRF gốc làm gì | Instant-NGP làm gì | Lý do cải tiến | Hệ quả |
|---|---|---|---|---|
| **Số mạng phải train** | **2 mạng riêng biệt** (coarse + fine), **mỗi mạng là bản sao kiến trúc đầy đủ** | **1 mô hình**, gồm **2 MLP nối tiếp** (density → màu) là 2 phần của cùng mô hình | Bỏ hierarchical sampling → không cần mạng coarse để "dò đường" | Giảm nửa số tham số phải học; loss chỉ còn 1 số hạng |
| **Nhánh density** | **8 lớp ẩn × 256 kênh** + skip connection tại lớp 5 | **1 lớp ẩn × 64 kênh** → 16 output | Bảng hash đã "nhớ cảnh"; MLP chỉ còn **giải nghĩa feature + phân giải collision**. Figure 10: **MLP density sâu hơn KHÔNG cải thiện gì** | Rất nhiều phép nhân ma trận được tiết kiệm cho **mỗi** điểm mẫu |
| **Nhánh màu** | 1 lớp ẩn 128 kênh, input 280 chiều (256 đặc trưng + 24 γ(d)) | **2 lớp ẩn × 64 kênh**, input **32 chiều** (16 + 16 SH) | Figure 10 quét `N_layers ∈ {1,2,3}` và `N_neurons ∈ [16,256]` → chọn (2, 64) | — |
| **Tổng tham số MLP** | **≈ 438 k** (theo Figure 2(b) paper) / ≈ 594 k × 2 mạng theo code NeRF gốc | **≈ 10 k** (xác nhận: 9 619 bằng phép đếm độc lập) | — | **Nhỏ hơn ~44 lần** (hoặc ~124 lần nếu so với cả 2 mạng NeRF gốc). **Đủ nhỏ để dùng fully-fused CUDA kernel** — mọi giá trị trung gian nằm trên chip |
| **Skip connection** | **Có** (nối lại γ(x) 60 chiều vào output lớp 4) | **Không có** | Mạng chỉ 1–2 lớp ẩn → không có vấn đề gradient suy giảm qua độ sâu | Đơn giản hóa cài đặt |
| **Kích hoạt đầu ra density** | **ReLU** (`σ = max(0,·)`) | **log-space density** → `σ = exp(output₀)` | ⚠️ Paper **không giải thích**. Suy luận: `exp` tự đảm bảo σ>0, xử lý dải động rộng tốt hơn, gradient khác 0 ở mọi nơi (ReLU có vùng gradient = 0) | — |
| **Kích hoạt đầu ra màu** | **Chỉ sigmoid** → ngầm giả định dữ liệu sRGB | **sigmoid** (sRGB) **HOẶC exponential** (linear HDR) | Nhóm tác giả **ưu tiên HDR** vì gần hơn với truyền sáng vật lý | **Mở khả năng train trực tiếp trên dữ liệu HDR** — NeRF gốc không có |
| **Có cần mạng nơ-ron không?** | Có (đó là toàn bộ mô hình) | **Có, và paper CHỨNG MINH là cần** — Figure 11: thay MLP bằng 1 lớp tuyến tính làm **chất lượng giảm đáng kể** (mất specular + nhiễu tần số cao do collision), dù MLP chỉ **đắt hơn 15%** | Khác với Plenoxels/DVGO (cùng thời, bỏ hẳn mạng), Instant-NGP cho rằng MLP có vai trò **không thể bỏ**: phân giải collision | Giữ được chất lượng cao mà vẫn nhanh |

### C. Nhóm thay đổi về LẤY MẪU & RAY MARCHING

| Thành phần | NeRF gốc làm gì | Instant-NGP làm gì | Lý do cải tiến | Hệ quả |
|---|---|---|---|---|
| **Chiến lược lấy mẫu dọc tia** | **Stratified sampling** (64 điểm, ngẫu nhiên trong mỗi đoạn) **+ Hierarchical sampling** (tính `w_i=T_iα_i` → PDF → CDF → inverse transform sampling → thêm 128 điểm) | **Bước đi cố định `Δt = √3/1024`** + **bỏ qua ô trống theo occupancy grid** | Occupancy grid **độc lập với encoding đã học** → biểu diễn được cực gọn (1 bit/ô), độ phân giải tách rời, và **dùng được cả cho baseline không có encoding học được** (nhờ đó so sánh công bằng ở Table 2) | **Số điểm mẫu/tia: từ 192 cố định → 3.1–25.7** (Table 3) ⟹ **giảm ~7.5 đến 62 lần số lần gọi mạng**. Chỉ cần **1 lượt forward** thay vì 2 |
| **Cảnh lớn** | Dùng **warp không gian** (co không gian xa về gốc) | **KHÔNG warp** — chỉ ánh xạ tuyến tính vào khối đơn vị, rồi dùng **bước đi tăng theo lũy thừa `Δt = t/256`** (clamp vào `[√3/1024, s·√3/1024]`), dựa trên **định lý chắn** | Paper báo cáo: warp **làm tia uốn cong** → **tái tạo kém hơn** trong cài đặt của họ | **Chi phí chỉ tăng theo LOGARIT của đường kính cảnh**, không mất chất lượng cảm nhận được |
| **Dừng sớm** | **Không có** — luôn chạy đủ 192 điểm mẫu cho mọi tia | **Dừng khi transmittance < 10⁻⁴**, gán đóng góp còn lại = 0 | Khi tia đã bị chặn 99.99% thì mọi thứ phía sau đóng góp ≤ 0.01% | Tiết kiệm lớn cho các tia chạm vật thể đặc (= phần lớn tia hữu ích) |
| **Cấu trúc tăng tốc** | Không có | **Cascade K lưới occupancy 128³, 1 bit/ô** (256 KB/lưới), xếp theo **thứ tự Morton (z-curve)**, duyệt bằng **DDA**. K=1 cho scene tổng hợp, K∈[1,5] cho cảnh thật. Lưới thứ k phủ `[−2^(k−1)+0.5, 2^(k−1)+0.5]³` | Chọn lưới nào: **lưới mịn nhất có cạnh ô > Δt**, trong các lưới phủ x → khớp độ phân giải bỏ qua với độ phân giải lấy mẫu | Bộ nhớ không đáng kể (K=5 → 1.25 MB) so với 12–266 MB của bảng hash |
| **Cập nhật cấu trúc tăng tốc** | Không áp dụng | **Mỗi 16 vòng lặp**: (1) decay × 0.95, (2) lấy mẫu M ô, giá trị = **max**(cũ, density mô hình tại điểm ngẫu nhiên trong ô), (3) đặt bit nếu density > `0.01·1024/√3 ≈ 5.91`. M = toàn bộ ô trong 256 bước đầu; sau đó M = nửa số ô, chia đôi giữa "lấy mẫu đều" và "rejection sampling chỉ trong ô đang chiếm chỗ" | Decay để thông tin sai ở giai đoạn đầu **phai dần**; `max` để **thiên về an toàn** (bỏ sót vật thể làm hỏng ảnh, đánh dấu nhầm chỉ làm chậm); ngưỡng tương ứng **opacity 1% cho 1 bước nhỏ nhất** (ý nghĩa vật lý rõ ràng) | Occupancy grid **tự bắt kịp** hình học đang "hiện ra" dần trong lúc train |
| **Dồn mẫu cho GPU** | Không có | **Compaction vào bộ đệm đặc** — gom mọi điểm mẫu còn sống vào 1 mảng liên tục | ⚠️ Paper **chỉ nêu 1 dòng, không chi tiết**. Suy luận: số điểm mẫu/tia rất lệch (3.1–25.7) → nếu 1 luồng = 1 tia thì tải mất cân bằng; 1 luồng = 1 điểm mẫu thì cân bằng hoàn hảo | Tận dụng hết tính song song của GPU |

### D. Nhóm thay đổi về TRAINING & LOSS

| Thành phần | NeRF gốc làm gì | Instant-NGP làm gì | Lý do cải tiến | Hệ quả |
|---|---|---|---|---|
| **Hàm loss** | `L = Σ_r [‖Ĉ_c−C‖₂² + ‖Ĉ_f−C‖₂²]` — **2 số hạng** | `L = Σ_r ‖Ĉ−C‖₂²` — **1 số hạng** (L2) | Không có mạng coarse nên không phải ép mạng coarse học tốt | Đơn giản hơn; không "chia" tín hiệu học cho 2 mạng |
| **Chính quy hóa** | Không nêu trong paper | **L2 yếu, hệ số 10⁻⁶, CHỈ áp cho trọng số MLP (Φ), KHÔNG áp cho bảng hash (θ)** | Mục đích: *"ngăn phân kỳ sau các giai đoạn train dài"*. ⚠️ Lý do loại trừ θ không được paper nêu. Suy luận: θ **chính là nơi lưu nội dung cảnh**, kéo về 0 sẽ xóa thông tin ở vùng ít quan sát | Train ổn định được lâu |
| **Adam `β₂`** | 0.999 | **0.99** | Paper nói lựa chọn β₁, β₂ *"chỉ tạo khác biệt nhỏ"* | — |
| **Adam `ε`** | 10⁻⁷ | **10⁻¹⁵** (khác 8 bậc độ lớn!) | Paper **giải thích rõ**: giá trị ε nhỏ *"có thể tăng tốc đáng kể sự hội tụ của các entry bảng hash khi gradient của chúng thưa và yếu"*. Với ε lớn, mẫu số `√v̂ + ε` bị ε chi phối → entry ở vùng ít quan sát gần như không học được gì | **Siêu tham số đặc thù cho cấu trúc bảng hash** — không có ý nghĩa với NeRF gốc |
| **Learning rate** | 5×10⁻⁴ → 5×10⁻⁵ (giảm theo hàm mũ) | **10⁻²** (lớn hơn **20 lần**), giảm **× 0.33 sau 20 k bước, lặp lại mỗi 10 k bước** | ⚠️ Paper **không giải thích**. Suy luận: mạng nhỏ + encoding học được làm mặt loss "dễ đi" hơn | Hội tụ trong vài nghìn bước thay vì hàng trăm nghìn |
| **Mẹo Adam** | Không có | **Bỏ qua bước Adam cho entry bảng hash có gradient ĐÚNG BẰNG 0** | Tiết kiệm ~10% hiệu năng khi gradient thưa (`T ≫ batch size`). Paper **thừa nhận vi phạm 1 số giả định của Adam** nhưng **không thấy suy giảm hội tụ** | — |
| **Đơn vị của batch** | **4 096 TIA** (cố định), mỗi tia 192 điểm mẫu → 786 432 điểm mẫu | **2¹⁸ = 262 144 ĐIỂM MẪU** (cố định) → **10 Ki–85 Ki TIA** (biến thiên) | Paper phát hiện: **nhiều tia hơn = nhiều biến thiên góc nhìn hơn trong 1 batch = hội tụ về sai số thấp hơn trong ít bước hơn**. Vì số điểm mẫu/tia biến thiên, phải cố định batch theo điểm mẫu | **2.5–21× nhiều tia hơn mip-NeRF** (10–85 Ki so với 4 Ki) trong khi batch nhỏ hơn 4 lần |
| **Khởi tạo** | Không nêu chi tiết | MLP: **Glorot/Xavier**. Bảng hash: **`U(−10⁻⁴, 10⁻⁴)`**. Paper đã thử nhiều phương án kể cả khởi tạo 0, tất cả chỉ hơi tệ hơn → **bảng hash bền vững với cách khởi tạo** | Một chút ngẫu nhiên (phá đối xứng) + dự đoán ban đầu gần 0 | Dễ cài đặt lại |
| **Số bước train** | 100 000 – 300 000 | **31 000** (figure) / **~50 000** (sau 5 phút) | — | — |
| **Thời gian train 1 scene** | **~1–2 ngày** (NVIDIA V100) | **5 giây – 5 phút** (NVIDIA RTX 3090) | Tổng hợp của toàn bộ các thay đổi trên | **Tốc độ: "vài bậc độ lớn" (several orders of magnitude)** theo Abstract |
| **Thời gian 1 bước train** | Không nêu | **~6 ms** (bản hash) so với **~30 ms** (bản frequency của chính họ) | — | **5× nhanh hơn mỗi bước**, cộng với cần ít bước hơn |

### E. Nhóm thay đổi về CÀI ĐẶT (không phải đóng góp lý thuyết, nhưng ảnh hưởng lớn tới tốc độ)

| Thành phần | NeRF gốc làm gì | Instant-NGP làm gì | Lý do | Hệ quả |
|---|---|---|---|---|
| **Nền tảng** | TensorFlow / PyTorch tiêu chuẩn | **CUDA thuần + fully-fused MLP** của framework **tiny-cuda-nn** | Mạng đủ nhỏ (64 neuron) để **mọi giá trị trung gian nằm trong thanh ghi / shared memory trên chip**, không phải ghi/đọc bộ nhớ toàn cục | **~10× nhanh hơn** so với cài đặt Python "ngây thơ" (Section 4, chú thích 1) |
| **Độ chính xác số** | Full precision (float32) | **Entry bảng hash lưu ở HALF PRECISION (2 byte)**, kèm **bản sao chủ full precision** để cập nhật mixed-precision ổn định (Micikevicius et al. 2018) | Giảm nửa băng thông bộ nhớ cho phần chiếm chỗ nhiều nhất | Bộ nhớ giảm nửa; tốc độ tăng |
| **Thứ tự tính toán encoding** | Không áp dụng | **Theo TỪNG MỨC cho toàn bộ batch**: tra mức 0 cho mọi input, rồi mức 1 cho mọi input, ... | Để **chỉ vài bảng hash liên tiếp cần nằm trong cache** tại mỗi thời điểm | Tự động tận dụng tốt cache + song song **cho 1 dải rộng giá trị T** |
| **Giới hạn phần cứng được công bố** | Không nêu | **"Vách đá hiệu năng" tại `T > 2¹⁹`** trên RTX 3090, vì L2 cache 6 MB không còn đủ khi `2·T·F > 6·2²⁰` (kiểm chứng: T=2¹⁹ → 2 MB ✓; T=2²¹ → 8 MB ✗) | Minh bạch về giới hạn | Người dùng biết chọn T ≤ 2¹⁹ cho hiệu năng tối ưu |
| **Có công bố mã nguồn?** | Có | Có: `github.com/nvlabs/instant-ngp` + cập nhật vào `tiny-cuda-nn` + **PyTorch bindings** | *"to permit their use in existing projects with little overhead"* | Dễ tái sử dụng cho đồ án |

### F. Những thứ Instant-NGP KHÔNG thay đổi (quan trọng không kém!)

| Thành phần | Trạng thái | Ghi chú |
|---|---|---|
| Chuẩn bị dữ liệu, COLMAP/SfM, bộ ba (R,C,K) | **Giữ nguyên 100%** | Xem `pipeline_NeRF.md` Giai đoạn 1 |
| Công thức sinh tia `r(t) = o + t·d_view` | **Giữ nguyên** | `pipeline_NeRF.md` Giai đoạn 2 mục 2–3 |
| Mô hình camera pinhole, chuyển pixel → hướng tia | **Giữ nguyên** | `pipeline_NeRF.md` Giai đoạn 2 mục 1 |
| Định nghĩa σ là xác suất vi phân tia bị hấp thụ | **Giữ nguyên** | `pipeline_NeRF.md` Giai đoạn 3 |
| Công thức volume rendering liên tục & rời rạc, `T_i`, `α_i` | **Giữ nguyên hoàn toàn** | `pipeline_NeRF.md` Giai đoạn 3 mục 3.3 |
| Nguyên tắc **σ chỉ phụ thuộc vị trí, màu phụ thuộc cả vị trí và hướng nhìn** (để đảm bảo nhất quán đa góc nhìn) | **Giữ nguyên** — vẫn tách MLP density (không thấy hướng nhìn) và MLP màu (thấy hướng nhìn) | Đây là 1 trong các ý tưởng cốt lõi của NeRF gốc mà Instant-NGP **hoàn toàn tôn trọng** |
| Mục tiêu bài toán: novel view synthesis từ ảnh 2D + pose | **Giữ nguyên** | — |

> **📌 KẾT LUẬN CỦA BẢNG TỔNG HỢP.** Instant-NGP **không phải 1 phương pháp mới thay thế NeRF** — nó là **1 bộ thay thế thành phần (drop-in replacement)** cho khâu input encoding của NeRF, cộng với 1 gói tối ưu cài đặt. Paper tự định nghĩa đúng như vậy ở Section 7 (Conclusion): *"In the context of neural network input encodings, it is a **drop-in replacement**, for example speeding up NeRF by several orders of magnitude."* Toàn bộ nền tảng lý thuyết của NeRF (radiance field, volume rendering, ràng buộc multiview consistency) **được giữ nguyên không đổi**.

---

## Kết quả thực nghiệm (trích từ paper)

### Bảng PSNR trên 8 scene tổng hợp (nguyên văn Table 2 của paper)

PSNR (Peak Signal-to-Noise Ratio, **đơn vị dB, càng cao càng tốt**) — chỉ số đo chất lượng ảnh tái tạo so với ảnh tham chiếu.

| Phương pháp | Mic | Ficus | Chair | Hotdog | Materials | Drums | Ship | Lego | **Trung bình** |
|---|---|---|---|---|---|---|---|---|---|
| **Ours: Hash (1 s)** | 26.09 | 21.30 | 21.55 | 21.63 | 22.07 | 17.76 | 20.38 | 18.83 | **21.202** |
| **Ours: Hash (5 s)** | 32.60 | 30.35 | 30.77 | 33.42 | 26.60 | 23.84 | 26.38 | 30.13 | **29.261** |
| **Ours: Hash (15 s)** | 34.76 | 32.26 | 32.95 | 35.56 | 28.25 | 25.23 | 28.56 | 33.68 | **31.407** |
| **Ours: Hash (1 phút)** | 35.92 | 33.05 | 34.34 | 36.78 | 29.33 | 25.82 | 30.20 | 35.63 | **32.635** |
| **Ours: Hash (5 phút)** | 36.22 | 33.51 | 35.00 | 37.40 | 29.78 | 26.02 | 31.10 | 36.39 | **33.176** |
| mip-NeRF (**~nhiều giờ**) | 36.51 | 33.29 | 35.14 | 37.48 | 30.71 | 25.48 | 30.41 | 35.70 | **33.090** |
| NSVF (**~nhiều giờ**) | 34.27 | 31.23 | 33.19 | 37.14 | 32.68 | 25.18 | 27.93 | 32.29 | **31.739** |
| **NeRF gốc (~nhiều giờ)** | 32.91 | 30.13 | 33.00 | 36.18 | 29.62 | 25.01 | 28.65 | 32.54 | **31.005** |
| Ours: Frequency (5 phút) | 31.89 | 28.74 | 31.02 | 34.86 | 28.93 | 24.18 | 28.06 | 32.77 | **30.056** |
| Ours: Frequency (1 phút) | 26.62 | 24.72 | 28.51 | 32.61 | 26.36 | 21.33 | 24.32 | 28.88 | **26.669** |

*(Giá trị của NeRF, mip-NeRF, NSVF được paper lấy từ chính các paper gốc tương ứng.)*

### Đọc bảng này — 5 kết luận quan trọng nhất

1. **Instant-NGP vượt NeRF gốc chỉ sau 15 GIÂY.** `Ours: Hash (15 s)` đạt trung bình **31.407 dB** so với **31.005 dB** của NeRF gốc — vốn mất **nhiều giờ** (paper NeRF gốc báo cáo 1–2 ngày trên V100). Paper phát biểu: *"Our PSNR is competitive with NeRF and NSVF after just 15 s of training."*

2. **Sau 1–5 phút thì cạnh tranh được cả mip-NeRF.** `Ours: Hash (5 phút)` đạt **33.176 dB**, **nhỉnh hơn một chút** mip-NeRF (**33.090 dB**).

3. **Instant-NGP mạnh nhất ở scene có CHI TIẾT HÌNH HỌC CAO.** Paper nêu đúng 4 scene mà họ **đạt PSNR tốt nhất trong tất cả các phương pháp**: **Ficus, Drums, Ship, Lego**.

4. **Nhưng YẾU HƠN ở scene có PHẢN CHIẾU PHỨC TẠP PHỤ THUỘC GÓC NHÌN.** Paper thừa nhận rõ: mip-NeRF và NSVF **vượt** Instant-NGP ở scene **Materials** (NSVF: 32.68; mip-NeRF: 30.71; Instant-NGP 5 phút: 29.78). Paper **tự giải thích nguyên nhân**: *"we attribute this to the **much smaller MLP** that we necessarily employ to obtain our speedup of several orders of magnitude."* → **Đây là 1 đánh đổi thật, được chính tác giả thừa nhận: MLP nhỏ đi thì khả năng biểu diễn hiệu ứng phản chiếu phức tạp giảm.**

5. **Phép tách bạch nguồn tăng tốc — dòng "Ours: Frequency".** Đây là phiên bản dùng **cùng cài đặt CUDA, cùng occupancy grid, cùng ray marching** nhưng thay hash encoding bằng frequency encoding + MLP lớn (7/1 lớp, 256/256 neuron, 16/4 tần số — Appendix D). Nó đạt **30.056 dB sau 5 phút** (tiệm cận NeRF gốc), trong khi bản hash đã đạt mức tương đương **chỉ sau 5–15 giây** → **chênh 20–60×, và chênh này CHỈ do hash encoding + MLP nhỏ**. Paper cũng ghi: bản frequency *"có thể tiếp tục cải thiện chút nữa nếu train lâu hơn"* (vì 5 phút chỉ tương ứng ~10 k bước với 30 ms/bước).

### Kết quả ở 3 bài toán khác (tóm lược — để thấy tính bất biến với bài toán)

| Bài toán | Kết quả đáng chú ý nhất |
|---|---|
| **Gigapixel image** (Section 5.1) | Trên ảnh panorama Tokyo: **ACORN** đạt 38.59 dB sau **36.9 GIỜ** train. Instant-NGP với số tham số tương đương (T=2²⁴) đạt **cùng mức PSNR sau 2.5 PHÚT**, và đạt đỉnh **41.9 dB sau 4 phút**. Paper nói trong ~10–100× tăng tốc còn lại (sau khi trừ ~10× do fully-fused kernel), phần lớn đến từ việc encoding cho phép dùng MLP nhỏ hơn hẳn ACORN. Paper nhấn mạnh **giá trị lớn nhất là SỰ ĐƠN GIẢN**: ACORN cần 1 lịch trình học (learning curriculum) với phép chia nhỏ cảnh thích nghi, Instant-NGP **không cần gì cả**. Figure 6: ảnh 20 000 × 23 466 (469 M pixel) tái tạo được **29.8 dB với chỉ 3.4% số bậc tự do của input**. |
| **SDF** (Section 5.2) | **NGLOD** (dùng octree, không có collision) đạt **chất lượng thị giác cao nhất**. Instant-NGP **tiệm cận NGLOD về chỉ số IoU** với hiệu năng và bộ nhớ tương đương, **nhưng có "vi cấu trúc dạng hạt" mà NGLOD không có** — paper gán nguyên nhân cho hash collision (lập luận: NGLOD là bản không-collision tương đương). **Ưu điểm riêng của Instant-NGP:** SDF được định nghĩa **ở mọi nơi trong thể tích train**, còn NGLOD chỉ định nghĩa **bên trong octree** (tức gần bề mặt) → cho phép dùng các kỹ thuật render như **bóng mềm xấp xỉ** từ các mẫu khoảng cách ngoài bề mặt. |
| **Neural Radiance Caching** (Section 5.3) | So với triangle wave encoding của Müller et al. 2021: hash encoding cho **tái tạo sắc nét hơn** với chi phí hiệu năng **chỉ 0.7 ms**, giảm FPS từ **147 → 133** ở độ phân giải 1920×1080. Đáng chú ý: 0.7 ms đó **bao gồm cả chi phí train VÀ chi phí chạy** — vì NRC được train **trực tuyến trong lúc render**. |

---

## Hạn chế còn lại của Instant-NGP

### A. Hạn chế paper TỰ THỪA NHẬN

| # | Hạn chế | Chi tiết theo paper |
|---|---|---|
| **1** | **Vi cấu trúc dạng hạt (grainy microstructure) do hash collision** | Lỗi đặc trưng của encoding. **Rõ nhất ở SDF** (Figure 1, 7), ở đúng tỉ lệ của mức lưới mịn nhất, **KHÔNG mất đi dù train lâu hơn**. NeRF cũng có nhưng **cường độ nhẹ hơn rất nhiều**. Hướng khắc phục paper đề xuất: **lọc (filter) kết quả tra bảng** hoặc **thêm tiên nghiệm độ trơn vào loss** (Section 6) |
| **2** | **MLP nhỏ làm giảm khả năng biểu diễn phản chiếu phức tạp** | Table 2: thua mip-NeRF và NSVF ở scene **Materials**. Paper gán nguyên nhân trực tiếp cho MLP nhỏ — *"the much smaller MLP that we necessarily employ"* |
| **3** | **Nội suy bậc cao làm GIẢM chất lượng, và paper KHÔNG giải thích được vì sao** | Appendix A: smoothstep làm encoding `C¹`-trơn với chi phí gần như 0, nhưng *"the reconstruction quality tends to decrease as higher-order interpolation is used... **Future research is needed to explain the loss of quality**."* |
| **4** | **Khó dùng trong bối cảnh SINH (generative)** | Section 6: các encoding có tham số khi dùng trong bối cảnh sinh thường sắp feature trong 1 **lưới đặc**, để 1 mạng sinh riêng (thường là CNN kiểu StyleGAN) điền vào. Hash encoding **thêm 1 lớp phức tạp**: feature **không được sắp theo mẫu đều đặn** trong miền input — chúng **không song ánh với 1 lưới điểm đều**. Paper **để ngỏ cho nghiên cứu tương lai** |
| **5** | **Hàm hash là thủ công, chưa được tối ưu** | Section 6: paper đã thử 3 hàm hash khác (PCG32, space-filling curve, tiling) và **loại cả 3**. Họ gợi mở hướng **tự học hàm hash** (biến thành dictionary learning) qua (1) công thức đánh chỉ số liên tục khả vi giải tích hoặc (2) tối ưu tiến hóa |
| **6** | **Chưa định lượng được phần đóng góp của ray marching** | Section 5.4 cuối: paper **tự thừa nhận** cần thêm 1 nghiên cứu để tách riêng ảnh hưởng của các sơ đồ ray marching tiên tiến, độc lập với encoding và kiến trúc mạng |
| **7** | **Phụ thuộc chi tiết phần cứng** | "Vách đá hiệu năng" tại `T > 2¹⁹` do L2 cache 6 MB của RTX 3090. `F = 1` chạy chậm vì atomic half-precision accumulation không hiệu quả cho số vô hướng. Đổi GPU thì các ngưỡng này **thay đổi** |

### B. Hạn chế KẾ THỪA từ NeRF gốc (Instant-NGP không nhắm giải quyết)

| # | Hạn chế | Ghi chú |
|---|---|---|
| **1** | **Cảnh không giới hạn (unbounded)** | Instant-NGP yêu cầu cảnh nằm trong 1 hộp bao đã biết, ánh xạ vào khối đơn vị. Nó **cố tình không dùng warp** (vì làm tia uốn cong → chất lượng kém hơn trong cài đặt của họ), nên không có cơ chế riêng cho cảnh vô hạn. Đây là vấn đề **Mip-NeRF 360** và **NeRF++** nhắm giải quyết (xem `nerf_cai_tien.md`) |
| **2** | **Chống răng cưa (anti-aliasing)** | Instant-NGP **không** có cơ chế chống răng cưa theo nguyên lý như Integrated Positional Encoding của **Mip-NeRF**. Nó giải quyết bằng **vũ lực**: bắn nhiều tia mỗi pixel (khả thi nhờ tốc độ). Về lý thuyết đây là giải pháp "kém thanh thoát" hơn, nhưng thực tiễn hiệu quả |
| **3** | **Vẫn cần camera pose chính xác từ COLMAP** | Không phải hướng của paper này |
| **4** | **Vẫn phải train lại từ đầu cho mỗi scene** | Không có khả năng tổng quát hóa sang scene mới |
| **5** | **Vẫn là ray marching** | Dù nhanh, bản chất render vẫn là "N lần truy vấn + tích lũy cho mỗi pixel", khác với rasterization của **3D Gaussian Splatting** |

### C. Hạn chế thực tiễn khi TÁI CÀI ĐẶT trong đồ án

| # | Hạn chế | Ghi chú |
|---|---|---|
| **1** | **~10× tốc độ đến từ CUDA kernel tùy biến** | Paper ghi rõ ở chú thích 1 Section 4: fully-fused CUDA kernel nhanh hơn ~10× so với 1 cài đặt Python "ngây thơ". Nếu cài lại bằng PyTorch thuần, **sẽ mất phần tăng tốc này**. Giải pháp: dùng **PyTorch bindings mà paper công bố** cho tiny-cuda-nn |
| **2** | **Nhiều chi tiết chỉ có trong code, không có trong paper** | Rõ nhất là "compaction of samples into dense buffers" — chỉ 1 dòng trong paper, chi tiết phải đọc `github.com/nvlabs/instant-ngp` |
| **3** | **Bộ nhớ GPU cao hơn NeRF gốc rất nhiều** | Với T=2¹⁹: ~12.2 M tham số half-precision ≈ 24.4 MB chỉ cho encoding; với T=2²⁴ lên tới ~266 M tham số ≈ 532 MB. So với ~5 MB của NeRF gốc. Cần GPU có đủ VRAM |

---

## Phụ lục — Những điểm trong `nerf_cai_tien.md` cần sửa sau khi đối chiếu paper thật

*Mục "Instant-NGP" trong `nerf_cai_tien.md` được viết từ kiến thức tổng quát, chưa verify. Sau khi đọc paper gốc, đây là các điểm cần sửa, xếp theo mức độ nghiêm trọng.*

| # | Mức độ | Bản sơ bộ nói | Thực tế theo paper | Vị trí trong paper |
|---|---|---|---|---|
| **1** | **SAI** | *"MLP phía sau chỉ cần rất nhỏ — ước lượng khoảng 2 lớp ẩn, 64 kênh/lớp"* | Cấu hình "2 lớp ẩn × 64 kênh" là của **3 bài toán KHÁC** (gigapixel, SDF, NRC). Cấu hình **NeRF** là **HAI MLP nối tiếp**: MLP density **1 lớp ẩn × 64** (output 16 giá trị, giá trị đầu là **log-density**), rồi MLP màu **2 lớp ẩn × 64**. Tổng ≈ **10 k tham số** | Section 4 (*Architecture*) + Section 5.4 (*Model Architecture*) + Figure 10 |
| **2** | **SAI (về cơ chế)** | *"các đỉnh va chạm **thường rơi vào vùng density thấp**/ít quan trọng nên ảnh hưởng nhỏ"* | Hàm hash **rải collision GIẢ NGẪU NHIÊN**, **không hề thiên về vùng density thấp**. Lập luận đúng của paper gồm 4 mảnh: (a) mức thô **ánh xạ 1:1, không collision**, nên encoding tổng thể là **đơn ánh**; (b) collision rải giả ngẫu nhiên nên **xác suất collide đồng thời ở MỌI mức là cực nhỏ**; (c) khi collide, **gradient LẤY TRUNG BÌNH**, và mẫu quan trọng (visibility × density, **nhân với nhau**) **áp đảo** trung bình đó; (d) **MLP tự học phân giải** collision (Figure 11 chứng minh: bỏ MLP → nhiễu tần số cao) | Section 3 (*Implicit hash collision resolution*) + Figure 11 |
| **3** | **THIẾU HOÀN TOÀN** | Không hề nhắc tới **occupancy grid** hay việc Instant-NGP **BỎ HẲN** hierarchical sampling coarse/fine của NeRF gốc | Instant-NGP **không có mạng coarse/fine, không có PDF/CDF/importance sampling, loss chỉ 1 số hạng**. Thay bằng: **cascade K lưới occupancy 128³, 1 bit/ô, Morton order, duyệt DDA**, cập nhật **mỗi 16 vòng lặp** (decay 0.95, lấy max, ngưỡng `0.01·1024/√3`); bước đi cố định `Δt = √3/1024` (hoặc `t/256` lũy thừa cho cảnh lớn); **dừng sớm khi transmittance < 10⁻⁴**. Kết quả: **số điểm mẫu/tia giảm từ 192 cố định xuống 3.1–25.7** | Section 5.4 (*Accelerated ray marching*) + **toàn bộ Appendix E** + Table 3 |
| **4** | **THIẾU HOÀN TOÀN** | Không nhắc gì tới việc Instant-NGP **đổi cách mã hóa hướng nhìn** | NeRF gốc dùng `γ(d)` sin/cos `L_f=4` → **24 chiều**. Instant-NGP dùng **16 hệ số đầu của cơ sở Spherical Harmonics** → **16 chiều** | Section 4 (*Non-spatial input dimensions ξ*) + Section 5.4 |
| **5** | **KHÔNG CÓ CƠ SỞ** | *"cải thiện tốc độ ước lượng khoảng **~1000 lần**"* | Paper **không công bố con số 1000×**. Các con số **có căn cứ** là: **20–60×** do hash encoding + MLP nhỏ (tách bạch bằng baseline "Ours: Frequency" ở Table 2), **~10×** do fully-fused CUDA kernel so với Python ngây thơ (Section 4 chú thích 1), và **"vài bậc độ lớn" (several orders of magnitude)** cho tổng thể (Abstract). Paper còn **tự thừa nhận chưa định lượng được** phần đóng góp của ray marching | Abstract + Section 4 + Section 5.4 + Table 2 |
| **6** | **THIẾU SIÊU THAM SỐ CỤ THỂ** | Chỉ nêu *"L=16"*, *"T=2¹⁴ đến 2²⁴"*, *"feature 2 số thực"*, *"lưới 16³ đến 2048³"* một cách rời rạc, không có công thức | Đầy đủ (Table 1): **L=16, T=2¹⁴–2²⁴, F=2, N_min=16, N_max=512–524288** (với NeRF: `N_max = 2048 × kích thước cảnh`), **b ∈ [1.26, 2]**, công thức `N_l = ⌊N_min·b^l⌋` (Eq. 2) và `b = exp((ln N_max − ln N_min)/(L−1))` (Eq. 3). Điều kiện ánh xạ 1:1: `(N_l+1)^d ≤ T`. Hàm hash (Eq. 4) với **π₁=1, π₂=2654435761, π₃=805459861** | Table 1 + Section 3, Eq. 2–4 |
| **7** | **THIẾU SIÊU THAM SỐ TRAINING** | Không nêu | Adam **β₁=0.9, β₂=0.99** (không phải 0.999!), **ε=10⁻¹⁵** (không phải 10⁻⁷ — khác 8 bậc, và paper **giải thích rõ lý do**: giúp entry bảng hash có gradient thưa/yếu hội tụ nhanh hơn), **lr = 10⁻²**, giảm × 0.33 sau 20 k bước rồi mỗi 10 k bước, **L2 reg 10⁻⁶ CHỈ cho MLP**, **batch = 2¹⁸ ĐIỂM MẪU** (không phải tia!) → 10 Ki–85 Ki tia, khởi tạo hash `U(−10⁻⁴,10⁻⁴)` + Glorot cho MLP, **bỏ qua bước Adam cho entry có gradient = 0** (tiết kiệm ~10%) | Section 4 (*Training*, *Initialization*) + Section 5.4 + Table 3 |
| **8** | **ĐÁNH GIÁ SAI MỨC ĐỘ** | *"**Hash collision** có thể gây artifact **nhỏ** (nhiễu/nhòe) ở 1 số vùng, đặc biệt vùng chi tiết cao nhưng **ít được quan sát** trong tập ảnh train"* | Paper gọi đây là **"lỗi nổi bật nhất (salient artifact)"** của encoding, đặt tên cụ thể là **"vi cấu trúc dạng hạt" (grainy microstructure)**, xuất hiện **ở đúng tỉ lệ của mức lưới mịn nhất** (không phải "vùng ít được quan sát"), và **KHÔNG mất đi dù train lâu hơn**. Nó **rõ nhất ở SDF**, nhẹ hơn nhiều ở NeRF. Paper coi việc khắc phục nó là **chìa khóa để đạt chất lượng SOTA cho SDF** | Section 5.2 + Section 6 (*Microstructure due to hash collisions*) + Figure 1, 7 |
| **9** | **THIẾU (các đánh đổi thật)** | Không nhắc | (a) Instant-NGP **yếu hơn** mip-NeRF/NSVF ở scene phản chiếu phức tạp (**Materials**), paper tự gán nguyên nhân cho **MLP nhỏ**. (b) Encoding chỉ **`C⁰`-trơn** (NeRF gốc `C^∞`); smoothstep cho `C¹` nhưng **mặc định tắt vì giảm chất lượng, và paper không giải thích được vì sao**. (c) **Khó dùng trong bối cảnh sinh (generative)** vì feature không song ánh với lưới đều | Table 2 + Appendix A + Section 6 |
| **10** | **THIẾU (các quyết định thiết kế đáng nói)** | Không nhắc | (a) Paper **CỐ TÌNH không xử lý collision** theo cách kinh điển (không probing/bucketing/chaining) vì chúng gây **phân kỳ thực thi** trên GPU. (b) Paper **CỐ TÌNH không warp không gian** như NeRF gốc/Mip-NeRF 360 vì warp **làm tia uốn cong → chất lượng kém hơn**. (c) Paper **nối (concatenate) thay vì cộng** các mức, có 2 lý do rõ ràng. (d) Encoding **chỉ cần tinh chỉnh 2 siêu tham số (T và N_max)**, dùng chung cài đặt cho cả 4 bài toán. (e) Figure 11 **chứng minh MLP là cần thiết** (khác Plenoxels/DVGO bỏ hẳn mạng), chi phí chỉ hơn 15% | Section 2, 3, 6 + Appendix E.1 + Figure 11 |
| **11** | **THIẾU (con số tốc độ render cụ thể)** | *"Tốc độ render... đạt **gần** thời gian thực"* | Paper công bố con số rõ: **render hàng chục mili-giây ở 1920×1080** (Abstract), **60 FPS ở độ phân giải HD** (Section 5.4), và nhấn mạnh đạt được điều này **KHÔNG CẦN đệm (cache) output MLP** như FastNeRF/NeX/PlenOctrees. Hệ quả đẹp: đủ nhanh để làm **chống răng cưa / motion blur / depth-of-field bằng vũ lực** (bắn nhiều tia mỗi pixel) | Abstract + Section 5.4 + Figure 12 |
| **12** | **Diễn đạt chưa chính xác** | *"Bộ nhớ lưu trữ sau train: lớn hơn NeRF gốc"* (không có số) | Định lượng được: số tham số encoding = `F · Σ_l min((N_l+1)³, T)`, chặn trên bởi `T·L·F = T·32`. Với T=2¹⁴ → **494 k** (khớp Figure 2(e)); T=2¹⁹ → ~12.2–12.6 M; T=2²⁴ → ~266 M. Lưu ở **half precision (2 byte)** kèm **bản sao chủ full precision** cho cập nhật mixed-precision. Và có **"vách đá hiệu năng" tại T > 2¹⁹** do L2 cache 6 MB của RTX 3090 (`2·T·F > 6·2²⁰`) | Section 3, 4 + Figure 2, 4 |

### Gợi ý hành động cho `nerf_cai_tien.md`

1. **Xóa câu "lưu ý không có paper gốc"** ở đầu mục Instant-NGP — giờ đã verify trực tiếp với arXiv:2201.05989v2.
2. **Sửa 2 điểm SAI** (#1 kiến trúc MLP, #2 cơ chế collision) — đây là 2 điểm sai về nội dung khoa học, nếu đưa vào báo cáo sẽ bị hỏi.
3. **Xóa hoặc ghi rõ nguồn cho con số "~1000 lần"** (#5) — thay bằng "20–60× do hash encoding + MLP nhỏ, ~10× do cài đặt CUDA, tổng thể 'vài bậc độ lớn' theo Abstract".
4. **Bổ sung 1 đoạn ngắn về occupancy grid** (#3) và **1 dòng về Spherical Harmonics** (#4) — đây là 2 thay đổi lớn so với NeRF gốc mà bản sơ bộ bỏ sót hoàn toàn.
5. Phần chi tiết đầy đủ thì **trỏ sang file này** (`pipeline_InstantNGP.md`), không cần nhồi hết vào `nerf_cai_tien.md` (vốn là file khảo sát nhiều phương pháp, nên giữ ngắn gọn ở mỗi mục).

---

## Tài liệu liên quan trong thư mục đồ án

- **`Doan/pipeline_NeRF.md`** — tài liệu song song cho **NeRF gốc** (arXiv:2003.08934). File này **phụ thuộc vào nó**: Giai đoạn 1 (COLMAP/SfM), công thức sinh tia, mô hình pinhole, và toàn bộ toán volume rendering đều **không được nhắc lại ở đây** mà trỏ sang đó.
- **`Doan/nerf_cai_tien.md`** — khảo sát ngắn 7 phương pháp cải tiến NeRF (Instant-NGP, Mip-NeRF, Mip-NeRF 360, NeRF++, Plenoxels, 3D Gaussian Splatting) kèm bảng so sánh tổng hợp. Mục Instant-NGP ở đó **cần sửa theo phụ lục trên**.
- **`Doan/lythuyet.md`**, **`Doan/tomtat_paper_NeRF.md`** — ghi chú học tập và tóm tắt paper NeRF gốc.
- **`Doan/03-Reference/Related/2022 Instant Neural Graphics Primitives with a Multiresolution Hash Encoding.pdf`** — paper gốc (15 trang), nguồn của toàn bộ tài liệu này.

### Cách dùng file này cho báo cáo đồ án

Theo cấu trúc báo cáo yêu cầu (`huongdantrinhbay.rtf`, xem `CLAUDE.md`):

| Chương báo cáo | Dùng phần nào của file này |
|---|---|
| **Ch.2 — Các công trình liên quan** | **[BẢNG TỔNG HỢP "Thay đổi gì so với NeRF gốc"](#bảng-tổng-hợp--instant-ngp-thay-đổi-những-gì-so-với-nerf-gốc)** (nhóm A–F) + **[Kết quả thực nghiệm](#kết-quả-thực-nghiệm-trích-từ-paper)** (Table 2) + **[Hạn chế](#hạn-chế-còn-lại-của-instant-ngp)** |
| **Ch.3 — Phương pháp** (nếu chọn Instant-NGP làm phương pháp chính) | Trình bày theo đúng thứ tự *nguyên lý → phương pháp → giải thuật*: **Giai đoạn 2** (nguyên lý + công thức Eq. 2–4) → **Giai đoạn 3** (kiến trúc) → **Giai đoạn 4** (giải thuật training) → **[Sơ đồ tổng thể](#53-sơ-đồ-tổng-thể-toàn-bộ-pipeline-instant-ngp)** |
| **Ch.4 — Cài đặt và thử nghiệm** | **Giai đoạn 4 mục 4.7** (bảng siêu tham số đầy đủ), **mục 4.9** (môi trường: CUDA/tiny-cuda-nn, GPU RTX 3090, PyTorch bindings), **mục 4.11** (quy trình 1 vòng lặp), **Hạn chế mục C** (lưu ý khi tái cài đặt) |
| **Ch.5 — Kết luận & hướng phát triển** | **[Hạn chế mục A](#a-hạn-chế-paper-tự-thừa-nhận)** — đặc biệt các hướng tương lai paper tự đề xuất: lọc kết quả tra bảng / tiên nghiệm độ trơn để diệt microstructure; **tự học hàm hash** (dictionary learning); mở rộng sang bối cảnh sinh; áp dụng cho trường density thể tích không đồng nhất (mây, khói — VDB) |
