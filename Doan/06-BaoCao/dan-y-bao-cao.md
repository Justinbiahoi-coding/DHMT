# DÀN Ý CHI TIẾT BÁO CÁO ĐỒ ÁN

**Đề tài:** Xây dựng ứng dụng kết xuất ảnh (rendering) với góc nhìn tùy ý dựa vào dãy ảnh 2D cho trước — Tìm hiểu mô hình NeRF và NeRF cải tiến

**Nhóm:** 2 thành viên — Bùi Văn Thiên (24120138) và [tên thành viên 2]
**Lớp:** Đồ Họa Máy Tính CQ2024/23
**Phương pháp chọn trình bày:** Mip-NeRF 360 (Barron et al., CVPR 2022)
**Độ dài dự kiến:** 35-45 trang

---

## NGUYÊN TẮC TRÌNH BÀY — HỌC TỪ CÁC PAPER TOP ĐẦU

Trước khi vào dàn ý, đây là 6 nguyên tắc rút ra từ cách NeRF (ECCV 2020), Mip-NeRF 360 (CVPR 2022) và Instant-NGP (SIGGRAPH 2022) tổ chức nội dung. Áp dụng xuyên suốt báo cáo.

**1. Nêu vấn đề trước, giải pháp sau.** Mip-NeRF 360 mở đầu phần phương pháp bằng cách tuyên bố rõ **ba vấn đề** cần giải (Parameterization, Efficiency, Ambiguity), rồi dành mỗi mục cho một vấn đề. Người đọc luôn biết "đang đọc cái này để giải quyết chuyện gì". → Chương 3 của ta bắt chước đúng cấu trúc này.

**2. Có mục "Preliminaries" (Kiến thức nền) trước khi trình bày cải tiến.** Mip-NeRF 360 dành hẳn mục 1 để tóm tắt lại mip-NeRF trước khi nói mình thay đổi gì. Không có mục này, người đọc không phân biệt được đâu là đóng góp mới. → Chương 3 mục 3.1 và 3.2 đóng vai trò này.

**3. Mỗi công thức phải có bảng ký hiệu.** Paper top đầu luôn định nghĩa mọi ký hiệu ngay khi xuất hiện lần đầu. → Lập 1 bảng "Danh mục ký hiệu" ở đầu báo cáo, và nhắc lại ngắn khi dùng.

**4. Kết quả phải có cả định lượng và định tính.** Bảng số (PSNR/SSIM/LPIPS) chứng minh "tốt hơn bao nhiêu"; ảnh đặt cạnh nhau chứng minh "tốt hơn ở chỗ nào". Thiếu một trong hai là yếu. → Chương 4 mục 4.5.

**5. Phải có Ablation Study.** Tắt từng thành phần rồi đo lại — đây là cách chứng minh "thành phần này thực sự cần thiết", không phải thêm vào cho đẹp. Cả NeRF lẫn Mip-NeRF 360 đều có. → Chương 4 mục 4.6 (làm được bao nhiêu thì làm, có còn hơn không).

**6. Trung thực về hạn chế.** Mọi paper top đầu đều có mục Limitations. Mip-NeRF 360 tự thừa nhận yếu ở đâu; Instant-NGP tự nhận artifact "grainy microstructure" không mất đi dù train lâu. Thầy đánh giá cao sự trung thực hơn là báo cáo hoàn hảo giả tạo. → Chương 4 mục 4.7 và Chương 5 mục 5.2.

**Chú thích trạng thái nguyên liệu:** 🟢 viết được ngay · 🟡 có một phần · 🔴 chưa có gì

---

# PHẦN MỞ ĐẦU (~4 trang)

| Thành phần | Nội dung cụ thể |
|---|---|
| Trang bìa | Tên trường/khoa, tên đồ án, tên môn, nhóm, GVHD (PGS.TS Lý Quốc Ngọc), năm |
| Lời cảm ơn | ~半 trang |
| Mục lục | Tự động sinh, tới mục cấp 3 |
| Danh mục hình | Đánh số theo chương (Hình 3.1, Hình 3.2...) |
| Danh mục bảng | Tương tự |
| **Danh mục từ viết tắt** | NeRF, MLP, SfM, COLMAP, PSNR, SSIM, LPIPS, IPE, PE, NDC, SH, 3DGS, GPU, TPU, CUDA, RGB, SDF |
| **Danh mục ký hiệu toán học** | `x`(vị trí 3D), `d`(hướng nhìn), `o`(gốc tia), `t`(tham số tia), `σ`(density), `c`(màu), `T`(transmittance), `α`(opacity), `γ(·)`(positional encoding), `μ,Σ`(mean/covariance), `Θ`(trọng số mạng) |

**Tóm tắt (Abstract) — ~200 từ, viết sau cùng.** Cấu trúc 4 câu theo chuẩn paper:
1. *Bối cảnh:* bài toán tổng hợp góc nhìn mới và tầm quan trọng
2. *Khoảng trống:* NeRF gốc còn hạn chế gì
3. *Việc đã làm:* khảo sát N phương pháp, trình bày chi tiết Mip-NeRF 360, cài đặt thử nghiệm
4. *Kết quả:* con số cụ thể đạt được

---

# CHƯƠNG 1 — GIỚI THIỆU (~5 trang)

> Bám sát đúng 4 mục thầy yêu cầu trong `huongdantrinhbay.rtf`, thêm mục 1.5 về bố cục.

## 1.1. Ý nghĩa khoa học của chủ đề 🟡 (~1 trang)

**Nội dung cần viết — 4 đoạn:**

- **Đoạn 1 — Đặt vấn đề.** Con người nhìn một vật từ vài góc là hình dung được toàn bộ hình dạng 3D của nó. Máy tính làm điều tương tự khó ở chỗ nào: ảnh 2D đã mất thông tin độ sâu, một pixel ứng với vô số điểm 3D khả dĩ. Bài toán **tổng hợp góc nhìn mới (novel view synthesis)** chính là khôi phục lại khả năng đó.

- **Đoạn 2 — Quá trình phát triển trước NeRF.** Tóm tắt ngắn hành trình: nội suy light field (cần ảnh dày đặc) → biểu diễn mesh (khó tối ưu, cần mesh mẫu) → voxel grid (bộ nhớ tăng lũy thừa theo độ phân giải) → neural implicit surface (cần dữ liệu 3D ground-truth). Mỗi hướng đều vướng một rào cản cơ bản.

- **Đoạn 3 — Vì sao NeRF là bước ngoặt.** Ba điểm: (a) chuyển từ biểu diễn **tường minh** (lưu từng điểm/mặt) sang **biểu diễn ẩn** — nén cả cảnh vào trọng số mạng nơ-ron vài MB; (b) chỉ cần ảnh RGB thường, không cần quét 3D hay dữ liệu ground-truth; (c) chất lượng đạt mức photorealistic lần đầu tiên.

