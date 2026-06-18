#!/usr/bin/env python3
"""
publish.py — 微信公众号发布脚本。

从 wechat-format 产出的 HTML 中提取配图（含压缩）、上传至微信图床、
替换 URL、创建图文草稿（draft/add），最后清理产物文件。

Usage:
  python scripts/publish.py <html_path>
  python scripts/publish.py <html_path> --dry-run

依赖（可选）:
  Pillow:         图片自动压缩 (pip install Pillow)
  python-dotenv:  .env 自动加载 (pip install python-dotenv)
"""

import argparse
import asyncio
import io
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import httpx


# ── 可选依赖 ──────────────────────────────────────────────────

try:
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

try:
    from dotenv import load_dotenv

    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False


# ── 常量 ──────────────────────────────────────────────────────

TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
UPLOADIMG_URL = "https://api.weixin.qq.com/cgi-bin/media/uploadimg"
ADD_MATERIAL_URL = "https://api.weixin.qq.com/cgi-bin/material/add_material"
BATCHGET_MATERIAL_URL = "https://api.weixin.qq.com/cgi-bin/material/batchget_material"
DRAFT_ADD_URL = "https://api.weixin.qq.com/cgi-bin/draft/add"

MAX_IMAGE_BYTES = 1 * 1024 * 1024  # 1 MB


# ── 类型 ──────────────────────────────────────────────────────


@dataclass
class ImageEntry:
    local_path: str
    slug: str
    remote_url: str = ""


# ── 异常 ──────────────────────────────────────────────────────


class PublishError(Exception):
    """publish.py 可恢复错误。"""


# ── .env 加载 ─────────────────────────────────────────────────


def _load_env_simple(path: Path) -> dict:
    if not path.exists():
        return {}
    env = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        env[key.strip()] = val.strip().strip("\"'")
    return env


def _get_env() -> dict:
    env_path = Path(__file__).parent / ".env"
    if HAS_DOTENV:
        load_dotenv(env_path)
        return os.environ
    return _load_env_simple(env_path)


# ── HTML 标记提取 ─────────────────────────────────────────────


_MARKER_RE = re.compile(r"<!--wechat-(\w+):(.*?)-->")


def _extract_markers(html: str) -> dict:
    """提取 <!--wechat-xxx:value--> 标记。"""
    markers = {}
    for m in _MARKER_RE.finditer(html):
        key, val = m.group(1), m.group(2).strip()
        markers[key] = val
    return markers


def _remove_markers(html: str) -> str:
    """移除所有 <!--wechat-xxx:...--> 标记行。"""
    return _MARKER_RE.sub("", html)


def _extract_body(html: str) -> str:
    """从完整 HTML 中提取 <div id=\"output\"> 内的内容。"""
    m = re.search(
        r'<div\s+id="output"[^>]*>(.*?)</section>\s*</div>\s*</body>',
        html,
        re.DOTALL,
    )
    return m.group(1).strip() if m else html


# ── 自动压缩 ──────────────────────────────────────────────────


def _scan_images(html: str) -> List[ImageEntry]:
    """从 HTML <img> 标签中提取本地图片路径。"""
    entries = []
    seen = set()
    for m in re.finditer(r'<img[^>]+src="([^"]+)"', html):
        src = m.group(1)
        if not src.startswith(("file://", "/")):
            continue
        path = src.replace("file://", "")
        p = Path(path)
        if not p.exists():
            print(f"  ⚠  图片文件不存在，跳过: {path}")
            continue
        resolved = p.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        entries.append(ImageEntry(local_path=str(resolved), slug=p.stem))
    return entries


# ── 图片压缩 ──────────────────────────────────────────────────


def _compress(image_path: str) -> bytes:
    """压缩图片至 ≤1MB，返回字节数据。"""
    if not HAS_PILLOW:
        size = Path(image_path).stat().st_size
        if size > MAX_IMAGE_BYTES:
            raise PublishError(
                f"{image_path} ({size / 1024 / 1024:.1f}MB) 超过 1MB 限制。\n"
                f"  请手动压缩后重试，或安装 Pillow 启用自动压缩: pip install Pillow"
            )
        return Path(image_path).read_bytes()

    img = Image.open(image_path)
    fmt = img.format or "PNG"

    buf = io.BytesIO()
    img.save(buf, format=fmt)
    if buf.tell() <= MAX_IMAGE_BYTES:
        return buf.getvalue()

    w, h = img.size
    if max(w, h) > 1024:
        ratio = 1024 / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    for quality in [85, 70, 55, 40]:
        buf = io.BytesIO()
        if fmt == "PNG":
            rgb = img.convert("RGB")
            rgb.save(buf, format="JPEG", quality=quality, optimize=True)
        else:
            img.save(buf, format=fmt, quality=quality, optimize=True)
        if buf.tell() <= MAX_IMAGE_BYTES:
            return buf.getvalue()

    raise PublishError(
        f"无法将 {image_path} 压缩至 1MB 以下。请手动缩小尺寸或降低画质。"
    )


