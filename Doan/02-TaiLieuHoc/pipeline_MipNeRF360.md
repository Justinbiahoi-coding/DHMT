# Quy trình Đầy đủ Mip-NeRF 360: Từ Ảnh Input đến Ảnh Output

*Tài liệu hệ thống hóa toàn bộ các sự kiện xảy ra khi dùng **Mip-NeRF 360** (Barron et al., CVPR 2022) để tạo ra 1 ảnh output ở góc nhìn mới cho **cảnh 360° không giới hạn (unbounded)** — từ lúc chỉ có 1 thư mục ảnh thô, qua ước lượng camera pose, phép co không gian (scene contraction), mạng đề xuất (proposal network) + chưng cất trực tuyến (online distillation), hàm chính quy hóa biến dạng (distortion loss), cho tới khi render ra ảnh hoàn chỉnh. Tài liệu được biên soạn theo đúng tinh thần, cấu trúc và mức độ chi tiết của `pipeline_NeRF.md` (tài liệu pipeline NeRF gốc trong cùng bộ đồ án), nhằm dùng làm cặp đối chiếu trực tiếp giữa 2 phương pháp.*

## Lưu ý về nguồn và mức độ xác thực (ĐỌC TRƯỚC)

Tài liệu này phân biệt rõ 3 cấp độ nguồn, được ghi nhãn ngay tại chỗ sử dụng:

| Nhãn | Ý nghĩa |
|---|---|
| **[P360]** | Đã **verify trực tiếp** với văn bản paper gốc **arXiv:2111.12077v3** (bản 25/03/2022), *"Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields"*, Jonathan T. Barron, Ben Mildenhall, Dor Verbin, Pratul P. Srinivasan, Peter Hedman — Google Research & Harvard University, CVPR 2022. Mọi công thức có số hiệu (Eq. 1–20), mọi siêu tham số và mọi con số benchmark trong tài liệu này đều trích từ bản PDF đó. |
| **[MIP-NỀN]** | **Kiến thức nền về Mip-NeRF (2021)** mà paper 360 giả định người đọc đã biết (conical frustum, Integrated Positional Encoding). Paper Mip-NeRF gốc (Barron et al., ICCV 2021, arXiv:2103.13415) **không có trong thư mục `Reference/`**, nên phần giải thích *nguyên lý/trực giác* của các khái niệm này dựa trên kiến thức tổng quát + những gì paper 360 mô tả lại ở Mục 1 ("Preliminaries: mip-NeRF"). **Công thức** của IPE thì vẫn là [P360] vì paper 360 in lại nguyên nó ở Eq. 1. |
| **[SUY-RA]** | **Suy luận/dẫn giải toán học của người biên soạn**, không có trong văn bản paper, được đưa vào để giúp hiểu bản chất (ví dụ: tính tường minh ma trận Jacobian của phép co; ví dụ số minh họa; chứng minh phép co và phép giãn nghịch đảo triệt tiêu nhau). Các phần này **đúng về mặt toán học nhưng không nên trích dẫn như là nội dung paper**. |

**Quy ước về bản quyền:** toàn bộ phần diễn giải trong tài liệu này được viết lại hoàn toàn bằng lời và cấu trúc riêng, **không dịch nguyên văn và không paraphrase sát câu** từ paper. Công thức toán, siêu tham số và số liệu thực nghiệm là dữ kiện khoa học — được trích chính xác, kèm số hiệu mục/công thức trong paper để truy nguồn.

**Quy ước trình bày:** mỗi công thức/ký hiệu lần đầu xuất hiện đều có bảng "Chú thích ký hiệu" đi kèm; khi dùng lại ở phần sau chỉ nhắc nhẹ. Mỗi lần nói tới 1 thành phần kỹ thuật đều có khối **🔁 ĐỐI CHIẾU NeRF GỐC** nêu rõ: NeRF gốc làm gì → Mip-NeRF 360 đổi thành gì → vì sao.

## Mục lục

