"""Streamlit chat UI built on the provided chat.py agent loop."""

from __future__ import annotations

import json
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import execute_tool_call, now_iso, run_model_tool_loop, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from providers.base import ModelResponse, ToolCall
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
PROMPT_PATH = ROOT / "artifacts/system_prompt.md"
TOOLS_PATH = ROOT / "artifacts/tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)


def readable_reply(raw: str | None) -> tuple[str, dict[str, Any]]:
    """The starter still returns JSON; users see only the `reply` text."""
    text = (raw or "").strip()
    candidate = text
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == "```":
            candidate = "\n".join(lines[1:-1]).strip()
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        return text, {}
    if not isinstance(data, dict) or not isinstance(data.get("reply"), str):
        return text, {}
    details = {name: data[name] for name in ("intent", "action", "evidence_ids") if name in data}
    return data["reply"].strip(), details


def new_chat(provider_name: str, artifact: Any) -> dict[str, Any]:
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = f"{artifact.version}_{provider_name}_{stamp}_{secrets.token_hex(4)}"
    path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "model": getattr(make_provider(provider_name), "default_model", None),
        "system_prompt": str(PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    write_transcript(path, transcript)
    return {"messages": [], "history": [], "pending_ticket": None,
            "transcript": transcript, "path": path}


def save_turn(chat: dict[str, Any], turn: dict[str, Any], reply: str,
              details: dict[str, Any] | None = None) -> None:
    turn["ended_at"] = now_iso()
    turn["assistant_reply"] = reply
    turn["assistant_details"] = details or {}
    chat["transcript"]["turns"].append(turn)
    chat["messages"].extend([
        {"role": "user", "content": turn["user"]},
        {"role": "assistant", "content": reply, "details": details or {},
         "tools": turn.get("tool_events", []), "error": turn.get("error"),
         "ui_events": turn.get("ui_events", [])},
    ])
    chat["history"].extend([
        {"role": "user", "content": turn["user"]},
        {"role": "assistant", "content": turn.get("assistant_text") or reply},
    ])
    write_transcript(chat["path"], chat["transcript"])


class GuardedProvider:
    """Keep the supplied loop unchanged while preventing model-only ticket writes."""

    def __init__(self, provider: Any) -> None:
        self.provider = provider
        self.ticket_proposals: list[dict[str, Any]] = []

    def complete(self, messages, tools, *, model=None, temperature=0.0, tool_choice=None):
        response = self.provider.complete(
            messages, tools, model=model, temperature=temperature, tool_choice=tool_choice
        )
        safe_calls: list[ToolCall] = []
        for call in response.tool_calls:
            args = dict(call.args)
            if call.name == "create_ticket":
                self.ticket_proposals.append(dict(args))
                args["confirmed"] = False
            safe_calls.append(ToolCall(name=call.name, args=args))
        return ModelResponse(text=response.text, tool_calls=safe_calls, raw=response.raw)


def review_ticket_events(chat: dict[str, Any], events: list[dict[str, Any]],
                         proposals: list[dict[str, Any]]) -> bool:
    """Expose the exact validated payload for a separate UI confirmation."""
    proposal_index = 0
    pending = False
    for event in events:
        if event.get("tool") != "create_ticket":
            continue
        if proposal_index < len(proposals):
            event["model_args"] = proposals[proposal_index]
        proposal_index += 1
        result = event.get("result", {})
        if not isinstance(result, dict) or result.get("status") != "needs_confirmation":
            continue
        args = event.get("args", {})
        chat["pending_ticket"] = {
            "summary": args.get("summary", "").strip(),
            "priority": (args.get("priority") or "medium").strip().lower(),
            "asset_id": (args.get("asset_id") or "").strip().upper(),
        }
        pending = True
    return pending


def send(chat: dict[str, Any], user_text: str, provider_name: str,
         system_prompt: str, tools: list[dict[str, Any]]) -> None:
    invalidated = chat["pending_ticket"] is not None
    chat["pending_ticket"] = None
    turn: dict[str, Any] = {
        "turn_index": len(chat["transcript"]["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
        "ui_events": ([{"type": "ticket_confirmation_invalidated"}] if invalidated else []),
    }
    messages = [{"role": "system", "content": system_prompt},
                *trim_history(chat["history"], 5),
                {"role": "user", "content": user_text}]
    try:
        guarded_provider = GuardedProvider(make_provider(provider_name))
        result = run_model_tool_loop(
            provider=guarded_provider, messages=messages, tools=tools,
            model=None, max_tool_rounds=4,
        )
        turn.update(result)
        reply, details = readable_reply(result["assistant_text"])
        pending = review_ticket_events(chat, turn["tool_events"], guarded_provider.ticket_proposals)
        if pending:
            turn["status"] = "waiting_for_user"
            reply = "Kiểm tra đúng nội dung ticket bên dưới rồi chọn Xác nhận hoặc Hủy."
        elif any(isinstance(event.get("result"), dict) and event["result"].get("error")
                 for event in turn["tool_events"]):
            reply = "⚠️ Yêu cầu chưa hoàn tất vì công cụ báo lỗi. Mở Chi tiết để xem kết quả thực tế."
    except Exception as exc:
        turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}",
                     "assistant_text": "Không thể hoàn thành yêu cầu. Xem lỗi bên dưới."})
        reply, details = turn["assistant_text"], {}
    save_turn(chat, turn, reply, details)


