"""CrewAI Multi-Agent Pipeline Setup for Poiema Poster Generation.

Agents:
1. Spiritual Copywriter: Analyzes WORKLOG.md and drafts orthodox gospel copy.
2. Theology Auditor: Runs 3-tier heresy guardrails (Blacklist -> TypeSafe Jev -> Scripture).
3. Visual Art Director: Crafts optimized Imagen 3 prompts and generates backgrounds.
4. Publishing Manager: Coordinates font check, Pillow composition, Drive upload, and WORKLOG commit.
"""

from datetime import datetime
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
from pydantic import BaseModel, Field

from drive_uploader import upload_poster_to_drive
from guardrails.theology_guard import (
    PosterContent,
    TheologyAuditResult,
    audit_poster_content,
)
from image_composer import compose_poster
from utils.font_downloader import ensure_fonts_exist
from utils.image_generator import (
    build_imagen_prompt,
    generate_background_image,
)

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Utility Tools for CrewAI Agents
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
            # Parse markdown table lines: | YYYY-MM-DD | Theme | ...
            if line.startswith("|") and not line.startswith("| 날짜") and "---" not in line:
                parts = [col.strip() for col in line.split("|")]
                if len(parts) >= 3 and parts[2]:
                    topics.append(parts[2])
    except Exception as e:
        logger.warning(f"Could not parse WORKLOG.md: {e}")
    return topics[-10:]  # Return last 10 themes


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
        "| 날짜 | 주제 | 메인 헤드라인 | 대표 성경 구절 | TypeSafe 위험도 | 결과물 파일 | Google Drive 상태 |\n"
        "| :--- | :--- | :--- | :--- | :---: | :--- | :--- |\n"
    )

    if not p.exists():
        p.write_text(header, encoding="utf-8")

    # Format row
    risk_display = (
        f"{theology_risk:.2f} (안전)"
        if theology_risk <= 0.3
        else f"{theology_risk:.2f} (주의)"
    )
    drive_display = (
        f"[드라이브 링크]({drive_link})"
        if drive_link.startswith("http")
        else "로컬 보관"
    )
    row = f"| {date_str} | {theme} | {headline} | {scripture_ref} | {risk_display} | `{poster_filename}` | {drive_display} |\n"

    with open(p, "a", encoding="utf-8") as f:
        f.write(row)
    logger.info(f"Updated WORKLOG.md with daily entry: {theme} ({date_str})")


# ---------------------------------------------------------------------------
# Offline & Online Copywriting Engine
# ---------------------------------------------------------------------------