1. **[Giai đoạn 0](#giai-đoạn-0-ba-vấn-đề-paper-360-đặt-ra--bản-đồ-giải-pháp)** — Ba vấn đề paper 360 đặt ra & bản đồ giải pháp
2. **[Giai đoạn 1](#giai-đoạn-1-chuẩn-bị-dữ-liệu--camera-pose-gần-như-không-đổi-so-với-nerf-gốc)** — Chuẩn bị dữ liệu & Camera Pose (gần như không đổi so với NeRF gốc)
3. **[Giai đoạn 2](#giai-đoạn-2-trọng-tâm-1--scene-contraction-tham-số-hóa-tia-và-lấy-mẫu)** — **TRỌNG TÂM 1:** Scene Contraction, tham số hóa tia & lấy mẫu
4. **[Giai đoạn 3](#giai-đoạn-3-kiến-trúc-mlp--volume-rendering)** — Kiến trúc MLP & Volume Rendering
5. **[Giai đoạn 4](#giai-đoạn-4-trọng-tâm-2--proposal-network-online-distillation-và-distortion-loss)** — **TRỌNG TÂM 2:** Proposal Network, Online Distillation & Distortion Loss
6. **[Giai đoạn 5](#giai-đoạn-5-inference--sơ-đồ-tổng-thể-pipeline)** — Inference & Sơ đồ tổng thể Pipeline
7. **[Bảng tổng hợp "Thay đổi gì so với NeRF gốc"](#bảng-tổng-hợp--thay-đổi-gì-so-với-nerf-gốc)** ← phần đối chiếu trọng tâm
8. **[Kết quả thực nghiệm & Ablation](#kết-quả-thực-nghiệm--ablation-study-trích-từ-paper)**
9. **[Hạn chế & những điểm chưa chắc chắn](#hạn-chế-của-mô-hình--những-điểm-người-biên-soạn-chưa-chắc-chắn)**

---

## Giai đoạn 0: Ba vấn đề paper 360 đặt ra & bản đồ giải pháp

Trước khi vào pipeline, cần hiểu **vì sao** Mip-NeRF 360 tồn tại. Paper mở đầu bằng cách chỉ ra: khi đem các mô hình họ NeRF áp dụng cho cảnh **unbounded 360°**, phát sinh đúng **3 vấn đề** — và toàn bộ paper là 3 câu trả lời cho 3 vấn đề đó, lần lượt ở Mục 2, Mục 3, Mục 4 **[P360, phần Introduction]**.

### 0.1. "Cảnh unbounded 360°" nghĩa là gì

Định nghĩa thao tác: cảnh mà **(a)** camera có thể chĩa về **bất kỳ hướng nào** (không bị giới hạn cùng chiều như kiểu "forward-facing"), và **(b)** nội dung cảnh có thể nằm ở **bất kỳ khoảng cách nào** — từ vật thể trung tâm cách camera vài chục cm, tới hàng cây/tòa nhà/bầu trời ở xa gần như vô hạn. Tên "360" xuất phát từ kiểu chụp mà paper nhắm tới: camera đi **vòng tròn quanh 1 điểm cố định** trong cảnh, xoay hết 360° **[P360, Abstract]**.

### 0.2. Ba vấn đề và ba giải pháp tương ứng

| # | Vấn đề | Bản chất khó khăn | Giải pháp của Mip-NeRF 360 | Mục trong paper | Giai đoạn trong tài liệu này |
|---|---|---|---|---|---|
| 1 | **Parameterization** (tham số hóa) | Cảnh 360° có thể chiếm 1 vùng không gian Euclid lớn tùy ý, nhưng Mip-NeRF đòi hỏi tọa độ 3D phải nằm trong 1 miền **bị chặn** | **Scene contraction** `contract(·)` + lấy mẫu tuyến tính theo **disparity** (nghịch đảo khoảng cách) | Mục 2 | Giai đoạn 2 |
| 2 | **Efficiency** (hiệu năng) | Cảnh lớn & nhiều chi tiết cần MLP dung lượng lớn, nhưng truy vấn 1 MLP lớn dày đặc dọc mọi tia khi train thì cực đắt | **Proposal MLP nhỏ + NeRF MLP lớn**, huấn luyện bằng **online distillation** | Mục 3 | Giai đoạn 4 |
| 3 | **Ambiguity** (tính nhập nhằng) | Nội dung ở xa chỉ được quan sát bởi **rất ít tia**, làm trầm trọng tính under-constrained vốn có của bài toán dựng 3D từ ảnh 2D → sinh artifact | **Distortion loss** `L_dist` — 1 regularizer trên phân phối trọng số dọc tia | Mục 4 | Giai đoạn 4 |

> **🔁 ĐỐI CHIẾU NeRF GỐC — tầm nhìn tổng quát**
> - **NeRF gốc** giải bài toán "vật thể đặt giữa khung, nền đã bị mask" bằng cách tham số hóa trực tiếp trong **không gian Euclid 3D có chặn**; và giải bài toán "forward-facing" bằng **NDC (Normalized Device Coordinates)** — 1 phép bóp hình chóp camera sâu vô hạn thành 1 khối lập phương hữu hạn, trong đó khoảng cách dọc trục z tương ứng với **disparity** (nghịch đảo khoảng cách) **[P360, Introduction]**.
> - **Điểm then chốt paper 360 nhấn mạnh:** NDC chỉ "mở" được **1 chiều duy nhất** (trục z — hướng camera nhìn). Cảnh unbounded **theo mọi hướng** cần 1 phép tham số hóa khác. Mip-NeRF 360 chính là "NDC cho mọi hướng", nhưng áp dụng được cho **thể tích (Gaussian)** chứ không chỉ cho **điểm**.

---

## Giai đoạn 1: Chuẩn bị dữ liệu & Camera Pose (gần như không đổi so với NeRF gốc)

> **Kết luận ngắn:** Mip-NeRF 360 **KHÔNG thay đổi gì về bản chất thuật toán** ở giai đoạn này — vẫn dùng **COLMAP / Structure-from-Motion** y như NeRF gốc. Toàn bộ 7 bước SfM (SIFT → Feature Matching → RANSAC/Essential Matrix → phân tích ra (R,t) → Triangulation/DLT → Incremental SfM/P3P → Bundle Adjustment/Levenberg-Marquardt) đã trình bày đầy đủ trong **`pipeline_NeRF.md`, Giai đoạn 1** — **không lặp lại ở đây**.
>
> Paper chỉ nhắc đúng 1 câu: camera pose được ước lượng bằng COLMAP, "như trong NeRF" **[P360, Mục 6]**.

Phần dưới chỉ nêu những gì **thực sự khác**, tất cả nằm ở **loại dữ liệu** và **các bước tiền xử lý đặt quanh COLMAP**, không nằm ở bản thân thuật toán SfM.

### 1.1. Khác biệt 1 — loại dataset mà paper này nhắm tới

Paper tự xây 1 **dataset mới** vì các dataset NeRF cũ không bộc lộ đúng vấn đề cần giải. Thông số dataset **[P360, Mục 6 + Phụ lục D]**:

| Thuộc tính | Dataset Mip-NeRF 360 | Dataset NeRF gốc (để đối chiếu) |
|---|---|---|
| Số scene | **9 scene**: 5 ngoài trời (`bicycle`, `flowers`, `garden`, `stump`, `treehill`) + 4 trong nhà (`room`, `counter`, `kitchen`, `bonsai`) | 8 scene synthetic Blender + 8 scene thật forward-facing (LLFF) |
| Cấu trúc cảnh | **1 vật thể/khu vực trung tâm phức tạp + 1 hậu cảnh chi tiết trải ra xa** | Vật thể đơn lẻ, nền bị mask/xóa (Blender); hoặc cảnh nhìn 1 chiều (LLFF) |
| Số ảnh / scene | **100 – 330 ảnh** | thường 20–100 ảnh |
| Kiểu quỹ đạo camera | Vòng tròn (ring) quanh 1 điểm cố định, xoay 360° | Vòng quanh vật thể (object-centric) hoặc quét ngang (forward-facing) |
| Độ phân giải dùng train | Giảm mẫu (downsample) về **1.0 – 1.6 megapixel** bằng ImageMagick | thường 800×800 (Blender) |
| Chia train/test | **1 trong 8 ảnh** làm test set, lấy cách đều để phủ nhiều góc nhìn nhất có thể | tỉ lệ khác, tùy dataset |
| Thiết bị | Sony NEX C-3 (lens 18–55mm, zoom rộng nhất) cho ngoài trời; Fujifilm X100V (lens cố định 22mm) cho trong nhà | — |
| Kiểm soát quang học | **Khóa cứng ISO, white balance, shutter speed, khẩu độ, focus** theo ảnh đầu tiên; chụp trời nhiều mây để bóng mềm; trong nhà dùng nguồn sáng tán xạ lớn | cảnh phải tĩnh, không nêu chi tiết |

**Vì sao paper phải tự dựng dataset thay vì dùng "Tanks and Temples" (một dataset 360° có sẵn):** vì bộ đó để autoexposure/auto-white-balance **thay đổi giữa các ảnh**, và nhiều ảnh bị dư sáng làm giá trị RGB bị "kẹp trần" (clipped). Khi dữ liệu có biến thiên quang học như vậy, việc **đo** độ chính xác của 1 thuật toán view synthesis trở thành bài toán ill-posed — không biết mô hình "nên" tái tạo điều kiện sáng nào mới đúng. Paper chủ ý tách bạch: thách thức "ảnh in the wild" là **vấn đề khác**, trực giao với thách thức "cảnh unbounded" mà paper muốn giải **[P360, Phụ lục D]**.

> **🔁 ĐỐI CHIẾU NeRF GỐC — dataset**
> - **NeRF gốc:** cảnh **bounded**. Với Blender, nền bị xóa trắng → mạng chỉ phải học vật thể trong 1 hộp nhỏ. Với LLFF, mọi camera nhìn gần cùng 1 hướng → NDC xử lý được.
> - **Mip-NeRF 360:** cảnh **unbounded + 360°**, hậu cảnh là **nội dung thật cần tái tạo**, không phải nền bỏ đi. Đây là thay đổi về **đề bài**, và nó là nguyên nhân gốc sinh ra mọi thay đổi kỹ thuật ở các giai đoạn sau.

### 1.2. Khác biệt 2 — cấu hình COLMAP và bước undistort

**[P360, Phụ lục D]**: dùng **shared intrinsics** (1 ma trận K duy nhất dùng chung cho mọi ảnh trong 1 scene — hợp lý vì chụp bằng cùng 1 máy, khóa cứng tiêu cự), calibrate theo **mô hình méo xuyên tâm OpenCV (OpenCV radial distortion model)**, rồi **undistort ảnh bằng COLMAP trước khi train**.

| Thuật ngữ | Ý nghĩa |
|---|---|
| **Radial distortion** (méo xuyên tâm) | Hiện tượng ống kính thực tế làm đường thẳng trong cảnh bị cong trên ảnh, mức cong tăng dần theo khoảng cách từ tâm ảnh ra biên (lens góc rộng bị nặng hơn) |
| **Undistort** (khử méo) | Biến đổi lại ảnh để nó khớp đúng với mô hình camera lỗ kim lý tưởng (`pipeline_NeRF.md`, Giai đoạn 2 mục 1.2) — sau bước này, công thức pixel → hướng tia mới chính xác |
| **Shared intrinsics** | Bắt buộc mọi ảnh trong cùng scene dùng chung 1 bộ (fx, fy, cx, cy) → giảm số tham số phải ước lượng, tăng độ ổn định cho Bundle Adjustment |

Lý do bước undistort quan trọng hơn ở Mip-NeRF 360 so với NeRF gốc: lens được dùng ở **zoom rộng nhất** để bao được cảnh 360°, và lens góc rộng thì méo xuyên tâm nặng. Nếu không khử méo, hướng tia tính ra từ pixel ở biên ảnh sẽ sai, phá vỡ tính nhất quán đa góc nhìn.

### 1.3. Khác biệt 3 — chuẩn hóa hệ tọa độ world bằng PCA (bước MỚI, không có ở NeRF gốc)

Đây là bước đáng chú ý nhất của Giai đoạn 1, vì **nó là điều kiện tiên quyết để phép co không gian ở Giai đoạn 2 hoạt động đúng**. Sau khi COLMAP trả về pose, paper áp 1 **phép biến đổi cứng (rigid transform) + phép đổi tỉ lệ (rescaling)** lên toàn bộ pose **[P360, Phụ lục D]**:

**Bước 1 — Dời tâm (recentering):** tính **vị trí trung bình của mọi camera**, rồi trừ nó khỏi mọi vị trí camera. Sau bước này, "đám mây vị trí camera" có tâm tại gốc tọa độ (0,0,0).

**Bước 2 — Xác định trục "up" bằng PCA:** tính các **thành phần chính (principal components)** của tập vector vị trí camera đã dời tâm.

| Thuật ngữ | Ý nghĩa |
|---|---|
| **PCA (Principal Component Analysis)** | Kỹ thuật thống kê tìm ra các hướng mà dữ liệu **phân tán mạnh nhất**. Với 1 tập điểm 3D, PCA cho 3 vector trực giao: hướng phân tán nhất, nhì, và ít nhất |
| **Thành phần chính nhỏ nhất** | Hướng mà dữ liệu **ít phân tán nhất** |

**Logic của bước này [SUY-RA phần giải thích, dữ kiện là P360]:** nếu camera được chụp theo **vòng tròn nằm (gần) trong 1 mặt phẳng**, thì 2 hướng phân tán mạnh nhất chính là 2 hướng nằm **trong** mặt phẳng vòng tròn đó, còn hướng phân tán **ít nhất** chính là **pháp tuyến** của mặt phẳng đó — tức là hướng "lên trên" theo trực giác. Vì vậy paper lấy **thành phần chính nhỏ nhất làm trục "up" của hệ world**. Ba vector trực giao này tạo thành cơ sở mới của hệ tọa độ.

**Bước 3 — Đổi tỉ lệ:** sau khi dời tâm và đổi cơ sở, co giãn (rescale) toàn bộ vị trí camera sao cho chúng nằm gọn trong khối lập phương **[−1, 1]³**. Paper ghi: nếu pose đầu vào nằm xấp xỉ trên 1 mặt cầu, bước này thường khiến chúng nằm **trong vùng không gian được tham số hóa tuyến tính (đều)**, tức phần bên trong hình cầu bán kính 1.

> **⚠️ ĐIỂM CỰC KỲ QUAN TRỌNG — rất dễ hiểu sai:** vùng "bán kính ≤ 1" mà phép co giữ nguyên ở Giai đoạn 2 được đo **từ gốc tọa độ world mới này** (tâm của đám camera), **KHÔNG phải đo từ mỗi camera**. Nói cách khác: vùng không bị biến dạng là **vùng trung tâm cảnh** — nơi vật thể chính và các camera cùng nằm — còn mọi thứ ở ngoài (hậu cảnh xa) đều bị nén. Nếu hiểu sai thành "bán kính 1 tính từ camera" thì toàn bộ hình học của phép co sẽ bị hiểu lệch.

### 1.4. Kết quả của Giai đoạn 1

Đầu ra nạp cho Giai đoạn 2:
- Với **mỗi ảnh**: bộ (R, C, K) đã tinh chỉnh, **sau khi** undistort và **sau khi** dời tâm/đổi cơ sở/đổi tỉ lệ ở mục 1.3 — mọi camera nằm trong [−1,1]³, trục up đã khớp với pháp tuyến quỹ đạo chụp.
- Với **mỗi pixel**: ngoài tọa độ (u,v), còn cần biết **kích thước vật lý của pixel trên mặt phẳng ảnh** — đại lượng này quyết định **bán kính của hình nón** ở Giai đoạn 2 (chi tiết mục 2.5). NeRF gốc không cần thông tin này; Mip-NeRF và Mip-NeRF 360 thì cần.
- Cận gần/cận xa `t_n`, `t_f` cho mỗi tia.

---

## Giai đoạn 2: TRỌNG TÂM 1 — Scene Contraction, tham số hóa tia và lấy mẫu

Đây là nội dung **Mục 2 của paper** ("Scene and Ray Parameterization") — câu trả lời cho Vấn đề 1 (Parameterization). Giai đoạn này gồm 3 khối kiến thức xếp tầng:

- **(A)** Nền tảng kế thừa từ Mip-NeRF: hình nón cụt + IPE → mục 2.1–2.2.
- **(B)** Đóng góp mới 1: phép co `contract(·)` và cách áp nó lên **Gaussian** (không chỉ lên điểm) → mục 2.3–2.6.
- **(C)** Đóng góp mới 2: tham số hóa khoảng cách tia theo **disparity** (ánh xạ t ↔ s) và lấy mẫu trong không gian s → mục 2.7–2.9.

### 2.1. Nền tảng kế thừa [MIP-NỀN] — từ "tia mảnh" sang "hình nón cụt"

**Vấn đề của NeRF gốc:** NeRF gốc mô hình hóa input của MLP bằng các **điểm 3D vô cùng nhỏ (infinitesimally small)** dọc theo 1 tia — và chính điều này gây **aliasing (răng cưa)** khi render ở các độ phân giải khác nhau **[P360, Introduction — đây là cách paper 360 tóm tắt lại vấn đề]**.

**Lý do vật lý:** 1 pixel trên ảnh không phải 1 điểm toán học, nó là 1 **ô vuông nhỏ** có bề rộng bằng 1/(độ phân giải). Khi "chiếu ngược" ô vuông đó ra không gian 3D, ta được 1 **vùng hình nón** mở rộng dần theo khoảng cách — không phải 1 đường thẳng. Lấy mẫu chỉ đúng trên trục nón (tức tia mảnh ở tâm pixel) là bỏ sót toàn bộ phần còn lại của nón, và đó là lấy mẫu dưới mức (undersampling) ⇒ aliasing.

**Cách Mip-NeRF sửa:** thay vì xét điểm, nó xét **hình nón cụt (conical frustum)**. Cụ thể, với 1 vector khoảng cách **t** đã sắp tăng dần, tia bị chia thành các **khoảng (interval)**:

```
T_i = [t_i , t_{i+1})
```

và với mỗi khoảng `T_i`, ta tính **mean và covariance của hình nón cụt tương ứng**:

```
(μ, Σ) = r(T_i)
```

**[P360, Mục 1]** ghi rõ: bán kính của các hình nón cụt này được quyết định bởi **tiêu cự của tia và kích thước pixel trên mặt phẳng ảnh**.

#### Chú thích ký hiệu (Giai đoạn 2 — khối A)

| Ký hiệu | Ý nghĩa | Nguồn gốc |
|---|---|---|
| `r(t) = o + t·d` | công thức tia: `o` là gốc tia (tâm camera), `d` là vector hướng, `t` là khoảng cách dọc tia | giống hệt NeRF gốc, xem `pipeline_NeRF.md` Giai đoạn 2 mục 3 |
| **t** (in đậm) | **vector** các khoảng cách đã sắp tăng dần, định nghĩa các mốc chia tia | mới so với NeRF gốc: NeRF coi t_i là các *điểm*, Mip-NeRF coi t là các *mốc biên khoảng* |
| `T_i = [t_i, t_{i+1})` | **khoảng (interval) thứ i** trên tia — nửa đóng nửa mở | khái niệm trung tâm của mọi mô hình họ Mip-NeRF |
| `μ` (mu) | **mean** — vector 3 chiều, vị trí trung tâm của hình nón cụt `T_i` | [P360, Mục 1] |
| `Σ` (Sigma) | **covariance matrix** — ma trận 3×3, mô tả hình nón cụt "phình" bao nhiêu theo từng hướng | [P360, Mục 1] |
| `diag(Σ)` | vector gồm các phần tử trên đường chéo chính của Σ — tức phương sai theo từng trục tọa độ | dùng trong Eq. 1 |
| **Conical frustum** | hình nón cụt — phần hình nón bị cắt bởi 2 mặt phẳng song song, tại `t_i` và `t_{i+1}` | [MIP-NỀN] |
| **Multivariate Gaussian** | phân phối chuẩn nhiều chiều, đặc tả đầy đủ bởi đúng cặp (μ, Σ) | thuật ngữ thống kê chuẩn |

**Vì sao xấp xỉ nón cụt bằng Gaussian** [MIP-NỀN]: tính toán giải tích chính xác trên 1 hình nón cụt thật rất phức tạp; nhưng 1 nón cụt "trông giống" 1 khối elip (kéo dài dọc trục, phình theo hướng ngang), và Gaussian đa biến là cách biểu diễn gọn nhất cho 1 khối elip như vậy — chỉ cần 3 số cho μ và 6 số cho Σ (Σ đối xứng). Paper 360 ghi lại chính xác tinh thần này khi gọi Eq. 1 là **"kỳ vọng của các encoding mà NeRF dùng, lấy theo 1 Gaussian xấp xỉ hình nón cụt"** **[P360, Mục 1]**.

> **🔁 ĐỐI CHIẾU NeRF GỐC — đơn vị lấy mẫu**
> | | NeRF gốc | Mip-NeRF / Mip-NeRF 360 |
> |---|---|---|
> | Đơn vị hình học | **1 điểm** `r(t_i)` — không có bề rộng | **1 khoảng** `T_i`, hiện thực hóa thành **1 hình nón cụt** → xấp xỉ Gaussian (μ,Σ) |
> | Biết kích thước pixel? | **Không cần** | **Bắt buộc** — nó quyết định bán kính nón |
> | Hệ quả | Aliasing khi đổi độ phân giải/khoảng cách | Khử aliasing có nguyên lý toán học |
> **Lý do thay đổi:** 1 điểm không mang thông tin về "tỉ lệ" (scale) nên mạng không có cách nào biết nó đang được hỏi ở độ phân giải nào; 1 khoảng thì mang luôn thông tin tỉ lệ bên trong Σ.

### 2.2. Nền tảng kế thừa — Integrated Positional Encoding (IPE), Eq. 1

Có (μ, Σ) rồi, cần biến nó thành vector đặc trưng để nạp vào MLP. Mip-NeRF dùng **Integrated Positional Encoding**, và paper 360 in lại nguyên công thức ở **Eq. 1 [P360, Mục 1]**:

```
                 ⎧  sin(2^ℓ · μ) ⊙ exp( −2^(2ℓ−1) · diag(Σ) )  ⎫ L−1
γ(μ, Σ)  =       ⎨                                              ⎬
                 ⎩  cos(2^ℓ · μ) ⊙ exp( −2^(2ℓ−1) · diag(Σ) )  ⎭ ℓ=0
```

#### Chú thích ký hiệu Eq. 1

| Ký hiệu | Ý nghĩa |
|---|---|
| `γ(μ, Σ)` | hàm IPE — nhận vào **1 cặp (mean, covariance)** (tức 1 vùng không gian), trả về 1 vector đặc trưng nhiều chiều |
| `ℓ` (ell) | **chỉ số mức tần số**, chạy từ 0 đến L−1 |
| `L` | số mức tần số — siêu tham số (trong NeRF gốc: L=10 cho vị trí) |
| `2^ℓ` | **tần số** của mức ℓ — tăng theo luỹ thừa 2: 1, 2, 4, 8, ... |
| `sin(2^ℓ·μ)`, `cos(2^ℓ·μ)` | áp sin/cos lên **từng thành phần** của vector μ (3 thành phần x,y,z) |
| `⊙` | **nhân từng phần tử (element-wise product)** — không phải nhân ma trận |
| `exp(−2^(2ℓ−1)·diag(Σ))` | **hệ số suy giảm (attenuation factor)** — đây chính là linh hồn của IPE |
| `diag(Σ)` | vector phương sai theo từng trục, trích từ đường chéo Σ |
| `{·}` với chỉ số ℓ=0..L−1 | nối (concatenate) kết quả của mọi mức tần số lại thành 1 vector dài |

#### Giải mã hệ số suy giảm — cơ chế khử aliasing

Viết lại số mũ: `2^(2ℓ−1) = ½ · 2^(2ℓ) = ½ · (2^ℓ)²`. Vậy hệ số suy giảm là:

```
exp( −½ · (2^ℓ)² · σ² )
```

với σ² là phương sai theo trục đang xét. Đây **chính xác** là biên độ của kỳ vọng `E[sin(ω·x)]` khi `x ~ N(μ, σ²)` — tức Eq. 1 không phải công thức đặt ra tùy ý, nó là **kết quả giải tích đóng (closed-form)** của phép tính kỳ vọng của positional encoding trên 1 Gaussian **[SUY-RA phần liên hệ; dữ kiện Eq.1 là P360]**.

**Đọc ý nghĩa — 3 trường hợp:**

| Tình huống | σ² (độ phình vùng) | Tần số 2^ℓ | Hệ số suy giảm | Hệ quả |
|---|---|---|---|---|
| Pixel gần camera, ảnh phân giải cao | nhỏ | cao | ≈ 1 | **Giữ nguyên** chi tiết tần số cao |
| Pixel xa camera (nón phình rộng) | lớn | cao | ≈ 0 | **Tự động tắt** tần số cao — đúng việc cần làm để chống aliasing |
| Bất kỳ | bất kỳ | thấp (ℓ=0) | ≈ 1 | Luôn giữ thông tin tần số thấp |

**Trực giác:** nếu vùng không gian đang xét đã **lớn hơn bước sóng** của tần số đang hỏi, thì trong vùng đó hàm sin dao động qua lại nhiều lần và trung bình của nó gần 0 — tức tần số đó **vô nghĩa** ở tỉ lệ này. Hệ số `exp(−½(2^ℓ)²σ²)` tự động phát hiện và triệt tiêu đúng các tần số vô nghĩa đó. Đây là lý do Mip-NeRF khử được aliasing **mà không cần bất kỳ bước hậu xử lý nào**.

**⚠️ Lưu ý về ký hiệu π:** Positional encoding của NeRF gốc viết `sin(2^ℓ · π · p)` (có hệ số π), còn **Eq. 1 của paper 360 viết `sin(2^ℓ · μ)` — KHÔNG có π**. Khác biệt này chỉ là quy ước chuẩn hóa miền tọa độ (π có thể gộp vào hệ số scale của tọa độ), không ảnh hưởng bản chất, nhưng **khi trích dẫn vào báo cáo thì phải trích đúng dạng của từng paper**.

> **🔁 ĐỐI CHIẾU NeRF GỐC — encoding**
> | | NeRF gốc | Mip-NeRF 360 |
> |---|---|---|
> | Công thức | `γ(p) = (sin(2⁰πp), cos(2⁰πp), ..., sin(2^(L−1)πp), cos(2^(L−1)πp))` — PE của **1 điểm** | `γ(μ,Σ)` Eq. 1 — IPE của **1 vùng**, có thêm hệ số `exp(−2^(2ℓ−1)diag(Σ))` |
> | Nhận biết tỉ lệ | **Không** — 2 lần hỏi cùng 1 điểm ở 2 độ phân giải khác nhau cho **cùng 1** vector encoding | **Có** — vùng lớn/nhỏ cho vector encoding khác nhau |
> | Kết quả ablation | — | **[P360, Ablation G]**: bỏ IPE, quay về PE của NeRF làm PSNR tụt từ **24.37 → 23.87**, SSIM từ **0.687 → 0.664**, LPIPS từ **0.300 → 0.322** trên scene `bicycle` |

### 2.3. ĐÓNG GÓP MỚI — Công thức co không gian `contract(x)`, Eq. 10

Đây là công thức quan trọng nhất của Giai đoạn 2. **[P360, Mục 2, Eq. 10]** — trích chính xác:

```
                 ⎧  x                                     nếu ‖x‖ ≤ 1
contract(x)  =   ⎨
                 ⎩  ( 2 − 1/‖x‖ ) · ( x / ‖x‖ )           nếu ‖x‖ > 1
```

#### Chú thích ký hiệu Eq. 10

| Ký hiệu | Ý nghĩa |
|---|---|
| `x` | tọa độ 3D **gốc** (trong hệ world đã chuẩn hóa ở Giai đoạn 1 mục 1.3) — chưa bị co |
| `‖x‖` | **chuẩn Euclid** của x — khoảng cách từ x tới **gốc tọa độ world**, tính bằng `√(x₁²+x₂²+x₃²)`. **Nhắc lại:** đo từ **tâm cảnh**, không phải từ camera |
| `x / ‖x‖` | **vector đơn vị** cùng hướng với x — chỉ mang thông tin **hướng**, độ dài bằng 1 |
| `2 − 1/‖x‖` | **độ dài mới** (bán kính mới) gán cho điểm đó sau khi co |
| `contract(x)` | tọa độ sau khi co — vẫn là 1 vector 3 chiều |

#### Mổ xẻ công thức — vì sao nó có dạng này

Công thức tách điểm thành 2 phần: **hướng** (`x/‖x‖`) và **độ lớn** (`‖x‖`). Phép co **giữ nguyên hoàn toàn hướng** và **chỉ bóp lại độ lớn**. Nói cách khác, `contract(·)` là 1 **phép biến đổi xuyên tâm (radial map)**: mọi điểm chỉ bị trượt dọc theo đường thẳng nối nó với gốc tọa độ, không bao giờ bị xoay đi đâu khác. Đây là lý do nó bảo toàn được cấu trúc góc của cảnh.

Hàm bóp độ lớn là `h(r) = 2 − 1/r` với `r = ‖x‖`. Kiểm tra các tính chất **[SUY-RA]**:

| r = ‖x‖ | Bán kính sau co: `2 − 1/r` | Nhận xét |
|---|---|---|
| 0.5 | — (dùng nhánh trên) → 0.5 | Vùng trong: giữ nguyên y hệt |
| **1** | `2 − 1 = 1` | **Khớp liền mạch** với nhánh trên tại biên → hàm **liên tục** |
| 2 | `2 − 0.5 = 1.5` | Khoảng cách 2 → 1.5 |
| 4 | `2 − 0.25 = 1.75` | Khoảng cách 4 → 1.75 |
| 10 | `2 − 0.1 = 1.9` | Khoảng cách 10 → 1.9 |
| 100 | `2 − 0.01 = 1.99` | Khoảng cách 100 → 1.99 |
| → ∞ | → **2** (tiệm cận, không bao giờ đạt) | **Toàn bộ vô cực được gói vào 1 lớp vỏ mỏng quanh bán kính 2** |

**Hình học của phép co — 3 vùng rõ rệt:**

```
  ‖x‖ = 0 ───────── 1 ──────────────────── ∞      (không gian GỐC, vô hạn)
            │  giữ  │        bị NÉN           
            │ nguyên│   (càng xa càng nén)    
            ▼       ▼                         
  ‖·‖ = 0 ───────── 1 ─── 2                        (không gian ĐÃ CO, hữu hạn)
          [ TUYẾN  ][ PHI  ]
          [  TÍNH  ][TUYẾN ]
```

- **Vùng trong (‖x‖ ≤ 1) — hình cầu bán kính 1:** `contract(x) = x`, **không biến dạng gì cả**. Đây là nơi chứa vật thể/khu vực trung tâm và toàn bộ camera (nhờ bước chuẩn hóa ở Giai đoạn 1 mục 1.3). Giữ nguyên tuyến tính ⇒ MLP có đầy đủ "độ phân giải" để học chi tiết cao.
- **Vùng ngoài (‖x‖ > 1) — vỏ cầu từ bán kính 1 tới 2:** bị nén phi tuyến. Càng xa nén càng mạnh: đoạn từ 1→2 (dài 1 đơn vị thật) được cấp 0.5 đơn vị trong không gian co; đoạn từ 10→∞ (dài vô hạn) chỉ được cấp 0.1 đơn vị.
- **Biên bán kính 2:** không bao giờ bị vượt qua. **[P360, Figure 2]** nói rõ `contract(·)` ánh xạ tọa độ vào **1 hình cầu bán kính 2**, và các điểm trong bán kính 1 thì **không bị tác động**.

#### Vì sao chọn đúng dạng `2 − 1/r` mà không phải 1 hàm bóp khác

**[P360, Mục 2]** nêu trực tiếp động lực thiết kế: **cùng một động lực với NDC — các điểm ở xa nên được phân bố tỉ lệ với disparity (nghịch đảo khoảng cách), chứ không phải tỉ lệ với khoảng cách.**

Diễn giải **[SUY-RA]**: với `r > 1`, bán kính sau co là `2 − 1/r`. Số hạng biến thiên duy nhất là `−1/r` — tức **1/r (disparity)**. Nghĩa là: *bán kính trong không gian co là 1 hàm affine (bậc nhất) của disparity*. Vậy nếu ta lấy mẫu **đều theo disparity**, ta sẽ nhận được các điểm **cách đều nhau trong không gian đã co** — và đó chính xác là điều mục 2.7–2.8 sẽ khai thác.

**Lý do sâu hơn, mang tính quang học:** do phép chiếu phối cảnh, 1 vật ở xa chiếm 1 phần nhỏ trên mặt phẳng ảnh, còn cùng vật đó khi ở gần thì chiếm nhiều pixel và hiện rõ chi tiết. Do đó **1 phép tham số hóa 3D lý tưởng phải cấp nhiều "dung lượng" (capacity) cho nội dung gần và ít dung lượng cho nội dung xa** **[P360, Introduction]**. Hàm `2 − 1/r` làm đúng việc đó: nó cấp nửa "ngân sách" bán kính (từ 0 tới 1) cho vùng trung tâm, và nửa còn lại (từ 1 tới 2) cho toàn bộ phần còn lại của vũ trụ.

> **🔁 ĐỐI CHIẾU NeRF GỐC — tham số hóa không gian**
> - **NeRF gốc, chế độ object-centric:** tọa độ 3D Euclid thô, **không biến đổi gì**, với giả định cảnh nằm gọn trong 1 hộp đã biết. Nếu có nội dung ngoài hộp → **không biểu diễn được**.
> - **NeRF gốc, chế độ forward-facing:** dùng **NDC** — bóp hình chóp camera sâu vô hạn thành khối lập phương, với trục z tương ứng disparity. Hạn chế: **chỉ mở được 1 hướng duy nhất** (hướng camera nhìn).
> - **Mip-NeRF 360:** `contract(·)` — "NDC theo **mọi** hướng", đối xứng cầu quanh tâm cảnh.
> - **Vì sao bắt buộc phải đổi:** cảnh 360° có nội dung ở xa theo **mọi** hướng. NDC chỉ mở trục z nên vẫn để các hướng khác bị chặn → thất bại.
> - **Bằng chứng số [P360, Ablation H]:** nếu **bỏ phép co** và thay bằng cách "thêm tần số positional encoding để bao trọn cảnh", kết quả tụt: PSNR **24.37 → 23.77**, SSIM **0.687 → 0.642**, LPIPS **0.300 → 0.347**, **đồng thời chậm hơn** (7.09h → 8.79h) và **nhiều tham số hơn** (9.0M → 10.9M). Tức phép co **vừa tốt hơn vừa rẻ hơn**.
> - **[P360, Ablation I]:** dùng phép co + lấy mẫu theo thang logarit của **DONeRF** cũng kém hơn: PSNR **23.99**, SSIM **0.654**. Tức dạng `2 − 1/r` không phải tùy ý — nó thắng các dạng co khác đã công bố.

### 2.4. ĐÓNG GÓP MỚI QUAN TRỌNG NHẤT — áp phép co lên **Gaussian**, không chỉ lên **điểm** (Eq. 8–9)

> **⚠️ Đây là điểm mà mọi bản tóm tắt sơ bộ thường bỏ sót, nhưng lại là đóng góp kỹ thuật cốt lõi của Mục 2.**

**[P360, Mục 2]** mở đầu bằng đúng vấn đề này: *đã có công trình trước nghiên cứu việc tham số hóa **điểm** cho cảnh unbounded, nhưng điều đó **không giải quyết** được bài toán trong ngữ cảnh mip-NeRF, nơi ta buộc phải tái tham số hóa **các Gaussian***.

**Vì sao đây là vấn đề thật:** từ mục 2.1, đơn vị lấy mẫu của Mip-NeRF **không phải điểm mà là cặp (μ, Σ)**. Ta biết cách co 1 điểm (Eq. 10), nhưng **Σ thì co như thế nào?** Nếu chỉ co μ và để nguyên Σ, thì Gaussian sau co sẽ sai hình dạng hoàn toàn: 1 nón cụt ở xa, vốn rất to trong không gian thật, sau khi co phải trở nên rất **nhỏ và dẹt** — nếu giữ Σ nguyên thì nó vẫn to, và IPE sẽ tắt sai các tần số.

**Giải pháp của paper — xấp xỉ tuyến tính hóa (linearization).** Với `f(x)` là **1 phép biến đổi tọa độ trơn (smooth) bất kỳ** ánh xạ `ℝⁿ → ℝⁿ` (ở đây n = 3), khai triển Taylor bậc 1 quanh μ **[P360, Eq. 8]**:

```
f(x) ≈ f(μ) + J_f(μ) · (x − μ)                                    (Eq. 8)
```

Từ đó, cách áp `f` lên cả cặp (μ, Σ) **[P360, Eq. 9]**:

```
f(μ, Σ) = ( f(μ) ,  J_f(μ) · Σ · J_f(μ)ᵀ )                        (Eq. 9)
```

#### Chú thích ký hiệu Eq. 8–9

| Ký hiệu | Ý nghĩa |
|---|---|
| `f(x)` | 1 phép biến đổi tọa độ **trơn** (khả vi) từ ℝ³ → ℝ³. Trong Mip-NeRF 360, `f = contract` |
| `J_f(μ)` | **ma trận Jacobian** của `f` tại điểm μ — ma trận 3×3 gồm mọi đạo hàm riêng `∂f_i/∂x_j`. Nó là **xấp xỉ tuyến tính tốt nhất** của `f` ngay tại lân cận μ |
| `J_f(μ)ᵀ` | ma trận chuyển vị của Jacobian |
| `J Σ Jᵀ` | **quy tắc biến đổi covariance qua 1 phép biến đổi tuyến tính** — quy tắc chuẩn trong lý thuyết xác suất: nếu `y = A·x` thì `Cov(y) = A·Cov(x)·Aᵀ` |
| `f(μ, Σ)` | kết quả: 1 Gaussian mới, mean là `f(μ)`, covariance là `J Σ Jᵀ` |

**Vì sao công thức này đúng về mặt xác suất [SUY-RA]:** `f` là phi tuyến, nên ảnh của 1 Gaussian qua `f` **không còn là Gaussian** nữa (nó bị uốn méo). Nhưng nếu Gaussian "đủ nhỏ" so với độ cong của `f`, thì trong vùng đó `f` gần như tuyến tính (đúng theo Eq. 8), và phép biến đổi tuyến tính **bảo toàn tính Gaussian** với luật covariance `Cov → A Cov Aᵀ`. Vậy Eq. 9 là **xấp xỉ Gaussian bậc 1** của ảnh thực sự.

**Tên gọi của kỹ thuật này:** **[P360, Mục 2]** ghi rõ Eq. 9 *"tương đương về chức năng với Extended Kalman filter kinh điển, trong đó `f` đóng vai trò mô hình chuyển trạng thái (state transition model)"*. Đây là lý do paper và phần Kết luận gọi đóng góp này là **"Kalman-like scene parameterization"** (tham số hóa cảnh kiểu Kalman).

| Thuật ngữ | Ý nghĩa |
|---|---|
| **Kalman filter** | Thuật toán cổ điển (Kalman, 1960) theo dõi trạng thái 1 hệ động lực bằng cách truyền 1 phân phối Gaussian qua các bước thời gian |
| **Extended Kalman filter (EKF)** | Biến thể dùng khi mô hình chuyển trạng thái là **phi tuyến**: tuyến tính hóa nó bằng Jacobian tại điểm hiện tại, rồi truyền covariance theo `J Σ Jᵀ`. **Chính xác bằng Eq. 9.** |

**Tính tổng quát — một điểm đáng nhấn:** vì Eq. 8–9 đúng với **mọi** `f` trơn, paper tự nhận đóng góp này là **"1 phương pháp áp bất kỳ phép tham số hóa trơn nào lên thể tích (volumes) chứ không chỉ lên điểm (points)"** — tách bạch với đóng góp thứ hai là *bản thân* phép tham số hóa `contract` **[P360, Introduction]**. Tức là Mục 2 có **2 đóng góp riêng biệt**, không phải 1.

**Cách tính `J_f(μ)` trong thực tế [P360, Phụ lục B]:** có thể tính trực tiếp bằng **autodiff** (vi phân tự động) của các framework học sâu. Cách rẻ hơn (không cần dựng tường minh ma trận Jacobian) là dựng 1 **hàm** mà việc áp nó tương đương với nhân ma trận `J_f(μ)`; trong **Jax**, dùng toán tử `linearize` và **áp 2 lần liên tiếp lên Σ**, với việc **chuyển vị các chiều của ma trận covariance sau mỗi lần áp**. (Lý do áp 2 lần: `J Σ Jᵀ` cần nhân J ở cả 2 phía của Σ.)

### 2.5. [SUY-RA] Tính tường minh Jacobian của `contract` — vì sao Gaussian ở xa trở nên **cực kỳ dị hướng**

Paper không in `J_contract` ra, nhưng tính được nó giúp hiểu 1 chi tiết của paper mà nếu không có nó thì khó hiểu (xem mục 2.6). **Phần dưới là dẫn giải của người biên soạn — đúng toán học, nhưng không nằm trong văn bản paper.**

Với `r = ‖x‖ > 1`, đặt `u = x/r` (vector đơn vị xuyên tâm) và `h(r) = 2 − 1/r`. Khi đó `contract(x) = h(r)·u`. Lấy đạo hàm, dùng `∂r/∂x = uᵀ` và `∂u/∂x = (I − u uᵀ)/r`:

```
J = h'(r) · u uᵀ  +  h(r)/r · (I − u uᵀ)
  = (1/r²) · u uᵀ  +  (2/r − 1/r²) · (I − u uᵀ)
```

Đây là 1 ma trận có **2 trị riêng (eigenvalue)** rõ ràng:

| Hướng | Trị riêng (hệ số co) | Ý nghĩa |
|---|---|---|
| **Xuyên tâm** (dọc theo u — hướng ra/vào tâm cảnh) | `1/r²` | Co theo **bình phương nghịch đảo** khoảng cách |
| **Tiếp tuyến** (2 hướng vuông góc u) | `2/r − 1/r²` | Co theo xấp xỉ **nghịch đảo** khoảng cách |

Kiểm tra số:

| r | Co xuyên tâm `1/r²` | Co tiếp tuyến `2/r − 1/r²` | Tỉ lệ dị hướng |
|---|---|---|---|
| 1 | 1.000 | 1.000 | **1× (không dị hướng — khớp liền mạch với vùng trong)** |
| 2 | 0.250 | 0.750 | 3× |
| 4 | 0.0625 | 0.4375 | 7× |
| 10 | 0.0100 | 0.1900 | 19× |
| 100 | 0.0001 | 0.0199 | 199× |

**Kết luận quan trọng:** ở xa, phép co bóp hướng xuyên tâm **mạnh hơn hẳn** hướng tiếp tuyến (tỉ lệ ≈ `2r − 1`). Vì vậy 1 hình nón cụt ở xa — vốn gần như hình cầu dài — sau khi co trở thành 1 **đĩa dẹt rất mỏng theo hướng xuyên tâm**, tức 1 Gaussian **cực kỳ dị hướng (highly anisotropic)**.

Điều này khớp chính xác với nhận xét trong **[P360, Phụ lục A]**: *mô hình của họ cần truy cập **ma trận covariance đầy đủ**, vì nếu không thì phép bóp kiểu Kalman sẽ **không chính xác khi gặp các Gaussian dị hướng mạnh — thứ xảy ra thường xuyên ở các phần xa của cảnh***. Phần dẫn giải ở trên giải thích **vì sao** chúng dị hướng mạnh.

### 2.6. Hệ quả: **Off-Axis IPE** — một thay đổi MỚI của bản 360 so với Mip-NeRF

**[P360, Phụ lục A]** — đây là chi tiết thường bị bỏ qua khi tóm tắt, nhưng nó là 1 **thay đổi thật** so với Mip-NeRF, không phải phần kế thừa.

**Vấn đề:** khi dựng đặc trưng IPE, ta phải chọn 1 **cơ sở P (basis)** để chiếu Gaussian lên. Mip-NeRF chọn `P = ma trận đơn vị` (tức chiếu lên đúng 3 trục x, y, z) — gọi là **axis-aligned IPE**. Lựa chọn này tiện vì chỉ cần **đường chéo** của Σ (đúng như `diag(Σ)` trong Eq. 1), không cần tính các phần tử ngoài đường chéo.

Nhưng axis-aligned IPE có 1 **lỗ hổng biểu diễn**: 2 Gaussian có **cùng phân phối biên (marginal distribution) trên từng trục** nhưng **hướng nghiêng khác nhau** sẽ cho **đặc trưng IPE giống hệt nhau** — mạng không thể phân biệt chúng. **[P360, Figure 8]** minh họa đúng điều này bằng 3 Gaussian 2 biến có marginal giống nhau.

Với phép co ở mục 2.4–2.5, Gaussian ở xa **rất dị hướng và nghiêng theo hướng xuyên tâm** (hướng này nói chung **không trùng** trục x/y/z nào) — nên lỗ hổng này trở thành vấn đề thật.

**Giải pháp:** dùng **off-axis IPE** — thay `P = I` bằng 1 **ma trận cao và gầy (large skinny matrix)** gồm các **đỉnh đã chuẩn hóa độ dài 1 của 1 khối hai mươi mặt được chia nhỏ 2 lần (twice-tessellated icosahedron)**, đã loại bỏ các bản sao âm trùng lặp. **[P360, Eq. 17]** in tường minh ma trận này — gồm **21 hàng × 3 cột** (21 hướng chiếu). Một vài hàng đầu để minh họa:

```
P = ⎡ 0.8506508   0           0.5257311  ⎤
    ⎢ 0.809017    0.5         0.309017   ⎥
    ⎢ 0.5257311   0.8506508   0          ⎥
    ⎢ 1           0           0          ⎥
    ⎢ ...  (tổng cộng 21 hàng, xem Eq. 17 của paper để lấy đủ)  ⎥
    ⎣ −0.809017   0.5        −0.309017   ⎦
```

| Thuật ngữ | Ý nghĩa |
|---|---|
| **Icosahedron** | Khối 20 mặt đều — 1 trong 5 khối đa diện Platon, có 12 đỉnh |
| **Tessellation / chia nhỏ (subdivide)** | Chia mỗi mặt tam giác thành các tam giác nhỏ hơn rồi đẩy đỉnh mới ra mặt cầu → được nhiều đỉnh phân bố **gần đều** trên mặt cầu hơn |
| **"Loại bỏ bản sao âm"** | Nếu v là 1 đỉnh thì −v cũng là 1 đỉnh (icosahedron đối xứng tâm); nhưng chiếu lên v và lên −v cho thông tin **như nhau** (vì sin/cos chỉ khác dấu), nên chỉ giữ 1 trong 2 |
| **Basis P** | Tập các hướng mà Gaussian được chiếu lên trước khi mã hóa sin/cos. 21 hướng phân bố gần đều trên nửa mặt cầu ⇒ bất kể Gaussian nghiêng theo hướng nào, luôn có vài hướng trong P "nhìn thấy" được độ nghiêng đó |

**Chi phí tính toán và cách tối ưu [P360, Phụ lục A]:** tính IPE với P lớn theo đúng công thức của Mip-NeRF, tức `diag(P Σ Pᵀ)`, là **quá đắt** (phải dựng ma trận 21×21 rồi chỉ lấy đường chéo). Cách thay thế khả thi là tính biểu thức tương đương:

```
sum( Pᵀ ∘ (Σ Pᵀ) , 0 )
```

trong đó `∘` là nhân từng phần tử và `sum(·, 0)` là tổng theo **hàng**. Với tối ưu nhỏ này, off-axis IPE chỉ **đắt hơn một chút** so với axis-aligned IPE. *(Ghi chú về độ chắc chắn: người biên soạn hiểu đây là mẹo "chỉ tính các phần tử đường chéo cần thiết thay vì cả ma trận"; quy ước chính xác về chiều tổng (`sum` theo hàng hay cột) phụ thuộc quy ước lưu trữ ma trận của Jax, nên **không nên trích dẫn chi tiết trục này mà không đọc code công bố**.)*

**Giá trị thực nghiệm [P360, Phụ lục A]:** bỏ đặc trưng off-axis làm SSIM trên scene `bicycle` tụt từ **0.687 → 0.664** — tức mức ảnh hưởng tương đương với việc bỏ hẳn IPE (mục 2.2).

> **🔁 ĐỐI CHIẾU — 3 cấp độ encoding**
> | Mô hình | Encoding | Nhận biết tỉ lệ? | Nhận biết **hướng nghiêng** của vùng? |
> |---|---|---|---|
> | **NeRF gốc** | PE của điểm | ❌ | ❌ (không có khái niệm vùng) |
> | **Mip-NeRF** | IPE axis-aligned (P = I) | ✅ | ❌ |
> | **Mip-NeRF 360** | **IPE off-axis (P = 21 đỉnh icosahedron)** | ✅ | ✅ |
> **Lý do leo thang:** mỗi lần thêm 1 thành phần mới (vùng thay điểm → phép co làm vùng bị nghiêng), encoding phải được nâng cấp tương ứng để không mất thông tin.

### 2.7. ĐÓNG GÓP MỚI — tham số hóa khoảng cách tia theo disparity: ánh xạ t ↔ s (Eq. 11)

Đã xử lý "tọa độ 3D co thế nào". Còn 1 nửa câu hỏi: **chọn các khoảng cách `t` ở đâu dọc tia?**

**[P360, Mục 2]** phân tích: trong NeRF, việc này thường làm bằng cách lấy mẫu **đều** giữa cận gần và cận xa (Eq. 5). **Nhưng** — và đây là 1 quan sát tinh tế mà paper nêu ra — **nếu đang dùng NDC, thì chuỗi mẫu "đều" đó thực chất là đều theo inverse depth (disparity), không phải đều theo khoảng cách**. Thiết kế đó rất phù hợp cho cảnh unbounded khi camera chỉ nhìn 1 hướng, nhưng **không áp dụng được** cho cảnh unbounded theo mọi hướng. Vì vậy Mip-NeRF 360 **lấy mẫu `t` tuyến tính theo disparity một cách tường minh**.

Để làm được, paper định nghĩa 1 **ánh xạ khả nghịch (invertible mapping)** giữa khoảng cách Euclid `t` và khoảng cách **đã chuẩn hóa** `s` **[P360, Eq. 11]**:

```
        g(t) − g(t_n)
s  ≜  ─────────────────  ,        t  ≜  g⁻¹( s·g(t_f) + (1−s)·g(t_n) )          (Eq. 11)
       g(t_f) − g(t_n)
```

#### Chú thích ký hiệu Eq. 11

| Ký hiệu | Ý nghĩa |
|---|---|
| `t` | khoảng cách **Euclid** dọc tia (đơn vị thật của không gian world) |
| `s` | khoảng cách **đã chuẩn hóa**, luôn nằm trong **[0, 1]**; `s=0` ↔ `t=t_n`, `s=1` ↔ `t=t_f` |
| `t_n`, `t_f` | cận gần (near) và cận xa (far) của tia — giống NeRF gốc |
| `g(·)` | **1 hàm vô hướng khả nghịch bất kỳ** — đây là "núm điều khiển" quyết định kiểu phân bố mẫu |
| `g⁻¹(·)` | hàm nghịch đảo của `g` |
| `≜` | "được định nghĩa là" |
| **"s-space" / "t-space"** | 2 cách nói về khoảng cách dọc tia. Paper dùng xen kẽ, chọn cái nào thuận tiện hơn trong từng ngữ cảnh **[P360, Mục 2]** |

**Đọc công thức:** vế trái là phép **nội suy tuyến tính trong miền `g`**: đưa `t` qua `g`, chuẩn hóa về [0,1] bằng 2 mốc `g(t_n)`, `g(t_f)`. Vế phải là phép đảo ngược. Vì `g` khả nghịch, 2 chiều này khớp nhau hoàn hảo — ánh xạ **1-1**.

#### Lựa chọn `g` quyết định kiểu lấy mẫu

**[P360, Mục 2]** nêu 2 lựa chọn cụ thể:

| `g(x)` | Mẫu đều trong s-space tương ứng với gì trong t-space | Thuộc về |
|---|---|---|
| **`g(x) = 1/x`** | **tuyến tính theo disparity** (nghịch đảo khoảng cách) | **lựa chọn của Mip-NeRF 360** |
| `g(x) = log(x)` | thang **logarit** | lấy lại đúng cách phân bố của **DONeRF** |

Paper chọn **`g(x) = 1/x`** và dựng các mẫu **phân bố đều trong s-space** ⇒ các khoảng cách `t` thu được **phân bố tuyến tính theo disparity**.

#### [SUY-RA] Kiểm chứng bằng số với `g(x) = 1/x`

Lấy `t_n = 1`, `t_f → ∞` (nên `g(t_f) = 1/∞ = 0`). Thay vào Eq. 11:

```
s = (1/t − 1/1) / (0 − 1) = 1 − 1/t        ⟹        t = 1/(1 − s)
```

| s (đều nhau) | t tương ứng | Nhận xét |
|---|---|---|
| 0.00 | 1.0 | cận gần |
| 0.25 | 1.33 | bước t nhỏ |
| 0.50 | 2.0 | |
| 0.75 | 4.0 | bước t bắt đầu phình |
| 0.90 | 10.0 | |
| 0.99 | 100.0 | |
| → 1.00 | → ∞ | **cận xa vô hạn được xử lý tự nhiên, không cần đặt `t_f` hữu hạn tùy ý** |

**Đây là câu trả lời cho vấn đề "không có `t_f` hữu hạn" của cảnh unbounded:** trong s-space, cận xa luôn là `s = 1`, hữu hạn và gọn gàng, kể cả khi `t_f = ∞`.

#### [SUY-RA] Chứng minh: phép co và cách chia khoảng theo disparity **triệt tiêu lẫn nhau**

**[P360, Figure 2]** phát biểu (bằng lời) rằng: thiết kế của `contract(·)` **kết hợp với** lựa chọn chia khoảng tia tuyến tính theo disparity khiến **các tia bắn ra từ 1 camera đặt tại gốc cảnh sẽ có các khoảng cách đều nhau trong vùng màu cam** (tức vùng đã co, bán kính 1→2). Paper cũng nói lựa chọn này **"đối trọng" (counter-balance)** với `contract(·)`, và rằng 2 thiết kế này được **đồng thiết kế (co-designed)**. Dưới đây là chứng minh ngắn — *dẫn giải của người biên soạn, không có trong paper*:

Xét 1 tia bắn từ **gốc tọa độ cảnh** nên với điểm trên tia ở khoảng cách `t > 1`, ta có `‖x‖ = t`. Theo Eq. 10, bán kính sau co:

```
‖contract(x)‖ = 2 − 1/t
```

Theo kết quả trên (với `t_n = 1`, `t_f = ∞`): `1/t = 1 − s`. Thay vào:

```
‖contract(x)‖ = 2 − (1 − s) = 1 + s
```

**Kết quả:** khi `s` chạy đều từ 0 → 1, bán kính trong không gian co chạy đều từ 1 → 2. **Hai phi tuyến triệt tiêu nhau hoàn hảo, cho ra các khoảng cách đều tăm tắp trong không gian đã co.** ∎

**Vì sao điều này quan trọng:** **[P360, Mục 2]** kết luận rằng nhờ đồng thiết kế này, họ có được 1 phép tham số hóa cảnh unbounded **rất giống với tình huống cực kỳ hiệu quả của chính paper NeRF gốc: các khoảng tia cách đều nhau trong 1 không gian bị chặn**. Nói cách khác: Mip-NeRF 360 **không phát minh 1 chế độ hoạt động mới cho MLP** — nó **biến bài toán unbounded trở lại thành đúng bài toán bounded cách đều mà NeRF gốc vốn đã giải tốt**. Đây là tư tưởng thiết kế đẹp nhất của Mục 2.

### 2.8. Lấy mẫu trong s-space — thay thế Stratified Sampling của NeRF gốc

Paper nhắc lại cách lấy mẫu của Mip-NeRF **[P360, Eq. 5 và Eq. 6]** rồi nêu thay đổi.

**Cách của Mip-NeRF (Eq. 5, Eq. 6):**

```
t_c ~ U[t_n, t_f] ,      t_c = sort({t_c})                         (Eq. 5)
t_f ~ hist(t_c, w_c) ,   t_f = sort({t_f})                         (Eq. 6)
```

| Ký hiệu | Ý nghĩa |
|---|---|
| `t_c` | vector khoảng cách **"coarse"** (thô) — lượt lấy mẫu đầu tiên |
| `U[t_n, t_f]` | phân phối **đều (uniform)** trên đoạn [t_n, t_f] |
| `sort({·})` | sắp xếp tăng dần — cần thiết vì các khoảng `T_i` phải liền kề theo thứ tự |
| `w_c` | vector trọng số **"coarse"** do MLP sinh ra ở lượt đầu (xem Giai đoạn 3, Eq. 4) |
| `hist(t_c, w_c)` | **histogram** (biểu đồ tần suất) định nghĩa bởi các mốc `t_c` và trọng số `w_c`; lấy mẫu từ nó bằng **inverse transform sampling** (kỹ thuật đã mô tả trong `pipeline_NeRF.md` Giai đoạn 4) |
| `t_f` | vector khoảng cách **"fine"** (tinh) — lượt lấy mẫu thứ hai, tập trung vào nơi `w_c` cao |

**[P360, Mục 1]** cũng nêu 1 chi tiết của Mip-NeRF: *khi train, việc lấy mẫu này là **ngẫu nhiên (stochastic)**; nhưng khi đánh giá (evaluation), các mẫu được **đặt cách đều** từ `t_n` tới `t_f`* — tức có sự khác biệt train/test có chủ đích.

**Thay đổi của Mip-NeRF 360 — ngắn nhưng rất quan trọng [P360, Mục 2]:** thay vì thực hiện việc lấy mẫu của Eq. 5 và Eq. 6 bằng khoảng cách **`t`**, Mip-NeRF 360 thực hiện chúng bằng khoảng cách **`s`**.

Hệ quả, như paper nêu, có **2 tầng**:
1. **Các mẫu khởi tạo** (Eq. 5) cách đều theo **disparity**, không phải theo khoảng cách.
2. **Các lượt lấy mẫu lại (resampling) tiếp theo** từ từng khoảng của trọng số `w` (Eq. 6) **cũng** phân bố theo đúng tinh thần đó.

Điểm (2) là điều dễ bị bỏ sót: không chỉ lượt đầu, mà **mọi lượt resample đều diễn ra trong s-space**, nên tính chất "cách đều trong không gian co" được bảo toàn xuyên suốt, chứ không bị phá vỡ sau lượt đầu.

> **🔁 ĐỐI CHIẾU NeRF GỐC — lấy mẫu dọc tia (so sánh trực tiếp)**
>
> | | **NeRF gốc** | **Mip-NeRF 360** |
> |---|---|---|
> | Công thức lấy mẫu lượt 1 | `t_i ~ U[ t_n + (i−1)/N·(t_f−t_n) , t_n + i/N·(t_f−t_n) ]` — chia **[t_n, t_f] thành N đoạn bằng nhau theo `t`**, lấy 1 mẫu ngẫu nhiên mỗi đoạn (stratified sampling) | Chia **[0, 1] theo `s`**, rồi đổi về `t` qua Eq. 11 với `g(x) = 1/x` |
> | Mẫu cách đều theo cái gì | **khoảng cách Euclid `t`** | **disparity `1/t`** |
> | Cần `t_f` hữu hạn? | **Có — bắt buộc.** Phải biết trước cảnh kết thúc ở đâu | **Không.** `t_f = ∞` vẫn hợp lệ, vì `s` luôn kết thúc tại 1 |
> | Phân bố mẫu ở vùng xa | Càng xa, khoảng cách giữa 2 mẫu liên tiếp **không đổi** theo `t`, nhưng "lượng cảnh" mà mỗi mẫu phải đại diện thì tăng vọt ⇒ vùng xa bị **lấy mẫu dưới mức nghiêm trọng** | Khoảng cách giữa 2 mẫu **giãn ra theo t²**, khớp đúng với việc vùng xa cần ít dung lượng hơn ⇒ **mật độ mẫu tỉ lệ với độ quan trọng thị giác** |
> | Tương tác với tham số hóa không gian | Không có tham số hóa nào để tương tác | **Đồng thiết kế** với `contract(·)`: 2 phi tuyến triệt tiêu nhau, cho khoảng cách đều trong không gian co (mục 2.7) |
> | Hệ quả thực tế | Nền xa bị mờ/thiếu chi tiết — đúng như **[P360, Figure 1a]** minh họa với mip-NeRF (SSIM 0.526 vs 0.804 của Mip-NeRF 360 trên cùng cảnh) | Nền xa có chi tiết, depth map hợp lý |

### 2.9. Kết quả của Giai đoạn 2

Với mỗi tia, ta có 1 tập các **khoảng** chia theo `s` (đều trong s-space). Với mỗi khoảng:
1. Tính hình nón cụt tương ứng → `(μ, Σ)` trong không gian Euclid gốc (mục 2.1).
2. Áp phép co kiểu Kalman → `contract(μ, Σ)` theo Eq. 9–10 (mục 2.3–2.4), được 1 Gaussian nằm gọn trong cầu bán kính 2, có thể rất dị hướng.
3. Mã hóa bằng **off-axis IPE** → vector đặc trưng (mục 2.2, 2.6). **[P360, Mục 2]** ghi gọn thành: thay vì dùng đặc trưng IPE của Mip-NeRF trong không gian Euclid (Eq. 1), họ dùng **các đặc trưng tương tự trong không gian đã co**, viết là `γ(contract(μ, Σ))`.

Các vector đặc trưng này là input cho MLP ở Giai đoạn 3.

---

## Giai đoạn 3: Kiến trúc MLP & Volume Rendering

Giai đoạn này **ít thay đổi nhất** so với NeRF gốc về mặt *công thức*, nhưng thay đổi **rất nhiều** về mặt *quy mô* và một vài chi tiết kỹ thuật. Nội dung tương ứng **[P360, Mục 1 và Mục 5]**.

### 3.1. MLP làm gì — Eq. 2

**[P360, Eq. 2]**:

```
∀ T_i ∈ t ,     (τ_i , c_i) = MLP( γ( r(T_i) ) ; Θ_NeRF )
```

#### Chú thích ký hiệu Eq. 2

| Ký hiệu | Ý nghĩa | Đối chiếu NeRF gốc |
|---|---|---|
| `∀ T_i ∈ t` | "với mọi khoảng `T_i` trong vector mốc `t`" — chạy qua **từng khoảng** trên tia | NeRF gốc chạy qua **từng điểm** |
| `τ_i` (tau) | **density** (mật độ thể tích) của khoảng thứ i | NeRF gốc ký hiệu bằng `σ`. **Chỉ khác tên biến**, cùng ý nghĩa vật lý: xác suất vi phân tia bị chặn tại đó |
| `c_i` | **màu** (RGB) của khoảng thứ i | giống `c_i` của NeRF gốc |
| `γ(r(T_i))` | đặc trưng IPE của hình nón cụt ứng với khoảng `T_i` — kết quả của Giai đoạn 2 | NeRF gốc: `γ(x)` của 1 điểm |
| `Θ_NeRF` | **tập toàn bộ trọng số** của "NeRF MLP" | NeRF gốc: `Θ` (và có 2 bộ: coarse + fine) |

**Về hướng nhìn `d`:** **[P360, Mục 1]** ghi rõ: *vector hướng nhìn `d` **cũng** được đưa vào MLP, nhưng chúng tôi lược bỏ nó trong ký hiệu cho đơn giản.* Nghĩa là cơ chế **view-dependent color** (màu phụ thuộc góc nhìn) của NeRF gốc **được giữ nguyên hoàn toàn**.

> **⚠️ Điểm không chắc chắn (ghi rõ thay vì đoán):** paper **không mô tả chi tiết** cách `d` được nối vào mạng (vị trí nối, số chiều encoding của `d`, có skip connection ở lớp nào...). Theo tinh thần "kế thừa Mip-NeRF", rất có thể kiến trúc giống Mip-NeRF/NeRF gốc (tách nhánh density trước khi `d` được nối vào, rồi 1 lớp nhỏ cho màu) — nhưng **đây là suy đoán hợp lý, không phải dữ kiện paper**. Khi viết báo cáo đồ án, nếu cần chi tiết này thì phải đối chiếu **code công bố** (`multinerf` / `mipnerf360` của Google Research), và ghi rõ nguồn là code chứ không phải paper.

### 3.2. Hai thay đổi cụ thể trong kiến trúc mạng

#### Thay đổi 1 — Hàm kích hoạt của density: **softplus** thay vì **ReLU**

**[P360, Mục 5]** ghi: cả 2 MLP *dùng kích hoạt nội là **ReLU** và kích hoạt **softplus** cho density `τ`*.

| Hàm | Công thức | Tính chất |
|---|---|---|
| **ReLU** | `max(0, x)` | Cắt phẳng tuyệt đối về 0 với mọi input âm ⇒ **gradient bằng 0** ở vùng âm (nơ-ron có thể "chết") |
| **Softplus** | `log(1 + eˣ)` | Luôn **dương**, **trơn** (khả vi mọi nơi), là phiên bản làm mượt của ReLU; gradient **không bao giờ bằng 0** |

> **🔁 ĐỐI CHIẾU NeRF GỐC — kích hoạt density**
> - **NeRF gốc:** dùng **ReLU** cho `σ` (để đảm bảo density không âm).
> - **Mip-NeRF 360:** dùng **softplus**.
> - **Lý do [SUY-RA — paper chỉ nêu dữ kiện, không nêu lý do]:** nếu density vừa bị đẩy xuống âm 1 chút, ReLU cho gradient 0 và nơ-ron đó không còn cách nào học lại. Với cảnh unbounded có rất nhiều vùng không gian trống (density phải ≈ 0 trên phần lớn tia), vấn đề "nơ-ron density chết" nghiêm trọng hơn nhiều so với cảnh bounded. Softplus luôn có gradient khác 0 nên vùng trống vẫn có thể được "sửa lại" nếu tối ưu hóa phát hiện là sai. Diễn giải này hợp lý nhưng **cần đánh dấu là suy luận**.

#### Thay đổi 2 — Quy mô mạng tăng mạnh

**[P360, Mục 5]**:

| Mạng | Số lớp | Số kênh ẩn (hidden units) | Dự đoán gì |
|---|---|---|---|
| **Proposal MLP** `Θ_prop` | **4** | **256** | Chỉ **density** (chi tiết ở Giai đoạn 4) |
| **NeRF MLP** `Θ_NeRF` | **8** | **1024** | **density + màu** |

So sánh: NeRF gốc dùng **8 lớp × 256 kênh** cho *mỗi* mạng (coarse và fine). Mip-NeRF 360 giữ **8 lớp** nhưng tăng độ rộng lên **1024 kênh** — gấp **4 lần** chiều rộng, tức khoảng **16 lần** số trọng số ở các lớp giữa (vì số trọng số 1 lớp FC ≈ kênh_vào × kênh_ra).

**Con số tổng [P360, Introduction + Table 1]:**
- Tổng dung lượng mô hình lớn hơn Mip-NeRF khoảng **~15×**, nhưng thời gian train chỉ tăng khoảng **~2×**.
- Số tham số: Mip-NeRF **0.7M** → Mip-NeRF 360 **9.9M** (trên dataset 360).

**Vì sao giữ được tỉ lệ "15× dung lượng, 2× thời gian":** chính là nhờ cơ chế Proposal Network ở Giai đoạn 4 — MLP lớn chỉ được gọi **1 lần với ít mẫu**, còn các lượt lấy mẫu lặp lại nhiều dùng MLP nhỏ. Đây là lý do Giai đoạn 4 và Giai đoạn 3 không tách rời được về mặt thiết kế.

**Bằng chứng cho việc cần mạng lớn [P360, Ablation F]:** dùng **NeRF MLP nhỏ** (256 kênh thay vì 1024) làm train nhanh hơn (**4.31h** so với **7.09h**) nhưng chất lượng tụt rõ: PSNR **24.37 → 22.80**, SSIM **0.687 → 0.515**, LPIPS **0.300 → 0.480**. Paper kết luận: điều này cho thấy **giá trị của mô hình dung lượng cao khi xử lý cảnh nhiều chi tiết**.

### 3.3. Volume Rendering — Eq. 3 & Eq. 4: **giống hệt NeRF gốc về công thức**

**[P360, Eq. 3 và Eq. 4]** — paper dẫn nguồn phép cầu phương số (numerical quadrature) tới Max (1995), đúng như NeRF gốc:

```
C(r, t) = Σ_i  w_i · c_i                                                      (Eq. 3)

w_i = ( 1 − e^( −τ_i (t_{i+1} − t_i) ) ) · e^( −Σ_{i'<i} τ_{i'} (t_{i'+1} − t_{i'}) )   (Eq. 4)
```

#### Chú thích ký hiệu Eq. 3–4

| Ký hiệu | Ý nghĩa | Đối chiếu NeRF gốc |
|---|---|---|
| `C(r, t)` | **màu pixel cuối cùng** đã render cho tia `r` với bộ mốc `t` | NeRF gốc: `Ĉ(r)` |
| `w_i` | **trọng số alpha-compositing** của khoảng thứ i — "khoảng này đóng góp bao nhiêu phần vào màu pixel" | NeRF gốc: `w_i = T_i · α_i` — **cùng một đại lượng** |
| `1 − e^(−τ_i(t_{i+1}−t_i))` | **độ chắn sáng (opacity, α_i)** của riêng khoảng i. `(t_{i+1} − t_i)` chính là `δ_i` của NeRF gốc | giống hệt `α_i = 1 − exp(−σ_i δ_i)` |
| `e^(−Σ_{i'<i} τ_{i'}(t_{i'+1}−t_{i'}))` | **transmittance tích lũy `T_i`** — xác suất ánh sáng "sống sót" đi qua **mọi khoảng phía trước** mà chưa bị chặn | giống hệt `T_i = exp(−Σ_{j<i} σ_j δ_j)` |
| `i'` | chỉ số chạy qua các khoảng **đứng trước** khoảng i | — |

**Tính chất quan trọng mà paper nhấn mạnh [P360, Mục 1]:** *theo cách xây dựng, các trọng số alpha-compositing `w` được **đảm bảo có tổng nhỏ hơn hoặc bằng 1***.

**Vì sao tính chất này đáng nhấn:** nó khiến vector `w` **giống 1 phân phối xác suất (gần như vậy)** — tổng ≤ 1. Điều này là **tiền đề toán học** cho cả 2 cơ chế mới ở Giai đoạn 4:
- `L_prop` so sánh `w` và `ŵ` như **2 histogram** → chỉ có nghĩa khi chúng là khối lượng (mass) chuẩn hóa được.
- `L_dist` có cực tiểu tại `w = 0` **chính vì** `w` tổng ≤ 1 chứ không bắt buộc = 1 (paper nhắc lại đúng điều này ở Mục 4).

> **🔁 ĐỐI CHIẾU NeRF GỐC — volume rendering**
> **Kết luận:** về **công thức**, hoàn toàn **không thay đổi**. Mip-NeRF 360 vẫn dùng đúng phép cầu phương `Σ T_i α_i c_i` của NeRF gốc. Mọi thay đổi nằm ở **(a)** `τ_i, c_i` được tính từ **khoảng/Gaussian đã co** thay vì từ điểm thô, và **(b)** `t_i` được chọn trong **s-space** thay vì đều theo `t`. Đây là 1 ví dụ rõ về triết lý của paper: **giữ nguyên lõi vật lý đã đúng, chỉ thay phần tham số hóa và phần lấy mẫu**.

### 3.4. Một chi tiết nhỏ nhưng ảnh hưởng tới depth map — **màu nền ngẫu nhiên**

**[P360, Phụ lục A, "Background Colors"]** — chi tiết này không có trong NeRF gốc:

**Vấn đề:** NeRF và Mip-NeRF giả định **màu nền đã biết**, thường đặt là đen hoặc trắng. Hệ quả là mô hình thường tái tạo cảnh theo cách hậu cảnh bị biểu diễn **bán trong suốt (semi-transparent)** thay vì **đục (opaque)**. Hậu cảnh bán trong suốt **vẫn có thể cho ảnh render trông thật**, nhưng nó khiến các đại lượng **khoảng cách kết thúc tia trung bình/trung vị (mean/median ray termination distance)** trở nên vô nghĩa ⇒ **depth map kém chính xác**.

**Giải pháp:** khi tổng hợp (composite) màu pixel **trong lúc train**, lấy 1 **màu nền RGB ngẫu nhiên** từ `[0,1]³`. Việc này buộc quá trình train phải tái tạo 1 **hậu cảnh hoàn toàn đục**. Khi test, đặt màu nền cố định là `(0.5, 0.5, 0.5)`.

**Phạm vi áp dụng:** nền ngẫu nhiên được dùng cho **dataset 360 và dataset LLFF**; còn với **dataset Blender**, paper dùng nền trắng cố định/đã biết như các công trình trước.

| Thuật ngữ | Ý nghĩa |
|---|---|
| **Semi-transparent background** | Hậu cảnh mà mạng học thành 1 "màn sương" có density thấp trải dài, thay vì 1 bề mặt đục rõ ràng |
| **Median ray termination distance** | Khoảng cách `t` tại đó transmittance tích lũy giảm xuống một nửa — 1 cách ước lượng "độ sâu" của pixel. **[P360, Figure 7]** cho biết các depth map trong paper được vẽ bằng đại lượng này |
| **Composite** | Phép trộn màu đã render (`Σ w_i c_i`) với màu nền theo phần "ánh sáng còn lại" `1 − Σ w_i` |

**[SUY-RA] Logic vì sao nền ngẫu nhiên cưỡng chế hậu cảnh đục:** nếu `Σ w_i < 1`, phần thiếu hụt `1 − Σ w_i` sẽ bị lấp bằng màu nền. Khi màu nền **cố định**, mạng có thể "lợi dụng" nó: học `Σ w_i < 1` và để màu nền bù vào, vì màu nền đó luôn như vậy nên vẫn khớp ảnh thật. Khi màu nền **đổi ngẫu nhiên mỗi lần**, chiến lược đó thất bại — bất kỳ phần thiếu hụt nào cũng sẽ cho ra 1 màu ngẫu nhiên không khớp ảnh thật. Cách duy nhất để loss thấp là ép `Σ w_i ≈ 1`, tức hậu cảnh **phải đục**.

### 3.5. Kết quả của Giai đoạn 3

Với mỗi tia: 1 màu pixel dự đoán `C(r, t)` **và** 1 vector trọng số `w` (cùng bộ mốc `t`) mô tả "ánh sáng đến từ đâu dọc tia". **Cặp (t, w) này không chỉ là sản phẩm phụ** — nó là **nguyên liệu đầu vào cho cả 2 hàm loss mới** của Giai đoạn 4.

---

## Giai đoạn 4: TRỌNG TÂM 2 — Proposal Network, Online Distillation và Distortion Loss

Giai đoạn này gộp **Mục 3** ("Coarse-to-Fine Online Distillation" — trả lời Vấn đề 2: Efficiency) và **Mục 4** ("Regularization for Interval-Based Models" — trả lời Vấn đề 3: Ambiguity), cộng với **Mục 5** ("Optimization" — siêu tham số).

### 4.1. Vấn đề cần giải: tại sao kiến trúc coarse/fine của NeRF gốc **lãng phí**

**[P360, Introduction]** nêu phê phán rất cụ thể: chi phí train bị **làm trầm trọng hơn** bởi chính chiến lược resampling coarse-to-fine mà NeRF và Mip-NeRF dùng — MLP được đánh giá **nhiều lần** với các khoảng tia "coarse" và "fine", và **được giám sát bằng image reconstruction loss ở CẢ HAI lượt**. Paper gọi cách này là **lãng phí (wasteful)**, với lý do sắc gọn:

> **Bản render "coarse" của cảnh KHÔNG đóng góp gì vào ảnh cuối cùng.**

Nhắc lại hàm loss của Mip-NeRF **[P360, Eq. 7]** để thấy rõ:

```
Σ_{r∈R}   (1/10) · L_recon( C(r, t_c), C*(r) )  +  L_recon( C(r, t_f), C*(r) )          (Eq. 7)
```

| Ký hiệu | Ý nghĩa |
|---|---|
| `R` | tập các tia trong dữ liệu train (thực tế: trong batch hiện tại) |
| `C*(r)` | màu pixel **thật (ground truth)** ứng với tia `r`, lấy từ ảnh input |
| `L_recon` | **mean squared error** (MSE) — paper ghi rõ điều này cho Mip-NeRF |
| `C(r, t_c)`, `C(r, t_f)` | màu render ở lượt coarse và lượt fine |
| **`1/10`** | **hệ số 0.1** mà Mip-NeRF đặt cho nhánh coarse — chi tiết mà bản tóm tắt NeRF gốc thường bỏ qua. Ở NeRF gốc 2 nhánh có **trọng số bằng nhau** |
| `Θ_NeRF` (ẩn) | Mip-NeRF dùng **1 MLP duy nhất** dùng chung cho cả 2 lượt (khác NeRF gốc dùng 2 MLP riêng) |

**Chi phí quy mô mà paper dẫn ra làm bối cảnh [P360, Introduction]:** khi Martin-Brualla et al. mở rộng NeRF từ vật thể sang **tòa nhà**, họ phải **nhân đôi số kênh ẩn** và **tăng số lần đánh giá MLP lên 8×**. Paper nhận xét: NeRF **đã** mất nhiều giờ để train, và nhân thêm **~40×** nữa thì **không khả thi** với phần lớn ứng dụng.

### 4.2. Giải pháp: chia vai — 1 MLP **nhỏ** để "đề xuất", 1 MLP **lớn** để "render"

**[P360, Mục 3]**: thay vì train 1 NeRF MLP duy nhất được giám sát ở nhiều tỉ lệ, họ train **2 MLP**:

| | **NeRF MLP** `Θ_NeRF` | **Proposal MLP** `Θ_prop` |
|---|---|---|
| Kích thước | **8 lớp × 1024 kênh** (lớn) | **4 lớp × 256 kênh** (nhỏ) |
| Dự đoán | **density + màu** | **CHỈ density** — **không dự đoán màu** |
| Sinh ra | trọng số `w` (qua Eq. 4) + màu ⇒ **ảnh render** | trọng số đề xuất `ŵ` (qua Eq. 4) |
| Được giám sát bởi | **`L_recon`** — so với ảnh input thật | **`L_prop`** — so với `(t, w)` của NeRF MLP. **KHÔNG BAO GIỜ so với ảnh thật** |
| Số lần gọi mỗi tia | **1 lần**, với **32 mẫu** | **2 lần**, mỗi lần **64 mẫu** |

#### Chú thích ký hiệu mới của Giai đoạn 4

| Ký hiệu | Ý nghĩa |
|---|---|
| `Θ_prop` | tập trọng số của proposal MLP |
| `ŵ` (w có dấu mũ) | vector trọng số **đề xuất (proposal)**, do proposal MLP sinh ra qua Eq. 4 |
| `t̂` (t có dấu mũ) | vector mốc khoảng cách của histogram **đề xuất** |
| `(t̂, ŵ)` | **histogram đề xuất** — cặp (các mốc biên, các khối lượng) |
| `(t, w)` | **histogram của NeRF MLP** |
| `ŝ_k, ŵ_k` | histogram đề xuất của **lượt (level) thứ k** — vì có 2 lượt, k = 0 và 1; viết theo `s` vì việc lấy mẫu diễn ra trong s-space |
| **Histogram** | ở đây: 1 hàm bậc thang trên trục khoảng cách tia, mỗi "bin" là 1 khoảng `T_i` và chiều cao tỉ lệ với khối lượng `w_i` |

**Luồng dữ liệu [P360, Mục 3 + Figure 3]:**

```
 ┌─ Lượt 0 ─────────────────────────────────────────────────────────┐
 │  64 mẫu chia đều trong s-space                                   │
 │        ↓ Proposal MLP (4×256) → chỉ density → Eq.4 → (ŝ₀, ŵ₀)   │
 └────────────────────────┬─────────────────────────────────────────┘
                          │ resample 64 khoảng mới từ (ŝ₀, ŵ₀)
 ┌─ Lượt 1 ───────────────▼─────────────────────────────────────────┐
 │        ↓ Proposal MLP (4×256) → chỉ density → Eq.4 → (ŝ₁, ŵ₁)   │
 └────────────────────────┬─────────────────────────────────────────┘
                          │ resample 32 khoảng mới từ (ŝ₁, ŵ₁)
 ┌─ Lượt cuối ────────────▼─────────────────────────────────────────┐
 │        ↓ NeRF MLP (8×1024) → density + MÀU → Eq.4 → (s, w)      │
 │        ↓ Eq.3 → C(r,t)  ───────────────────►  ẢNH RENDER         │
 └──────────────────────────────────────────────────────────────────┘
```

**[P360, Mục 3]** nói rõ ý đồ: *dùng 1 NeRF MLP lớn và 1 proposal MLP nhỏ, **đánh giá và lấy mẫu lại từ proposal MLP nhiều lần với nhiều mẫu**, nhưng **chỉ đánh giá NeRF MLP đúng 1 lần với 1 tập mẫu nhỏ hơn**. Việc này cho ta 1 mô hình hành xử như thể nó có dung lượng cao hơn Mip-NeRF rất nhiều, mà chỉ đắt hơn 1 cách vừa phải khi train.*

Và 1 nhận định đáng chú ý: *dùng 1 MLP nhỏ để mô hình hóa phân phối đề xuất **không làm giảm độ chính xác**, điều này gợi ý rằng **chưng cất NeRF MLP là 1 nhiệm vụ dễ hơn so với tổng hợp góc nhìn***.

> **🔁 ĐỐI CHIẾU NeRF GỐC — mạng "dò đường"**
>
> | | **NeRF gốc (mạng coarse)** | **Mip-NeRF 360 (proposal MLP)** |
> |---|---|---|
> | Số mạng | 2 mạng **riêng biệt, cùng kích thước** (coarse 8×256, fine 8×256) | 2 mạng **khác hẳn kích thước** (prop 4×256, NeRF 8×1024) |
> | Mạng dò đường dự đoán gì | **density VÀ màu** (đầy đủ như mạng fine) | **CHỈ density — không có nhánh màu** |
> | Giám sát mạng dò đường bằng gì | **`‖Ĉ_c(r) − C(r)‖²`** — so màu render thô với **ảnh thật** | **`L_prop`** — so histogram của nó với **histogram của NeRF MLP**. Hoàn toàn **không thấy ảnh thật** |
> | Số lượt lấy mẫu lại | 1 lượt (coarse 64 → fine thêm 128) | **2 lượt** (64 → 64 → 32) |
> | Mẫu cho mạng render cuối | **192** (= 64 + 128) điểm | **32** khoảng |
> | Chi phí | Mạng dò đường tốn gần bằng mạng chính | Mạng dò đường rẻ hơn nhiều lần ⇒ gọi nhiều lần vẫn rẻ |
> | **Vì sao đổi** | Màu do mạng coarse render ra **bị bỏ đi hoàn toàn** ⇒ tính nó là lãng phí; và việc ép nó khớp ảnh thật là **ép nó học 1 nhiệm vụ khó hơn mức cần thiết** | Mạng dò đường chỉ cần biết **"cảnh nằm ở đâu dọc tia"**, không cần biết **"cảnh màu gì"** ⇒ bỏ hẳn nhánh màu và đổi tín hiệu giám sát |
> | **Bằng chứng số [P360, Ablation E]** | — | Bỏ proposal MLP và train theo cách của Mip-NeRF (áp `L_recon` ở mọi tỉ lệ coarse): PSNR **24.37 → 23.45**, SSIM **0.687 → 0.659**, thời gian **7.09h → 18.89h**. Tức **vừa kém hơn vừa chậm hơn 2.7×** |
> | **Bằng chứng số [P360, Ablation D]** | — | Bỏ proposal MLP, dùng **1 MLP duy nhất** mô hình cả cảnh lẫn trọng số đề xuất: chất lượng **không giảm** (PSNR 24.26, SSIM 0.682) nhưng thời gian train tăng **~3×** (**18.89h**). ⇒ Đây là lý do trực tiếp cho việc dùng 1 proposal MLP **nhỏ**: nó **không mua thêm chất lượng, nó mua tốc độ** |

### 4.3. "Online Distillation" là gì

**[P360, Introduction]** định nghĩa trực tiếp: *"**distillation**" (chưng cất) thông thường chỉ việc train 1 mạng nhỏ để khớp với output của 1 mạng lớn **đã được train xong** (Hinton et al.); còn ở đây, họ chưng cất **cấu trúc của các output do NeRF MLP dự đoán** vào proposal MLP một cách **"trực tuyến" (online)**, bằng cách **train cả 2 mạng đồng thời**.*

| Thuật ngữ | Ý nghĩa |
|---|---|
| **Knowledge distillation** | Kỹ thuật kinh điển: mạng "teacher" lớn đã train xong → dùng output của nó làm nhãn mềm để train mạng "student" nhỏ |
| **Online distillation** (ở đây) | Teacher (NeRF MLP) và student (proposal MLP) **cùng được khởi tạo ngẫu nhiên và train đồng thời** — teacher chưa hề "biết gì" lúc bắt đầu |
| **Stop-gradient** | Toán tử chặn gradient: cho phép giá trị đi qua ở lượt forward, nhưng **không cho gradient chảy ngược qua** |

**Cơ chế then chốt — stop-gradient và quan hệ "dẫn/theo" [P360, Mục 3]:** họ đặt 1 **stop-gradient trên các output `t` và `w` của NeRF MLP** khi tính `L_prop`, để **NeRF MLP "dẫn đầu" và proposal MLP "theo sau"**. Paper nêu rõ hậu quả nếu không làm vậy: *nếu không, NeRF có thể bị khuyến khích tạo ra 1 bản tái tạo cảnh **tệ hơn** chỉ để làm công việc của proposal MLP **dễ hơn**.*

**[SUY-RA] Diễn giải:** `L_prop` là 1 hàm của **cả 2** bên. Nếu để gradient chảy về cả 2, tối ưu hóa có 2 cách giảm `L_prop`: (a) proposal MLP học khớp NeRF MLP — đúng ý đồ; hoặc (b) NeRF MLP **tự làm phân phối của nó thô/nhòe đi** để dễ bị bao bọc — sai ý đồ, và trực tiếp phá hỏng chất lượng ảnh. Stop-gradient chặn đứng đường (b).

**Hệ quả kỹ thuật tiện lợi [P360, Mục 5]:** vì có stop-gradient, việc tối ưu `Θ_prop` **độc lập** với việc tối ưu `Θ_NeRF`, nên **không cần siêu tham số nào để cân tỉ lệ ảnh hưởng của `L_prop`** (hệ số của nó mặc nhiên là 1). So sánh: Mip-NeRF phải chọn hệ số `1/10` cho nhánh coarse ở Eq. 7 — 1 siêu tham số mà Mip-NeRF 360 **loại bỏ được**.

**Các công trình liên quan mà paper tự đặt mình bên cạnh [P360, Introduction]** — hữu ích cho Chương 2 (Các công trình liên quan) của đồ án:

| Công trình | Làm gì | Khác biệt so với Mip-NeRF 360 |
|---|---|---|
| **NeRV** | Online distillation cho **nhiệm vụ hoàn toàn khác**: xấp xỉ tích phân render để mô hình hóa visibility và chiếu sáng gián tiếp | Cùng tinh thần, khác mục đích |
| **DONeRF** — "sampling oracle networks" | Mạng dự đoán nơi lấy mẫu | **DONeRF dùng độ sâu ground-truth để giám sát**; Mip-NeRF 360 **không cần** |
| **TerminNeRF** | Ý tưởng liên quan | Chỉ **tăng tốc inference**, và thực tế **làm chậm train** (phải train 1 NeRF tới hội tụ trước, rồi train thêm mô hình phụ) |
| **NeRF in Detail** | Mạng "proposer" học được | Chỉ đạt **tăng tốc 25%**, trong khi Mip-NeRF 360 **tăng tốc train 300%** |
| **PlenOctrees / "baking" NeRF** | Nén NeRF đã train vào định dạng render nhanh | **Không tăng tốc train** |
| **Neural Sparse Voxel Fields** | Dựng cấu trúc octree trong khi tối ưu | **Không giảm đáng kể thời gian train** |

### 4.4. Hàm loss chưng cất `L_prop` — Eq. 12 & Eq. 13

Đây là công thức khó nhất của paper về mặt ý tưởng. Paper dành gần 1 trang để lập luận **vì sao không dùng được 1 độ đo histogram thông thường**.

#### Vấn đề: 2 histogram có **các bin KHÔNG trùng nhau**

**[P360, Mục 3]**: thoạt nhìn bài toán có vẻ tầm thường, vì "tối thiểu hóa độ khác biệt giữa 2 histogram" là 1 nhiệm vụ đã được giải quyết tốt trong thống kê. **Nhưng** — các **"bin"** của 2 histogram, tức `t` và `t̂`, **không nhất thiết giống nhau**. Thực tế còn tệ hơn: *nếu proposal MLP **thành công** trong việc loại bỏ các vùng khoảng cách không có cảnh, thì `t̂` và `t` sẽ **rất khác nhau***. Trong khi đó, tài liệu thống kê có nhiều cách đo khác biệt giữa 2 histogram **có cùng bin**, còn trường hợp này thì **tương đối ít được khai phá**.

Lý do sâu xa paper nêu: *ta **không thể giả định bất cứ điều gì** về cách khối lượng được phân bố **bên trong** 1 bin*. Một bin có trọng số khác 0 có thể ứng với: 1 phân phối **đều** trên toàn bin, 1 **hàm delta** (toàn bộ khối lượng dồn vào 1 điểm) nằm ở **bất kỳ đâu** trong bin, hoặc **vô số** phân phối khác.

#### Nguyên lý thiết kế mà paper đặt ra

**[P360, Mục 3]** — tiêu chí thiết kế, phát biểu lại bằng lời riêng:

> **Nếu TỒN TẠI dù chỉ 1 phân phối khối lượng duy nhất nào có thể giải thích được CẢ HAI histogram, thì loss PHẢI bằng 0. Loss chỉ được khác 0 khi điều đó là BẤT KHẢ THI — tức khi 2 histogram không thể nào là 2 ảnh phản chiếu của cùng 1 phân phối khối lượng liên tục "thật" nào.**

Đây là 1 tiêu chí rất chặt, và nó dẫn tới việc dùng **bất đẳng thức chặn trên** thay vì 1 độ đo khoảng cách đối xứng.

#### Hàm `bound` — Eq. 12

```
bound( t̂, ŵ, T )  =  Σ_{ j : T ∩ T̂_j ≠ ∅ }  ŵ_j                              (Eq. 12)
```

#### Chú thích ký hiệu Eq. 12

| Ký hiệu | Ý nghĩa |
|---|---|
| `T` | 1 khoảng **bất kỳ** trên tia (trong thực tế: 1 khoảng `T_i` của NeRF MLP) |
| `T̂_j` | khoảng thứ j của histogram **đề xuất** |
| `T ∩ T̂_j ≠ ∅` | "khoảng `T` và khoảng `T̂_j` **có giao nhau** (chồng lấp, dù chỉ 1 phần)" |
| `Σ_{j: ...} ŵ_j` | **cộng dồn trọng số đề xuất của MỌI khoảng đề xuất có chồng lấp với `T`** |
| `bound(t̂, ŵ, T)` | kết quả: **tổng khối lượng đề xuất có thể "chạm tới" khoảng `T`** |

**Đọc công thức:** `bound` trả lời câu hỏi: *"theo histogram đề xuất, **nhiều nhất** có thể có bao nhiêu khối lượng nằm trong khoảng `T`?"* Vì ta không biết khối lượng phân bố thế nào trong mỗi bin đề xuất, trường hợp xấu nhất là **toàn bộ** khối lượng của mọi bin chồng lấp đều dồn vào đúng phần giao với `T`. Đó chính là tổng ở Eq. 12.

**Điều kiện nhất quán mà paper suy ra:** nếu 2 histogram nhất quán với nhau, thì **bắt buộc** phải có

```
w_i  ≤  bound( t̂, ŵ, T_i )        với MỌI khoảng (T_i, w_i) trong (t, w)
```

**[P360, Mục 3]** ghi nhận tính chất này *tương tự với tính chất cộng tính (additivity) của 1 **độ đo ngoài (outer measure)** trong lý thuyết độ đo*.

| Thuật ngữ | Ý nghĩa |
|---|---|
| **Outer measure** (độ đo ngoài) | Khái niệm trong lý thuyết độ đo: cách gán "kích thước" cho **mọi** tập hợp bằng cách phủ nó bởi các tập dễ đo và lấy **cận dưới đúng (infimum)** của tổng kích thước các tập phủ. Tính chất cốt lõi: độ đo của 1 tập **không vượt quá** tổng độ đo của các tập phủ nó |
| Liên hệ với Eq. 12 | Các bin đề xuất chồng lấp với `T_i` chính là 1 **phép phủ** của `T_i`; nên khối lượng thật trong `T_i` (tức `w_i`) không được vượt tổng khối lượng của các tập phủ đó |

#### Hàm loss `L_prop` — Eq. 13

```
L_prop( t, w, t̂, ŵ )  =  Σ_i  (1 / w_i) · max( 0 , w_i − bound(t̂, ŵ, T_i) )²       (Eq. 13)
```

#### Chú thích ký hiệu Eq. 13

| Thành phần | Ý nghĩa và vai trò |
|---|---|
| `w_i − bound(t̂, ŵ, T_i)` | **lượng khối lượng histogram "vượt mức"** — phần mà NeRF MLP khẳng định có, nhưng histogram đề xuất **không đủ sức bao** |
| `max(0, ·)` | **chỉ phạt khi vi phạm**. Nếu `bound ≥ w_i` (đề xuất bao đủ) thì số hạng này **bằng 0** — loss bằng 0. Đây là cơ chế hiện thực hóa tiêu chí thiết kế ở trên |
| `(·)²` | bình phương — phạt nặng các vi phạm lớn |
| `1 / w_i` | **chia cho `w_i`** — chi tiết tinh tế, lý do xem bên dưới |
| `Σ_i` | tổng trên **mọi khoảng** của histogram NeRF MLP |

**Ba tính chất mà paper giải thích tường minh [P360, Mục 3]:**

**(1) Loss này giống "phiên bản half-quadratic của khoảng cách histogram chi-squared"** — một độ đo thường dùng trong thống kê và thị giác máy tính.

| Thuật ngữ | Ý nghĩa |
|---|---|
| **Chi-squared histogram distance** | Độ đo khác biệt giữa 2 histogram, dạng `Σ (a_i − b_i)²/(a_i + b_i)` hoặc `Σ (a_i − b_i)²/a_i` — đặc điểm là **chia cho khối lượng**, nên 1 chênh lệch tuyệt đối nhỏ ở bin nhẹ bị coi là nghiêm trọng hơn cùng chênh lệch ở bin nặng |
| **Half-quadratic** | "nửa bậc hai": chỉ bậc hai ở **một phía** (ở đây: phía vi phạm), phía còn lại **phẳng bằng 0** — do có `max(0, ·)` |

**(2) Loss này KHÔNG đối xứng, và đó là CHỦ Ý.** Paper nêu rõ: họ **chỉ muốn phạt** proposal weights khi chúng **ước lượng THIẾU (underestimate)** phân phối mà NeRF MLP hàm ý. **Ước lượng VƯỢT (overestimate) là điều NÊN mong đợi** — vì proposal weights thường **thô hơn** NeRF weights, nên chúng **sẽ tạo thành 1 "đường bao trên" (upper envelope)** quanh NeRF weights.

**[SUY-RA] Vì sao bất đối xứng mới đúng:** proposal MLP chỉ có 4 lớp × 256 kênh và được lấy mẫu thưa hơn — nó **về mặt dung lượng không thể** sắc nét bằng NeRF MLP. Nếu ép nó khớp **chính xác**, ta ép nó làm điều bất khả thi, và tối ưu hóa sẽ hỏng. Nhưng nếu nó **bao trọn** phân phối thật (dù rộng hơn), thì mục đích của nó — *"đừng bỏ sót vùng nào có cảnh"* — **đã hoàn thành**, vì phần dư thừa chỉ làm phí vài mẫu, không làm mất cảnh. Nói cách khác: **bỏ sót là lỗi chết người, bao rộng chỉ là lỗi tốn kém.**

**(3) Vì sao chia cho `w_i`.** Paper giải thích: phép chia cho `w_i` **đảm bảo rằng gradient của loss này theo `bound` là 1 **hằng số** khi `bound` bằng 0**, điều này dẫn tới **tối ưu hóa hành xử ổn định (well-behaved)**.

**[SUY-RA] Kiểm chứng:** khi `bound = 0`, số hạng là `w_i²/w_i = w_i`. Đạo hàm theo `bound` tại đó: `∂/∂bound [ (w_i − bound)²/w_i ] = −2(w_i − bound)/w_i`, tại `bound = 0` cho **−2** — đúng là 1 **hằng số**, không phụ thuộc `w_i`. Nếu **không** chia cho `w_i`, gradient sẽ là `−2 w_i`, nên các khoảng có `w_i` nhỏ gần như **không sinh gradient** và proposal MLP sẽ "phớt lờ" chúng — chính là các vùng cảnh mờ/nhạt mà ta không muốn bỏ sót.

**Tối ưu hóa tính toán [P360, Mục 3]:** vì `t` và `t̂` **đã được sắp xếp**, Eq. 13 tính được hiệu quả bằng **summed-area tables** (bảng tổng tích lũy, Crow 1984) — tức tính tổng tích lũy 1 lần rồi mọi truy vấn "tổng trong 1 khoảng" chỉ là 1 phép trừ, thay vì cộng lại từ đầu mỗi lần.

**Tính bất biến quan trọng [P360, Mục 3]:** loss này **bất biến với mọi phép biến đổi đơn điệu của khoảng cách `t`** (với giả định `w` và `ŵ` đã được tính trong t-space). Nghĩa là nó hành xử **y hệt** dù áp trên khoảng cách Euclid `t` hay trên khoảng cách chuẩn hóa `s`. *(Đây là lý do Eq. 13 viết theo `t` nhưng Eq. 16 viết theo `s` mà không có mâu thuẫn.)*

**Áp vào đâu [P360, Mục 3]:** loss được áp giữa **histogram của NeRF `(t, w)`** và **TẤT CẢ các histogram đề xuất `(t̂_k, ŵ_k)`** — tức cả 2 lượt, không chỉ lượt cuối.

#### [SUY-RA] Ví dụ số minh họa `L_prop`

Lấy histogram NeRF: mốc `t = [0, 1, 2]`, trọng số `w = [0.3, 0.6]`, tức `T_1 = [0,1)` với `w_1 = 0.3`, và `T_2 = [1,2)` với `w_2 = 0.6`.

**Trường hợp A — đề xuất bao đủ.** `t̂ = [0, 0.5, 1.5, 2]`, `ŵ = [0.1, 0.5, 0.2]`:

| Khoảng NeRF | Các bin đề xuất chồng lấp | `bound` | `w_i` | Vi phạm? |
|---|---|---|---|---|
| `T_1 = [0,1)` | `[0,0.5)` ✓, `[0.5,1.5)` ✓, `[1.5,2)` ✗ | 0.1 + 0.5 = **0.6** | 0.3 | 0.3 ≤ 0.6 → **không** |
| `T_2 = [1,2)` | `[0,0.5)` ✗, `[0.5,1.5)` ✓, `[1.5,2)` ✓ | 0.5 + 0.2 = **0.7** | 0.6 | 0.6 ≤ 0.7 → **không** |

⇒ `L_prop = 0`. **Đáng chú ý:** các bin **hoàn toàn khác nhau** (3 bin vs 2 bin, các mốc lệch nhau) mà loss vẫn bằng 0 — đúng đúng tiêu chí thiết kế của paper.

**Trường hợp B — đề xuất bỏ sót.** `t̂ = [0, 0.5, 1.5, 2]`, `ŵ = [0.1, 0.2, 0.2]`:

| Khoảng NeRF | `bound` | `w_i` | Số hạng loss |
|---|---|---|---|
| `T_1` | 0.1 + 0.2 = **0.3** | 0.3 | `max(0, 0.3−0.3)² / 0.3 = 0` |
| `T_2` | 0.2 + 0.2 = **0.4** | 0.6 | `max(0, 0.6−0.4)² / 0.6 = 0.04/0.6 ≈ **0.0667**` |

⇒ `L_prop ≈ 0.0667` — gradient sẽ đẩy proposal MLP tăng khối lượng ở vùng quanh `T_2`.

#### Diễn tiến thực tế trong lúc train

**[P360, Figure 4]** minh họa trên 1 tia của scene `bicycle`:
- **(a) 0% quá trình train:** mọi trọng số **phân bố đều** theo khoảng cách tia — cả NeRF MLP và cả 2 proposal.
- **(b) 4% quá trình train:** NeRF weights **bắt đầu dồn lại quanh 1 bề mặt**.
- **(c) 100%:** NeRF MLP đã **định vị gọn** trọng số quanh bề mặt, còn proposal MLP **"đuổi kịp"** và dự đoán các histogram thô **bao bọc (envelope)** quanh NeRF weights.

Đây là minh chứng trực quan cho quan hệ "dẫn/theo" do stop-gradient tạo ra ở mục 4.3.

### 4.5. Distortion Loss `L_dist` — Eq. 14 & Eq. 15: chống **floaters** và **background collapse**

Đây là nội dung **Mục 4 của paper**, trả lời Vấn đề 3 (Ambiguity).

#### Hai loại artifact mà paper đặt tên và nhắm tới

**[P360, Mục 4]** — paper gọi tên 2 artifact đặc trưng của NeRF đã train:

| Artifact | Định nghĩa theo paper (diễn giải lại) |
|---|---|
| **Floaters** | Các **vùng nhỏ, rời rạc, không liên thông** của không gian có density cao, tồn tại để "giải thích cho xong" 1 phần nào đó của **1 tập con các góc nhìn input**; nhưng khi xem từ 1 góc khác, chúng trông như **những đám mây mờ** lơ lửng |
| **Background collapse** | Hiện tượng các **bề mặt ở xa bị mô hình hóa SAI thành những đám mây nội dung dày đặc, bán trong suốt, nằm GẦN camera** |

**Vì sao cảnh unbounded làm 2 artifact này nặng hơn [P360, Introduction]:** bản thân bài toán dựng NeRF đã **under-constrained** về cơ bản — **1 họa vô hạn các NeRF có thể "giải thích hết" các ảnh input**, nhưng chỉ 1 tập con nhỏ cho kết quả chấp nhận được ở góc nhìn mới. Paper nêu 1 ví dụ cực đoan rất rõ: *1 NeRF có thể tái tạo **tất cả** ảnh input bằng cách đơn giản dựng mỗi ảnh thành **1 mặt phẳng có texture đặt ngay trước camera tương ứng của nó***. Với cảnh unbounded, nội dung ở xa **chỉ được quan sát bởi rất ít tia**, nên tình trạng này trầm trọng hơn nhiều.

**Cách NeRF gốc chống vấn đề này — và vì sao không đủ [P360, Mục 4 + Introduction]:** NeRF gốc chính quy hóa các cảnh nhập nhằng bằng cách **tiêm nhiễu Gaussian vào nhánh density của MLP trước bộ chỉnh lưu (rectifier)**, nhằm khuyến khích density **hướng về 0 hoặc về vô cùng** (tức dứt khoát rỗng hoặc dứt khoát đặc). Paper thừa nhận cách này **giảm được 1 phần floaters** bằng việc làm density bán trong suốt bị bất lợi, nhưng khẳng định nó **không đủ** cho nhiệm vụ khó hơn của họ.

**Paper cũng tự phân biệt với các regularizer NeRF khác đã công bố [P360, Introduction]:** loss robust trên density, hay các hình phạt độ trơn (smoothness) trên bề mặt — nhưng chúng *giải quyết các vấn đề khác* (render chậm, bề mặt không trơn). Và quan trọng: *các regularizer đó được thiết kế cho **các mẫu điểm (point samples)** mà NeRF dùng, trong khi cách tiếp cận của paper được thiết kế để làm việc với **các trọng số liên tục được định nghĩa dọc theo mỗi tia mip-NeRF***. Đây chính là lý do tiêu đề Mục 4 là "Regularization **for Interval-Based Models**".

#### Công thức gốc — Eq. 14

```
                       ∞  ∞
L_dist( s, w )  =  ∫  ∫   w_s(u) · w_s(v) · |u − v|  du dv                      (Eq. 14)
                     −∞ −∞
```

với `w_s(u)` là phép **nội suy vào hàm bậc thang** định nghĩa bởi `(s, w)` tại `u`:

```
w_s(u)  =  Σ_i  w_i · 1_[s_i, s_{i+1})(u)
```

#### Chú thích ký hiệu Eq. 14

| Ký hiệu | Ý nghĩa |
|---|---|
| `s` | vector mốc khoảng cách **đã chuẩn hóa** (s-space, Eq. 11) |
| `w` | vector trọng số alpha-compositing do **NeRF MLP** sinh ra (Eq. 4) |
| `w_s(u)` | **hàm bậc thang (step function)** trên trục `s`: bằng `w_i` khi `u` nằm trong khoảng `[s_i, s_{i+1})`, bằng 0 nếu ngoài mọi khoảng |
| `1_[a,b)(u)` | **hàm chỉ thị (indicator function)**: bằng 1 nếu `a ≤ u < b`, bằng 0 nếu không |
| `u`, `v` | 2 biến tích phân — **2 vị trí bất kỳ** dọc tia |
| `|u − v|` | **khoảng cách** giữa 2 vị trí đó |
| `∫∫ ... du dv` | tích phân kép trên **mọi cặp vị trí** dọc tia |

**Đọc công thức:** đây là **tích phân của khoảng cách giữa MỌI CẶP ĐIỂM dọc hàm bậc thang 1 chiều này, có trọng số bằng `w` mà NeRF MLP gán cho mỗi điểm** **[P360, Mục 4]**. Nói ngắn: *"trung bình có trọng số của khoảng cách giữa mọi cặp vị trí có ánh sáng"*.

**Tên gọi và họ hàng toán học [P360, Mục 4]:** paper gọi đại lượng này là **"distortion" (biến dạng)** vì nó *giống 1 phiên bản liên tục của đại lượng distortion mà **k-means** tối thiểu hóa* (k-means tối thiểu hóa tổng bình phương khoảng cách từ các điểm tới tâm cụm — tức cũng là 1 độ đo "các điểm có gom cụm chặt không"). Paper cũng nói nó *có thể được nghĩ như việc **cực đại hóa 1 dạng tự tương quan (autocorrelation)***.

**Vì sao dùng `s` chứ không dùng `t` — lý do paper nêu rõ [P360, Mục 4]:** *dùng khoảng cách chuẩn hóa `s` vì dùng `t` sẽ **nâng trọng số (up-weight) các khoảng ở xa lên rất nhiều** và khiến các khoảng ở gần **bị bỏ qua một cách hữu hiệu (effectively ignored)**.*

**[SUY-RA] Diễn giải:** trong t-space, các khoảng ở xa có bề rộng rất lớn (mục 2.7: từ `s=0.99` tới `s=1` ứng với `t` từ 100 tới ∞). Vì `L_dist` có hệ số `|u − v|` là khoảng cách tuyệt đối, các khoảng xa sẽ chi phối toàn bộ giá trị loss, và regularizer sẽ chỉ "quan tâm" tới hậu cảnh, bỏ mặc tiền cảnh. Chuẩn hóa về `s ∈ [0,1]` cân bằng lại: mỗi vùng được "tiếng nói" tỉ lệ với độ quan trọng thị giác của nó. **Đây là 1 điểm nữa cho thấy `s`-space không chỉ phục vụ việc lấy mẫu, mà còn là hệ quy chiếu đúng để định nghĩa regularizer.**

#### Dạng tính được — Eq. 15

Eq. 14 dễ **định nghĩa** nhưng **không tầm thường để tính**. Tuy nhiên, vì `w_s(·)` **nhận giá trị hằng số bên trong mỗi khoảng**, tích phân kép rút gọn thành tổng hữu hạn **[P360, Eq. 15]**:

```
                      ⎪    s_i + s_{i+1}     s_j + s_{j+1} ⎪     1
L_dist( s, w )  =  Σ  ⎪w_i w_j ─────────── − ───────────── ⎪  +  ─ Σ w_i² (s_{i+1} − s_i)
                   i,j⎪          2                 2        ⎪     3 i
```

Viết lại cho rõ cấu trúc:

```
L_dist(s,w) = Σ_{i,j} w_i · w_j · | m_i − m_j |   +   (1/3) · Σ_i w_i² · (s_{i+1} − s_i)
                └──────── số hạng 1 ────────┘       └──────── số hạng 2 ────────┘
      với  m_i = (s_i + s_{i+1}) / 2   là ĐIỂM GIỮA của khoảng thứ i
```

#### Chú thích ký hiệu Eq. 15

| Thành phần | Ý nghĩa |
|---|---|
| `m_i = (s_i + s_{i+1})/2` | **điểm giữa (midpoint)** của khoảng thứ i trong s-space |
| **Số hạng 1** | **tối thiểu hóa các khoảng cách có trọng số giữa MỌI CẶP điểm giữa các khoảng** — paper nói đúng vậy. Nó phạt việc trọng số bị **rải ra xa nhau** |
| **Số hạng 2** | **tối thiểu hóa kích thước có trọng số của TỪNG khoảng riêng lẻ** — paper nói đúng vậy. Nó phạt việc 1 khoảng **quá rộng** mà vẫn mang nhiều trọng số |
| Hệ số `1/3` | hằng số sinh ra từ việc tích phân `|u−v|` trên 1 ô vuông `[s_i,s_{i+1})²` — *(ghi chú: paper không chứng minh, người biên soạn chưa tự kiểm tra lại từng bước giải tích, nên **trích nguyên hệ số 1/3 theo paper** mà không diễn giải thêm)* |
| `Σ_{i,j}` | tổng trên **mọi cặp** (i, j), bao gồm cả `i = j` (cặp này cho số hạng 1 bằng 0 vì `m_i − m_i = 0`) và tính **cả 2 thứ tự** (i,j) và (j,i) |

**[P360, Mục 4]** kết luận: *ở dạng này, distortion loss trở nên **tầm thường để tính***.

#### Bốn hành vi mà `L_dist` cưỡng chế

**[P360, Figure 6]** liệt kê tường minh 4 hiệu ứng, qua việc vẽ `∇L_dist` (gradient của regularizer) theo `s` và `w` trên 1 hàm bậc thang mẫu. Loss này khuyến khích mỗi tia **gọn gàng (compact) hết mức có thể** bằng cách:

| # | Hành vi | Thành phần nào của Eq. 15 gây ra |
|---|---|---|
| 1 | **Tối thiểu hóa bề rộng của từng khoảng** | Số hạng 2 |
| 2 | **Kéo các khoảng ở xa về phía nhau** | Số hạng 1 |
| 3 | **Dồn trọng số vào 1 khoảng duy nhất, hoặc 1 số ít khoảng gần nhau** | Số hạng 1 |
| 4 | **Đẩy mọi trọng số về 0 khi có thể** (ví dụ khi toàn bộ tia là không gian trống) | Cả 2 — vì cả 2 đều là hàm tăng theo `w` |

**Điểm cực tiểu của loss [P360, Mục 4]:** loss được tối thiểu hóa bằng cách đặt **`w = 0`** — và paper nhắc lại lý do điều này hợp lệ: **`w` có tổng không vượt quá 1, chứ không bắt buộc bằng đúng 1** (tính chất đã nêu ở Giai đoạn 3 mục 3.3). *Nếu điều đó không thể (tức nếu tia **không rỗng**), thì loss được tối thiểu hóa bằng cách **dồn trọng số vào 1 vùng nhỏ nhất có thể**.*

> **⚠️ Lưu ý tránh hiểu sai:** nghe "loss cực tiểu tại `w = 0`" dễ tưởng regularizer này sẽ xóa sạch cảnh. Không — vì nó chỉ là **1 trong 3 số hạng** của hàm loss tổng (Eq. 16), và số hạng `L_recon` sẽ phản đối dữ dội nếu `w = 0` ở nơi có cảnh thật. `L_dist` chỉ **thắng ở những nơi mà `L_recon` không quan tâm** — tức chính xác là các vùng không gian ít được quan sát, nơi floaters sinh ra. Đây là cơ chế chống floaters.

#### [SUY-RA] Ví dụ số: `L_dist` phân biệt "gọn" với "rải" như thế nào

Chia s-space `[0,1]` thành 10 khoảng bề rộng 0.1 (nên `m_i` = 0.05, 0.15, ..., 0.95).

| Trường hợp | Phân bố `w` | Số hạng 1 | Số hạng 2 | **`L_dist`** |
|---|---|---|---|---|
| **A — tia rỗng** | mọi `w_i = 0` | 0 | 0 | **0.000** (cực tiểu tuyệt đối) |
| **B — gọn (1 bề mặt)** | `w = 1.0` ở khoảng giữa (m=0.45), còn lại 0 | 0 (chỉ 1 khoảng ⇒ không có cặp khác nhau) | `(1/3)·1²·0.1 = 0.0333` | **0.033** |
| **C — rải (2 cụm xa nhau — giống floater)** | `w = 0.5` ở `m=0.05` và `w = 0.5` ở `m=0.95` | `2 × 0.5 × 0.5 × |0.95−0.05| = 0.450` | `(1/3)(0.25·0.1 + 0.25·0.1) = 0.0167` | **0.467** |

**Kết quả: trường hợp C bị phạt gấp ~14× so với B**, dù **tổng khối lượng `Σw` của B và C bằng nhau (= 1)**. Đây chính xác là hành vi mong muốn: 2 cấu hình **render ra màu pixel có thể rất giống nhau** (nên `L_recon` không phân biệt được), nhưng `L_dist` **phân biệt rất rõ** và ưu tiên cấu hình đúng vật lý — một bề mặt mỏng thay vì 2 đám mây lơ lửng.

> **🔁 ĐỐI CHIẾU NeRF GỐC — chống artifact**
>
> | | **NeRF gốc** | **Mip-NeRF 360** |
> |---|---|---|
> | Cơ chế | **Tiêm nhiễu Gaussian** vào density trước rectifier | **`L_dist`** — regularizer tường minh trên phân phối trọng số dọc tia |
> | Tác động lên gì | Lên **từng giá trị density riêng lẻ** (ép về 0 hoặc ∞) | Lên **hình dạng toàn cục của phân phối dọc cả tia** (ép gọn lại) |
> | Thiết kế cho | **Mẫu điểm (point samples)** | **Khoảng/trọng số liên tục của tia mip-NeRF** |
> | Có cần siêu tham số | σ của nhiễu | `λ = 0.01` (Eq. 16) |
> | **Bằng chứng số [P360, Ablation C]** | Áp cách tiêm nhiễu (σ = 1) của NeRF gốc vào mô hình 360: PSNR **24.00**, SSIM **0.655**, LPIPS **0.328** — **tệ hơn** cả việc không có regularizer nào | Mô hình đầy đủ: PSNR **24.37**, SSIM **0.687**, LPIPS **0.300** |
> | Kết luận của paper | Cách tiêm nhiễu **làm giảm chất lượng tái tạo** (thấy rõ ở độ sâu của những tán cây xa trong **[P360, Figure 5]**) và **chỉ loại bỏ được một phần** artifact | `L_dist` chặn **cả floaters lẫn background collapse** hiệu quả hơn |

> **⚠️ MỘT PHÁT HIỆN QUAN TRỌNG, DỄ BỊ BÁO CÁO SAI [P360, Ablation B]:**
> **Bỏ `L_dist` KHÔNG làm các chỉ số định lượng xấu đi** — thậm chí PSNR còn **cao hơn một chút**: **24.41** (không có `L_dist`) so với **24.37** (mô hình đầy đủ); SSIM **0.687** ở cả hai; LPIPS **0.300** ở cả hai. Paper nói thẳng: *bỏ `L_dist` **không ảnh hưởng đáng kể** tới các chỉ số của chúng tôi, **nhưng** dẫn tới các artifact "floater" trong hình học của cảnh*, như **Figure 5** cho thấy.
>
> **Ý nghĩa cho đồ án:** đây là 1 ví dụ điển hình về việc **PSNR/SSIM/LPIPS không đo được chất lượng hình học 3D**. Floaters chỉ hiện ra rõ ở **depth map** và khi **xem video chuyển động camera liên tục**, chứ không hiện ra trên các ảnh test tĩnh. **Không nên viết trong báo cáo rằng "`L_dist` cải thiện PSNR"** — nó không cải thiện. Giá trị của nó là **chất lượng hình học và tính ổn định thời gian (temporal stability)**, và đây đúng là lý do paper liên tục khuyến nghị người đọc xem video bổ sung.

### 4.6. Hàm loss tổng và toàn bộ siêu tham số — Mục 5 của paper

#### Hàm loss tổng — Eq. 16

```
                                          1
L_recon( C(t), C* )  +  λ · L_dist(s, w)  +  Σ  L_prop( s, w, ŝ_k, ŵ_k )          (Eq. 16)
                                         k=0
```

**[P360, Mục 5]** ghi rõ: loss này được **lấy trung bình trên mọi tia trong mỗi batch** (các tia không được viết ra trong ký hiệu).

#### Chú thích ký hiệu Eq. 16

| Ký hiệu | Ý nghĩa |
|---|---|
| `L_recon(C(t), C*)` | **loss tái tạo ảnh** — so màu render với màu thật. Chỉ áp cho **NeRF MLP**, **chỉ 1 lần** (không áp ở các lượt coarse) |
| `λ` (lambda) | **hệ số cân bằng** giữa số hạng dữ liệu `L_recon` và regularizer `L_dist`. **`λ = 0.01` trong MỌI thí nghiệm** |
| `Σ_{k=0}^{1} L_prop(...)` | tổng loss chưng cất trên **cả 2 lượt proposal** (k = 0 và k = 1) |
| `ŝ_k, ŵ_k` | histogram đề xuất của lượt k |
| (không có hệ số cho `L_prop`) | Nhờ stop-gradient, **không cần** siêu tham số cân `L_prop` (mục 4.3) |

**Hàm `L_recon` cụ thể — thay đổi so với Mip-NeRF [P360, Mục 5]:** dùng **Charbonnier loss**:

```
L_recon(x, x*)  =  √( (x − x*)²  +  ε² )        với  ε = 0.001
```

| Thuật ngữ | Ý nghĩa |
|---|---|
| **Charbonnier loss** (còn gọi pseudo-Huber) | Hàm mất mát **robust**: với sai số nhỏ nó hành xử như **bình phương** (mượt, gradient tỉ lệ sai số); với sai số lớn nó hành xử như **tuyến tính** (gradient bị chặn) ⇒ **outlier không chi phối** quá trình train |
| `ε = 0.001` | Hằng số nhỏ quyết định ngưỡng chuyển giữa 2 chế độ, và đảm bảo hàm **khả vi tại 0** (MAE thuần thì không) |
| So với MSE của Mip-NeRF | Paper nêu lý do dùng Charbonnier: nó *đạt được quá trình tối ưu hóa **ổn định hơn một chút** so với mean squared error mà mip-NeRF dùng* |

> **🔁 ĐỐI CHIẾU NeRF GỐC — hàm loss tổng**
>
> | | **NeRF gốc** | **Mip-NeRF** | **Mip-NeRF 360** |
> |---|---|---|---|
> | Công thức | `Σ_r [ ‖Ĉ_c(r)−C(r)‖² + ‖Ĉ_f(r)−C(r)‖² ]` | `Σ_r [ (1/10)L_recon(C(r,t_c),C*) + L_recon(C(r,t_f),C*) ]` (Eq. 7) | `L_recon + λL_dist + Σ_k L_prop` (Eq. 16) |
> | Số lần áp loss ảnh | **2 lần** (coarse + fine), trọng số bằng nhau | **2 lần**, trọng số 1/10 và 1 | **1 lần duy nhất** — chỉ cho NeRF MLP |
> | Dạng loss ảnh | **MSE** | **MSE** | **Charbonnier** (robust, ε=0.001) |
> | Có regularizer | ❌ (chỉ có tiêm nhiễu density) | ❌ | ✅ **`L_dist`**, λ=0.01 |
> | Có loss giám sát mạng dò đường | ❌ (mạng coarse học từ ảnh thật) | ❌ | ✅ **`L_prop`** × 2 lượt |
> | Số siêu tham số cân loss | 0 (2 nhánh bằng nhau) | 1 (hệ số 1/10) | **1** (`λ`) — ít hơn mong đợi nhờ stop-gradient |

#### Bảng siêu tham số đầy đủ — trích nguyên từ [P360, Mục 5]

| Siêu tham số | Giá trị | Ghi chú / đối chiếu NeRF gốc |
|---|---|---|
| **Proposal MLP** | **4 lớp, 256 kênh ẩn** | NeRF gốc: mạng coarse 8 lớp × 256 |
| **NeRF MLP** | **8 lớp, 1024 kênh ẩn** | NeRF gốc: mạng fine 8 lớp × 256 |
| Kích hoạt nội | **ReLU** (cả 2 MLP) | giống NeRF gốc |
| Kích hoạt density `τ` | **softplus** (cả 2 MLP) | NeRF gốc: ReLU |
| Số lượt proposal | **2 lượt**, mỗi lượt **64 mẫu** → sinh `(ŝ₀,ŵ₀)` và `(ŝ₁,ŵ₁)` | NeRF gốc: 1 lượt coarse 64 điểm |
| Số mẫu cho NeRF MLP | **1 lượt, 32 mẫu** → sinh `(s, w)` | NeRF gốc: 192 điểm (64+128) cho mạng fine |
| `λ` (hệ số `L_dist`) | **0.01** — dùng trong mọi thí nghiệm | NeRF gốc: không có |
| `L_recon` | **Charbonnier**, `ε = 0.001` | NeRF gốc: MSE |
| **Số vòng lặp** | **250.000 (250k)** | NeRF gốc: 100k–300k |
| **Batch size** | **2¹⁴ = 16.384 tia** | NeRF gốc: 4.096 tia (gấp **4×**) |
| Optimizer | **Adam** | giống NeRF gốc |
| `β₁` | **0.9** | giống NeRF gốc |
| `β₂` | **0.999** | giống NeRF gốc |
| `ε` (Adam) | **10⁻⁶** | NeRF gốc: 10⁻⁷ |
| Learning rate | **giảm log-tuyến tính (log-linearly annealed) từ 2×10⁻³ xuống 2×10⁻⁵** | NeRF gốc: 5×10⁻⁴ → 5×10⁻⁵ (giảm theo hàm mũ). Mip-NeRF 360 **bắt đầu với lr cao gấp 4×** |
| **Warm-up** | **512 vòng lặp đầu** | **MỚI** — NeRF gốc không có |
| **Gradient clipping** | **chặn chuẩn (norm) ở 10⁻³** | **MỚI** — NeRF gốc không có |
| Phần cứng báo cáo | **TPU v2, 32 nhân** | NeRF gốc: 1 GPU NVIDIA V100 |
| Thời gian train | **6.89 giờ** (dataset 360) | NeRF gốc: ~1–2 ngày (trên phần cứng khác, **không so sánh trực tiếp được**) |

| Thuật ngữ | Ý nghĩa |
|---|---|
| **Warm-up** | Giai đoạn đầu train, learning rate được tăng dần từ rất nhỏ lên giá trị đích thay vì dùng ngay giá trị cao — tránh "sốc" làm trọng số bay đi lung tung lúc còn khởi tạo ngẫu nhiên |
| **Gradient clipping (theo norm)** | Nếu độ dài (norm) của vector gradient vượt ngưỡng, co nó lại về đúng ngưỡng mà giữ nguyên hướng — chống "gradient explosion" |
| **Log-linear annealing** | Learning rate giảm theo đường thẳng **trên thang logarit** — tức giảm theo cấp số nhân đều đặn qua các vòng lặp |

**[SUY-RA] Vì sao cần warm-up và gradient clipping ở Mip-NeRF 360 mà NeRF gốc không cần:** hàm loss Eq. 16 có 3 số hạng tương tác với nhau, trong đó `L_prop` có hệ số `1/w_i` — khi `w_i` rất nhỏ lúc mới khởi tạo, số hạng này có thể sinh gradient rất lớn. Thêm nữa, lr khởi điểm cao gấp 4× NeRF gốc. Cả 2 yếu tố làm giai đoạn đầu train dễ bất ổn hơn, nên cần warm-up + clipping. *Đây là suy luận, paper chỉ nêu dữ kiện.*

### 4.7. Ba chi tiết triển khai bổ sung (Phụ lục A) — nhỏ nhưng nên biết

**[P360, Phụ lục A]** mở đầu bằng việc thừa nhận mô hình *chứa 1 số thành phần nhỏ không được thảo luận trong phần chính, giúp cải thiện hiệu năng chút ít*. Ngoài **off-axis IPE** (đã trình bày ở mục 2.6) và **màu nền ngẫu nhiên** (mục 3.4), còn 3 chi tiết sau liên quan trực tiếp tới cơ chế proposal.

#### (a) **Annealing** trọng số đề xuất — Eq. 18

Trước khi lấy mẫu lại các khoảng tia từ trọng số đề xuất `ŵ`, các trọng số này được **annealing bằng cách nâng lên 1 luỹ thừa**. Với `N` bước train, tại bước `n`:

```
                  b·n/N
                ───────────
                (b−1)·n/N + 1
ŵ_n   ∝    ŵ                                                             (Eq. 18)

   tức:  ŵ_n  ∝  ŵ^e(n)   với số mũ   e(n) = (b·n/N) / ((b−1)·n/N + 1)
```

tức: **số mũ** áp lên `ŵ` là `e(n) = (b·n/N) / ((b−1)·n/N + 1)`, với **`b = 10`** trong mọi thí nghiệm.

| Ký hiệu | Ý nghĩa |
|---|---|
| `N` | tổng số bước train (250k) |
| `n` | bước train hiện tại |
| `b` | **siêu tham số bias**, đặt **b = 10** |
| `e(n)` | số mũ áp lên `ŵ` tại bước n |
| `∝` | "tỉ lệ với" — sau khi nâng luỹ thừa thì chuẩn hóa lại |

**[P360, Phụ lục A]** nêu: số mũ là **hàm bias của Schlick** áp lên `n/N ∈ [0,1]`, nó **uốn số mũ sao cho nó tăng nhanh từ 0 rồi bão hòa dần về 1**.

**[SUY-RA] Kiểm chứng số với b = 10:**

| `n/N` | `e(n) = 10(n/N) / (9(n/N)+1)` | Diễn giải |
|---|---|---|
| 0.00 | **0.000** | `ŵ⁰ = 1` cho mọi bin ⇒ **phân phối PHẲNG** — lấy mẫu gần như đều |
| 0.10 | 0.526 | đã hơn nửa đường |
| 0.25 | 0.769 | |
| 0.50 | 0.909 | gần như dùng hết phân phối đề xuất |
| 1.00 | **1.000** | `ŵ¹ = ŵ` ⇒ **dùng đúng phân phối đề xuất** |

**Ý nghĩa [P360, Phụ lục A]:** ở đầu quá trình train, số mũ là 0 ⇒ phân phối phẳng; ở cuối, số mũ là 1 ⇒ dùng đúng phân phối đề xuất. Việc annealing này **khuyến khích "exploration" (khám phá) trong lúc train**, bằng cách khiến NeRF MLP **được đưa vào 1 dải khoảng đề xuất rộng hơn** so với bình thường ở giai đoạn đầu.

**Giá trị thực nghiệm:** bỏ annealing làm SSIM trên `bicycle` tụt từ **0.687 → 0.679** — paper gọi đây là **tác động dương vừa phải (modest)**.

**[SUY-RA] Vì sao cần:** lúc mới khởi tạo, proposal MLP dự đoán gần như ngẫu nhiên. Nếu tin ngay vào nó, NeRF MLP chỉ được hỏi ở những vùng mà proposal MLP **tình cờ** đánh giá cao — và vì `L_prop` chỉ giám sát proposal dựa trên `w` của NeRF MLP, 2 mạng có thể **cùng nhau khóa vào 1 nghiệm sai** (vòng lặp phản hồi dương). Annealing phá vỡ vòng lặp đó ở giai đoạn đầu.

#### (b) **Dilation** (làm nở) histogram đề xuất — Eq. 19 & Eq. 20

Trước khi lấy mẫu lại, mỗi histogram đề xuất `(t̂, ŵ)` được **"làm nở" (dilate)** một chút.

**Lý do paper nêu [P360, Phụ lục A]:** việc này **giảm artifact aliasing**, *có lẽ vì proposal MLP chỉ được giám sát bằng các tia tương ứng với **các pixel input**, nên các dự đoán của nó **có thể chỉ đúng với 1 số góc nhất định** — theo 1 nghĩa nào đó, **proposal network bị aliasing về mặt góc xoay (rotationally aliased)**.* Làm rộng các khoảng của proposal MLP giúp **đối trọng lại** sự aliasing đó.

**Quy trình [P360, Eq. 19]:**
1. Chuyển histogram thành **mật độ xác suất**: `p̂_i = ŵ_i / (ŝ_{i+1} − ŝ_i)` — cho ta 1 **mật độ tích phân bằng 1** thay vì 1 histogram **tổng bằng 1**.
2. Làm nở bằng phép **lấy max trên 1 cửa sổ trượt**:
```
     max      p̂_ŝ(s')                                                   (Eq. 19)
 s−ε ≤ s' < s+ε
```
3. Tính hiệu quả bằng cách dựng tập mốc mới `sort( ŝ ∪ {ŝ−ε} ∪ {ŝ+ε} )` rồi lấy max trên mọi khoảng của tập mở rộng đó.
4. Chuyển `p̂` đã nở trở lại thành histogram bằng cách **nhân mỗi phần tử với bề rộng khoảng của nó**, rồi **chuẩn hóa lại cho tổng bằng 1**.

**Chọn `ε` [P360, Eq. 20]:** `ε` được đặt theo **kích thước kỳ vọng của 1 bin histogram** — với mỗi lượt coarse-to-fine `k` mà ta lấy `n_k` khoảng fine từ histogram coarse trước đó:

```
              a
ε_k  =  ────────────────  +  b                                           (Eq. 20)
         Π_{k'=1}^{k−1} n_k
```

với **`a = 0.5`** và **`b = 0.0025`**.

| Ký hiệu | Ý nghĩa |
|---|---|
| `ε_k` | bán kính cửa sổ làm nở cho lượt thứ k |
| `n_k` | số khoảng được lấy ở lượt k |
| `Π_{k'<k} n_k` | **tích của mọi số mẫu ở các lượt trước** — nghịch đảo của nó là **kích thước kỳ vọng của 1 bin** ở lượt đó |
| `a = 0.5` | quyết định histogram được nở bao nhiêu **so với kích thước bin kỳ vọng** |
| `b = 0.0025` | quyết định mức nở **theo giá trị tuyệt đối** (sàn tối thiểu) |

#### (c) **Sampling** — cách chọn mốc khoảng từ histogram (Eq. tại Figure 9)

**Cách của Mip-NeRF:** để sinh `n` khoảng "fine", nó lấy **n+1** mẫu khoảng cách từ histogram coarse `(t̂, ŵ)` rồi dùng chính **các mẫu đã sắp xếp đó làm 2 đầu mút** của `n` khoảng.

**Vấn đề [P360, Figure 9]:** cách này **"xói mòn" (erode)** histogram coarse, vì các mẫu **khó có khả năng trải hết bề rộng của mỗi bin coarse**. Hệ quả là các khoảng sinh ra **không bao phủ phần đầu và phần cuối của các mode (đỉnh) của histogram**, và **trải không đối xứng qua các khoảng trống giữa các mode**.

**Cách của Mip-NeRF 360:** lấy **n** mẫu đã sắp xếp từ histogram coarse, rồi dùng **điểm giữa (midpoint) của mỗi cặp mẫu liền kề** làm 2 đầu mút của tập `n` khoảng "fine" mới. Để xử lý **điều kiện biên**, họ **phản chiếu (reflect) mẫu đầu và mẫu cuối quanh mốc đầu và mốc cuối**.

**Đánh giá của paper:** thay đổi này *có **ít tác động về mặt định lượng** lên chất lượng render, nhưng họ nhận thấy nó **giảm aliasing về mặt định tính***.

> **Ghi chú tổng về 3 chi tiết (a)(b)(c):** cả 3 đều là **tinh chỉnh kỹ thuật quanh cơ chế resampling**, và cả 3 đều nhắm vào cùng 1 chủ đề: **làm cho proposal MLP "rộng rãi/khoan dung" hơn một chút**, để nó không vô tình chặn NeRF MLP khỏi những vùng không gian thực sự có cảnh. Nếu đồ án cần cài đặt lại Mip-NeRF 360, **(a) và (b) nên được cài** (mỗi cái đóng góp ~0.008 SSIM), còn (c) thuần túy là chất lượng thị giác.

### 4.8. Quy trình 1 vòng lặp train — tóm tắt toàn bộ

1. **Lấy batch tia ngẫu nhiên:** chọn **2¹⁴ = 16.384** tia từ toàn bộ pixel của toàn bộ ảnh train (các tia có thể đến từ nhiều ảnh khác nhau).
2. **Lượt proposal 0:** chia **64** khoảng đều trong **s-space** (`s ∈ [0,1]`, đổi về `t` qua Eq. 11 với `g(x)=1/x`) → với mỗi khoảng tính nón cụt `(μ,Σ)` → áp `contract(μ,Σ)` (Eq. 9–10) → off-axis IPE → **Proposal MLP (4×256)** → density → Eq. 4 → `(ŝ₀, ŵ₀)`.
3. **Resample 1:** **annealing** `ŵ₀` theo Eq. 18 → **dilate** theo Eq. 19–20 → lấy **64** khoảng mới (midpoint-based, mục 4.7c).
4. **Lượt proposal 1:** chạy lại **Proposal MLP** trên 64 khoảng mới → `(ŝ₁, ŵ₁)`.
5. **Resample 2:** annealing + dilate `ŵ₁` → lấy **32** khoảng cuối.
6. **Lượt NeRF:** 32 khoảng → nón cụt → contract → off-axis IPE (+ hướng nhìn `d`) → **NeRF MLP (8×1024)** → `(τ_i, c_i)` → Eq. 4 → `(s, w)` → Eq. 3 → **màu render `C(r,t)`**, composite với **màu nền RGB ngẫu nhiên**.
7. **Tính loss Eq. 16:** `L_recon` (Charbonnier, ε=0.001) + `0.01·L_dist(s,w)` (Eq. 15) + `L_prop(s,w,ŝ₀,ŵ₀) + L_prop(s,w,ŝ₁,ŵ₁)` (Eq. 13), **với stop-gradient trên `(s,w)` trong các số hạng `L_prop`**.
8. **Cập nhật:** backpropagation → **gradient clipping** (norm 10⁻³) → **Adam** (β₁=0.9, β₂=0.999, ε=10⁻⁶) với lr theo lịch log-tuyến tính (có **warm-up 512 bước**) → cập nhật **cả `Θ_prop` lẫn `Θ_NeRF`**.

Lặp lại **250.000** lần.

---

## Giai đoạn 5: Inference & Sơ đồ tổng thể Pipeline

Sau 250.000 vòng lặp, cả `Θ_prop` và `Θ_NeRF` đã hội tụ và được **đóng băng**. Giai đoạn này mô tả cách dùng chúng để sinh ảnh ở góc nhìn mới.

> **Lưu ý về nguồn:** paper **không có mục riêng mô tả tường minh quy trình inference** (giống paper NeRF gốc). Quy trình dưới đây được **suy ra trực tiếp** từ kiến trúc đã mô tả ở Mục 1–5 của paper, cộng với 2 dữ kiện mà paper nêu tường minh về chế độ đánh giá (đánh dấu [P360] bên dưới). Phần suy ra được đánh dấu [SUY-RA].

### 5.1. Quy trình render 1 ảnh ở góc nhìn mới

#### Chú thích ký hiệu mới

| Ký hiệu | Ý nghĩa |
|---|---|
| `Θ_NeRF`, `Θ_prop` | 2 tập trọng số đã train xong, **cố định (frozen)** — không còn cập nhật |

**Bước 1 — Chọn pose mới (R, C).** Người dùng chọn 1 cặp (R, C) bất kỳ trong hệ world **đã chuẩn hóa ở Giai đoạn 1 mục 1.3**. Thường là nội suy mượt giữa các pose train để tạo video "bay camera".

> **⚠️ Hạn chế mà paper nêu tường minh [P360, Limitations]:** *chất lượng tổng hợp góc nhìn **có thể giảm nếu camera bị di chuyển ra xa khỏi TÂM của cảnh**.* Đây là hệ quả trực tiếp của thiết kế `contract(·)`: phép co giữ nguyên tuyến tính chỉ trong **hình cầu bán kính 1 quanh tâm cảnh**, nên nếu camera ra ngoài vùng đó, nó sẽ "nhìn" vào vùng không gian đã bị nén mạnh, nơi mô hình có ít dung lượng biểu diễn.

**Bước 2 — Với mỗi pixel (u,v):** lặp lại đúng chuỗi Giai đoạn 2 → 3 → 4 (bước 2–6 của mục 4.8), nhưng:

| Khác biệt khi inference | Chi tiết |
|---|---|
| **Không có backpropagation, không tính loss** | chỉ forward pass |
| **Lấy mẫu khởi tạo: cách đều, không ngẫu nhiên** | **[P360, Mục 1]** ghi rõ cho Mip-NeRF: *trong lúc train việc lấy mẫu này là stochastic, nhưng **khi đánh giá thì các mẫu được đặt cách đều** từ `t_n` tới `t_f`*. Với Mip-NeRF 360, việc "cách đều" này diễn ra **trong s-space** |
| **Annealing đã đạt giá trị cuối** | `n/N = 1` ⇒ số mũ = 1 ⇒ dùng **đúng** phân phối đề xuất `ŵ`, không làm phẳng nữa (Eq. 18) |
| **Màu nền cố định** | **[P360, Phụ lục A]**: khi test, màu nền được đặt là **(0.5, 0.5, 0.5)** (xám trung tính), không còn ngẫu nhiên |
| **Không có ground truth** | góc nhìn mới chưa từng được chụp |

**Bước 3 — Ghép toàn bộ pixel** theo đúng vị trí (u,v) → ảnh output hoàn chỉnh.

**Bước 4 — (Tùy chọn) Xuất depth map.** **[P360, Figure 7]** cho biết các depth map trong paper được tính bằng **khoảng cách kết thúc tia trung vị (median ray termination distance)**. Chất lượng depth map là 1 **điểm mạnh mà paper nhấn mạnh nhiều lần**: mô hình *tạo ra depth map cực kỳ chi tiết, trong khi SVS và Deep Blending thì không* (các "SVS depths" trong Figure 7 thực chất do COLMAP sinh ra và được dùng làm **input** cho SVS, chứ không phải output của nó) **[P360, Mục 6]**.

### 5.2. So sánh Train vs Inference

| | **Train (Giai đoạn 4)** | **Inference (Giai đoạn 5)** |
|---|---|---|
| `Θ_prop`, `Θ_NeRF` | đang cập nhật mỗi vòng | **cố định** |
| Ground truth `C*(r)` | có — từ ảnh train | **không có** |
| `L_recon`, `L_dist`, `L_prop` | cả 3 được tính + backprop | **không tính gì** |
| Lấy mẫu khởi tạo trong s-space | **ngẫu nhiên (stochastic)** | **cách đều (deterministic)** |
| Annealing `ŵ` (Eq. 18) | số mũ tăng từ 0 → 1 theo tiến độ | số mũ = **1** (dùng nguyên `ŵ`) |
| Màu nền | **ngẫu nhiên** từ [0,1]³ | **(0.5, 0.5, 0.5)** |
| Số lần chạy | 250.000 batch × 16.384 tia | 1 lần/pixel/ảnh |

### 5.3. Sơ đồ tổng thể toàn bộ Pipeline Mip-NeRF 360

```
┌────────────────────────────────────────────────────────────────────────────────┐
│ GIAI ĐOẠN 1 — Dữ liệu & Camera Pose  (chạy 1 lần, offline)                     │
│   100–330 ảnh cảnh 360° unbounded (1 vật thể trung tâm + hậu cảnh xa)          │
│   ──► COLMAP/SfM (shared intrinsics, OpenCV radial model) ──► undistort         │
│   ──► downsample về 1.0–1.6 MP ──► 1/8 ảnh làm test set                        │
│   ──► ★MỚI: dời tâm camera + PCA chọn trục "up" + rescale vào [−1,1]³          │
│   ──► (R, C, K) cho mỗi ảnh  +  kích thước pixel (cần cho bán kính nón)         │
└──────────────────────────────────┬─────────────────────────────────────────────┘
                                   ▼
   ╔════════════════════════════════════════════════════════════════════════════╗
   ║  VÒNG LẶP TRAIN — 250.000 lần,  batch = 2¹⁴ = 16.384 tia,  CÓ backprop      ║
   ║                                                                            ║
   ║  ┌──────────────────────────────────────────────────────────────────────┐  ║
   ║  │ GIAI ĐOẠN 2 — Tham số hóa & Lấy mẫu                                   │  ║
   ║  │  pixel(u,v) ──► d ──► r(t)=o+t·d                                      │  ║
   ║  │  ★ s-space: chia đều s∈[0,1], đổi về t qua Eq.11 với g(x)=1/x         │  ║
   ║  │    (⇒ mẫu tuyến tính theo DISPARITY, t_f=∞ vẫn hợp lệ)                │  ║
   ║  │  mỗi khoảng T_i ──► nón cụt ──► Gaussian (μ,Σ)        [kế thừa mip]   │  ║
   ║  │  ★ contract(μ,Σ) = (contract(μ), J Σ Jᵀ)   Eq.9+Eq.10  [Kalman-like]  │  ║
   ║  │    (vùng ‖x‖≤1 giữ nguyên; ‖x‖>1 nén vào vỏ cầu bán kính → 2)         │  ║
   ║  │  ★ off-axis IPE  γ(contract(μ,Σ))  (P = 21 đỉnh icosahedron)  Eq.1+17 │  ║
   ║  └────────────────────────────────┬─────────────────────────────────────┘  ║
   ║                                   ▼                                        ║
   ║  ┌──────────────────────────────────────────────────────────────────────┐  ║
   ║  │ GIAI ĐOẠN 4a — ★PROPOSAL MLP (4 lớp × 256), 2 LƯỢT × 64 mẫu           │  ║
   ║  │   ──► CHỈ density (KHÔNG có nhánh màu) ──► Eq.4 ──► (ŝ₀,ŵ₀),(ŝ₁,ŵ₁)  │  ║
   ║  │   resample: ★annealing Eq.18  +  ★dilation Eq.19-20  +  ★midpoint     │  ║
   ║  └────────────────────────────────┬─────────────────────────────────────┘  ║
   ║                                   ▼  32 khoảng cuối                        ║
   ║  ┌──────────────────────────────────────────────────────────────────────┐  ║
   ║  │ GIAI ĐOẠN 3 — NeRF MLP (8 lớp × ★1024), chạy ĐÚNG 1 LẦN               │  ║
   ║  │   + hướng nhìn d ──► (τ_i, c_i),  ★density dùng softplus              │  ║
   ║  │   ──► Eq.4 ──► (s, w) ──► Eq.3 ──► C(r,t)                             │  ║
   ║  │   ──► composite với ★màu nền RGB NGẪU NHIÊN                           │  ║
   ║  └────────────────────────────────┬─────────────────────────────────────┘  ║
   ║                                   ▼                                        ║
   ║  ┌──────────────────────────────────────────────────────────────────────┐  ║
   ║  │ GIAI ĐOẠN 4b — HÀM LOSS Eq.16  (chỉ áp loss ảnh ĐÚNG 1 LẦN)           │  ║
   ║  │    L_recon(Charbonnier, ε=0.001)                   ← ảnh thật C*      │  ║
   ║  │  + 0.01 · ★L_dist(s,w)       Eq.15   ← chống floaters & bg collapse   │  ║
   ║  │  + ★L_prop(s,w,ŝ₀,ŵ₀) + L_prop(s,w,ŝ₁,ŵ₁)  Eq.12-13                  │  ║
   ║  │        ↑ ★STOP-GRADIENT trên (s,w): NeRF "dẫn", proposal "theo"       │  ║
   ║  │  ──► backprop ──► ★grad clip (norm 1e-3) ──► Adam ──► Θ_prop, Θ_NeRF  │  ║
   ║  └────────────────────────────────┬─────────────────────────────────────┘  ║
   ║                                   └──── quay lại Giai đoạn 2, batch MỚI ───╣
   ╚═══════════════════════════════════════╦════════════════════════════════════╝
                                           │  (sau 250k bước, Θ cố định)
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│ GIAI ĐOẠN 5 — INFERENCE                                                        │
│   Θ CỐ ĐỊNH · KHÔNG backprop · KHÔNG ground truth                              │
│   Chọn (R,C) mới (nên giữ gần TÂM cảnh — xem Limitations)                       │
│   Mỗi pixel: lặp Giai đoạn 2 → 4a → 3 (chỉ forward)                            │
│     · mẫu khởi tạo CÁCH ĐỀU trong s-space (không ngẫu nhiên)                    │
│     · annealing đã = 1 (dùng nguyên ŵ)  ·  màu nền = (0.5,0.5,0.5)             │
│   ──► ghép pixel ──► ẢNH OUTPUT  +  DEPTH MAP (median ray termination)          │
└────────────────────────────────────────────────────────────────────────────────┘

   ★ = thành phần KHÁC so với NeRF gốc
```

### 5.4. Bảng tra cứu: Giai đoạn ↔ Mục/Công thức trong paper gốc (arXiv:2111.12077)

| Giai đoạn (tài liệu này) | Nội dung | Mục / Công thức trong paper |
|---|---|---|
| **0** | 3 vấn đề (Parameterization / Efficiency / Ambiguity) | Introduction (3 đoạn có tiêu đề in nghiêng cùng tên) |
| **1** | COLMAP/SfM, dataset, chuẩn hóa pose bằng PCA | Mục 6 (1 câu về COLMAP); **Phụ lục D** (toàn bộ chi tiết dataset + chuẩn hóa pose) |
| **2** (nền kế thừa) | Conical frustum, `(μ,Σ) = r(T_i)`, IPE | **Mục 1** "Preliminaries: mip-NeRF", **Eq. 1** |
| **2** (mới) | Tuyến tính hóa `f`, áp lên Gaussian kiểu Kalman | **Mục 2**, **Eq. 8**, **Eq. 9** |
| **2** (mới) | `contract(x)` | **Mục 2**, **Eq. 10**, **Figure 2** |
| **2** (mới) | Ánh xạ `t ↔ s`, `g(x)=1/x`, lấy mẫu trong s-space | **Mục 2**, **Eq. 11**; lấy mẫu gốc ở **Eq. 5, Eq. 6** |
| **2** (mới) | Off-axis IPE, ma trận cơ sở P | **Phụ lục A**, **Eq. 17**, **Figure 8** |
| **3** | MLP → (τ, c); hướng nhìn d | **Mục 1**, **Eq. 2** |
| **3** | Volume rendering | **Mục 1**, **Eq. 3**, **Eq. 4** |
| **3** | Kiến trúc & quy mô 2 MLP, softplus | **Mục 5** |
| **3** | Màu nền ngẫu nhiên | **Phụ lục A** "Background Colors" |
| **4** | Phê phán coarse/fine của Mip-NeRF; loss Mip-NeRF | **Introduction** ("Efficiency"); **Mục 1**, **Eq. 7** |
| **4** | Proposal MLP + online distillation, stop-gradient | **Mục 3**, **Figure 3**, **Figure 4** |
| **4** | `bound(·)` và `L_prop` | **Mục 3**, **Eq. 12**, **Eq. 13**; minh họa ở **Phụ lục C**, **Figure 10** |
| **4** | Floaters, background collapse, `L_dist` | **Mục 4**, **Eq. 14**, **Eq. 15**, **Figure 5**, **Figure 6** |
| **4** | Loss tổng, Charbonnier, mọi siêu tham số | **Mục 5**, **Eq. 16** |
| **4** | Annealing / Dilation / Sampling (midpoint) | **Phụ lục A**, **Eq. 18**, **Eq. 19**, **Eq. 20**, **Figure 9** |
| **4** | Tính Jacobian bằng autodiff / `linearize` của Jax | **Phụ lục B** |
| **5** | Inference (quy trình) | **Không có mục riêng** — suy ra từ Mục 1–5; 2 dữ kiện tường minh: lấy mẫu cách đều khi eval (**Mục 1**), màu nền test (**Phụ lục A**) |
| **5** | Depth map (median ray termination) | **Figure 7** |
| **—** | Kết quả định lượng | **Mục 6**, **Table 1** (dataset 360), **Table 2** (ablation), **Table 3** (Blender), **Table 4** (LLFF), **Table 5–7** (chi tiết theo scene / Tanks and Temples) |
| **—** | Hạn chế | **Mục 6** "Limitations" |
| **—** | Tác động xã hội tiêu cực tiềm tàng | **Phụ lục E** |

---

## BẢNG TỔNG HỢP — "Thay đổi gì so với NeRF gốc"

> **Cách đọc cột "Nguồn thay đổi":** **[MIP-2021]** = thay đổi đã có từ Mip-NeRF (2021), bản 360 **kế thừa**; **[360-MỚI]** = thay đổi **mới của riêng bản 360**; **[360-NÂNG-CẤP]** = thành phần có gốc từ Mip-NeRF nhưng bản 360 **sửa/mở rộng thêm**.
>
> *Lưu ý độ chắc chắn: việc gán nhãn [MIP-2021] dựa trên phần "Preliminaries: mip-NeRF" của paper 360 (những gì paper mô tả như là **đã có sẵn**) — độ tin cậy cao. Nhưng vì **paper Mip-NeRF gốc không có trong thư mục**, không thể loại trừ khả năng 1 vài chi tiết nhỏ bị gán nhãn lệch. Các nhãn [360-MỚI] thì chắc chắn, vì paper trình bày chúng như đóng góp của chính nó.*

### Phần A — Thay đổi về TRÌNH BÀY/LẤY MẪU HÌNH HỌC

| # | Thành phần | NeRF gốc làm gì | Mip-NeRF 360 làm gì | Lý do cải tiến | Hệ quả | Nguồn thay đổi |
|---|---|---|---|---|---|---|
| A1 | **Đơn vị lấy mẫu dọc tia** | **1 điểm** `r(t_i)` vô cùng nhỏ | **1 khoảng** `T_i = [t_i, t_{i+1})`, hiện thực hóa thành **hình nón cụt** → xấp xỉ **Gaussian (μ,Σ)** | 1 pixel là 1 **ô vuông** chứ không phải 1 điểm ⇒ vùng nó "thấy" là 1 hình nón phình theo khoảng cách. Điểm không mang thông tin tỉ lệ | Khử aliasing; mạng biết nó đang được hỏi ở độ phân giải nào | **[MIP-2021]** |
| A2 | **Mã hóa input** | **PE** `γ(p) = (sin(2^ℓπp), cos(2^ℓπp))_{ℓ=0..L−1}` của 1 điểm | **IPE** Eq. 1: thêm hệ số `exp(−2^(2ℓ−1)diag(Σ))` | Là kỳ vọng giải tích của PE trên Gaussian ⇒ **tự động tắt các tần số lớn hơn kích thước vùng** | Anti-aliasing có nguyên lý toán học, không cần hậu xử lý. Ablation G: bỏ IPE ⇒ SSIM 0.687→0.664 | **[MIP-2021]** |
| A3 | **Cơ sở chiếu của IPE** | — (không có khái niệm) | **Off-axis IPE**: `P` = 21 đỉnh icosahedron chia nhỏ 2 lần (Eq. 17), thay vì `P = I` của Mip-NeRF | Phép co (A5) sinh Gaussian **cực kỳ dị hướng và nghiêng**; IPE theo trục không phân biệt được các Gaussian cùng marginal nhưng khác hướng nghiêng | Cần **Σ đầy đủ** (không chỉ đường chéo). Ablation: bỏ off-axis ⇒ SSIM 0.687→0.664 | **[360-NÂNG-CẤP]** |
| A4 | **Tham số hóa khoảng cách tia** | Lấy mẫu **đều theo `t`** (stratified sampling trên [t_n, t_f]) | Ánh xạ `t ↔ s` (Eq. 11) với **`g(x)=1/x`**, lấy mẫu **đều theo `s`** ⇒ **tuyến tính theo disparity** | Vùng xa cần ít dung lượng hơn vùng gần (do phép chiếu phối cảnh). Lấy mẫu đều theo `t` làm vùng xa bị undersampling nặng | **`t_f = ∞` trở nên hợp lệ** (vì `s` luôn kết thúc tại 1); mật độ mẫu tỉ lệ độ quan trọng thị giác | **[360-MỚI]** |
| A5 | **Tham số hóa không gian 3D** | Tọa độ Euclid thô (object-centric) **hoặc** NDC (chỉ cho forward-facing, chỉ mở trục z) | **`contract(x)`** Eq. 10 — bóp mọi hướng vào cầu bán kính 2, giữ nguyên cầu bán kính 1 | Cảnh unbounded theo **mọi** hướng; NDC chỉ mở được **1** hướng | Vô hạn gói vào miền hữu hạn; vùng trung tâm giữ đủ chi tiết. Ablation H: bỏ phép co ⇒ PSNR 24.37→23.77, **và chậm hơn, nhiều tham số hơn** | **[360-MỚI]** |
| A6 | **Áp biến đổi lên THỂ TÍCH, không chỉ ĐIỂM** | — (chỉ có điểm) | Eq. 8–9: tuyến tính hóa `f` bằng **Jacobian**, truyền covariance theo **`J Σ Jᵀ`** — tương đương **Extended Kalman filter** | Đơn vị lấy mẫu là (μ,Σ); co μ mà để Σ nguyên thì hình dạng Gaussian sau co sẽ sai hoàn toàn | Đóng góp **tổng quát**: áp được **bất kỳ** phép tham số hóa trơn nào lên thể tích. Tên "Kalman-like scene parameterization" | **[360-MỚI]** |
| A7 | **Đồng thiết kế A4 + A5** | — | `2 − 1/t` (bán kính sau co) và `1 − 1/t` (toạ độ s) **triệt tiêu nhau**: bán kính co = `1 + s` | Để các mẫu **cách đều trong không gian đã co** | Biến bài toán unbounded **trở lại** thành bài toán "khoảng cách đều trong không gian bị chặn" — đúng chế độ mà NeRF gốc vốn giải tốt | **[360-MỚI]** |

### Phần B — Thay đổi về KIẾN TRÚC MẠNG & COARSE-TO-FINE

| # | Thành phần | NeRF gốc làm gì | Mip-NeRF 360 làm gì | Lý do cải tiến | Hệ quả | Nguồn thay đổi |
|---|---|---|---|---|---|---|
| B1 | **Số & vai trò các mạng** | **2 mạng cùng kích thước**: coarse 8×256 + fine 8×256, **cả hai dự đoán density + màu** | **2 mạng khác hẳn vai trò**: **Proposal MLP 4×256 (CHỈ density)** + **NeRF MLP 8×1024 (density + màu)** | Mạng dò đường chỉ cần biết **"cảnh ở đâu"**, không cần biết **"cảnh màu gì"** | Mạng nhỏ gọi nhiều lần (rẻ), mạng lớn gọi 1 lần (đắt nhưng ít) ⇒ **dung lượng ~15× Mip-NeRF, thời gian chỉ ~2×** | **[360-MỚI]** (Mip-NeRF dùng **1** MLP đa tỉ lệ gọi lặp lại — đã khác NeRF gốc, nhưng vẫn khác hẳn bản 360) |
| B2 | **Giám sát mạng dò đường** | `‖Ĉ_c(r) − C(r)‖²` — **so màu render thô với ẢNH THẬT** | **`L_prop`** (Eq. 13) — so **histogram** của nó với histogram `(t,w)` của NeRF MLP. **Không bao giờ thấy ảnh thật** | Bản render coarse **bị bỏ đi hoàn toàn**, tính nó là lãng phí; và ép nó khớp ảnh thật là ép nó học nhiệm vụ khó hơn cần thiết | Ablation E: dùng cách giám sát của Mip-NeRF ⇒ PSNR 24.37→23.45 **và** 7.09h→18.89h. Ablation A: bỏ hẳn `L_prop` ⇒ PSNR sụp xuống **20.49**, SSIM **0.406** | **[360-MỚI]** |
| B3 | **Quan hệ dẫn/theo** | — (2 mạng độc lập, cùng học từ ảnh) | **Stop-gradient** trên `(t,w)` của NeRF MLP trong `L_prop` ⇒ NeRF **dẫn**, proposal **theo** | Nếu không, tối ưu hóa có thể làm NeRF MLP **nhòe đi** để proposal dễ bao ⇒ hỏng ảnh | Tối ưu `Θ_prop` **độc lập** với `Θ_NeRF` ⇒ **không cần siêu tham số cân `L_prop`** (Mip-NeRF phải chọn hệ số 1/10 ở Eq. 7) | **[360-MỚI]** |
| B4 | **Tính bất đối xứng của loss chưng cất** | — | `max(0, w_i − bound)²` — **chỉ phạt khi đề xuất BỎ SÓT**, không phạt khi bao rộng | Proposal MLP nhỏ **về dung lượng không thể** sắc nét bằng NeRF MLP; nhưng "bao rộng" chỉ tốn vài mẫu, còn "bỏ sót" thì mất cảnh | Proposal weights hình thành **đường bao trên (upper envelope)** quanh NeRF weights — thấy rõ ở Figure 4 | **[360-MỚI]** |
| B5 | **Số lượt & số mẫu** | coarse **64** điểm → fine **64+128 = 192** điểm | proposal **64** → proposal **64** → NeRF **32** | Dồn tài nguyên: mạng lớn chỉ cần 32 mẫu vì 2 lượt proposal đã khoanh vùng rất gọn | Số lần gọi **mạng lớn** giảm từ 192 xuống **32** mẫu/tia | **[360-MỚI]** |
| B6 | **Kích thước mạng chính** | 8 lớp × **256** kênh | 8 lớp × **1024** kênh | Cảnh lớn & chi tiết làm dung lượng MLP **bão hòa**; cần mạng rộng hơn | 0.7M → **9.9M** tham số. Ablation F: dùng NeRF MLP 256 kênh ⇒ PSNR 24.37→22.80, SSIM 0.687→0.515 | **[360-MỚI]** |
| B7 | **Kích hoạt density** | **ReLU** | **Softplus** | (paper chỉ nêu dữ kiện) **[SUY-RA]**: ReLU cho gradient 0 ở vùng âm ⇒ nơ-ron density "chết"; cảnh unbounded có rất nhiều vùng trống nên vấn đề này nặng hơn | Tối ưu hóa ổn định hơn ở các vùng không gian trống | **[360-MỚI]** (hoặc có thể từ Mip-NeRF — **không xác minh được** vì thiếu paper 2021) |
| B8 | **Resampling: chọn mốc khoảng** | Dùng trực tiếp các mẫu đã sắp xếp làm mốc biên | **Lấy `n` mẫu, dùng ĐIỂM GIỮA của từng cặp liền kề** làm mốc; phản chiếu mẫu đầu/cuối để xử lý biên | Cách cũ **"xói mòn"** histogram: các mẫu khó trải hết bề rộng mỗi bin ⇒ không bao phủ đầu/cuối các mode | Ít tác động định lượng, nhưng **giảm aliasing về định tính** | **[360-MỚI]** |
| B9 | **Annealing trọng số đề xuất** | — | Nâng `ŵ` lên luỹ thừa `e(n)` tăng từ 0→1 theo tiến độ train (Eq. 18, hàm bias Schlick, b=10) | Lúc đầu proposal MLP dự đoán gần như ngẫu nhiên; tin ngay vào nó ⇒ 2 mạng có thể cùng khóa vào nghiệm sai | Khuyến khích **exploration**. Bỏ nó ⇒ SSIM 0.687→0.679 | **[360-MỚI]** |
| B10 | **Dilation histogram đề xuất** | — | Làm nở mỗi `(ŝ,ŵ)` bằng max trên cửa sổ ±`ε_k` (Eq. 19–20; a=0.5, b=0.0025) | Proposal MLP chỉ được giám sát bằng tia của **pixel input** ⇒ nó bị **"aliasing về góc xoay"**; dự đoán của nó có thể chỉ đúng với 1 số góc | Giảm artifact aliasing | **[360-MỚI]** |

### Phần C — Thay đổi về HÀM LOSS & CHÍNH QUY HÓA

| # | Thành phần | NeRF gốc làm gì | Mip-NeRF 360 làm gì | Lý do cải tiến | Hệ quả | Nguồn thay đổi |
|---|---|---|---|---|---|---|
| C1 | **Số lần áp loss ảnh** | **2 lần** (coarse + fine), trọng số bằng nhau | **1 lần duy nhất** — chỉ cho NeRF MLP (Eq. 16) | Render coarse không góp gì vào ảnh cuối | Bớt 1 nửa tín hiệu giám sát "vô ích"; nhường chỗ cho `L_prop` | **[360-MỚI]** |
| C2 | **Dạng loss ảnh** | **MSE** `‖·‖²` | **Charbonnier** `√((x−x*)² + ε²)`, ε=0.001 | Paper: *đạt tối ưu hóa **ổn định hơn một chút** so với MSE* | Robust với outlier (pixel dư sáng, nhiễu) | **[360-MỚI]** |
| C3 | **Chống floaters / background collapse** | **Tiêm nhiễu Gaussian vào density** trước rectifier | **`L_dist`** (Eq. 14–15), λ=0.01 — regularizer trên **hình dạng phân phối trọng số dọc cả tia** | Bài toán under-constrained: **1 họa vô hạn** NeRF giải thích được ảnh input. Nhiễu density chỉ tác động lên **từng giá trị riêng lẻ**; cần ràng buộc **toàn cục trên tia**. Và các regularizer cũ thiết kế cho **mẫu điểm**, không cho **khoảng** | Chặn floaters **và** background collapse. Ablation C: cách tiêm nhiễu của NeRF gốc ⇒ PSNR **24.00** (tệ hơn cả việc không regularize) | **[360-MỚI]** |
| C4 | **Hệ quy chiếu của regularizer** | — | `L_dist` tính trên **`s`** (chuẩn hóa), **không** trên `t` | Dùng `t` sẽ **nâng trọng số các khoảng xa lên rất nhiều** và khiến các khoảng gần **bị bỏ qua hữu hiệu** | Mọi vùng cảnh có "tiếng nói" tỉ lệ độ quan trọng thị giác | **[360-MỚI]** |
| C5 | **Loss chưng cất** | — | **`L_prop`** (Eq. 12–13): nửa-bậc-hai, 1 phía, chia cho `w_i`; dựa trên **tính chất độ đo ngoài (outer measure)** | 2 histogram có **bin khác nhau hoàn toàn** ⇒ không dùng được độ đo histogram thông thường. Tiêu chí: *nếu TỒN TẠI 1 phân phối giải thích được cả hai thì loss PHẢI = 0* | Chia cho `w_i` làm **gradient theo `bound` là hằng số khi `bound`=0** ⇒ tối ưu hóa ổn định, không "phớt lờ" các bin nhẹ | **[360-MỚI]** |
| C6 | **Màu nền khi train** | **Cố định** (đen/trắng đã biết) | **Ngẫu nhiên** từ `[0,1]³` khi train; `(0.5,0.5,0.5)` khi test | Nền cố định ⇒ mạng học hậu cảnh **bán trong suốt** ⇒ median ray termination vô nghĩa ⇒ **depth map kém** | Cưỡng chế hậu cảnh **đục** ⇒ depth map chính xác. Áp dụng cho dataset 360 và LLFF, **không** cho Blender | **[360-MỚI]** |

### Phần D — Thay đổi về DỮ LIỆU & LỊCH TRÌNH HUẤN LUYỆN

| # | Thành phần | NeRF gốc | Mip-NeRF 360 | Lý do / Hệ quả | Nguồn |
|---|---|---|---|---|---|
| D1 | Loại cảnh | Bounded: vật thể có nền masked, hoặc forward-facing | **Unbounded 360°**: 1 vật thể/khu vực trung tâm **+ hậu cảnh chi tiết trải ra xa** (9 scene: 5 ngoài trời, 4 trong nhà) | Đây là **thay đổi đề bài**, nguồn gốc của mọi thay đổi kỹ thuật khác | **[360-MỚI]** |
| D2 | Số ảnh/scene | ~20–100 | **100–330** | Cảnh lớn hơn cần nhiều quan sát hơn | **[360-MỚI]** |
| D3 | Tiền xử lý pose | COLMAP → dùng trực tiếp | COLMAP → **dời tâm camera, PCA chọn trục "up", rescale vào [−1,1]³** | **Điều kiện tiên quyết** để `contract(·)` đặt đúng vùng giữ nguyên lên vùng trung tâm cảnh | **[360-MỚI]** |
| D4 | Hiệu chuẩn | — | **Shared intrinsics** + mô hình méo xuyên tâm OpenCV + **undistort bằng COLMAP trước khi train** | Lens góc rộng (để bao 360°) có méo nặng; không khử thì hướng tia ở biên ảnh sai | **[360-MỚI]** |
| D5 | Batch size | 4.096 tia | **16.384 tia (2¹⁴)** — gấp **4×** | Tận dụng TPU v2 32 nhân; gradient ít nhiễu hơn | **[360-MỚI]** |
| D6 | Số vòng lặp | 100k–300k | **250k** | Tương đương | — |
| D7 | Learning rate | 5×10⁻⁴ → 5×10⁻⁵ (exponential decay) | **2×10⁻³ → 2×10⁻⁵ (log-linear)** — khởi điểm cao gấp **4×** | Batch lớn gấp 4× cho phép lr cao hơn | **[360-MỚI]** |
| D8 | Warm-up | **Không có** | **512 bước đầu** | Loss 3 số hạng (có `1/w_i`) dễ bất ổn lúc khởi tạo | **[360-MỚI]** |
| D9 | Gradient clipping | **Không có** | **Chặn norm ở 10⁻³** | Cùng lý do D8 | **[360-MỚI]** |
| D10 | Adam `ε` | 10⁻⁷ | **10⁻⁶** | Chi tiết nhỏ | **[360-MỚI]** |
| D11 | Chia test set | Tùy dataset | **1 trong 8 ảnh**, lấy cách đều để phủ nhiều góc nhìn | Đánh giá công bằng trên toàn quỹ đạo | **[360-MỚI]** |
| D12 | Phần cứng báo cáo | 1 GPU NVIDIA V100 | **TPU v2, 32 nhân** | ⚠️ **Không so sánh trực tiếp thời gian train giữa 2 paper được** — khác phần cứng hoàn toàn | — |

### Phần E — Bảng cô đọc: NeRF gốc → Mip-NeRF → Mip-NeRF 360

| Chiều so sánh | **NeRF (2020)** | **Mip-NeRF (2021)** | **Mip-NeRF 360 (2022)** |
|---|---|---|---|
| Đơn vị lấy mẫu | điểm | **nón cụt / Gaussian** | nón cụt / Gaussian (**đã co**) |
| Encoding | PE | **IPE (axis-aligned, P=I)** | **IPE off-axis (P = 21 hướng)** |
| Tham số hóa không gian | Euclid thô / NDC (1 hướng) | Euclid thô (vẫn bounded) | **`contract(·)` — mọi hướng** |
| Khoảng cách tia | đều theo `t` | đều theo `t` | **đều theo `s` = tuyến tính theo disparity** |
| Cần `t_f` hữu hạn | **có** | **có** | **không** |
| Số MLP | **2** (coarse + fine, cùng cỡ) | **1** MLP đa tỉ lệ, gọi lặp lại | **2** (proposal nhỏ + NeRF lớn, **khác vai trò**) |
| Mạng dò đường dự đoán màu? | **có** | **có** (cùng 1 MLP) | **KHÔNG** |
| Giám sát mạng dò đường | ảnh thật | ảnh thật (hệ số 1/10) | **`L_prop`** (histogram của NeRF MLP) |
| Regularizer | tiêm nhiễu density | tiêm nhiễu density | **`L_dist`** (λ=0.01) |
| Loss ảnh | MSE × 2 nhánh | MSE × 2 nhánh (1/10 và 1) | **Charbonnier × 1 nhánh** |
| Kích hoạt density | ReLU | ReLU | **softplus** |
| Số tham số | ~1.5M (theo Table 1) | **0.7M** | **9.9M** |
| PSNR trên dataset 360 | **23.85** | **24.04** | **27.69** |
| Thời gian train (TPU v2 32 nhân) | 4.16h | 3.17h | **6.89h** |

---

## Kết quả thực nghiệm & Ablation Study (trích từ paper)

### Bảng 1 — So sánh định lượng trên dataset 360 **[P360, Table 1]**

Chỉ số: **PSNR ↑** (cao hơn tốt hơn), **SSIM ↑**, **LPIPS ↓** (thấp hơn tốt hơn). Thời gian & số tham số đo trên **TPU v2, 32 nhân**.

| Phương pháp | PSNR ↑ | SSIM ↑ | LPIPS ↓ | Thời gian (giờ) | # Tham số |
|---|---|---|---|---|---|
| NeRF | 23.85 | 0.605 | 0.451 | 4.16 | 1.5M |
| NeRF + tham số hóa của DONeRF | 24.03 | 0.607 | 0.455 | 4.59 | 1.4M |
| mip-NeRF | 24.04 | 0.616 | 0.441 | 3.17 | 0.7M |
| NeRF++ | 25.11 | 0.676 | 0.375 | 9.45 | 2.4M |
| Deep Blending | 23.70 | 0.666 | 0.318 | — | — |
| Point-Based Neural Rendering | 23.71 | 0.735 | 0.252 | — | — |
| Stable View Synthesis (SVS) | 25.33 | 0.771 | **0.211** | — | — |
| mip-NeRF với MLP lớn hơn | 26.19 | 0.748 | 0.285 | 22.71 | 9.0M |
| NeRF++ với các MLP lớn hơn | 26.39 | 0.750 | 0.293 | 19.88 | 9.0M |
| **Mip-NeRF 360 (Our Model)** | **27.69** | **0.792** | 0.237 | **6.89** | 9.9M |
| Mip-NeRF 360 w/GLO | 26.26 | 0.786 | 0.237 | 6.90 | 9.9M |

| Chỉ số | Ý nghĩa |
|---|---|
| **PSNR** (Peak Signal-to-Noise Ratio) | Đo sai số pixel theo thang decibel: `10·log₁₀(1/MSE)`. Đơn giản, nhưng không khớp tốt với cảm nhận thị giác |
| **SSIM** (Structural Similarity Index) | Đo độ tương đồng **cấu trúc** (so sánh độ sáng, độ tương phản, tương quan cục bộ) — gần cảm nhận người hơn PSNR |
| **LPIPS** (Learned Perceptual Image Patch Similarity) | Đo khoảng cách trong **không gian đặc trưng của 1 mạng CNN đã train** — được thiết kế để khớp cảm nhận người |
| **GLO** | Biến thể dùng **latent appearance embedding 4 chiều** từ NeRF-W, giúp giảm artifact do điều kiện sáng không nhất quán khi chụp. Paper ghi: vì các cảnh của họ **không có vật thể thoáng qua (transient)**, họ **không hưởng lợi từ các thành phần khác của NeRF-W** |

**Các con số chủ đạo mà paper công bố [P360, Abstract + Mục 6]:**
- **Giảm 57% mean-squared error so với mip-NeRF**, với thời gian train chỉ tăng **2.17×**.
- Các baseline mip-NeRF/NeRF++ dùng MLP lớn hơn thì cạnh tranh hơn, **nhưng chậm hơn ~3×** so với Mip-NeRF 360 và **vẫn kém chính xác hơn đáng kể**.
- Mô hình thắng Deep Blending và Point-Based Neural Rendering **trên mọi chỉ số**.
- So với **SVS**: thắng **PSNR và SSIM**, nhưng **thua LPIPS**.

**Về việc thua LPIPS — lập luận của paper [P360, Mục 6 + Phụ lục D]:** paper cho rằng điều này **có thể** do SVS được giám sát để **trực tiếp tối thiểu hóa 1 loss tri giác giống LPIPS**, trong khi Mip-NeRF 360 tối thiểu hóa loss tái tạo theo từng pixel. Họ đưa dẫn chứng ở **Figure 13**: 1 cảnh mà SVS đạt LPIPS **thấp hơn (0.396 vs 0.422)** mặc dù **PSNR và SSIM đều kém hơn** và hậu cảnh của SVS **bị mờ** rõ rệt. Họ nhận xét LPIPS *thường xuyên không nhất quán một cách rõ rệt với cảm nhận thị giác của chính họ* và dẫn công trình đã chỉ ra **các lỗ hổng (vulnerabilities) của LPIPS**.

**Các ưu thế khác mà paper nêu so với SVS/Deep Blending [P360, Mục 6]:**
1. Các mô hình đó cần **dữ liệu train ngoài (external training data)**; Mip-NeRF 360 **không cần**.
2. Các mô hình đó cần **proxy geometry do 1 gói MVS sinh ra** (và **có thể thất bại khi hình học đó sai**); Mip-NeRF 360 **không cần**.
3. Mip-NeRF 360 **tự sinh depth map cực kỳ chi tiết**; SVS và Deep Blending **không**.
4. **[P360, Phụ lục D]** bổ sung: Mip-NeRF 360 **cực kỳ gọn — chỉ ~10 triệu tham số**, trong khi SVS cần **nhiều CNN lớn + truy cập toàn bộ ảnh train** (vì nó hoạt động bằng cách trộn các ảnh train lại với nhau).

### Bảng 2 — Ablation Study (trên scene `bicycle`) **[P360, Table 2]**

| Biến thể | PSNR ↑ | SSIM ↑ | LPIPS ↓ | Thời gian (h) | # Tham số | Điều ablation này chứng minh |
|---|---|---|---|---|---|---|
| **A) Bỏ `L_prop`** | **20.49** | **0.406** | **0.573** | 6.21 | 9.0M | **Sụp đổ hoàn toàn** — proposal MLP không được giám sát gì cả. ⇒ `L_prop` là thành phần **tối quan trọng nhất** |
| **B) Bỏ `L_dist`** | 24.41 | 0.687 | 0.300 | 7.08 | 9.0M | **Chỉ số KHÔNG xấu đi** (PSNR còn cao hơn 0.04!) **nhưng sinh floaters** trong hình học (Figure 5) |
| **C) Bỏ `L_dist`, thay bằng tiêm nhiễu (σ=1) của NeRF gốc** | 24.00 | 0.655 | 0.328 | 7.08 | 9.0M | Cách của NeRF gốc **làm giảm chất lượng** và **kém hiệu quả hơn** trong việc loại floaters |
| **D) Bỏ Proposal MLP (1 MLP làm cả 2 việc)** | 24.26 | 0.682 | 0.307 | **18.89** | 8.7M | Chất lượng **không giảm**, nhưng train **chậm ~3×** ⇒ proposal MLP nhỏ **mua TỐC ĐỘ, không mua chất lượng** |
| **E) Bỏ Proposal MLP + dùng cách train của mip-NeRF** | 23.45 | 0.659 | 0.328 | 18.89 | 8.7M | **Vừa chậm hơn vừa kém hơn** ⇒ biện minh cho chiến lược giám sát `L_prop` |
| **F) NeRF MLP nhỏ (256 kênh thay vì 1024)** | 22.80 | 0.515 | 0.480 | **4.31** | 1.1M | Nhanh hơn nhưng kém hẳn ⇒ **giá trị của mô hình dung lượng cao** cho cảnh chi tiết |
| **G) Bỏ IPE hoàn toàn, dùng PE của NeRF** | 23.87 | 0.664 | 0.322 | 7.08 | 9.0M | ⇒ **giá trị của việc xây trên mip-NeRF thay vì trên NeRF** |
| **H) Bỏ phép co, thay bằng thêm tần số PE để bao cảnh** | 23.77 | 0.642 | 0.347 | 8.79 | 10.9M | Phép co **vừa tốt hơn, vừa nhanh hơn, vừa ít tham số hơn** |
| **I) Dùng phép co + lấy mẫu logarit của DONeRF** | 23.99 | 0.654 | 0.334 | 7.20 | 9.0M | Thiết kế `g(x)=1/x` + `contract` **thắng** các phép co đã công bố khác |
| **Mô hình đầy đủ** | **24.37** | **0.687** | **0.300** | 7.09 | 9.0M | — |

