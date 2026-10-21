"""Poiema Gospel Stationery Studio - Modern Desktop GUI App.

Built with CustomTkinter for a native, sleek macOS / Desktop pair-programming experience.
Allows one-click creation and email distribution of:
- Verse Cards (감성 말씀 카드)
- Gospel Leaflets (스토리 전도지)
- Devotional Postcards (데일리 묵상 엽서)

With real-time 9:16 visual preview, multi-genre selection (Photo, Illustration, Symbol, Anime, Storybook),
and direct Gmail dispatching.
"""

from datetime import datetime
import logging
import os
from pathlib import Path
import subprocess
import sys
import threading
from typing import Optional
from PIL import Image, ImageTk
import customtkinter as ctk

# Ensure correct base path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from crew_setup import PosterPipelineOrchestrator

# Setup logging to GUI
logger = logging.getLogger("PoiemaGUI")

ctk.set_appearance_mode("System")  # Follow macOS Dark/Light theme
ctk.set_default_color_theme("blue")


class TextHandler(logging.Handler):
    """Custom logging handler redirecting logs to CTkTextbox."""

    def __init__(self, textbox: ctk.CTkTextbox):
        super().__init__()
        self.textbox = textbox

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.textbox.configure(state="normal")
            self.textbox.insert("end", msg + "\n")
            self.textbox.see("end")
            self.textbox.configure(state="disabled")

        self.textbox.after(0, append)


class PoiemaStudioApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("🕊️ 포이에마성령교회 말씀카드 & 전도지 스튜디오")
        self.geometry("1100x760")
        self.minsize(980, 680)

        self.current_preview_path: Optional[Path] = None

        # 1. Main Grid Layout (Left: Controls, Right: Visual Preview)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_left_control_panel()
        self._build_right_preview_panel()

        # Connect Logging
        self.log_handler = TextHandler(self.log_textbox)
        self.log_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
        )
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)

        logger.info("포이에마 말씀카드 & 전도지 스튜디오가 준비되었습니다. 주제를 입력하고 생성을 시작하세요!")

    def _build_left_control_panel(self):
        """Constructs the left configuration and control side."""
        left_frame = ctk.CTkFrame(self, corner_radius=14)
        left_frame.grid(row=0, column=0, padx=(18, 9), pady=18, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)

        # Header Title
        title_lbl = ctk.CTkLabel(
            left_frame,
            text="🕊️ Poiema Gospel Studio",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title_lbl.pack(pady=(18, 4), padx=20, anchor="w")

        sub_lbl = ctk.CTkLabel(
            left_frame,
            text="AI 말씀 기획 · 수묵 캘리그라피 · FLUX.1 비주얼 · 자동 메일 발송",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        sub_lbl.pack(pady=(0, 16), padx=20, anchor="w")

        # 1. Topic Input Field
        topic_title = ctk.CTkLabel(
            left_frame, text="1. 말씀 / 전도 주제 (Topic)", font=ctk.CTkFont(size=14, weight="bold")
        )
        topic_title.pack(padx=20, pady=(6, 2), anchor="w")

        self.topic_entry = ctk.CTkEntry(
            left_frame,
            placeholder_text="예: 새벽 기도와 성령 충만 (비워두면 이전 기록 기반 자동 기획)",
            height=38,
            font=ctk.CTkFont(size=13),
        )
        self.topic_entry.pack(fill="x", padx=20, pady=(0, 12))

        # 2. Form Factor Selector
        form_title = ctk.CTkLabel(
            left_frame, text="2. 폼팩터 형식 (Form Factor)", font=ctk.CTkFont(size=14, weight="bold")
        )
        form_title.pack(padx=20, pady=(6, 2), anchor="w")

        self.form_options = {
            "🎴 감성 말씀 카드 (Verse Card)": "verse_card",
            "📜 마음을 여는 스토리 전도지 (Gospel Leaflet)": "gospel_leaflet",
            "✉️ 데일리 묵상 엽서 (Devotional Postcard)": "devotional_postcard",
            "🎲 자동 추천 (Random Variant)": "random",
        }
        self.form_combo = ctk.CTkComboBox(
            left_frame,
            values=list(self.form_options.keys()),
            height=36,
            font=ctk.CTkFont(size=13),
        )
        self.form_combo.set("🎴 감성 말씀 카드 (Verse Card)")
        self.form_combo.pack(fill="x", padx=20, pady=(0, 12))

        # 3. Visual Genre Selector
        genre_title = ctk.CTkLabel(
            left_frame, text="3. AI 배경 화풍 (Visual Genre)", font=ctk.CTkFont(size=14, weight="bold")
        )
        genre_title.pack(padx=20, pady=(6, 2), anchor="w")

        self.genre_options = {
            "🕊️ 신성한 심벌 아트 (비둘기, 십자가, 올리브)": "symbolic",
            "📸 실사형 35mm 감성 사진 (Photography)": "photography",
            "🎨 감성 수채화 & 오일파스텔 일러스트": "illustration",
            "🎬 지브리/신카이 마코토 맑은 하늘 애니메이션": "anime",
            "📖 포근하고 따뜻한 동화책 그림 (Storybook)": "storybook",
            "🎲 테마 맞춤 자동 선정 (Auto Rotate)": "auto",
        }
        self.genre_combo = ctk.CTkComboBox(
            left_frame,
            values=list(self.genre_options.keys()),
            height=36,
            font=ctk.CTkFont(size=13),
        )
        self.genre_combo.set("🕊️ 신성한 심벌 아트 (비둘기, 십자가, 올리브)")
        self.genre_combo.pack(fill="x", padx=20, pady=(0, 12))

        # 4. Church Contact Toggle
        self.contact_switch = ctk.CTkSwitch(
            left_frame,
            text="하단 교회 연락처 배너 노출",
            font=ctk.CTkFont(size=13),
        )
        self.contact_switch.pack(padx=20, pady=(4, 16), anchor="w")

        # 5. Action Buttons Frame
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 12))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.btn_preview = ctk.CTkButton(
            btn_frame,
            text="🎨 미리보기 생성 (로컬)",
            height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self._trigger_generation(dry_run=True),
        )
        self.btn_preview.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.btn_dispatch = ctk.CTkButton(
            btn_frame,
            text="🚀 생성 및 Gmail 발송",
            height=44,
            fg_color="#1E7E34",
            hover_color="#155D27",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self._trigger_generation(dry_run=False),
        )
        self.btn_dispatch.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        # 6. Progress Bar & Status Text
        self.progress_bar = ctk.CTkProgressBar(left_frame)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=20, pady=(4, 6))

        self.status_lbl = ctk.CTkLabel(
            left_frame, text="대기 중", font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.status_lbl.pack(padx=20, pady=(0, 8), anchor="w")

        # 7. Realtime Log Console
        self.log_textbox = ctk.CTkTextbox(
            left_frame,
            height=160,
            font=ctk.CTkFont(family="Courier", size=11),
            activate_scrollbars=True,
        )
        self.log_textbox.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        self.log_textbox.configure(state="disabled")

    def _build_right_preview_panel(self):
        """Constructs the right real-time visual preview side."""
        right_frame = ctk.CTkFrame(self, corner_radius=14)
        right_frame.grid(row=0, column=1, padx=(9, 18), pady=18, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        header_lbl = ctk.CTkLabel(
            right_frame,
            text="🖼️ 실시간 완성본 미리보기 (9:16 Preview)",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        header_lbl.grid(row=0, column=0, padx=20, pady=(18, 10), sticky="w")

        # Image Canvas Frame
        self.canvas_frame = ctk.CTkFrame(right_frame, corner_radius=10, fg_color="#1A1A1A")
        self.canvas_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        self.preview_lbl = ctk.CTkLabel(
            self.canvas_frame,
            text="생성 버튼을 누르면\n이곳에 9:16 완성본이 표시됩니다.",
            font=ctk.CTkFont(size=14),
            text_color="#888888",
        )
        self.preview_lbl.grid(row=0, column=0, sticky="nsew")

        # Bottom Utility Buttons
        bot_bar = ctk.CTkFrame(right_frame, fg_color="transparent")
        bot_bar.grid(row=2, column=0, padx=20, pady=(6, 18), sticky="ew")
        bot_bar.grid_columnconfigure((0, 1), weight=1)

        self.btn_open_file = ctk.CTkButton(
            bot_bar,
            text="📂 원본 이미지 열기",
            height=36,
            state="disabled",
            command=self._open_current_image,
        )
        self.btn_open_file.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.btn_open_folder = ctk.CTkButton(
            bot_bar,
            text="📁 결과 폴더(output) 열기",
            height=36,
            command=self._open_output_folder,
        )
        self.btn_open_folder.grid(row=0, column=1, padx=(6, 0), sticky="ew")

    # -----------------------------------------------------------------------
    # Generation Logic via Background Thread
    # -----------------------------------------------------------------------

    def _trigger_generation(self, dry_run: bool = False):
        """Spawns pipeline execution in worker thread."""
        self.btn_preview.configure(state="disabled")
        self.btn_dispatch.configure(state="disabled")
        self.progress_bar.set(0.15)
        self.progress_bar.start()

        mode_text = "미리보기 생성 중..." if dry_run else "생성 및 Gmail 발송 중..."
        self.status_lbl.configure(text=f"⏳ {mode_text}", text_color="#3B8ED0")

        # Extract UI inputs
        topic = self.topic_entry.get().strip() or None
        form_sel = self.form_options.get(self.form_combo.get(), "verse_card")
        form_factor = None if form_sel == "random" else form_sel

        genre_sel = self.genre_options.get(self.genre_combo.get(), "symbolic")
        forced_genre = None if genre_sel == "auto" else genre_sel

        show_contact = self.contact_switch.get()
        if show_contact:
            os.environ["SHOW_CHURCH_CONTACT"] = "true"
        else:
            os.environ.pop("SHOW_CHURCH_CONTACT", None)

        threading.Thread(
            target=self._run_pipeline_worker,
            args=(topic, form_factor, forced_genre, dry_run),
            daemon=True,
        ).start()

    def _run_pipeline_worker(
        self,
        topic: Optional[str],
        form_factor: Optional[str],
        forced_genre: Optional[str],
        dry_run: bool,
    ):
        """Worker thread executing the orchestrator."""
        try:
            orchestrator = PosterPipelineOrchestrator()
            result = orchestrator.execute_full_pipeline(
                topic_override=topic,
                form_factor_override=form_factor,
                forced_genre=forced_genre,
                dry_run=dry_run,
            )

            poster_path = Path(result.get("poster_path", ""))
            self.after(0, self._on_generation_success, poster_path, dry_run, result)

        except Exception as e:
            logger.error(f"파이프라인 실행 중 오류 발생: {e}", exc_info=True)
            self.after(0, self._on_generation_failure, str(e))

    def _on_generation_success(self, poster_path: Path, dry_run: bool, result: dict):
        """Invoked on main thread upon success."""
        self.progress_bar.stop()
        self.progress_bar.set(1.0)
        self.btn_preview.configure(state="normal")
        self.btn_dispatch.configure(state="normal")

        if dry_run:
            self.status_lbl.configure(text="✓ 로컬 미리보기 생성 완료!", text_color="#28A745")
        else:
            self.status_lbl.configure(text="✓ 생성 및 Gmail 발송 완료!", text_color="#28A745")

        self.current_preview_path = poster_path
        self.btn_open_file.configure(state="normal")

        # Load & display preview image
        self._display_preview_image(poster_path)

    def _on_generation_failure(self, err_msg: str):
        """Invoked on main thread upon failure."""
        self.progress_bar.stop()
        self.progress_bar.set(0.0)
        self.btn_preview.configure(state="normal")
        self.btn_dispatch.configure(state="normal")
        self.status_lbl.configure(text=f"✗ 오류 발생: {err_msg[:40]}...", text_color="#DC3545")

    def _display_preview_image(self, path: Path):
        """Renders 9:16 image properly scaled onto the preview label."""
        if not path.exists():
            return
        try:
            pil_img = Image.open(path)
            # Calculate scaled dimensions fitting inside canvas frame
            target_h = 560
            target_w = int(target_h * (9 / 16))

            scaled = pil_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=scaled, dark_image=scaled, size=(target_w, target_h))

            self.preview_lbl.configure(image=ctk_img, text="")
            self.preview_lbl.image = ctk_img
        except Exception as e:
            logger.error(f"미리보기 이미지 표시 실패: {e}")

    def _open_current_image(self):
        """Opens the generated artwork in system default viewer."""
        if self.current_preview_path and self.current_preview_path.exists():
            if sys.platform == "darwin":
                subprocess.run(["open", str(self.current_preview_path)])
            elif sys.platform.startswith("win"):
                os.startfile(str(self.current_preview_path))
            else:
                subprocess.run(["xdg-open", str(self.current_preview_path)])

    def _open_output_folder(self):
        """Opens output directory in Finder/Explorer."""
        out_dir = BASE_DIR / "output"
        out_dir.mkdir(parents=True, exist_ok=True)
        if sys.platform == "darwin":
            subprocess.run(["open", str(out_dir)])
        elif sys.platform.startswith("win"):
            os.startfile(str(out_dir))
        else:
            subprocess.run(["xdg-open", str(out_dir)])


if __name__ == "__main__":
    app = PoiemaStudioApp()
    app.mainloop()
