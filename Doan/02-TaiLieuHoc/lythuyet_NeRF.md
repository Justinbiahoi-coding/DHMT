# Lý thuyết NeRF (Neural Radiance Fields) — Ghi chú học

## Phần I: Bài toán NeRF giải quyết là gì

Bạn chụp nhiều tấm ảnh 2D (ví dụ 20-100 tấm) của cùng một cảnh/vật thể, mỗi tấm từ một góc khác nhau (đi vòng quanh vật thể, chụp mỗi góc một tấm).

**Câu hỏi đặt ra:** từ những tấm ảnh đó, làm sao tạo ra một ảnh mới, chụp từ một góc mà bạn chưa hề chụp bao giờ?

Bài toán này gọi là **novel view synthesis** (tổng hợp góc nhìn mới). Ví dụ: có ảnh chụp một cái ly từ trước mặt, từ trái, từ phải — nhưng chưa chụp từ trên xuống. NeRF "tưởng tượng" ra ảnh nhìn từ trên xuống đó, chân thực về ánh sáng, bóng đổ, độ phản chiếu.

- **Input:** tập ảnh 2D của cảnh, mỗi ảnh kèm thông tin "ảnh này chụp từ vị trí/góc nào" (camera pose).
- **Output:** một mô hình biểu diễn cảnh đó, từ đó render ra ảnh ở bất kỳ góc nào mong muốn.

**Khác biệt cốt lõi so với đồ họa 3D truyền thống:** NeRF không lưu cảnh dưới dạng mesh (lưới tam giác) hay point cloud. Nó lưu cảnh bên trong **trọng số của một mạng nơ-ron** — cảnh 3D trở thành một hàm số toán học mà mạng học được, chứ không phải một cấu trúc dữ liệu hình học tường minh.

## Phần II: NeRF "nhìn" không gian bằng cách nào — khái niệm Ray

Với mỗi camera pose đã biết, với mỗi **pixel** trên ảnh, ta vẽ được một tia thẳng (**ray**) đi từ tâm camera, xuyên qua đúng pixel đó, đâm sâu vào không gian 3D của cảnh.

Trên tia đó, lấy ra nhiều **điểm mẫu** rải rác dọc theo tia (ví dụ 64-128 điểm). Mỗi điểm mẫu mang:

- **Tọa độ vị trí (x, y, z)** — điểm này nằm ở đâu trong không gian 3D.
- **Hướng tia (θ, φ)** (vector hướng) — cùng một điểm vật lý, nhìn từ hướng khác nhau có thể phản chiếu ánh sáng khác nhau (ví dụ bề mặt kim loại bóng, mặt nước).

### Công thức tia r(t) = o + t·d — giải thích từng đại lượng + vì sao có dạng này

**Chú thích ký hiệu:**

| Ký hiệu | Tên gọi | Ý nghĩa | Kiểu dữ liệu |
|---|---|---|---|
| r | tia (ray) | tên cả đường thẳng đang xét | hàm số, nhận t → trả về 1 điểm |
| r(t) | điểm trên tia tại tham số t | tọa độ 3D cụ thể (x,y,z) ứng với t đó | vector 3 chiều |
| o | gốc tia (origin) | điểm xuất phát — chính là tâm camera trong hệ world | vector 3 chiều, cố định (không đổi theo t) |
| t | tham số | số thực bất kỳ, điều khiển "đi xa bao nhiêu" dọc tia từ gốc o | số thực (scalar) |
| d | vector hướng (direction) | hướng tia — tính từ pixel (u,v)+pose+intrinsics (Phần V) | vector 3 chiều, cố định (không đổi theo t) |
| t·d | phép nhân vô hướng-vector | nhân t với từng thành phần d → vector cùng hướng d, dài gấp t lần | vector 3 chiều |

**Đọc công thức:** "điểm trên tia tại t" = "xuất phát từ tâm camera" **cộng với** "đi theo hướng d, xa thêm t đơn vị". Với o,d cố định, t=0 → r(0)=o (đúng tại gốc); t tăng dần → điểm đi xa dần theo đúng hướng d, không đổi hướng.

**Vì sao có dạng công thức này — xuất phát từ đâu:**

1. *Ý tưởng gốc — "đi theo 1 hướng, xa dần":* đứng tại o, muốn đi theo hướng d. "Đi 1 bước" = cộng thêm vector d vào vị trí: `o+d`. "Đi 2 bước" = `o+d+d=o+2d`. "Đi 3 bước" = `o+3d`. Đây chỉ là phép cộng vector lặp lại.

2. *Tổng quát hóa từ số bước nguyên sang số thực bất kỳ:* đại số tuyến tính cho phép nhân vector với **bất kỳ số thực nào** (phép nhân vô hướng — scalar multiplication, 1 phép toán nền tảng của không gian vector): `t·d` = vector d với độ dài nhân lên t lần (t>1: dài ra; 0<t<1: ngắn lại; t<0: đổi chiều ngược). → "đi t bước" (t là số thực bất kỳ, kể cả thập phân/âm) theo hướng d từ o: **r(t)=o+t·d**. Đây là cách tự nhiên nhất diễn tả "từ o, theo hướng d, xa bao nhiêu tùy t" bằng ngôn ngữ vector.

3. *Chứng minh công thức này thực sự vạch ra 1 đường thẳng (không phải định nghĩa suông):* lấy 2 điểm bất kỳ trên tập hợp này, ứng t₁,t₂. Tính vector nối 2 điểm:
   ```
   r(t₂)−r(t₁) = (o+t₂d)−(o+t₁d) = (t₂−t₁)·d
   ```
   Vector nối **bất kỳ 2 điểm nào** trên tập hợp luôn là 1 bội số của d (chỉ khác hệ số t₂−t₁) — luôn cùng phương với d, không bao giờ lệch hướng. Đây chính xác là định nghĩa toán học của **thẳng hàng (collinear)**: vector nối mọi cặp điểm cùng phương 1 vector cố định ⟺ tập hợp nằm trên đúng 1 đường thẳng. Vậy r(t)=o+t·d được **chứng minh** vạch ra đúng 1 đường thẳng, nhờ tính chất đại số của phép nhân vô hướng + cộng vector.

   *Kiểm chứng bằng số (o=(0,0,5), d=(0.125,0.125,-1), t₁=2,t₂=5):* r(2)=(0.25,0.25,3), r(5)=(0.625,0.625,0) → r(5)−r(2)=(0.375,0.375,−3). Và (t₂−t₁)·d = 3·(0.125,0.125,−1) = (0.375,0.375,−3) — khớp chính xác.

**Vì sao cần công thức này (mục đích thực dụng):** pixel (u,v) chỉ cho biết 1 hướng (d) — không cho biết điểm 3D cụ thể nào (1 pixel ứng với cả 1 đường thẳng vô hạn điểm). r(t) là cách sinh ra hàng loạt điểm 3D cụ thể dọc đúng hướng d đó (thay t khác nhau) — chính là các điểm mẫu đưa vào mạng nơ-ron F(x,y,z,θ,φ)→(r,g,b,σ).

→ NeRF nhận **input 5 chiều**: (x, y, z, θ, φ) — 3 chiều vị trí + 2 chiều hướng nhìn.

**Output** của mạng nơ-ron tại mỗi điểm mẫu là 4 số:

- **Màu (r, g, b)**
- **Density σ** (độ "đặc") — càng lớn thì càng chắc là bề mặt vật chất; σ = 0 nghĩa là điểm nằm trong khoảng không, không có gì.

Về bản chất, mạng nơ-ron của NeRF chỉ là một hàm:

```
F(x, y, z, θ, φ) → (r, g, b, σ)
```

Học hàm này chính là học toàn bộ hình dạng + màu sắc của cảnh.

### Hàm F là gì, chi tiết — bên trong nó không phải công thức toán viết tay

**F không phải 1 công thức đóng (closed-form) kiểu y=ax+b** — nó là cách viết gọn cho "đưa input qua mạng nơ-ron, mạng tính toán qua nhiều lớp, cho ra output" (kiến trúc 8 lớp cụ thể đã vẽ ở Phần VIII bên dưới). Không có công thức ngắn gọn nào viết ra được "F(x,y,z,θ,φ) = ..." bằng vài phép toán — F tồn tại dưới dạng **hàng trăm nghìn trọng số** bên trong mạng, chỉ tính được bằng cách chạy qua từng lớp.

**Vì sao gọi là "radiance field" (trường bức xạ):** trong vật lý, 1 "trường" (field) là 1 hàm gán 1 giá trị cho **mọi điểm** trong không gian (ví dụ trường nhiệt độ: mỗi điểm trong phòng có 1 nhiệt độ). F gán (màu, density) cho **mọi điểm (x,y,z)** kết hợp **mọi hướng nhìn (θ,φ)** trong không gian cảnh — tại mỗi điểm, theo mỗi hướng, cảnh "phát ra" ánh sáng màu gì. Đó là lý do NeRF = **Ne**ural **R**adiance **F**ield.

**Input/Output của F, nhắc gọn:**
- (x,y,z): tọa độ 1 điểm mẫu lấy trên tia (công thức r(t) ở trên) — trong hệ tọa độ world (Phần III).
- (θ,φ): hướng của tia đó — thực tế code thường biểu diễn bằng vector đơn vị 3 chiều **d** (đã dùng trong r(t)=o+t·d) thay vì 2 góc, 2 cách tương đương về thông tin.
- (r,g,b): màu tại điểm đó, nhìn theo đúng hướng đó.
- σ: density tại điểm đó — không phụ thuộc hướng nhìn (lý do ở Phần VIII: hình dạng vật lý không đổi theo góc nhìn).

**Vì sao F phải "học" chứ không viết công thức tay:** không ai biết trước "cái ly ở tọa độ nào, màu gì" bằng công thức có sẵn — đó chính là thứ **cần tìm ra** từ dữ liệu ảnh. F được biểu diễn bằng 1 mạng nơ-ron (MLP) **đủ linh hoạt** — về mặt lý thuyết, mạng nơ-ron là **universal function approximator** (bộ xấp xỉ hàm phổ quát): 1 MLP đủ lớn có thể xấp xỉ **bất kỳ hàm liên tục nào** với sai số nhỏ tùy ý (định lý toán học đã chứng minh, không phải giả định). Nhờ tính chất này, không cần biết trước "công thức đúng" của cảnh — chỉ cần chọn kiến trúc mạng đủ lớn (8 lớp, 256 kênh — Phần VIII), rồi dùng volume rendering + loss MSE + gradient descent (Phần VII) để **chỉnh dần** hàng trăm nghìn trọng số cho tới khi F khớp với dữ liệu ảnh quan sát được.

**Lưu ý — mọi điểm trên cùng 1 tia có chung hướng (θ,φ):** nhìn công thức tia r(t)=o+t·d, chỉ có t thay đổi giữa các điểm mẫu, còn d (hướng) cố định cho cả tia. Nên N điểm mẫu trên 1 tia có (x,y,z) khác nhau nhưng (θ,φ) giống hệt nhau — hợp lý vì đó là hướng nhìn của cùng 1 pixel, chỉ "quét" xa dần dọc hướng đó. Pixel khác thì mới có d khác.

**"Không gian 3D" ở đây là gì, cụ thể:** là hệ tọa độ world thật (Phần III) chứa toàn bộ cảnh/vật thể + khoảng không khí xung quanh (thường giới hạn lại thành 1 bounding box/sphere vừa đủ chứa vật thể). Mỗi điểm (x,y,z) lấy trên tia là 1 tọa độ thật trong không gian đó — có thể rơi vào bề mặt vật thể (σ cao) hoặc khoảng không (σ≈0). Vì mọi camera (dù chụp từ góc khác nhau) dùng chung 1 hệ tọa độ world (nhờ COLMAP), các tia từ nhiều ảnh khác nhau xuyên qua cùng 1 điểm vật lý sẽ cho ra cùng (x,y,z) — điều kiện để mạng học ra 1 hàm nhất quán cho toàn cảnh. Đây cũng là lý do pose sai dù nhỏ sẽ làm hình học học ra bị nhòe/lệch (các tia không giao đúng chỗ nữa).