**Hai ablation chỉ báo cáo trong Phụ lục A (chỉ có SSIM):**

| Biến thể | SSIM | Mô hình đầy đủ | Kết luận |
|---|---|---|---|
| Bỏ đặc trưng **off-axis IPE** | 0.664 | 0.687 | Tác động ngang với việc bỏ hẳn IPE |
| Bỏ **annealing** (Eq. 18) | 0.679 | 0.687 | Tác động **dương vừa phải (modest)** |

### Bảng 3–4 — Kết quả trên 2 dataset KHÔNG phải mục tiêu thiết kế

Để đầy đủ, paper cũng đánh giá trên các dataset cũ, dùng 1 **phiên bản đơn giản hóa** của mô hình.

**Cấu hình đơn giản hóa cho Blender [P360, Phụ lục D]:** *chỉ 1 lượt lấy mẫu; **128 mẫu** cho proposal MLP; **32 mẫu** cho NeRF MLP; proposal MLP 4 lớp × 256; NeRF MLP 8 lớp × 256 (hoặc 512); **IPE axis-aligned**; **loss MSE**; và **KHÔNG có distortion regularizer**.* Lý do: bài toán này dễ hơn, nên đơn giản hóa để chạy nhanh.

**Blender dataset (vật thể synthetic nhỏ, nền trắng) [P360, Table 3]:**

