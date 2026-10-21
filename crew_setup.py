"""CrewAI Multi-Agent Pipeline Setup for Poiema Daily Gospel Poster & Cards.

Agents:
1. Spiritual Copywriter: Creative Christian essayist & copywriter crafting verse cards, leaflets, and devotional postcards.
2. Theology Auditor: 3-tier orthodoxy guardrail (Local Blacklist -> TypeSafe AI Jev -> Scripture Consistency).
3. Visual Art Director: Trend-conscious director prompting Google Imagen 3 (or bespoke textured fine-art paper wash).
4. Publishing Manager: Bespoke calligraphy rendering, red seal stamp, email dispatcher, and worklog archiver.
"""

from datetime import datetime
import json
import logging
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Safe crewai import for cross-version compatibility
try:
    from crewai import Agent, Crew, Process, Task
    from crewai.tools import tool
    HAS_CREWAI = True
except ImportError:
    HAS_CREWAI = False

from pydantic import BaseModel, Field

from drive_uploader import upload_poster_to_drive
from guardrails.theology_guard import (
    PosterContent,
    TheologyAuditResult,
    audit_poster_content,
)
from image_composer import compose_poster
from utils.email_sender import send_daily_poster_email
from utils.font_downloader import ensure_fonts_exist
from utils.image_generator import (
    build_imagen_prompt,
    generate_background_image,
)

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Utility Tools
# ---------------------------------------------------------------------------

def get_recent_topics_from_worklog(
    worklog_path: Optional[Path] = None,
) -> List[str]:
    """Reads the last topics logged in WORKLOG.md to avoid topic duplication."""
    p = worklog_path or (BASE_DIR / "WORKLOG.md")
    if not p.exists():
        return []

    topics = []
    try:
        content = p.read_text(encoding="utf-8")
        for line in content.splitlines():
            if line.startswith("|") and not line.startswith("| 날짜") and "---" not in line:
                parts = [col.strip() for col in line.split("|")]
                if len(parts) >= 3 and parts[2]:
                    topics.append(parts[2])
    except Exception as e:
        logger.warning(f"Could not parse WORKLOG.md: {e}")
    return topics[-10:]


def append_to_worklog(
    date_str: str,
    theme: str,
    headline: str,
    scripture_ref: str,
    theology_risk: float,
    poster_filename: str,
    drive_link: str,
    worklog_path: Optional[Path] = None,
) -> None:
    """Records daily poster generation history into WORKLOG.md."""
    p = worklog_path or (BASE_DIR / "WORKLOG.md")
    header = (
        "# 🕊️ 포이에마성령교회 일간 말씀 포스터 제작 히스토리 (WORKLOG)\n\n"
        "이 문서는 매일 자동 생성된 말씀 광고 포스터의 기획 주제, 신학 검증 결과 및 배포 상태를 기록합니다.\n\n"
        "| 날짜 | 주제 | 메인 헤드라인 | 대표 성경 구절 | TypeSafe 위험도 | 결과물 파일 | 배포 상태 |\n"
        "| :--- | :--- | :--- | :--- | :---: | :--- | :--- |\n"
    )

    if not p.exists():
        p.write_text(header, encoding="utf-8")

    risk_display = (
        f"{theology_risk:.2f} (안전)"
        if theology_risk <= 0.3
        else f"{theology_risk:.2f} (주의)"
    )
    row = f"| {date_str} | {theme} | {headline} | {scripture_ref} | {risk_display} | `{poster_filename}` | {drive_link} |\n"

    with open(p, "a", encoding="utf-8") as f:
        f.write(row)
    logger.info(f"Updated WORKLOG.md with daily entry: {theme} ({date_str})")


# ---------------------------------------------------------------------------
# Creative Aesthetic Seed Pool (High-Art Fallback Library)
# ---------------------------------------------------------------------------