- **Đoạn 4 — Vị trí trong bức tranh nghiên cứu hiện nay.** NeRF mở ra cả một nhánh nghiên cứu mới (neural rendering / radiance field). Nêu con số: lượng công trình kế thừa tăng vọt từ 2020, dẫn tới 3D Gaussian Splatting năm 2023.

**Hình cần có:** Hình 1.1 — minh họa trực quan bài toán (vài ảnh input ở các góc → ảnh output ở góc mới chưa chụp).

**Trích dẫn:** `Survey/2022 Advances in Neural Rendering` (phần Introduction), `Survey/2022 CVM Review`, `Selected/2020 NeRF` (Introduction), `Foundation/2019 LLFF`.

## 1.2. Ý nghĩa ứng dụng 🔴 (~1 trang)

**Nội dung cần viết — mỗi lĩnh vực 1 đoạn ngắn, nêu rõ *vì sao NeRF phù hợp*, không chỉ liệt kê:**

| Lĩnh vực | Góc nhìn cần nhấn |
|---|---|
| VR/AR, metaverse | Cần dựng môi trường 3D chân thực nhanh, chi phí thấp — thay vì mô hình hóa thủ công tốn hàng tháng |
| Số hóa di sản | Bảo tồn hiện vật/di tích không thể chạm vào; chỉ cần chụp ảnh thường |
| Thương mại điện tử | Xem sản phẩm 360°, thử đồ ảo — tăng tỉ lệ chuyển đổi |
| Bất động sản, du lịch | Tham quan ảo không gian thật |
| Robot, xe tự hành | Dựng bản đồ 3D môi trường từ camera giá rẻ thay vì LiDAR đắt tiền |
| Điện ảnh, VFX | Dựng cảnh từ footage quay thật, chèn vật thể ảo khớp ánh sáng |

**Lưu ý khi viết:** nêu 1-2 ví dụ cụ thể có thật (ví dụ Google dùng NeRF trong Immersive View của Maps) sẽ thuyết phục hơn liệt kê chung chung.

## 1.3. Phát biểu bài toán 🟢 (~1,5 trang)

> Thầy yêu cầu rõ ở `phuongphap.rtf` 2.4: Input, Output, các tác vụ cần thực hiện, tập dữ liệu thử nghiệm.

**1.3.1. Input**
- Tập ảnh RGB 2D: `{I₁, I₂, ..., I_N}`, thường N = 20-100 ảnh
- Điều kiện ràng buộc: cảnh **tĩnh** (vật thể và ánh sáng không đổi giữa các lần chụp), các ảnh có **độ chồng lấp** đủ lớn
- Kèm theo (hoặc phải ước lượng): tham số camera của từng ảnh — ma trận nội tại **K**, ma trận xoay **R**, tâm camera **C**

**1.3.2. Output**
- Ảnh RGB render tại một camera pose **tùy ý** chưa có trong tập input
- Mở rộng: chuỗi ảnh tạo thành video quay quanh cảnh; mô hình 3D dạng mesh (nếu cần)

**1.3.3. Các tác vụ cần thực hiện** — chia 4 tác vụ:
1. **Ước lượng tham số camera** từ tập ảnh (Structure-from-Motion)
2. **Xây dựng biểu diễn cảnh** có khả năng truy vấn tại điểm 3D bất kỳ
3. **Kết xuất ảnh** từ biểu diễn đó tại một góc nhìn cho trước
4. **Tối ưu hóa** biểu diễn sao cho ảnh render khớp với ảnh quan sát được

**1.3.4. Framework chung — 4 công đoạn** (chưa đi vào phương pháp cụ thể, đúng yêu cầu thầy)

```
Ảnh 2D  →  [1] Ước lượng   →  [2] Biểu diễn  →  [3] Kết xuất  →  Ảnh góc
            camera pose        cảnh 3D            ảnh            nhìn mới
                                   ↑                  │
                                   └── [4] Tối ưu ────┘
                                       (so với ảnh thật)
```

**Hình cần có:** Hình 1.2 — sơ đồ framework 4 công đoạn ở trên, vẽ đẹp lại bằng công cụ vẽ.

**1.3.5. Tập dữ liệu thử nghiệm chuẩn**
- **Blender Synthetic** (8 vật thể tổng hợp, 360°) — từ paper NeRF gốc
- **LLFF** (8 cảnh thật, forward-facing) — từ paper LLFF
- **Mip-NeRF 360 dataset** (9 cảnh thật 360° unbounded: 5 ngoài trời, 4 trong nhà) — bộ chính của đồ án
- Nêu rõ độ phân giải, số ảnh, cách chia train/test của từng bộ

## 1.4. Đóng góp của báo cáo 🟡 (~0,5 trang)

Viết dưới dạng danh sách gạch đầu dòng, mỗi ý 1-2 câu:

1. **Khảo sát có hệ thống** quá trình phát triển các phương pháp radiance field giai đoạn 2020-2024, phân loại theo vấn đề được giải quyết thay vì theo thời gian
2. **Trình bày chi tiết Mip-NeRF 360** đặt trong mạch kế thừa NeRF → Mip-NeRF → Mip-NeRF 360, làm rõ từng cải tiến giải quyết hạn chế nào
3. **Cài đặt thử nghiệm** trên cả dữ liệu chuẩn và dữ liệu tự thu thập, đánh giá định lượng (PSNR/SSIM/LPIPS) và định tính
4. **Phân tích hạn chế** của phương pháp qua quan sát thực nghiệm, và đối chiếu với các hướng phát triển mới nhất

> ⚠️ Thầy ghi rõ "SV chỉ cần đọc, hiểu, cài đặt lại. Chưa đòi hỏi đề xuất giải pháp mới" — nên **không** cố viết đóng góp kiểu "chúng tôi đề xuất phương pháp mới". Trung thực về phạm vi.

## 1.5. Bố cục báo cáo 🔴 (~0,5 trang)

Một đoạn giới thiệu nội dung từng chương còn lại.

---

# CHƯƠNG 2 — CÁC CÔNG TRÌNH NGHIÊN CỨU LIÊN QUAN (~9 trang)

> **Hai câu hỏi thầy yêu cầu phải trả lời được:** *Người ta đã làm gì rồi?* (mục 2.1-2.4) và *Mình muốn làm gì?* (mục 2.5)

## 2.1. Các phương pháp trước NeRF 🟡 (~1,5 trang)

**Nội dung cần viết — 4 nhóm, mỗi nhóm nêu: ý tưởng cốt lõi + hạn chế cơ bản:**