| Mô hình | # kênh ẩn | PSNR ↑ | SSIM ↑ | LPIPS ↓ | Thời gian (h) | # Tham số |
|---|---|---|---|---|---|---|
| mip-NeRF | 256 | **33.09** | 0.961 | 0.043 | 2.89 | 0.61M |
| **Mip-NeRF 360** | 256 | 32.96 | 0.960 | 0.043 | **1.86** | 0.84M |
| mip-NeRF | 512 | 33.03 | **0.964** | **0.037** | 7.03 | 2.27M |
| **Mip-NeRF 360** | 512 | **33.25** | 0.962 | 0.039 | **3.42** | 3.23M |

Paper kết luận: mô hình của họ **không được thiết kế để cải thiện độ chính xác trên các cảnh này**, và thực tế độ chính xác **tương đương** mip-NeRF trên mọi chỉ số. **Nhưng** — nhờ dùng proposal network — nó **nhanh hơn đáng kể khi train**, và **mức tăng tốc tương đối này càng lớn khi dung lượng mô hình càng tăng** (1.55× ở 256 kênh → **2.06×** ở 512 kênh).

**LLFF dataset (forward-facing) [P360, Table 4]:** cấu hình như Blender nhưng **vẫn bật distortion regularizer** và **dùng Charbonnier thay MSE**.

