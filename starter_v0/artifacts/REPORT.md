# Day 04 Lab v3 Report — Trợ lý AI của nhóm

- Lĩnh vực tự chọn: IT Helpdesk
- Nhiệm vụ và luồng cơ bản đã chốt trước v0: Trợ lý IT Helpdesk; nhận yêu cầu, hỏi lại khi thiếu mã thiết bị/mã nhân viên hoặc thông tin xác nhận, chọn công cụ phù hợp để tra trạng thái dịch vụ, kiểm tra thiết bị, tra người dùng, tìm hướng dẫn/chính sách nội bộ và trình bày kết quả dựa trên dữ liệu công cụ. Nếu người dùng muốn tạo ticket, chỉ ghi dữ liệu sau khi xác nhận đúng nội dung.
- Đường dẫn bộ 30 câu cơ bản và 12 câu an toàn; commit chốt bộ trước v0: Bộ IT cố định của starter tại `starter_v0/data/eval_base.json` (30 câu: 20 một lượt, 10 nhiều lượt) và `starter_v0/data/eval_adversarial.json` (12 câu an toàn). Hai file có từ commit gốc `2c1a5ec`.
- Chức năng mở rộng ngoài luồng cơ bản (nếu có; tối đa 10 trong tổng 100 điểm):

## Team

- Team: Nhóm Một
- Thành viên và INDIVIDUAL: [TEAM.md](../../TEAM.md)
- Members: Nguyễn Nhật Thăng, Nguyễn Minh Quyền, Vương Việt Hoàng, Nguyễn Quang Hữu
- Provider/model: OpenRouter

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Agent hỗ trợ IT Helpdesk của Northstar Labs bằng cách tra dữ liệu giả lập về dịch vụ, thiết bị, người dùng, hướng dẫn và chính sách; agent có thể hỏi lại khi thiếu thông tin, tổng hợp finding và đề xuất ticket. Dữ liệu chỉ là snapshot của bài lab, không phản ánh hệ thống thật; trong Web UI, ticket chỉ được ghi sau khi người dùng xác nhận đúng nội dung qua nút xác nhận.

**Link dùng thử:**

> Chạy tại máy theo [README.md](../../README.md), rồi mở `http://localhost:8501`. 

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| `clarify` | Hỏi lại khi thiếu thông tin hoặc cần xác nhận. | core |
| `search_kb` | Tìm bài hướng dẫn trong knowledge base IT giả lập. | core |
| `check_service_status` | Tra trạng thái dịch vụ theo môi trường production/staging. | core |
| `inspect_device` | Xem thông tin và chẩn đoán của thiết bị theo asset ID. | core |
| `lookup_user` | Tra nhân viên theo employee ID trong danh bạ hỗ trợ. | core |
| `format_incident_report` | Định dạng finding đã có thành báo cáo brief/technical/handoff. | core |
| `policy` | Tìm các mục trong chính sách IT nội bộ giả lập. | optional (starter) |
| `create_ticket` | Kiểm tra payload và tạo ticket local sau xác nhận đúng nội dung. | optional (starter) |
| `search_device_info` | Tìm thông tin công khai về hãng/model thiết bị qua Tavily; không gửi mã hay dữ liệu nội bộ. | optional (starter) |

Phân loại trên theo `track` trong các file `tools/<name>/TOOL.md`.

## A3. Câu hỏi mẫu

1. “VPN production hiện có đang gặp sự cố không?” — kỳ vọng gọi `check_service_status(service="vpn", environment="production")`.
2. “Kiểm tra riêng kết nối VPN trên LT-204.” — kỳ vọng gọi `inspect_device(asset_id="LT-204", check="vpn")`.
3. “Tìm hướng dẫn cấu hình Outlook profile trên Windows 11.” — kỳ vọng gọi `search_kb` với `category="email"`.

## A4. Kịch bản demo và bằng chứng hiện có

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Tra trạng thái VPN production (đã có một lượt chat lưu lại) | `check_service_status(service="vpn", environment="production")`; kết quả `degraded`, incident `INC-1042`. | Transcript mang nhãn v0; chưa có bằng chứng cải thiện ở v1–v3. | [`transcripts/v0_openrouter_20260915T194012034827_uXGfF4xn.transcript.json`](../transcripts/v0_openrouter_20260915T194012034827_uXGfF4xn.transcript.json); case `H01_service_status_routing` trong [run v0](../runs/v0_B_base_openrouter_20260915T183654405815.json). |


# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ
liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Optional và bonus tool evidence

Phần này chỉ điền khi nhóm có sử dụng optional tool hoặc tự xây bonus tool.
Phần chung tối đa 90 điểm; mở rộng tối đa 10 điểm, tổng tối đa 100. Công cụ tự xây để phục vụ luồng cơ bản của lĩnh vực mới thuộc phần chung. `policy`,
`create_ticket` và `search_device_info` là tool có sẵn, không phải tool mới do
nhóm tự xây.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in |  |  |  |
| External search + privacy boundary |  |  |  |
| Bonus: tool mới do nhóm tự xây |  |  |  |

## B6. Safety review

- Agent có bao giờ tự đoán asset ID hoặc employee ID không?
- Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?
- Ticket chỉ được tạo sau xác nhận rõ chưa?
- Tool result error nào cần review thủ công?

## B7. Technical reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào không thể chỉ nhìn automatic score?
- Nếu có thêm một vòng, nhóm sẽ thử hypothesis nào?

# PHẦN C — Checkout trước khi nộp

Phần này được hoàn thành sau khi toàn bộ code, evidence và report đã được đưa
lên repository chung. Nhóm chưa nên nộp link trên VLearn nếu reflection hoặc
commit evidence của bất kỳ thành viên nào còn thiếu.

## C1. Nhận xét chung của nhóm

Hoàn thành mục nhận xét chung trong [TEAM.md](../../TEAM.md). Dẫn tới các run, file và commit trong phần B để chứng minh kết quả. Ghi dưới đây đường dẫn tới mục đã hoàn thành:

> Link:

## C2. INDIVIDUAL của từng thành viên

Mỗi người tự viết và commit mục INDIVIDUAL của mình trong [TEAM.md](../../TEAM.md), nêu phần việc, bằng chứng kỹ thuật và điều đã học. Không yêu cầu chép lại cùng nội dung ở đây. Mỗi mục phải có file/commit/PR thật, không dùng commit tự đánh giá làm bằng chứng kỹ thuật duy nhất.

> Link các mục INDIVIDUAL:

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của
repository chung:

- [ ] `TEAM.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [ ] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [ ] Phần nhận xét chung trong TEAM.md đã hoàn thành và có evidence.
- [ ] Mỗi thành viên đã tự viết và commit mục INDIVIDUAL trong TEAM.md.
- [ ] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI
      và report đã có trong repository.
- [ ] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL:

- [ ] Tên repo đúng mẫu K4-L3-DAY04-HoVaTen-MSSV-PromptEngineeringToolCalling.
- [ ] Kiểm tra deadline và bản chốt theo [SUBMISSION.md](../../SUBMISSION.md).
