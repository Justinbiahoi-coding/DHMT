# Quy trình Đầy đủ NeRF: Từ Ảnh Input đến Ảnh Output

*Tài liệu hệ thống hóa toàn bộ các sự kiện xảy ra khi dùng NeRF (Neural Radiance Fields) để tạo thành công 1 ảnh output ở góc nhìn mới — từ lúc chỉ có 1 thư mục ảnh thô, qua toàn bộ quá trình ước lượng camera pose, xây dựng và huấn luyện mạng, cho tới khi render ra ảnh hoàn chỉnh. Biên soạn dựa trên nội dung đã trình bày trong `lythuyet.md` và `tomtat_paper_NeRF.md`, hệ thống lại theo đúng trình tự thời gian thực tế của 1 pipeline NeRF, có chú thích/định nghĩa đầy đủ mọi công thức, đại lượng, định lý ngay lần đầu xuất hiện.*

## Mục lục

1. **[Giai đoạn 1](#giai-đoạn-1-chuẩn-bị-dữ-liệu-đầu-vào--ước-lượng-camera-pose-colmapsfm)** — Chuẩn bị dữ liệu đầu vào & Ước lượng Camera Pose (COLMAP/SfM)
2. **[Giai đoạn 2](#giai-đoạn-2-sinh-ray-lấy-mẫu-điểm--positional-encoding)** — Sinh Ray, Lấy mẫu điểm & Positional Encoding
3. **[Giai đoạn 3](#giai-đoạn-3-forward-pass-qua-mlp--volume-rendering)** — Forward Pass qua MLP & Volume Rendering
4. **[Giai đoạn 4](#giai-đoạn-4-hierarchical-sampling-hàm-loss--vòng-lặp-training)** — Hierarchical Sampling, Hàm Loss & Vòng lặp Training
5. **[Giai đoạn 5](#giai-đoạn-5-inference--render-output--sơ-đồ-tổng-thể-pipeline)** — Inference — Render Output & Sơ đồ Tổng thể Pipeline

**Quy ước xuyên suốt tài liệu:** mỗi công thức/ký hiệu lần đầu xuất hiện đều có bảng "Chú thích ký hiệu" đi kèm; khi nhắc lại ở phần sau chỉ lướt nhẹ qua ý nghĩa (không giảng lại từ đầu). Phần nào có nguồn gốc không chắc chắn từ văn bản chính paper gốc (ví dụ: chi tiết triển khai chỉ có trong code công bố) đều được ghi chú rõ ràng, tách bạch khỏi nội dung chính văn paper.

---

## Giai đoạn 1: Chuẩn bị dữ liệu đầu vào & Ước lượng Camera Pose (COLMAP/SfM)

### 1.1. Yêu cầu dữ liệu đầu vào

NeRF không học từ dữ liệu 3D có sẵn (mesh, point cloud, CAD) — toàn bộ pipeline chỉ cần **ảnh 2D chụp thường** của cảnh/vật thể cần tái tạo. Yêu cầu cụ thể:

- **Số lượng ảnh:** thường 20–100 ảnh cho 1 scene. Quá ít ảnh (dưới ~15–20) khiến các bước ước lượng camera pose (mục 1.2) và việc học hình học ở giai đoạn sau thiếu ràng buộc, dễ cho kết quả sai/mờ.
- **Góc chụp:** đi vòng quanh vật thể (nếu vật thể độc lập, kiểu "object-centric") hoặc quét ngang qua cảnh (nếu cảnh rộng, kiểu "forward-facing"), mỗi ảnh lệch góc vừa phải so với ảnh liền kề — độ chồng lấp (overlap) giữa 2 ảnh liên tiếp phải đủ lớn để thuật toán ở mục 1.2 tìm được điểm chung giữa chúng.
- **Yêu cầu vật lý của cảnh:** cảnh phải **tĩnh** trong suốt quá trình chụp (vật thể/ánh sáng không đổi giữa các ảnh) — vì NeRF giả định có 1 hàm radiance field duy nhất, cố định, mô tả toàn bộ cảnh.
- **Đầu ra cần có sau Giai đoạn 1 này** (input bắt buộc cho các giai đoạn sau): với **mỗi ảnh**, cần biết chính xác (a) camera đã đứng ở đâu, chĩa hướng nào lúc chụp ảnh đó (gọi là **pose**), và (b) đặc tính quang học của ống kính dùng chụp. Nếu dữ liệu tổng hợp (synthetic, dựng bằng phần mềm 3D) thì các thông số này có sẵn (ground truth). Nếu ảnh chụp thật ngoài đời, các thông số này **không có sẵn** — phải dùng thuật toán ước lượng lại từ chính nội dung ảnh, đây là nội dung chính của mục 1.2.

### 1.2. Pose camera gồm những con số nào

**Pose** = vị trí + hướng nhìn của 1 camera tại thời điểm chụp 1 ảnh, biểu diễn trong 1 hệ tọa độ chung cho toàn cảnh gọi là **hệ world** (world coordinate system) — một hệ trục x,y,z cố định, dùng chung cho mọi ảnh, không đổi giữa các ảnh khác nhau.

Pose gồm 2 thành phần, gọi chung là **ma trận ngoại tại (extrinsic matrix)**:

- **R — ma trận xoay (rotation matrix), kích thước 3×3:** mô tả camera đang xoay/chĩa theo hướng nào. Gồm 3 vector cột, mỗi cột là tọa độ (trong hệ world) của 1 trong 3 trục cục bộ của camera (ví dụ: cột 1 = hướng "bên phải" của camera, cột 2 = hướng "lên trên" của camera, cột 3 = hướng "ra sau"/"ra trước" của camera, tùy quy ước). Về mặt toán học, nhân R với 1 vector sẽ **xoay** vector đó — R chính là phép biến đổi "hướng đo theo khung quy chiếu riêng của camera" sang "hướng đo theo khung quy chiếu chung (world)".
- **C — tâm camera (camera center), vector 3×1:** tọa độ (x,y,z) của vị trí đặt camera trong hệ world.

Ghép R và C lại thành 1 ma trận 4×4 gọi là **ma trận camera-to-world**:

```
[ R11 R12 R13 | Cx ]
[ R21 R22 R23 | Cy ]
[ R31 R32 R33 | Cz ]
[  0   0   0  |  1  ]
```

Mỗi ảnh input có đúng 1 ma trận như vậy đi kèm.

Ngoài R, C (mô tả "camera đặt/xoay ở đâu" — gọi chung là thông số **ngoại tại/extrinsic**), còn cần 1 ma trận thứ 3 mô tả bản chất quang học của chính ống kính, không phụ thuộc vị trí camera — gọi là thông số **nội tại/intrinsic**, ký hiệu **K**, kích thước 3×3:

```
K = [ fx   0   cx ]
    [  0  fy   cy ]
    [  0   0    1 ]
```

- **fx, fy (focal length — tiêu cự):** tính theo đơn vị pixel, liên hệ với góc nhìn (field of view) của ống kính — tiêu cự càng lớn, góc nhìn càng hẹp (càng "zoom").
- **cx, cy (principal point — điểm chính):** tọa độ pixel nơi trục quang học của ống kính cắt mặt phẳng ảnh, thường gần đúng bằng tâm hình học của ảnh.

**Tóm lại:** pose + intrinsic của 1 ảnh = bộ 3 **(R, C, K)**. R, C nói về "camera đặt/xoay ở đâu trong không gian" (ngoại tại, đổi theo từng ảnh); K nói về "bản chất ống kính" (nội tại, giữ nguyên nếu cùng 1 máy ảnh chụp toàn bộ dataset).

### 1.3. Vì sao bắt buộc phải có (R, C, K) chính xác

Ở các giai đoạn sau (sinh tia, lấy mẫu điểm 3D), việc "bắn 1 tia xuyên qua đúng pixel đang xét, vào đúng hướng trong không gian cảnh" chỉ tính được nếu biết chính xác camera đã đứng ở đâu (C), xoay thế nào (R), và ống kính quy đổi góc ra pixel ra sao (K). Nếu bộ 3 này sai dù chỉ một chút, các tia tính ra từ nhiều ảnh khác nhau sẽ **không giao đúng chỗ** trong không gian 3D thật — hậu quả là mô hình học được bị nhòe, lệch hình học, hoặc hoàn toàn không hội tụ.

### 1.4. Lấy (R, C, K) từ đâu — COLMAP / Structure-from-Motion (SfM)

Với dữ liệu tổng hợp, (R,C,K) có sẵn (ground truth). Với ảnh chụp thật, các thông số này phải được **ước lượng ngược lại** từ chính nội dung ảnh — công cụ chuẩn dùng cho việc này là **COLMAP**, một phần mềm mã nguồn mở hiện thực hóa kỹ thuật **Structure-from-Motion (SfM)**.

**SfM là gì — trực giác:** "Structure from Motion" nghĩa là khôi phục lại **cấu trúc 3D** (Structure) của cảnh, suy ra từ **sự chuyển động** (Motion, tức các vị trí chụp khác nhau) của camera qua nhiều ảnh. Ví von: giống con người nghiêng đầu qua trái–phải, vật ở gần dịch chuyển nhiều trong tầm nhìn hơn vật ở xa (hiệu ứng **thị sai — parallax**) — não bộ dùng độ chênh lệch đó để cảm nhận độ sâu. SfM làm đúng việc này bằng toán học, dựa trên nhiều ảnh thay vì 2 mắt.

COLMAP thực hiện tuần tự 7 bước sau:

#### Bước 1 — Phát hiện điểm đặc trưng (Feature Detection) bằng SIFT

**SIFT (Scale-Invariant Feature Transform — "phép biến đổi đặc trưng bất biến tỉ lệ")** là thuật toán tìm ra những điểm "dễ nhận ra" trong ảnh (góc vật, hoa văn, cạnh sắc nét...) — ổn định dù ảnh bị xoay, co giãn, hay đổi sáng nhẹ. Gồm các bước con:

**(a) Dựng không gian tỉ lệ (scale-space) bằng Gaussian blur:** làm mờ ảnh gốc với độ mờ σ tăng dần, tạo ra 1 chồng ảnh mờ dần gọi là 1 **octave**. Gaussian là kernel làm mờ duy nhất thỏa tiêu chí "không sinh thêm cấu trúc giả" khi tăng σ — nền tảng lý thuyết scale-space. Sau khi σ trong 1 octave đã tăng gấp đôi, hạ độ phân giải ảnh xuống 1 nửa (downsample) để tạo octave tiếp theo. Dùng thường 4–5 octave để phủ được dải kích thước vật thể từ nhỏ tới lớn (gần/xa camera).

**(b) Difference of Gaussians (DoG):** lấy hiệu giữa 2 ảnh mờ liền kề trong cùng 1 octave — đây là phép xấp xỉ rẻ tiền của toán tử phát hiện góc/đốm sáng kinh điển (Laplacian of Gaussian).

**(c) Tìm cực trị cục bộ:** với mỗi pixel trong ảnh DoG, so sánh nó với **26 pixel lân cận** — 8 pixel cùng mức mờ (lưới 3×3 trừ chính nó) + 9 pixel ở mức mờ ngay trên + 9 pixel ở mức mờ ngay dưới (khối 3×3×3, trừ tâm). Nếu pixel đang xét là giá trị lớn nhất hoặc nhỏ nhất trong 26 pixel đó, nó là 1 **keypoint ứng viên**. So sánh theo cả 3 chiều (x, y, và mức tỉ lệ) — chứ không chỉ trong 1 ảnh — chính là cơ chế tạo ra tính "bất biến tỉ lệ" của SIFT: chỉ giữ lại điểm ổn định ở đúng 1 quy mô kích thước nhất định, không phải nhiễu ngẫu nhiên.

**(d) Tinh chỉnh & lọc bỏ:**
- *Nội suy dưới-pixel (subpixel):* khai triển Taylor bậc 2 của hàm DoG, ký hiệu D, quanh pixel ứng viên x₀: `D(x) ≈ D(x₀) + (∂D/∂x)ᵀΔx + ½ΔxᵀHΔx`, trong đó Δx là độ lệch (có thể là số thập phân) cần tìm từ x₀ tới cực trị thật, H là ma trận Hessian (ma trận đạo hàm bậc 2 của D). Lấy đạo hàm biểu thức trên theo Δx và cho bằng 0, giải ra: `Δx̂ = -H⁻¹(∂D/∂x)` — vị trí cực trị chính xác hơn mức pixel nguyên.
- *Loại điểm tương phản thấp:* tính giá trị D tại điểm đã nội suy; nếu |D| nhỏ hơn 1 ngưỡng (thường 0.03, với ảnh chuẩn hóa [0,1]) thì loại, vì điểm tương phản thấp dễ bị nhiễu ảnh chi phối, không ổn định để dùng khớp ảnh về sau.
- *Loại điểm nằm trên cạnh:* dùng ma trận Hessian 2×2 (chỉ xét x,y) `H = [[Dxx, Dxy], [Dxy, Dyy]]`, với Dxx, Dyy, Dxy là các đạo hàm bậc 2 của D. Gọi α, β là 2 trị riêng (eigenvalue) của H, r = α/β. Một góc thật có 2 trị riêng lớn và xấp xỉ nhau (r≈1); một điểm nằm trên cạnh có 1 trị riêng lớn, 1 rất nhỏ (r lớn) — vì dọc theo cạnh, D gần như không đổi, vị trí không xác định rõ theo hướng đó. Thay vì tính trực tiếp α, β (tốn kém), dùng công thức `Tr(H)²/Det(H) = (α+β)²/(αβ) = (r+1)²/r` (Tr = vết ma trận = Dxx+Dyy; Det = định thức = DxxDyy−Dxy²) — tỉ lệ này tăng đơn điệu theo r. Với ngưỡng chuẩn r=10, nếu `Tr(H)²/Det(H) > 12.1` thì bị loại (là cạnh, không ổn định).

**(e) Gán hướng chủ đạo:** quanh mỗi keypoint còn lại, dựng 1 histogram gradient với **36 khoảng (bin)**, mỗi bin rộng 10°, có trọng số theo độ lớn gradient. Hướng ứng với bin có tổng phiếu cao nhất là **hướng chủ đạo** của keypoint — dùng để sau này "xoay" hệ quy chiếu cục bộ về chuẩn, tạo tính bất biến với phép xoay ảnh.

**(f) Tính descriptor — vector 128 số:** lấy vùng 16×16 pixel quanh keypoint (đã xoay theo hướng chủ đạo ở bước e), chia thành lưới **4×4 = 16 ô** nhỏ (mỗi ô 4×4 pixel). Mỗi ô dựng 1 histogram gradient với **8 hướng** (8 bin, mỗi bin 45°). Nối 16 ô × 8 số = **128 số**, chuẩn hóa về độ dài 1 (triệt tiêu ảnh hưởng đổi sáng tuyến tính), rồi cắt ngưỡng giá trị >0.2 và chuẩn hóa lại lần 2 (giảm ảnh hưởng vùng lóa sáng). Vector 128 số này — gọi là **descriptor** — chính là "vân tay số" nhận dạng keypoint: 2 điểm cùng 1 vị trí vật lý thật (dù chụp từ góc khác) sẽ có descriptor gần giống nhau (khoảng cách Euclid nhỏ trong không gian 128 chiều); 2 điểm khác nhau sẽ có descriptor khác hẳn.

#### Bước 2 — Khớp điểm đặc trưng giữa các ảnh (Feature Matching)

Với mỗi cặp ảnh, so từng descriptor (128 số) của ảnh A với từng descriptor của ảnh B, tìm cặp có khoảng cách Euclid nhỏ nhất (dùng cấu trúc **KD-tree** — cây phân hoạch không gian nhiều chiều — để tăng tốc tìm kiếm thay vì so trực tiếp từng cặp). Áp dụng **Lowe's ratio test** để loại match mơ hồ: với mỗi điểm ở A, tìm 2 điểm gần nhất ở B (khoảng cách d₁ gần nhất, d₂ gần nhì); nếu tỉ lệ d₁/d₂ > 0.8 (hai khoảng cách xấp xỉ nhau, không rõ ràng điểm nào đúng) thì loại bỏ match đó.

#### Bước 3 — Kiểm chứng hình học (Geometric Verification) bằng RANSAC

Hai ảnh chụp cùng 1 cảnh cứng từ 2 vị trí khác nhau phải tuân theo 1 ràng buộc hình học chặt chẽ gọi là **ràng buộc cực (epipolar constraint)**, biểu diễn qua 1 ma trận 3×3 gọi là **Essential Matrix, ký hiệu E**. Vì tập match ở Bước 2 vẫn còn lẫn match sai (do trùng hợp ngẫu nhiên), dùng thuật toán **RANSAC (Random Sample Consensus — "đồng thuận trên mẫu ngẫu nhiên")** để lọc:

1. Chọn ngẫu nhiên 5 cặp match (Essential Matrix có đúng 5 bậc tự do, nên 5 cặp là đủ dữ liệu tối thiểu để giải — dùng thuật toán **5-point**, giải ra tối đa 10 nghiệm E khả dĩ).
2. Với mỗi E ứng viên, đếm có bao nhiêu match khác (trong toàn bộ tập) thỏa mãn `x₂ᵀEx₁ ≈ 0` (x₁, x₂ là tọa độ 2 điểm khớp dạng thuần nhất) trong phạm vi sai số cho phép — gọi là **inlier**.
3. Lặp lại K lần (K thường ~1000–2000, tính theo công thức xác suất `N = log(1-p)/log(1-wⁿ)`, với p = độ tự tin mong muốn tìm được mẫu toàn inlier (thường 0.99), w = tỉ lệ inlier ước tính, n=5), giữ lại E có số inlier nhiều nhất.

#### Bước 4 — Phân tích Essential Matrix ra Pose tương đối (R, t)

Phân tích E bằng **SVD (Singular Value Decomposition — phân tích giá trị suy biến)**: `E = U·Σ·Vᵀ`, trong đó U, V là các ma trận trực giao 3×3, Σ là ma trận đường chéo. Dùng 1 ma trận xoay cố định `W = [[0,-1,0],[1,0,0],[0,0,1]]`, suy ra `R = U·W·Vᵀ` (hoặc `U·Wᵀ·Vᵀ`) và `t = ±(cột 3 của U)` — cho ra **4 tổ hợp (R,t)** khả dĩ (vì SVD không duy nhất về dấu). Chọn đúng 1 trong 4 bằng kiểm tra **cheirality**: tam giác hóa thử 1 điểm với mỗi tổ hợp, chọn tổ hợp cho điểm 3D nằm **phía trước** cả 2 camera (nhìn thấy được, không phải điểm ảo nằm sau lưng camera). Lưu ý: E chỉ cho pose tương đối tới 1 hệ số tỉ lệ (scale ambiguity) — không biết khoảng cách thật tính theo mét/cm.

#### Bước 5 — Tam giác hóa (Triangulation) bằng DLT

Có 2 pose camera (từ Bước 4) + 1 cặp điểm khớp trên 2 ảnh → bắn 2 tia (theo công thức tia đã dùng ở các giai đoạn sau, r(t)=o+t·d) từ 2 tâm camera qua 2 điểm ảnh tương ứng, tìm điểm 3D gần đúng nhất với cả 2 tia. Vì sai số đo đạc khiến 2 tia thường không giao chính xác tuyệt đối, dùng phương pháp **DLT (Direct Linear Transform)**: ràng buộc chiếu đúng `x × (P·X) = 0` (x là tọa độ pixel quan sát, P là ma trận chiếu 3×4 gộp cả K và pose, X là tọa độ 3D thuần nhất 4 chiều cần tìm) khai triển thành hệ phương trình tuyến tính, giải bằng SVD, nghiệm X = cột ứng với trị suy biến nhỏ nhất của ma trận hệ số — đây là nghiệm bình phương tối thiểu (least-squares).

#### Bước 6 — Thêm dần từng ảnh còn lại (Incremental SfM) bằng P3P

Với mỗi ảnh mới chưa có pose: (a) khớp feature với các ảnh đã có pose; (b) lọc ra các match trùng với điểm 3D đã triangulate ở các bước trước, có được tập tương ứng 2D (pixel) – 3D (điểm đã biết tọa độ); (c) giải bài toán **PnP (Perspective-n-Point)**, cụ thể dùng **P3P (Perspective-3-Point)**: biết 3 điểm 3D + vị trí 2D tương ứng, dùng định lý hàm cosin trong tam giác tạo bởi tâm camera và 3 điểm đó (góc giữa các cặp tia tính được từ pixel + K) để dựng hệ phương trình, rút gọn thành **1 phương trình đa thức bậc 4** theo 1 ẩn — vì pose camera có 6 bậc tự do (3 xoay + 3 dịch) nhưng quan hệ phép chiếu phối cảnh phi tuyến nên không giải tuyến tính trực tiếp được. Đa thức bậc 4 cho tối đa 4 nghiệm thực; dùng 1 điểm thứ 4 (ngoài 3 điểm ban đầu) để kiểm tra, chọn đúng 1 nghiệm. Toàn bộ quy trình P3P này cũng được bọc trong vòng lặp RANSAC để loại trừ correspondence sai; (d) sau khi có pose ảnh mới, triangulate thêm các điểm mới quan sát được từ ảnh đó, mở rộng đám mây điểm 3D. Lặp lại cho tới khi hết ảnh.

#### Bước 7 — Tinh chỉnh toàn cục (Bundle Adjustment) bằng Levenberg-Marquardt

Chạy định kỳ xen kẽ trong suốt Bước 6 (không chỉ 1 lần cuối, để tránh sai số tích lũy — "drift" — khi thêm nhiều ảnh): điều chỉnh **đồng thời** toàn bộ pose của mọi camera **và** toàn bộ tọa độ điểm 3D, nhằm tối thiểu hóa tổng bình phương **sai số tái chiếu (reprojection error)** — khoảng cách giữa vị trí pixel thật đã phát hiện (Bước 1) và vị trí pixel suy ra khi chiếu lại điểm 3D qua pose camera tương ứng. Đây là bài toán tối ưu phi tuyến quy mô lớn (với 100 ảnh + 10.000 điểm 3D, có thể lên tới hàng chục nghìn tham số), giải bằng thuật toán **Levenberg-Marquardt (LM)** — phương pháp kết hợp giữa Gauss-Newton (hội tụ nhanh gần nghiệm, dùng xấp xỉ đạo hàm bậc 2 qua ma trận Jacobian J) và Gradient Descent (ổn định hơn khi còn xa nghiệm). Công thức cập nhật tham số mỗi vòng lặp:

```
(JᵀJ + λ·diag(JᵀJ))·Δ = -Jᵀ·r
```

trong đó J là ma trận Jacobian của hàm sai số tái chiếu theo mọi tham số, r là vector sai số hiện tại, Δ là bước cập nhật cần giải, λ là hệ số giảm xóc (damping) — λ nhỏ thì công thức tiến gần Gauss-Newton (hội tụ nhanh), λ lớn thì tiến gần Gradient Descent (an toàn hơn khi xa nghiệm); λ được tự động tăng/giảm qua từng vòng lặp tùy việc cập nhật có làm giảm sai số hay không.

### 1.5. Kết quả của Giai đoạn 1

Sau khi COLMAP hoàn tất 7 bước trên, với **mỗi ảnh** trong dataset đầu vào, ta có đầy đủ bộ ba **(R, C, K)** đã tinh chỉnh chính xác nhất có thể — toàn bộ nằm chung trên **1 hệ tọa độ world** duy nhất (hệ này hình thành từ chính cặp ảnh khởi tạo ở Bước 3–4, các ảnh sau chỉ được định vị tương đối theo hệ đó qua Bước 6). Ngoài ra còn thu được 1 đám mây điểm 3D thưa (sparse point cloud, sản phẩm phụ của quá trình triangulate) — dùng để ước lượng khoảng **t_near, t_far** (biên gần/xa của cảnh so với mỗi camera), cần cho giai đoạn lấy mẫu điểm trên tia về sau.

Đến đây, với mỗi ảnh, pipeline NeRF đã có đủ thông tin để trả lời câu hỏi: "camera này đứng ở đâu, chĩa hướng nào, ống kính quy đổi pixel ra góc nhìn ra sao?" — nhưng vẫn chưa biết **từng pixel cụ thể trên ảnh ứng với hướng nào trong không gian 3D**. Đây chính là nội dung của **Giai đoạn 2: Sinh tia (Ray Generation)** — dùng bộ (R, C, K) vừa có, kết hợp tọa độ (u,v) của từng pixel, tính ra vector hướng và từ đó dựng công thức tia hoàn chỉnh cho mỗi pixel trên mỗi ảnh.


---

## Giai đoạn 2: Sinh Ray, Lấy mẫu điểm & Positional Encoding

Tiếp nối Giai đoạn 1: với mỗi ảnh trong tập dữ liệu, ta đã có đầy đủ bộ ba (R, C, K) — ma trận xoay, tâm camera, ma trận nội tại. Giai đoạn này mô tả cách dùng bộ ba đó để, từ 1 pixel cụ thể (u,v) trên 1 ảnh, sinh ra tập hợp các điểm 5 chiều (x,y,z,θ,φ) đã được mã hóa, sẵn sàng đưa vào mạng MLP.

### 1. Nền tảng: Pinhole Camera Model / Phép chiếu phối cảnh

#### 1.1. Trực giác về phối cảnh

Quan sát đời thường: hai vật có cùng kích thước thật, nhưng vật ở xa mắt/camera hơn sẽ trông **nhỏ hơn** trong ảnh. Ví dụ hai cột đèn cao bằng nhau đặt cách xa nhau trên một con đường thẳng — trong ảnh chụp, cột đèn ở xa luôn trông thấp hơn cột đèn ở gần. Hiện tượng này gọi là **phối cảnh (perspective)**, và nó không phải ảo giác — đó là hệ quả hình học tất yếu của cách ánh sáng truyền theo đường thẳng và hội tụ vào một điểm quan sát (mắt hoặc ống kính).

#### 1.2. Mô hình camera lỗ kim (pinhole camera)

Mô hình camera đơn giản và cơ bản nhất trong thị giác máy tính là **camera lỗ kim**: tưởng tượng một hộp kín, một mặt của hộp có một lỗ cực nhỏ (gọi là **tâm chiếu** — center of projection), mặt đối diện là mặt phẳng cảm biến/phim. Ánh sáng từ một điểm bất kỳ trong thế giới thực đi theo đường thẳng, xuyên qua lỗ kim đó, rồi chạm vào mặt phẳng cảm biến tại đúng một điểm.

Vì mọi tia sáng đều phải đi qua đúng một điểm duy nhất (lỗ kim), hình chiếu lên mặt cảm biến sẽ bị **lộn ngược** cả theo chiều dọc lẫn chiều ngang so với vật thật — giống hệt cách một chiếc camera obscura cổ điển hoạt động.

#### 1.3. Mẹo toán học: mặt phẳng ảnh ảo đặt phía trước

Để tránh phải xử lý ảnh bị lộn ngược trong mọi phép tính, quy ước chuẩn trong đồ họa máy tính và thị giác máy tính là đặt một **mặt phẳng ảnh ảo (virtual image plane)** ở **phía trước** lỗ kim (chứ không phải phía sau như mô hình vật lý thật), cách lỗ kim đúng một khoảng bằng khoảng cách tới mặt cảm biến thật. Vì hai mặt phẳng (ảo ở trước, thật ở sau) đối xứng nhau qua đúng tâm chiếu, hình chiếu lên mặt phẳng ảo sẽ **giống hệt về tỉ lệ hình học** với hình chiếu lên mặt phẳng thật, chỉ khác là **không bị lộn ngược**. Toàn bộ các công thức camera tiêu chuẩn (bao gồm cả NeRF) đều dùng quy ước mặt phẳng ảnh ảo này.

#### 1.4. Dựng công thức chiếu bằng tam giác đồng dạng

Đặt gốc tọa độ (0,0,0) trùng với tâm chiếu (tâm camera). Trục Z là trục quang học — trục đi xuyên qua tâm lỗ kim, vuông góc với mặt phẳng ảnh, theo đúng hướng camera đang nhìn. Mặt phẳng ảnh ảo đặt cách gốc tọa độ một khoảng bằng **f** (focal length — tiêu cự) dọc theo trục Z.

Xét một điểm 3D thật trong không gian, tọa độ P = (X, Y, Z), trong đó Z đóng vai trò là **độ sâu (depth)** — khoảng cách của điểm đó tới camera đo dọc theo trục quang học. Vẽ một đường thẳng nối điểm P với gốc tọa độ (tâm camera); đường thẳng này sẽ cắt mặt phẳng ảnh ảo tại một điểm có tọa độ (x_img, y_img).

Xét hai tam giác vuông đồng dạng: tam giác lớn có đáy là X (khoảng cách ngang của điểm P tới trục quang học) và chiều cao là Z (độ sâu); tam giác nhỏ có đáy là x_img và chiều cao là f. Hai tam giác này đồng dạng vì chúng chia sẻ chung một góc ở đỉnh (tại gốc tọa độ) và hai cạnh đối diện song song với nhau (vì cùng nằm trên một đường thẳng duy nhất xuyên qua gốc). Từ tính đồng dạng, tỉ lệ giữa các cạnh tương ứng phải bằng nhau:

```
x_img / f = X / Z     ⟹     x_img = f · X / Z
```

Tương tự theo trục còn lại:

```
y_img = f · Y / Z
```

Đây chính là công thức phép chiếu phối cảnh cơ bản: khi Z (độ sâu, tức khoảng cách tới camera) tăng lên, x_img giảm xuống theo tỉ lệ nghịch — đúng với quan sát trực giác ban đầu rằng "vật ở xa thì trông nhỏ hơn".

**Kiểm chứng bằng số:** giả sử f = 500, một điểm có X = 4. Nếu Z = 2 thì x_img = 500·4/2 = 1000. Nếu điểm đó dịch ra xa gấp đôi, Z = 4, thì x_img = 500·4/4 = 500 — đúng bằng một nửa giá trị trước, khớp với quy luật tỉ lệ nghịch.

#### 1.5. Từ tọa độ mặt phẳng ảnh sang tọa độ pixel

Cặp (x_img, y_img) ở trên là tọa độ hình học thuần túy, có gốc tại tâm hình học của mặt phẳng ảnh. Nhưng ảnh số lưu trữ theo **tọa độ pixel (u, v)**, với gốc nằm ở góc trên-trái của ảnh (quy ước phổ biến trong xử lý ảnh). Do đó cần dịch chuyển thêm một lượng bằng tọa độ pixel của tâm ảnh:

```
u = fx · X/Z + cx
v = fy · Y/Z + cy
```

Trong đó fx, fy là tiêu cự f quy đổi sang đơn vị pixel (có thể khác nhau nếu pixel cảm biến không hoàn toàn vuông), còn cx, cy là **principal point** — tọa độ pixel nơi trục quang học thực sự cắt qua mặt phẳng ảnh (thường gần đúng bằng tâm hình học của ảnh). Toàn bộ bốn giá trị fx, fy, cx, cy chính là bốn phần tử khác không trong ma trận nội tại **K** đã định nghĩa ở Giai đoạn 1.

### 2. Công thức pixel → hướng tia (d)

#### Chú thích ký hiệu

| Ký hiệu | Ý nghĩa |
|---|---|
| u, v | tọa độ pixel đang xét trên ảnh |
| fx, fy | tiêu cự theo đơn vị pixel, theo trục x và trục y (hai phần tử của ma trận K) |
| cx, cy | tọa độ pixel của principal point (hai phần tử của ma trận K) |
| x_cam, y_cam, z_cam | tọa độ của một điểm trên tia, biểu diễn trong hệ quy chiếu cục bộ của camera (chưa xoay sang hệ world) |
| R | ma trận xoay 3×3 của camera, đã định nghĩa ở Giai đoạn 1 |
| C | tâm camera trong hệ world, đã định nghĩa ở Giai đoạn 1 |
| d_cam | vector hướng của tia, biểu diễn trong hệ cục bộ của camera |
| d_world (hay gọi tắt là **d**) | vector hướng của tia, đã xoay sang hệ world — đại lượng thực sự dùng trong công thức tia |

#### Bài toán: đảo ngược phép chiếu

Công thức ở mục 1.5 cho biết cách tính pixel (u,v) từ một điểm 3D (X,Y,Z) đã biết trước. Nhưng bài toán ở đây là **ngược lại**: biết (u,v), cần tìm hướng của tia sáng đã tạo ra pixel đó. Đây là bài toán khó hơn vì một pixel duy nhất không xác định được một điểm 3D cụ thể — nó chỉ xác định được một **đường thẳng** (tất cả các điểm 3D nằm trên đường thẳng đó đều chiếu xuống đúng pixel (u,v)), vì công thức chiếu chỉ phụ thuộc vào **tỉ lệ** X/Z và Y/Z, không phụ thuộc giá trị tuyệt đối.

Đảo ngược công thức `u = fx·X/Z + cx` để tìm tỉ lệ:

```
X/Z = (u - cx) / fx
```

Vì chỉ biết được tỉ lệ X/Z chứ không biết X và Z riêng lẻ, ta **chọn tùy ý** một giá trị cụ thể cho Z để tính ra một điểm đại diện trên đường thẳng đó. Lựa chọn thuận tiện nhất về mặt tính toán là đặt **z_cam = -1** (giải thích dấu âm ngay bên dưới) — nghĩa là "coi như điểm đó nằm đúng trên mặt phẳng ảnh ảo, cách tâm camera một đơn vị khoảng cách theo hướng camera đang nhìn". Khi đó:

```
x_cam = (u - cx) / fx
y_cam = -(v - cy) / fy
z_cam = -1
```

#### Giải thích từng dấu trong công thức trên

- **Dấu âm ở y_cam:** tọa độ pixel v tăng dần khi đi **xuống dưới** ảnh (quy ước chuẩn của ảnh số, gốc ở góc trên-trái), trong khi trục y của hệ tọa độ camera (theo quy ước OpenGL mà NeRF sử dụng) lại hướng **lên trên**. Hai quy ước ngược chiều nhau nên cần đảo dấu để khớp.
- **z_cam = -1 (âm):** theo quy ước OpenGL dùng trong NeRF, camera nhìn theo hướng trục **-Z** (trục z âm), không phải +Z như hình vẽ ở mục 1.4 (hình vẽ đó dựng theo quy ước Z dương cho dễ hình dung tam giác đồng dạng). Do đó "cách tâm camera 1 đơn vị theo hướng đang nhìn" tương ứng với z_cam = -1, không phải +1.
- **Giá trị z_cam = -1 là lựa chọn tùy ý, không phải đo đạc:** vì mục tiêu cuối cùng chỉ là tìm **hướng** của tia (không cần vị trí chính xác trên tia), việc chọn z_cam = -2 thay vì -1 sẽ làm x_cam, y_cam tăng gấp đôi theo đúng tỉ lệ, nhưng **hướng tổng thể** (tỉ lệ x_cam : y_cam : z_cam) không đổi — nên kết quả cuối cùng (vector hướng, sau khi chuẩn hóa hoặc dùng trực tiếp trong công thức tia) không phụ thuộc vào lựa chọn này.

Vector d_cam = (x_cam, y_cam, z_cam) chính là vector hướng của tia, nhưng vẫn đang biểu diễn trong **hệ tọa độ cục bộ của camera** (giả định camera không hề xoay so với các trục world).

#### Xoay sang hệ tọa độ world

Vì camera thực tế có thể xoay theo bất kỳ hướng nào (ghi lại trong ma trận R), cần xoay vector d_cam theo đúng góc xoay đó để có được hướng thật trong không gian:

```
d_world = R · d_cam
```

Đây là phép nhân ma trận 3×3 với vector 3×1 — một phép toán đại số tuyến tính tiêu chuẩn, không có gì đặc biệt thêm. Nếu camera hoàn toàn không xoay (R là ma trận đơn vị), d_world sẽ trùng với d_cam.

Từ đây trở đi, ký hiệu **d** (không ghi chỉ số) sẽ luôn ám chỉ d_world — vector hướng đã được biểu diễn đúng trong hệ tọa độ world, sẵn sàng dùng trong công thức tia.

### 3. Công thức tia: r(t) = o + t·d

#### Chú thích ký hiệu

| Ký hiệu | Ý nghĩa |
|---|---|
| r | tên gọi của cả đường thẳng (tia) đang xét |
| r(t) | một điểm cụ thể trên tia, ứng với tham số t — là một vector tọa độ 3 chiều (x,y,z) |
| o | gốc của tia (origin) — chính là tâm camera C trong hệ world, đã biết từ Giai đoạn 1 |
| t | tham số thực (số thực bất kỳ), điều khiển vị trí trên tia |
| d | vector hướng của tia trong hệ world, tính được ở mục 2 |

#### Vì sao công thức có dạng o + t·d

Xuất phát từ ý tưởng đơn giản: đứng tại điểm o, muốn di chuyển theo hướng d. "Đi 1 bước" theo hướng d nghĩa là cộng thêm vector d vào vị trí hiện tại: vị trí mới = o + d. "Đi 2 bước" là o + d + d = o + 2d, "đi 3 bước" là o + 3d — đây chỉ là phép cộng vector lặp lại.

Đại số tuyến tính cho phép tổng quát hóa "số bước" từ số nguyên sang **bất kỳ số thực nào**, thông qua phép toán **nhân vô hướng (scalar multiplication)** — một trong các phép toán nền tảng định nghĩa không gian vector: với một số thực t bất kỳ, t·d là một vector cùng phương với d nhưng có độ dài nhân lên |t| lần (và đảo chiều nếu t âm). Nhờ phép toán này, "đi t bước" (t là số thực bất kỳ, kể cả số thập phân hoặc số âm) theo hướng d từ điểm o được viết gọn thành:

```
r(t) = o + t·d
```

#### Chứng minh công thức này thực sự vạch ra một đường thẳng

Lấy hai điểm bất kỳ trên tập hợp các điểm r(t), ứng với hai giá trị tham số t1 và t2. Vector nối hai điểm đó là:

```
r(t2) - r(t1) = (o + t2·d) - (o + t1·d) = (t2 - t1)·d
```

Kết quả then chốt: vector nối **bất kỳ hai điểm nào** trong tập hợp này luôn là một bội số vô hướng của d (chỉ khác nhau ở hệ số (t2-t1)), nghĩa là vector nối hai điểm bất kỳ luôn **cùng phương với d**, không bao giờ lệch hướng. Đây chính xác là định nghĩa toán học của tính **thẳng hàng (collinear)**: nếu vector nối mọi cặp điểm trong một tập hợp đều cùng phương với một vector cố định, tập hợp đó nằm trên đúng một đường thẳng. Vậy công thức r(t) = o + t·d được chứng minh là vạch ra đúng một đường thẳng đi qua o, theo hướng d — không phải chỉ là một định nghĩa quy ước.

### 4. Chọn điểm mẫu trên tia

#### Giới hạn khoảng lấy mẫu

Tham số t về lý thuyết chạy từ âm vô cùng tới dương vô cùng, nhưng phần cảnh có ý nghĩa chỉ nằm trong một khoảng hữu hạn. Đặt hai giá trị **t_near (tₙ)** và **t_far (t_f)** — cận gần và cận xa của vùng không gian cần quan tâm (biết trước hoặc ước lượng từ phạm vi của cảnh, ví dụ nếu biết vật thể nằm cách camera từ 2 đến 6 mét thì đặt tₙ=2, t_f=6).

#### Stratified sampling

Không thể lấy vô hạn điểm mẫu trong khoảng [tₙ, t_f] — cần chọn ra N điểm hữu hạn (N thường là 64 hoặc tương tự). Thay vì chọn N điểm cố định đều nhau (deterministic), kỹ thuật **stratified sampling** chia khoảng [tₙ, t_f] thành N đoạn con bằng nhau, rồi **lấy ngẫu nhiên đúng một điểm trong mỗi đoạn con**:

```
tᵢ = tₙ + (i + εᵢ)/N · (t_f - tₙ),     εᵢ ~ Uniform(0,1),     i = 0, 1, ..., N-1
```

trong đó εᵢ là một số thực lấy ngẫu nhiên đều trong khoảng [0,1) cho mỗi đoạn, i là chỉ số đoạn (ở đây đánh số từ 0).

Đối chiếu với công thức gốc trong paper NeRF (ký hiệu Eq. 2), paper viết dưới dạng (đánh số đoạn từ 1 đến N thay vì 0 đến N-1):

```
tᵢ ~ U[ tₙ + (i-1)/N·(t_f-tₙ) , tₙ + i/N·(t_f-tₙ) ]
```

nghĩa là lấy một mẫu phân bố đều (ký hiệu U[a,b] là phân phối đều trong khoảng [a,b]) trong đúng đoạn con thứ i. Về bản chất, đây là cùng một thuật toán với công thức ở trên, chỉ khác quy ước đánh số thứ tự đoạn (paper bắt đầu từ 1, cách viết thông dụng khác bắt đầu từ 0) — không có khác biệt gì về mặt thuật toán hay kết quả.

#### Vì sao không dùng một lưới điểm cố định

Nếu dùng cùng một tập vị trí t cố định, không thay đổi, cho mọi lần render (gọi là deterministic quadrature — phép cầu phương tất định), biểu diễn cảnh về bản chất sẽ bị giới hạn: mạng MLP chỉ từng được "hỏi" tại đúng N vị trí rời rạc cố định đó trong suốt quá trình tối ưu — giống hệt hạn chế vốn có của một voxel grid rời rạc (độ phân giải bị giới hạn bởi số ô lưới cố định). Ngược lại, vì stratified sampling lấy mẫu **ngẫu nhiên khác nhau mỗi lần** (mỗi vòng lặp huấn luyện, mỗi lần render), qua suốt quá trình tối ưu, mạng MLP được đánh giá tại **vô số vị trí liên tục khác nhau** trong khoảng [tₙ, t_f] — đây chính là cơ chế cho phép NeRF biểu diễn một hàm số **liên tục** của không gian, dù việc tính toán thực tế vẫn chỉ dùng một tập hữu hạn N điểm mẫu ở mỗi lần đánh giá.

### 5. Positional Encoding

#### Chú thích ký hiệu

| Ký hiệu | Ý nghĩa |
|---|---|
| p | một giá trị tọa độ vô hướng bất kỳ cần mã hóa (ví dụ một trong ba thành phần x, y, z của vị trí, hoặc một trong ba thành phần của vector hướng d) |
| γ(·) | hàm positional encoding, ánh xạ một số thực sang một vector nhiều chiều |
| L | số mức tần số dùng trong γ(·) — một siêu tham số (hyperparameter) cố định, chọn trước khi huấn luyện |
| γ(x) | kết quả áp dụng γ(·) lên toàn bộ ba thành phần của vị trí x = (x,y,z) |
| γ(d) | kết quả áp dụng γ(·) lên toàn bộ ba thành phần của hướng nhìn d |

#### Vấn đề cần giải quyết: vì sao cần positional encoding

Nếu đưa trực tiếp tọa độ (x,y,z,θ,φ) — những con số có giá trị liên tục thông thường — vào mạng MLP mà không qua biến đổi nào, kết quả render ra sẽ kém ở việc biểu diễn các chi tiết biến thiên nhanh (tần số cao) về màu sắc và hình học — ảnh sinh ra bị mờ, thiếu chi tiết nhỏ.

Hiện tượng này liên quan tới một phát hiện về mạng nơ-ron sâu nói chung: mạng có xu hướng thiên lệch (bias) về việc học các hàm biến thiên **chậm (tần số thấp)** trước, và gặp khó khăn hơn khi phải học các hàm biến thiên **nhanh (tần số cao)** — gọi là hiện tượng **spectral bias**. Một cách khắc phục đã được chứng minh hiệu quả: ánh xạ input sang một không gian **nhiều chiều hơn**, dùng các hàm có tần số cao (như sin, cos ở nhiều tần số khác nhau), **trước khi** đưa vào mạng — việc này giúp mạng dễ dàng khớp (fit) với dữ liệu có biến thiên tần số cao hơn.

#### Công thức đầy đủ

```
γ(p) = ( sin(2⁰πp), cos(2⁰πp), sin(2¹πp), cos(2¹πp), ..., sin(2^(L-1)πp), cos(2^(L-1)πp) )
```

Hàm này nhận vào một số thực p (đã chuẩn hóa về khoảng [-1,1]) và trả về một vector gồm 2L số — với mỗi mức tần số từ 2⁰ đến 2^(L-1), tính cả giá trị sin và cos của (tần số đó nhân với πp).

Hàm γ(·) được áp dụng **riêng biệt** cho từng thành phần trong ba tọa độ của vị trí x (đã chuẩn hóa về [-1,1]) và cho từng thành phần trong ba thành phần của vector hướng nhìn d (vốn đã nằm trong [-1,1] theo cách xây dựng, vì là vector đơn vị).

#### Giá trị L và số chiều kết quả

Trong triển khai thực tế, L = 10 được dùng cho γ(x) (vị trí), và L = 4 được dùng cho γ(d) (hướng nhìn) — hai giá trị L khác nhau cho hai loại input.

Tính số chiều cụ thể: với γ(x), mỗi một trong ba tọa độ x,y,z qua hàm γ(·) với L=10 sẽ cho ra 2×10 = 20 số; vì có ba tọa độ nên tổng số chiều của γ(x) là 3×20 = **60 chiều**. Với γ(d), mỗi một trong ba thành phần của d qua hàm γ(·) với L=4 cho ra 2×4 = 8 số; tổng số chiều của γ(d) là 3×8 = **24 chiều**.

#### Phân biệt với positional encoding trong Transformer

Cùng một công thức toán học (dùng sin/cos ở nhiều tần số) cũng xuất hiện trong kiến trúc **Transformer** nổi tiếng, nơi nó cũng được gọi là "positional encoding" — nhưng **mục đích hoàn toàn khác**. Trong Transformer, công thức này dùng để cung cấp thông tin về **vị trí rời rạc của từng token trong một chuỗi** (ví dụ từ thứ 1, thứ 2, thứ 3... trong câu), vì bản thân kiến trúc Transformer không có khái niệm thứ tự tuần tự. Trong NeRF, cùng công thức đó được dùng để ánh xạ **tọa độ không gian liên tục** sang một không gian chiều cao hơn, với mục đích giúp mạng MLP dễ dàng xấp xỉ các hàm biến thiên tần số cao hơn — không liên quan gì tới khái niệm "vị trí trong chuỗi".

### Kết quả của Giai đoạn 2 — chuyển tiếp sang Giai đoạn 3

Sau các bước trên, với mỗi pixel (u,v) ban đầu, ta đã có được N bộ dữ liệu (một bộ cho mỗi điểm mẫu trên tia), mỗi bộ gồm: vị trí 3D r(tᵢ) = (x,y,z) đã qua positional encoding thành γ(x) 60 chiều, và hướng nhìn d đã qua positional encoding thành γ(d) 24 chiều (giống nhau cho cả N điểm, vì mọi điểm trên cùng một tia chia sẻ chung một hướng d). Toàn bộ N bộ (γ(x), γ(d)) này giờ đã sẵn sàng để đưa vào mạng MLP — nội dung của Giai đoạn 3: Forward Pass qua MLP & Volume Rendering.


---

## Giai đoạn 3: Forward Pass qua MLP & Volume Rendering

Sau Giai đoạn 2, với mỗi tia ta đã có N bộ (γ(x),γ(d)) — tọa độ vị trí và hướng nhìn của N điểm mẫu, đã qua positional encoding, sẵn sàng đưa vào mạng nơ-ron. Giai đoạn này mô tả: (1) mạng nơ-ron F xử lý các bộ đó ra sao để cho ra (màu, density) tại từng điểm, và (2) cách cộng dồn N bộ (màu, density) đó thành đúng 1 màu pixel dự đoán Ĉ(r).

### 3.1. Hàm F(x,y,z,θ,φ) → (r,g,b,σ) là gì

**Không phải công thức đóng.** F không có dạng viết tay kiểu y=ax+b — nó là 1 **mạng nơ-ron** (hàng trăm nghìn trọng số số thực), chỉ tính được bằng cách cho input chạy tuần tự qua các lớp của mạng. "F(x,y,z,θ,φ)→(r,g,b,σ)" chỉ là cách viết gọn thể hiện: mạng nhận 5 số input, trả về 4 số output.

**Ý nghĩa tên gọi "radiance field" (trường bức xạ):** trong vật lý, một "trường" (field) là hàm gán 1 giá trị cho **mọi điểm** trong không gian (ví dụ trường nhiệt độ: mỗi điểm trong phòng có 1 nhiệt độ). F gán (màu, density) cho mọi điểm (x,y,z) kết hợp mọi hướng nhìn (θ,φ) trong không gian cảnh — đó là "trường bức xạ": tại mỗi điểm, theo mỗi hướng, cảnh phát ra ánh sáng màu gì. Neural Radiance Field = trường bức xạ được biểu diễn bởi mạng nơ-ron.

**Vì sao phải học F chứ không viết tay:** không ai biết trước "cảnh có hình dạng/màu gì" bằng công thức có sẵn — đó chính là thứ cần tìm ra từ ảnh. Việc này khả thi nhờ **universal function approximator** (định lý xấp xỉ phổ quát): một mạng nơ-ron feedforward đủ lớn (đủ số lớp, đủ số kênh mỗi lớp) có thể xấp xỉ **bất kỳ hàm liên tục nào** trên một miền compact, với sai số nhỏ tùy ý. Nhờ tính chất này, không cần biết trước dạng hàm đúng của cảnh — chỉ cần chọn kiến trúc đủ lớn rồi dùng dữ liệu (ảnh quan sát) để "chỉnh" trọng số sao cho F khớp với thực tế.

### 3.2. Kiến trúc MLP 8 lớp — chi tiết từng bước, đầy đủ số chiều

#### Một lớp Fully-Connected (FC) là phép toán gì

```
output = activation(W · input + b)
```

| Ký hiệu | Ý nghĩa |
|---|---|
| **input** | vector số thực đưa vào lớp (kích thước = số kênh lớp trước) |
| **W** | ma trận trọng số (trainable) — kích thước (số_kênh_ra × số_kênh_vào) |
| **b** | vector bias (trainable) — kích thước (số_kênh_ra) |
| **activation** | hàm phi tuyến áp lên từng phần tử của (W·input+b) |
| **output** | vector kết quả — kích thước = số kênh lớp này |

Nếu không có activation (phi tuyến), xếp chồng nhiều lớp FC tương đương với đúng 1 lớp tuyến tính duy nhất (tích các ma trận tuyến tính vẫn là tuyến tính) — activation là thứ cho phép mạng biểu diễn được hàm phi tuyến phức tạp.

**ReLU** (Rectified Linear Unit): `ReLU(x) = max(0,x)` — giữ nguyên giá trị dương, cắt về 0 với giá trị âm. Dùng cho các lớp ẩn vì tính toán rẻ, gradient không bị "triệt tiêu" (vanishing gradient) như các hàm sigmoid/tanh ở vùng giá trị lớn.

**Sigmoid**: `Sigmoid(x) = 1/(1+e^(-x))` — luôn cho ra giá trị trong khoảng (0,1) dù input là bất kỳ số thực nào.

#### Sơ đồ đầy đủ với số chiều cụ thể

Input: γ(x) có 60 chiều (L=10 → mỗi tọa độ x,y,z sinh 2×10=20 số → 3×20=60).

| Bước | Input → Output | Phép toán |
|---|---|---|
| Lớp 1 | 60 → 256 | FC + ReLU |
| Lớp 2 | 256 → 256 | FC + ReLU |
| Lớp 3 | 256 → 256 | FC + ReLU |
| Lớp 4 | 256 → 256 | FC + ReLU |
| **Skip connection** | ghép γ(x) (60) vào output lớp 4 (256) | concatenate → 316 |
| Lớp 5 | 316 → 256 | FC + ReLU |
| Lớp 6 | 256 → 256 | FC + ReLU |
| Lớp 7 | 256 → 256 | FC + ReLU |
| Lớp 8 | 256 → 256 | FC (nhánh σ thường không qua ReLU) |

Sau lớp 8, output 256 chiều **rẽ làm 2 nhánh dùng chung input đó**:

**Nhánh density:**
```
σ = FC(256 → 1)
```
Chỉ nhận đúng 256 số xuất phát hoàn toàn từ γ(x) — **không có γ(d) lẫn vào** ở nhánh này.

**Nhánh màu:** giữ nguyên vector đặc trưng 256 chiều, ghép thêm γ(d) (L=4 → 3×2×4=24 chiều):

```
256 (đặc trưng) + 24 (γ(d)) = 280 chiều
```

| Bước | Input → Output | Phép toán |
|---|---|---|
| FC nhỏ | 280 → 128 | FC + ReLU |
| Lớp cuối | 128 → 3 | FC + **Sigmoid** |

Output cuối: 3 số (r,g,b).

**Lưu ý nguồn:** chi tiết "skip connection nối lại ở đúng lớp thứ 5" đến từ **code triển khai công bố của nhóm tác giả** (repository chính thức), không phải trích trực tiếp từ văn bản paper — văn bản chính của paper chỉ ghi "8 lớp fully-connected, 256 kênh, ReLU" mà không nêu rõ vị trí chính xác của skip connection. Khi trích dẫn cho báo cáo nên ghi rõ nguồn là "theo code công bố", không gán cho chính văn bản paper.

#### Vì sao Sigmoid ở lớp cuối, không dùng ReLU

ReLU chỉ chặn **dưới** ở 0 (không chặn trên) — output có thể là bất kỳ số dương lớn nào, không hợp lệ làm giá trị màu RGB chuẩn hóa (cần nằm trong [0,1]). Sigmoid ép output luôn nằm **chính xác trong (0,1)** bất kể giá trị input trước đó lớn/nhỏ ra sao — khớp đúng yêu cầu của giá trị màu, không cần cắt ngưỡng thủ công.

#### Vì sao σ tách khỏi hướng nhìn, màu thì không

**Ràng buộc thiết kế có chủ đích**, phục vụ tính **nhất quán đa góc nhìn (multiview consistency)**: hình dạng vật lý của 1 vật thể (density/σ tại 1 điểm) không thay đổi tùy theo bạn đứng ở đâu quan sát nó — cái ly vẫn ở đúng vị trí đó dù nhìn từ trái hay phải. Vì vậy σ chỉ được phép phụ thuộc **vị trí** (γ(x)), không được phép phụ thuộc **hướng nhìn** (γ(d)) — kiến trúc mạng ép buộc điều này bằng cách tách nhánh σ ra trước khi γ(d) được đưa vào.

Ngược lại, **màu quan sát được** tại 1 điểm có thể thay đổi theo góc nhìn — hiện tượng **view-dependent** (hay **non-Lambertian**): bề mặt bóng, kim loại, phản chiếu ánh sáng khác nhau tùy góc nhìn (ví dụ ánh phản chiếu đặc trưng - specular highlight - di chuyển vị trí khi bạn di chuyển đầu). Vì vậy nhánh màu được phép nhận cả γ(x) (qua vector đặc trưng 256 chiều) **và** γ(d) — cho phép mạng mô phỏng hiệu ứng này.

### 3.3. Volume Rendering — từ N bộ (màu, density) ra 1 màu pixel

#### Định nghĩa chính xác của σ(x)

σ(x) được định nghĩa là **xác suất vi phân (differential probability)** để một tia kết thúc (bị hấp thụ) tại một hạt vô cùng nhỏ ở vị trí x. Đây là định nghĩa chuẩn — không chỉ là "độ đặc" theo nghĩa thông thường, mà là **tốc độ hấp thụ ánh sáng tức thời** tại điểm đó: σ càng lớn, xác suất một tia đi ngang qua điểm đó bị chặn đứng ngay tại đó càng cao.

#### Công thức tích phân liên tục

```
C(r) = ∫ₜₙ^t_f  T(t) · σ(r(t)) · c(r(t),d)  dt ,   T(t) = exp( -∫ₜₙ^t σ(r(s)) ds )
```

**Chú thích ký hiệu:**

| Ký hiệu | Ý nghĩa |
|---|---|
| C(r) | màu pixel kỳ vọng (expected color) của tia r |
| tₙ, t_f | cận gần (near) và cận xa (far) của đoạn tia cần xét |
| T(t) | **transmittance tích lũy** — xác suất tia đi được từ tₙ tới t mà không va chạm/bị hấp thụ bởi hạt nào dọc đường |
| σ(r(t)) | density tại điểm r(t) trên tia (định nghĩa ở trên) |
| c(r(t),d) | màu phát xạ tại điểm r(t), theo đúng hướng nhìn d |
| dt | độ rộng vi phân (vô cùng nhỏ) của 1 "lát cắt" trên tia |

**Đọc công thức theo nghĩa vật lý:** với mỗi lát cắt vô cùng mỏng tại t (bề rộng dt), đóng góp của nó vào màu pixel cuối = (xác suất ánh sáng từ lát đó **tới được** camera, tức T(t)) × (xác suất lát đó **hấp thụ/phát** ánh sáng, tức σ(r(t))) × (màu phát ra tại đó, tức c(r(t),d)) × (độ rộng lát, dt). Tích phân = cộng dồn liên tục đóng góp của mọi lát cắt từ tₙ tới t_f.

#### Derive T(t) từ phương trình vi phân — vì sao có dạng exp(-∫σds)

Tốc độ ánh sáng **mất đi** khi đi thêm 1 đoạn dt tỉ lệ thuận với (a) lượng ánh sáng còn lại hiện tại T(t), và (b) mật độ hấp thụ tại đó σ(r(t)):

```
dT/dt = -σ(r(t)) · T(t)
```

Đây là phương trình vi phân tuyến tính bậc 1 dạng **suy giảm mũ** (exponential decay) — cùng dạng với phân rã phóng xạ hay hấp thụ ánh sáng qua môi trường (định luật Beer-Lambert). Giải phương trình này với điều kiện đầu T(tₙ)=1 (tại điểm gần nhất, ánh sáng còn nguyên vẹn 100%, chưa bị hấp thụ gì):

```
T(t) = exp( -∫ₜₙ^t σ(r(s)) ds )
```

Đây là **nghiệm toán học chính xác** của phương trình vi phân trên — không phải công thức đặt ra tùy ý.

#### Công thức rời rạc — cách thực sự tính được bằng máy tính

Tích phân liên tục không tính trực tiếp được (σ là output của mạng nơ-ron tại vô số điểm liên tục, không có công thức giải tích đóng). Ước lượng bằng N điểm mẫu rời rạc trên tia (t₁,...,t_N, lấy theo stratified sampling đã học ở Giai đoạn 2):

```
Ĉ(r) = Σᵢ₌₁^N  Tᵢ · αᵢ · cᵢ  ,   Tᵢ = exp( -Σⱼ<ᵢ σⱼδⱼ ) ,   αᵢ = 1 - exp(-σᵢδᵢ)
```

**Chú thích ký hiệu:**

| Ký hiệu | Ý nghĩa |
|---|---|
| δᵢ | khoảng cách giữa 2 điểm mẫu liên tiếp, δᵢ = tᵢ₊₁ − tᵢ |
| αᵢ | "độ chặn sáng" của đoạn thứ i — xác suất đoạn đó hấp thụ ánh sáng (dẫn từ định luật Beer-Lambert: xác suất sống sót qua đoạn dày δ, mật độ σ là exp(-σδ); xác suất bị chặn = 1 trừ đi) |
| Tᵢ | transmittance rời rạc — tích các xác suất sống sót của mọi đoạn trước i |
| cᵢ, σᵢ | màu và density tại điểm mẫu thứ i (output của MLP, mục 3.2) |

**Chứng minh công thức rời rạc là xấp xỉ của tích phân liên tục (tổng Riemann):** khi δᵢ nhỏ, dùng xấp xỉ toán học `1-exp(-x) ≈ x` (khai triển Taylor bậc 1 quanh x=0):

```
αᵢ = 1-exp(-σᵢδᵢ) ≈ σᵢ·δᵢ    (khi δᵢ→0)
```

Thay vào: `Ĉ(r) = Σᵢ Tᵢ·σᵢ·cᵢ·δᵢ` — đây chính xác là dạng **tổng Riemann** (giá trị hàm tại từng điểm nhân bề rộng đoạn, cộng lại) dùng để định nghĩa tích phân. Khi số điểm N→∞ (δ→0), tổng này tiến tới đúng `∫T(t)σ(r(t))c(r(t),d)dt`. Nói cách khác: công thức rời rạc không phải một công thức khác — nó là xấp xỉ số của đúng công thức tích phân liên tục ở trên, với N hữu hạn điểm mẫu thay vì vô hạn.

#### Ví dụ số minh họa — occlusion (che khuất) tự học được

3 điểm mẫu trên 1 tia, mỗi đoạn δ=1:

| i | σᵢ | màu cᵢ | ý nghĩa | Tᵢ | αᵢ | đóng góp Tᵢ·αᵢ·cᵢ |
|---|---|---|---|---|---|---|
| 1 (gần camera) | 0.1 | đỏ (1,0,0) | không khí loãng | 1 | 0.095 | (0.095, 0, 0) |
| 2 (giữa) | 2.0 | xanh lá (0,1,0) | bề mặt vật thể (đặc) | 0.905 | 0.865 | (0, 0.783, 0) |
| 3 (xa nhất) | 0.1 | xanh dương (0,0,1) | vật phía sau bề mặt | 0.1225 | 0.095 | (0, 0, 0.012) |

Tính:
- T₁ = exp(0) = 1 (không có gì chặn trước nó). α₁ = 1−exp(−0.1) ≈ 0.095.
- T₂ = exp(−0.1) ≈ 0.905. α₂ = 1−exp(−2.0) ≈ 0.865.
- T₃ = exp(−(0.1+2.0)) = exp(−2.1) ≈ 0.1225. α₃ = 1−exp(−0.1) ≈ 0.095.

**C(r) ≈ (0.095, 0.783, 0.012)** — gần như thuần xanh lá. Điểm 2 (bề mặt đặc) gần như quyết định toàn bộ màu pixel — đúng logic vật lý: đó là bề mặt thật sự "nhìn thấy được". Điểm 3 (nằm phía sau bề mặt đặc đó) gần như không đóng góp gì (chỉ 0.012) vì T₃ đã tụt rất thấp sau khi "xuyên qua" đoạn 2 đặc.

**Điểm mấu chốt:** NeRF tự học được khái niệm che khuất (occlusion) mà không cần ai dạy nó luật hình học nào cả — chỉ cần công thức Tᵢ·αᵢ này, mạng tự động học ra: muốn ảnh dự đoán khớp ảnh thật, nó phải đặt σ lớn đúng tại bề mặt thật của vật thể, và điều đó tự động làm những gì phía sau bị "che" trong công thức, không cần lập trình quy tắc che khuất một cách tường minh.

---

Tới đây, với mỗi tia, ta đã có Ĉ(r) tính từ mạng "coarse" dùng stratified sampling đơn thuần (N_c điểm lấy đều). Nhưng cách lấy mẫu đều này lãng phí: phần lớn tia là khoảng không (σ≈0), chỉ vài đoạn ngắn quanh bề mặt vật thể mới thực sự quan trọng. Giai đoạn 4 trình bày cách lấy mẫu thông minh hơn (hierarchical sampling, dùng chính các trọng số Tᵢαᵢ vừa tính được ở đây để "chỉ đường"), công thức hàm loss, và toàn bộ vòng lặp huấn luyện.


---

## Giai đoạn 4: Hierarchical Sampling, Hàm Loss & Vòng lặp Training

Ở Giai đoạn 3, mạng "coarse" đã cho ra màu dự đoán Ĉ(r) bằng cách lấy mẫu đều (stratified sampling) dọc tia rồi volume rendering. Giai đoạn này giải quyết 2 vấn đề còn lại: lấy mẫu sao cho **hiệu quả hơn** (hierarchical sampling), và **train** mạng như thế nào để nó thực sự học đúng cảnh.

### 1. Vấn đề cần giải quyết — stratified sampling đơn thuần lãng phí ở đâu

Nhắc lại ví dụ 3 điểm mẫu ở Giai đoạn 3: trên 1 tia, chỉ điểm nằm đúng bề mặt vật thể (σ lớn) đóng góp đáng kể vào màu cuối (~88% trọng số), 2 điểm còn lại (không khí trước/sau bề mặt) gần như không đóng góp gì. Nếu lấy N_c điểm dàn đều khắp [tₙ, t_f] (stratified sampling, Giai đoạn 2), phần lớn điểm sẽ rơi vào vùng "không khí" vô ích, trong khi vùng bề mặt mỏng — nơi quyết định màu pixel — chỉ được 1-2 điểm "chạm trúng" một cách tình cờ. Đây là lãng phí tính toán: cùng 1 ngân sách N điểm, phần lớn bị "phí" vào chỗ không quan trọng.

**Ý tưởng:** thay vì lấy mẫu đều khắp, hãy **tập trung lấy mẫu dày hơn ở những chỗ có khả năng cao là bề mặt thật** (σ lớn), và thưa hơn ở vùng không khí. Nhưng vấn đề là: trước khi chạy mạng, làm sao biết trước chỗ nào có bề mặt? → Giải pháp: chạy 1 mạng "thô" trước để **dò đường**, rồi dùng kết quả đó hướng dẫn việc lấy mẫu tiếp theo.

### 2. Kiến trúc 2 mạng, 2 lượt lấy mẫu

#### Lượt 1 — Mạng "coarse" (thô)

Lấy **N_c** điểm dàn đều theo stratified sampling (công thức đã có ở Giai đoạn 2), chạy qua mạng coarse, thu được tập (σᵢ, cᵢ) cho từng điểm — đây chính xác là bước đã làm ở Giai đoạn 3.

Từ các giá trị (σᵢ, cᵢ) đó, tính 1 đại lượng mới gọi là **trọng số** wᵢ:

```
wᵢ = Tᵢ · αᵢ = Tᵢ · (1 − exp(−σᵢδᵢ))
```

**Bảng chú thích ký hiệu:**

| Ký hiệu | Ý nghĩa | Nguồn gốc |
|---|---|---|
| wᵢ | trọng số (weight) của điểm mẫu thứ i | đại lượng mới, tính từ Tᵢ và αᵢ |
| Tᵢ | transmittance tích lũy tới điểm i (xác suất ánh sáng "sống sót" tới được điểm i mà chưa va chạm gì trước đó) | đã định nghĩa ở Giai đoạn 3 |
| αᵢ = 1−exp(−σᵢδᵢ) | độ "chặn sáng" (opacity) của đoạn i | đã định nghĩa ở Giai đoạn 3 |
| σᵢ | density tại điểm mẫu i | đã định nghĩa ở Giai đoạn 3 |
| δᵢ = tᵢ₊₁ − tᵢ | khoảng cách giữa 2 điểm mẫu liên tiếp | đã định nghĩa ở Giai đoạn 3 |

**Quan sát quan trọng:** wᵢ chính là **số hạng trong công thức volume rendering** Ĉ(r)=Σᵢ Tᵢαᵢcᵢ, nhưng **bỏ màu cᵢ ra** — tức wᵢ đo "điểm này đóng góp/quan trọng bao nhiêu vào màu cuối cùng", không quan tâm màu cụ thể là gì. Lấy lại ví dụ 3 điểm ở Giai đoạn 3 (w₁=0.095, w₂=0.783, w₃=0.012): điểm 2 (bề mặt thật) có w cao vượt trội — đây chính là tín hiệu để biết "nên lấy mẫu dày quanh đây".

#### Lượt 2 — Lấy mẫu theo trọng số (Importance Sampling)

**Chuẩn hóa trọng số** thành 1 phân phối xác suất:

```
ŵᵢ = wᵢ / Σⱼ₌₁^Nc wⱼ
```

| Ký hiệu | Ý nghĩa |
|---|---|
| ŵᵢ | trọng số đã chuẩn hóa (normalized weight) của điểm i — 1 số trong [0,1], tổng tất cả ŵᵢ = 1 |
| Σⱼ wⱼ | tổng tất cả trọng số wᵢ của N_c điểm (dùng làm mẫu số để chuẩn hóa) |

Với ví dụ 3 điểm: tổng w ≈ 0.095+0.783+0.012 = 0.89 → ŵ₁≈0.107, ŵ₂≈0.880, ŵ₃≈0.013. Điểm 2 chiếm tới 88% "xác suất quan trọng".

Tập hợp {ŵᵢ} này, gắn với các khoảng [tᵢ, tᵢ₊₁] tương ứng, tạo thành 1 **PDF dạng hằng số từng đoạn** (piecewise-constant probability density function) dọc theo tia — tức là 1 hàm mật độ xác suất không đổi trong mỗi đoạn nhỏ [tᵢ,tᵢ₊₁], nhưng giá trị khác nhau giữa các đoạn.

| Ký hiệu | Ý nghĩa |
|---|---|
| PDF (Probability Density Function) | hàm mật độ xác suất — ở đây mô tả "khả năng 1 điểm quan trọng nằm ở vị trí t nào dọc tia", xây từ {ŵᵢ} |
| piecewise-constant | "hằng số từng đoạn" — giá trị PDF không đổi trong mỗi đoạn [tᵢ,tᵢ₊₁], nhưng nhảy bậc giữa các đoạn khác nhau |

**Lấy mẫu từ PDF này bằng Inverse Transform Sampling:**

1. Dựng **CDF** (Cumulative Distribution Function — hàm phân phối tích lũy) từ PDF: CDFₖ = Σᵢ₌₁^k ŵᵢ — tức cộng dồn các ŵᵢ theo thứ tự, cho biết "xác suất điểm quan trọng nằm trước hoặc tại đoạn k".
2. Sinh N_f số ngẫu nhiên **u** theo phân phối đều Uniform(0,1).
3. Với mỗi số u, "tra ngược" qua CDF: tìm đoạn k sao cho CDFₖ₋₁ ≤ u < CDFₖ, rồi nội suy ra vị trí t cụ thể trong đoạn đó.

| Ký hiệu | Ý nghĩa |
|---|---|
| CDF (Cumulative Distribution Function) | hàm phân phối tích lũy — tổng dồn của PDF, tăng dần từ 0 đến 1 |
| N_f | số điểm mẫu mới lấy thêm ở lượt 2 |
| u ~ Uniform(0,1) | số ngẫu nhiên sinh đều trong khoảng [0,1] |
| inverse transform sampling | kỹ thuật lấy mẫu: sinh số ngẫu nhiên đều, rồi "tra ngược" qua CDF để được mẫu theo đúng phân phối PDF mong muốn — kỹ thuật thống kê chuẩn, không phải phát minh riêng của NeRF |

**Kết quả:** N_f điểm mới sinh ra, **tự động tập trung dày đặc** quanh các đoạn có ŵ cao (tức quanh vùng nghi là bề mặt vật thể), thưa thớt ở vùng ŵ thấp (không khí) — đúng mục tiêu đặt ra ở mục 1.

#### Lượt 3 — Mạng "fine" (tinh)

Gộp **N_c điểm cũ** (từ lượt 1) với **N_f điểm mới** (từ lượt 2), sắp xếp lại toàn bộ theo thứ tự t tăng dần, rồi đưa **toàn bộ N_c+N_f điểm** này qua 1 mạng **riêng biệt** gọi là mạng "fine" (không tái sử dụng trọng số của mạng coarse). Chạy lại volume rendering (công thức Giai đoạn 3) trên tập điểm đầy đủ này, thu được màu dự đoán cuối cùng:

```
Ĉ_f(r)
```

— đây là màu render "chính thức" cuối cùng của tia r, chính xác hơn Ĉ_c(r) vì tập trung tài nguyên tính toán đúng chỗ quan trọng.

### 3. Lưu ý quan trọng — Hierarchical Sampling KHÔNG phải Importance Sampling đúng nghĩa thống kê

Dễ nhầm lẫn: trong thống kê, **importance sampling** đúng nghĩa là kỹ thuật ước lượng 1 tích phân/kỳ vọng bằng cách lấy mẫu theo 1 phân phối "khôn ngoan" (không đều), sau đó **chia lại (reweight)** mỗi mẫu bằng hệ số 1/pdf(mẫu đó) để đảm bảo kết quả ước lượng cuối cùng **không chệch** (unbiased) so với lấy mẫu đều.

NeRF **không làm bước chia lại trọng số 1/pdf này**. Thay vào đó, N_c+N_f điểm sau khi gộp được đưa thẳng vào công thức volume rendering tiêu chuẩn (Ĉ_f(r)=Σ Tᵢαᵢcᵢ) như thể chúng là 1 tập mẫu bình thường — tức là **coi N_c+N_f điểm này như 1 cách rời rạc hóa không đồng đều (nonuniform discretization) của toàn miền tích phân [tₙ,t_f]**, chứ không coi mỗi điểm là 1 ước lượng xác suất độc lập cho toàn bộ tích phân.

Nói cách khác: mục tiêu của hierarchical sampling trong NeRF là "chọn đúng vị trí lấy mẫu để xấp xỉ tích phân tốt hơn" (giống tinh thần importance sampling), nhưng cách tính kết quả cuối cùng vẫn là phép cầu phương (quadrature) tiêu chuẩn trên tập điểm không đều đó, không phải công thức ước lượng kỳ vọng có reweight của importance sampling thống kê. Phân biệt này không ảnh hưởng gì đến cách cài đặt thực tế (vẫn làm đúng 3 lượt đã mô tả), chỉ là điểm cần biết để tránh hiểu nhầm thuật ngữ khi đọc thêm tài liệu thống kê.

### 4. Hàm Loss — huấn luyện cả 2 mạng cùng lúc

```
L = Σ_{r∈R} [ ‖Ĉ_c(r) − C(r)‖₂² + ‖Ĉ_f(r) − C(r)‖₂² ]
```

**Bảng chú thích ký hiệu:**

| Ký hiệu | Ý nghĩa |
|---|---|
| L | giá trị loss tổng, cần tối thiểu hóa qua quá trình train |
| R | tập hợp các tia **trong 1 batch** hiện tại (không phải toàn bộ ảnh — chỉ 1 phần được chọn ngẫu nhiên mỗi vòng lặp, xem mục 6) |
| r ∈ R | 1 tia cụ thể trong tập R |
| C(r) | màu pixel **thật** (ground truth) tương ứng với tia r, lấy từ ảnh gốc đã chụp |
| Ĉ_c(r) | màu dự đoán từ mạng **coarse** (Giai đoạn 3) |
| Ĉ_f(r) | màu dự đoán từ mạng **fine** (mục 2, Lượt 3) |
| ‖·‖₂² | bình phương chuẩn Euclid — với vector màu (r,g,b), bằng (Δr)²+(Δg)²+(Δb)² |

Đây chính là hàm **MSE** (Mean Squared Error — sai số bình phương trung bình) quen thuộc, nhưng tính **cộng gộp cho cả 2 nhánh** coarse và fine, trên **cùng 1** màu thật C(r).

**Vì sao vẫn tối thiểu hóa cả Ĉ_c(r) dù kết quả cuối cùng chỉ lấy Ĉ_f(r):** vì mạng coarse **không chỉ là bước trung gian bỏ đi** — nó quyết định trọng số wᵢ, từ đó quyết định **vị trí** lấy N_f mẫu bổ sung cho mạng fine (mục 2, Lượt 2). Nếu không train mạng coarse (hoặc train tệ), nó sẽ dự đoán σ sai lệch, dẫn tới trọng số wᵢ sai, khiến lượt lấy mẫu thứ 2 tập trung **sai chỗ** (ví dụ tập trung vào vùng không khí thay vì bề mặt thật) — làm hỏng luôn cả chất lượng của mạng fine dù bản thân mạng fine có kiến trúc tốt. Do đó, loss phải ép cả 2 mạng cùng học tốt — đây là 1 dạng **huấn luyện đa nhiệm (multi-task)** ẩn: mạng coarse vừa phải tự dự đoán đúng màu, vừa phải "dẫn đường" tốt cho mạng fine.

### 5. Siêu tham số thực nghiệm (Hyperparameters)

| Siêu tham số | Giá trị | Ý nghĩa |
|---|---|---|
| Batch size | 4096 tia | số tia xử lý đồng thời trong 1 vòng lặp cập nhật trọng số |
| N_c | 64 | số điểm mẫu cho mạng coarse (stratified sampling) |
| N_f | 128 | số điểm mẫu **bổ sung** cho mạng fine (tổng N_c+N_f=192 điểm khi chạy mạng fine) |
| Optimizer | Adam | thuật toán tối ưu dựa trên gradient, có "đà" (momentum) + điều chỉnh learning rate thích ứng theo từng tham số |
| β1 | 0.9 | hệ số làm mượt (decay rate) cho ước lượng mô-men bậc 1 (trung bình trượt của gradient) trong Adam |
| β2 | 0.999 | hệ số làm mượt cho ước lượng mô-men bậc 2 (trung bình trượt của bình phương gradient) trong Adam |
| ε | 10⁻⁷ | hằng số nhỏ cộng vào mẫu số trong công thức Adam, tránh chia cho 0 |
| Learning rate | bắt đầu 5×10⁻⁴, giảm dần theo hàm mũ (exponential decay) xuống 5×10⁻⁵ | tốc độ học — giảm dần qua quá trình train giúp hội tụ ổn định hơn ở giai đoạn cuối |
| Số vòng lặp | 100.000 – 300.000 vòng | số lần cập nhật trọng số tới khi mạng hội tụ (tùy độ phức tạp của scene) |
| Thời gian train | ~1–2 ngày | trên 1 GPU NVIDIA V100, cho 1 scene |

### 6. Quy trình 1 vòng lặp train — tóm tắt toàn bộ

1. **Lấy batch tia ngẫu nhiên:** chọn ngẫu nhiên 4096 pixel từ **toàn bộ** ảnh trong dataset (không phải lấy hết pixel của 1 ảnh — các tia trong cùng 1 batch có thể đến từ nhiều ảnh khác nhau), mỗi pixel ứng với 1 tia (công thức r(t)=o+t·d, Giai đoạn 2).
2. **Mạng coarse:** với mỗi tia, lấy N_c=64 điểm theo stratified sampling → chạy qua mạng coarse → có (σᵢ,cᵢ) cho từng điểm → volume rendering → Ĉ_c(r).
3. **Hierarchical sampling:** từ kết quả coarse, tính trọng số wᵢ, chuẩn hóa thành PDF, lấy thêm N_f=128 điểm bằng inverse transform sampling → gộp với 64 điểm cũ thành 192 điểm.
4. **Mạng fine:** chạy toàn bộ 192 điểm qua mạng fine → volume rendering → Ĉ_f(r).
5. **Cập nhật trọng số:** tính loss L (mục 4) trên toàn batch 4096 tia, chạy backpropagation tính gradient của L theo **mọi trọng số của cả 2 mạng**, dùng Adam cập nhật trọng số theo hướng giảm loss.

Lặp lại 5 bước này 100.000–300.000 lần (mỗi lần là 1 batch ngẫu nhiên mới) cho tới khi mạng hội tụ — đây chính là toàn bộ "quá trình train" của NeRF cho 1 scene.

---

Sau khi hoàn tất hàng trăm nghìn vòng lặp này, trọng số của cả 2 mạng (coarse + fine) coi như đã "cố định" — cảnh đã được mã hóa xong vào mạng. Giai đoạn tiếp theo (Giai đoạn 5) mô tả: với bộ trọng số đã train xong đó, làm thế nào để thực sự **render ra 1 ảnh output** ở góc nhìn hoàn toàn mới mà người dùng muốn xem.


---

## Giai đoạn 5: Inference — Render Output & Sơ đồ Tổng thể Pipeline

Sau khi Giai đoạn 4 hoàn tất (mạng coarse và mạng fine đã hội tụ sau hàng trăm nghìn vòng lặp train), ta có trong tay 2 bộ trọng số **cố định**. Giai đoạn cuối cùng này mô tả cách dùng bộ trọng số đó để thực sự **sinh ra ảnh output** ở góc nhìn mới — mục tiêu cuối cùng của toàn bộ hệ thống.

### Chú thích ký hiệu mới

| Ký hiệu | Ý nghĩa |
|---|---|
| **Θ** | Tập hợp toàn bộ trọng số (weights) của mạng — gồm cả trọng số mạng coarse và mạng fine. Sau khi train xong, Θ **không đổi nữa** (đóng băng/frozen), dùng lại cho mọi lần render sau này. |

### (a) Quy trình Inference — render 1 ảnh ở góc nhìn mới

#### Bước 1 — Chọn camera pose mới (R, C)

Người dùng (hoặc thuật toán quay camera tự động) chọn 1 cặp (R, C) **bất kỳ** mô tả vị trí + hướng camera muốn render — có thể là:
- Nội suy (interpolate) mượt giữa 2 pose đã có trong tập train, để tạo hiệu ứng "bay camera" mượt qua cảnh (cách phổ biến nhất để demo kết quả NeRF).
- Hoặc 1 pose hoàn toàn mới, miễn nằm trong vùng không gian hợp lý quanh vật thể (không đi quá xa vùng camera đã quan sát, nếu không chất lượng render sẽ kém do mạng chưa từng "thấy" dữ liệu ở vùng đó).

Lưu ý: pose này **không cần** có ảnh thật tương ứng — đây chính là ý nghĩa "novel view synthesis" (tổng hợp góc nhìn chưa từng chụp).

#### Bước 2 — Với mỗi pixel (u,v) của ảnh cần render

Lặp lại đúng chuỗi xử lý đã học ở Giai đoạn 2–4, nhưng lần này **không có bước cập nhật trọng số**:

1. Tính hướng tia **d** từ (u,v) + (R,C,K) — đúng công thức Giai đoạn 2.
2. Dựng tia **r(t) = o + t·d**.
3. Lấy N_c điểm mẫu bằng stratified sampling.
4. Forward N_c điểm này qua **mạng coarse đã train** (dùng Θ cố định) → ra (c_i, σ_i) → tính trọng số w_i = T_i·α_i.
5. Dùng hierarchical sampling (inverse transform sampling từ PDF dựng từ w_i) lấy thêm N_f điểm mới, tập trung quanh vùng w cao.
6. Gộp N_c+N_f điểm, forward qua **mạng fine đã train** → ra (c_i, σ_i) đầy đủ cho mọi điểm.
7. Volume rendering (công thức Ĉ(r) = Σ T_i·α_i·c_i) → ra đúng **1 màu (r,g,b)** — đây là màu của pixel (u,v) trên ảnh output.

#### Bước 3 — Lặp cho toàn bộ pixel

Lặp lại Bước 2 cho **mọi pixel** của ảnh cần render (ví dụ ảnh 800×800 → 640.000 pixel, mỗi pixel 1 tia riêng). Ghép toàn bộ màu tính được theo đúng vị trí (u,v) → ra **1 ảnh 2D hoàn chỉnh**. Đây chính là **output cuối cùng** — kết quả render ảnh ở góc nhìn mới, hoàn toàn do mạng "tưởng tượng" ra dựa trên những gì đã học được từ tập ảnh train.

#### Bước 4 — Khác biệt cốt lõi so với 1 bước train

| | Train (Giai đoạn 4) | Inference (Giai đoạn 5) |
|---|---|---|
| Trọng số Θ | Đang cập nhật (thay đổi mỗi vòng lặp) | Cố định, không đổi |
| Ground truth C(r) | Có — là màu pixel thật từ ảnh train | **Không có** — góc nhìn mới chưa từng được chụp |
| Loss, backpropagation | Có — tính loss rồi lan truyền ngược | **Không có** — chỉ là forward pass thuần |
| Số lần chạy | Hàng trăm nghìn vòng lặp (mỗi vòng 1 batch tia ngẫu nhiên) | 1 lần cho mỗi pixel của mỗi ảnh muốn render |

Nói ngắn gọn: train là quá trình "học" (có so sánh đúng/sai và tự sửa), còn inference là quá trình "hỏi" (chỉ hỏi mạng đã học xong "ở đây màu gì", không còn gì để sửa nữa).

#### Bước 5 — Mở rộng: xuất mesh 3D thay vì ảnh 2D (nhắc ngắn gọn)

Nếu muốn có 1 file mesh (.obj) để xem trong phần mềm 3D (Blender...) thay vì chỉ render ảnh phẳng, cần thêm bước riêng: quét 1 lưới điểm dày đặc (ví dụ 256³ điểm) phủ khắp bounding box của cảnh, hỏi mạng density σ tại từng điểm lưới, rồi dùng thuật toán **Marching Cubes** để dựng bề mặt từ lưới giá trị density đó. Chi tiết bước này đã có trong `lythuyet.md` Phần II.

### (b) Sơ đồ tổng thể toàn bộ Pipeline

```
┌──────────────────────────────────────────────────────────────────────┐
│  GIAI ĐOẠN 1 — Chuẩn bị dữ liệu & COLMAP/SfM  (chạy 1 lần, offline)  │
│  Thư mục ảnh thô ──► SIFT+RANSAC+Triangulation+Bundle Adjustment      │
│  ──► pose (R,C,K) cho mỗi ảnh + bounding scene                       │
└───────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
        ╔════════════════════════════════════════════════════╗
        ║   VÒNG LẶP TRAIN — lặp 100.000–300.000 LẦN          ║
        ║   (mỗi lần: 1 batch 4096 tia ngẫu nhiên, CÓ backprop)║
        ║                                                      ║
        ║  ┌─────────────────────────────────────────────┐    ║
        ║  │ GIAI ĐOẠN 2 — Ray, Sampling, Encoding        │    ║
        ║  │ pixel(u,v) ──► d ──► r(t)=o+t·d              │    ║
        ║  │ ──► N_c điểm (stratified) ──► γ(x),γ(d)       │    ║
        ║  └──────────────────┬──────────────────────────┘    ║
        ║                     ▼                                ║
        ║  ┌─────────────────────────────────────────────┐    ║
        ║  │ GIAI ĐOẠN 3 — MLP + Volume Rendering (coarse)│    ║
        ║  │ γ(x),γ(d) ──► F_Θ (8 lớp) ──► (c,σ)          │    ║
        ║  │ ──► Volume Rendering ──► Ĉ_c(r)              │    ║
        ║  └──────────────────┬──────────────────────────┘    ║
        ║                     ▼                                ║
        ║  ┌─────────────────────────────────────────────┐    ║
        ║  │ GIAI ĐOẠN 4 — Hierarchical + Loss + Backprop │    ║
        ║  │ w_i=T_iα_i ──► lấy thêm N_f điểm              │    ║
        ║  │ ──► mạng fine ──► Ĉ_f(r)                     │    ║
        ║  │ ──► Loss L=‖Ĉ_c−C‖²+‖Ĉ_f−C‖²                │    ║
        ║  │ ──► backprop ──► CẬP NHẬT Θ (Adam)           │    ║
        ║  └──────────────────┬──────────────────────────┘    ║
        ║                     │                                ║
        ║                     └──── quay lại Giai đoạn 2 ──────╣
        ║                          với batch tia MỚI            ║
        ╚════════════════════════════╦═══════════════════════╝
                                      │  (khi loss hội tụ, Θ cố định)
                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GIAI ĐOẠN 5 — INFERENCE  (chạy mỗi lần muốn render 1 ảnh mới)       │
│  Θ CỐ ĐỊNH, KHÔNG backprop, KHÔNG cần ground truth                   │
│  Chọn (R,C) mới ──► mỗi pixel lặp lại Giai đoạn 2+3+4(chỉ forward)    │
│  ──► ghép toàn bộ pixel ──► ẢNH OUTPUT ở góc nhìn mới                 │
└──────────────────────────────────────────────────────────────────────┘
```

### Bảng tra cứu: Giai đoạn ↔ Mục trong paper gốc (arXiv:2003.08934)

| Giai đoạn | Nội dung | Mục tương ứng trong paper |
|---|---|---|
| 1 | Chuẩn bị dữ liệu, COLMAP/SfM | Mục 5.3 (chỉ nhắc 1 câu dùng COLMAP; chi tiết SfM không có trong paper) |
| 2 | Ray, Stratified Sampling, Positional Encoding | Mục 3 (ray), Mục 4 (stratified sampling, Eq. 2), Mục 5.1 (positional encoding) |
| 3 | Kiến trúc MLP, Volume Rendering | Mục 3 (kiến trúc mạng), Mục 4 (volume rendering, Eq. 1 và Eq. 3) |
| 4 | Hierarchical Sampling, Loss, Training | Mục 5.2 (hierarchical sampling, Eq. 5), Mục 5.3 (loss Eq. 6, hyperparameters) |
| 5 | Inference, kết quả | Mục 6 (Results — minh họa kết quả render, không mô tả quy trình inference tường minh; quy trình ở đây suy ra trực tiếp từ kiến trúc đã mô tả) |

---

Tổng kết: 5 giai đoạn trên mô tả **toàn bộ vòng đời của 1 hệ thống NeRF**, từ lúc chỉ có 1 thư mục ảnh thô chụp ngoài đời, qua quá trình ước lượng camera pose, xây dựng và train 1 cặp mạng nơ-ron biểu diễn cảnh dưới dạng hàm liên tục 5D, cho tới khi có thể "hỏi" mạng đó để sinh ra ảnh ở bất kỳ góc nhìn nào chưa từng được chụp. Điểm mấu chốt xuyên suốt toàn bộ pipeline là: không có bước nào lưu trữ tường minh hình dạng 3D của cảnh — toàn bộ thông tin đó được nén lại bên trong vài MB trọng số Θ, và chỉ "hiện ra" dưới dạng ảnh khi được truy vấn qua đúng chuỗi Ray → Sampling → MLP → Volume Rendering. Giai đoạn Inference chính là bằng chứng cho thấy việc train (Giai đoạn 1–4) đã thành công: nếu Θ học đúng, bất kỳ góc nhìn mới nào đưa vào cũng cho ra ảnh hợp lý, nhất quán với các góc đã học.

---

## Tài liệu liên quan trong thư mục đồ án

- `Doan/lythuyet.md` — ghi chú học tập dạng hỏi-đáp, có thêm 1 số nội dung mở rộng (ví dụ: nền tảng Pinhole Camera đầy đủ hơn, so sánh NeRF gốc vs NeRF cải tiến) không nằm trong phạm vi 5 giai đoạn pipeline ở trên.
- `Doan/tomtat_paper_NeRF.md` / `.docx` — bản tóm tắt/diễn giải lại toàn bộ paper gốc theo đúng cấu trúc các mục của paper (Abstract, Related Work, Results, Ablation study, Conclusion...), bao gồm cả phần không thuộc pipeline kỹ thuật (so sánh với NV/SRN/LLFF, bảng kết quả định lượng).
- File này (`pipeline_NeRF.md`) khác 2 file trên ở chỗ: tổ chức lại nội dung theo đúng **trình tự thời gian thực tế** khi chạy NeRF (từ ảnh thô → output), phù hợp dùng làm khung sườn cho phần **Chương 3 (Phương pháp)** và **Chương 4 (Cài đặt và thử nghiệm)** của đồ án.
