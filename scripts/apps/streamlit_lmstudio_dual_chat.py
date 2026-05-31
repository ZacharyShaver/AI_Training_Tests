#!/usr/bin/env python3
"""Streamlit app for running a timed two-model conversation via LM Studio.

The app talks to an LM Studio local server using its OpenAI-compatible API.
The default base URL can be overridden in the sidebar or via the
LMSTUDIO_BASE_URL environment variable.
"""

from __future__ import annotations

import html
import json
import os
import time
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import requests
import streamlit as st

DEFAULT_BASE_URL = os.environ.get("LMSTUDIO_BASE_URL", "http://192.168.21.1:45")
DEFAULT_PROMPT_A = (
    "You are Participant A in a thoughtful dialogue. Reason carefully, stay on topic, "
    "respond directly to the other participant, and keep each message to 2-4 sentences."
)
DEFAULT_PROMPT_B = (
    "You are Participant B in a thoughtful dialogue. Build on the other participant's "
    "points, challenge weak reasoning politely, and keep each message to 2-4 sentences."
)
TRANSCRIPT_LIMIT = 12


@dataclass
class ChatMessage:
    """Stores a single message in the visible transcript."""

    speaker: str
    model_id: str
    role: str
    content: str


@dataclass
class ModelInfo:
    """Minimal model metadata returned by LM Studio."""

    id: str
    model_type: str
    state: str
    context_length: int | None = None


def initialize_state() -> None:
    """Create all session state keys used by the app."""
    st.session_state.setdefault("models", [])
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("last_refresh_error", "")
    st.session_state.setdefault("last_run_summary", "")


def fetch_models(base_url: str) -> list[ModelInfo]:
    """Fetch LM Studio model metadata and keep only models usable for chat."""
    response = requests.get(f"{base_url.rstrip('/')}/api/v0/models", timeout=15)
    response.raise_for_status()
    payload = response.json()
    supported_types = {"llm", "vlm"}
    models: list[ModelInfo] = []

    for model in payload.get("data", []):
        model_id = model.get("id")
        model_type = model.get("type")
        if not model_id or model_type not in supported_types:
            continue

        models.append(
            ModelInfo(
                id=model_id,
                model_type=model_type,
                state=model.get("state", "unknown"),
                context_length=model.get("max_context_length"),
            )
        )

    return sorted(models, key=lambda model: (model.state != "loaded", model.id.lower()))


def refresh_models(base_url: str) -> None:
    """Refresh the cached model list and surface any connection error."""
    try:
        st.session_state.models = fetch_models(base_url)
        st.session_state.last_refresh_error = ""
    except requests.RequestException as exc:
        st.session_state.models = []
        st.session_state.last_refresh_error = str(exc)


def format_model_label(model: ModelInfo) -> str:
    """Create a readable label for a model dropdown."""
    context_text = (
        f" · {model.context_length} ctx" if isinstance(model.context_length, int) else ""
    )
    return f"{model.id} [{model.state} | {model.model_type}{context_text}]"