CURATED_THEMES_PRESETS = [
    {
        "theme": "성령 충만과 내면의 평안",
        "headline": "오직 성령으로 충만함을 받으라",
        "sub_headline": "주님의 영이 임하는 곳에 참된 자유와 온전한 쉼이 있습니다",
        "points": [
            {
                "title": "진리의 영으로 깨어남",
                "description": "보혜사 성령님께서 우리의 생각을 지키시고 모든 은혜 가운데로 인도하십니다.",
                "scripture": {
                    "reference": "요한복음 14:26",
                    "text": "보혜사 곧 아버지께서 내 이름으로 보내실 성령 그가 너희에게 모든 것을 가르치시고",
                },
            },
            {
                "title": "연약함을 도우시는 중보",
                "description": "우리가 마땅히 기도할 바를 알지 못할 때도 성령께서 친히 말할 수 없는 탄식으로 간구하십니다.",
                "scripture": {
                    "reference": "로마서 8:26",
                    "text": "이와 같이 성령도 우리의 연약함을 도우시나니 우리는 마땅히 기도할 바를 알지 못하나",
                },
            },
            {
                "title": "아름다운 성령의 열매",
                "description": "세상의 기준이 아닌 주님의 사랑과 희락과 화평으로 세상을 이기는 능력을 얻습니다.",
                "scripture": {
                    "reference": "갈라디아서 5:22-23",
                    "text": "오직 성령의 열매는 사랑과 희락과 화평과 오래 참음과 자비와 양선과 충성과",
                },
            },
        ],
        "call_to_action": "오늘 하루, 성령 하나님을 깊이 의지하며 세상이 줄 수 없는 평안을 누리십시오.",
        "visual_concept": "Golden divine rays streaming from above into an open peaceful mountain meadow, holy aura",
    },
    {
        "theme": "말씀의 능력과 승리의 삶",
        "headline": "주의 말씀은 내 발에 등이요",
        "sub_headline": "어두운 세상 속에서 흔들리지 않는 빛과 인도하심을 따릅니다",
        "points": [
            {
                "title": "인생의 바른 길잡이",
                "description": "사람의 생각과 세상 풍조가 아닌 영원히 변치 않는 진리의 말씀 위에 섭니다.",
                "scripture": {
                    "reference": "시편 119:105",
                    "text": "주의 말씀은 내 발에 등이요 내 길에 빛이니이다",
                },
            },
            {
                "title": "살아있고 활력 있는 권능",
                "description": "하나님의 말씀은 우리의 영혼과 관절과 골수를 찔러 쪼개며 참된 생명력을 회복시킵니다.",
                "scripture": {
                    "reference": "히브리서 4:12",
                    "text": "하나님의 말씀은 살아 있고 활력이 있어 좌우에 날선 어떤 검보다도 예리하여",
                },
            },
            {
                "title": "믿음의 든든한 반석",
                "description": "말씀을 듣고 삶으로 살아내는 자는 어떤 비바람에도 흔들리지 않는 집을 짓습니다.",
                "scripture": {
                    "reference": "마태복음 7:24",
                    "text": "그러므로 누구든지 나의 이 말을 듣고 행하는 자는 그 집을 반석 위에 지은 지혜로운 사람 같으리니",
                },
            },
        ],
        "call_to_action": "오늘도 기록된 언약의 말씀을 묵상하며 확신 가운데 담대히 전진하십시오.",
        "visual_concept": "An ancient open Bible illuminated by soft celestial golden light beam, serene sanctuary",
    },
    {
        "theme": "주님과의 친밀한 동행",
        "headline": "내가 너와 항상 함께하리라",
        "sub_headline": "두려움을 이기고 주님의 강한 오른손을 붙드는 온전한 신뢰",
        "points": [
            {
                "title": "임마누엘 하나님의 약속",
                "description": "홀로 걷는 고난의 길에서도 주님은 결코 우리를 떠나지 아니하시며 지켜주십니다.",
                "scripture": {
                    "reference": "이사야 41:10",
                    "text": "두려워하지 말라 내가 너와 함께 함이라 놀라지 말라 나는 네 하나님이 됨이라",
                },
            },
            {
                "title": "선한 목자의 인도하심",
                "description": "푸른 풀밭과 쉴 만한 물가로 이끄시는 주님 안에서 부족함 없는 만족을 고백합니다.",
                "scripture": {
                    "reference": "시편 23:1-2",
                    "text": "여호와는 나의 목자시니 내게 부족함이 없으리로다 그가 나를 푸른 풀밭에 누이시며",
                },
            },
            {
                "title": "날마다 더해지는 새 힘",
                "description": "오직 여호와를 앙망하는 자는 독수리가 날개 치며 올라감 같은 새 능력을 얻습니다.",
                "scripture": {
                    "reference": "이사야 40:31",
                    "text": "오직 여호와를 앙망하는 자는 새 힘을 얻으리니 독수리가 날개치며 올라감 같을 것이요",
                },
            },
        ],
        "call_to_action": "어떤 순간에도 나를 사랑하시는 주님의 손을 놓지 않고 기쁨으로 동행합시다.",
        "visual_concept": "A peaceful tranquil path through a sun-drenched majestic pine forest, radiant light",
    },
]


