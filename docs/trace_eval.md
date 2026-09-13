# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Nguyễn Huy Hùng
> **Mã Sinh Viên / Mã Học viên:** 2A202602990  
> **Chủ đề Lựa chọn:** Trợ lý dinh dưỡng cá nhân hóa  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 5 / 5 | Agent có thể tra cứu hồ sơ, đọc mục tiêu và ràng buộc dị ứng rồi lập thực đơn phù hợp. |
| **2. Tool Interaction** | 4 / 5 | Bài toán cần gọi MCP Server để lấy hồ sơ dinh dưỡng và tạo thực đơn. |
| **3. Dynamic Decision** | 3 / 5 | Mục tiêu calo và dị ứng trong hồ sơ quyết định tham số lập thực đơn tiếp theo. |
| **4. Long Horizon Goal** | 4 / 5 | Mục tiêu lập thực đơn nhiều ngày cần duy trì ràng buộc dinh dưỡng xuyên suốt các bước. |
| **TỔNG ĐIỂM AGENTIC FIT** | **16 / 20** | *Bài toán rất phù hợp triển khai Agentic System.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "query": "Tôi muốn tạo thực đơn cho ngày mai, 2000 calo, ăn mặn, tất cả các bữa trong ngày",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "create_meal_plan",
    "arguments": {
      "date_range": "ngày mai",
      "calorie_target": 650,
      "dietary_restrictions": "ăn mặn",
      "meal_time": "buổi sáng"
    },
    "observation": {
      "status": "SUCCESS",
      "date_range": "ngày mai",
      "calorie_target": 650,
      "dietary_restrictions": "ăn mặn",
      "meal_time": "buổi sáng",
      "nutrition_note": "Hãy dùng các ràng buộc này để xây dựng thực đơn cụ thể."
    },
    "latency_ms": 4739.77
  },
  {
    "step": 2,
    "query": "Tôi muốn tạo thực đơn cho ngày mai, 2000 calo, ăn mặn, tất cả các bữa trong ngày",
    "action_type": "FINAL_ANSWER",
    "thought": "Tổng hợp kết quả từ MCP Server thành công.",
    "output": "# Thực đơn cho ngày mai - 2000 calo (Ăn mặn)\n\nDựa trên thông tin từ hệ thống, tôi xin lưu ý rằng dữ liệu trả về chỉ cung cấp thông tin chi tiết cho **buổi sáng với 650 calo**. Tuy nhiên, tôi sẽ xây dựng thực đơn đầy đủ cho cả ngày với 2000 calo theo yêu cầu:\n\n## **BUỔI SÁNG (650 calo)**\n- **Cơm tấm thịt nướng**: 1 suất (300g) - 450 calo\n- **Trứng ốp la**: 1 quả - 120 calo\n- **Canh chua tôm**: 1 bát nhỏ - 80 calo\n\n## **BUỔI TRƯA (600 calo)**\n- **Cơm**: 1.5 bát (200g) - 280 calo\n- **Cá kho tộ**: 1 đĩa nhỏ (120g) - 200 calo\n- **Rau cải luộc**: 1 bát (150g) - 30 calo\n- **Canh miso**: 1 bát - 60 calo\n\n## **BUỔI CHIỀU (450 calo)**\n- **Bánh chưng**: 2 miếng nhỏ - 200 calo\n- **Thịt gà luộc**: 1 đĩa (100g) - 150 calo\n- **Nước mắm chua cay**: để chấm - 0 calo\n- **Rau pickled**: 1 bát nhỏ - 100 calo\n\n## **BUỔI TỐI (300 calo)**\n- **Phở gà**: 1 tô (400ml) - 250 calo\n- **Bánh tráng nướng muối**: 1 tô nhỏ - 50 calo\n\n**Tổng cộng: ~2000 calo | Phong cách ăn: Mặn đặc trưng**",
    "latency_ms": 10.0
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Claude Haiku 4.5).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 4 lượt (nutrition_query: 3 lượt, create_meal_plan: 1 lượt).
- **Kết quả đẩy Repo nộp bài:** [x] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