AESTHETIC_SEED_POOL = [
    {
        "form_factor": "verse_card",
        "theme": "말씀의 빛과 길",
        "headline": "주의 말씀은 내 발에 등이요",
        "calligraphy_emphasis": ["말씀", "등"],
        "scripture_ref": "시편 119:105",
        "scripture_text": "주의 말씀은 내 발에 등이요 내 길에 빛이니이다",
        "meditation": "어두운 세상의 혼란 속에서도 주님의 말씀은 우리의 걸음을 밝히는 가장 확실한 등불입니다.",
        "call_to_action": "오늘 하루, 기록된 진리의 말씀을 마음에 새기며 흔들림 없이 동행하십시오.",
        "visual_concept": "Soft natural morning light falling on raw linen fabric, fresh olive leaves casting a serene gentle shadow, neutral beige tones",
    },
    {
        "form_factor": "gospel_leaflet",
        "theme": "지친 영혼의 참된 쉼",
        "headline": "수고하고 무거운 짐 진 자들아",
        "calligraphy_emphasis": ["수고하고", "짐"],
        "scripture_ref": "마태복음 11:28",
        "scripture_text": "수고하고 무거운 짐 진 자들아 다 내게로 오라 내가 너희를 쉬게 하리라",
        "meditation": "세상은 끊임없이 더 많은 조건과 증명을 요구하지만, 예수님은 당신의 지친 무릎과 눈물을 그대로 안아주십니다. 참된 평안과 쉼은 주님의 십자가 사랑 안에 있습니다.",
        "call_to_action": "지친 일상 속에서 잠시 멈추어, 당신을 부르시는 주님의 품 안에서 영혼의 쉼을 누리세요.",
        "visual_concept": "Cozy aesthetic cafe window bathed in warm golden hour light, tranquil steam rising from a ceramic mug, soothing atmosphere",
    },
    {
        "form_factor": "devotional_postcard",
        "theme": "성령 안에서 누리는 자유",
        "headline": "오직 성령으로 충만함을 받으라",
        "calligraphy_emphasis": ["성령", "충만"],
        "scripture_ref": "에베소서 5:18",
        "scripture_text": "술 취하지 말라 이는 방탕한 것이니 오직 성령으로 충만함을 받으라",
        "meditation": "주님, 나의 모든 조급함과 두려움을 내려놓고 성령 하나님의 세미한 음성에 온전히 귀 기울입니다. 내 삶을 인도하소서.",
        "call_to_action": "성령의 임재로 마음을 채우고 은혜의 능력으로 하루를 승리하십시오.",
        "visual_concept": "Minimalist misty green dawn over a completely still lake, soft ethereal celestial glow, textured fine-art watercolor look",
    },
    {
        "form_factor": "verse_card",
        "theme": "두려움을 이기는 언약",
        "headline": "내가 너와 항상 함께하리라",
        "calligraphy_emphasis": ["함께", "항상"],
        "scripture_ref": "이사야 41:10",
        "scripture_text": "두려워하지 말라 내가 너와 함께 함이라 놀라지 말라 나는 네 하나님이 됨이라",
        "meditation": "홀로 걷는 것 같은 광야에서도 임마누엘 하나님은 결코 당신의 손을 놓지 않으십니다.",
        "call_to_action": "강하고 담대하십시오. 당신을 지키시는 분은 졸지도 주무시지도 않습니다.",
        "visual_concept": "Delicate dried wildflowers arranged on warm artisanal paper, soft sunbeam hitting the surface, Kinfolk aesthetic",
    },
]


# ---------------------------------------------------------------------------
# Master Pipeline Orchestrator
# ---------------------------------------------------------------------------

