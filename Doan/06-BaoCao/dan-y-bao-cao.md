# DÀN Ý CHI TIẾT BÁO CÁO ĐỒ ÁN

**Đề tài:** Xây dựng ứng dụng kết xuất ảnh (rendering) với góc nhìn tùy ý dựa vào dãy ảnh 2D cho trước — Tìm hiểu mô hình NeRF và NeRF cải tiến

**Nhóm:** 2 thành viên — Bùi Văn Thiên (24120138) và [tên thành viên 2]
**Lớp:** Đồ Họa Máy Tính CQ2024/23 · **GVHD:** PGS.TS Lý Quốc Ngọc
**Phương pháp chọn trình bày:** Mip-NeRF 360 (Barron et al., CVPR 2022)
**Độ dài dự kiến:** 40-48 trang

> **Dàn ý này được xây dựng bám sát `01-DeBai/yeu-cau-cua-thay.md`** — đặc biệt là **8 lỗi thường gặp** trong `motsoluuyloi.rtf`. Mỗi chỗ liên quan đều có ghi chú `⚠️ LƯU Ý n` để đối chiếu.

---

## NGUYÊN TẮC XUYÊN SUỐT

### A. Trục tổ chức: "CÁC CÔNG ĐOẠN"

Đây là yêu cầu cốt lõi của thầy (Lưu ý 1, 2, 3, 8). Toàn bộ báo cáo xoay quanh **4 công đoạn** được định nghĩa ở mục 1.3:

```
[CĐ1] Ước lượng    [CĐ2] Biểu diễn    [CĐ3] Kết xuất    [CĐ4] Tối ưu hóa
      tham số camera       cảnh 3D            ảnh              biểu diễn
```

- **Chương 1** định nghĩa 4 công đoạn + ẩn số của từng công đoạn (Lưu ý 1, 2)
- **Chương 2** so sánh các phương pháp **theo đúng 4 công đoạn đó** (Lưu ý 3), và chỉ ra **khuyết điểm tồn đọng theo từng công đoạn** (Lưu ý 8)
- **Chương 3** trình bày Mip-NeRF 360 **theo đúng 4 công đoạn đó**
- **Chương 4** đánh giá kết quả gắn với từng công đoạn

→ Nhờ vậy người đọc luôn đối chiếu được: công đoạn này phương pháp A làm thế nào, phương pháp B làm thế nào.

### B. Sáu nguyên tắc trình bày học từ paper top đầu

1. **Nêu vấn đề trước, giải pháp sau.** Mip-NeRF 360 tuyên bố **ba vấn đề** (Parameterization, Efficiency, Ambiguity) rồi dành mỗi mục giải một vấn đề.
2. **Có mục "Preliminaries"** tóm tắt phương pháp nền trước khi nói mình thay đổi gì.
3. **Mỗi công thức có bảng ký hiệu** định nghĩa ngay lần đầu xuất hiện.
4. **Kết quả có cả định lượng và định tính.** Bảng số chứng minh "tốt hơn bao nhiêu"; ảnh cạnh nhau chứng minh "tốt hơn ở chỗ nào".
5. **Phải có Ablation Study** — tắt từng thành phần rồi đo lại.
6. **Trung thực về hạn chế.** Mọi paper top đầu đều có mục Limitations.

**Chú thích trạng thái nguyên liệu:** 🟢 viết được ngay · 🟡 có một phần · 🔴 chưa có gì

---

# PHẦN MỞ ĐẦU (~4 trang)

| Thành phần | Nội dung |
|---|---|
| Trang bìa | Trường/khoa, tên đồ án, môn học, nhóm, GVHD, năm |
| Lời cảm ơn | ~0,5 trang |
| Mục lục | Tự động, tới mục cấp 3 |
| Danh mục hình, bảng | Đánh số theo chương (Hình 3.1, Bảng 2.1...) |
| **Danh mục từ viết tắt** | NeRF, MLP, SfM, COLMAP, PSNR, SSIM, LPIPS, IPE, PE, NDC, SH, 3DGS, GPU, TPU, CUDA, SDF, FPS |
| **Danh mục ký hiệu** | `x`(vị trí 3D), `d`(hướng nhìn), `o`(gốc tia), `t`(tham số tia), `σ`(density), `c`(màu), `T`(transmittance), `α`(opacity), `γ(·)`(positional encoding), `μ,Σ`(mean/covariance Gaussian), `Θ`(trọng số mạng), `K,R,C`(nội tại/xoay/tâm camera) |

**Tóm tắt (~200 từ, viết sau cùng)** theo 4 câu: *bối cảnh → khoảng trống → việc đã làm → kết quả cụ thể*.

---

# CHƯƠNG 1 — GIỚI THIỆU (~7 trang)

## 1.1. Ý nghĩa khoa học của chủ đề 🟡 (~1 trang)

**Bốn đoạn:**

1. **Đặt vấn đề.** Con người nhìn vật từ vài góc là hình dung được hình dạng 3D. Máy tính khó ở chỗ: ảnh 2D đã mất thông tin độ sâu, một pixel ứng với vô số điểm 3D khả dĩ. Bài toán **tổng hợp góc nhìn mới (novel view synthesis)** là khôi phục khả năng đó.
2. **Quá trình phát triển trước NeRF.** Nội suy light field (cần ảnh dày đặc) → mesh (khó tối ưu) → voxel grid (bộ nhớ lũy thừa) → neural implicit surface (cần ground-truth 3D). Mỗi hướng vướng một rào cản cơ bản.
3. **Vì sao NeRF là bước ngoặt.** (a) Chuyển từ biểu diễn tường minh sang **biểu diễn ẩn** — nén cả cảnh vào vài MB trọng số; (b) chỉ cần ảnh RGB thường, **không cần dữ liệu 3D ground-truth**; (c) chất lượng photorealistic lần đầu đạt được.
4. **Vị trí trong nghiên cứu hiện nay.** NeRF mở ra nhánh neural rendering; số công trình kế thừa tăng vọt từ 2020, dẫn tới 3D Gaussian Splatting (2023).

**Hình 1.1:** minh họa bài toán — vài ảnh input ở các góc → ảnh output ở góc chưa chụp.

**Trích dẫn:** `Survey/2022 Advances in Neural Rendering`, `Survey/2022 CVM Review`, `Selected/2020 NeRF`

## 1.2. Ý nghĩa ứng dụng 🔴 (~1 trang)

Mỗi lĩnh vực 1 đoạn, nêu rõ **vì sao NeRF phù hợp**, không chỉ liệt kê:

| Lĩnh vực | Góc nhìn cần nhấn |
|---|---|
| VR/AR, metaverse | Dựng môi trường 3D chân thực nhanh, thay vì mô hình hóa thủ công hàng tháng |
| Số hóa di sản | Bảo tồn hiện vật không thể chạm vào; chỉ cần ảnh chụp thường |
| Thương mại điện tử | Xem sản phẩm 360°, thử đồ ảo |
| Bất động sản, du lịch | Tham quan ảo không gian thật |
| Robot, xe tự hành | Dựng bản đồ 3D từ camera giá rẻ thay vì LiDAR |
| Điện ảnh, VFX | Dựng cảnh từ footage thật, chèn vật thể ảo khớp ánh sáng |

> Nêu 1-2 ví dụ có thật (ví dụ Google Maps Immersive View) sẽ thuyết phục hơn liệt kê chung.

## 1.3. Phát biểu bài toán 🟢 (~3,5 trang) ⭐ MỤC QUAN TRỌNG NHẤT CHƯƠNG 1