| Nhóm | Ý tưởng | Hạn chế |
|---|---|---|
| Light field / image-based rendering | Nội suy trực tiếp giữa các ảnh | Cần ảnh lấy mẫu rất dày |
| Mesh-based | Tối ưu lưới tam giác bằng differentiable rasterizer | Khó hội tụ (cực tiểu cục bộ), cần mesh mẫu có sẵn |
| Voxel grid | Lưu màu/mật độ trên lưới 3D rời rạc | Bộ nhớ tăng lũy thừa theo độ phân giải |
| Neural implicit surface (SDF, occupancy) | Học hàm khoảng cách/xác suất chiếm chỗ bằng MLP | Cần ground-truth 3D; kết quả bị mờ quá mức |

**Trích dẫn:** phần Related Work của `Selected/2020 NeRF`, `Foundation/2019 LLFF`, `Survey/2022 Advances in Neural Rendering`.

## 2.2. NeRF và các hạn chế 🟢 (~1,5 trang)

- Tóm tắt ý tưởng cốt lõi trong ~1 đoạn + 1 hình (chi tiết để dành Chương 3, **không trình bày trùng**)
- **Năm hạn chế** — mỗi hạn chế nêu rõ nguyên nhân kỹ thuật, vì đây là nền cho mục 2.3:

| # | Hạn chế | Nguyên nhân |
|---|---|---|
| 1 | Train rất chậm (1-2 ngày/cảnh) | Mỗi điểm mẫu phải qua MLP 8 lớp × 256 kênh; hàng trăm nghìn điểm mỗi batch |
| 2 | Render chậm, không real-time | Mỗi pixel cần 192 lần truy vấn mạng |
| 3 | Răng cưa khi đổi tỉ lệ/khoảng cách | Tia mảnh không biểu diễn được vùng không gian mà pixel thực sự bao phủ |
| 4 | Kém với cảnh 360° không giới hạn | Lấy mẫu tuyến tính theo `t`; NDC chỉ dùng được cho cảnh forward-facing |
| 5 | Phụ thuộc camera pose chính xác | Pose sai → các tia không giao đúng chỗ → hình học nhòe |

## 2.3. Các hướng cải tiến 🟢 (~3 trang)

> **Chia theo vấn đề được giải quyết, KHÔNG theo thứ tự thời gian.** Lý do: chia theo năm chỉ ra một danh sách liệt kê; chia theo vấn đề thì tự nhiên trả lời được câu hỏi "người ta đã làm gì rồi".

**Mỗi mục con viết theo cùng một khuôn (giúp người đọc dễ so sánh):** *Vấn đề → Ý tưởng cốt lõi → Cách làm → Kết quả đạt được → Hạn chế còn lại*

**2.3.1. Hướng tăng tốc huấn luyện** (~1 trang)
- **Instant-NGP** — hash encoding đa độ phân giải thay positional encoding; MLP thu nhỏ còn 2 mạng tí hon; occupancy grid bỏ qua vùng trống. Nhanh hơn 20-60× nhờ encoding (theo Table 2 của paper), cộng ~10× nhờ CUDA kernel.
- **Plenoxels** — bỏ hẳn mạng nơ-ron, lưu trực tiếp density + hệ số Spherical Harmonics trên voxel grid thưa. Chứng minh mạng nơ-ron không bắt buộc.
- **TensoRF** — phân rã tensor 4D thành các thành phần bậc thấp, giảm mạnh số tham số.

**2.3.2. Hướng chống răng cưa** (~0,5 trang)
- **Mip-NeRF** — hình nón cụt thay tia mảnh, Integrated Positional Encoding.
- **Mip-Splatting** — mang ý tưởng này sang 3D Gaussian Splatting.

**2.3.3. Hướng xử lý cảnh không giới hạn** (~0,75 trang)
- **NeRF++** — tách 2 mạng trong/ngoài khối cầu đơn vị, tham số hóa `(x',y',z',1/r)`.
- **Mip-NeRF 360** — scene contraction, một mạng duy nhất, co không gian liên tục.
- Nêu rõ: hai cách giải quyết **cùng một vấn đề** nhưng triết lý khác nhau (cắt cứng vs co liên tục).

**2.3.4. Hướng tăng tốc kết xuất** (~0,5 trang)
- **3D Gaussian Splatting** — từ bỏ ray-marching, chuyển sang rasterization; biểu diễn tường minh bằng hàng triệu Gaussian 3D; render real-time.

**2.3.5. Hướng kết hợp** (~0,25 trang)
- **Zip-NeRF** — gộp scene contraction + IPE của Mip-NeRF 360 với hash grid của Instant-NGP.

## 2.4. Bảng so sánh các giải pháp 🟡 (~1,5 trang)

> Thầy yêu cầu rõ: *"Lập bảng so sánh các giải pháp dựa trên một số tiêu chí tự chọn"*

**Bảng 2.1 — So sánh 8 phương pháp theo 8 tiêu chí:**

| Phương pháp | Năm | Venue | Kiểu biểu diễn | Thời gian train | Tốc độ render | Dung lượng | Cảnh hỗ trợ | Chống alias |
|---|---|---|---|---|---|---|---|---|
| NeRF | 2020 | ECCV | Ẩn (MLP) | ~1-2 ngày | Rất chậm | ~5 MB | Bounded | Không |
| NeRF++ | 2020 | arXiv | Ẩn (2 MLP) | Chậm hơn NeRF | Rất chậm | Lớn hơn | + Background ∞ | Không |
| Mip-NeRF | 2021 | ICCV | Ẩn (1 MLP) | ~NeRF | Rất chậm | ~5 MB | Bounded | **Có** |
| Plenoxels | 2022 | CVPR | Tường minh (voxel) | Phút | Nhanh | Hàng trăm MB | Bounded | Không |
| Instant-NGP | 2022 | SIGGRAPH | Lai (hash + MLP nhỏ) | **Giây-phút** | Gần real-time | ~10-100 MB | Bounded | Không |
| TensoRF | 2022 | ECCV | Tường minh (tensor) | Phút | Nhanh | Vừa | Bounded | Không |
| **Mip-NeRF 360** | 2022 | CVPR | Ẩn (MLP + prop net) | Giờ | Rất chậm | Vừa | **Unbounded 360°** | **Có** |
| 3D Gaussian Splatting | 2023 | SIGGRAPH | Tường minh (Gaussian) | Chục phút | **Real-time** | Hàng trăm MB-GB | Unbounded | Không |