def build_turn_messages(
    *,
    topic: str,
    speaker_name: str,
    partner_name: str,
    system_prompt: str,
    transcript: list[ChatMessage],
) -> list[dict[str, str]]:
    """Build a compact prompt for one participant's next turn."""
    recent_history = transcript[-TRANSCRIPT_LIMIT:]

    if recent_history:
        transcript_text = "\n".join(
            f"{message.speaker}: {message.content}" for message in recent_history
        )
    else:
        transcript_text = "No conversation yet."

    user_prompt = (
        f"Topic: {topic}\n"
        f"You are {speaker_name}. You are speaking with {partner_name}.\n"
        "Continue the conversation with one message.\n"
        "Reply as natural dialogue only. Do not use stage directions, bullet points, "
        "speaker labels, or JSON.\n\n"
        f"Recent transcript:\n{transcript_text}"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def request_chat_completion(
    *,
    base_url: str,
    model_id: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> str:
    """Call LM Studio's OpenAI-compatible chat completions endpoint."""
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    response = requests.post(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        json=payload,
        timeout=120,
    )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        detail = ""
        try:
            payload = response.json()
            detail = payload.get("error", {}).get("message", "")
        except ValueError:
            detail = response.text.strip()

        if detail:
            raise RuntimeError(detail) from exc
        raise

    data = response.json()

    choices = data.get("choices", [])
    if not choices:
        raise ValueError("LM Studio returned no choices.")

    message = choices[0].get("message", {})
    content = (message.get("content") or "").strip()
    if not content:
        raise ValueError("LM Studio returned an empty completion.")

    return content


def stream_chat_completion(
    *,
    base_url: str,
    model_id: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> Iterator[str]:
    """Stream an LM Studio completion, yielding content pieces as they arrive."""
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    with requests.post(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        json=payload,
        stream=True,
        timeout=300,
    ) as response:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            detail = ""
            try:
                detail = response.json().get("error", {}).get("message", "")
            except ValueError:
                detail = response.text.strip()
            if detail:
                raise RuntimeError(detail) from exc
            raise

        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line or not raw_line.startswith("data:"):
                continue
            data = raw_line[len("data:") :].strip()
            if data == "[DONE]":
                break
            try:
                chunk = json.loads(data)
            except ValueError:
                continue
            choices = chunk.get("choices", [])
            if not choices:
                continue
            piece = (choices[0].get("delta", {}).get("content")) or ""
            if piece:
                yield piece


def sanitize_reply(reply: str) -> str:
    """Remove accidental speaker prefixes so the transcript stays clean."""
    cleaned = reply.strip()
    for prefix in ("Participant A:", "Participant B:", "A:", "B:"):
        if cleaned.startswith(prefix):
            return cleaned[len(prefix) :].strip()
    return cleaned


def render_transcript(
    messages: list[ChatMessage], pending: ChatMessage | None = None
) -> None:
    """Render the transcript with simple message bubble styling.

    If ``pending`` is given it is rendered as an extra, in-progress bubble after
    the committed messages, so a streaming reply ticks in live.
    """
    transcript_html = [
        (
            '<div style="'
            "background: linear-gradient(180deg, #f5efe6 0%, #fffdf9 100%);"
            "border: 1px solid #dbcdb8;"
            "border-radius: 18px;"
            "padding: 18px;"
            "min-height: 420px;"
            '">'
        )
    ]

    display = list(messages)
    if pending is not None:
        display.append(pending)

    if not display:
        transcript_html.append(
            '<div style="color:#6a5a48;">The conversation transcript will appear here.</div>'
        )
    else:
        for index, message in enumerate(display):
            is_left = index % 2 == 0
            row_justify = "flex-start" if is_left else "flex-end"
            bubble_background = "#fff8ef" if is_left else "#dcecff"
            bubble_border = "#e9dcc8" if is_left else "#bfd7fb"
            bubble_text = "#3c2d1c" if is_left else "#1d314a"
            is_pending = pending is not None and index == len(display) - 1
            cursor = (
                '<span style="opacity:0.5;">▌</span>' if is_pending else ""
            )
            label_suffix = " · typing…" if is_pending else ""
            transcript_html.append(
                (
                    f'<div style="display:flex; justify-content:{row_justify}; margin:10px 0;">'
                    f'<div style="max-width:78%; border-radius:16px; padding:12px 14px; '
                    f'box-shadow:0 6px 18px rgba(72, 49, 22, 0.08); white-space:pre-wrap; '
                    f'line-height:1.4; font-size:0.98rem; background:{bubble_background}; '
                    f'border:1px solid {bubble_border}; color:{bubble_text};">'
                    f'<div style="font-size:0.78rem; font-weight:600; '
                    f'margin-bottom:6px; opacity:0.85;">'
                    f"{html.escape(message.speaker)} · "
                    f"{html.escape(message.model_id)}{label_suffix}"
                    f"</div>{html.escape(message.content)}{cursor}</div></div>"
                )
            )

    transcript_html.append("</div>")
    st.markdown("".join(transcript_html), unsafe_allow_html=True)


def export_transcript(messages: list[ChatMessage]) -> str:
    """Create a simple JSON export for download."""
    return json.dumps([message.__dict__ for message in messages], ensure_ascii=False, indent=2)


def run_conversation(
    *,
    base_url: str,
    topic: str,
    model_a: str,
    model_b: str,
    prompt_a: str,
    prompt_b: str,
    duration_seconds: int,
    max_turns: int,
    temperature: float,
    max_tokens: int,
    transcript_placeholder: Any,
) -> None:
    """Run an alternating two-model conversation for the requested time."""
    st.session_state.messages = []
    st.session_state.last_run_summary = ""

    status_placeholder = st.empty()
    progress_bar = st.progress(0.0, text="Preparing conversation...")

    participants = [
        {
            "speaker": "Participant A",
            "partner": "Participant B",
            "model_id": model_a,
            "system_prompt": prompt_a,
        },
        {
            "speaker": "Participant B",
            "partner": "Participant A",
            "model_id": model_b,
            "system_prompt": prompt_b,
        },
    ]

    start_time = time.time()
    turn_index = 0

    while turn_index < max_turns and (time.time() - start_time) < duration_seconds:
        participant = participants[turn_index % 2]
        elapsed = time.time() - start_time
        remaining = max(0, duration_seconds - int(elapsed))

        status_placeholder.info(
            f"{participant['speaker']} is responding. "
            f"Turn {turn_index + 1}/{max_turns} · about {remaining}s remaining."
        )

        messages = build_turn_messages(
            topic=topic,
            speaker_name=participant["speaker"],
            partner_name=participant["partner"],
            system_prompt=participant["system_prompt"],
            transcript=st.session_state.messages,
        )

        pending = ChatMessage(
            speaker=participant["speaker"],
            model_id=participant["model_id"],
            role="assistant",
            content="",
        )
        accumulated = ""
        for piece in stream_chat_completion(
            base_url=base_url,
            model_id=participant["model_id"],
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            accumulated += piece
            pending.content = accumulated
            with transcript_placeholder.container():
                render_transcript(st.session_state.messages, pending=pending)

        st.session_state.messages.append(
            ChatMessage(
                speaker=participant["speaker"],
                model_id=participant["model_id"],
                role="assistant",
                content=sanitize_reply(accumulated),
            )
        )

        with transcript_placeholder.container():
            render_transcript(st.session_state.messages)

        turn_index += 1
        progress = min((time.time() - start_time) / duration_seconds, 1.0)
        progress_bar.progress(progress, text=f"Conversation running: {turn_index} turns complete")

    total_elapsed = round(time.time() - start_time, 1)
    progress_bar.progress(1.0, text="Conversation finished")
    status_placeholder.success(
        f"Finished after {turn_index} turns in {total_elapsed} seconds."
    )
    st.session_state.last_run_summary = (
        f"Completed {turn_index} turns over {total_elapsed} seconds."
    )


def main() -> None:
    """Render the Streamlit UI."""
    st.set_page_config(
        page_title="LM Studio Dual Model Chat",
        page_icon="💬",
        layout="wide",
    )
    initialize_state()

    st.title("LM Studio Dual Model Chat")
    st.caption(
        "Run a timed conversation between two local LM Studio models through the "
        "OpenAI-compatible server."
    )

    with st.sidebar:
        st.subheader("Server")
        base_url = st.text_input("LM Studio Base URL", value=DEFAULT_BASE_URL)
        if st.button("Refresh Model List", use_container_width=True):
            refresh_models(base_url)

        if not st.session_state.models:
            refresh_models(base_url)

        if st.session_state.last_refresh_error:
            st.error(f"Could not reach LM Studio: {st.session_state.last_refresh_error}")
        elif st.session_state.models:
            st.success(f"Found {len(st.session_state.models)} local model(s).")
        else:
            st.warning("No models were returned by the LM Studio server.")

        st.subheader("Run Settings")
        duration_seconds = st.slider("Conversation Length (seconds)", 10, 30000, 60, 5)
        max_turns = st.slider("Max Turns", 2, 400, 12, 2)
        temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
        max_tokens = st.slider("Max Tokens Per Turn", 64, 1024, 256, 32)

    model_infos = st.session_state.models
    if not model_infos:
        st.info("Start LM Studio's local server and refresh the model list to continue.")
        render_transcript(st.session_state.messages)
        return

    loaded_models = [model for model in model_infos if model.state == "loaded"]
    unloaded_models = [model for model in model_infos if model.state != "loaded"]

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Participant A")
        model_a_info = st.selectbox(
            "Model A",
            options=model_infos,
            index=0,
            key="model_a",
            format_func=format_model_label,
        )
        prompt_a = st.text_area(
            "System Prompt A",
            value=DEFAULT_PROMPT_A,
            height=180,
            key="prompt_a",
        )

    with col_right:
        st.subheader("Participant B")
        default_b_index = 1 if len(model_infos) > 1 else 0
        model_b_info = st.selectbox(
            "Model B",
            options=model_infos,
            index=default_b_index,
            key="model_b",
            format_func=format_model_label,
        )
        prompt_b = st.text_area(
            "System Prompt B",
            value=DEFAULT_PROMPT_B,
            height=180,
            key="prompt_b",
        )

    topic = st.text_input(
        "Topic",
        value="Discuss whether disciplined reasoning leads to wisdom.",
        help="The shared topic the two selected models will explore together.",
    )

    if loaded_models:
        st.caption(
            "Loaded models are listed first. LM Studio may reject unloaded models if "
            "loading them would exceed available memory."
        )
    elif unloaded_models:
        st.warning(
            "LM Studio returned models, but none are currently loaded. Load at least one "
            "chat-capable model in LM Studio before starting."
        )

    action_col1, action_col2 = st.columns([1, 1])
    with action_col1:
        run_clicked = st.button(
            "Start Timed Conversation", type="primary", use_container_width=True
        )
    with action_col2:
        clear_clicked = st.button("Clear Transcript", use_container_width=True)

    if clear_clicked:
        st.session_state.messages = []
        st.session_state.last_run_summary = ""

    st.subheader("Conversation")
    transcript_placeholder = st.empty()
    with transcript_placeholder.container():
        render_transcript(st.session_state.messages)

    if run_clicked:
        try:
            run_conversation(
                base_url=base_url,
                topic=topic,
                model_a=model_a_info.id,
                model_b=model_b_info.id,
                prompt_a=prompt_a,
                prompt_b=prompt_b,
                duration_seconds=duration_seconds,
                max_turns=max_turns,
                temperature=temperature,
                max_tokens=max_tokens,
                transcript_placeholder=transcript_placeholder,
            )
        except Exception as exc:
            st.error(f"Conversation failed: {exc}")

    if st.session_state.last_run_summary:
        st.caption(st.session_state.last_run_summary)

    if st.session_state.messages:
        st.download_button(
            label="Download Transcript JSON",
            data=export_transcript(st.session_state.messages),
            file_name="lmstudio_dual_chat_transcript.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
