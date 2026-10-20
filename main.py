"""Main CLI Entry Point for Poiema Daily Gospel Poster Pipeline.

Usage:
  python main.py                  # Full automated daily pipeline
  python main.py --dry-run        # Run locally without Google Drive upload
  python main.py --topic "은혜"   # Specify custom topic
  python main.py --show-contact   # Force show church contact information
"""

import argparse
import io
import json
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure standard output supports UTF-8 on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Load environment variables from .env if present
load_dotenv()

from crew_setup import PosterPipelineOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("PoiemaPosterPipeline")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="포이에마성령교회 일간 전도 및 말씀 광고 포스터 자동 생성 파이프라인"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="생성할 말씀 포스터의 특정 주제 (미지정 시 WORKLOG 참고 후 자동 기획)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="클라우드 업로드 없이 로컬 생성 및 합성만 테스트",
    )
    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Google Drive 업로드를 건너뛰고 로컬에만 저장",
    )
    parser.add_argument(
        "--show-contact",
        action="store_true",
        help="교회 연락처 배너를 강제로 포스터 하단에 노출",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="설정 파일 경로 (기본값: config.yaml)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logger.info("Starting Poiema Daily Gospel Poster Automation...")

    # Handle contact override
    if args.show_contact:
        os.environ["SHOW_CHURCH_CONTACT"] = "true"

    dry_run = args.dry_run or args.no_upload

    try:
        config_path = Path(args.config)
        orchestrator = PosterPipelineOrchestrator(config_path=config_path)
        result = orchestrator.execute_full_pipeline(
            topic_override=args.topic,
            dry_run=dry_run,
        )

        logger.info("\n" + "=" * 60)
        logger.info("🎉 포스터 생성 및 검증 파이프라인이 성공적으로 완료되었습니다!")
        logger.info(f"■ 주제: {result.get('theme')}")
        logger.info(f"■ 메인 헤드라인: {result.get('headline')}")
        logger.info(f"■ 결과물 경로: {result.get('poster_path')}")
        logger.info(
            f"■ 신학 가드레일 위험도: {result.get('theology_audit', {}).get('risk_score', 0.0):.2f}"
        )
        logger.info(
            f"■ Google Drive 링크: {result.get('drive_info', {}).get('web_view_link')}"
        )
        logger.info("=" * 60 + "\n")
        return 0

    except Exception as e:
        logger.exception(f"❌ 파이프라인 실행 중 치명적 오류가 발생했습니다: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