**⚠️ Lưu ý bắt buộc khi viết bảng này:**
- Mỗi con số phải **ghi rõ nguồn** (paper nào, bảng nào) bằng chú thích dưới bảng
- Phải **ghi rõ điều kiện đo** (phần cứng, dataset) vì các paper đo trên cấu hình khác nhau — nếu không sẽ bị hỏi "sao so sánh TPU với GPU được?"
- Nếu lấy số từ survey thì ghi rõ survey nào

**Bảng 2.2 (tùy chọn) — So sánh định lượng trên cùng dataset.** Nếu tìm được bảng trong `Survey/2022 CVM Review` hoặc Table 1 của `Selected/2022 Mip-NeRF 360` đo nhiều phương pháp trên cùng bộ dữ liệu, trích lại — đây là so sánh công bằng nhất.

## 2.5. Nhận xét và định hướng của đồ án 🔴 (~1 trang)

**Trả lời trực tiếp câu hỏi "mình muốn làm gì":**

- **Nhận xét từ bảng so sánh:** không có phương pháp nào thắng tuyệt đối. Ba trục đánh đổi rõ ràng: *tốc độ* (Instant-NGP, Plenoxels, 3DGS) ↔ *chất lượng và phạm vi cảnh* (Mip-NeRF 360) ↔ *dung lượng* (biểu diễn ẩn gọn, tường minh nặng).
- **Lý do chọn Mip-NeRF 360:** (a) giải quyết đồng thời 2 trong 5 hạn chế của NeRF (răng cưa + cảnh unbounded); (b) đại diện cho nhánh biểu diễn ẩn đạt chất lượng cao nhất trước khi 3DGS xuất hiện; (c) nằm trong mạch kế thừa rõ ràng NeRF → Mip-NeRF → Mip-NeRF 360, thuận lợi để trình bày có hệ thống.
- **Phạm vi đồ án:** đọc hiểu, trình bày lại, cài đặt thử nghiệm. **Không** đề xuất phương pháp mới (đúng yêu cầu của thầy).

---

# CHƯƠNG 3 — PHƯƠNG PHÁP: MIP-NERF 360 (~14 trang) ⭐ TRỌNG TÂM

> **Yêu cầu của thầy (`phuongphap.rtf` 2.6):** trình bày theo mạch **nguyên lý → phương pháp → giải thuật → chương trình minh họa**
>
> **Cấu trúc học từ paper gốc:** Mip-NeRF 360 mở đầu bằng việc tuyên bố **ba vấn đề** rồi dành mỗi mục cho một vấn đề. Ta bắt chước cấu trúc này ở mục 3.3.

## 3.0. Dẫn nhập: ba vấn đề Mip-NeRF 360 giải quyết 🟢 (~0,5 trang)

Nêu ngay đầu chương, đặt khung cho toàn bộ phần sau:

| Vấn đề | Mô tả | Giải quyết ở mục |
|---|---|---|
| **Parameterization** (tham số hóa) | Cảnh 360° không giới hạn trải tới vô cực — không thể lấy mẫu tuyến tính | 3.3.1 |
| **Efficiency** (hiệu quả) | Cảnh lớn cần mạng dung lượng lớn, nhưng truy vấn mạng lớn dày đặc dọc tia thì quá tốn | 3.3.2 |
| **Ambiguity** (mơ hồ) | Nội dung cảnh unbounded có thể nằm ở bất kỳ độ sâu nào, ít ảnh quan sát → sinh artifact | 3.3.3 |

## 3.1. NGUYÊN LÝ — Nền tảng NeRF 🟢 (~4 trang)

> Đây là tầng "nguyên lý" trong mạch thầy yêu cầu.

**3.1.1. Biểu diễn cảnh bằng trường bức xạ 5D** (~0,5 trang)
- Hàm `F_Θ: (x, d) → (c, σ)` — giải thích "trường" (field) theo nghĩa vật lý
- Vì sao gọi là biểu diễn **ẩn**: cảnh nằm trong trọng số, không lưu tường minh điểm/mặt nào
- Vì sao dùng mạng nơ-ron: định lý xấp xỉ phổ quát (universal approximation)
- **Bảng 3.1:** chú thích ký hiệu `x, d, c, σ, Θ`

**3.1.2. Mô hình camera và sinh tia** (~1 trang)
- Mô hình pinhole camera, phép chiếu phối cảnh (tam giác đồng dạng): `x_img = f·X/Z`
- Ma trận nội tại **K** (fx, fy, cx, cy) và ngoại tại (**R**, **C**)
- Công thức từ pixel ra hướng tia, rồi `r(t) = o + t·d`
- **Hình 3.1:** sơ đồ pinhole camera + tia xuyên qua pixel

**3.1.3. Lấy mẫu phân tầng (stratified sampling)** (~0,5 trang)
- Công thức chia `[t_n, t_f]` thành N đoạn, lấy ngẫu nhiên trong mỗi đoạn
- Vì sao **không** dùng lưới cố định: tránh giới hạn độ phân giải như voxel grid

**3.1.4. Positional Encoding** (~0,5 trang)
- Công thức `γ(p) = (sin(2⁰πp), cos(2⁰πp), ..., sin(2^(L-1)πp), cos(2^(L-1)πp))`
- Vấn đề **spectral bias**: mạng sâu thiên về học hàm tần số thấp
- Giá trị L=10 cho vị trí (→60 chiều), L=4 cho hướng (→24 chiều)

**3.1.5. Kiến trúc MLP** (~0,5 trang)
- 8 lớp × 256 kênh, skip connection, rẽ nhánh σ và màu
- **Điểm thiết kế quan trọng:** σ chỉ phụ thuộc vị trí, màu phụ thuộc cả vị trí lẫn hướng nhìn → đảm bảo nhất quán đa góc nhìn, đồng thời mô phỏng được hiệu ứng view-dependent
- **Hình 3.2:** sơ đồ kiến trúc mạng kèm số chiều từng lớp

**3.1.6. Volume Rendering** (~0,75 trang)
- Định nghĩa chính xác σ: xác suất vi phân tia kết thúc tại điểm đó
- Công thức tích phân liên tục `C(r) = ∫ T(t)·σ(r(t))·c(r(t),d) dt`, với `T(t) = exp(-∫σ ds)`
- Dẫn `T(t)` từ phương trình vi phân suy giảm mũ (định luật Beer-Lambert)
- Công thức rời rạc `Ĉ(r) = Σ Tᵢ·αᵢ·cᵢ` và chứng minh đây là tổng Riemann xấp xỉ tích phân
- **Bảng 3.2:** chú thích `T, α, δ`
- **Ví dụ số minh họa:** 3 điểm mẫu, cho thấy điểm bề mặt chi phối màu, điểm phía sau bị che