**"Không gian" đó lấy/lưu ở đâu khi chạy code — không có gì lưu sẵn cả:** trên máy chỉ có file ảnh + file pose (ma trận số, ví dụ `poses_bounds.npy`). Không có file/voxel/point-cloud nào lưu "không gian 3D" trọn vẹn. Mỗi bước train: đọc ảnh+pose (mảng số) → tính d, rồi r(t) → sinh ra N điểm (x,y,z) **tạm thời trong RAM/VRAM** (thuần phép cộng/nhân) → đưa vào mạng → tính (r,g,b,σ) → volume rendering → dùng xong, các điểm đó bị xóa, batch sau tính lại từ đầu. Thứ tồn tại lâu dài sau khi train là **trọng số mạng nơ-ron** (vài MB) — bản "nén" của toàn bộ không gian, hỏi lại (query) bất kỳ lúc nào cũng được. Đây gọi là **implicit representation** (biểu diễn ẩn), khác hẳn mesh/voxel/point-cloud là **explicit representation** (lưu sẵn từng điểm/mặt tường minh). Chỉ khi cần xuất mesh (.obj) để xem ngoài (Blender...) mới quét 1 lưới điểm dày đặc (vd 256³) qua mạng 1 lần rồi dùng Marching Cubes dựng mặt — đây là lúc duy nhất "không gian" được vật chất hóa thành dữ liệu thật.

## Phần III: Vì sao cần biết Camera Pose

Khi train, mạng cần biết chính xác tia nào đi qua điểm nào trong không gian, để biết tia đó tương ứng với pixel nào trên ảnh thật. Không biết ảnh chụp từ đâu/hướng nào → không tính được tia → không có gì để so sánh "màu mạng dự đoán" với "màu pixel thật" lúc train.

### Camera pose gồm những con số nào

Pose = vị trí + hướng nhìn của camera, biểu diễn trong hệ tọa độ **world** — một hệ trục x,y,z dùng chung cho toàn cảnh, không đổi giữa các ảnh. Gồm 2 thành phần, gọi là **extrinsic matrix**:

- **R** — ma trận xoay 3×3: gồm 3 vector cột, mỗi cột là 1 hướng trục của camera trong hệ world (ví dụ cột 1 = hướng "phải", cột 2 = hướng "lên", cột 3 = hướng "sau"/"trước" tùy quy ước).
- **C** — tọa độ 3D tâm camera trong hệ world. Ví dụ C = (0,0,5).

### R là gì, giải thích từ gốc — vấn đề cần giải quyết

Camera có thể xoay theo bất kỳ hướng nào trong không gian (chĩa thẳng, nghiêng, ngửa, úp...). **R là con số mô tả "camera đang xoay/chĩa theo hướng nào"** tại thời điểm chụp.

**Tác dụng thực sự của R — nhân với 1 vector sẽ XOAY vector đó.** Ví dụ đơn giản trong 2D trước (xoay góc θ):

```
R_2D = [ cosθ  -sinθ ]
       [ sinθ   cosθ ]
```

Lấy vector (1,0) (mũi tên chỉ phải) nhân R_2D: `R_2D·(1,0) = (cosθ,sinθ)`. Với θ=90°: ra (0,1) — mũi tên giờ chỉ thẳng lên. Vector (1,0) đã bị **xoay 90°** thành (0,1). Đây chính là tác dụng ma trận xoay: nhân với vector → ra vector đó sau khi đã xoay đi. R trong camera (3×3) làm đúng việc này nhưng trong không gian 3 chiều.

**Áp dụng vào camera:** hình dung camera như 1 hộp có 3 mũi tên gắn chết vào hộp — 1 chỉ sang phải hộp, 1 chỉ lên trên hộp, 1 chỉ ra sau hộp. Xoay hộp kiểu gì, 3 mũi tên vẫn gắn chặt, xoay theo. **R chính là bảng ghi "3 mũi tên đó hiện chỉ về hướng nào, đo trong hệ world cố định"** — mỗi cột của R là 1 trong 3 mũi tên đó, viết dưới dạng tọa độ (x,y,z) trong hệ world. Camera không xoay gì → R=ma trận đơn vị (cột 1=(1,0,0), cột 2=(0,1,0), cột 3=(0,0,1)). Camera xoay → các cột đổi thành vector khác, nhưng luôn vuông góc nhau, dài=1.

**Tác dụng thực dụng — dùng ở đâu trong pipeline:** Bước 2 công thức pixel→ray (Phần V): `d_world = R·d_cam`. d_cam là hướng tia tính theo hệ trục riêng của camera (giả sử không xoay); nhưng camera thực tế có xoay (ghi trong R) — nên hướng đó nhìn từ hệ world chung phải xoay theo đúng R mới ra hướng thật. `R·d_cam` = xoay d_cam theo đúng góc camera đang xoay → ra d_world, hướng tia thật trong không gian.

**Tóm gọn:** R là công cụ chuyển đổi "hướng đo theo kiểu riêng của camera" thành "hướng đo theo hệ chung của cả cảnh", bằng phép xoay — không phải con số trừu tượng khó hiểu.

Ghép lại thành ma trận 4×4 (camera-to-world matrix):

```
[ R11 R12 R13 | Cx ]
[ R21 R22 R23 | Cy ]
[ R31 R32 R33 | Cz ]
[  0   0   0  |  1 ]
```

Mỗi ảnh input có đúng 1 ma trận như vậy đi kèm.

**Lưu ý — vì sao R chỉ cần "phải, lên, sau" mà không cần thêm "trái, xuống, trước":**
Một trục (axis) là một đường thẳng, đã tự động bao gồm 2 hướng ngược nhau. "Trái" = -(cột "phải"), "xuống" = -(cột "lên"), "trước" = -(cột "sau") — chỉ là lấy dấu âm của vector đã có, không phải hướng độc lập cần thêm cột. Vì vậy 3 vector cột (3×3 = 9 số, thực chất chỉ 3 bậc tự do vì các cột phải vuông góc và có độ dài 1) là đủ để mô tả toàn bộ hướng xoay trong không gian 3 chiều.

**Gốc tọa độ (origin) của hệ world là gì:**
Không có gốc tọa độ tuyệt đối có sẵn trong tự nhiên — đây là quy ước do COLMAP tự chọn khi dựng lại cảnh (thường đặt gốc trùng camera đầu tiên, hoặc gần trọng tâm đám mây điểm 3D thu được). SfM chỉ dựng lại được hình dạng **tương đối** giữa các camera/điểm 3D, không biết tỉ lệ thật (mét/cm) trừ khi có tham chiếu thêm (GPS - Global Positioning System, hệ định vị toàn cầu; hoặc thước đo thật). Nhiều pipeline NeRF (LLFF, Blender dataset) có bước **normalize** sau COLMAP: dịch + co giãn toàn bộ pose để cảnh nằm gọn quanh gốc (0,0,0), cho dễ train.

### Pose lấy từ đâu ra — COLMAP / Structure-from-Motion (SfM) chi tiết

**SfM là gì — trực giác:** Structure from Motion = khôi phục cấu trúc 3D (Structure) của cảnh từ sự chuyển động (Motion) của camera qua nhiều ảnh — nhiều ảnh chụp từ các vị trí khác nhau, suy ngược ra hình dạng 3D + vị trí từng camera. Ví von: giống con người nghiêng đầu qua trái-phải, vật gần dịch chuyển nhiều trong tầm nhìn hơn vật xa (hiệu ứng **parallax**/thị sai) — não dùng chênh lệch đó cảm nhận độ sâu; SfM làm đúng việc này bằng toán học với nhiều ảnh.

**COLMAP là gì:** phần mềm mã nguồn mở implement toàn bộ pipeline SfM. Input: thư mục ảnh. Output: pose từng camera (R,C,K) + đám mây điểm 3D thưa.

**Bước 1 — Feature Detection (SIFT - Scale-Invariant Feature Transform, "phép biến đổi đặc trưng bất biến tỉ lệ"):** làm mờ ảnh gốc ở nhiều mức độ (Gaussian blur tăng dần) tạo "scale-space", lấy hiệu giữa các ảnh mờ liên tiếp (Difference-of-Gaussian, viết tắt **DoG**) tìm các điểm cực trị cục bộ (sáng/tối nổi bật hơn hẳn vùng lân cận, xuyên suốt nhiều mức mờ) → đó là **keypoint**. Mỗi keypoint được gán 1 **descriptor** — vector 128 số, mô tả hướng+độ mạnh gradient sáng-tối xung quanh (chia lưới 4×4 ô, mỗi ô 8 hướng → 4×4×8=128). Tính chất quan trọng: 2 điểm là cùng 1 vị trí vật lý thật (dù chụp góc khác) sẽ có descriptor gần giống nhau (khoảng cách Euclid nhỏ). Mỗi ảnh có vài trăm–nghìn keypoint.

*Thuật toán SIFT chi tiết:*
- **Scale-space:** làm mờ Gaussian tăng dần σ tạo 1 "octave" (chồng ảnh mờ dần cùng độ phân giải), rồi downsample 1/2 tạo octave tiếp theo (thường 4-5 octave) — để tìm điểm ổn định ở nhiều tỉ lệ.

  *Vì sao nhất định dùng Gaussian blur:* theo lý thuyết scale-space (Witkin 1983, Koenderink 1984), Gaussian là kernel làm mờ **duy nhất** thỏa "tiêu chí không sinh thêm cấu trúc mới" — tăng σ chỉ làm đặc trưng biến mất/hợp nhất, không bao giờ sinh cực trị giả. Kernel khác (box blur...) có thể tạo cực trị không tương ứng cấu trúc thật, phá logic "tìm đặc trưng ổn định qua nhiều tỉ lệ".

  *Vì sao 4-5 octave:* mỗi octave (sau downsample 1/2) phủ dải kích thước vật thể gấp đôi octave trước. Vật thể trong ảnh thật có thể chênh kích thước rất nhiều (gần/xa camera) — 4-5 octave đã phủ dải **16-32 lần**, đủ cho đa số ảnh thực tế mà chi phí tính toán vẫn ổn định (mỗi octave sau nhỏ hơn hẳn nhờ downsample).

- **Difference of Gaussians:** hiệu 2 ảnh mờ liền kề trong cùng octave — xấp xỉ rẻ tiền của toán tử Laplacian of Gaussian.
- **Tìm cực trị cục bộ:** mỗi pixel trong ảnh DoG so với 26 pixel lân cận (8 cùng mức + 9 mức trên + 9 mức dưới) — lớn nhất/nhỏ nhất trong 26 thì là ứng viên keypoint.

  *Vì sao đúng 26 (không chỉ so trong 1 ảnh):* mục tiêu là tìm điểm ổn định qua nhiều tỉ lệ (scale), không chỉ ổn định trong 1 ảnh — nếu chỉ so 8 hàng xóm cùng mức, dễ bắt nhầm nhiễu/đốm chỉ nổi bật tình cờ ở đúng 1 mức mờ. So thêm với 3×3=9 pixel ở mức mờ trên và 9 pixel ở mức mờ dưới (tổng khối 3×3×3, trừ tâm = 26) đảm bảo điểm đó là cực trị thật trong không gian 3 chiều (x,y,scale) — chính là gốc của tính "scale-invariant".

