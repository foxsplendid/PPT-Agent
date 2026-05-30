"""PDF paper parser backed by the MinerU cloud API.

MinerU (https://mineru.net) returns LLM-ready Markdown plus extracted
figures for academic PDFs. Use it when ``settings.mineru_api_key`` is
set; otherwise the pipeline falls back to the local PyMuPDF parser.

Flow:
1. POST /file-urls/batch  → presigned OSS URL + batch_id
2. PUT the PDF bytes to the OSS URL (no extra headers — signature is
   computed without Content-Type)
3. GET /extract-results/batch/{batch_id} until state == "done"
4. Download the result ZIP, extract Markdown + figures into output_dir
"""

from __future__ import annotations

import asyncio
import io
import logging
import re
import zipfile
from pathlib import Path

import httpx
from PIL import Image

from backend.config import settings

from .base import PaperParser
from .paper_model import PaperFigure, PaperSection, ParsedPaper

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://mineru.net/api/v4"
POLL_INTERVAL_SECONDS = 5
POLL_TIMEOUT_SECONDS = 600
UPLOAD_TIMEOUT_SECONDS = 180
DOWNLOAD_TIMEOUT_SECONDS = 180


class MinerUError(RuntimeError):
    """Raised when the MinerU API rejects a request or times out."""


class MinerUParser(PaperParser):
    """Parse academic PDFs via the MinerU extraction API."""

    last_parse_info: dict[str, object] = {}

    async def parse(self, file_path: Path, output_dir: Path) -> ParsedPaper:
        api_key = (settings.mineru_api_key or "").strip()
        if not api_key:
            raise MinerUError("MINERU_API_KEY is not configured")

        base_url = (settings.mineru_api_url or DEFAULT_BASE_URL).rstrip("/")
        output_dir.mkdir(parents=True, exist_ok=True)
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)

        headers = {"Authorization": f"Bearer {api_key}"}

        async with httpx.AsyncClient(timeout=UPLOAD_TIMEOUT_SECONDS) as client:
            # 1. request signed upload URL
            req = await client.post(
                f"{base_url}/file-urls/batch",
                headers={**headers, "Content-Type": "application/json"},
                json={
                    "enable_formula": True,
                    "enable_table": True,
                    "language": "en",
                    "model_version": "vlm",
                    "files": [{"name": file_path.name, "is_ocr": False, "data_id": "ppt-agent"}],
                },
            )
            req.raise_for_status()
            payload = req.json()
            if payload.get("code") not in (0, "0", None):
                raise MinerUError(f"file-urls/batch failed: {payload}")
            data = payload["data"]
            batch_id = data["batch_id"]
            upload_url = data["file_urls"][0]
            logger.info("MinerU batch_id=%s", batch_id)

            # 2. PUT file to OSS (signature is calculated without Content-Type)
            pdf_bytes = await asyncio.to_thread(file_path.read_bytes)
            put = await client.put(upload_url, content=pdf_bytes)
            if put.status_code >= 300:
                raise MinerUError(
                    f"upload to OSS failed ({put.status_code}): {put.text[:300]}"
                )

            # 3. poll until done
            zip_url = await self._poll_until_done(client, base_url, batch_id, headers)

            # 4. download result ZIP
            client.timeout = httpx.Timeout(DOWNLOAD_TIMEOUT_SECONDS)
            zr = await client.get(zip_url)
            zr.raise_for_status()
            zip_bytes = zr.content

        # Unpack synchronously (cheap)
        title, abstract, sections, figures = await asyncio.to_thread(
            self._unpack_zip, zip_bytes, images_dir
        )

        info = {
            "path": "mineru",
            "fallback": False,
            "batch_id": batch_id,
            "markdown_chars": sum(len(s.content) for s in sections),
            "figure_count": len(figures),
        }
        MinerUParser.last_parse_info = info
        logger.info("MinerU parsed: %s chars, %s figures", info["markdown_chars"], info["figure_count"])

        # Attach figures to the (single) document section so downstream
        # stages can find them. We don't have per-section figure mapping
        # from MinerU; the strategist agent works fine with this shape
        # because it scans manuscript text + figure inventory together.
        if sections and figures:
            sections[0].figures.extend(figures)

        return ParsedPaper(
            title=title,
            authors=[],
            abstract=abstract,
            sections=sections,
            source_type="pdf",
            figures_dir=images_dir,
        )

    async def _poll_until_done(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        batch_id: str,
        headers: dict[str, str],
    ) -> str:
        elapsed = 0.0
        while elapsed < POLL_TIMEOUT_SECONDS:
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            elapsed += POLL_INTERVAL_SECONDS
            r = await client.get(
                f"{base_url}/extract-results/batch/{batch_id}",
                headers=headers,
            )
            r.raise_for_status()
            payload = r.json()
            results = payload.get("data", {}).get("extract_result") or []
            if not results:
                continue
            item = results[0]
            state = item.get("state")
            logger.debug("MinerU poll [%.0fs]: state=%s", elapsed, state)
            if state == "done":
                url = item.get("full_zip_url")
                if not url:
                    raise MinerUError(f"done state has no full_zip_url: {item}")
                return url
            if state == "failed":
                raise MinerUError(f"extraction failed: {item.get('err_msg') or item}")
        raise MinerUError(f"extraction timed out after {POLL_TIMEOUT_SECONDS}s")

    # ── unpacking ────────────────────────────────────────────────────────────

    @staticmethod
    def _unpack_zip(
        zip_bytes: bytes,
        images_dir: Path,
    ) -> tuple[str, str, list[PaperSection], list[PaperFigure]]:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))

        md_name = next((n for n in zf.namelist() if n.endswith("full.md") or n.endswith(".md")), None)
        if not md_name:
            raise MinerUError("result ZIP has no markdown file")
        markdown = zf.read(md_name).decode("utf-8", errors="replace")

        # Extract images and read their pixel dimensions so downstream
        # layout/sizing logic (which expects ints, not None) keeps working.
        figures: list[PaperFigure] = []
        for name in zf.namelist():
            if not name.startswith("images/"):
                continue
            data = zf.read(name)
            if not data:
                continue
            out_path = images_dir / Path(name).name
            out_path.write_bytes(data)
            try:
                with Image.open(out_path) as im:
                    width, height = im.size
            except Exception:
                width, height = 0, 0
            figures.append(
                PaperFigure(
                    path=out_path,
                    extraction_method="mineru",
                    quality_score=0.9,
                    natural_width=width,
                    natural_height=height,
                )
            )

        # Pull title (first H1) and abstract (text under "Abstract" heading)
        title = "Untitled"
        m = re.search(r"^#\s+(.+)$", markdown, flags=re.MULTILINE)
        if m:
            title = m.group(1).strip()

        abstract = ""
        am = re.search(
            r"^#+\s*Abstract\s*\n+(.*?)(?=\n#+\s+|\Z)",
            markdown,
            flags=re.MULTILINE | re.IGNORECASE | re.DOTALL,
        )
        if am:
            abstract = am.group(1).strip()

        # Single-section shape matches the pymupdf4llm fallback path in
        # PDFParser; downstream agents handle it fine.
        sections = [PaperSection(title="Document", level=1, content=markdown)]
        return title, abstract, sections, figures