| Mô hình | # kênh ẩn | PSNR ↑ | SSIM ↑ | LPIPS ↓ | Thời gian (h) | # Tham số |
|---|---|---|---|---|---|---|
| mip-NeRF | 256 | **26.93** | 0.830 | 0.177 | 2.48 | 0.61M |
| **Mip-NeRF 360** | 256 | 26.68 | 0.847 | 0.150 | 2.39 | 0.84M |
| mip-NeRF | 512 | **27.01** | 0.845 | 0.148 | 6.15 | 2.27M |
| **Mip-NeRF 360** | 512 | 26.86 | **0.858** | **0.128** | **3.84** | 3.23M |

Paper kết luận: **không thắng về PSNR**, nhưng **cải thiện SSIM và LPIPS** và **tăng tốc đáng kể khi NeRF MLP lớn**.

> **💡 Ý nghĩa cho đồ án:** 2 bảng này rất hữu ích cho Chương 4 (Cài đặt và thử nghiệm): chúng cho thấy **nếu đồ án thử nghiệm trên dataset Blender (vốn là dataset dễ chạy nhất), KHÔNG nên kỳ vọng Mip-NeRF 360 cho PSNR cao hơn NeRF/Mip-NeRF** — lợi ích đo được sẽ là **thời gian train**, không phải chất lượng. Để thấy được ưu thế chất lượng của Mip-NeRF 360, **bắt buộc phải thử trên cảnh 360° unbounded**.

