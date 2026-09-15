# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Nhóm Một
- Người đại diện / MSSV: 2A202602756
- Tên repo: `K4B-Day4-Nhom-Mot`
- URL repo, nhánh nộp, commit chốt:https://github.com/Anreak/K4B-Day4-Nhom-Mot
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
|Nguyễn Nhật Thăng |2A202602727 | | | |
|Nguyễn Minh Quyền |2A202602438 | | | |
|Vương Việt Hoàng |2A202602528 | VietHoang04-sys | eval_group, kiểm tra case và đánh giá tool routing | `starter_v0/data/eval_group.json`, `starter_v0/artifacts/REPORT.md` |
|Nguyễn Quang Hữu |2A202602756 | | | |

## Nhận xét chung

- Kết quả và bằng chứng:
- Thay đổi hiệu quả nhất:
- Giới hạn còn lại:
- Cách phân công và tích hợp:

## INDIVIDUAL

Sao chép mục này cho từng thành viên.

### Nguyễn Nhật Thăng — 2A202602727

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:


### Nguyễn Minh Quyền — 2A202602438

- Phần việc và file/commit/PR: Phụ trách cải thiện tools.yaml cho phiên bản v1. Chỉnh sửa phần description của các tool lookup_user, inspect_device và check_service_status, không thay đổi parameters. Mục tiêu là cải thiện tool routing, xử lý thông tin thiếu và mapping argument. Chạy đánh giá bằng run_eval.py và kiểm tra kết quả v0 → v1. Hỗ trợ cãi thiện phiên bản v3
- Quyết định, khó khăn và cách xử lý:Quyết định chỉ thay đổi description để đánh giá riêng tác động của tool definitions, không thay đổi system_prompt hoặc logic chương trình. Khó khăn ban đầu là lỗi cú pháp YAML do indentation khi viết description. Sau đó kiểm tra lỗi từ traceback, sửa lại format YAML và chạy lại evaluation. Kết quả cải thiện từ 21/30 lên 26/30 case, tương ứng từ 70% lên 86.67%. Một số lỗi còn lại thuộc nhóm confirmation boundary và các case H17, H19 sẽ tiếp tục được xem xét.
- Điều đã học:Hiểu rõ hơn cách thiết kế tool description cho agent, đặc biệt là cách mô tả điều kiện gọi tool, thông tin bắt buộc và quy tắc mapping argument. Học được rằng chỉ cần thay đổi description cũng có thể ảnh hưởng đáng kể đến khả năng routing và sử dụng tool của LLM. Ngoài ra, hiểu cách sử dụng kết quả evaluation để xác định lỗi và thực hiện cải tiến theo từng phiên bản.
- AI/công cụ đã dùng và cách kiểm tra:Sử dụng OpenRouter làm provider để chạy agent evaluation. Sử dụng Python và run_eval.py để chạy bộ 30 test case. Kiểm tra các metric gồm case_accuracy, tool_routing_accuracy, argument_accuracy và multiturn_accuracy. So sánh kết quả v0 và v1
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Vương Việt Hoàng — 2A202602528

- Phần việc và file/commit/PR: Làm phần `eval_group`: thiết kế và kiểm tra bộ test 10 case cho nhóm, gồm 5 case một lượt và 5 case nhiều lượt trong `starter_v0/data/eval_group.json`; xác nhận trường `expect`/`failure_type` phù hợp với agent loop và tool routing; hỗ trợ đối chiếu kết quả đánh giá với báo cáo nhóm.
- Quyết định, khó khăn và cách xử lý: Chọn tập case tập trung vào các trường hợp gây lỗi thường gặp của agent như `missing_info`, `wrong_tool`, `wrong_arg_value`, `unnecessary_tool`, và multi-turn intent correction. Khi viết case, ưu tiên giữ tiêu chí rõ ràng, không mơ hồ và kiểm tra hành vi đúng mục tiêu của tool; nếu case quá mơ hồ, sửa lại để agent phải hỏi thêm thông tin thay vì đoán.
- Điều đã học: Evaluator cần khớp chặt với quy tắc nghiệp vụ, không chỉ viết câu hỏi tự nhiên. Trong multi-turn, trạng thái và ý định mới nhất phải được ưu tiên hơn lượt trước, và các tình huống hủy/xác nhận cần được định nghĩa rõ để tránh agent thực hiện tool sai.
- AI/công cụ đã dùng và cách kiểm tra: Sử dụng GitHub Copilot / ChatGPT để rà soát tính hợp lý của case, kiểm tra cú pháp JSON và xác nhận schema của evaluation set; test bằng script chạy `run_eval.py` và review lỗi để chỉnh case cho phù hợp.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Trong buổi nộp nhóm, đã tự submit URL repo chung trên VLearn theo hướng dẫn của lớp.

### Nguyễn Quang Hữu — 2A202602756

- Phần việc và file/commit/PR:  Xử lý phân tích và viết các report, cũng như chia việc, file report và team, và xử lý front-end
- Quyết định, khó khăn và cách xử lý: Xử lý chia việc, phân tích yêu cầu của đề bài, có khá nhiều thông tin từ rải rác, nên tôi đã dùng ai để gom chúng lại, và xử lý viết báo cáo, cũng như các thông tin được thành viên khác tạo, tôi tổng hợp chúng và điền report
- Điều đã học: Cách hệ thống sử dụng tool, system prompt , qua việc đọc và phân tích tài liệu và code, hiểu được những lỗ hổng bảo mật, những lý do cho lỗi, và các cách fix lỗi qua việc phân tích việc của các thành viên khác
- AI/công cụ đã dùng và cách kiểm tra: Đã sử dụng ai để tổng hợp và phân tích thông tin rải rác trong project, cũng như sử dụng ai để wording lại các ý chính
- Thời điểm đã tự nộp URL repo chung trên VLearn: 10pm 15/9/2026