> ⚠️ **LƯU Ý 1:** framework chỉ nêu công đoạn tổng quát, **tuyệt đối không nhắc tên phương pháp cụ thể** (không viết "dùng COLMAP", "dùng MLP").
> ⚠️ **LƯU Ý 2:** mỗi công đoạn phải nêu rõ **đã cho gì** và **ẩn số cần tìm là gì**.

### 1.3.1. Input và Output của hệ thống

**Input:**
- Tập ảnh RGB 2D: `{I₁, I₂, ..., I_N}`, N ≈ 20-100 ảnh
- Ràng buộc: cảnh **tĩnh** (vật thể/ánh sáng không đổi giữa các ảnh), độ **chồng lấp** giữa các ảnh liên tiếp đủ lớn

**Output:**
- Ảnh RGB render tại camera pose **tùy ý** chưa có trong tập input
- Mở rộng: video quay quanh cảnh; mô hình 3D dạng mesh

### 1.3.2. Framework chung — bốn công đoạn

> ⚠️ **LƯU Ý 1** — mô tả ở mức tổng quát, mỗi công đoạn có nhiều giải pháp khả dĩ (sẽ khảo sát ở Chương 2).

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
                                                  │ biểu diễn (so với │
                                                  │ ảnh thật)         │
                                                  └───────────────────┘