**3.1.7. Hierarchical sampling và hàm loss** (~0,5 trang)
- Hai mạng coarse/fine, trọng số `wᵢ = Tᵢαᵢ`, inverse transform sampling
- Hàm loss MSE cộng cả hai nhánh, giải thích vì sao phải train cả coarse

**Trích dẫn xuyên suốt:** `Selected/2020 NeRF`, `Foundation/1995 Optical Models`
**Nguyên liệu:** `02-TaiLieuHoc/pipeline_NeRF.md` (782 dòng), `lythuyet_NeRF.md`

## 3.2. Cải tiến thứ nhất — Mip-NeRF: chống răng cưa 🟡 (~2,5 trang)

> Mục "Preliminaries" bắt buộc — paper Mip-NeRF 360 giả định người đọc đã biết phần này.

**3.2.1. Vấn đề aliasing** (~0,5 trang)
- Một pixel không phải một **điểm** toán học mà là một **vùng** — chiếu ngược ra không gian 3D thành hình nón, càng xa càng rộng
- Hậu quả: khi camera ở xa hoặc render ở độ phân giải khác lúc train → chi tiết nhỏ bị lấy mẫu dưới mức → răng cưa, nhấp nháy
- **Hình 3.3:** so sánh tia mảnh của NeRF vs hình nón của Mip-NeRF

**3.2.2. Hình nón cụt và xấp xỉ Gaussian** (~0,75 trang)
- Conical frustum: vùng không gian pixel thực sự "nhìn thấy" trong đoạn `[tᵢ, tᵢ₊₁]`
- Xấp xỉ bằng Gaussian đa biến: mean **μ**, covariance **Σ**
- **Bảng 3.3:** chú thích `μ, Σ`

**3.2.3. Integrated Positional Encoding (IPE)** (~0,75 trang)
- Công thức `IPE(μ,Σ) = E_{x~N(μ,Σ)}[γ(x)]` — mã hóa cả một **vùng** thay vì một **điểm**
- Dạng đóng: biên độ sin/cos bị nhân hệ số suy giảm `exp(-½(2^l π)²σ²)`
- **Trực giác then chốt:** tần số cao tự động bị "tắt" khi vùng không gian quá lớn so với bước sóng → chống răng cưa có nguyên lý toán học, không phải hậu xử lý

**3.2.4. Gộp hai mạng coarse/fine thành một** (~0,5 trang)
- Vì IPE đã biểu diễn đa tỉ lệ sẵn, không cần hai mạng riêng
- Vẫn giám sát ở mọi tỉ lệ bằng loss ảnh (hệ số 1/10 cho nhánh coarse) — **chi tiết này quan trọng** vì chính nó là thứ Mip-NeRF 360 loại bỏ ở mục 3.3.2

**Trích dẫn:** `Selected/2021 Mip-NeRF` ⚠️ **cần đọc** để lấp các chỗ `[MIP-NỀN]` hiện chưa verify trong tài liệu

## 3.3. PHƯƠNG PHÁP — Mip-NeRF 360 🟢 (~5 trang)

> Tầng "phương pháp". Tổ chức theo đúng ba vấn đề đã nêu ở 3.0.

**3.3.1. Giải quyết Parameterization — Scene Contraction** (~1,75 trang)
- **Vấn đề cụ thể:** cảnh 360° trải tới vô cực; lấy mẫu tuyến tính theo `t` làm mật độ điểm mẫu ở vùng xa giảm mạnh; không có `t_far` hữu hạn hợp lý
- **Công thức `contract(x)`** (Eq. 10 của paper): giữ nguyên trong bán kính 1, nén dần ra ngoài, tiệm cận bán kính 2
  - ⚠️ Bán kính đo **từ gốc tọa độ world** (tâm đám camera sau bước chuẩn hóa), **không phải từ camera**
- **Đóng góp cốt lõi:** áp phép co lên **Gaussian (μ,Σ)** chứ không chỉ lên điểm, theo kiểu Extended Kalman filter (`f(μ), JΣJᵀ`) — Eq. 8-9. Paper nói rõ việc tham số hóa **điểm** đã có ở công trình trước và **không** giải quyết được ngữ cảnh mip-NeRF
- **Tham số hóa lại tia:** lấy mẫu đều trong không gian `s` định nghĩa bởi Eq. 11 với `g(x) = 1/x` → tuyến tính theo **disparity**; nhờ đó `t_far = ∞` trở nên hợp lệ
- **Off-axis IPE** (Eq. 17): nâng cấp bắt buộc vì `contract` sinh Gaussian cực kỳ dị hướng; dùng cơ sở 21 đỉnh icosahedron
- **Hình 3.4:** minh họa phép co không gian (vẽ lại từ Figure của paper, có ghi nguồn)
- **Bảng 3.4:** chú thích ký hiệu của mục này

**3.3.2. Giải quyết Efficiency — Proposal Network + Online Distillation** (~1,75 trang)
- **Vấn đề cụ thể:** cảnh lớn cần mạng dung lượng lớn, nhưng truy vấn dày đặc mạng lớn dọc mọi tia thì quá tốn
- **Kiến trúc hai mạng tách vai trò:**

| | Proposal MLP | NeRF MLP |
|---|---|---|
| Nhiệm vụ | Chỉ dự đoán **density** để hướng dẫn lấy mẫu | Dự đoán density **và màu** để render |
| Kích thước | 4 lớp × 256 | 8 lớp × 1024 |
| Số mẫu | 2 lượt × 64 | 32 |

- **Khác biệt căn bản với coarse/fine của NeRF:** proposal network **không** dự đoán màu và **không** được giám sát bằng loss ảnh
- **Online distillation** (Eq. 12-13): proposal được huấn luyện để histogram density của nó **bao trọn** histogram của NeRF MLP; dùng **stop-gradient** (NeRF dẫn, proposal theo); `L_prop` là **chặn trên một phía bất đối xứng**, không phải độ đo khoảng cách đối xứng
- **Kết quả:** tăng tốc huấn luyện ~300% (theo Ablation D của paper)
- **Hình 3.5:** sơ đồ luồng dữ liệu giữa proposal network và NeRF MLP

**3.3.3. Giải quyết Ambiguity — Distortion Loss** (~1,5 trang)
- **Vấn đề cụ thể:** cảnh unbounded có nhiều vùng ít được quan sát → sinh hai loại artifact có tên riêng: **floaters** (đốm mây mù lơ lửng) và **background collapse** (nền bị sụp vào gần)
- **Công thức `L_dist`** (Eq. 14-15): phạt phân phối trọng số bị phân tán dọc tia, khuyến khích dồn gọn tại một vị trí (đúng bản chất bề mặt là lớp mỏng)
- **Chi tiết quan trọng:** tính trên không gian `s` chứ không trên `t` — paper nêu rõ lý do
- **Phát hiện đáng chú ý (Ablation B):** bỏ `L_dist` **không** làm PSNR/SSIM/LPIPS xấu đi (PSNR còn nhỉnh hơn: 24.41 vs 24.37), chỉ sinh floaters nhìn thấy được trên depth map → ⚠️ **không được viết "L_dist cải thiện PSNR"**
- **Hình 3.6:** minh họa floaters trên depth map khi có/không có `L_dist`