# ── WeChat API ────────────────────────────────────────────────


async def _get_access_token(app_id: str, app_secret: str, proxy: Optional[str]) -> str:
    async with httpx.AsyncClient(proxy=proxy, timeout=15.0) as c:
        r = await c.get(
            TOKEN_URL,
            params=dict(grant_type="client_credential", appid=app_id, secret=app_secret),
        )
    body = r.json()
    if body.get("errcode"):
        raise PublishError(f"获取 access_token 失败: {body}")
    return body["access_token"]


async def _upload_image(
    token: str, image_data: bytes, filename: str, proxy: Optional[str]
) -> str:
    """上传图片到图文消息图库 (/cgi-bin/media/uploadimg)，返回 URL。"""
    async with httpx.AsyncClient(proxy=proxy, timeout=30.0) as c:
        r = await c.post(
            f"{UPLOADIMG_URL}?access_token={token}",
            files={"media": (filename, image_data, "image/png")},
        )
    body = r.json()
    if body.get("errcode"):
        raise PublishError(f"上传图片失败 ({filename}): {body}")
    return body["url"]


async def _upload_cover(
    token: str, image_path: str, proxy: Optional[str]
) -> str:
    """上传封面图到永久素材库 (/cgi-bin/material/add_material)，返回 media_id。"""
    image_data = _compress(image_path)
    filename = Path(image_path).name
    async with httpx.AsyncClient(proxy=proxy, timeout=30.0) as c:
        r = await c.post(
            f"{ADD_MATERIAL_URL}?access_token={token}&type=image",
            files={"media": (filename, image_data, "image/png")},
        )
    body = r.json()
    if body.get("errcode"):
        raise PublishError(f"上传封面失败 ({filename}): {body}")
    return body["media_id"]


async def _get_first_cover_media_id(token: str, proxy: Optional[str]) -> str:
    """从素材库获取第一张图片作为封面，返回 media_id。"""
    async with httpx.AsyncClient(proxy=proxy, timeout=15.0) as c:
        r = await c.post(
            f"{BATCHGET_MATERIAL_URL}?access_token={token}",
            json={"type": "image", "offset": 0, "count": 1},
        )
    body = r.json()
    items = body.get("item") or []
    if not items:
        raise PublishError(
            "素材库中无图片可用作为封面。\n"
            "  请上传一张图片到微信公众号素材管理后重试。"
        )
    return items[0]["media_id"]


async def _create_draft(
    token: str,
    title: str,
    author: str,
    digest: str,
    content: str,
    thumb_media_id: str,
    proxy: Optional[str],
) -> str:
    """创建图文草稿，返回 media_id。"""
    article = {
        "title": title,
        "author": author,
        "digest": digest,
        "content": content,
        "content_source_url": "",
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }
    if thumb_media_id:
        article["thumb_media_id"] = thumb_media_id

    async with httpx.AsyncClient(proxy=proxy, timeout=30.0) as c:
        r = await c.post(
            f"{DRAFT_ADD_URL}?access_token={token}",
            json={"articles": [article]},
        )
    body = r.json()
    if body.get("errcode"):
        raise PublishError(f"创建草稿失败: {body}")
    return body["media_id"]


# ── 主流程 ────────────────────────────────────────────────────