def ticket_decision(chat: dict[str, Any], confirm: bool) -> None:
    draft = chat["pending_ticket"]
    if not draft:
        return
    chat["pending_ticket"] = None
    if confirm:
        event = execute_tool_call(ToolCall("create_ticket", {**draft, "confirmed": True}))
        result = event.get("result", {})
        created = isinstance(result, dict) and result.get("status") == "created"
        reply = f"Đã tạo ticket {result['ticket_id']}." if created else "Không tạo được ticket. Xem lỗi công cụ bên dưới."
        status = "action_completed" if created else "action_error"
        user = "[UI] Xác nhận tạo ticket với đúng nội dung hiển thị"
    else:
        reply, status = "Đã hủy ticket; không có dữ liệu được ghi.", "action_cancelled"
        user = "[UI] Hủy ticket đang chờ xác nhận"
    save_turn(chat, {
        "turn_index": len(chat["transcript"]["turns"]) + 1,
        "started_at": now_iso(), "user": user, "status": status,
        "assistant_text": reply, "rounds": [],
        "tool_events": [event] if confirm else [],
        "ui_events": [{"type": "ticket_confirmed" if confirm else "ticket_cancelled"}],
    }, reply)


def show_details(message: dict[str, Any]) -> None:
    events = message.get("tools", [])
    with st.expander(f"🔍 Chi tiết xử lý · {len(events)} công cụ"):
        details = message.get("details", {})
        if details:
            st.write("**Ý định:**", details.get("intent", "—"))
            st.write("**Hành động:**", details.get("action", "—"))
            st.write("**Bằng chứng:**", details.get("evidence_ids", []))
        for ui_event in message.get("ui_events", []):
            st.info(ui_event.get("type", ""))
        if not events:
            st.caption("Lượt này không gọi công cụ.")
        for event in events:
            st.write(f"**{event.get('tool', 'tool')}**")
            result = event.get("result", {})
            error = event.get("error") or (result.get("error") if isinstance(result, dict) else None)
            if error:
                st.error(f"Lỗi công cụ: {error}")
            st.caption("Đầu vào thực thi")
            st.json(event.get("args", {}))
            if "model_args" in event:
                st.caption("Đầu vào model đề xuất")
                st.json(event["model_args"])
            st.caption("Kết quả / lỗi")
            st.json(result or {"error": event.get("error")})
            st.divider()
        if message.get("error"):
            st.error(message["error"])


def main() -> None:
    st.set_page_config(page_title="IT Helpdesk Agent", page_icon="🛠️", layout="wide")
    st.title("🛠️ IT Helpdesk Agent — Northstar Labs")
    with st.sidebar:
        provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"])
        version = "v3"
        st.caption("Phiên bản artifact đang chạy được tính từ prompt và tools hiện tại.")

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    tools = to_openai_tools(load_tool_declarations(TOOLS_PATH))
    artifact = build_artifact_version(version, PROMPT_PATH, TOOLS_PATH)
    key = (provider_name, artifact.artifact_version)
    if st.session_state.get("chat_key") != key:
        st.session_state.chat = new_chat(provider_name, artifact)
        st.session_state.chat_key = key
    chat = st.session_state.chat
    st.caption(f"Artifact Version Active: `{artifact.artifact_version}`")

    with st.sidebar:
        if st.button("＋ Hội thoại mới", use_container_width=True):
            st.session_state.chat = new_chat(provider_name, artifact)
            st.rerun()
        st.download_button("↓ Tải transcript JSON", data=chat["path"].read_bytes(),
                           file_name=chat["path"].name, mime="application/json",
                           use_container_width=True)
        st.caption(chat["path"].name)
        st.info("Chat hiển thị câu trả lời; mở Chi tiết để xem tool call, input, kết quả hoặc lỗi.")

    if not chat["messages"]:
        st.write("Hỏi về VPN, email, thiết bị hoặc hướng dẫn nội bộ để bắt đầu.")
    for message in chat["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                show_details(message)

    draft = chat["pending_ticket"]
    if draft:
        with st.container(border=True):
            st.warning("Ticket đang chờ xác nhận. Yêu cầu mới sẽ hủy xác nhận này.")
            st.write(f"**Nội dung:** {draft['summary']}")
            st.write(f"**Ưu tiên:** {draft['priority']} · **Thiết bị:** {draft['asset_id'] or 'Không có'}")
            yes, no = st.columns(2)
            if yes.button("Xác nhận và tạo ticket", type="primary", use_container_width=True):
                ticket_decision(chat, True)
                st.rerun()
            if no.button("Hủy", use_container_width=True):
                ticket_decision(chat, False)
                st.rerun()

    if prompt := st.chat_input("Nhập yêu cầu hỗ trợ IT..."):
        with st.spinner("Agent đang xử lý và kích hoạt tools..."):
            send(chat, prompt.strip(), provider_name, system_prompt, tools)
        st.rerun()


if __name__ == "__main__":
    main()