- **Tinh chỉnh & lọc:** nội suy bậc 2 tìm vị trí cực trị chính xác dưới-pixel; loại điểm tương phản thấp; loại điểm nằm trên cạnh (dùng ma trận Hessian 2×2, tỉ lệ 2 trị riêng quá lệch → là cạnh, không ổn định, loại).

  *Nội suy bậc 2 (subpixel):* khai triển Taylor bậc 2 của D quanh pixel ứng viên: `D(x)≈D(x₀)+(∂D/∂x)ᵀΔx+½ΔxᵀHΔx`. Đạo hàm theo Δx, cho=0, giải: `Δx̂ = -H⁻¹·(∂D/∂x)` — độ lệch (có thể là số thập phân) từ pixel nguyên tới cực trị thật. Nếu |Δx̂|>0.5 theo chiều nào → cực trị thật gần pixel lân cận hơn, dời tâm sang đó, lặp lại.

  **Chú thích ký hiệu (công thức nội suy):**
  - `D` = hàm DoG (giá trị ảnh DoG), phụ thuộc vị trí (x,y) và tỉ lệ σ — coi như 1 hàm số 3 biến.
  - `x` = vector vị trí đang xét trong không gian 3 chiều (x,y,σ) — không phải tọa độ x đơn lẻ, mà là cả bộ 3 giá trị.
  - `x₀` = vị trí pixel ứng viên ban đầu (số nguyên, rời rạc — pixel cực trị tìm được ở bước trước).
  - `Δx` = độ lệch (ẩn số cần tìm) từ x₀ tới vị trí cực trị thật — 1 vector 3 chiều (Δx,Δy,Δσ), có thể là số thập phân.
  - `∂D/∂x` = vector gradient (đạo hàm bậc 1) của D tại x₀ — đo D đang "dốc" theo hướng nào.
  - `H` = ma trận Hessian (đạo hàm bậc 2) của D tại x₀, kích thước 3×3 ở bước này — đo độ cong của D.
  - `Δx̂` = giá trị Δx sau khi giải phương trình (kết quả cụ thể, không còn là ẩn số).
  - `H⁻¹` = ma trận nghịch đảo của H.

  *Loại tương phản thấp:* tính `D(x̂)=D(x₀)+½(∂D/∂x)ᵀΔx̂` tại điểm đã nội suy (`x̂ = x₀+Δx̂`, vị trí cực trị đã tinh chỉnh) — đây là độ tương phản thật. |D(x̂)| < ngưỡng (paper gốc: 0.03, pixel chuẩn hóa [0,1]) → loại, vì dễ bị nhiễu ảnh hưởng.

  *Loại cạnh — vì sao dùng Tr/Det thay vì tính trực tiếp trị riêng:* góc thật có 2 trị riêng Hessian lớn & xấp xỉ nhau; cạnh có 1 trị riêng lớn, 1 rất nhỏ (phẳng dọc cạnh). Gọi α,β là 2 trị riêng, r=α/β: `Tr(H)²/Det(H) = (α+β)²/(αβ) = (r+1)²/r` — tăng đơn điệu theo r, tính được chỉ từ Dxx,Dyy,Dxy có sẵn (không cần giải phương trình đặc trưng tốn kém). Ngưỡng r=10 (chuẩn Lowe) → so `Tr²/Det > (11)²/10=12.1` thì loại.

  **Chú thích ký hiệu (bước loại cạnh):**
  - `H` = ma trận Hessian **2×2** ở bước này (chỉ xét x,y, khác H 3×3 ở bước nội suy trên): `H=[[Dxx,Dxy],[Dxy,Dyy]]`.
  - `Dxx, Dyy` = đạo hàm bậc 2 của D theo x, theo y riêng — đo độ cong dọc mỗi trục.
  - `Dxy` = đạo hàm hỗn hợp (theo cả x và y) — đo độ "xiên/chéo" của độ cong.
  - `α, β` = 2 trị riêng (eigenvalue) của ma trận H — về ý nghĩa hình học, đo độ cong lớn nhất/nhỏ nhất theo 2 hướng vuông góc.
  - `r` = tỉ lệ α/β (α là trị lớn hơn) — đo mức độ "méo" (r≈1: góc thật; r lớn: cạnh).
  - `Tr(H)` = vết ma trận (tổng đường chéo) = Dxx+Dyy = α+β.
  - `Det(H)` = định thức ma trận = Dxx·Dyy−Dxy² = α·β.

- **Gán hướng chủ đạo:** histogram gradient 36 bin (10°/bin) quanh keypoint, hướng tần suất cao nhất = hướng chủ đạo — giúp descriptor bất biến khi ảnh xoay.

  *Vì sao đúng 36 bin/10°:* con số thực nghiệm (Lowe thử nhiều độ phân giải, đo tỉ lệ khớp đúng khi ảnh xoay) — đủ mịn để phân biệt hướng rõ ràng (bin to hơn thì nhiều hướng khác nhau bị gộp, mất độ chính xác), không quá mịn tới mức bị nhiễu pixel đơn lẻ chi phối. Nếu có nhiều đỉnh histogram ≥80% đỉnh cao nhất (điểm ở góc giao nhiều cạnh) → tạo nhiều keypoint cùng vị trí/tỉ lệ, khác hướng.