async def _run(html_path: Path, dry_run: bool) -> None:
    env = _get_env()
    app_id = env.get("WECHAT_APP_ID") or env.get("APP_ID")
    app_secret = env.get("WECHAT_APP_SECRET") or env.get("APP_SECRET")
    author = env.get("WECHAT_AUTHOR") or ""
    proxy = env.get("WECHAT_PROXY") or os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or None
    if proxy and urlparse(proxy).scheme == "socks5":
        try:
            import socksio  # noqa: F401
        except ImportError:
            raise PublishError(
                "SOCKS5 代理需要安装 socksio 库:\n"
                "  pip install httpx[socks]\n"
                "  或切换为 HTTP 代理 http://..."
            )
    if not app_id or not app_secret:
        raise PublishError("请在 scripts/.env 中设置 WECHAT_APP_ID 和 WECHAT_APP_SECRET")

    # ── 读取 HTML ──────────────────────────────────────────────
    html = html_path.read_text(encoding="utf-8")

    # ── 提取标记 ───────────────────────────────────────────────
    markers = _extract_markers(html)
    title = markers.get("title", "").strip()
    digest = markers.get("digest", "").strip()
    cover_path = markers.get("cover", "").strip()

    if not title:
        raise PublishError("HTML 中未找到 <!--wechat-title:...--> 标记")

    html = _remove_markers(html)

    print(f"  标题: {title}")
    if digest:
        print(f"  摘要: {digest[:60]}…" if len(digest) > 60 else f"  摘要: {digest}")
    print(f"  作者: {author or '(未设置，请在 .env 中配置 WECHAT_AUTHOR)'}")

    # ── 扫描配图 ───────────────────────────────────────────────
    images = _scan_images(html)

    if not images and not cover_path:
        print("  未发现本地配图路径。")

    if images:
        print(f"\n  发现 {len(images)} 张配图:")
        for img in images:
            size = Path(img.local_path).stat().st_size
            size_str = (
                f"{size / 1024:.0f} KB"
                if size < 1024 * 1024
                else f"{size / 1024 / 1024:.1f} MB"
            )
            print(f"    {img.slug:30s} {size_str:>8s}")

    if dry_run:
        if cover_path:
            print(f"\n  封面: {cover_path}")
        print("\n  --dry-run 模式，未执行上传或创建草稿。")
        return

    # ── 获取 access_token ──────────────────────────────────────
    print("\n  获取 access_token ...")
    token = await _get_access_token(app_id, app_secret, proxy=proxy)
    print("  ✓ access_token 获取成功")

    # ── 上传配图 ───────────────────────────────────────────────
    for i, img in enumerate(images, 1):
        print(f"  [{i}/{len(images)}] {img.slug} ...", end="", flush=True)
        try:
            data = _compress(img.local_path)
            url = await _upload_image(
                token, data, Path(img.local_path).name, proxy=proxy
            )
            img.remote_url = url
            print(" ✓")
        except PublishError as e:
            print(f" ✗ {e}")

    successful = [img for img in images if img.remote_url]
    failed = [img for img in images if not img.remote_url]

    # ── 替换 HTML 中的本地路径 ─────────────────────────────────
    for img in successful:
        for src in (f"file://{img.local_path}", img.local_path):
            html = html.replace(f'src="{src}"', f'src="{img.remote_url}"')

    # ── 提取正文 ───────────────────────────────────────────────
    body_content = _extract_body(html)

    # ── 封面图 ─────────────────────────────────────────────────
    thumb_media_id = ""
    if cover_path:
        print(f"\n  上传封面图 ...", end="", flush=True)
        try:
            thumb_media_id = await _upload_cover(token, cover_path, proxy=proxy)
            print(" ✓")
        except PublishError as e:
            print(f" ✗ {e}")
            print("  尝试从素材库获取封面 ...", end="", flush=True)
            try:
                thumb_media_id = await _get_first_cover_media_id(token, proxy=proxy)
                print(" ✓")
            except PublishError as e2:
                print(f" ✗ {e2}")
    else:
        print("\n  未指定封面图，从素材库获取 ...", end="", flush=True)
        try:
            thumb_media_id = await _get_first_cover_media_id(token, proxy=proxy)
            print(" ✓")
        except PublishError as e:
            print(f" ✗ {e}")

    # ── 创建草稿 ───────────────────────────────────────────────
    print("\n  创建微信图文草稿 ...", end="", flush=True)
    try:
        media_id = await _create_draft(
            token=token,
            title=title,
            author=author,
            digest=digest,
            content=body_content,
            thumb_media_id=thumb_media_id,
            proxy=proxy,
        )
        print(" ✓")
        print(f"\n  🎉 草稿创建成功")
        print(f"     media_id: {media_id}")
    except PublishError as e:
        print(f" ✗\n\n错误: {e}")
        raise
    finally:
        # 无论草稿创建成功或失败，都删除产物文件
        if html_path.exists():
            html_path.unlink()
            print(f"  🗑  已删除: {html_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="上传配图 → 创建微信公众号图文草稿",
    )
    parser.add_argument("html_path", help="wechat-format 产出的 HTML 文件路径")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅列出图片和文章信息，不上传也不创建草稿",
    )
    args = parser.parse_args()

    html_path = Path(args.html_path)
    if not html_path.exists():
        print(f"错误: 文件不存在: {html_path}")
        sys.exit(1)

    try:
        asyncio.run(_run(html_path, dry_run=args.dry_run))
    except PublishError as e:
        print(f"\n错误: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n中断")
        sys.exit(0)


if __name__ == "__main__":
    main()