### Kết quả trên Tanks and Temples **[P360, Phụ lục D]**

Vì dataset này có biến thiên quang học, paper phải dựng **chỉ số "đã hiệu chỉnh màu" (color corrected)**: trước khi tính mỗi chỉ số, giải 1 bài toán **bình phương tối thiểu theo từng ảnh**, khớp 1 **khai triển đa thức bậc 2** của giá trị RGB render với ảnh thật, **bỏ qua các pixel bị kẹp trần (saturated)**.

Kết quả với chỉ số đã hiệu chỉnh: Mip-NeRF 360 **hơi thắng SVS về PSNR**, nhưng **kém hơn SVS về SSIM và LPIPS**. Paper lưu ý thêm 1 quan sát thú vị: cải thiện của họ so với SVS **rõ rệt nhất ở scene `playground`** — *đây là scene test duy nhất chủ yếu gồm **nội dung tự nhiên**, còn 3 scene còn lại chủ yếu là **xe cộ lớn***. Họ **phỏng đoán (speculate)** rằng SVS có thể phù hợp hơn với các **vật thể lớn gần như phẳng từng mảnh (piecewise planar)** — hợp lý vì SVS dựa vào 1 proxy geometry bản thân là lưới phẳng từng mảnh — còn mô hình của họ phù hợp hơn với cảnh chứa **nội dung tự nhiên (cây, cỏ, hoa...)**.