## 3.4. GIẢI THUẬT — Pipeline tổng thể 🟢 (~1,5 trang)

> Tầng "giải thuật" trong mạch thầy yêu cầu.

**3.4.1. Sơ đồ pipeline 5 giai đoạn**
- **Hình 3.7:** từ ảnh input → COLMAP → sinh tia → lấy mẫu → mạng → volume rendering → loss → (vòng lặp) → inference
- Đánh dấu rõ đâu là vòng lặp huấn luyện (có backprop), đâu là bước inference (chỉ forward)

**3.4.2. Mã giả (pseudocode) một vòng lặp huấn luyện**
```
for iter in 1..N_iters:
    rays ← lấy ngẫu nhiên batch tia từ toàn bộ pixel
    for mỗi tia r:
        s ← lấy mẫu đều trong không gian đã contract
        (σ_prop) ← ProposalMLP(contract(Gaussian(s)))
        s' ← resample theo trọng số từ proposal (2 lượt)
        (σ, c) ← NeRF_MLP(off-axis IPE(contract(Gaussian(s'))))
        Ĉ(r) ← VolumeRender(σ, c)
    L ← L_recon + λ_prop·L_prop + λ_dist·L_dist
    cập nhật Θ bằng Adam
```

**3.4.3. Bảng siêu tham số** — trích đầy đủ từ paper: số vòng lặp, batch size, learning rate và lịch giảm, hệ số λ của từng thành phần loss, kích thước mạng

## 3.5. Tổng hợp: Mip-NeRF 360 thay đổi gì so với NeRF 🟢 (~1 trang)

**Bảng 3.5 — Đối chiếu từng thành phần:**

| Thành phần | NeRF (2020) | Mip-NeRF 360 (2022) | Nguồn cải tiến | Lý do | Hệ quả |
|---|---|---|---|---|---|
| Đơn vị lấy mẫu | Tia mảnh, điểm rời rạc | Hình nón cụt → Gaussian | Mip-NeRF 2021 | Pixel là vùng, không phải điểm | Hết răng cưa |
| Mã hóa input | PE của một điểm | Off-axis IPE của một vùng | Mip-NeRF + **mới ở 360** | Gaussian dị hướng sau contract | SSIM 0.664→0.687 |
| Không gian | Tọa độ gốc | Scene contraction | **Mới ở 360** | Nén vô cực vào hữu hạn | Hỗ trợ cảnh 360° |
| Lấy mẫu trên tia | Tuyến tính theo `t` | Đều theo `s` (disparity) | **Mới ở 360** | Phân bổ mẫu hợp lý theo độ sâu | `t_far=∞` hợp lệ |
| Mạng dẫn đường | Coarse MLP (dự đoán cả màu) | Proposal MLP (chỉ density) | **Mới ở 360** | Tách vai trò, mạng nhỏ hơn | Train nhanh ~300% |
| Chính quy hóa | Không có | Distortion loss | **Mới ở 360** | Chống floaters, background collapse | Depth map sạch hơn |

> Cột "Nguồn cải tiến" phân biệt rõ cái gì đến từ Mip-NeRF 2021, cái gì là mới của bản 360 — chi tiết này thể hiện mình đọc kỹ, thầy sẽ đánh giá cao.

**Nguyên liệu:** `02-TaiLieuHoc/pipeline_MipNeRF360.md` (1.615 dòng, đã verify trực tiếp với paper)

---

# CHƯƠNG 4 — CÀI ĐẶT VÀ THỬ NGHIỆM (~9 trang) 🔴

> **Yêu cầu của thầy (`phuongphap.rtf` 2.7):** môi trường cài đặt (phần cứng, phần mềm) · tập dữ liệu thử nghiệm · bảng kết quả · đánh giá kết quả
>
> Đây là tầng "chương trình minh họa" trong mạch nguyên lý → phương pháp → giải thuật → CT minh họa.

## 4.1. Môi trường cài đặt (~1 trang)

**4.1.1. Ràng buộc phần cứng và cách xử lý**
- Máy cá nhân: MacBook Apple M2 Pro, 16GB RAM — **không có GPU NVIDIA/CUDA**
- Mọi bản triển khai NeRF phổ biến yêu cầu CUDA (riêng `tiny-cuda-nn` là CUDA kernel, không chạy trên Apple Silicon)
- **Giải pháp:** Google Colab / Kaggle — GPU NVIDIA miễn phí
- **Bảng 4.1:** đối chiếu phần cứng — máy cá nhân vs GPU Colab được cấp vs TPU v2 32 nhân mà paper gốc dùng. Bảng này **rất quan trọng** vì nó giải thích trước mọi khác biệt về thời gian/kết quả ở mục 4.5

**4.1.2. Phần mềm**
- Python, PyTorch (ghi rõ phiên bản), CUDA version
- `nerfstudio` (ghi rõ phiên bản), COLMAP
- Liệt kê theo dạng bảng để người đọc tái lập được

## 4.2. Lựa chọn và điều chỉnh mã nguồn (~1 trang)

**4.2.1. Mã nguồn sử dụng**
- Bản gốc của tác giả: `multinerf` (Google, JAX) — nêu rõ vì sao **không** dùng trực tiếp (yêu cầu TPU, thời gian train quá dài so với khuôn khổ đồ án)
- Bản dùng thực tế: **`nerfacto`** của nerfstudio

**4.2.2. `nerfacto` kế thừa gì từ Mip-NeRF 360** — bảng đối chiếu trung thực:

| Thành phần Mip-NeRF 360 | `nerfacto` có? | Ghi chú |
|---|---|---|
| Scene contraction | ✅ Có | Giữ nguyên tinh thần |
| Proposal network + online distillation | ✅ Có | Giữ nguyên |
| Distortion loss | ✅ Có | Giữ nguyên |
| Off-axis IPE | ❌ Thay bằng hash encoding | Đánh đổi để tăng tốc |
| MLP 8×1024 | ❌ Thay bằng MLP nhỏ + hash grid | Đánh đổi để tăng tốc |

> ⚠️ **Phải viết rõ điều này trong báo cáo.** Nếu giấu đi và trình bày như thể đã cài đặt đúng bản gốc, thầy hỏi là mất điểm nặng. Trình bày trung thực kèm lý do thì đây lại thành điểm cộng (cho thấy hiểu sâu cả hai phương pháp).

