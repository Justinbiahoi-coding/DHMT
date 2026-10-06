# Danh mục tài liệu tham khảo

16 paper, phân theo vai trò trong báo cáo. Tất cả tải từ nguồn chính thức (arXiv, openaccess.thecvf.com, trang tác giả).

**Quy ước đặt tên:** `[năm công bố gốc] [tên đầy đủ paper].pdf` — năm là năm bản v1/năm hội nghị, không phải năm revision mới nhất.

---

## `Selected/` — Paper gốc cho Chương 3 (Phương pháp)

Ba paper cùng một dòng kế thừa, trình bày theo đúng mạch này: NeRF → thêm chống răng cưa → thêm xử lý cảnh vô hạn.

| Năm | Paper | Tác giả | Venue |
|---|---|---|---|
| 2020 | NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis | Mildenhall, Srinivasan, Tancik, Barron, Ramamoorthi, Ng | ECCV 2020 |
| 2021 | Mip-NeRF: A Multiscale Representation for Anti-Aliasing Neural Radiance Fields | Barron, Mildenhall, Tancik, Hedman, Martin-Brualla, Srinivasan | ICCV 2021 |
| 2022 | **Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields** ← phương pháp chính | Barron, Mildenhall, Verbin, Srinivasan, Hedman | CVPR 2022 |

## `Survey/` — Cho Chương 2 (Khảo sát) và Chương 5 (Hướng phát triển)

| Năm | Paper | Venue | Ghi chú |
|---|---|---|---|
| 2022 | Advances in Neural Rendering | **Eurographics STAR** (Computer Graphics Forum) | Survey chính thức, 18 tác giả từ MPI/Google/MIT/Stanford/TUM — có cả tác giả NeRF gốc |
| 2022 | NeRF: Neural Radiance Field in 3D Vision, A Comprehensive Review | Computational Visual Media | Đã được chấp nhận (2025), DOI chưa cấp. Survey chuyên sâu riêng về NeRF, có taxonomy |
| 2024 | A Survey on 3D Gaussian Splatting | preprint (arXiv:2401.03890) | Survey hệ thống đầu tiên về 3DGS |

## `Foundation/` — Nền tảng cho Chương 1-2

| Năm | Paper | Vai trò trong đồ án |
|---|---|---|
| 1995 | Optical Models for Direct Volume Rendering (Nelson Max) | Nguồn công thức volume rendering + quy tắc cầu phương mà NeRF trích dẫn |
| 2016 | Structure-from-Motion Revisited (Schönberger, Frahm) | Paper gốc của **COLMAP** — công cụ ước lượng camera pose dùng trong toàn bộ pipeline |
| 2019 | Local Light Field Fusion (Mildenhall et al.) | Baseline NeRF gốc so sánh + nguồn bộ dữ liệu LLFF (forward-facing) |

## `Related/` — Các hướng cải tiến khác, cho Chương 2 (bảng so sánh) và Chương 5

| Năm | Paper | Hướng tiếp cận |
|---|---|---|
| 2020 | NeRF++: Analyzing and Improving Neural Radiance Fields | Cảnh unbounded — tách 2 mạng trong/ngoài khối cầu (trước Mip-NeRF 360) |
| 2022 | Instant Neural Graphics Primitives with a Multiresolution Hash Encoding | Tăng tốc — hash encoding đa độ phân giải (SIGGRAPH 2022) |
| 2022 | Plenoxels: Radiance Fields without Neural Networks | Bỏ hẳn mạng nơ-ron — voxel grid + Spherical Harmonics (CVPR 2022) |
| 2022 | TensoRF: Tensorial Radiance Fields | Tăng tốc — phân rã tensor (ECCV 2022) |
| 2023 | Zip-NeRF: Anti-Aliased Grid-Based Neural Radiance Fields | Gộp Mip-NeRF 360 + hash grid (ICCV 2023) — liên quan trực tiếp phương pháp chính |
| 2023 | 3D Gaussian Splatting for Real-Time Radiance Field Rendering | Bỏ ray-marching, dùng rasterization — render real-time (SIGGRAPH 2023) |
| 2024 | Mip-Splatting: Alias-free 3D Gaussian Splatting | Mang chống răng cưa của dòng Mip-NeRF sang 3DGS (CVPR 2024) |

---

## Gợi ý dùng cho từng chương

| Chương | Tài liệu chính |
|---|---|
| 1. Giới thiệu | `Foundation/` (phát biểu bài toán, bối cảnh) + `Selected/2020 NeRF` |
| 2. Công trình liên quan | `Survey/` (khung tổng quan) + `Related/` (dựng dòng phát triển, bảng so sánh) |
| 3. Phương pháp | `Selected/` — 3 paper theo thứ tự 2020 → 2021 → 2022 |
| 4. Cài đặt & thử nghiệm | `Foundation/2016 COLMAP` (pipeline tiền xử lý) + `Selected/2022 Mip-NeRF 360` (siêu tham số, metric) |
| 5. Kết luận & hướng phát triển | `Related/2023 Zip-NeRF`, `Related/2023 3D Gaussian Splatting`, `Survey/2024 A Survey on 3DGS` |
