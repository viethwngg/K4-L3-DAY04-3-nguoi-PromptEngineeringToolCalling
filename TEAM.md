# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: 3 nguoi
- Người đại diện / MSSV: Đàm Việt Hưng / 2A202602600
- Tên repo: `K4-L3-DAY04-3-nguoi-PromptEngineeringToolCalling`
- URL repo, nhánh nộp, commit chốt: https://github.com/viethwngg/K4-L3-DAY04-3-nguoi-PromptEngineeringToolCalling
- Deadline áp dụng và link thông báo đổi hạn nếu có: chưa có

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Đàm Việt Hưng | 2A202602600 | https://github.com/viethwngg/K4-L3-DAY04-3-nguoi-PromptEngineeringToolCalling | Xây dựng dữ liệu test nhóm; soạn file eval_group.json; làm 10 case nhóm | `data/eval_group.json` và commit 10 case nhóm |
| Lê Trung Kiên | 2A202602748 | https://github.com/viethwngg/K4-L3-DAY04-3-nguoi-PromptEngineeringToolCalling | làm  version2,3 và chạy version log | `system_prompt.md, tools.yaml,version_log.csv` prompt v1, v2, v3 |
| Ngô Anh Tú | 2A202602386 | https://github.com/viethwngg/K4-L3-DAY04-3-nguoi-PromptEngineeringToolCalling | làm version2 và thiết kế UI cho chat | `starter_v0/ui.py`, `starter_v0/requirements.txt`, `starter_v0/transcripts/ui_v1_gemini_20260915T202837287303.transcript.json`; commit `67f35e4` |
## Nhận xét chung

- Kết quả và bằng chứng: Team eval có 10/10 case pass với 5 single-turn và 5 multi-turn trong `starter_v0/data/eval_group.json`. Safety eval có 12/12 case pass với `provider_error_cases: 0`. Evidence chính nằm trong `starter_v0/runs/v3_B_group_openai_20260915T202711936864.json`, `starter_v0/runs/v3_B_adversarial_openai_20260915T203942469973.json` và `starter_v0/artifacts/REPORT.md`.
- Thay đổi hiệu quả nhất: Cải thiện `system_prompt.md` để xử lý latest intent, corrected employee/asset ID, clarification cho QA, và gọi song song các tool cần thiết. Runtime guard trong `starter_v0/agent.py` bổ sung kiểm soát confirmation giả/stale và ngăn internal identifier đi vào external search.
- Giới hạn còn lại: v0 Gemini không dùng để so sánh metric vì hết quota. UI/transcript và việc xác nhận commit/URL VLearn của từng thành viên cần được kiểm tra lần cuối trước khi nộp.
- Cách phân công và tích hợp: Đàm Việt Hưng xây dựng 10 team eval cases; Lê Trung Kiên phát triển prompt v1-v3 và version log; Ngô Anh Tú xây dựng UI dark theme và reviewed transcript. Các thay đổi được tích hợp qua các commit kỹ thuật trên branch chung.

## INDIVIDUAL

Sao chép mục này cho từng thành viên.

### Họ và tên — MSSV

### Đàm Việt Hưng — 2A202602600

- Phần việc và file/commit/PR: Xây dựng bộ 10 case nhóm gồm 5 single-turn và 5 multi-turn trong `starter_v0/data/eval_group.json`; commit `1222624`.
- Quyết định, khó khăn và cách xử lý: Giữ nguyên dataset qua các version để so sánh công bằng; bổ sung các case về policy routing, clarification, multi-turn correction và parallel tool calls.
- Điều đã học: Eval cần kiểm tra cả tên tool, argument, thứ tự/state nhiều lượt và boundary safety; chỉ nhìn câu trả lời text là chưa đủ.
- AI/công cụ đã dùng và cách kiểm tra: Dùng VS Code, Git và eval runner Python; kiểm tra bằng `python run_eval.py --provider openai --model gpt-4o --version v3 --suite group --eval-cases data/eval_group.json`.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Chưa ghi nhận.

### Lê Trung Kiên — 2A202602748

- Phần việc và file/commit/PR: Phát triển prompt v1-v3 trong `starter_v0/artifacts/system_prompt.md`, cập nhật `version_log.csv` và phối hợp kiểm tra `tools.yaml`; các commit tiêu biểu `a6ec1af`, `c767a87`, `b3177f0`, `ec16257`.
- Quyết định, khó khăn và cách xử lý: Dùng failure trace để thêm rule cho latest intent, corrected value, QA environment, parallel lookup và confirmation boundary; đối chiếu từng thay đổi với run JSON.
- Điều đã học: Prompt phải mô tả rõ precedence của state nhiều lượt và enum hợp lệ; metric chỉ có ý nghĩa khi không có provider error và trace đã được review.
- AI/công cụ đã dùng và cách kiểm tra: Dùng VS Code, Git, OpenAI gpt-4o và eval runner; kiểm tra team suite 10/10 và adversarial suite 12/12.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Chưa ghi nhận.

### Ngô Anh Tú — 2A202602386

- Phần việc và file/commit/PR: Xây dựng UI Helpdesk dark theme và reviewed transcript; các file gồm `starter_v0/ui.py`, `starter_v0/requirements.txt` và `starter_v0/transcripts/ui_v1_gemini_20260915T202837287303.transcript.json`; commit `67f35e4`.
- Quyết định, khó khăn và cách xử lý: Hiển thị tool call, kết quả và transcript để người dùng có thể kiểm tra hành vi agent thay vì chỉ xem câu trả lời cuối.
- Điều đã học: UI và transcript là evidence kỹ thuật; cần kiểm tra cả trạng thái lỗi, tool input, kết quả và version của phiên chạy.
- AI/công cụ đã dùng và cách kiểm tra: Dùng VS Code, Git và chạy thử UI/transcript theo cấu hình project; rà soát transcript không chứa API key hoặc dữ liệu thật.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Chưa ghi nhận.
