const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, AlignmentType, LevelFormat,
  ExternalHyperlink, ImageRun, PageBreak
} = require("docx");

const mdPath = process.argv[2];
const outPath = process.argv[3];
const baseDir = path.dirname(path.resolve(mdPath));
let md = fs.readFileSync(mdPath, "utf8");

// --- Tiền xử lý: bỏ chú thích HTML, đổi <br> thành dòng trống ---
md = md.replace(/<!--[\s\S]*?-->/g, "");
md = md.replace(/^\s*<br\s*\/?>\s*$/gim, "\u0000BLANK\u0000");
md = md.replace(/<br\s*\/?>/gi, "\n");

const lines = md.split("\n");
const warnings = [];

function parseInline(text, baseOpts = {}) {
  const runs = [];
  let i = 0, buf = "";
  const flush = (opts = {}) => {
    if (buf.length) { runs.push(new TextRun({ text: buf, ...baseOpts, ...opts })); buf = ""; }
  };
  while (i < text.length) {
    // Ảnh ![alt](path)
    let m = /^!\[([^\]]*)\]\(([^)]+)\)/.exec(text.slice(i));
    if (m) {
      flush();
      const img = path.resolve(baseDir, m[2]);
      const ext = path.extname(img).slice(1).toLowerCase();
      if (fs.existsSync(img) && ["png","jpg","jpeg","gif","bmp"].includes(ext)) {
        try {
          runs.push(new ImageRun({
            type: ext === "jpeg" ? "jpg" : ext,
            data: fs.readFileSync(img),
            transformation: { width: 500, height: 320 },
            altText: { title: m[1] || "Hình", description: m[1] || "Hình", name: m[1] || "Hình" }
          }));
        } catch (e) { warnings.push(`Không nhúng được ảnh: ${m[2]}`); buf += m[1]; }
      } else { warnings.push(`Không tìm thấy ảnh: ${m[2]}`); buf += `[Hình: ${m[1] || m[2]}]`; }
      i += m[0].length; continue;
    }
    // Liên kết [text](url)
    m = /^\[([^\]]+)\]\(([^)]+)\)/.exec(text.slice(i));
    if (m) {
      flush();
      runs.push(new ExternalHyperlink({
        link: m[2],
        children: [new TextRun({ text: m[1], ...baseOpts, style: "Hyperlink" })]
      }));
      i += m[0].length; continue;
    }
    if (text.startsWith("**", i)) {
      flush();
      const end = text.indexOf("**", i + 2);
      if (end === -1) { buf += text.slice(i); break; }
      runs.push(...parseInline(text.slice(i + 2, end), { ...baseOpts, bold: true }));
      i = end + 2; continue;
    }
    if (text[i] === "`") {
      flush();
      const end = text.indexOf("`", i + 1);
      if (end === -1) { buf += text.slice(i); break; }
      runs.push(new TextRun({ text: text.slice(i + 1, end), ...baseOpts, font: "Consolas", size: 20, color: "A6271D" }));
      i = end + 1; continue;
    }
    if (text[i] === "*") {
      flush();
      const end = text.indexOf("*", i + 1);
      if (end === -1) { buf += text.slice(i); break; }
      runs.push(new TextRun({ text: text.slice(i + 1, end), ...baseOpts, italics: true }));
      i = end + 1; continue;
    }
    buf += text[i]; i++;
  }
  flush();
  if (!runs.length) runs.push(new TextRun({ text: "", ...baseOpts }));
  return runs;
}

const children = [];
const numbering = { config: [
  { reference: "bullets", levels: [
    { level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 540, hanging: 270 } } } },
    { level: 1, format: LevelFormat.BULLET, text: "\u25E6", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 1080, hanging: 270 } } } }] },
  { reference: "numbers", levels: [
    { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 540, hanging: 270 } } } },
    { level: 1, format: LevelFormat.LOWER_LETTER, text: "%2.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 1080, hanging: 270 } } } }] },
]};

const border = { style: BorderStyle.SINGLE, size: 2, color: "AAAAAA" };
const borders = { top: border, bottom: border, left: border, right: border };
const CONTENT_W = 9026;

const isRow = l => /^\s*\|.*\|\s*$/.test(l);
const isSep = l => /^\s*\|?[\s:\-|]+\|?\s*$/.test(l) && l.includes("-");
const cells = l => l.split("|").map(s => s.trim())
  .filter((s, i, a) => !(i === 0 && s === "") && !(i === a.length - 1 && s === ""));