- **Tính descriptor:** vùng 16×16 pixel quanh keypoint (đã xoay theo hướng chủ đạo), chia lưới 4×4 ô, mỗi ô histogram gradient 8 hướng → 4×4×8=128 số, chuẩn hóa vector về độ dài 1 (bất biến với đổi độ sáng).

  *Vì sao 16×16, 4×4, 8 bin — hoàn toàn thực nghiệm:* Lowe thử nhiều cấu hình (2×2×8, 4×4×8, 8×8×8...) trên ảnh thật có xoay/co giãn/nhiễu/đổi sáng, đo recall vs false-positive. Quá ít ô (2×2) → descriptor thô, dễ khớp nhầm. Quá nhiều ô (8×8) → quá nhạy với sai lệch định vị keypoint 1-2 pixel (khó tránh do nhiễu), mất ổn định. 4×4×8=128 là điểm hiệu suất gần bão hòa trong thực nghiệm — tăng thêm không cải thiện đáng kể mà tốn thêm bộ nhớ/thời gian khớp.

  *Bổ sung nâng cao:* sau chuẩn hóa L2, còn cắt (clamp) giá trị >0.2 rồi chuẩn hóa lại lần 2 — giảm ảnh hưởng thay đổi ánh sáng phi tuyến (vùng lóa sáng/specular highlight làm vài bin có giá trị bất thường lớn, lấn át toàn vector).

  *Descriptor — vector 128 số cụ thể là gì:* chỉ là 1 danh sách 128 số thực gắn với 1 keypoint, vd `[0.02, 0.15, 0.08, ..., 0.05]`. Ráp lại từ 16 ô (lưới 4×4), mỗi ô ra 1 histogram 8 số (vd ô 1: `[5,2,0,1,8,3,0,1]` — đếm/gộp gradient có trọng số theo 8 hướng 0°,45°,...,315°, số lớn = nhiều cạnh theo hướng đó trong ô), nối 16 dãy 8-số liên tiếp thành 1 hàng dài `16×8=128`. Coi như "vân tay số" của vùng ảnh quanh keypoint: cùng 1 điểm vật lý thật (dù chụp góc khác) → 2 descriptor gần giống hệt nhau; 2 điểm khác nhau → 2 descriptor khác hẳn. Đây là lý do Bước 2 so khoảng cách Euclid giữa 2 vector 128 chiều được — coi descriptor như tọa độ 1 điểm trong không gian 128 chiều, công thức khoảng cách y hệt không gian 2-3 chiều: `√(Σ(aᵢ-bᵢ)²)`, i chạy 1→128.

  *Keypoint vs descriptor — phân biệt:* keypoint = "vị trí" (tọa độ pixel (x,y) + tỉ lệ σ + hướng θ, không phải vector). Descriptor = "đặc điểm nhận dạng" (vector 128 số) tính ra từ vùng ảnh quanh keypoint đó. Mỗi keypoint có đúng 1 descriptor đi kèm — giống địa chỉ nhà (keypoint) và vân tay người ở đó (descriptor): 2 thông tin khác nhau nhưng đi cùng nhau. Bước 2 (matching) so sánh descriptor (128 số) với nhau, không so trực tiếp tọa độ keypoint.

  *Cách tính descriptor — từng bước cụ thể:*
  1. Lấy vùng 16×16 pixel quanh keypoint, trên ảnh đã mờ Gaussian ở đúng mức σ của keypoint đó.
  2. Với mỗi pixel trong vùng (256 pixel), tính độ lớn gradient `m(x,y)=√[(L(x+1,y)-L(x-1,y))²+(L(x,y+1)-L(x,y-1))²]` và góc thô `atan2(...)`.
  3. Trừ góc thô cho hướng chủ đạo θ của keypoint → góc tương đối (quy về hệ chuẩn, tạo bất biến xoay).
  4. Nhân m(x,y) với trọng số Gaussian tâm tại keypoint (σ_G=8, bằng nửa bề rộng vùng 16) → pixel càng xa tâm càng ít ảnh hưởng.
  5. Với mỗi pixel: xác định thuộc ô nào trong lưới 4×4 (dựa vào x,y) và bin hướng nào trong 8 bin (dựa vào góc tương đối) → cộng giá trị trọng số vào đúng ô[subregion][bin].
  6. Sau khi duyệt hết 256 pixel, mỗi ô trong 16 ô có 1 histogram 8 số (vd ô 6: `[2,9,0,1,3,0,0,1]`).
  7. Nối 16 ô liên tiếp thành 1 vector dài `16×8=128` số.
  8. Chuẩn hóa: `v_norm = v/‖v‖₂` (‖v‖₂=√Σvᵢ²) — triệt tiêu ảnh hưởng thay đổi sáng tuyến tính đều.
  9. Cắt ngưỡng: giá trị nào >0.2 thì gán =0.2, rồi chuẩn hóa lại lần 2 — giảm ảnh hưởng thay đổi sáng phi tuyến (vùng lóa sáng). Kết quả cuối = descriptor lưu lại cho keypoint.

  *Bản đầy đủ (Lowe's paper):* thay vì 1 pixel "bỏ phiếu trọn" vào đúng 1 ô+1 bin, dùng **trilinear interpolation** — chia nhỏ đóng góp cho 2 ô gần nhất theo x, 2 ô gần nhất theo y, 2 bin góc gần nhất (tối đa 8 phần), tỉ lệ theo khoảng cách — tránh "nhảy cóc" khi pixel nằm sát ranh giới ô/bin.

**Bước 2 — Feature Matching:** so từng descriptor ảnh A với từng descriptor ảnh B, tìm cặp khoảng cách Euclid (trong không gian 128 chiều) gần nhau nhất. **Lowe's ratio test** lọc match mơ hồ: với mỗi điểm ở A, tìm 2 điểm gần nhất ở B; nếu khoảng cách gần nhất và gần nhì xấp xỉ nhau (tỉ lệ > 0.8) → mơ hồ, loại bỏ; chỉ giữ match có điểm gần nhất rõ ràng tốt hơn hẳn điểm gần nhì.

*Thuật toán chi tiết:* tìm lân cận gần nhất bằng **KD-tree** (k-dimensional tree, "cây k-chiều" — cấu trúc cây phân hoạch không gian) thay vì so trực tiếp từng cặp (brute-force, "vét cạn") — nhanh hơn nhiều khi có hàng nghìn điểm (gần O(n log n) thay vì O(n²), n = số điểm).

**Bước 3 — Geometric Verification (RANSAC - Random Sample Consensus, "đồng thuận trên mẫu ngẫu nhiên" + Epipolar Geometry, "hình học cực"):** 2 ảnh chụp cùng cảnh cứng từ 2 vị trí phải tuân theo ràng buộc hình học chặt (epipolar constraint), biểu diễn qua **Essential Matrix E** (3×3). Dùng **RANSAC**: chọn ngẫu nhiên 5 cặp match, tính thử E (thuật toán 5-point), kiểm tra bao nhiêu match khác "phù hợp" với E đó (inlier); lặp hàng nghìn lần, giữ E có nhiều inlier nhất. Kết quả: loại match sai (outlier), chỉ giữ match sạch + có E.

*Thuật toán chi tiết:*
- **5-point (Nistér):** E có đúng 5 bậc tự do → chỉ cần 5 cặp điểm khớp là đủ giải. Với 5 cặp, giải hệ phương trình đa thức → tối đa 10 nghiệm E khả dĩ, lọc bớt bằng ràng buộc phụ.
- **Vòng lặp RANSAC:** lặp K lần (~1000-2000): (1) chọn ngẫu nhiên 5 cặp match, (2) chạy 5-point ra E ứng viên, (3) đếm bao nhiêu match khác thỏa `x₂ᵀ·E·x₁ ≈ 0` (sai số < ngưỡng) = inlier, (4) giữ E có nhiều inlier nhất. Sau K lần, refine E bằng least-squares trên toàn bộ inlier của nó.

  **Chú thích ký hiệu:** `x₁, x₂` = tọa độ 1 cặp điểm khớp, dạng thuần nhất (homogeneous, thêm số 1 vào cuối: (u,v,1)), trên ảnh 1 và ảnh 2. `E` = ma trận Essential 3×3 đang muốn tìm/kiểm tra. `x₂ᵀ·E·x₁` = 1 con số (do nhân ma trận 1×3 · 3×3 · 3×1) — về lý thuyết phải bằng 0 nếu x₁,x₂ đúng là 2 hình chiếu của cùng 1 điểm 3D thật với pose tương ứng E; sai số nhỏ (do đo đạc không tuyệt đối) thì vẫn chấp nhận là inlier.

  *Vì sao ~1000-2000 lần — công thức xác suất cụ thể:* `N = log(1-p) / log(1-wⁿ)`, p=xác suất mong muốn tìm được ít nhất 1 lần mẫu toàn inlier (thường 0.99), w=tỉ lệ inlier ước tính (~0.5 với match thô sau ratio test), n=5 (cỡ mẫu tối thiểu). Ví dụ p=0.99,w=0.5,n=5: w⁵=0.03125, N=log(0.01)/log(0.96875)≈145. Dữ liệu nhiễu hơn (w thấp, vd 0.2) thì N tăng vọt (w⁵=0.00032→N≈14.300). Vì không biết trước w chính xác, COLMAP dùng chiến lược **adaptive**: bắt đầu với N ước lượng thận trọng, sau mỗi vòng cập nhật w=(inlier tốt nhất/tổng match), tính lại N, dừng sớm khi N ước lượng mới đã nhỏ hơn số vòng đã chạy — 1000-2000 là con số thường gặp thực tế khi w~0.3-0.5, không phải hằng số cố định trong thuật toán.

**Bước 4 — Essential Matrix → Pose tương đối (R,t):** phân tích E bằng SVD (Singular Value Decomposition, "phân tích giá trị suy biến" — phép phân tích 1 ma trận thành 3 ma trận thành phần) ra 4 khả năng (R₁,t),(R₁,-t),(R₂,t),(R₂,-t). Chọn đúng 1 bằng kiểm tra **cheirality**: tam giác hóa thử vài điểm với mỗi khả năng, chọn khả năng cho điểm 3D nằm phía trước cả 2 camera (nhìn thấy được, không phải ảo sau lưng camera). Lưu ý: E chỉ cho pose tương đối tới 1 hệ số tỉ lệ (scale ambiguity) — không biết khoảng cách thật bao nhiêu mét, chỉ biết hướng.

*Thuật toán chi tiết:* SVD phân tích E = U·Σ·Vᵀ. Dùng 1 ma trận xoay cố định W (ma trận hoán vị 90°): `R = U·W·Vᵀ` hoặc `R = U·Wᵀ·Vᵀ` (2 khả năng), `t = ±(cột 3 của U)` (2 khả năng) → 2×2=4 tổ hợp. Cheirality loại 3/4 tổ hợp cho điểm 3D nằm sau lưng ít nhất 1 camera (vô lý vật lý), còn đúng 1 tổ hợp hợp lệ.

*Ma trận W cụ thể:* `W = [[0,-1,0],[1,0,0],[0,0,1]]` — ma trận xoay 90° quanh trục z. Xuất hiện vì quan hệ đại số `E = [t]ₓ·R` (`[t]ₓ` = "ma trận tích có hướng" của t, biểu diễn phép tích có hướng thành phép nhân ma trận); có thể chứng minh `R=U·W·Vᵀ` (hoặc `U·Wᵀ·Vᵀ`) và `t=±cột 3 của U` thỏa đúng quan hệ đó (kết quả đại số tuyến tính có sẵn, không cần tự suy mỗi lần).

  **Chú thích ký hiệu:** `E` = ma trận Essential đã có (từ Bước 3). `U, Σ, V` = 3 ma trận thành phần khi phân tích SVD của E (U,V là ma trận trực giao 3×3, Σ là ma trận đường chéo). `Vᵀ, Wᵀ` = ma trận chuyển vị của V, W. `R` = ma trận xoay 3×3 cần tìm (pose tương đối). `t` = vector dịch chuyển 3 chiều cần tìm. `[t]ₓ` = cách biểu diễn t (vector) thành 1 ma trận 3×3 đặc biệt, sao cho phép nhân ma trận đó với vector khác cho kết quả giống phép tích có hướng (cross product) của t với vector đó.

*Vì sao đúng 4 nghiệm:* SVD của E không duy nhất về dấu (đổi dấu 1 cột U hoặc V vẫn là SVD hợp lệ) → 2 lựa chọn R (W hay Wᵀ) × 2 lựa chọn t (dấu + hay -) = 4 tổ hợp, đều thỏa cùng phương trình E=U·Σ·Vᵀ như nhau — về toán thuần túy cả 4 đều "đúng", không phân biệt được chỉ từ E, phải dùng ràng buộc vật lý bên ngoài (cheirality) để chọn.

**Bước 5 — Triangulation:** có 2 pose + 1 cặp điểm khớp (u₁,v₁),(u₂,v₂) → bắn 2 tia (công thức r(t)=o+t·d) từ 2 tâm camera qua 2 điểm đó. Do sai số đo đạc, 2 tia thường không giao chính xác 100% → dùng bình phương tối thiểu (DLT - Direct Linear Transform) tìm điểm 3D có tổng bình phương khoảng cách tới 2 tia nhỏ nhất.

*Thuật toán DLT chi tiết:* với điểm 3D chưa biết X (tọa độ thuần nhất 4 chiều), ràng buộc chiếu đúng `x × (P·X) = 0` (tích có hướng bằng 0 vì x và P·X phải cùng hướng) khai triển ra 2 phương trình tuyến tính theo X cho mỗi ảnh quan sát được điểm đó. Gộp phương trình từ 2 ảnh thành ma trận A, giải `A·X=0` bằng SVD của A → X = cột cuối của V (ứng trị suy biến nhỏ nhất) — nghiệm bình phương tối thiểu.

  **Chú thích ký hiệu:** `X` = tọa độ điểm 3D cần tìm, dạng thuần nhất 4 chiều (X,Y,Z,1) — ẩn số của bài toán. `x` = tọa độ pixel quan sát được (u,v,1), dạng thuần nhất — đã biết. `P` = ma trận chiếu (projection matrix) 3×4 của 1 camera, gộp cả K và (R,C) — biến đổi 1 điểm 3D thành tọa độ pixel tương ứng, đã biết (từ Bước 4). `A` = ma trận gộp các phương trình tuyến tính từ nhiều ảnh (kích thước 4×4 nếu 2 ảnh, mỗi ảnh góp 2 hàng). `V` (trong SVD của A) = 1 trong 3 ma trận thành phần của A=U·Σ·Vᵀ — cột cuối của nó chính là nghiệm X cần tìm.

**Bước 6 — Incremental SfM (thêm dần từng ảnh):** với mỗi ảnh mới: (a) khớp feature với các ảnh đã đăng ký; (b) match nào trùng điểm 3D đã triangulate → có tập correspondence (tương ứng) 2D-3D; (c) giải bài toán **PnP** (Perspective-n-Point, "phối cảnh n-điểm" — cụ thể dùng P3P + RANSAC) — biết điểm 3D + vị trí 2D tương ứng, tìm pose camera tạo ra kết quả đó → ra pose ảnh mới; (d) triangulate thêm điểm mới từ ảnh mới. Lặp tới hết ảnh.

*Thuật toán P3P + RANSAC chi tiết:*
- **P3P (Perspective-3-Point, "phối cảnh 3-điểm" — trường hợp riêng của PnP khi n=3):** biết 3 điểm 3D + vị trí 2D tương ứng trên ảnh mới. Dùng định lý hàm cosin trong tam giác tạo bởi tâm camera và 3 điểm đó (góc giữa các tia tính được từ pixel + K) → hệ phương trình đa thức bậc 4 → tối đa 4 nghiệm pose. Dùng thêm điểm thứ 4 để chọn đúng 1 nghiệm.

  *Vì sao tối thiểu 3 điểm:* pose camera có 6 bậc tự do (3 xoay+3 dịch). Mỗi correspondence 2D-3D cho 2 phương trình ràng buộc (từ u,v) — về lý thuyết 6/2=3 điểm đủ số phương trình, nhưng quan hệ phi tuyến (phép chiếu phối cảnh) nên không giải trực tiếp kiểu tuyến tính, thành hệ phương trình đa thức.

  *Vì sao ra đa thức bậc 4:* gọi khoảng cách từ camera tới 3 điểm là d₁,d₂,d₃ (ẩn số), góc giữa các cặp tia θ₁₂,θ₂₃,θ₁₃ (biết từ pixel+K). Định lý cosin cho 3 cặp tam giác → 3 phương trình bậc 2 liên hệ d₁,d₂,d₃. Khử biến (đặt x=d₂/d₁, y=d₃/d₁) rút gọn 3 phương trình bậc 2 thành 1 phương trình đa thức bậc 4 theo 1 ẩn còn lại → tối đa 4 nghiệm thực (đa thức bậc n có tối đa n nghiệm). Điểm thứ 4 (ngoài 3 điểm ban đầu) dùng kiểm tra, chọn nghiệm khớp với nó nhất.

  **Chú thích ký hiệu:** `d₁,d₂,d₃` = khoảng cách (chưa biết) từ tâm camera tới 3 điểm 3D đã biết tọa độ — đây là ẩn số chính cần giải. `θ₁₂,θ₂₃,θ₁₃` = góc giữa từng cặp tia camera→điểm (ví dụ θ₁₂ = góc giữa tia tới điểm 1 và tia tới điểm 2) — tính được từ tọa độ pixel + ma trận K, coi như đã biết trước khi giải. `x, y` (trong bước khử biến) = 2 biến trung gian đặt ra để giảm số ẩn, không phải tọa độ pixel (x,y) đã dùng ở các phần khác — chỉ là tỉ lệ x=d₂/d₁, y=d₃/d₁, giúp rút 3 phương trình về còn 1 ẩn.
- **RANSAC bọc ngoài:** lặp nhiều lần: chọn ngẫu nhiên 3-4 cặp correspondence 2D-3D, giải P3P, đếm inlier (correspondence khác khớp với pose vừa giải, sai số reprojection < ngưỡng), giữ pose nhiều inlier nhất.

**Bước 7 — Bundle Adjustment:** chạy định kỳ suốt quá trình (không chỉ 1 lần cuối, để tránh sai số tích lũy/drift) — điều chỉnh đồng thời TẤT CẢ pose + TẤT CẢ điểm 3D, tối thiểu hóa tổng bình phương **reprojection error** (khoảng cách giữa pixel thật đã phát hiện và pixel suy ra khi chiếu điểm 3D qua pose camera). Bài toán tối ưu phi tuyến lớn (hàng nghìn tham số), giải bằng **Levenberg-Marquardt**.

*Thuật toán Levenberg-Marquardt (LM) chi tiết:* mỗi pose 6 tham số (3 xoay+3 dịch) + mỗi điểm 3D 3 tham số → 100 ảnh + 10.000 điểm ≈ 30.600 tham số tối ưu cùng lúc. LM kết hợp 2 phương pháp: **Gauss-Newton** (hội tụ rất nhanh khi gần nghiệm, dùng xấp xỉ đạo hàm bậc 2 qua ma trận Jacobian, nhưng dễ phân kỳ khi ở xa nghiệm) và **Gradient Descent** (ổn định, luôn giảm loss, nhưng chậm khi gần nghiệm). Dùng 1 tham số damping λ trộn 2 cách: lặp — tính bước cập nhật theo λ, thử: loss giảm → chấp nhận bước, giảm λ (tin Gauss-Newton hơn, đi nhanh); loss không giảm → không chấp nhận, tăng λ (quay về gần Gradient Descent, thận trọng hơn), thử lại. Xa nghiệm λ lớn (an toàn), gần nghiệm λ nhỏ (hội tụ nhanh).

  *Công thức cập nhật cụ thể:* `(JᵀJ + λ·diag(JᵀJ))·Δ = -Jᵀ·r` (J=Jacobian của reprojection error theo mọi tham số, r=residual hiện tại, Δ=bước cập nhật cần tìm). λ→0: tiến về Gauss-Newton thuần (`JᵀJ·Δ=-Jᵀr`, hội tụ nhanh gần nghiệm). λ→∞: số hạng λ·diag(JᵀJ) áp đảo, xấp xỉ Gradient Descent (`Δ≈-Jᵀr/λ`, bước rất nhỏ theo đúng hướng gradient, an toàn nhưng chậm). λ chính là núm vặn chuyển đổi liên tục giữa 2 chế độ.

  **Chú thích ký hiệu:** `J` = ma trận Jacobian — mỗi hàng ứng 1 observation (1 điểm nhìn thấy trên 1 ảnh), mỗi cột ứng 1 tham số (1 trong 6 số của 1 pose, hoặc 1 trong 3 tọa độ của 1 điểm 3D); phần tử J[hàng][cột] = đạo hàm của sai số đó theo tham số đó. `r` = vector residual — mỗi phần tử là 1 reprojection error hiện tại (pixel thật − pixel dự đoán) của 1 observation. `Δ` = vector bước cập nhật (ẩn số cần giải mỗi vòng lặp) — cộng vào toàn bộ tham số hiện tại để được tham số mới. `λ` = số thực dương (damping), điều chỉnh qua từng vòng lặp tùy loss có giảm hay không. `diag(JᵀJ)` = ma trận chỉ giữ lại đường chéo của JᵀJ (các phần tử ngoài đường chéo cho về 0).

*Insight:* mỗi observation chỉ phụ thuộc đúng 1 camera + đúng 1 điểm 3D (không phụ thuộc camera/điểm khác) → ma trận Jacobian rất thưa (sparse). COLMAP (qua thư viện Ceres Solver) khai thác cấu trúc thưa này bằng kỹ thuật **Schur complement** để giải nhanh hơn hàng trăm lần so với giải trực tiếp — đây là lý do Bundle Adjustment với hàng chục nghìn tham số vẫn chạy được trong thời gian hợp lý.

**Kết quả:** mỗi ảnh có 1 ma trận pose (R, C) đã tinh chỉnh + K, tất cả nằm chung 1 hệ tọa độ world — hệ này chỉ là hệ quả của cặp ảnh khởi tạo ở Bước 3-4 (gốc + hướng ban đầu do cheirality chọn ra), các ảnh sau chỉ tính tương đối theo hệ đó qua PnP.

## Phụ lục: Phép chiếu phối cảnh (Perspective Projection) — nền tảng Pinhole Camera

### Phối cảnh là gì

Quan sát: 2 người cao bằng nhau đứng cách bạn 2m và 20m — người xa trông nhỏ hơn hẳn trong ảnh, dù thực tế cao bằng nhau. Đường ray tàu hỏa song song, nhìn xa dần trông như hội tụ về 1 điểm. Đây là **phối cảnh (perspective)**: vật càng xa camera thì hình chiếu của nó lên ảnh càng nhỏ. **Phép chiếu phối cảnh** = công thức toán mô tả chính xác quy luật đó, biến 1 điểm 3D (X,Y,Z) thành 1 điểm 2D (u,v) trên ảnh.

### Camera pinhole (lỗ kim)

1 hộp kín, 1 mặt có lỗ nhỏ xíu, mặt đối diện là phim/cảm biến. Ánh sáng từ mọi điểm trên vật đi theo đường thẳng, xuyên qua đúng lỗ kim, đập vào phim. Vì đi thẳng qua đúng 1 điểm, tia từ đỉnh vật đập vào đáy phim và ngược lại → ảnh tạo ra bị **lộn ngược** (trên-dưới, trái-phải đảo).

### Mẹo toán học: mặt phẳng ảnh ảo đặt phía trước

Để khỏi xử lý ảnh lộn ngược, Computer Vision/Graphics dùng mẹo: tưởng tượng 1 mặt phẳng ảnh ảo đặt **phía trước** lỗ kim (thay vì phía sau như thật), cùng khoảng cách. Ảnh tạo ra trên mặt phẳng ảo này giống hệt ảnh thật nhưng không bị lộn ngược — vì 2 tam giác (thật ở sau, ảo ở trước) đối xứng nhau qua tâm lỗ kim, tỉ lệ hình học y hệt. Đây là quy ước chuẩn dùng trong mọi công thức camera (kể cả NeRF).

### Dựng công thức bằng tam giác đồng dạng

Đặt gốc (0,0,0) = tâm lỗ kim = tâm camera. Trục Z = trục quang học (hướng camera nhìn). Mặt phẳng ảnh ảo cách gốc 1 khoảng = **f** (focal length) theo trục Z.

Xét điểm 3D thật P=(X,Y,Z), Z là depth (độ sâu dọc trục quang học). Vẽ đường thẳng từ P xuyên qua gốc → cắt mặt phẳng ảnh ảo tại (x_img, y_img).

Tam giác lớn (đáy X, cao Z) đồng dạng tam giác nhỏ (đáy x_img, cao f) — chung 1 góc ở đỉnh, cạnh song song vì cùng nằm trên 1 đường thẳng xuyên gốc. Tam giác đồng dạng → tỉ lệ cạnh bằng nhau:

```
x_img / f = X / Z   →   x_img = f · X / Z
y_img = f · Y / Z
```

Đây chính là công thức phép chiếu phối cảnh — Z lớn (xa) → x_img nhỏ, đúng quy luật "xa thì nhỏ".

**Kiểm chứng bằng số:** f=500, X=4. Z=2 → x_img=500·4/2=1000. Z=4 (xa gấp đôi) → x_img=500·4/4=500 (giảm đúng 1 nửa, tỉ lệ nghịch với Z).

### Từ tọa độ mặt phẳng ảnh ra tọa độ pixel

x_img, y_img có gốc tại tâm mặt phẳng ảnh; ảnh số cần tọa độ pixel (u,v) gốc ở góc trên-trái, nên dịch thêm (cx,cy) — tọa độ pixel tâm ảnh:

```
u = fx·X/Z + cx
v = fy·Y/Z + cy
```

(fx,fy = f tính theo đơn vị pixel). Đây là công thức chiếu phối cảnh đầy đủ. Khác 1 chỗ so với công thức đảo ngược dùng ở Phần V: quy ước NeRF/OpenGL cho camera nhìn theo hướng **-Z** (không phải +Z như hình dựng ở đây cho dễ hình dung) — nên "Z" (depth dương) được thay bằng "-Z" trong công thức thật, đó là nguồn gốc dấu trừ hay gặp.

## Phần IV: Camera Intrinsics — thông số riêng của ống kính

Ma trận **K** (3×3), mô tả đặc tính quang học của bản thân cái camera (khác với R, C — R,C nói về camera *đặt ở đâu*, K nói về *bản chất ống kính/cảm biến*, không đổi dù camera di chuyển đi đâu):

```
K = [ fx   0   cx ]
    [  0  fy   cy ]
    [  0   0    1 ]
```

- **fx, fy — focal length** (tiêu cự), đơn vị **pixel** (không phải mm, vì K làm việc trực tiếp trên ảnh số). Focal length càng lớn → ảnh càng "zoom" → field of view (FOV, "trường nhìn"/góc nhìn) càng hẹp. Công thức: `FOV = 2 · arctan(W / (2·fx))`. Ví dụ W=800, fx=800 → FOV ngang ≈ 53°; fx=1600 → FOV ≈ 28°.

- **cx, cy — principal point**: tọa độ pixel nơi trục quang học (đường thẳng xuyên tâm ống kính, vuông góc mặt cảm biến) cắt mặt phẳng ảnh — về lý thuyết là "tâm ảnh" quang học. Lắp ráp máy ảnh không hoàn hảo nên có thể lệch nhẹ so với W/2,H/2; khi không đo được chính xác thì giả định cx≈W/2, cy≈H/2.

**Lấy K từ đâu:** đọc từ EXIF (Exchangeable Image File Format, "định dạng file ảnh trao đổi được") ảnh, hoặc để COLMAP tự ước lượng cùng lúc với pose ở bước Bundle Adjustment.

**W/2, H/2 là gì:** W=Width (chiều rộng ảnh, pixel), H=Height (chiều cao ảnh, pixel). W/2, H/2 = tọa độ pixel chính giữa ảnh — dùng làm giá trị xấp xỉ cho cx,cy vì ống kính lắp đúng chuẩn thì trục quang học đi xuyên đúng tâm hình học ảnh; lắp ráp thực tế có sai số nhỏ nên không tuyệt đối chính xác, nhưng đủ dùng khi không đo được số thật.

**EXIF là gì:** khối dữ liệu ẩn máy ảnh/điện thoại tự nhúng vào file ảnh lúc chụp (không thấy trên ảnh, đọc được bằng phần mềm như `exiftool`). Chứa: hãng/model máy, **focal length**, khẩu độ, tốc độ màn trập, ISO, ngày giờ, đôi khi cả GPS. Nếu EXIF có focal length (thường tính bằng mm), có công thức đổi sang pixel (dựa vào kích thước cảm biến vật lý) để ra fx,fy — nhưng kém chính xác hơn để COLMAP tự ước lượng trực tiếp từ ảnh.

*Insight:* K mô tả "ống kính" (intrinsic — nội tại), R/C mô tả "vị trí đặt máy" (extrinsic — ngoại tại). Cùng 1 máy ảnh chụp 100 tấm ở 100 vị trí khác nhau → K giống hệt nhau cả 100 tấm, chỉ (R,C) đổi.

## Phần V: Công thức đầy đủ — từ pixel (u,v) ra một tia trong không gian 3D

Ví dụ số: ảnh W=800, H=600, fx=fy=800, cx=400, cy=300. Pose: R = ma trận đơn vị, C = (0,0,5). Tính tia cho pixel (u,v) = (500, 200).

**Bước 1 — Pixel → hướng trong hệ camera** (quy ước camera nhìn theo trục -z, y hướng lên, đúng code gốc NeRF):

```
x_cam = (u - cx) / fx = (500 - 400) / 800 = 0.125
y_cam = -(v - cy) / fy = -(200 - 300) / 800 = 0.125
z_cam = -1
```

d_cam = (0.125, 0.125, -1)

Giải thích dấu: chia cho fx,fy đưa từ đơn vị pixel về tỉ lệ tương đối so với tiêu cự (càng xa tâm ảnh, tia càng lệch nhiều). Dấu trừ ở y_cam vì pixel v tăng xuống dưới ảnh còn trục y camera quy ước hướng lên. z_cam=-1 vì mặt phẳng ảnh quy ước cách tâm camera 1 đơn vị theo hướng camera nhìn (-z).

**Vì sao ra được công thức này — gốc rễ tam giác đồng dạng (pinhole camera model):**

Với 1 điểm 3D (X,Y,Z) trong hệ camera, công thức chiếu phối cảnh chuẩn: `u - cx = fx · X/(-Z)`, `v - cy = -fy · Y/(-Z)` — suy ra từ tam giác đồng dạng (tam giác tâm camera→điểm 3D thật, đồng dạng với tam giác tâm camera→điểm trên mặt phẳng ảnh).

Biết (u,v) chỉ suy ra được **tỉ lệ** X/(-Z), Y/(-Z) — không suy ra X,Y,Z riêng lẻ, vì 1 pixel ứng với cả 1 tia vô hạn điểm. Vì chỉ cần **hướng** (không cần vị trí cụ thể trên tia), ta **tự chọn** -Z=1 (tức Z=-1, "mặt phẳng ảnh cách tâm đúng 1 đơn vị") — đây là lựa chọn tiện tính toán, không phải đo đạc. Thay vào công thức tỉ lệ: X=(u-cx)/fx, Y=-(v-cy)/fy, Z=-1 — đúng ra 3 giá trị x_cam,y_cam,z_cam ở trên.

Điểm (x_cam,y_cam,z_cam) là 1 điểm cụ thể trên tia, cách tâm camera 1 đơn vị theo hướng nhìn. Vì gốc hệ camera là (0,0,0), vector hướng d_cam = điểm − gốc = chính điểm đó. Chọn -Z khác 1 thì x_cam,y_cam đổi theo tỉ lệ nhưng hướng (tỉ lệ X:Y:Z) không đổi — nên kết quả cuối (hướng tia) không phụ thuộc lựa chọn này.

**Bước 2 — Xoay từ hệ camera sang hệ world** bằng R: `d_world = R · d_cam`. R=đơn vị → d_world=(0.125,0.125,-1) y hệt. Nếu R khác đơn vị, đây là phép nhân ma trận 3×3 với vector.

**Bước 3 — Gốc tia:** `o = C = (0,0,5)`

**Bước 4 — Công thức tia đầy đủ:** `r(t) = o + t·d = (0,0,5) + t·(0.125, 0.125, -1)`

| t | điểm r(t) |
|---|---|
| 0 | (0, 0, 5) — tâm camera |
| 2 | (0.25, 0.25, 3) |
| 5 | (0.625, 0.625, 0) |

z giảm dần khi t tăng — khớp logic: camera ở z=5 "nhìn" dần vào cảnh có z nhỏ hơn.

## Phần VI: Chọn điểm mẫu trên tia — t lấy giá trị nào

Không thể lấy vô hạn điểm (t chạy từ 0 đến vô cực) — phải giới hạn khoảng và chọn hữu hạn điểm.

**Giới hạn khoảng:** đặt t_near, t_far (biết trước/ước lượng, ví dụ cảnh cách camera 2-6m → t_near=2, t_far=6).

**Stratified sampling:** chia [t_near, t_far] thành N đoạn bằng nhau (N=64), mỗi đoạn lấy 1 điểm ngẫu nhiên:

```
t_i = t_near + (i + ε_i)/N × (t_far - t_near),   ε_i ~ Uniform(0,1),  i=0..N-1
```

Lấy ngẫu nhiên trong từng đoạn (không cố định) buộc mạng học hàm mượt, liên tục theo t — không "học vẹt" đúng N giá trị cố định, nội suy đúng cả ở t chưa từng thấy lúc train.

**Đối chiếu đúng công thức gốc trong paper (Eq. 2):** paper viết (đánh số đoạn từ i=1 đến N, không phải 0 đến N-1 như trên):
```
tᵢ ~ U[ tₙ + (i-1)/N·(t_f-tₙ) , tₙ + i/N·(t_f-tₙ) ]
```
— tức lấy 1 mẫu phân bố đều (Uniform, ký hiệu U[...]) trong **đúng đoạn con thứ i**. Về bản chất là cùng 1 công thức với bản 0-indexed ở trên, chỉ khác quy ước đánh số đoạn (paper bắt đầu từ 1, tôi dạy bắt đầu từ 0) — không có khác biệt gì về thuật toán.

**Vì sao không dùng lưới điểm cố định (deterministic quadrature) như khi render voxel grid rời rạc:** paper giải thích — nếu dùng 1 tập vị trí **cố định** (không đổi qua các lần train) để truy vấn MLP, về bản chất sẽ giới hạn độ phân giải của biểu diễn, vì MLP chỉ từng được "hỏi" đúng tại 1 tập điểm rời rạc cố định đó — giống hệt hạn chế của voxel grid. Stratified sampling (lấy mẫu ngẫu nhiên khác nhau mỗi lần) đảm bảo qua suốt quá trình tối ưu, MLP được đánh giá tại **vô số vị trí liên tục khác nhau** — đây chính là lý do NeRF biểu diễn được cảnh **liên tục** dù chỉ dùng 1 tập mẫu rời rạc để ước lượng tích phân ở mỗi lần render.

**Hierarchical sampling** (tóm tắt — chi tiết đầy đủ ở Phần IX): dùng 2 mạng — mạng "coarse" chạy trước với N_c điểm lấy đều (stratified), cho biết sơ bộ chỗ nào density σ cao (khả năng có bề mặt vật thể). Mạng "fine" lấy thêm N_f điểm mới, tập trung dày hơn quanh vùng density cao đó (**importance sampling**). Lý do: phần lớn tia là khoảng không (σ=0, vô ích), chỉ vài đoạn ngắn quanh bề mặt vật thể mới có σ lớn.

---

**Pipeline đầy đủ tới đây:** ảnh input → COLMAP ra pose (R,C) + K → công thức pixel→ray → chọn N điểm mẫu (x,y,z,θ,φ) trên tia → sẵn sàng đưa vào mạng nơ-ron.

## Phần VII: Volume Rendering — cộng dồn N điểm (r,g,b,σ) thành 1 màu pixel

### Vấn đề

N điểm mẫu trên tia, mỗi điểm đã có (màu c_i, density σ_i) từ mạng nơ-ron. Cần gộp N cặp đó thành 1 màu pixel duy nhất.

### Định nghĩa chính xác của σ(x) — theo đúng paper (mục 4)

Trước giờ vẫn gọi σ là "độ đặc" cho dễ hình dung — paper định nghĩa chính xác hơn: **σ(x) là xác suất vi phân (differential probability) để 1 tia kết thúc (bị hấp thụ) tại 1 hạt vô cùng nhỏ ở vị trí x**. Nói cách khác, σ không phải "độ đặc vật lý" theo nghĩa thông thường, mà là **tốc độ hấp thụ ánh sáng tức thời** tại điểm đó — σ càng lớn, xác suất 1 tia đi ngang qua điểm đó bị "chặn đứng" ngay tại đó càng cao. Cách hiểu "độ đặc" chỉ là hình dung trực quan gần đúng, cách hiểu "xác suất hấp thụ vi phân" mới là định nghĩa chuẩn dùng để suy ra toàn bộ công thức volume rendering bên dưới.

### Công thức tích phân liên tục gốc (trước khi rời rạc hóa) — Eq. 1 trong paper

Trước khi tới công thức rời rạc (dùng N điểm mẫu) đã học, paper viết dạng **tích phân liên tục** trước — đây là công thức "lý tưởng" (nếu tính được tích phân thật, không cần xấp xỉ bằng mẫu rời rạc):

```
C(r) = ∫ₜₙ^t_f T(t)·σ(r(t))·c(r(t),d) dt ,   T(t) = exp( -∫ₜₙ^t σ(r(s)) ds )
```

**Chú thích ký hiệu:** `tₙ, t_f` = cận gần/xa của tia (t_near, t_far đã học ở Phần VI). `T(t)` = transmittance tích lũy từ tₙ đến t — xác suất tia đi được từ tₙ tới t **mà không va chạm hạt nào** dọc đường (dạng liên tục của T_i đã học). Phần tích phân bên trong exp, `∫ₜₙ^t σ(r(s))ds`, cộng dồn liên tục mọi "mật độ hấp thụ" từ tₙ tới t.

**Vì sao không tính trực tiếp được tích phân này:** σ(r(t)) là output của 1 mạng nơ-ron tại vô số điểm t liên tục — không có công thức giải tích (closed-form) nào để tính tích phân của 1 mạng nơ-ron bất kỳ. Phải **ước lượng số (numerically estimate)** bằng cách lấy N điểm mẫu rời rạc rồi cộng theo công thức đã học (Eq. 3 — chính là công thức Ĉ(r)=ΣTᵢαᵢcᵢ ở mục dưới). Đây chính là lý do có 2 tầng công thức: **công thức liên tục** (định nghĩa đúng ý nghĩa vật lý, mục 4 paper) và **công thức rời rạc** (cách thực sự tính được bằng máy tính, dùng stratified sampling N điểm — Eq. 2-3).

### Trực giác: ánh sáng đi qua "sương mù màu" có mật độ thay đổi

Coi không gian dọc tia như làn khói có màu + độ đặc khác nhau từng đoạn. Ánh sáng đi từ xa (t lớn) về camera (t nhỏ). Mỗi đoạn nhỏ có thể chặn bớt ánh sáng phía sau nó, đồng thời góp màu riêng vào.

### Đại lượng 1 — Độ chặn sáng của 1 đoạn (α_i)

Dựa trên định luật vật lý **Beer-Lambert** (hấp thụ ánh sáng qua môi trường): xác suất ánh sáng sống sót qua 1 đoạn dày δ, mật độ σ là `exp(-σ·δ)`. Xác suất bị chặn (ngược lại):

```
α_i = 1 - exp(-σ_i · δ_i)      (δ_i = t_{i+1} - t_i, khoảng cách 2 điểm mẫu liên tiếp)
```

σ_i lớn (đặc, bề mặt) → α_i → gần 1 (chặn gần hết). σ_i≈0 (không khí) → α_i → gần 0 (gần như trong suốt).

### Đại lượng 2 — Độ "còn sống" tích lũy trước đó (T_i)

Xác suất ánh sáng từ đoạn i thực sự tới được camera — phải sống sót qua tất cả đoạn phía trước nó trước:

```
T_i = exp( -Σ_{j=1}^{i-1} σ_j·δ_j )    = tích xác suất sống sót từng đoạn trước đó
```

Không có gì đặc phía trước → T_i≈1 (màu đoạn i "lọt" ra ngoài). Có vật cản đặc phía trước → T_i tụt gần 0 → màu đoạn i gần như không đóng góp (bị che khuất — đúng vật lý: có vật chắn trước thì không thấy được cái sau).

### Công thức tổng hợp

```
C(r) = Σ_{i=1}^{N}  T_i · α_i · c_i
```

### Ví dụ số — 3 điểm mẫu (δ=1 mỗi đoạn)

| i | σ_i | màu c_i | ý nghĩa | T_i | α_i | đóng góp T_i·α_i·c_i |
|---|---|---|---|---|---|---|
| 1 (gần camera) | 0.1 | đỏ (1,0,0) | không khí loãng | 1 | 0.095 | (0.095,0,0) |
| 2 (giữa) | 2.0 | xanh lá (0,1,0) | bề mặt vật thể (đặc) | 0.905 | 0.865 | (0,0.783,0) |
| 3 (xa nhất) | 0.1 | xanh dương (0,0,1) | vật phía sau bề mặt | 0.1225 | 0.095 | (0,0,0.012) |

**C(r) ≈ (0.095, 0.783, 0.012)** — gần như thuần xanh lá. Điểm 2 (bề mặt đặc) gần như quyết định màu pixel — đúng logic: đó là bề mặt thật sự "nhìn thấy được". Điểm 3 (phía sau bề mặt đặc) gần như không đóng góp (0.012) vì T_3 tụt rất thấp sau khi "xuyên qua" đoạn 2 — đúng vật lý: bị che khuất, không thấy được.

*Insight:* đây là cách NeRF tự học được khái niệm che khuất (occlusion) mà không cần dạy luật hình học nào — chỉ cần công thức T_i·α_i, mạng tự học đặt σ lớn đúng tại bề mặt thật để khớp ảnh dự đoán với ảnh thật, và điều đó tự động làm phần phía sau bị "che" trong công thức.

### Kết nối với việc train

So C(r) dự đoán với màu pixel thật trong ảnh gốc, dùng loss MSE (Mean Squared Error, "sai số bình phương trung bình"):

```
Loss = Σ_rays || C(r)_dự_đoán − C(r)_thật ||²
```

Backpropagation chỉnh trọng số mạng để giảm loss, lặp hàng chục nghìn lần cho tới khi mạng học đúng hình dạng + màu sắc cảnh.

## Phần VIII: Kiến trúc MLP (Multi-Layer Perceptron, "mạng nơ-ron nhiều lớp" — chính là mạng nơ-ron F(x,y,z,θ,φ)→(r,g,b,σ) đã nhắc ở Phần II) 5D → 4D chi tiết

### Input đi qua Positional Encoding trước

Trước khi vào MLP, (x,y,z) và (θ,φ) không đưa thẳng vào mạng — được biến đổi qua hàm **positional encoding** γ(·) (dùng sin/cos ở nhiều tần số) để mạng dễ học chi tiết nhỏ hơn. Kết quả γ(x) (từ vị trí), γ(d) (từ hướng) có số chiều lớn hơn 3 và 2 chiều gốc nhiều lần. *(Công thức γ(·) cụ thể — học chi tiết riêng sau.)*

### Kiến trúc 8 lớp — density KHÔNG phụ thuộc hướng nhìn, màu THÌ CÓ

```
γ(x) (vị trí đã encode)
    │
    ▼
┌─────────────┐
│ 8 lớp FC     │  mỗi lớp 256 kênh, activation ReLU (Rectified Linear Unit, hàm f(x)=max(0,x))
│ (fully       │  → có 1 skip connection: NỐI THÊM γ(x) vào lại giữa mạng
│ connected)   │    (giúp thông tin vị trí không bị "phai" qua nhiều lớp)
└──────┬──────┘
       │
       ├──────────────────► σ (density)   ← chỉ phụ thuộc γ(x), KHÔNG có γ(d)
       │
       ▼
  vector đặc trưng 256 chiều
       │
       │   + γ(d) (hướng nhìn đã encode) ─┐
       ▼                                   │
┌─────────────┐                            │
│ 1 lớp FC nhỏ │◄───────────────────────────┘
│ (128 kênh)   │
└──────┬──────┘
       ▼
┌─────────────┐
│ lớp cuối     │  activation Sigmoid (ép ra khoảng [0,1])
└──────┬──────┘
       ▼
      (r, g, b)
```

### Chi tiết từng lớp — số chiều cụ thể qua từng bước

**"1 lớp FC" là phép toán gì:** `output = activation(W·input + b)` — W là ma trận trọng số học được (số hàng=số kênh output, số cột=số kênh input), b là bias, activation là hàm phi tuyến (ReLU ở đây).

**Input:** γ(x) — với L=10 (Phần X): mỗi tọa độ x,y,z qua 2×10=20 số (sin+cos ở 10 tần số) → 3×20=**60 chiều**.

| Lớp | Input → Output | Phép toán |
|---|---|---|
| Lớp 1 | 60 → 256 | FC + ReLU |
| Lớp 2 | 256 → 256 | FC + ReLU |
| Lớp 3 | 256 → 256 | FC + ReLU |
| Lớp 4 | 256 → 256 | FC + ReLU |
| **Skip connection** | nối γ(x) (60 chiều) vào output lớp 4 (256 chiều) | ghép (concatenate) → **316 chiều** |
| Lớp 5 | 316 → 256 | FC + ReLU |
| Lớp 6 | 256 → 256 | FC + ReLU |
| Lớp 7 | 256 → 256 | FC + ReLU |
| Lớp 8 | 256 → 256 | FC (nhánh ra σ thường không qua ReLU) |

**Rẽ nhánh sau lớp 8** — output 256 chiều dùng chung làm input cho 2 việc:

- **Nhánh σ:** `256 → 1` (1 lớp FC nhỏ) — chỉ dùng đúng 256 số xuất phát từ γ(x), **không có γ(d) lẫn vào** → đây là lý do cơ học khiến σ không phụ thuộc hướng nhìn.
- **Nhánh màu:** giữ nguyên vector đặc trưng 256 chiều, đi tiếp bước dưới.

**Nối hướng nhìn vào nhánh màu:** γ(d) (L=4 → 3×2×4=**24 chiều**) ghép với vector đặc trưng 256 chiều → **280 chiều**.

| Lớp | Input → Output | Phép toán |
|---|---|---|
| FC nhỏ | 280 → 128 | FC + ReLU |
| Lớp cuối | 128 → 3 | FC + **Sigmoid** |

**Vì sao lớp cuối dùng Sigmoid, không dùng ReLU như các lớp trước:** Sigmoid `f(x)=1/(1+e^(-x))` luôn cho ra giá trị nằm **chính xác trong (0,1)** bất kể input là số gì — khớp đúng yêu cầu màu RGB chuẩn hóa phải nằm [0,1]. ReLU chỉ chặn dưới ở 0, không chặn trên — output có thể ra số rất lớn, không hợp lệ làm giá trị màu.

**Tóm luồng dữ liệu đầy đủ số chiều:**

```
γ(x)[60] → 4 lớp FC[256] → ghép γ(x) lại[316] → 4 lớp FC[256]
                                                        │
                            ┌───────────────────────────┤
                            ▼                            ▼
                     FC[256→1] = σ            vector đặc trưng[256]
                                                        │
                                              ghép γ(d)[24] → [280]
                                                        │
                                              FC[280→128] + ReLU
                                                        │
                                              FC[128→3] + Sigmoid = (r,g,b)
```

### Vì sao thiết kế lệch như vậy (density tách riêng, không nhận hướng nhìn)

Chủ đích vật lý: **hình dạng vật thể (density/σ) cố định**, không đổi dù nhìn từ hướng nào — cái ly vẫn ở đúng chỗ đó dù đứng bên trái hay bên phải. Nhưng **màu sắc quan sát được có thể đổi theo hướng nhìn** (hiện tượng **view-dependent**: bề mặt bóng, phản chiếu, ánh kim loại — nhìn góc khác thấy màu/độ sáng khác). Vì vậy:
- σ chỉ nhận γ(x) → đảm bảo hình dạng nhất quán mọi góc nhìn.
- (r,g,b) nhận cả γ(x) (qua vector đặc trưng 256 chiều) và γ(d) → cho phép mạng mô phỏng hiệu ứng phản chiếu/ánh sáng đổi theo góc nhìn.

*Insight:* đây là 1 trong những quyết định thiết kế thông minh nhất của NeRF — tách bạch "cái gì không đổi theo góc nhìn" (hình học) và "cái gì đổi theo góc nhìn" (ánh sáng/màu) ngay trong kiến trúc mạng, thay vì để mạng tự mò — giúp NeRF render được vật liệu bóng/phản chiếu chân thực.

**Nguồn gốc chi tiết — đối chiếu với đúng nguyên văn paper (mục 3):** *"We encourage the representation to be multiview consistent by restricting the network to predict the volume density σ as a function of only the location x, while allowing the RGB color c to be predicted as a function of both location and viewing direction. [...] the MLP F_Θ first processes the input 3D coordinate x with 8 fully-connected layers (using ReLU activations and 256 channels per layer), and outputs σ and a 256-dimensional feature vector. This feature vector is then concatenated with the camera ray's viewing direction and passed to one additional fully-connected layer (using a ReLU activation and 128 channels) that output the view-dependent RGB color."* — khớp đúng số lớp/số kênh/activation đã vẽ ở sơ đồ trên.

**Lưu ý về skip connection:** đoạn văn chính của paper **không ghi rõ vị trí cụ thể** của skip connection (nối lại γ(x) giữa 8 lớp) — chi tiết "nối lại ở đúng lớp thứ 5" đến từ **code gốc tác giả công bố** (repo GitHub chính thức của nhóm tác giả, file kiến trúc mạng), không phải trích trực tiếp từ văn bản paper. Về triển khai thực tế thì đúng là skip ở lớp 5, nhưng khi trích dẫn cho báo cáo đồ án nên ghi rõ nguồn là "theo code công bố", không gán cho chính văn bản paper.

## Phần IX: Hierarchical Sampling — chi tiết đầy đủ

### Vấn đề

Nhìn bảng ví dụ Phần VII: chỉ điểm 2 (bề mặt, đóng góp 0.783) thực sự quan trọng. Điểm 1,3 gần như phí công. Nếu sample đều tăm tắp (N=64 dàn đều), phần lớn điểm rơi vào khoảng không (σ≈0) — lãng phí, trong khi vùng bề mặt thật chỉ được vài điểm "chạm trúng".

**Ý tưởng:** sample dày hơn ở chỗ quan trọng (gần bề mặt), thưa hơn ở chỗ toàn không khí.

### Cách làm — 2 mạng, 2 lượt sample

**Lượt 1 (mạng coarse):**
1. Lấy N_c điểm dàn đều dọc tia (stratified sampling, Phần VI).
2. Đưa qua mạng coarse → (c_i,σ_i) từng điểm.
3. Tính trọng số **w_i = T_i · α_i** (chính là số hạng trong công thức volume rendering, bỏ màu c_i ra — đo "điểm này quan trọng/đóng góp bao nhiêu", không quan tâm màu gì).

Với ví dụ Phần VII: w_1=0.095, w_2=0.783, w_3=0.012 → chuẩn hóa (chia tổng ≈0.89) → điểm 2 chiếm ~88% "xác suất quan trọng", điểm 1 ~11%, điểm 3 ~1.3%.

**Lượt 2 (importance sampling):**
4. Coi {w_i chuẩn hóa} là 1 phân phối xác suất (PDF) dọc tia — chỗ w cao "hút" nhiều điểm mẫu mới.
5. Dùng **inverse transform sampling**: dựng hàm phân phối tích lũy (CDF) từ PDF, sinh N_f số ngẫu nhiên đều [0,1], "tra ngược" qua CDF ra vị trí t tương ứng → N_f điểm mới tự động tập trung dày quanh vùng w cao.

   Ví von: như trải 1 sợi dây cao su dọc trục t, kéo giãn mạnh ở chỗ w cao (điểm 2), kéo dẹt ở chỗ w thấp (điểm 1,3) — rải đều điểm mới trên dây đã giãn. Chỗ giãn nhiều tự nhiên hứng nhiều điểm hơn.

**Lượt 3 (mạng fine):**
6. Gộp N_c điểm cũ + N_f điểm mới (vd 64+128=192), sắp lại theo t.
7. Đưa toàn bộ qua mạng **fine** (mạng thứ 2 riêng, không dùng lại coarse) → volume rendering lại từ đầu → màu pixel cuối cùng, chính xác hơn vì tập trung đúng chỗ quan trọng.

### Train cả 2 mạng cùng lúc

```
Loss = Loss(màu từ mạng coarse) + Loss(màu từ mạng fine)
```

Cả 2 so với cùng 1 màu pixel thật — mạng coarse vẫn phải học tốt vì nó quyết định trọng số w hướng dẫn nơi lấy mẫu cho mạng fine — coarse học tệ thì lượt sample 2 sẽ sai chỗ.

*Insight:* hierarchical sampling là dạng "học đi đôi với tự tìm chỗ đáng học" — mạng coarse không cần chính xác cao, chỉ cần chỉ đúng vùng đáng chú ý (phác thảo thô), rồi dồn tài nguyên tính toán (mạng fine, nhiều điểm hơn) vào đúng vùng đó thay vì chia đều lãng phí.

### Lưu ý quan trọng — KHÔNG phải importance sampling đúng nghĩa (paper tự làm rõ, cuối mục 5.2)

Dễ nhầm hierarchical sampling với kỹ thuật **importance sampling** kinh điển trong thống kê (lấy mẫu theo đúng phân phối xác suất để ước lượng kỳ vọng không chệch). Paper tự phân biệt rõ 2 thứ này: hierarchical sampling ở đây nhắm tới **mục tiêu tương tự** importance sampling, nhưng cách dùng khác — coi N_f mẫu lấy thêm như **cách rời rạc hóa không đồng đều (nonuniform discretization) của toàn miền tích phân [tₙ,t_f]**, chứ **không** coi mỗi mẫu là 1 ước lượng xác suất độc lập cho toàn bộ tích phân (đúng nghĩa importance sampling thống kê sẽ cần thêm bước chia lại trọng số 1/pdf(mẫu) cho mỗi mẫu để giữ tính không chệch — NeRF không làm bước đó, chỉ đơn giản dùng tất cả N_c+N_f điểm làm input volume rendering bình thường như nhau). Phân biệt này không ảnh hưởng tới cách cài đặt (vẫn làm đúng 7 bước đã nêu), chỉ là điểm cần biết để không hiểu nhầm thuật ngữ khi đọc thêm tài liệu thống kê về importance sampling.

## Phần X-sơ bộ: Implementation Details & Hyperparameters (mục 5.3 paper) — chi tiết train thực tế

*(Phần lý thuyết thuật toán đã xong ở trên — đây là các con số/thiết lập cụ thể khi thực sự chạy train, cần cho Chương 4 đồ án khi cài đặt thử nghiệm.)*

### Hàm loss đầy đủ (Eq. 6 paper)

```
L = Σ_{r∈R} [ ‖Ĉ_c(r) − C(r)‖₂² + ‖Ĉ_f(r) − C(r)‖₂² ]
```

**Chú thích ký hiệu:** `R` = tập hợp các tia trong 1 batch (không phải toàn bộ ảnh — chỉ 1 phần được chọn ngẫu nhiên mỗi vòng lặp). `C(r)` = màu pixel **thật** (ground truth) ứng với tia r. `Ĉ_c(r)` = màu dự đoán từ mạng **coarse**. `Ĉ_f(r)` = màu dự đoán từ mạng **fine**. `‖·‖₂²` = bình phương chuẩn Euclid (tổng bình phương từng thành phần r,g,b của hiệu 2 màu).

Đây chính là công thức MSE đã học ở Phần VII, nhưng viết **đầy đủ cho cả 2 nhánh** coarse+fine cộng lại — đã giải thích lý do ở Phần IX (cần tối ưu cả coarse vì nó quyết định cách lấy mẫu cho fine).

### Quy trình 1 vòng lặp train (tóm tắt lại theo đúng mục 5.3)

1. Lấy ngẫu nhiên 1 **batch tia** từ toàn bộ pixel của toàn bộ ảnh trong dataset (không phải lấy hết pixel của 1 ảnh — lấy ngẫu nhiên xuyên suốt nhiều ảnh khác nhau trong 1 batch).
2. Với mỗi tia: lấy N_c mẫu theo stratified sampling (Phần VI) → chạy mạng coarse.
3. Từ output coarse, chạy hierarchical sampling (Phần IX) → thêm N_f mẫu → chạy mạng fine trên N_c+N_f mẫu.
4. Volume rendering (Phần VII) cho cả 2 nhánh → Ĉ_c(r), Ĉ_f(r).
5. Tính loss L (công thức trên), backpropagation, cập nhật trọng số cả 2 mạng.

### Siêu tham số cụ thể dùng trong thực nghiệm của paper

| Siêu tham số | Giá trị |
|---|---|
| Batch size (số tia/vòng lặp) | 4096 tia |
| N_c (mẫu mạng coarse) | 64 |
| N_f (mẫu thêm cho mạng fine) | 128 (tổng 192 khi chạy fine) |
| Optimizer | Adam |
| Learning rate | bắt đầu 5×10⁻⁴, giảm dần theo hàm mũ (exponential decay) xuống 5×10⁻⁵ |
| Adam β₁, β₂, ε | 0.9, 0.999, 10⁻⁷ (mặc định) |
| Số vòng lặp tới hội tụ | ~100.000–300.000 vòng (tùy scene) |
| Thời gian train 1 scene | ~1-2 ngày trên 1 GPU NVIDIA V100 |

*Insight:* đây là lý do nhược điểm "train chậm" của NeRF gốc (đã nhắc ở ghi chú NeRF gốc vs cải tiến, cuối file) — 100k-300k vòng lặp, mỗi vòng phải chạy forward+backward qua 2 mạng MLP cho 4096×192 ≈ 786.000 điểm mẫu, là khối lượng tính toán rất lớn cho **1 scene duy nhất**.

## Vì sao các con số phía NeRF (N=64/128, MLP 8 lớp/256 kênh) — khác hẳn nhóm COLMAP

Nhóm thuật toán COLMAP ở Phần III (SIFT, RANSAC, P3P...) có nền tảng toán chặt chẽ — mọi con số (26, 5-point, bậc 4, công thức N lần lặp...) đều suy ra được từ định lý/công thức xác suất cụ thể. Ngược lại, các con số phía NeRF chủ yếu đến từ **thực nghiệm đánh đổi chất lượng/tốc độ**, không có công thức lý thuyết ép buộc:

- **N_c=64, N_f=128:** tác giả thử nhiều giá trị N trên các scene benchmark, đo PSNR (chỉ số chất lượng ảnh) so với thời gian train/render. Tăng N cải thiện chất lượng rất ít nhưng tăng compute tuyến tính — 64/128 là điểm "đủ tốt" tác giả chốt làm mặc định.
- **8 lớp, 256 kênh:** mạng chỉ cần "học thuộc" 1 scene duy nhất (không cần tổng quát hóa qua nhiều scene như mạng phân loại ảnh) — không cần sâu/rộng như ResNet hàng trăm lớp. 8×256 đủ dung lượng nhớ chi tiết hình học+màu của 1 scene, đủ nhỏ để train trong thời gian chấp nhận được.
- **Skip connection ở lớp 5:** thực nghiệm cho thấy nối lại input ở giữa mạng giúp gradient lan truyền tốt hơn, giảm "quên" thông tin vị trí gốc qua nhiều lớp — không có công thức chính xác cho "lớp thứ mấy tối ưu", giữa mạng là lựa chọn thực nghiệm hợp lý.

*Insight:* đọc paper deep learning thì đừng cố tìm "công thức chứng minh vì sao 256" — không có, chỉ có "thử và đo kết quả trên benchmark". Khác hẳn tinh thần các thuật toán hình học cổ điển ở Phần III.

---

## Ghi chú: đây là NeRF gốc hay NeRF cải tiến

Toàn bộ nội dung trên (ray, MLP 5D→4D, volume rendering, hierarchical sampling) là **NeRF gốc**: Mildenhall et al., "NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis", ECCV (European Conference on Computer Vision, hội nghị khoa học chuyên ngành Thị giác máy tính ở Châu Âu) 2020. Nhược điểm nổi tiếng: train rất chậm (1-2 ngày/scene), render không real-time, kém với cảnh ngoài trời/không giới hạn (unbounded), cần pose chính xác.

**NeRF cải tiến** (ứng viên cho Chương 3 đồ án — chọn 1 để trình bày chi tiết):

| Tên | Cải tiến chính |
|---|---|
| Instant-NGP (NVIDIA, 2022) | Train nhanh ~1000 lần nhờ hash encoding thay MLP thuần |
| Mip-NeRF | Xử lý alias/blur khi camera zoom/khoảng cách khác nhau, dùng "cone" thay tia mảnh |
| Mip-NeRF 360 | Mở rộng Mip-NeRF cho cảnh ngoài trời/không giới hạn |
| NeRF++ | Giải quyết cảnh unbounded bằng tách nền xa xử lý riêng |
| Plenoxels | Bỏ hẳn mạng nơ-ron, dùng voxel grid + nội suy, train siêu nhanh |
| 3D Gaussian Splatting (2023) | Biểu diễn cảnh bằng hàng triệu Gaussian 3D, render real-time, đang rất hot |

---

## Related Work (Các công trình liên quan) — mục 2 paper gốc, diễn giải cho Chương 2 đồ án

*(Tóm tắt/diễn giải lại bằng lời riêng, không dịch nguyên văn — paper gốc: Mildenhall et al. 2020, arXiv:2003.08934)*

### Bối cảnh: 2 hướng tiếp cận có trước NeRF

Trước NeRF có 2 hướng chính để biểu diễn cảnh/vật thể 3D cho bài toán render — NeRF đối chiếu với cả 2 để làm rõ đóng góp của mình.

### Nhánh 1 — Neural 3D shape representations (biểu diễn hình dạng bằng mạng nơ-ron)

Hướng này biểu diễn hình dạng 3D liên tục dạng **level set** — train 1 mạng ánh xạ tọa độ (x,y,z) sang signed distance hoặc occupancy field. Hạn chế ban đầu: cần **ground-truth 3D geometry** để train (thường từ bộ dữ liệu 3D tổng hợp như ShapeNet), không áp dụng trực tiếp cho cảnh thật.

Công trình sau nới lỏng yêu cầu này bằng **hàm render khả vi (differentiable rendering)** — tối ưu biểu diễn hình dạng ẩn chỉ từ ảnh 2D:
- **Niemeyer et al.:** bề mặt = 3D occupancy field, dùng phương pháp số tìm giao điểm tia-bề mặt, tính đạo hàm bằng implicit differentiation; giao điểm đưa vào 1 neural texture field riêng dự đoán màu khuếch tán.
- **Sitzmann et al.:** tại mỗi tọa độ 3D, mạng xuất feature vector + RGB; dùng RNN "đi dọc" từng tia để tự quyết định vị trí bề mặt.

**Hạn chế chung:** dù biểu diễn được hình học độ phân giải cao, nhóm này vẫn giới hạn ở hình dạng đơn giản, kết quả render bị mờ/nhòe quá mức (oversmoothed). → NeRF khác: không học hình dạng bề mặt tường minh, mà học trực tiếp **radiance field 5D**, nhờ đó biểu diễn được hình học+vẻ ngoài độ phân giải cao hơn, render ảnh photorealistic cho cảnh phức tạp.

### Nhánh 2 — View synthesis và image-based rendering

Với ảnh lấy mẫu dày đặc, có thể tổng hợp góc nhìn mới chỉ bằng nội suy light field đơn giản. Với ảnh thưa hơn (như đồ án), có 2 lớp phương pháp chính:

**(a) Mesh-based:** mesh với vẻ ngoài khuếch tán hoặc phụ thuộc góc nhìn, tối ưu bằng differentiable rasterizer/pathtracer qua gradient descent. Hạn chế: tối ưu dựa trên gradient từ reprojection ảnh thường khó hội tụ (dễ rơi cực tiểu cục bộ/loss landscape xấu), và cần có sẵn **mesh mẫu với topology cố định** làm khởi tạo — thường không có sẵn với cảnh thật tự do.

**(b) Volumetric:** biểu diễn thực tế hình dạng/vật liệu phức tạp, phù hợp tối ưu gradient, ít artifact hơn mesh-based.
- Sớm nhất: tô màu trực tiếp voxel grid từ ảnh quan sát.
- Gần đây: train mạng sâu trên tập dữ liệu nhiều scene để **dự đoán ra biểu diễn thể tích đã lấy mẫu**, dùng alpha-compositing hoặc compositing đã học để render.
- Nhóm khác: kết hợp CNN + voxel grid lấy mẫu, tối ưu riêng từng scene — CNN bù artifact từ voxel độ phân giải thấp, hoặc cho voxel đổi theo thời gian/animation.

**Hạn chế cốt lõi nhóm volumetric:** khả năng mở rộng lên độ phân giải cao bị giới hạn nghiêm trọng do **lấy mẫu rời rạc** (voxel) — ảnh độ phân giải cao hơn cần lưới mịn hơn, tốn bộ nhớ tăng theo cấp số nhân.

**→ Đây là vấn đề NeRF giải quyết:** thay vì lấy mẫu rời rạc, NeRF mã hóa 1 **khối liên tục** ngay trong trọng số mạng nơ-ron — chất lượng render cao hơn hẳn nhóm volumetric trước, chi phí lưu trữ chỉ bằng 1 phần nhỏ.

*Insight cho đồ án:* đây là khung trả lời 2 câu hỏi bắt buộc của Chương 2 (`huongdantrinhbay.rtf`) — "người ta đã làm gì rồi" (2 nhánh trên, mỗi nhánh có hạn chế riêng) và "NeRF muốn làm gì tiếp" (mã hóa liên tục trong MLP, không cần ground-truth 3D, không lấy mẫu rời rạc).

*(Chưa làm: mục 5.1 Positional Encoding, mục 7 Results/Experiments của paper gốc.)*

*(Chưa ghi: Phần X - Positional Encoding γ(·) chi tiết. Sẽ bổ sung sau khi học tiếp.)*