```

**Hình 1.2:** sơ đồ trên, vẽ lại đẹp bằng công cụ vẽ.

Mô tả từng công đoạn ở mức tổng quát:

| Công đoạn | Nhiệm vụ | Các hướng giải pháp khả dĩ (chưa chọn) |
|---|---|---|
| **CĐ1** | Xác định mỗi ảnh được chụp từ vị trí nào, hướng nào, với ống kính ra sao | Structure-from-Motion, SLAM, cảm biến gắn kèm, pose có sẵn (dữ liệu tổng hợp) |
| **CĐ2** | Xây dựng cấu trúc dữ liệu/hàm số mô tả cảnh 3D, truy vấn được tại điểm bất kỳ | Biểu diễn tường minh (mesh, voxel, point cloud, Gaussian) hoặc ẩn (mạng nơ-ron, hàm liên tục) |
| **CĐ3** | Từ biểu diễn + một góc nhìn, sinh ra ảnh 2D | Rasterization, ray tracing, ray marching + volume rendering, splatting |
| **CĐ4** | Điều chỉnh tham số của biểu diễn sao cho ảnh sinh ra khớp ảnh quan sát | Gradient descent (nếu quy trình khả vi), phương pháp tối ưu phi tuyến, lấp đầy trực tiếp |

### 1.3.3. Ẩn số cần tìm trong từng công đoạn

> ⚠️ **LƯU Ý 2** — đây là mục thầy nhấn mạnh là hay bị bỏ sót. Phải viết rõ ràng, có bảng.

**Bảng 1.1 — Đã cho và ẩn số của từng công đoạn:**

| Công đoạn | Đã cho (biết) | **Ẩn số cần tìm** | Ràng buộc để giải |
|---|---|---|---|
| **CĐ1** | Tập ảnh `{I₁..I_N}` | Với mỗi ảnh `i`: ma trận nội tại `Kᵢ`, ma trận xoay `Rᵢ`, tâm camera `Cᵢ`. Kèm theo: tập điểm 3D thưa `{X_j}` | Cùng một điểm vật lý xuất hiện trên nhiều ảnh phải chiếu về đúng vị trí quan sát được (sai số tái chiếu nhỏ nhất) |
| **CĐ2** | Không gian cảnh được giới hạn; dạng biểu diễn đã chọn | **Tham số `Θ` của biểu diễn** — tùy dạng mà `Θ` là trọng số mạng, giá trị trên lưới voxel, hay tập tham số của các primitive | `Θ` phải sinh ra ảnh khớp với mọi ảnh quan sát được |
| **CĐ3** | Biểu diễn `Θ`, camera pose cần render | *(Không có ẩn số học)* — đây là bước tính toán xuôi. Ẩn số thiết kế: chọn thuật toán kết xuất nào, lấy mẫu bao nhiêu điểm | Phải khả vi nếu muốn dùng gradient descent ở CĐ4 |
| **CĐ4** | Ảnh render `Ĉ`, ảnh thật `C` | `Θ` tối ưu — chính là ẩn số của CĐ2, được giải ở đây | Tối thiểu hóa hàm mất mát giữa `Ĉ` và `C` |

> **Nhận xét quan trọng cần viết:** CĐ2 và CĐ4 **gắn chặt với nhau** — CĐ2 định nghĩa *dạng* của ẩn số `Θ`, CĐ4 là *cách tìm* ra `Θ`. Việc chọn dạng biểu diễn ở CĐ2 quyết định luôn CĐ4 giải được bằng cách nào. Đây là chỗ các phương pháp khác nhau nhiều nhất (xem Chương 2).

### 1.3.4. Các tác vụ cần thực hiện

Liệt kê cụ thể hóa 4 công đoạn thành các tác vụ thực thi được (đây là phần thầy yêu cầu ở `phuongphap.rtf` 2.4).

### 1.3.5. Tập dữ liệu thử nghiệm chuẩn

> ⚠️ **LƯU Ý 7** — không chỉ nêu số lượng, phải nêu **thách thức** chứa trong dữ liệu.

**Bảng 1.2 — Các bộ dữ liệu chuẩn của bài toán:**

| Dataset | Số cảnh | Loại | **Thách thức chứa trong dữ liệu** |
|---|---|---|---|
| Blender Synthetic | 8 vật thể | Tổng hợp, 360° | Vật liệu non-Lambertian (phản chiếu), hình học phức tạp (dây chằng tàu thủy, bánh răng) |
| LLFF | 8 cảnh | Thật, forward-facing | Cảnh thật có nhiễu, nội dung từ gần tới vô cực, vùng bị che khuất một phần |
| **Mip-NeRF 360** | 9 cảnh (5 ngoài trời, 4 trong nhà) | Thật, 360° unbounded | **Cảnh không giới hạn** (nền trải tới chân trời), chi tiết cả gần lẫn rất xa, ánh sáng ngoài trời thay đổi, vùng ít ảnh quan sát |

## 1.4. Đóng góp của báo cáo 🟡 (~0,75 trang)

1. **Khảo sát có hệ thống** các phương pháp radiance field 2020-2024, **so sánh theo đúng bốn công đoạn** của framework, chỉ ra khuyết điểm tồn đọng ở từng công đoạn
2. **Trình bày chi tiết Mip-NeRF 360** trong mạch kế thừa NeRF → Mip-NeRF → Mip-NeRF 360, làm rõ từng cải tiến tác động vào công đoạn nào
3. **Cài đặt thử nghiệm** trên dữ liệu chuẩn và dữ liệu tự thu thập; đánh giá **cả độ chính xác lẫn độ phức tạp tính toán**
4. **Phân tích hạn chế** qua quan sát thực nghiệm, đối chiếu với hướng phát triển mới nhất

> ⚠️ Thầy ghi rõ *"SV chỉ cần đọc, hiểu, cài đặt lại. Chưa đòi hỏi đề xuất giải pháp mới"* → **không** viết đóng góp kiểu "chúng tôi đề xuất phương pháp mới".

## 1.5. Bố cục báo cáo 🔴 (~0,25 trang)

---

# CHƯƠNG 2 — CÁC CÔNG TRÌNH NGHIÊN CỨU LIÊN QUAN (~11 trang)

> **Hai câu hỏi phải trả lời:** *Người ta đã làm gì rồi?* (2.1-2.4) · *Mình muốn làm gì?* (2.5)
>
> ⚠️ **LƯU Ý 3** — mọi giải pháp trình bày theo **cùng một khuôn**, bám theo **bốn công đoạn** ở mục 1.3.2.
> ⚠️ **LƯU Ý 8** — phải chỉ ra **khuyết điểm tồn đọng theo từng công đoạn**, phân loại *độ chính xác* hay *độ phức tạp tính toán*.

## 2.1. Các phương pháp trước NeRF 🟡 (~1,5 trang)

Trình bày theo công đoạn để thấy mỗi hướng vướng ở đâu:

| Nhóm phương pháp | CĐ2 (Biểu diễn) | CĐ3 (Kết xuất) | Rào cản chính |
|---|---|---|---|
| Light field / IBR | Tập ảnh gốc + thông tin độ sâu thô | Nội suy giữa ảnh | Cần lấy mẫu rất dày |
| Mesh-based | Lưới tam giác | Rasterization / path tracing | Tối ưu khó hội tụ, cần mesh mẫu |
| Voxel grid | Lưới 3D rời rạc | Ray marching | Bộ nhớ tăng lũy thừa theo độ phân giải |
| Neural implicit surface | Hàm SDF/occupancy ẩn | Tìm giao điểm bề mặt | Cần ground-truth 3D; kết quả mờ |

## 2.2. NeRF — phương pháp nền tảng 🟢 (~2 trang)

**2.2.1. Ánh xạ NeRF vào bốn công đoạn** (khuôn chuẩn, áp dụng cho mọi phương pháp sau):

| Công đoạn | NeRF giải quyết thế nào |
|---|---|
| CĐ1 | Dùng Structure-from-Motion (COLMAP) ước lượng `K, R, C` |
| CĐ2 | Hàm liên tục `F_Θ(x,d) → (c,σ)` cài trong MLP 8 lớp × 256 kênh |
| CĐ3 | Ray marching + volume rendering: lấy 192 điểm mẫu/tia, tích lũy theo công thức transmittance |
| CĐ4 | Gradient descent (Adam) trên loss MSE giữa ảnh render và ảnh thật |

**2.2.2. Năm hạn chế của NeRF — gắn với công đoạn và phân loại:**

> ⚠️ **LƯU Ý 8** — phân loại rõ *độ chính xác* hay *độ phức tạp tính toán*.

| # | Hạn chế | Thuộc công đoạn | Loại khuyết điểm | Nguyên nhân kỹ thuật |
|---|---|---|---|---|
| 1 | Train chậm (1-2 ngày/cảnh) | CĐ2 + CĐ4 | Độ phức tạp tính toán | Mỗi điểm mẫu qua MLP 8×256; hàng trăm nghìn điểm/batch |
| 2 | Render chậm, không real-time | CĐ3 | Độ phức tạp tính toán | 192 lần truy vấn mạng cho mỗi pixel |
| 3 | Răng cưa khi đổi tỉ lệ | CĐ3 | Độ chính xác | Tia mảnh không biểu diễn được vùng pixel thực sự bao phủ |
| 4 | Kém với cảnh 360° unbounded | CĐ2 + CĐ3 | Độ chính xác | Lấy mẫu tuyến tính theo `t`; NDC chỉ dùng cho forward-facing |
| 5 | Phụ thuộc pose chính xác | CĐ1 | Độ chính xác | Pose sai → tia không giao đúng chỗ → hình học nhòe |

## 2.3. Các giải pháp SOTA 🟢 (~4 trang)

> ⚠️ **LƯU Ý 3** — **mỗi phương pháp trình bày theo CÙNG một khuôn 5 mục:**
> *(a) Giải quyết khuyết điểm nào · (b) Tác động vào công đoạn nào · (c) Ý tưởng cốt lõi · (d) Kết quả đạt được · (e) Hạn chế còn lại*

Áp dụng khuôn này cho 7 phương pháp, mỗi phương pháp ~0,5 trang:

| Mục | Phương pháp | Khuyết điểm giải quyết | Công đoạn tác động |
|---|---|---|---|
| 2.3.1 | **Instant-NGP** (SIGGRAPH 2022) | #1 Train chậm | CĐ2 (hash encoding thay PE, MLP nhỏ) + CĐ3 (occupancy grid bỏ qua vùng trống) |
| 2.3.2 | **Plenoxels** (CVPR 2022) | #1 Train chậm | CĐ2 (bỏ hẳn mạng nơ-ron, dùng voxel thưa + SH) |
| 2.3.3 | **TensoRF** (ECCV 2022) | #1 Train chậm | CĐ2 (phân rã tensor bậc thấp) |
| 2.3.4 | **Mip-NeRF** (ICCV 2021) | #3 Răng cưa | CĐ3 (hình nón cụt thay tia mảnh) + CĐ2 (IPE thay PE) |
| 2.3.5 | **NeRF++** (2020) | #4 Cảnh unbounded | CĐ2 (tách 2 mạng trong/ngoài khối cầu) |
| 2.3.6 | **Mip-NeRF 360** (CVPR 2022) | #3 + #4 | CĐ2 (scene contraction) + CĐ3 (lấy mẫu theo disparity) + CĐ4 (proposal net, distortion loss) |
| 2.3.7 | **3D Gaussian Splatting** (SIGGRAPH 2023) | #2 Render chậm | CĐ2 (Gaussian tường minh) + CĐ3 (rasterization thay ray marching) |
| 2.3.8 | **Zip-NeRF** (ICCV 2023) | #1 + #3 + #4 | Kết hợp Mip-NeRF 360 (CĐ2,3,4) + hash grid của Instant-NGP (CĐ2) |

## 2.4. Bảng so sánh các giải pháp theo công đoạn 🟡 (~2 trang)

> ⚠️ **LƯU Ý 3** — đây là bảng thầy yêu cầu: **cột ứng với các công đoạn**, hàng là phương pháp.

**Bảng 2.1 — So sánh theo bốn công đoạn (bảng chính):**

| Phương pháp | CĐ1: Ước lượng pose | CĐ2: Biểu diễn cảnh | CĐ3: Kết xuất | CĐ4: Tối ưu |
|---|---|---|---|---|
| NeRF | SfM (COLMAP) | MLP 8×256, PE | Ray marching, 192 mẫu/tia, coarse+fine | MSE loss, Adam |
| NeRF++ | SfM | 2 MLP (trong/ngoài cầu), tham số hóa `1/r` | Ray marching 2 đoạn, ghép transmittance | MSE loss |
| Mip-NeRF | SfM | 1 MLP, **IPE** (mã hóa vùng) | **Hình nón cụt** thay tia mảnh | MSE loss, giám sát đa tỉ lệ |
| Plenoxels | SfM | **Voxel thưa + hệ số SH** (không mạng) | Ray marching + nội suy tam tuyến | Gradient trực tiếp lên voxel + TV regularization |
| Instant-NGP | SfM | **Hash grid đa độ phân giải** + MLP nhỏ | Ray marching + **occupancy grid** | MSE loss, Adam (ε=10⁻¹⁵) |
| TensoRF | SfM | **Tensor phân rã bậc thấp** | Ray marching | MSE + regularization |
| **Mip-NeRF 360** | SfM | **Scene contraction** + MLP 8×1024 + off-axis IPE | Lấy mẫu đều theo **disparity**, hình nón cụt | MSE + **L_prop** (distillation) + **L_dist** (distortion) |
| 3D Gaussian Splatting | SfM (+ dùng cả sparse point cloud) | **Hàng triệu Gaussian 3D tường minh** | **Rasterization/splatting** | L1 + D-SSIM, **adaptive density control** |

**Bảng 2.2 — So sánh hiệu năng (độ chính xác + độ phức tạp tính toán):**

> ⚠️ **LƯU Ý 6** — phải có **cả hai loại** độ đo.

| Phương pháp | PSNR↑ | SSIM↑ | LPIPS↓ | Thời gian train | Tốc độ render | Bộ nhớ | Số truy vấn mạng/tia |
|---|---|---|---|---|---|---|---|

**⚠️ Quy tắc bắt buộc khi lập 2 bảng này:**
- Mỗi con số **ghi rõ nguồn** (paper nào, Bảng mấy) bằng chú thích dưới bảng
- **Ghi rõ điều kiện đo** (phần cứng, dataset) — các paper đo trên cấu hình khác nhau, không chú thích sẽ bị hỏi "sao so TPU với GPU được"
- Ưu tiên lấy số từ **một nguồn đo chung** (ví dụ Table 1 của `Selected/2022 Mip-NeRF 360` đo nhiều phương pháp trên cùng dataset) — đây là so sánh công bằng nhất

## 2.5. Khuyết điểm tồn đọng và định hướng của đồ án 🔴 (~1,5 trang)

> ⚠️ **LƯU Ý 8** — mục này thầy nhấn mạnh: phải **nhìn ra khuyết điểm còn tồn đọng cần giải quyết trong các công đoạn**.

**Bảng 2.3 — Khuyết điểm tồn đọng theo từng công đoạn:**

| Công đoạn | Khuyết điểm còn tồn đọng | Loại | Đã có ai giải quyết tới đâu |
|---|---|---|---|
| **CĐ1** | Phụ thuộc hoàn toàn vào chất lượng SfM; thất bại với cảnh ít kết cấu, bề mặt phản chiếu; không xử lý được cảnh động | Độ chính xác | Hướng pose-free NeRF (BARF, NeRF--) — chưa trưởng thành |
| **CĐ2** | Đánh đổi giữa dung lượng và chất lượng chưa giải quyết triệt để: biểu diễn ẩn gọn nhưng chậm, tường minh nhanh nhưng nặng hàng trăm MB | Cả hai | Zip-NeRF cố gắng dung hòa nhưng vẫn chưa real-time như 3DGS |
| **CĐ3** | Ray marching vẫn tốn nhiều truy vấn; rasterization nhanh nhưng mất tính liên tục, khó biểu diễn hiệu ứng trong suốt/khúc xạ | Độ phức tạp tính toán | 3DGS đạt real-time nhưng đánh đổi dung lượng |
| **CĐ4** | Cần nhiều ảnh (20-100); chất lượng sụp nhanh khi ít ảnh; xuất hiện floaters ở vùng ít quan sát | Độ chính xác | L_dist của Mip-NeRF 360 giảm được floaters; hướng few-shot NeRF còn mở |

**Định hướng của đồ án — trả lời "mình muốn làm gì":**
- **Lý do chọn Mip-NeRF 360:** giải quyết đồng thời 2 khuyết điểm (#3 răng cưa ở CĐ3, #4 cảnh unbounded ở CĐ2+CĐ3), tác động vào cả 3 công đoạn CĐ2-CĐ3-CĐ4; đại diện nhánh biểu diễn ẩn đạt chất lượng cao nhất; nằm trong mạch kế thừa rõ ràng thuận lợi để trình bày có hệ thống
- **Phạm vi:** đọc hiểu, trình bày lại, cài đặt thử nghiệm — **không** đề xuất phương pháp mới

---

# CHƯƠNG 3 — PHƯƠNG PHÁP: MIP-NERF 360 (~15 trang) ⭐ TRỌNG TÂM

> ⚠️ **`phuongphap.rtf` 2.6:** mạch **nguyên lý → phương pháp → giải thuật → CT minh họa**
> ⚠️ **LƯU Ý 4, 5:** phải nêu rõ ground truth, cách "đánh nhãn", loss function; phải có sơ đồ riêng cho **giai đoạn học** và **giai đoạn kiểm thử**

## 3.0. Dẫn nhập: ba vấn đề Mip-NeRF 360 giải quyết 🟢 (~0,5 trang)

| Vấn đề (theo paper) | Mô tả | Thuộc công đoạn | Giải ở mục |
|---|---|---|---|
| **Parameterization** | Cảnh 360° trải tới vô cực, không lấy mẫu tuyến tính được | CĐ2 + CĐ3 | 3.3.1 |
| **Efficiency** | Cảnh lớn cần mạng dung lượng lớn, truy vấn dày đặc quá tốn | CĐ3 + CĐ4 | 3.3.2 |
| **Ambiguity** | Nội dung có thể ở bất kỳ độ sâu nào, ít ảnh quan sát → artifact | CĐ4 | 3.3.3 |

## 3.1. NGUYÊN LÝ — Nền tảng NeRF 🟢 (~4 trang)

- **3.1.1.** Biểu diễn cảnh bằng trường bức xạ 5D `F_Θ(x,d) → (c,σ)` · ý nghĩa "trường" · vì sao biểu diễn **ẩn** · định lý xấp xỉ phổ quát · **Bảng 3.1** chú thích ký hiệu
- **3.1.2.** Mô hình pinhole camera · phép chiếu phối cảnh (tam giác đồng dạng) · ma trận `K`, `(R,C)` · công thức tia `r(t)=o+t·d` · **Hình 3.1**
- **3.1.3.** Lấy mẫu phân tầng (stratified sampling) · vì sao không dùng lưới cố định
- **3.1.4.** Positional Encoding `γ(p)` · vấn đề **spectral bias** · L=10 (vị trí, 60 chiều), L=4 (hướng, 24 chiều)
- **3.1.5.** Kiến trúc MLP 8×256 · skip connection · **điểm thiết kế then chốt:** σ chỉ phụ thuộc vị trí, màu phụ thuộc cả hướng nhìn → nhất quán đa góc nhìn + mô phỏng được hiệu ứng view-dependent · **Hình 3.2**
- **3.1.6.** Volume Rendering · định nghĩa chính xác σ (xác suất vi phân) · công thức tích phân liên tục + dẫn `T(t)` từ phương trình vi phân (Beer-Lambert) · công thức rời rạc là tổng Riemann · **Bảng 3.2** · **ví dụ số 3 điểm mẫu** minh họa occlusion
- **3.1.7.** Hierarchical sampling · trọng số `wᵢ=Tᵢαᵢ` · inverse transform sampling · hàm loss MSE cộng cả 2 nhánh

**Nguyên liệu:** `02-TaiLieuHoc/pipeline_NeRF.md`, `lythuyet_NeRF.md` · **Trích dẫn:** `Selected/2020 NeRF`, `Foundation/1995 Optical Models`

## 3.2. Preliminaries — Mip-NeRF: chống răng cưa 🟡 (~2,5 trang)

- **3.2.1.** Vấn đề aliasing: pixel là **vùng** không phải **điểm** · **Hình 3.3** so sánh tia mảnh vs hình nón
- **3.2.2.** Hình nón cụt (conical frustum) · xấp xỉ Gaussian đa biến `(μ, Σ)` · **Bảng 3.3**
- **3.2.3.** Integrated Positional Encoding: `IPE(μ,Σ) = E[γ(x)]` · dạng đóng với hệ số suy giảm `exp(-½(2^l π)²σ²)` · **trực giác:** tần số cao tự tắt khi vùng quá lớn → chống răng cưa có nguyên lý, không phải hậu xử lý
- **3.2.4.** Gộp 2 mạng coarse/fine thành 1; vẫn giám sát đa tỉ lệ bằng loss ảnh (hệ số 1/10 cho coarse) — **chi tiết này quan trọng** vì chính nó là thứ bản 360 loại bỏ

**Trích dẫn:** `Selected/2021 Mip-NeRF` ⚠️ **cần đọc** để lấp các chỗ `[MIP-NỀN]`

## 3.3. PHƯƠNG PHÁP — Mip-NeRF 360 🟢 (~5 trang)

**3.3.1. Parameterization — Scene Contraction** *(tác động CĐ2 + CĐ3)* (~1,75 trang)
- Vấn đề cụ thể · công thức `contract(x)` (Eq. 10) · ⚠️ bán kính đo **từ gốc tọa độ world**, không phải từ camera
- **Đóng góp cốt lõi:** áp phép co lên **Gaussian (μ,Σ)** theo kiểu Extended Kalman filter (`f(μ), JΣJᵀ` — Eq. 8-9), không chỉ lên điểm
- Tham số hóa lại tia: lấy mẫu đều trong không gian `s` (Eq. 11, `g(x)=1/x`) → tuyến tính theo **disparity**; `t_far = ∞` trở nên hợp lệ
- **Off-axis IPE** (Eq. 17): nâng cấp bắt buộc vì contract sinh Gaussian dị hướng; cơ sở 21 đỉnh icosahedron
- **Hình 3.4** minh họa phép co · **Bảng 3.4** ký hiệu

**3.3.2. Efficiency — Proposal Network + Online Distillation** *(tác động CĐ3 + CĐ4)* (~1,75 trang)

| | Proposal MLP | NeRF MLP |
|---|---|---|
| Nhiệm vụ | Chỉ dự đoán density để hướng dẫn lấy mẫu | Dự đoán density **và màu** để render |
| Kích thước | 4 lớp × 256 | 8 lớp × 1024 |
| Số mẫu | 2 lượt × 64 | 32 |

- **Khác biệt căn bản với coarse/fine của NeRF:** proposal **không** dự đoán màu, **không** được giám sát bằng loss ảnh
- Online distillation (Eq. 12-13): histogram density của proposal phải **bao trọn** histogram NeRF MLP; **stop-gradient**; `L_prop` là **chặn trên một phía bất đối xứng**
- Kết quả: tăng tốc train ~300% (Ablation D) · **Hình 3.5** sơ đồ luồng dữ liệu

**3.3.3. Ambiguity — Distortion Loss** *(tác động CĐ4)* (~1,5 trang)
- Hai artifact có tên riêng: **floaters** và **background collapse**
- Công thức `L_dist` (Eq. 14-15) · tính trên không gian `s` chứ không trên `t` (paper nêu rõ lý do)
- ⚠️ **Phát hiện quan trọng (Ablation B):** bỏ `L_dist` **không** làm PSNR/SSIM/LPIPS xấu đi (PSNR còn nhỉnh hơn: 24.41 vs 24.37), chỉ sinh floaters thấy trên depth map → **không được viết "L_dist cải thiện PSNR"**
- **Hình 3.6** depth map có/không `L_dist`

## 3.4. GIẢI THUẬT — Tiến trình hoạt động của hệ thống 🟢 (~2,5 trang)

> ⚠️ **LƯU Ý 5** — thầy yêu cầu trình bày rõ tiến trình **cả giai đoạn học lẫn giai đoạn kiểm thử**. Tách thành 2 mục riêng, 2 sơ đồ riêng.

### 3.4.1. Giai đoạn học (Training)

> ⚠️ **LƯU Ý 4** — phải nêu rõ input, ground truth, cách đánh nhãn, loss function.

**Bảng 3.5 — Đặc tả giai đoạn học:**

| Thành phần | Nội dung |
|---|---|
| **Input** | Tập ảnh `{Iᵢ}` + pose `(Kᵢ,Rᵢ,Cᵢ)` từ CĐ1 |
| **Output xác thực (ground truth)** | **Màu RGB thật của từng pixel** trong các ảnh đã chụp |
| **Cách đánh nhãn** | ⭐ **Không cần đánh nhãn thủ công.** Bản thân ảnh chụp chính là nhãn — mỗi pixel `(u,v)` của ảnh `Iᵢ` tương ứng một tia, và màu pixel đó là giá trị đích mà tia phải render ra. Đây là bài toán **tự giám sát (self-supervised)** — khác hẳn các bài toán thị giác máy tính cần người gán nhãn thủ công |
| **Loss function** | `L = L_recon + λ_prop·L_prop + λ_dist·L_dist` — trong đó `L_recon` là MSE giữa màu render và màu thật, `L_prop` là distillation loss cho proposal network, `L_dist` là distortion loss |
| **Tham số được tối ưu** | `Θ` = trọng số của NeRF MLP và Proposal MLP |
| **Thuật toán tối ưu** | Adam, learning rate giảm theo lịch |

**Hình 3.7 — Sơ đồ giai đoạn học:**
```
Ảnh + pose → chọn batch tia → lấy mẫu (contract, disparity) → Proposal MLP
    → resample → NeRF MLP → volume rendering → Ĉ(r)
                                                   │
         Màu pixel thật C(r) ────────────────────► So sánh → Loss
                                                              │
                                              Backpropagation ▼
                                                   Cập nhật Θ ──┐
                                                                │
                            (lặp N vòng) ◄──────────────────────┘