---

## Hạn chế của mô hình & những điểm người biên soạn chưa chắc chắn

### Hạn chế mà chính paper nêu **[P360, Mục 6, "Limitations"]**

Paper mở đầu phần này bằng việc thừa nhận: *dù Mip-NeRF 360 vượt trội mip-NeRF và các công trình trước một cách đáng kể, **nó không hoàn hảo***. Ba hạn chế cụ thể:

1. **Bỏ sót các cấu trúc mảnh và chi tiết nhỏ.** Ví dụ paper tự chỉ ra: **nan hoa bánh xe** trong scene `bicycle` (Figure 5), và **gân lá** trong scene `stump` (Figure 7).
2. **Chất lượng tổng hợp góc nhìn có thể giảm nếu camera bị di chuyển ra xa khỏi TÂM của cảnh.** (Hệ quả trực tiếp của `contract(·)` — xem Giai đoạn 5 mục 5.1.)
3. **Vẫn cần nhiều giờ train trên accelerator**, như phần lớn các mô hình họ NeRF ⇒ **không thể train trên thiết bị (on-device)**.

### Thêm về khía cạnh "tốc độ" — một điểm dễ bị diễn giải lệch

> **⚠️ Cần cẩn trọng khi viết về tốc độ của Mip-NeRF 360 trong báo cáo.** Có 2 cách nói, cả 2 đều có cơ sở trong paper, nhưng chúng **trả lời 2 câu hỏi khác nhau**:
>
> **(a) "Mip-NeRF 360 chậm hơn mip-NeRF"** — đúng, nếu so với mip-NeRF **nguyên bản** (dung lượng nhỏ): **6.89h vs 3.17h**, tức **2.17×**. Nhưng nói thế mà không nói thêm là **so sánh không công bằng**, vì mô hình 360 có **~14× số tham số**.
>
> **(b) "Hiệu năng (Efficiency) là 1 trong 3 đóng góp chính của paper"** — cũng đúng, và dữ kiện ủng hộ rất mạnh:
> - So với **mip-NeRF cùng cỡ** (9.0M tham số): **6.89h vs 22.71h** ⇒ Mip-NeRF 360 **nhanh hơn 3.3×**.
> - So với **NeRF++ cùng cỡ** (9.0M): **6.89h vs 19.88h** ⇒ **nhanh hơn 2.9×**.
> - **Ablation D:** bỏ proposal MLP ⇒ **18.89h** thay vì 7.09h ⇒ cơ chế proposal **tăng tốc train 300%** (đúng con số paper dùng ở Introduction khi so với "NeRF in Detail").
> - **Trên Blender/LLFF, Mip-NeRF 360 NHANH HƠN mip-NeRF một cách tuyệt đối** (1.86h vs 2.89h; 3.42h vs 7.03h).
> - **[P360, Introduction]:** dung lượng mô hình tổng lớn hơn mip-NeRF **~15×** nhưng thời gian train chỉ tăng **~2×**.
>
> **Cách nói chính xác nhất:** *Mip-NeRF 360 không phải 1 phương pháp "NeRF nhanh" theo nghĩa của Instant-NGP (vẫn mất nhiều giờ, không phải vài giây/phút). Nhưng trong nội bộ họ phương pháp chất lượng cao, nó là bước tiến **rõ rệt về hiệu năng tính trên mỗi đơn vị dung lượng mô hình** — và paper đặt "Efficiency" ngang hàng với 2 đóng góp còn lại, không coi nó là nhượng bộ.*