**4.2.3. Phần tự viết** (yêu cầu của thầy: "tận dụng source code có sẵn **và tự viết**")
- Script tiền xử lý dữ liệu tự chụp (lọc ảnh mờ, resize, đặt tên)
- Script chạy COLMAP tự động và kiểm tra chất lượng pose
- Script đánh giá: tính PSNR/SSIM/LPIPS, xuất bảng kết quả
- Notebook tổng hợp để tái lập toàn bộ thử nghiệm
- Script dựng video demo quay camera quanh cảnh

## 4.3. Tập dữ liệu thử nghiệm (~1,5 trang)

**4.3.1. Dataset chuẩn**
- Chọn 1-2 cảnh từ bộ Mip-NeRF 360 (ví dụ `garden`, `bicycle`) — mục đích: **đối chiếu được với số liệu công bố trong paper**
- Bảng mô tả: số ảnh, độ phân giải, trong nhà/ngoài trời, cách chia train/test

**4.3.2. Dataset tự thu thập** (phần thể hiện công sức riêng)
- Mô tả quy trình chụp: thiết bị (điện thoại gì), số ảnh, cách di chuyển camera (vòng tròn quanh vật thể), điều kiện ánh sáng, thời gian chụp
- **Hình 4.1:** vài ảnh mẫu từ bộ dữ liệu tự chụp
- Những lỗi gặp phải khi chụp và cách khắc phục (ảnh mờ, thiếu overlap, ánh sáng đổi giữa các ảnh...)

**4.3.3. Tiền xử lý bằng COLMAP**
- Quy trình: ảnh thô → feature extraction → matching → sparse reconstruction → xuất camera pose
- **Hình 4.2:** ảnh chụp màn hình kết quả COLMAP (sparse point cloud + vị trí các camera)
- Số liệu: bao nhiêu ảnh được đăng ký thành công / tổng số ảnh, số điểm 3D thu được, reprojection error trung bình

## 4.4. Kịch bản thử nghiệm (~0,5 trang)

| Mã | Mục đích | Dữ liệu | Cấu hình |
|---|---|---|---|
| TN1 | Đối chiếu với số liệu paper | 1-2 cảnh dataset chuẩn | `nerfacto` mặc định |
| TN2 | Kiểm chứng trên dữ liệu thật tự thu thập | Dataset tự chụp | `nerfacto` mặc định |
| TN3 | So sánh với baseline | Cùng dữ liệu TN2 | `nerfacto` vs `instant-ngp` (hoặc `vanilla-nerf`) |
| TN4 *(nếu kịp)* | Ablation — kiểm chứng vai trò từng thành phần | Cùng dữ liệu TN2 | Bật/tắt distortion loss, đổi số lượng proposal samples |

> TN4 là phần "ăn điểm": paper top đầu nào cũng có ablation. Chỉ cần làm 1-2 cấu hình là đủ chứng minh mình hiểu cơ chế chứ không chỉ chạy lệnh có sẵn.

## 4.5. Kết quả (~3 trang)

**4.5.1. Chỉ số đánh giá** — giải thích ngắn gọn mỗi chỉ số đo gì:
- **PSNR** (Peak Signal-to-Noise Ratio, cao hơn tốt hơn) — sai khác pixel theo nghĩa thuần số học
- **SSIM** (Structural Similarity, cao hơn tốt hơn) — tương đồng về cấu trúc
- **LPIPS** (Learned Perceptual Image Patch Similarity, thấp hơn tốt hơn) — khác biệt theo cảm nhận thị giác, dùng mạng học sẵn

**4.5.2. Kết quả định lượng**
- **Bảng 4.2:** kết quả TN1 — so với số liệu paper công bố trên cùng cảnh
- **Bảng 4.3:** kết quả TN2 + TN3 — so sánh các phương pháp trên dữ liệu tự chụp
- Mỗi bảng kèm: thời gian huấn luyện, số vòng lặp, dung lượng mô hình

**4.5.3. Kết quả định tính**
- **Hình 4.3:** ảnh so sánh cạnh nhau — Ground truth | Kết quả của ta | (baseline nếu có), có khung phóng to vùng chi tiết
- **Hình 4.4:** depth map — cho thấy hình học học được có sạch không, có floaters không
- **Hình 4.5:** vài khung hình từ video quay camera quanh cảnh
- Video demo đính kèm (ghi link hoặc để trong phụ lục)

## 4.6. Ablation Study (~1 trang) *(nếu làm được TN4)*

**Bảng 4.4:** bật/tắt từng thành phần → chỉ số thay đổi thế nào

| Cấu hình | PSNR | SSIM | LPIPS | Nhận xét quan sát được |
|---|---|---|---|---|
| Đầy đủ | | | | |
| Bỏ distortion loss | | | | Kỳ vọng: số không xấu đi nhiều nhưng depth map có floaters |
| Giảm số proposal samples | | | | |

> Nếu kết quả trùng với phát hiện trong paper (bỏ `L_dist` không làm PSNR xấu đi) thì đây là điểm rất mạnh của báo cáo — chứng minh mình tái lập được đúng hành vi mà paper mô tả.

## 4.7. Đánh giá và thảo luận (~1 trang)

**Nội dung cần viết — trả lời thẳng các câu hỏi sau:**

1. **Kết quả có đạt như paper công bố không?** Nếu thấp hơn, phân tích nguyên nhân: khác phần cứng, khác implementation (`nerfacto` vs bản gốc), số vòng lặp ít hơn, dữ liệu tự chụp khó hơn dữ liệu chuẩn...
2. **Artifact quan sát được:** floaters ở đâu, vùng nào mờ, vùng nào thiếu dữ liệu quan sát → đối chiếu với các hạn chế paper tự nêu
3. **Chi phí tính toán thực tế:** thời gian train, VRAM tiêu thụ, giới hạn gặp phải trên Colab
4. **Hạn chế của chính quá trình thử nghiệm:** số cảnh ít, chưa chạy đủ vòng lặp, chưa thử hết cấu hình...

---

# CHƯƠNG 5 — KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN (~3 trang)

## 5.1. Kết luận (~1 trang)
- **Tóm tắt những gì đã làm:** khảo sát N công trình, trình bày chi tiết Mip-NeRF 360 trong mạch kế thừa, cài đặt và thử nghiệm trên dữ liệu chuẩn + tự thu thập
- **Kết quả chính đạt được:** nêu con số cụ thể
- **Bài học rút ra:** về mặt kỹ thuật (hiểu được cơ chế nào quan trọng) và về mặt quy trình (tầm quan trọng của việc dựng môi trường sớm, của việc đọc paper gốc thay vì tài liệu thứ cấp)

