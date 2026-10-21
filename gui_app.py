"""Poiema Gospel Stationery Studio - Interactive Multi-Agent GUI.

Features:
1. Tab 1: Studio & Live 9:16 Preview (주제 기획, 폼팩터, 화풍, 실시간 미리보기)
2. Tab 2: Crew AI Deliberation Room & Human-in-the-Loop Intervention (에이전트 실시간 협의실 & 사용자 중간 개입/수정)
3. Tab 3: Local Engine & System Settings (Apple M2 GPU 상태, TypeSafe API, 메일 설정)
"""

from datetime import datetime
import json
import logging
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
from typing import Any, Dict, Optional
from PIL import Image, ImageTk
import customtkinter as ctk

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from crew_setup import PosterPipelineOrchestrator

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class PoiemaStudioApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("🕊️ 포이에마성령교회 말씀카드 & 전도지 스튜디오 (Local Multi-Agent Studio)")
        self.geometry("1180x820")
        self.minsize(1050, 720)

        self.current_preview_path: Optional[Path] = None
        self.intervention_queue = queue.Queue()
        self.pending_content: Optional[Dict[str, Any]] = None

        # Main Tabview
        self.tabview = ctk.CTkTabview(self, corner_radius=12)
        self.tabview.pack(fill="both", expand=True, padx=16, pady=16)

        self.tab_studio = self.tabview.add("🎛️ 스튜디오 & 미리보기")
        self.tab_agents = self.tabview.add("🤖 Crew AI 협의실 & 사용자 개입")
        self.tab_settings = self.tabview.add("⚙️ 로컬 AI 엔진 및 환경")

        self._build_studio_tab()
        self._build_agents_tab()
        self._build_settings_tab()

    # -----------------------------------------------------------------------
    # TAB 1: Studio & Live Preview
    # -----------------------------------------------------------------------

    def _build_studio_tab(self):
        tab = self.tab_studio
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Left Panel: Controls
        left_frame = ctk.CTkFrame(tab, corner_radius=12)
        left_frame.grid(row=0, column=0, padx=(10, 8), pady=10, sticky="nsew")

        title_lbl = ctk.CTkLabel(
            left_frame, text="🕊️ 말씀 카드 & 전도지 제작", font=ctk.CTkFont(size=20, weight="bold")
        )
        title_lbl.pack(padx=18, pady=(16, 2), anchor="w")

        desc_lbl = ctk.CTkLabel(
            left_frame, text="로컬 AI 멀티에이전트 × 수묵 캘리그라피 × 붉은 전각 낙관", font=ctk.CTkFont(size=12), text_color="gray"
        )
        desc_lbl.pack(padx=18, pady=(0, 14), anchor="w")

        # 1. Topic
        ctk.CTkLabel(left_frame, text="1. 주제 (Topic)", font=ctk.CTkFont(size=13, weight="bold")).pack(padx=18, pady=(4, 2), anchor="w")
        self.topic_entry = ctk.CTkEntry(
            left_frame, placeholder_text="예: 새벽 기도와 성령 충만 (비워두면 자동 기획)", height=36
        )
        self.topic_entry.pack(fill="x", padx=18, pady=(0, 10))

        # 2. Form Factor
        ctk.CTkLabel(left_frame, text="2. 폼팩터 형식", font=ctk.CTkFont(size=13, weight="bold")).pack(padx=18, pady=(4, 2), anchor="w")
        self.form_map = {
            "🎴 감성 말씀 카드 (Verse Card)": "verse_card",
            "📜 마음을 여는 스토리 전도지 (Gospel Leaflet)": "gospel_leaflet",
            "✉️ 데일리 묵상 엽서 (Devotional Postcard)": "devotional_postcard",
            "🎲 테마 맞춤 자동 추천": "random",
        }
        self.form_combo = ctk.CTkComboBox(left_frame, values=list(self.form_map.keys()), height=34)
        self.form_combo.set("🎴 감성 말씀 카드 (Verse Card)")
        self.form_combo.pack(fill="x", padx=18, pady=(0, 10))

        # 3. Visual Genre
        ctk.CTkLabel(left_frame, text="3. AI 배경 화풍 (Visual Genre)", font=ctk.CTkFont(size=13, weight="bold")).pack(padx=18, pady=(4, 2), anchor="w")
        self.genre_map = {
            "🕊️ 신성한 심벌 아트 (비둘기, 십자가, 올리브)": "symbolic",
            "📸 실사형 35mm 감성 사진 (Photography)": "photography",
            "🎨 감성 수채화 & 오일파스텔 일러스트": "illustration",
            "🎬 지브리 감성 맑은 하늘 애니메이션": "anime",
            "📖 포근하고 따뜻한 동화책 그림 (Storybook)": "storybook",
            "🎲 자동 추천": "auto",
        }
        self.genre_combo = ctk.CTkComboBox(left_frame, values=list(self.genre_map.keys()), height=34)
        self.genre_combo.set("🕊️ 신성한 심벌 아트 (비둘기, 십자가, 올리브)")
        self.genre_combo.pack(fill="x", padx=18, pady=(0, 10))

        # 4. Engine Selector
        ctk.CTkLabel(left_frame, text="4. 생성 엔진 선택", font=ctk.CTkFont(size=13, weight="bold")).pack(padx=18, pady=(4, 2), anchor="w")
        self.engine_combo = ctk.CTkComboBox(
            left_frame,
            values=[
                "⚡ FLUX.1 클라우드 엔진 (워터마크 자동 클리닝)",
                "💻 Apple Silicon M2 GPU 로컬 엔진 (워터마크 0%)",
            ],
            height=34,
        )
        self.engine_combo.set("⚡ FLUX.1 클라우드 엔진 (워터마크 자동 클리닝)")
        self.engine_combo.pack(fill="x", padx=18, pady=(0, 10))

        # Options
        self.contact_switch = ctk.CTkSwitch(left_frame, text="하단 교회 연락처 배너 포함", font=ctk.CTkFont(size=12))
        self.contact_switch.pack(padx=18, pady=(2, 6), anchor="w")

        self.intervention_switch = ctk.CTkSwitch(
            left_frame,
            text="👤 단계별 사용자 승인 모드 (기획 후 일시정지 및 수정)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#3B8ED0",
        )
        self.intervention_switch.pack(padx=18, pady=(2, 14), anchor="w")

        # Action Buttons
        btn_box = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_box.pack(fill="x", padx=18, pady=(0, 10))
        btn_box.grid_columnconfigure((0, 1), weight=1)

        self.btn_preview = ctk.CTkButton(
            btn_box,
            text="🎨 미리보기 생성 (로컬)",
            height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self._start_pipeline(dry_run=True),
        )
        self.btn_preview.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.btn_dispatch = ctk.CTkButton(
            btn_box,
            text="🚀 생성 및 Gmail 발송",
            height=42,
            fg_color="#1E7E34",
            hover_color="#155D27",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self._start_pipeline(dry_run=False),
        )
        self.btn_dispatch.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        # Status & Progress
        self.progress_bar = ctk.CTkProgressBar(left_frame)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=18, pady=(4, 6))

        self.status_lbl = ctk.CTkLabel(left_frame, text="대기 중", font=ctk.CTkFont(size=12), text_color="gray")
        self.status_lbl.pack(padx=18, pady=(0, 8), anchor="w")

        # Right Panel: Live Visual Preview
        right_frame = ctk.CTkFrame(tab, corner_radius=12)
        right_frame.grid(row=0, column=1, padx=(8, 10), pady=10, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            right_frame, text="🖼️ 실시간 9:16 완성본 미리보기", font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        self.canvas_box = ctk.CTkFrame(right_frame, corner_radius=10, fg_color="#161616")
        self.canvas_box.grid(row=1, column=0, padx=16, pady=8, sticky="nsew")
        self.canvas_box.grid_rowconfigure(0, weight=1)
        self.canvas_box.grid_columnconfigure(0, weight=1)

        self.preview_lbl = ctk.CTkLabel(
            self.canvas_box, text="생성 버튼을 누르면\n이곳에 9:16 완성본이 표시됩니다.", text_color="#777777"
        )
        self.preview_lbl.grid(row=0, column=0, sticky="nsew")

        bot_util = ctk.CTkFrame(right_frame, fg_color="transparent")
        bot_util.grid(row=2, column=0, padx=16, pady=(8, 16), sticky="ew")
        bot_util.grid_columnconfigure((0, 1), weight=1)

        self.btn_open_img = ctk.CTkButton(bot_util, text="📂 원본 이미지 열기", state="disabled", command=self._open_img)
        self.btn_open_img.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.btn_open_dir = ctk.CTkButton(bot_util, text="📁 output 폴더 열기", command=self._open_dir)
        self.btn_open_dir.grid(row=0, column=1, padx=(6, 0), sticky="ew")

    # -----------------------------------------------------------------------
    # TAB 2: Crew AI Deliberation Room & Human-in-the-Loop
    # -----------------------------------------------------------------------

    def _build_agents_tab(self):
        tab = self.tab_agents
        tab.grid_columnconfigure(0, weight=3)
        tab.grid_columnconfigure(1, weight=2)
        tab.grid_rowconfigure(0, weight=1)

        # Left: Live Dialogue Feed between Agents
        feed_frame = ctk.CTkFrame(tab, corner_radius=12)
        feed_frame.grid(row=0, column=0, padx=(10, 8), pady=10, sticky="nsew")

        ctk.CTkLabel(
            feed_frame, text="💬 Crew AI 에이전트 실시간 협의실", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(padx=16, pady=(16, 4), anchor="w")

        ctk.CTkLabel(
            feed_frame, text="4개 전문 에이전트가 나누는 기획·검증·예술 협의 과정이 실시간으로 출력됩니다.", font=ctk.CTkFont(size=12), text_color="gray"
        ).pack(padx=16, pady=(0, 10), anchor="w")

        self.chat_feed = ctk.CTkTextbox(feed_frame, font=ctk.CTkFont(size=12), activate_scrollbars=True)
        self.chat_feed.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.chat_feed.configure(state="disabled")

        # Right: Human-in-the-Loop Intervention Editor
        edit_frame = ctk.CTkFrame(tab, corner_radius=12)
        edit_frame.grid(row=0, column=1, padx=(8, 10), pady=10, sticky="nsew")

        ctk.CTkLabel(
            edit_frame, text="👤 사용자 중간 개입 및 수정판", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(padx=16, pady=(16, 4), anchor="w")

        ctk.CTkLabel(
            edit_frame, text="AI가 기획한 카피를 마음에 들게 직접 수정하거나 즉시 승인할 수 있습니다.", font=ctk.CTkFont(size=12), text_color="gray"
        ).pack(padx=16, pady=(0, 10), anchor="w")

        # Edit Fields
        ctk.CTkLabel(edit_frame, text="메인 헤드라인 (캘리그래피)", font=ctk.CTkFont(size=12, weight="bold")).pack(padx=16, pady=(4, 2), anchor="w")
        self.edit_headline = ctk.CTkEntry(edit_frame, height=34)
        self.edit_headline.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(edit_frame, text="성경 구절 출처", font=ctk.CTkFont(size=12, weight="bold")).pack(padx=16, pady=(4, 2), anchor="w")
        self.edit_ref = ctk.CTkEntry(edit_frame, height=34)
        self.edit_ref.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(edit_frame, text="성경 본문 말씀", font=ctk.CTkFont(size=12, weight="bold")).pack(padx=16, pady=(4, 2), anchor="w")
        self.edit_text = ctk.CTkTextbox(edit_frame, height=70)
        self.edit_text.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(edit_frame, text="묵상 및 복음 에세이", font=ctk.CTkFont(size=12, weight="bold")).pack(padx=16, pady=(4, 2), anchor="w")
        self.edit_meditation = ctk.CTkTextbox(edit_frame, height=90)
        self.edit_meditation.pack(fill="x", padx=16, pady=(0, 12))

        # Approval Buttons
        self.btn_approve = ctk.CTkButton(
            edit_frame,
            text="✓ 이 내용으로 승인하고 다음 단계 진행",
            height=42,
            fg_color="#1E7E34",
            hover_color="#155D27",
            font=ctk.CTkFont(size=13, weight="bold"),
            state="disabled",
            command=self._on_user_approve,
        )
        self.btn_approve.pack(fill="x", padx=16, pady=(0, 8))

        self.btn_replan = ctk.CTkButton(
            edit_frame,
            text="🔄 다른 주제/카피로 다시 기획 요청",
            height=36,
            fg_color="#D9534F",
            hover_color="#C9302C",
            state="disabled",
            command=self._on_user_replan,
        )
        self.btn_replan.pack(fill="x", padx=16, pady=(0, 16))

    # -----------------------------------------------------------------------
    # TAB 3: Local Engine & System Settings
    # -----------------------------------------------------------------------

    def _build_settings_tab(self):
        tab = self.tab_settings
        frame = ctk.CTkFrame(tab, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=14, pady=14)

        ctk.CTkLabel(frame, text="⚙️ 시스템 및 로컬 AI 엔진 현황", font=ctk.CTkFont(size=18, weight="bold")).pack(padx=20, pady=(20, 8), anchor="w")

        info_box = ctk.CTkTextbox(frame, font=ctk.CTkFont(family="Courier", size=13))
        info_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        env_status = (
            "===========================================================\n"
            "🕊️ POIEMA GOSPEL STATIONERY ENGINE STATUS\n"
            "===========================================================\n"
            "■ 로컬 하드웨어: Apple Silicon M2 (arm64)\n"
            "■ Metal GPU 가속 (MPS): 활성화 완료 (PyTorch MPS=True)\n"
            "■ 로컬 이미지 엔진: SDXL-Turbo / diffusers (워터마크 0% 완전 순수 이미지)\n"
            "■ 외부 신학 가드레일: TypeSafe AI Jev API 연동 (복음주의 건전성 심사)\n"
            "■ 클라우드 자동화 상태: GitHub Actions 자동 스케줄 해제 (로컬 독립 구동)\n"
            "■ 지원 폰트: 평창평화체(캘리), 마루부리(명조), 프리텐다드\n"
            "===========================================================\n"
        )
        info_box.insert("end", env_status)
        info_box.configure(state="disabled")

    # -----------------------------------------------------------------------
    # Logic & Threading
    # -----------------------------------------------------------------------

    def _append_chat(self, agent_name: str, message: str):
        """Appends dialogue message to Agent Tab Feed."""
        badge_colors = {
            "Spiritual Copywriter": "✍️ [카피라이터]",
            "Theology Auditor": "🛡️ [신학심사관]",
            "Visual Art Director": "🎨 [시각감독]",
            "Publishing Manager": "🖨️ [발행관리자]",
            "System": "⚙️ [시스템]",
        }
        badge = badge_colors.get(agent_name, f"[{agent_name}]")
        formatted = f"{badge} {message}\n"

        def _do():
            self.chat_feed.configure(state="normal")
            self.chat_feed.insert("end", formatted)
            self.chat_feed.see("end")
            self.chat_feed.configure(state="disabled")

        self.after(0, _do)

    def _start_pipeline(self, dry_run: bool = False):
        self.btn_preview.configure(state="disabled")
        self.btn_dispatch.configure(state="disabled")
        self.progress_bar.start()

        mode = "미리보기 생성 중..." if dry_run else "생성 및 Gmail 발송 중..."
        self.status_lbl.configure(text=f"⏳ {mode}", text_color="#3B8ED0")

        topic = self.topic_entry.get().strip() or None
        form_sel = self.form_map.get(self.form_combo.get(), "verse_card")
        form_factor = None if form_sel == "random" else form_sel

        genre_sel = self.genre_map.get(self.genre_combo.get(), "symbolic")
        forced_genre = None if genre_sel == "auto" else genre_sel

        engine_choice = "local" if "로컬" in self.engine_combo.get() else "pollinations"
        enable_intervention = self.intervention_switch.get()

        if self.contact_switch.get():
            os.environ["SHOW_CHURCH_CONTACT"] = "true"
        else:
            os.environ.pop("SHOW_CHURCH_CONTACT", None)

        threading.Thread(
            target=self._worker,
            args=(topic, form_factor, forced_genre, engine_choice, enable_intervention, dry_run),
            daemon=True,
        ).start()

    def _worker(self, topic, form_factor, forced_genre, engine_choice, enable_intervention, dry_run):
        try:
            orchestrator = PosterPipelineOrchestrator()

            intervention_cb = self._human_intervention_callback if enable_intervention else None

            result = orchestrator.execute_full_pipeline(
                topic_override=topic,
                form_factor_override=form_factor,
                forced_genre=forced_genre,
                engine_choice=engine_choice,
                dry_run=dry_run,
                agent_listener=self._append_chat,
                intervention_callback=intervention_cb,
            )

            poster_path = Path(result.get("poster_path", ""))
            self.after(0, self._on_success, poster_path, dry_run)

        except Exception as e:
            self._append_chat("System", f"오류 발생으로 중단됨: {e}")
            self.after(0, self._on_failure, str(e))

    def _human_intervention_callback(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Pauses worker thread and waits for user approval/edit via Tab 2."""
        self.pending_content = dict(content)
        self.after(0, self._populate_editor, content)
        # Switch to Agent tab so user sees it
        self.after(0, lambda: self.tabview.set("🤖 Crew AI 협의실 & 사용자 개입"))

        # Block until user clicks Approve or Replan
        action, modified = self.intervention_queue.get()
        self.pending_content = None
        return modified

    def _populate_editor(self, content: Dict[str, Any]):
        self.edit_headline.delete(0, "end")
        self.edit_headline.insert(0, content.get("headline", ""))

        self.edit_ref.delete(0, "end")
        self.edit_ref.insert(0, content.get("scripture_ref", ""))

        self.edit_text.delete("1.0", "end")
        self.edit_text.insert("1.0", content.get("scripture_text", ""))

        self.edit_meditation.delete("1.0", "end")
        self.edit_meditation.insert("1.0", content.get("meditation", ""))

        self.btn_approve.configure(state="normal")
        self.btn_replan.configure(state="normal")

    def _on_user_approve(self):
        if not self.pending_content:
            return
        self.pending_content["headline"] = self.edit_headline.get().strip()
        self.pending_content["scripture_ref"] = self.edit_ref.get().strip()
        self.pending_content["scripture_text"] = self.edit_text.get("1.0", "end").strip()
        self.pending_content["meditation"] = self.edit_meditation.get("1.0", "end").strip()

        self.btn_approve.configure(state="disabled")
        self.btn_replan.configure(state="disabled")
        self.intervention_queue.put(("approve", self.pending_content))

    def _on_user_replan(self):
        self.btn_approve.configure(state="disabled")
        self.btn_replan.configure(state="disabled")
        self.intervention_queue.put(("replan", None))

    def _on_success(self, poster_path: Path, dry_run: bool):
        self.progress_bar.stop()
        self.progress_bar.set(1.0)
        self.btn_preview.configure(state="normal")
        self.btn_dispatch.configure(state="normal")

        msg = "✓ 로컬 미리보기 완성!" if dry_run else "✓ 생성 및 Gmail 발송 완료!"
        self.status_lbl.configure(text=msg, text_color="#28A745")

        self.current_preview_path = poster_path
        self.btn_open_img.configure(state="normal")

        # Switch back to Studio Tab and show image
        self.tabview.set("🎛️ 스튜디오 & 미리보기")
        self._display_preview(poster_path)

    def _on_failure(self, err_msg: str):
        self.progress_bar.stop()
        self.progress_bar.set(0.0)
        self.btn_preview.configure(state="normal")
        self.btn_dispatch.configure(state="normal")
        self.status_lbl.configure(text=f"✗ 오류 발생: {err_msg[:40]}...", text_color="#DC3545")

    def _display_preview(self, path: Path):
        if not path.exists():
            return
        try:
            pil_img = Image.open(path)
            target_h = 580
            target_w = int(target_h * (9 / 16))
            scaled = pil_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=scaled, dark_image=scaled, size=(target_w, target_h))
            self.preview_lbl.configure(image=ctk_img, text="")
            self.preview_lbl.image = ctk_img
        except Exception as e:
            logger.error(f"미리보기 실패: {e}")

    def _open_img(self):
        if self.current_preview_path and self.current_preview_path.exists():
            subprocess.run(["open", str(self.current_preview_path)])

    def _open_dir(self):
        out_dir = BASE_DIR / "output"
        out_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["open", str(out_dir)])


if __name__ == "__main__":
    app = PoiemaStudioApp()
    app.mainloop()