```

**Mã giả một vòng lặp huấn luyện** — viết đầy đủ như trong dàn ý.

### 3.4.2. Giai đoạn kiểm thử / suy luận (Testing / Inference)

**Bảng 3.6 — Đặc tả giai đoạn kiểm thử:**

| Thành phần | Nội dung |
|---|---|
| **Input** | `Θ` đã học xong (cố định) + camera pose mới `(R,C)` do người dùng chọn |
| **Ground truth** | **Không có** — đây là góc nhìn chưa từng chụp. *(Riêng khi đánh giá trên tập test thì có, vì tập test được giữ lại từ đầu)* |
| **Output** | Ảnh RGB hoàn chỉnh ở góc nhìn mới |
| **Có backpropagation?** | **Không** — chỉ forward pass thuần |

**Hình 3.8 — Sơ đồ giai đoạn kiểm thử:**
```
Pose mới (R,C) → với MỖI pixel (u,v):
                     sinh tia → lấy mẫu → Proposal MLP → resample
                     → NeRF MLP → volume rendering → 1 màu pixel
                 → ghép toàn bộ pixel → ẢNH OUTPUT
```

> **Điểm cần nhấn mạnh khi viết:** sự khác nhau giữa 2 giai đoạn không chỉ là "có/không backprop" mà còn ở chỗ: giai đoạn học **lấy ngẫu nhiên** batch tia từ nhiều ảnh khác nhau, còn giai đoạn kiểm thử phải chạy **toàn bộ** pixel của một ảnh theo đúng thứ tự.

### 3.4.3. Bảng siêu tham số
Trích đầy đủ từ paper: số vòng lặp, batch size, learning rate và lịch giảm, hệ số `λ` của từng thành phần loss, kích thước mạng, số mẫu mỗi lượt.

## 3.5. Tổng hợp: Mip-NeRF 360 thay đổi gì so với NeRF 🟢 (~1 trang)

**Bảng 3.7 — Đối chiếu theo công đoạn:**

| Thành phần | Công đoạn | NeRF (2020) | Mip-NeRF 360 (2022) | Nguồn cải tiến | Lý do | Hệ quả |
|---|---|---|---|---|---|---|
| Đơn vị lấy mẫu | CĐ3 | Tia mảnh | Hình nón cụt → Gaussian | Mip-NeRF 2021 | Pixel là vùng | Hết răng cưa |
| Mã hóa input | CĐ2 | PE của điểm | Off-axis IPE của vùng | Mip-NeRF + **mới ở 360** | Gaussian dị hướng sau contract | SSIM 0.664→0.687 |
| Không gian | CĐ2 | Tọa độ gốc | Scene contraction | **Mới ở 360** | Nén vô cực vào hữu hạn | Hỗ trợ 360° |
| Lấy mẫu trên tia | CĐ3 | Tuyến tính theo `t` | Đều theo `s` (disparity) | **Mới ở 360** | Phân bổ mẫu hợp lý | `t_far=∞` hợp lệ |
| Mạng dẫn đường | CĐ3+CĐ4 | Coarse MLP (có màu) | Proposal MLP (chỉ density) | **Mới ở 360** | Tách vai trò | Train nhanh ~300% |
| Chính quy hóa | CĐ4 | Không có | Distortion loss | **Mới ở 360** | Chống floaters | Depth map sạch hơn |

**Nguyên liệu:** `02-TaiLieuHoc/pipeline_MipNeRF360.md` (1.615 dòng, đã verify với paper)

---

# CHƯƠNG 4 — CÀI ĐẶT VÀ THỬ NGHIỆM (~11 trang) 🔴

> ⚠️ **`phuongphap.rtf` 2.7:** môi trường (phần cứng, phần mềm) · tập dữ liệu · bảng kết quả · đánh giá
> ⚠️ **LƯU Ý 6:** độ đo phải có **cả độ chính xác lẫn độ phức tạp tính toán**, và phải phân tích **quan hệ loss ↔ độ đo**
> ⚠️ **LƯU Ý 7:** mô tả dataset phải nêu **thách thức**, số mẫu, tính đa dạng, tiêu chí xây dựng

## 4.1. Môi trường cài đặt (~1 trang)

**4.1.1. Ràng buộc phần cứng và cách xử lý**
- Máy cá nhân: MacBook Apple M2 Pro, 16GB RAM — **không có GPU NVIDIA/CUDA**; `tiny-cuda-nn` là CUDA kernel, không chạy trên Apple Silicon
- Giải pháp: Google Colab / Kaggle
- **Bảng 4.1:** đối chiếu phần cứng — máy cá nhân vs GPU Colab vs TPU v2 32 nhân của paper gốc. Bảng này giải thích trước mọi khác biệt về thời gian/kết quả ở mục 4.6

**4.1.2. Phần mềm** — bảng liệt kê phiên bản Python, PyTorch, CUDA, nerfstudio, COLMAP (để người đọc tái lập được)

## 4.2. Lựa chọn và điều chỉnh mã nguồn (~1 trang)

**4.2.1.** Bản gốc `multinerf` (Google, JAX) — vì sao **không** dùng trực tiếp
**4.2.2.** Bản dùng thực tế: `nerfacto` — **bảng đối chiếu trung thực kế thừa gì:**

| Thành phần Mip-NeRF 360 | `nerfacto` | Ghi chú |
|---|---|---|
| Scene contraction | ✅ | Giữ nguyên |
| Proposal network + online distillation | ✅ | Giữ nguyên |
| Distortion loss | ✅ | Giữ nguyên |
| Off-axis IPE | ❌ thay bằng hash encoding | Đánh đổi để tăng tốc |
| MLP 8×1024 | ❌ thay bằng MLP nhỏ + hash grid | Đánh đổi để tăng tốc |

> ⚠️ **Phải viết rõ.** Giấu đi mà bị hỏi là mất điểm nặng; trình bày trung thực kèm lý do thì thành điểm cộng.

**4.2.3. Phần tự viết** *(thầy yêu cầu: "tận dụng source code có sẵn **và tự viết**")*
- Script tiền xử lý dữ liệu tự chụp (lọc ảnh mờ, resize, chuẩn hóa tên)
- Script chạy COLMAP tự động + kiểm tra chất lượng pose
- **Script đánh giá:** tính PSNR/SSIM/LPIPS, đo thời gian, đếm số truy vấn mạng, xuất bảng
- Notebook tổng hợp tái lập toàn bộ thử nghiệm
- Script dựng video demo

## 4.3. Tập dữ liệu (~2 trang)

> ⚠️ **LƯU Ý 7** — mục này thầy nhấn mạnh.

**4.3.1. Tiêu chí xây dựng tập mẫu** — nêu rõ chọn dữ liệu theo nguyên tắc gì (phải chứa đúng thách thức mà phương pháp nhắm giải quyết: cảnh unbounded, chi tiết đa tỉ lệ)

**4.3.2. Dataset chuẩn** — chọn 1-2 cảnh từ bộ Mip-NeRF 360

**Bảng 4.2 — Mô tả dataset:**

| Thuộc tính | Nội dung |
|---|---|
| Số lượng mẫu | Số ảnh train / test |
| Độ phân giải | |
| Cách chia train/test | Theo quy ước của paper (giữ lại mỗi ảnh thứ 8) |
| **Cách "đánh nhãn"** | Tự giám sát — ảnh chụp chính là nhãn, không có khâu gán nhãn thủ công |
| **Tính đa dạng** | Trong nhà / ngoài trời, vật thể gần / nền xa |
| **⭐ Thách thức chứa trong dữ liệu** | Cảnh unbounded (nền tới chân trời), chi tiết đa tỉ lệ (lá cây mảnh ↔ toàn cảnh), bề mặt phản chiếu, ánh sáng ngoài trời thay đổi giữa các ảnh, vùng ít ảnh quan sát |

**4.3.3. Dataset tự thu thập** *(phần thể hiện công sức riêng)*
- Quy trình chụp: thiết bị, số ảnh, cách di chuyển camera, điều kiện ánh sáng
- **Thách thức cố ý đưa vào:** chọn cảnh có cả vật thể gần lẫn nền xa, có bề mặt phản chiếu → để kiểm chứng đúng khả năng mà Mip-NeRF 360 tuyên bố
- **Hình 4.1:** vài ảnh mẫu · Lỗi gặp phải khi chụp và cách khắc phục

**4.3.4. Tiền xử lý bằng COLMAP** *(ứng với CĐ1)*
- Quy trình: ảnh thô → feature extraction → matching → sparse reconstruction → xuất pose
- **Hình 4.2:** kết quả COLMAP (sparse point cloud + vị trí camera)
- Số liệu chất lượng CĐ1: số ảnh đăng ký thành công / tổng, số điểm 3D, **reprojection error trung bình**

## 4.4. Độ đo đánh giá (~1,5 trang) ⭐ MỤC THẦY NHẤN MẠNH

> ⚠️ **LƯU Ý 6** — phải có **cả hai nhóm độ đo**, và phải phân tích **quan hệ giữa loss function và độ đo**.

### 4.4.1. Nhóm độ đo độ chính xác

| Độ đo | Đo cái gì | Chiều tốt | Đặc điểm |
|---|---|---|---|
| **PSNR** | Sai khác pixel theo nghĩa số học, dẫn từ MSE | ↑ cao hơn tốt | Dễ tính, nhưng không phản ánh cảm nhận thị giác |
| **SSIM** | Tương đồng về cấu trúc (độ sáng, tương phản, cấu trúc cục bộ) | ↑ cao hơn tốt | Gần cảm nhận người hơn PSNR |
| **LPIPS** | Khác biệt theo cảm nhận, đo bằng đặc trưng của mạng học sẵn | ↓ thấp hơn tốt | Gần cảm nhận người nhất |

### 4.4.2. Nhóm độ đo độ phức tạp tính toán

| Độ đo | Ý nghĩa |
|---|---|
| Thời gian huấn luyện | Giờ/cảnh trên phần cứng cụ thể |
| Thời gian kết xuất | Giây/ảnh hoặc FPS |
| **Số lần truy vấn mạng trên mỗi tia** | Độ phức tạp thuật toán, độc lập phần cứng — con số này **so sánh công bằng hơn** thời gian |
| Số tham số mô hình | Dung lượng lưu trữ |
| Bộ nhớ GPU tiêu thụ khi train | Ràng buộc triển khai thực tế |

> **Lưu ý khi viết:** nên nhấn mạnh *số lần truy vấn mạng/tia* vì đây là độ đo **không phụ thuộc phần cứng** — khắc phục được vấn đề mỗi paper đo trên máy khác nhau.

### 4.4.3. ⭐ Quan hệ giữa loss function và độ đo đánh giá

> ⚠️ **LƯU Ý 6** — thầy cảnh báo lỗi *"học một đằng, đánh giá một nẻo"*. Đây là mục thể hiện hiểu sâu.

**Nội dung cần phân tích:**

| Độ đo | Có được tối ưu trực tiếp bởi loss không? | Phân tích |
|---|---|---|
| **PSNR** | ✅ **Có** — quan hệ trực tiếp | `L_recon` là MSE; mà `PSNR = 10·log₁₀(MAX²/MSE)`. Giảm MSE **tương đương** tăng PSNR. Đây là trường hợp "học đúng cái mình đánh giá" |
| **SSIM** | ❌ Không | Mô hình không hề tối ưu cấu trúc cục bộ; SSIM cải thiện chỉ là **hệ quả gián tiếp** của việc giảm MSE |
| **LPIPS** | ❌ Không | Mô hình không tối ưu đặc trưng tri giác |

**Hệ quả cần nêu — đây là chỗ ăn điểm:**
- Vì chỉ MSE được tối ưu, mô hình có xu hướng cho ảnh **hơi mờ** (mờ đều thì MSE thấp hơn là sắc nét nhưng lệch chi tiết) → giải thích vì sao PSNR cao mà LPIPS vẫn có thể kém
- Liên hệ với Ablation B của paper: bỏ `L_dist` làm PSNR **tăng nhẹ** nhưng sinh floaters — minh chứng rõ ràng rằng **tối ưu đúng độ đo chưa chắc cho kết quả tốt về mặt thị giác**
- Đây chính xác là hiện tượng thầy cảnh báo, và việc nhận ra nó cho thấy hiểu bản chất
- Ghi chú: 3D Gaussian Splatting dùng `L1 + D-SSIM` — tức **có** tối ưu SSIM trực tiếp, khác với NeRF

## 4.5. Kịch bản thử nghiệm (~0,5 trang)

| Mã | Mục đích | Dữ liệu | Cấu hình |
|---|---|---|---|
| TN1 | Đối chiếu với số liệu paper | 1-2 cảnh dataset chuẩn | `nerfacto` mặc định |
| TN2 | Kiểm chứng trên dữ liệu tự thu thập | Dataset tự chụp | `nerfacto` mặc định |
| TN3 | So sánh với baseline | Cùng dữ liệu TN2 | `nerfacto` vs `instant-ngp` |
| TN4 | **Ablation** — vai trò từng thành phần | Cùng dữ liệu TN2 | Bật/tắt distortion loss; đổi số proposal samples |

> TN4 là phần ăn điểm: paper top đầu nào cũng có ablation. Chỉ cần 1-2 cấu hình là đủ chứng minh hiểu cơ chế.

## 4.6. Kết quả (~3 trang)

**4.6.1. Kết quả định lượng**
- **Bảng 4.3:** TN1 — kết quả của ta vs số liệu paper trên cùng cảnh (cột: PSNR, SSIM, LPIPS, thời gian train, số vòng lặp)
- **Bảng 4.4:** TN2 + TN3 — so sánh phương pháp trên dữ liệu tự chụp, **có cả cột độ phức tạp tính toán** (thời gian, FPS, số tham số, VRAM)

**4.6.2. Kết quả định tính**
- **Hình 4.3:** Ground truth | Kết quả của ta | Baseline — có khung phóng to vùng chi tiết
- **Hình 4.4:** depth map — kiểm tra hình học có sạch không, có floaters không
- **Hình 4.5:** vài khung hình từ video quay camera quanh cảnh

**4.6.3. Ablation Study (TN4)**

**Bảng 4.5:**

| Cấu hình | PSNR | SSIM | LPIPS | Thời gian | Quan sát định tính |
|---|---|---|---|---|---|
| Đầy đủ | | | | | |
| Bỏ distortion loss | | | | | Kỳ vọng: số không xấu đi nhiều nhưng depth map có floaters |
| Giảm proposal samples | | | | | |

> Nếu kết quả trùng phát hiện của paper (bỏ `L_dist` không làm PSNR xấu đi) thì đây là điểm rất mạnh — chứng minh tái lập được đúng hành vi paper mô tả, và **minh họa trực tiếp cho phân tích ở mục 4.4.3**.

## 4.7. Đánh giá và thảo luận (~2 trang)

**Trả lời thẳng các câu hỏi:**

1. **Kết quả có đạt như paper không?** Nếu thấp hơn, phân tích: khác phần cứng, khác implementation (`nerfacto` vs bản gốc), số vòng lặp ít hơn, dữ liệu tự chụp khó hơn
2. **Đánh giá theo từng công đoạn** *(gắn lại với trục công đoạn xuyên suốt báo cáo)*:

| Công đoạn | Quan sát thực nghiệm |
|---|---|
| CĐ1 | COLMAP đăng ký được bao nhiêu % ảnh? Reprojection error? Có ảnh nào thất bại không, vì sao? |
| CĐ2 | Dung lượng mô hình, có đủ dung lượng biểu diễn chi tiết không |
| CĐ3 | Thời gian render/ảnh, số mẫu/tia thực tế |
| CĐ4 | Loss hội tụ thế nào, có floaters không, cần bao nhiêu vòng lặp |

3. **Artifact quan sát được:** floaters ở đâu, vùng nào mờ → đối chiếu với hạn chế paper tự nêu
4. **Hạn chế của chính quá trình thử nghiệm:** số cảnh ít, chưa chạy đủ vòng lặp, giới hạn phiên Colab

---

# CHƯƠNG 5 — KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN (~3 trang)

## 5.1. Kết luận (~1 trang)
- Tóm tắt đã làm gì: khảo sát theo 4 công đoạn, trình bày chi tiết Mip-NeRF 360, cài đặt và thử nghiệm
- Kết quả chính (nêu con số)
- Bài học: về kỹ thuật (cơ chế nào quan trọng) và về quy trình (dựng môi trường sớm, đọc paper gốc thay vì tài liệu thứ cấp)

## 5.2. Hạn chế của đồ án (~0,75 trang)
- **Phần cứng:** không có GPU riêng, phụ thuộc Colab
- **Cài đặt:** dùng `nerfacto` thay bản gốc → không tái lập chính xác 100% kết quả paper
- **Phạm vi:** ít cảnh thử nghiệm, chưa thử hết cấu hình, chưa so sánh được toàn bộ phương pháp ở Chương 2

## 5.3. Hướng phát triển (~1,25 trang)

**5.3.1. Hướng kỹ thuật** — mỗi hướng nêu rõ *giải quyết khuyết điểm nào ở công đoạn nào* (gắn với Bảng 2.3):
- **Zip-NeRF (ICCV 2023)** — gộp scene contraction + IPE (CĐ2,3) với hash grid (CĐ2) → khắc phục khuyết điểm *độ phức tạp tính toán* mà ta gặp phải
- **3D Gaussian Splatting (SIGGRAPH 2023)** — chuyển CĐ3 sang rasterization → real-time
- **Mip-Splatting (CVPR 2024)** — mang chống răng cưa sang 3DGS
- **Hướng pose-free NeRF** — giải khuyết điểm ở CĐ1 (phụ thuộc chất lượng SfM)

**5.3.2. Hướng ứng dụng** — số hóa không gian cụ thể, tích hợp web 3D, tối ưu cho thiết bị di động

---

# TÀI LIỆU THAM KHẢO (~2 trang)

16 tài liệu trong `03-Reference/`. **Thống nhất chuẩn IEEE**, trích dẫn dạng `[1]`, `[2]`.

# PHỤ LỤC

- **PL A:** Mã nguồn các script tự viết
- **PL B:** Hướng dẫn tái lập thử nghiệm trên Colab
- **PL C:** Bảng phân công công việc chi tiết
- **PL D:** Ảnh/video kết quả bổ sung

---

# BẢNG PHÂN CÔNG CÔNG VIỆC

> ⚠️ **`phuongphap.rtf` 2.9** — bảng phân công cho từng thành viên với mốc thời gian cụ thể.

**Nguyên tắc:** hai hướng song song — *lý thuyết/báo cáo* và *cài đặt/thực nghiệm*. Chương 3 là trọng tâm nên cả hai cùng tham gia.

| Tuần | Thành viên 1 (Bùi Văn Thiên) | Thành viên 2 | Mốc kiểm tra |
|---|---|---|---|
| 1 | Đọc 3 survey; viết mục 1.3 (framework + **ẩn số từng công đoạn**) | **Dựng môi trường Colab, chạy thử dataset mẫu** | ⚠️ Phải có ảnh render đầu tiên |
| 2 | Viết Chương 2 mục 2.1-2.3 (theo khuôn 4 công đoạn) | Chạy thành công TN1 trên dataset chuẩn | Có kết quả TN1 |
| 3 | Viết mục 2.4-2.5 (**bảng so sánh theo công đoạn** + bảng khuyết điểm tồn đọng) + Chương 1 | Đọc paper Mip-NeRF 2021, viết mục 3.2 | **Nộp thầy duyệt dàn ý + Chương 1-2** |
| 4 | Viết Chương 3 mục 3.0-3.1 | Chụp dữ liệu thật, chạy COLMAP | Có dataset tự chụp đã xử lý |
| 5 | Viết mục 3.1 (tiếp) | Train TN2 trên dataset tự chụp | Có kết quả TN2 |
| 6 | Viết mục 3.3 | Chạy TN3 (so sánh baseline) | Xong nháp Chương 3 |
| 7 | Viết mục 3.4 (**2 sơ đồ học/kiểm thử**) + 3.5 | Chạy TN4 (ablation), dựng video demo | Đủ dữ liệu cho Chương 4 |
| 8 | Viết Chương 4 mục 4.1-4.3 | Tổng hợp bảng kết quả, chuẩn bị hình so sánh | Xong nửa đầu Chương 4 |
| 9 | Viết mục 4.4 (**độ đo + quan hệ loss↔độ đo**), 4.5-4.7 | Hỗ trợ phân tích, viết mục 4.6.3 | **Xong Chương 4** |
| 10 | Viết Chương 5, phần mở đầu, tài liệu tham khảo | Làm slide, chuẩn bị phụ lục | Bản báo cáo đầy đủ |
| 11 | **Rà soát theo bảng kiểm 13 mục** trong `yeu-cau-cua-thay.md` | Hoàn thiện slide, tập thuyết trình | Bản hoàn chỉnh |
| 12 | Dự phòng, sửa theo góp ý | Dự phòng, tập thuyết trình | **Nộp + bảo vệ** |

> ⚠️ **Rủi ro lớn nhất là môi trường cài đặt ở Chương 4** → xếp vào **tuần 1**. Nếu hết tuần 2 vẫn chưa train được dataset mẫu thì phải báo động và đổi phương án (thuê GPU cloud, mượn máy có GPU NVIDIA).

---

# VIỆC CẦN LÀM NGAY

| # | Việc | Vì sao ưu tiên |
|---|---|---|
| 1 | **Dựng môi trường Colab + train thử dataset mẫu** | Gỡ rủi ro lớn nhất; mọi thứ ở Chương 4 phụ thuộc vào đây |
| 2 | **Gửi dàn ý này cho thầy duyệt** | Rẻ nhất để sửa hướng |
| 3 | **Đọc 3 survey** → viết Chương 2 | Nguyên liệu sẵn, làm được ngay |
| 4 | **Đọc paper Mip-NeRF 2021** | Lấp các chỗ `[MIP-NỀN]` chưa verify ở mục 3.2 |

---

# ✅ BẢNG KIỂM ĐỐI CHIẾU 8 LƯU Ý CỦA THẦY

| Lưu ý | Yêu cầu | Dàn ý đáp ứng ở đâu |
|---|---|---|
| **1** | Framework tổng quát, không nhắc phương pháp cụ thể | Mục 1.3.2 — bảng 4 công đoạn chỉ nêu "các hướng giải pháp khả dĩ" |
| **2** | Xác định ẩn số từng công đoạn | Mục 1.3.3 — **Bảng 1.1** (đã cho / ẩn số / ràng buộc) |
| **3** | So sánh theo cùng cột tiêu chí ứng với công đoạn | Mục 2.3 (khuôn 5 mục chung) + mục 2.4 **Bảng 2.1** (cột = công đoạn) |
| **4** | Ground truth, cách đánh nhãn, loss function | Mục 3.4.1 — **Bảng 3.5**, nhấn mạnh tính **tự giám sát** |
| **5** | Tiến trình giai đoạn học và kiểm thử | Mục 3.4.1 + 3.4.2 — **2 sơ đồ riêng** (Hình 3.7, 3.8) |
| **6** | Độ chính xác + độ phức tạp tính toán + quan hệ loss↔độ đo | Mục 4.4 — 3 mục con, đặc biệt **4.4.3** phân tích "học một đằng đánh giá một nẻo" |
| **7** | Dataset: đánh nhãn, số mẫu, đa dạng, **thách thức** | Mục 1.3.5 **Bảng 1.2** + mục 4.3 **Bảng 4.2** |
| **8** | Khuyết điểm tồn đọng theo công đoạn | Mục 2.2.2 (hạn chế NeRF theo công đoạn) + mục 2.5 **Bảng 2.3** |