class PosterPipelineOrchestrator:
    """Coordinates the 4 agents to execute modern Christian stationery generation."""

    def __init__(self, config_path: Optional[Path] = None):
        import yaml

        self.config_path = config_path or (BASE_DIR / "config.yaml")
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.typesafe_key = os.getenv("TYPESAFE_API_KEY")

    def run_spiritual_copywriter(
        self,
        topic_override: Optional[str] = None,
        form_factor_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Agent 1 (Spiritual Copywriter): Plans orthodox, creative Christian copy."""
        recent_topics = get_recent_topics_from_worklog()
        logger.info(f"[Spiritual Copywriter] Recent WORKLOG topics: {recent_topics}")

        today_str = datetime.now().strftime("%Y.%m.%d")
        
        # Decide form factor
        form_factors = ["verse_card", "gospel_leaflet", "devotional_postcard"]
        chosen_form = form_factor_override or random.choice(form_factors)

        # 1. Dynamic Gemini Generation
        if self.gemini_key and self.gemini_key.strip():
            try:
                from google import genai
                from google.genai import types

                system_prompt = (
                    "당신은 '포이에마성령교회'의 복음주의 영성 카피라이터이자 기독교 에세이스트(Spiritual Copywriter)입니다.\n"
                    "과거의 진부하고 딱딱한 '행사 포스터'나 설교 3단 요약 강의안 틀을 완전히 탈피하여, "
                    "인스타그램 감성 말씀카드, 마음을 어루만지는 따뜻한 전도지, 깊은 묵상 엽서 형태로 기획하세요.\n\n"
                    "신학적 원칙:\n"
                    "- 100% 개역개정 성경 정경 66권 기반, 건전한 정통 복음주의 신학 준수.\n"
                    "- 신천지, 구원파, 하나님의교회, JMS 등 한국 이단의 은어나 왜곡된 비유풀이를 절대 쓰지 마십시오.\n\n"
                    "폼팩터 가이드라인:\n"
                    "1. verse_card (감성 말씀 카드): 1개 핵심 구절 중심, 붓으로 쓸 헤드라인, 1~2줄의 깊은 묵상.\n"
                    "2. gospel_leaflet (스토리 전도지): 현대인의 지친 일상에 건네는 공감 질문 헤드라인, 3~4줄의 따뜻한 복음 에세이, 언약의 말씀.\n"
                    "3. devotional_postcard (데일리 묵상 엽서): 아침 묵상 선포 헤드라인, 말씀 구절, 정갈한 '오늘의 기도' 문구.\n"
                )

                topic_req = (
                    f"지정 주제: {topic_override}"
                    if topic_override
                    else f"최근 주제들({recent_topics})과 중복되지 않는 신선하고 깊은 은혜/평안/성령/동행 주제 선정"
                )

                user_prompt = (
                    f"오늘 날짜: {today_str}\n"
                    f"선택 폼팩터: {chosen_form}\n"
                    f"{topic_req}\n\n"
                    "다음 JSON 구조로 응답하세요:\n"
                    "{\n"
                    f'  "form_factor": "{chosen_form}",\n'
                    '  "date_str": "YYYY.MM.DD",\n'
                    '  "theme": "주제명",\n'
                    '  "headline": "붓글씨로 그릴 유려한 캘리그라피 헤드라인 (10~15자 내외)",\n'
                    '  "calligraphy_emphasis": ["붓에 힘을 실어 크게 강조할 핵심 단어1", "핵심단어2"],\n'
                    '  "scripture_ref": "성경 권 장:절 (예: 시편 119:105)",\n'
                    '  "scripture_text": "개역개정 정경 성경 말씀 본문",\n'
                    '  "meditation": "읽는 이의 마음을 울리는 감성 묵상 또는 복음 에세이 (2~4줄)",\n'
                    '  "call_to_action": "축복 및 권면의 한 줄 문구",\n'
                    '  "visual_concept": "Imagen 3용 영문 감성 비주얼 묘사 (킨포크, 35mm 필름, 린넨, 아침 햇살 등 미니멀한 자연 오브제 위주)"\n'
                    "}"
                )

                client = genai.Client(api_key=self.gemini_key)
                # Try gemini-2.5-flash, fallback to gemini-2.0-flash
                try:
                    target_model = "gemini-2.5-flash"
                    response = client.models.generate_content(
                        model=target_model,
                        contents=[user_prompt],
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            response_mime_type="application/json",
                        ),
                    )
                except Exception:
                    target_model = "gemini-2.0-flash"
                    response = client.models.generate_content(
                        model=target_model,
                        contents=[user_prompt],
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            response_mime_type="application/json",
                        ),
                    )
                data = json.loads(response.text)
                data["date_str"] = today_str
                data["form_factor"] = chosen_form
                logger.info(f"[Spiritual Copywriter] Successfully planned '{data.get('theme')}' ({chosen_form})")
                return data

            except Exception as e:
                logger.warning(f"LLM Copywriter failed ({e}). Using aesthetic seed pool.")

        # 2. Curated Aesthetic Seed Fallback
        for seed in AESTHETIC_SEED_POOL:
            if seed["theme"] not in recent_topics:
                selected = dict(seed)
                selected["date_str"] = today_str
                if form_factor_override:
                    selected["form_factor"] = form_factor_override
                logger.info(f"[Spiritual Copywriter] Selected aesthetic seed: '{selected['theme']}' ({selected['form_factor']})")
                return selected

        selected = dict(AESTHETIC_SEED_POOL[0])
        selected["date_str"] = today_str
        if form_factor_override:
            selected["form_factor"] = form_factor_override
        return selected

    def run_theology_auditor(
        self, draft_content: Dict[str, Any]
    ) -> TheologyAuditResult:
        """Agent 2 (Theology Auditor): Executes 3-tier heresy guardrails."""
        logger.info(f"[Theology Auditor] Auditing content for theme '{draft_content.get('theme')}'...")
        threshold = (
            self.config.get("guardrails", {})
            .get("typesafe", {})
            .get("risk_threshold", 0.3)
        )
        result = audit_poster_content(draft_content, risk_threshold=threshold)
        return result

    def run_visual_art_director(
        self,
        theme: str,
        visual_concept: str,
        form_factor: str = "verse_card",
        forced_genre: Optional[str] = None,
        engine_choice: str = "auto",
        date_str: str = "",
        output_dir: Optional[Path] = None,
    ) -> Path:
        """Agent 3 (Visual Art Director): Prompts & triggers AI for background."""
        logger.info(f"[Visual Art Director] Directing background artwork for theme '{theme}' ({form_factor}, genre: {forced_genre})...")
        prompt = build_imagen_prompt(theme, visual_concept, form_factor=form_factor)
        out_dir = output_dir or (BASE_DIR / "output")
        out_dir.mkdir(parents=True, exist_ok=True)
        today_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
        bg_path = out_dir / f"bg_{today_slug}.png"

        aspect = self.config.get("image_generation", {}).get("aspect_ratio", "9:16")
        width = self.config.get("image_generation", {}).get("width", 1080)
        height = self.config.get("image_generation", {}).get("height", 1920)

        return generate_background_image(
            prompt=prompt,
            output_path=bg_path,
            api_key=self.gemini_key,
            aspect_ratio=aspect,
            width=width,
            height=height,
            date_str=date_str,
            theme=theme,
            form_factor=form_factor,
            visual_concept=visual_concept,
            forced_genre=forced_genre,
            engine_choice=engine_choice,
        )

    def run_publishing_manager(
        self,
        bg_image_path: Path,
        content: Dict[str, Any],
        audit_result: TheologyAuditResult,
        dry_run: bool = False,
    ) -> Tuple[Path, Dict[str, Any]]:
        """Agent 4 (Publishing Manager): Composes artwork, sends via Gmail, and updates WORKLOG."""
        logger.info(f"[Publishing Manager] Beginning bespoke graphic composition & distribution...")

        today_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
        form_tag = content.get("form_factor", "card")
        poster_filename = f"poiema_{form_tag}_{today_slug}.png"
        out_path = BASE_DIR / "output" / poster_filename

        # 1. Graphic composition (Pillow)
        final_poster_path = compose_poster(
            bg_image_path, content, self.config, out_path
        )

        dispatch_status_parts = []

        # 2. Email Dispatch via Gmail
        email_info = {"sent": False, "message": "Email disabled in config"}
        if not dry_run and self.config.get("email", {}).get("enabled", True):
            church_name = self.config.get("church", {}).get("name", "포이에마성령교회")
            email_ok, email_msg = send_daily_poster_email(
                poster_path=final_poster_path,
                content=content,
                church_name=church_name,
            )
            email_info = {"sent": email_ok, "message": email_msg}
            if email_ok:
                dispatch_status_parts.append("✉️ Gmail 발송 완료")
            else:
                dispatch_status_parts.append("✉️ Gmail 미발송")

        # 3. Cloud Publishing (Google Drive) - Optional
        drive_info = {"uploaded": False, "web_view_link": str(final_poster_path)}
        if not dry_run and self.config.get("drive", {}).get("enabled", False):
            folder_id = self.config.get("drive", {}).get("folder_id")
            sa_path = self.config.get("drive", {}).get("service_account_path")
            success, drive_info = upload_poster_to_drive(
                final_poster_path,
                folder_id=folder_id,
                service_account_path=sa_path,
                custom_title=f"포이에마_{content.get('theme')}_{content.get('date_str')}.png",
            )
            if success and drive_info.get("uploaded"):
                dispatch_status_parts.append(f"[드라이브 링크]({drive_info.get('web_view_link')})")

        dispatch_status_str = " / ".join(dispatch_status_parts) if dispatch_status_parts else "로컬 보관"

        # 4. Log to WORKLOG.md
        sc_ref = content.get("scripture_ref", "말씀")

        append_to_worklog(
            date_str=content.get("date_str", datetime.now().strftime("%Y.%m.%d")),
            theme=f"[{form_tag}] {content.get('theme', '말씀 묵상')}",
            headline=content.get("headline", ""),
            scripture_ref=sc_ref,
            theology_risk=audit_result.risk_score,
            poster_filename=poster_filename,
            drive_link=dispatch_status_str,
        )

        return final_poster_path, {
            "email_info": email_info,
            "drive_info": drive_info,
        }

    def execute_full_pipeline(
        self,
        topic_override: Optional[str] = None,
        form_factor_override: Optional[str] = None,
        forced_genre: Optional[str] = None,
        engine_choice: str = "auto",
        dry_run: bool = False,
        agent_listener: Optional[Any] = None,
        intervention_callback: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Runs the pipeline with agent communication feed and optional human intervention."""
        def notify(agent_name: str, message: str, data: Any = None):
            logger.info(f"[{agent_name}] {message}")
            if agent_listener:
                try:
                    agent_listener(agent_name, message, data)
                except Exception:
                    pass

        max_retries = (
            self.config.get("guardrails", {})
            .get("typesafe", {})
            .get("max_retries", 3)
        )

        notify("System", f"=== 포이에마 말씀 콘텐츠 파이프라인 가동 (최대 재시도: {max_retries}) ===")
        ensure_fonts_exist(BASE_DIR / "fonts")

        attempt = 1
        content = None
        audit_res = None

        while attempt <= max_retries:
            notify("System", f"파이프라인 시도 #{attempt}/{max_retries} 시작...")
            
            # Step 1: Spiritual Copywriter
            notify("Spiritual Copywriter", "말씀 기획 및 복음 카피 작성 중...")
            content = self.run_spiritual_copywriter(
                topic_override=topic_override,
                form_factor_override=form_factor_override,
            )
            notify(
                "Spiritual Copywriter",
                f"기획 완료! [주제: {content.get('theme')}] [헤드라인: {content.get('headline')}]",
                data=content,
            )

            # Optional Human-in-the-Loop Intervention (사용자 중간 개입)
            if intervention_callback:
                notify("System", "👤 사용자의 카피 검토 및 중간 개입 대기 중...")
                modified_content = intervention_callback(content)
                if modified_content and isinstance(modified_content, dict):
                    content = modified_content
                    notify("Spiritual Copywriter", f"사용자 수정 사항이 반영되었습니다: [헤드라인: {content.get('headline')}]")

            # Step 2: Theology Auditor
            notify("Theology Auditor", f"3중 신학 가드레일(블랙리스트 + TypeSafe AI Jev + 정경 검증) 심사 시작...")
            audit_res = self.run_theology_auditor(content)

            if audit_res.is_theologically_sound:
                notify(
                    "Theology Auditor",
                    f"✓ 신학 검증 통과! (위험도: {audit_res.risk_score:.2f}, 레이어: {audit_res.failed_layer})",
                    data=audit_res.dict(),
                )
                break
            else:
                notify(
                    "Theology Auditor",
                    f"✗ 신학 검증 반려 (시도 #{attempt}): {audit_res.reason}",
                    data=audit_res.dict(),
                )
                attempt += 1

        if not audit_res or not audit_res.is_theologically_sound:
            raise RuntimeError(
                f"Theology Guardrail rejected content after {max_retries} attempts."
            )

        # Step 3: Visual Art Director
        theme = content.get("theme", "은혜와 평안")
        concept = content.get("visual_concept", "")
        date_str = content.get("date_str", "")
        form_factor = content.get("form_factor", "verse_card")
        
        notify(
            "Visual Art Director",
            f"배경 비주얼 생성 착수 (폼팩터: {form_factor}, 스타일: {forced_genre or '자동'}, 엔진: {engine_choice})...",
        )
        bg_path = self.run_visual_art_director(
            theme,
            concept,
            form_factor=form_factor,
            forced_genre=forced_genre,
            engine_choice=engine_choice,
            date_str=date_str,
        )
        notify("Visual Art Director", f"✓ 배경 아트워크 생성 완료: {bg_path.name}")

        # Step 4: Graphics Composition & Publishing
        notify("Publishing Manager", "수묵 캘리그래피 및 붉은 전각 낙관 정밀 조판 시작...")
        final_poster, dispatch_info = self.run_publishing_manager(
            bg_path, content, audit_res, dry_run=dry_run
        )
        notify("Publishing Manager", f"✓ 최종 결과물 완성: {final_poster.name}")

        return {
            "success": True,
            "theme": theme,
            "form_factor": form_factor,
            "headline": content.get("headline"),
            "poster_path": str(final_poster),
            "dispatch_info": dispatch_info,
            "drive_info": dispatch_info.get("drive_info", {}),
            "theology_audit": audit_res.dict(),
            "content": content,
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = PosterPipelineOrchestrator()
    result = pipeline.execute_full_pipeline(dry_run=True)
    print("\nPipeline Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
