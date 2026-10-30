"""Typesetting for README SVGs.

GitHub renders README SVGs as <img>, so web fonts never load. Instead every
glyph is shaped with HarfBuzz (real kerning), drawn once as a <path> in <defs>,
and placed with <use>. The SVG carries its own typography and stays small.
"""
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTS = Path(__file__).parent / "fonts"


class Face:
    def __init__(self, key, filename):
        self.key = key
        path = FONTS / filename
        self.tt = TTFont(path)
        self.upem = self.tt["head"].unitsPerEm
        self.glyphset = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        blob = hb.Blob.from_file_path(str(path))
        self.hbfont = hb.Font(hb.Face(blob))
        self.used = {}

    def _glyph_id(self, gid):
        name = self.order[gid]
        ref = f"{self.key}{gid}"
        if ref not in self.used:
            pen = SVGPathPen(self.glyphset)
            # font units are y-up, SVG is y-down
            self.glyphset[name].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))
            self.used[ref] = pen.getCommands()
        return ref

    def shape(self, text, tracking=0.0):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, {"kern": True, "liga": True})
        out, x = [], 0.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            out.append((info.codepoint, x + pos.x_offset, pos.y_offset))
            x += pos.x_advance + tracking * self.upem
        width = x - tracking * self.upem if out else 0
        return out, width

    def width(self, text, size, tracking=0.0):
        return self.shape(text, tracking)[1] * size / self.upem

    def text(self, text, x, y, size, fill=None, cls=None, anchor="start", tracking=0.0, extra=""):
        glyphs, w = self.shape(text, tracking)
        s = size / self.upem
        if anchor == "end":
            x -= w * s
        elif anchor == "middle":
            x -= w * s / 2
        uses = []
        for gid, gx, gy in glyphs:
            if self.order[gid] in ("space", "uni00A0") or not self._has_outline(gid):
                continue
            ref = self._glyph_id(gid)
            uses.append(f'<use href="#{ref}" x="{gx:.0f}" y="{-gy:.0f}"/>')
        attrs = []
        if fill:
            attrs.append(f'fill="{fill}"')
        if cls:
            attrs.append(f'class="{cls}"')
        return (f'<g transform="translate({x:.2f} {y:.2f}) scale({s:.5f})" {" ".join(attrs)} {extra}>'
                + "".join(uses) + "</g>")

    def _has_outline(self, gid):
        pen = SVGPathPen(self.glyphset)
        self.glyphset[self.order[gid]].draw(pen)
        return bool(pen.getCommands())

    def defs(self):
        return "".join(f'<path id="{k}" d="{d}"/>' for k, d in self.used.items())


def faces():
    return {
        "display": Face("d", "ArchivoBlack.ttf"),
        "mono": Face("m", "JetBrainsMono-Medium.ttf"),
        "monob": Face("b", "JetBrainsMono-Bold.ttf"),
    }


THEMES = {
    "light": dict(bg="#E9EDEE", ink="#15150F", stroke="#5B6470", dim="#A7ADB5",
                  faint="#D5DADC", accent="#1E9E96", accentText="#167670", panel="#F3F5F5"),
    "dark": dict(bg="#0E1012", ink="#E9EDEE", stroke="#8A929C", dim="#3B424A",
                 faint="#1C2024", accent="#2DBFB5", accentText="#3FD1C6", panel="#14171A"),
}