## 5.2. Hạn chế của đồ án (~0,75 trang)
Viết trung thực, chia 3 nhóm:
- **Hạn chế phần cứng:** không có GPU riêng, phụ thuộc Colab (giới hạn thời gian phiên, GPU được cấp thay đổi)
- **Hạn chế về cài đặt:** dùng `nerfacto` thay vì bản gốc, nên không tái lập được chính xác 100% kết quả paper
- **Hạn chế về phạm vi:** số cảnh thử nghiệm ít, chưa thử hết các cấu hình, chưa so sánh được với toàn bộ các phương pháp trong Chương 2

## 5.3. Hướng phát triển (~1,25 trang)

**5.3.1. Hướng kỹ thuật** — mỗi hướng 1 đoạn, nêu rõ *giải quyết hạn chế nào của đồ án này*:
- **Zip-NeRF (ICCV 2023):** gộp scene contraction + IPE của Mip-NeRF 360 với hash grid của Instant-NGP → vừa nhanh vừa chất lượng, khắc phục đúng điểm yếu tốc độ mà ta gặp phải
- **3D Gaussian Splatting (SIGGRAPH 2023):** chuyển sang rasterization, render real-time — hướng đang chiếm ưu thế hiện nay
- **Mip-Splatting (CVPR 2024):** mang chống răng cưa sang 3DGS, cho thấy ý tưởng của dòng Mip-NeRF vẫn còn giá trị

**5.3.2. Hướng ứng dụng**
- Số hóa một không gian cụ thể (phòng học, hiện vật bảo tàng của trường...)
- Tích hợp vào ứng dụng web xem 3D
- Tối ưu để chạy trên thiết bị di động

**Trích dẫn:** `Related/2023 Zip-NeRF`, `Related/2023 3DGS`, `Related/2024 Mip-Splatting`, `Survey/2024 A Survey on 3DGS`

---

# TÀI LIỆU THAM KHẢO (~2 trang)

16 tài liệu hiện có trong `03-Reference/`. Yêu cầu:
- **Thống nhất một chuẩn** (đề xuất IEEE — phổ biến trong ngành CS)
- Trích dẫn trong bài theo dạng `[1]`, `[2]`...
- Mỗi mục đủ: tác giả, tên bài, venue, năm, (DOI hoặc arXiv ID)
- Sắp xếp theo thứ tự xuất hiện trong bài hoặc theo alphabet — chọn một và giữ nhất quán

# PHỤ LỤC

- **PL A:** Mã nguồn các script tự viết
- **PL B:** Hướng dẫn tái lập thử nghiệm (từng bước chạy trên Colab)
- **PL C:** Bảng phân công công việc chi tiết
- **PL D:** Ảnh/video kết quả bổ sung

---

# BẢNG PHÂN CÔNG CÔNG VIỆC

> Yêu cầu của thầy (`phuongphap.rtf` 2.9): *"Lập bảng phân công công việc cho từng thành viên với các cột mốc thời gian cụ thể"*

**Nguyên tắc chia việc:** hai hướng song song — **lý thuyết/báo cáo** và **cài đặt/thực nghiệm**. Chương 3 là trọng tâm nên cả hai cùng tham gia.

| Tuần | Thành viên 1 (Bùi Văn Thiên) | Thành viên 2 | Mốc kiểm tra |
|---|---|---|---|
| 1 | Đọc 3 survey, lập dàn ý Chương 2 | **Dựng môi trường Colab, chạy thử dataset mẫu của nerfstudio** | ⚠️ Phải có ảnh render đầu tiên |
| 2 | Viết Chương 2 mục 2.1-2.3 | Chạy thành công trên 1 cảnh dataset chuẩn (TN1) | Có kết quả TN1 |
| 3 | Viết Chương 2 mục 2.4-2.5 (bảng so sánh) + Chương 1 | Đọc paper Mip-NeRF 2021, viết mục 3.2 | **Nộp thầy duyệt dàn ý + Chương 1-2** |
| 4 | Viết Chương 3 mục 3.0-3.1 | Chụp dữ liệu thật, chạy COLMAP | Có dataset tự chụp đã xử lý |
| 5 | Viết Chương 3 mục 3.1 (tiếp) | Train trên dataset tự chụp (TN2) | Có kết quả TN2 |
| 6 | Viết Chương 3 mục 3.3 | Chạy TN3 (so sánh baseline) | Xong bản nháp Chương 3 |
| 7 | Viết Chương 3 mục 3.4-3.5 | Chạy TN4 (ablation), dựng video demo | Có đủ dữ liệu cho Chương 4 |
| 8 | Viết Chương 4 mục 4.1-4.3 | Tổng hợp bảng kết quả, chuẩn bị hình ảnh so sánh | Xong nửa đầu Chương 4 |
| 9 | Viết Chương 4 mục 4.4-4.7 | Hỗ trợ phân tích kết quả, viết mục 4.6 | **Xong Chương 4** |
| 10 | Viết Chương 5, phần mở đầu, tài liệu tham khảo | Làm slide, chuẩn bị phụ lục | Bản báo cáo đầy đủ |
| 11 | Rà soát toàn bộ: chính tả, định dạng, đánh số hình/bảng, kiểm tra trích dẫn | Hoàn thiện slide, tập thuyết trình | Bản hoàn chỉnh |
| 12 | Dự phòng, chỉnh sửa theo góp ý | Dự phòng, tập thuyết trình | **Nộp + bảo vệ** |

> ⚠️ **Rủi ro lớn nhất của đồ án này là môi trường cài đặt ở Chương 4.** Vì vậy việc đó được xếp vào **tuần 1**, không phải tuần 8. Nếu hết tuần 2 vẫn chưa train được dataset mẫu thì phải báo động ngay và đổi phương án (thuê GPU cloud, mượn máy có GPU NVIDIA).

---

# VIỆC CẦN LÀM NGAY (theo thứ tự ưu tiên)

| # | Việc | Vì sao ưu tiên |
|---|---|---|
| 1 | **Dựng môi trường Colab + train thử dataset mẫu** | Gỡ rủi ro lớn nhất; mọi thứ ở Chương 4 phụ thuộc vào đây |
| 2 | **Gửi dàn ý này cho thầy duyệt** | Rẻ nhất để sửa hướng; đừng viết 40 trang rồi mới biết lệch |
| 3 | **Đọc 3 survey** → viết Chương 2 | Nguyên liệu có sẵn, làm được ngay, không phụ thuộc gì |
| 4 | **Đọc paper Mip-NeRF 2021** | Lấp các chỗ `[MIP-NỀN]` chưa verify trong mục 3.2 |