let i = 0, inCode = false, codeBuf = [];
while (i < lines.length) {
  const line = lines[i];

  if (line.trim() === "\u0000BLANK\u0000") {
    children.push(new Paragraph({ text: "", spacing: { after: 240 } })); i++; continue;
  }
  if (line.trim().startsWith("```")) {
    if (!inCode) { inCode = true; codeBuf = []; i++; continue; }
    inCode = false;
    children.push(new Paragraph({
      shading: { fill: "F4F4F4", type: ShadingType.CLEAR }, spacing: { before: 100, after: 200 },
      children: codeBuf.flatMap((l, k) => [
        ...(k ? [new TextRun({ break: 1 })] : []),
        new TextRun({ text: l, font: "Consolas", size: 18 })])
    }));
    i++; continue;
  }
  if (inCode) { codeBuf.push(line); i++; continue; }
  if (!line.trim()) { i++; continue; }

  if (/^---+$/.test(line.trim())) {
    children.push(new Paragraph({
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E75B6", space: 1 } },
      spacing: { after: 240 } }));
    i++; continue;
  }

  if (isRow(line) && i + 1 < lines.length && isSep(lines[i + 1])) {
    const head = cells(line), n = head.length, w = Math.floor(CONTENT_W / n);
    const rows = [new TableRow({ tableHeader: true, children: head.map(c => new TableCell({
      borders, width: { size: w, type: WidthType.DXA },
      shading: { fill: "D9E8F5", type: ShadingType.CLEAR },
      margins: { top: 60, bottom: 60, left: 100, right: 100 },
      children: [new Paragraph({ spacing: { after: 0 }, children: parseInline(c, { bold: true, size: 20 }) })]
    })) })];
    i += 2;
    while (i < lines.length && isRow(lines[i])) {
      const cs = cells(lines[i]); while (cs.length < n) cs.push("");
      rows.push(new TableRow({ children: cs.slice(0, n).map(c => new TableCell({
        borders, width: { size: w, type: WidthType.DXA },
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: [new Paragraph({ spacing: { after: 0 }, children: parseInline(c, { size: 20 }) })]
      })) }));
      i++;
    }
    children.push(new Table({ width: { size: CONTENT_W, type: WidthType.DXA },
      columnWidths: new Array(n).fill(w), rows }));
    children.push(new Paragraph({ text: "", spacing: { after: 160 } }));
    continue;
  }

  let m;
  if ((m = line.match(/^>\s?(.*)$/))) {
    const content = [m[1]]; i++;
    while (i < lines.length && /^>\s?/.test(lines[i])) { content.push(lines[i].replace(/^>\s?/, "")); i++; }
    children.push(new Paragraph({
      shading: { fill: "FFF8E1", type: ShadingType.CLEAR },
      border: { left: { style: BorderStyle.SINGLE, size: 12, color: "F0A500", space: 6 } },
      indent: { left: 180 }, spacing: { before: 120, after: 180 },
      children: content.filter(Boolean).flatMap((l, k) => [
        ...(k ? [new TextRun({ break: 1 })] : []), ...parseInline(l, { size: 21 })])
    }));
    continue;
  }

  if ((m = line.match(/^(#{1,4})\s+(.+)/))) {
    const lv = m[1].length;
    const H = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3, HeadingLevel.HEADING_4][lv-1];
    children.push(new Paragraph({ heading: H,
      pageBreakBefore: lv === 1 && children.length > 0,
      children: parseInline(m[2]) }));
    i++; continue;
  }

  if ((m = line.match(/^(\s*)[-*]\s+(.+)/))) {
    children.push(new Paragraph({ numbering: { reference: "bullets", level: m[1].length >= 2 ? 1 : 0 },
      spacing: { after: 60 }, children: parseInline(m[2]) }));
    i++; continue;
  }
  if ((m = line.match(/^(\s*)\d+\.\s+(.+)/))) {
    children.push(new Paragraph({ numbering: { reference: "numbers", level: m[1].length >= 2 ? 1 : 0 },
      spacing: { after: 60 }, children: parseInline(m[2]) }));
    i++; continue;
  }

  // Cảnh báo nếu còn thẻ HTML sót lại
  if (/<[a-z/][^>]*>/i.test(line)) warnings.push(`Thẻ HTML chưa xử lý, dòng ${i+1}: ${line.trim().slice(0,50)}`);

  children.push(new Paragraph({ spacing: { after: 140 }, children: parseInline(line.trim()) }));
  i++;
}

const F = "Times New Roman";
const doc = new Document({
  numbering,
  styles: {
    default: { document: { run: { font: F, size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: F, color: "1F4E79" },
        paragraph: { spacing: { before: 320, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: F, color: "2E75B6" },
        paragraph: { spacing: { before: 260, after: 140 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 25, bold: true, font: F },
        paragraph: { spacing: { before: 200, after: 110 }, outlineLevel: 2 } },
      { id: "Heading4", name: "Heading 4", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, italics: true, font: F },
        paragraph: { spacing: { before: 160, after: 90 }, outlineLevel: 3 } },
    ]
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 },
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children
  }]
});

Packer.toBuffer(doc).then(b => {
  fs.writeFileSync(outPath, b);
  console.log("OK:", outPath);
  if (warnings.length) {
    console.log("CẢNH BÁO:");
    [...new Set(warnings)].forEach(w => console.log("  -", w));
  }
});