### Những điểm người biên soạn ghi nhận là KHÔNG CHẮC CHẮN

Theo đúng yêu cầu "thà ghi rõ không chắc hơn là đoán bừa", dưới đây là danh sách đầy đủ:

| # | Điểm không chắc chắn | Mức độ & cách xử lý |
|---|---|---|
| 1 | **Chi tiết nhánh màu và view-direction của NeRF MLP** | Paper nói `d` **có** được đưa vào MLP nhưng *"lược bỏ cho đơn giản"*. **Không biết**: vị trí nối `d`, số chiều encoding của `d`, vị trí skip connection, có tách nhánh density trước khi nối `d` hay không. ⇒ Nếu báo cáo cần, **phải đọc code công bố** và ghi nguồn là code |
| 2 | **Đúng công thức IPE nào được dùng trong không gian co** | Paper viết `γ(contract(μ,Σ))` và nói dùng *"các đặc trưng tương tự (xem phụ lục)"*. Người biên soạn hiểu "tương tự" = **Eq. 1 nhưng với cơ sở off-axis P của Eq. 17 thay cho P=I**. Đây là cách đọc hợp lý nhất, **nhưng paper không viết công thức hợp nhất ra tường minh** |
| 3 | **Quy ước trục trong `sum(Pᵀ ∘ (Σ Pᵀ), 0)`** | Paper ghi `sum(·, 0)` là "tổng theo hàng". Người biên soạn hiểu ý đồ (tính chỉ các phần tử đường chéo cần thiết) nhưng **quy ước chiều cụ thể phụ thuộc cách lưu ma trận của Jax** ⇒ không nên trích chi tiết trục mà không đọc code |
| 4 | **Hệ số 1/3 trong Eq. 15** | Trích **nguyên theo paper**. Người biên soạn **chưa tự dẫn lại** bước tích phân `∫∫|u−v|` trên ô vuông sinh ra hệ số này ⇒ không diễn giải thêm |
| 5 | **Số hàng chính xác của ma trận P (Eq. 17)** | Đếm được **21 hàng** từ bản PDF đã trích xuất. Vì PDF trích xuất qua công cụ tự động, **có khả năng nhỏ bị lệch 1 hàng** ⇒ nếu cần trích đúng ma trận, **đếm lại trực tiếp trên file PDF** |
| 6 | **Nhãn [MIP-2021] vs [360-MỚI] cho một vài chi tiết** | Cụ thể: **softplus cho density** (B7) và **hệ số 1/10 ở Eq. 7**. Vì **không có paper Mip-NeRF 2021** trong thư mục, không xác minh được chi tiết nào thuộc Mip-NeRF và chi tiết nào do bản 360 thêm. ⇒ Đã ghi chú tại chỗ trong bảng |
| 7 | **Chi tiết nội bộ của Mip-NeRF (cách tính `(μ,Σ)` của nón cụt)** | Paper 360 **chỉ nói** bán kính nón do tiêu cự và kích thước pixel quyết định, **không in công thức tính `μ`, `Σ`**. ⇒ Nếu đồ án cần cài đặt lại, **phải đọc paper Mip-NeRF 2021 (arXiv:2103.13415)** — khuyến nghị bổ sung file này vào `Reference/` |
| 8 | **Lý do dùng softplus thay ReLU** | Paper **chỉ nêu dữ kiện**, không nêu lý do. Diễn giải "tránh nơ-ron density chết" là **[SUY-RA]** |
| 9 | **Lý do cần warm-up + gradient clipping** | Paper **chỉ nêu dữ kiện**. Diễn giải là **[SUY-RA]** |
| 10 | **Jacobian tường minh của `contract`** (mục 2.5) | **Hoàn toàn là [SUY-RA]**. Đúng về toán học và khớp với nhận xét của paper về Gaussian dị hướng, nhưng **paper không in nó** ⇒ nếu dùng trong báo cáo, phải ghi rõ "tự dẫn" |
| 11 | **Chứng minh phép co + s-space triệt tiêu nhau** (mục 2.7) | **[SUY-RA]**. Paper **phát biểu kết luận bằng lời** ở Figure 2 (các khoảng cách đều nhau trong vùng cam), nhưng **không chứng minh** ⇒ chứng minh ở đây là của người biên soạn |

### Vấn đề tác động xã hội mà paper tự nêu **[P360, Phụ lục E]**

Hữu ích cho phần Kết luận của đồ án, vì nó cho thấy thực hành khoa học có trách nhiệm. Paper nêu 4 rủi ro:
1. **Deep fakes:** các mô hình họ NeRF đã được tích hợp vào các cách tiếp cận mô hình sinh (generative modeling), và kỹ thuật sinh có thể bị dùng để tạo nội dung giả nhằm lừa dối. Paper lưu ý công trình của họ **không trực tiếp liên quan tới mô hình sinh** (nó nhằm **dựng lại mô hình vật lý chính xác** của 1 cảnh), nhưng **đóng góp của họ có thể hữu ích cho các cách tiếp cận sinh dựa trên NeRF**.
2. **Giám sát (surveillance):** kỹ thuật này về mặt lý thuyết có thể được dùng để dựng 1 hệ thống giám sát, và hệ thống đó có thể gây tác động xấu nếu bị dùng cẩu thả hoặc có chủ ý xấu.
3. **Việc làm:** hệ thống có thể dùng để sinh hiệu ứng thị giác (hiện là công việc thâm dụng lao động) ⇒ **có thể ảnh hưởng tiêu cực tới cơ hội việc làm của các nghệ sĩ**.
4. **Năng lượng/khí hậu:** train NeRF đòi hỏi nhiều giờ tính toán trên accelerator ⇒ tiêu thụ năng lượng, **đáng quan ngại nếu năng lượng đó được sản xuất theo cách gây hại khí hậu**. (Paper có ghi chú rằng render khi test **có thể được tăng tốc đáng kể**.)

---

## Tổng kết

Năm giai đoạn trên mô tả toàn bộ vòng đời của 1 hệ thống Mip-NeRF 360. Nếu phải cô đọng thành 1 câu: **Mip-NeRF 360 không phát minh 1 cách biểu diễn cảnh mới — nó giữ nguyên lõi vật lý của NeRF (volume rendering `Σ T_i α_i c_i`) và thay đổi 3 thứ bao quanh lõi đó:**

1. **Hệ tọa độ** mà lõi đó hoạt động trong (`contract` + s-space) — để biến 1 bài toán unbounded trở lại thành chính bài toán bounded cách đều mà NeRF gốc vốn giải tốt.
2. **Cách phân bổ tài nguyên tính toán** (proposal MLP nhỏ gọi nhiều lần + NeRF MLP lớn gọi 1 lần, nối với nhau bằng online distillation) — để có dung lượng của 1 mô hình lớn với giá của 1 mô hình trung bình.
3. **Thông tin tiên nghiệm (prior) được cài vào hàm loss** (`L_dist`) — để chọn ra nghiệm **đúng về hình học** trong cái "họ vô hạn các nghiệm cùng giải thích được ảnh input".

Điểm đáng học nhất về phương pháp luận cho 1 đồ án: **3 thay đổi này không độc lập mà được đồng thiết kế**. `contract` chỉ hiệu quả vì có s-space triệt tiêu nó; s-space cũng chính là hệ quy chiếu đúng để định nghĩa `L_dist`; `contract` sinh ra Gaussian dị hướng nên **buộc** phải nâng cấp IPE thành off-axis; và `L_prop` chỉ khả thi vì volume rendering đảm bảo `Σw ≤ 1`, biến `w` thành 1 đại lượng kiểu histogram so sánh được. Rút 1 mắt ra là các mắt khác yếu đi — đúng như bảng ablation cho thấy.

---

## Tài liệu liên quan trong thư mục đồ án

- **`Doan/pipeline_NeRF.md`** — tài liệu pipeline NeRF gốc, 5 giai đoạn tương ứng. **Đọc cùng file này** để thấy rõ đối chiếu; đặc biệt Giai đoạn 1 (7 bước COLMAP/SfM, không lặp lại ở đây) và Giai đoạn 3 (chi tiết kiến trúc MLP 8×256 + volume rendering, là nền để hiểu Giai đoạn 3 ở đây).
- **`Doan/nerf_cai_tien.md`** — khảo sát ngắn 6 biến thể NeRF (dùng cho Chương 2: Các công trình nghiên cứu liên quan). **Mục "Mip-NeRF 360" và "Mip-NeRF" trong file đó được viết từ kiến thức tổng quát, CHƯA verify với paper** — xem phần "Những điểm cần sửa trong `nerf_cai_tien.md`" ở ngay dưới.
- **`Doan/lythuyet.md`**, **`Doan/tomtat_paper_NeRF.md`** — ghi chú lý thuyết và tóm tắt paper NeRF gốc.
- **`Doan/03-Reference/Selected/2022 Mip-NeRF 360 - Unbounded Anti-Aliased Neural Radiance Fields.pdf`** — paper gốc đã dùng để verify toàn bộ tài liệu này.
- **Khuyến nghị bổ sung vào `Reference/`:** paper **Mip-NeRF (Barron et al., ICCV 2021, arXiv:2103.13415)** — cần thiết để verify các phần đánh nhãn **[MIP-NỀN]** (công thức tính `(μ,Σ)` của nón cụt, chi tiết kiến trúc MLP đa tỉ lệ, cơ chế axis-aligned IPE).

### Những điểm cần sửa trong `nerf_cai_tien.md` (phát hiện khi đối chiếu paper thật)

| # | Chỗ cần sửa | Bản sơ bộ nói | Paper thật nói |
|---|---|---|---|
| 1 | Mục Mip-NeRF 360 §2 | *"điểm nào nằm trong bán kính 1 **từ camera**"* | Bán kính đo **từ GỐC TỌA ĐỘ WORLD** (= tâm đám camera, sau bước PCA + rescale ở Phụ lục D). **Không phải từ camera.** Đây là sai sót về hình học, làm hiểu lệch toàn bộ cơ chế |
| 2 | Mục Mip-NeRF 360 §2 | Chỉ nêu `contract(x)` cho **điểm** | **Thiếu đóng góp cốt lõi**: Eq. 8–9, áp phép co lên **Gaussian (μ,Σ)** theo kiểu **Extended Kalman filter** (`J Σ Jᵀ`). Paper nói thẳng rằng việc tham số hóa **điểm** đã có ở công trình trước và **không giải quyết** được ngữ cảnh mip-NeRF |
| 3 | Mục Mip-NeRF 360 §3 | *"lấy mẫu **đều trong không gian đã contract**"* | Lấy mẫu đều trong **s-space** định nghĩa bởi **Eq. 11 với `g(x)=1/x`** (tuyến tính theo disparity). Đây là 1 cơ chế **riêng biệt**, được **đồng thiết kế** để triệt tiêu `contract`, không phải "lấy mẫu trong không gian co". Và `t_f = ∞` trở nên hợp lệ — mất hẳn ý này |
| 4 | Mục Mip-NeRF 360 §6 (Hạn chế) | *"Không tối ưu về tốc độ train — vẫn chậm"* | **Gây hiểu lệch.** "Efficiency" là **1 trong 3 đóng góp chính** của paper. So cùng số tham số, Mip-NeRF 360 **nhanh hơn 3.3× mip-NeRF** và **2.9× NeRF++**; cơ chế proposal **tăng tốc train 300%** (Ablation D); trên Blender/LLFF nó **nhanh hơn mip-NeRF tuyệt đối** |
| 5 | Mục Mip-NeRF 360 §4 | Mô tả distortion loss **chỉ bằng lời**, và chỉ nói chống **floaters** | Thiếu: **Eq. 14–15 tường minh**; nó tính trên **`s` chứ không trên `t`** (và paper nêu rõ lý do); nó cũng chống **"background collapse"** (artifact thứ 2, paper đặt tên riêng); và **phát hiện quan trọng — Ablation B: bỏ `L_dist` KHÔNG làm PSNR/SSIM/LPIPS xấu đi** (PSNR còn cao hơn: 24.41 vs 24.37), chỉ sinh floaters thấy được ở depth map. ⇒ **Không được viết "`L_dist` cải thiện PSNR"** |
| 6 | Mục Mip-NeRF 360 §3 + §5 | *"Proposal Network — 1 mạng nhỏ... cùng tinh thần với mạng coarse"* | Thiếu các dữ kiện định lượng: **2 lượt proposal × 64 mẫu, NeRF MLP chỉ 32 mẫu**; prop **4 lớp × 256** vs NeRF **8 lớp × 1024**; **stop-gradient** (NeRF dẫn, prop theo) và lý do; `L_prop` là **chặn trên 1 phía bất đối xứng** (Eq. 12–13) **chứ không phải** độ đo khoảng cách histogram đối xứng |
| 7 | Bảng so sánh §5, dòng "Chống aliasing" | *"Có (**kế thừa** IPE từ Mip-NeRF)"* | Chỉ **nửa đúng**. Bản 360 **nâng cấp IPE thành off-axis IPE** (Eq. 17, cơ sở 21 đỉnh icosahedron) — 1 **thay đổi MỚI, bắt buộc** vì `contract` sinh Gaussian cực kỳ dị hướng. Ablation: bỏ off-axis ⇒ SSIM 0.687→0.664 |
| 8 | Lưu ý đầu mục Mip-NeRF 360 | *"Công thức `contract(x)` ... **không chắc khớp 100%** hệ số chính xác trong paper"* | **Công thức trong bản sơ bộ KHỚP CHÍNH XÁC với Eq. 10.** Có thể **xóa lời cảnh báo này** và nâng cấp thành trích dẫn chính thức "Eq. 10, arXiv:2111.12077" |
| 9 | Mục Mip-NeRF §4 | *"Mip-NeRF **không cần kiến trúc 2 mạng riêng** nữa — chỉ cần 1 mạng duy nhất, áp dụng lặp lại nhiều lần"* | **Khớp với paper 360** (Figure 3 mô tả mip-NeRF là *"một MLP đa tỉ lệ được truy vấn lặp lại"*). **Giữ nguyên.** Nhưng **nên bổ sung**: mip-NeRF vẫn **giám sát ở MỌI tỉ lệ** bằng loss ảnh (Eq. 7, với hệ số **1/10** cho nhánh coarse) — và **chính điều này** là thứ Mip-NeRF 360 loại bỏ |
| 10 | Mục Mip-NeRF, các con số benchmark | Ghi là **"ước lượng, cần verify"** | Có thể thay bằng số thật **từ Table 1 của paper 360** (đo trên dataset 360, TPU v2 32 nhân): mip-NeRF **PSNR 24.04 / SSIM 0.616 / LPIPS 0.441 / 3.17h / 0.7M tham số**. **Lưu ý:** đây là số do **paper 360** đo, không phải số trong paper Mip-NeRF 2021 |

---

*Tài liệu được biên soạn bằng cách đọc toàn văn arXiv:2111.12077v3 (18 trang, gồm phần chính Mục 1–7 và Phụ lục A–E). Mọi công thức, siêu tham số và số liệu đã được đối chiếu trực tiếp với bản PDF. Các phần diễn giải, ví dụ số, chứng minh bổ trợ và bảng đối chiếu là nội dung gốc của người biên soạn, viết lại hoàn toàn bằng lời và cấu trúc riêng.*
