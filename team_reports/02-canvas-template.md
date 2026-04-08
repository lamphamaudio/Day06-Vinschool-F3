# AI Product Canvas — template

Điền Canvas cho product AI của nhóm. Mỗi ô có câu hỏi guide — trả lời trực tiếp, xóa phần in nghiêng khi điền.

---

## Canvas


|                   | Value                                                                                                                                                                                                                                                                                                             | Trust                                                                                                                                                                                                                                                                                                                                                                                                                                              | Feasibility                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được?                                                                                                                                                                                                                                             | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào?                                                                                                                                                                                                                                                                                                                                                  | Cost bao nhiêu/request? Latency bao lâu? Risk chính là gì?                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **Trả lời**       | 1. User: Người muốn đặt vé máy bay, người cần hỗ trợ thông tin vé máy bay 2. Pain: Khi hỏi một câu hỏi mơ hồ, AI không hỏi lại để confirm rõ thông tin mà chỉ thuần dùng rule base 3. AI đưa ra được đề xuất dựa vào dữ liệu trong database để làm rõ mục đích câu hỏi và đưa ra được câu trả lời phù hợp nhất | 1. Khi AI sai thì user nhận được thông tin sai lệnh về chuyến bay 2. Khi AI đề xuất chuyến bay, cần đưa ra link nguồn của chuyến bay, user có thể truy cập trực tiếp vào link để kiểm tra tính chính xác của câu trả lời 3.User có thể chỉnh lại các thông tin mà AI hiểu sai (điểm đi, điểm đến, ngày bay, số lượng hành khách, mức giá mong muốn) hoặc chọn lại chuyến bay đúng từ danh sách gợi ý để hệ thống trả kết quả mới chính xác hơn. | 1. Giả định cụ thể: MVP chỉ trả lời tư vấn và gợi ý chuyến bay (không xử lý thanh toán/đặt vé), dữ liệu lấy từ 1 API chuyến bay cập nhật mỗi 5 phút. 2. Cost ước lượng: ~0.003–0.015 USD/request (GPT-4o-mini), có thể giảm thêm nếu cache truy vấn phổ biến. 3. Latency mục tiêu: P50 ~1.5–2.5s, P95 ~4–6s/request (phụ thuộc thời gian gọi API chuyến bay). 4. Risk chính: dữ liệu giá/ghế hết nhanh hơn chu kỳ cập nhật; AI diễn giải đúng intent nhưng tổng hợp kết quả sai; API đối tác timeout/rate-limit gây trả lời chậm hoặc thiếu dữ liệu |


---

## Automation hay augmentation?

☐ Automation — AI làm thay, user không can thiệp
☐ Augmentation — AI gợi ý, user quyết định cuối cùng

**Justify:** Chọn Augmentation. AI chỉ nên gợi ý và tổng hợp phương án chuyến bay; user vẫn là người quyết định cuối cùng sau khi đối chiếu link nguồn vì giá/ghế thay đổi nhanh và AI có thể trả thông tin sai ở bước cuối.

Gợi ý: nếu AI sai mà user không biết → automation nguy hiểm, cân nhắc augmentation.

---

## Learning signal


| #   | Câu hỏi                                                                                                 | Trả lời                                                                                                                                                             |
| --- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | User correction đi vào đâu?                                                                             | Correction log theo phiên chat: user sửa intent (điểm đi/đến, ngày, ngân sách), user đổi lựa chọn chuyến bay, và feedback `Sai thông tin` khi đối chiếu link nguồn. |
| 2   | Product thu signal gì để biết tốt lên hay tệ đi?                                                        | (a) Tỷ lệ user chấp nhận gợi ý ngay lần đầu, (b) Tỷ lệ user phải sửa query/lọc lại, (c) Tỷ lệ click link nguồn xong quay lại báo sai, (d) CSAT sau phiên tư vấn.    |
| 3   | Data thuộc loại nào? ☐ User-specific · ☐ Domain-specific · ☐ Real-time · ☐ Human-judgment · ☐ Khác: ___ | ☑ User-specific · ☑ Domain-specific · ☑ Real-time · ☑ Human-judgment. Khác: outcome label (đặt vé/không đặt vé) để đánh giá chất lượng đề xuất.                     |


**Có marginal value không?** (Model đã biết cái này chưa? Ai khác cũng thu được data này không?)
Có. Giá trị biên đến từ correction theo ngữ cảnh người dùng + outcome thực tế sau khi đối chiếu link nguồn; đây là signal gắn với product flow, model nền không có sẵn và đối thủ khó có đủ ý nghĩa signal này nếu không có cùng hành vi user.

---

---

## Cách dùng

1. Điền Value trước — chưa rõ pain thì chưa điền Trust/Feasibility
2. Trust: trả lời 4 câu UX (đúng → sai → không chắc → user sửa)
3. Feasibility: ước lượng cost, không cần chính xác — order of magnitude đủ
4. Learning signal: nghĩ về vòng lặp dài hạn, không chỉ demo ngày mai
5. Đánh [?] cho chỗ chưa biết — Canvas là hypothesis, không phải đáp án

---

*AI Product Canvas — Ngày 5 — VinUni A20 — AI Thực Chiến · 2026*