class PosterPipelineOrchestrator:
    """Coordinates the 4 agents to execute the poster generation pipeline."""

    def __init__(self, config_path: Optional[Path] = None):
        import yaml

        self.config_path = config_path or (BASE_DIR / "config.yaml")
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.typesafe_key = os.getenv("TYPESAFE_API_KEY")

    def run_spiritual_copywriter(
        self, topic_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Agent 1 (Spiritual Copywriter): Plans orthodox gospel content."""
        recent_topics = get_recent_topics_from_worklog()
        logger.info(
            f"[Spiritual Copywriter] Recent WORKLOG topics: {recent_topics}"
        )

        today_str = datetime.now().strftime("%Y.%m.%d")

        # 1. If Gemini API is available, generate dynamically using LLM
        if self.gemini_key and self.gemini_key.strip():
            try:
                from google import genai
                from google.genai import types

                system_prompt = (
                    "당신은 '포이에마성령교회'의 복음주의 말씀 기획 카피라이터(Spiritual Copywriter)입니다. "
                    "정통 기독교(개역개정 성경)에 기반하여 신학적으로 건전하고 성도들에게 깊은 위로와 도전을 주는 "
                    "일간 말씀 광고 포스터 기획안을 JSON으로 작성하세요.\n"
                    "절대로 신천지, 구원파, 하나님의교회, JMS 등 한국 이단의 용어나 교리 왜곡(비유풀이, 14만4천, 어머니하나님, 섭리사 등)을 쓰지 마십시오.\n"
                    "최근 다룬 주제와 겹치지 않는 새로운 주제(성령 충만, 은혜, 동행, 감사, 회개, 믿음, 소망 등)를 선택하세요."
                )

                topic_req = (
                    f"주제: {topic_override}"
                    if topic_override
                    else f"최근 주제들({recent_topics})과 중복되지 않는 새로운 성령/은혜 주제 선정"
                )

                user_prompt = (
                    f"오늘 날짜: {today_str}\n{topic_req}\n\n"
                    "다음 JSON 구조로 응답하세요:\n"
                    "{\n"
                    '  "date_str": "YYYY.MM.DD",\n'
                    '  "theme": "주제명",\n'
                    '  "headline": "대형 캘리그라피 메인 헤드라인 (15자 내외)",\n'
                    '  "sub_headline": "헤드라인 보조 설명 문구",\n'
                    '  "points": [\n'
                    '    {"title": "소제목1", "description": "묵상 설명", "scripture": {"reference": "성경 장:절", "text": "개역개정 말씀"}},\n'
                    '    {"title": "소제목2", "description": "묵상 설명", "scripture": {"reference": "성경 장:절", "text": "개역개정 말씀"}},\n'
                    '    {"title": "소제목3", "description": "묵상 설명", "scripture": {"reference": "성경 장:절", "text": "개역개정 말씀"}}\n'
                    "  ],\n"
                    '  "call_to_action": "축복 및 권면의 한 줄 문구",\n'
                    '  "visual_concept": "Imagen 3용 영문 시각 배경 묘사 (영어 2~3문장)"\n'
                    "}"
                )

                client = genai.Client(api_key=self.gemini_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[user_prompt],
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                    ),
                )
                data = json.loads(response.text)
                data["date_str"] = today_str
                logger.info(
                    f"[Spiritual Copywriter] Successfully planned theme: '{data.get('theme')}'"
                )
                return data

            except Exception as e:
                logger.warning(
                    f"LLM Copywriter failed ({e}). Using curated orthodox preset library."
                )

        # 2. Curated Preset Fallback
        for preset in CURATED_THEMES_PRESETS:
            if preset["theme"] not in recent_topics:
                selected = dict(preset)
                selected["date_str"] = today_str
                logger.info(
                    f"[Spiritual Copywriter] Selected curated orthodox theme: '{selected['theme']}'"
                )
                return selected

        # If all were used, pick the first one
        selected = dict(CURATED_THEMES_PRESETS[0])
        selected["date_str"] = today_str
        return selected

    def run_theology_auditor(
        self, draft_content: Dict[str, Any]
    ) -> TheologyAuditResult:
        """Agent 2 (Theology Auditor): Executes 3-tier heresy guardrails."""
        logger.info(
            f"[Theology Auditor] Auditing content for theme '{draft_content.get('theme')}'..."
        )
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
        output_dir: Optional[Path] = None,
    ) -> Path:
        """Agent 3 (Visual Art Director): Prompts & triggers Imagen 3 for background."""
        logger.info(
            f"[Visual Art Director] Directing background artwork for theme '{theme}'..."
        )
        prompt = build_imagen_prompt(theme, visual_concept)
        out_dir = output_dir or (BASE_DIR / "output")
        out_dir.mkdir(parents=True, exist_ok=True)
        today_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
        bg_path = out_dir / f"bg_{today_slug}.png"

        aspect = self.config.get("image_generation", {}).get(
            "aspect_ratio", "9:16"
        )
        width = self.config.get("image_generation", {}).get("width", 1080)
        height = self.config.get("image_generation", {}).get("height", 1920)

        return generate_background_image(
            prompt=prompt,
            output_path=bg_path,
            api_key=self.gemini_key,
            aspect_ratio=aspect,
            width=width,
            height=height,
        )

    def run_publishing_manager(
        self,
        bg_image_path: Path,
        content: Dict[str, Any],
        audit_result: TheologyAuditResult,
        dry_run: bool = False,
    ) -> Tuple[Path, Dict[str, Any]]:
        """Agent 4 (Publishing Manager): Composes poster, uploads to Drive, and updates WORKLOG."""
        logger.info(
            f"[Publishing Manager] Beginning final graphic composition & distribution..."
        )

        today_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
        poster_filename = f"poiema_poster_{today_slug}.png"
        out_path = BASE_DIR / "output" / poster_filename

        # 1. Graphic composition (Pillow)
        final_poster_path = compose_poster(
            bg_image_path, content, self.config, out_path
        )

        # 2. Cloud Publishing (Google Drive)
        drive_info = {"uploaded": False, "web_view_link": str(final_poster_path)}
        if not dry_run and self.config.get("drive", {}).get("enabled", True):
            folder_id = self.config.get("drive", {}).get("folder_id")
            sa_path = self.config.get("drive", {}).get("service_account_path")
            success, drive_info = upload_poster_to_drive(
                final_poster_path,
                folder_id=folder_id,
                service_account_path=sa_path,
                custom_title=f"포이에마_말씀광고_{content.get('theme')}_{content.get('date_str')}.png",
            )

        # 3. Log to WORKLOG.md
        first_sc = "말씀 인용"
        points = content.get("points", [])
        if points:
            first_pt = points[0]
            sc_obj = (
                first_pt.get("scripture", {})
                if isinstance(first_pt, dict)
                else getattr(first_pt, "scripture")
            )
            first_sc = (
                sc_obj.get("reference", "말씀")
                if isinstance(sc_obj, dict)
                else getattr(sc_obj, "reference", "말씀")
            )

        append_to_worklog(
            date_str=content.get(
                "date_str", datetime.now().strftime("%Y.%m.%d")
            ),
            theme=content.get("theme", "말씀 묵상"),
            headline=content.get("headline", ""),
            scripture_ref=first_sc,
            theology_risk=audit_result.risk_score,
            poster_filename=poster_filename,
            drive_link=drive_info.get("web_view_link", "로컬"),
        )

        return final_poster_path, drive_info

    def execute_full_pipeline(
        self,
        topic_override: Optional[str] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Runs the entire pipeline with retry loop (up to max_retries) on guardrail failure."""
        max_retries = (
            self.config.get("guardrails", {})
            .get("typesafe", {})
            .get("max_retries", 3)
        )

        logger.info(
            f"=== Starting Poiema Gospel Poster Pipeline (Max Retries: {max_retries}) ==="
        )

        # Pre-flight: Ensure font readiness
        ensure_fonts_exist(BASE_DIR / "fonts")

        attempt = 1
        content = None
        audit_res = None

        while attempt <= max_retries:
            logger.info(f"--- Pipeline Attempt #{attempt}/{max_retries} ---")
            # Step 1: Copywriting
            content = self.run_spiritual_copywriter(
                topic_override=topic_override
            )

            # Step 2: 3-Tier Theology Guardrail
            audit_res = self.run_theology_auditor(content)

            if audit_res.is_theologically_sound:
                logger.info(
                    f"✓ Guardrail PASSED! (Risk score: {audit_res.risk_score:.2f}, Layer: {audit_res.failed_layer})"
                )
                break
            else:
                logger.warning(
                    f"✗ Guardrail REJECTED on attempt #{attempt}: {audit_res.reason}"
                )
                logger.info(
                    f"Feedback for Copywriter: {audit_res.feedback_for_copywriter}"
                )
                attempt += 1

        if not audit_res or not audit_res.is_theologically_sound:
            raise RuntimeError(
                f"Theology Guardrail rejected content after {max_retries} attempts. Reason: {audit_res.reason if audit_res else 'Unknown'}"
            )

        # Step 3: Visual Background Generation
        theme = content.get("theme", "은혜와 평안")
        concept = content.get(
            "visual_concept",
            "Golden heavenly light shining down on peaceful sanctuary",
        )
        bg_path = self.run_visual_art_director(theme, concept)

        # Step 4: Graphics Composition & Publishing
        final_poster, drive_info = self.run_publishing_manager(
            bg_path, content, audit_res, dry_run=dry_run
        )

        return {
            "success": True,
            "theme": theme,
            "headline": content.get("headline"),
            "poster_path": str(final_poster),
            "drive_info": drive_info,
            "theology_audit": audit_res.dict(),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = PosterPipelineOrchestrator()
    result = pipeline.execute_full_pipeline(dry_run=True)
    print("\nPipeline Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
