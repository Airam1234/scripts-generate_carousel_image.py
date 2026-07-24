#!/usr/bin/env node
/**
 * Build the accessible Word version of an issue.
 *
 *   export NODE_PATH=$(npm root -g)
 *   node scripts/build_docx.js work/content.js output/InTheLoop_July2026_Accessible.docx
 *
 * The content module describes the issue declaratively; see templates/content.js.
 * Everything that makes the file accessible — real heading styles, alt text on
 * every image, live hyperlinks, a document language — is handled here so the
 * content file does not have to think about it.
 */
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  ImageRun, ExternalHyperlink, LevelFormat, convertInchesToTwip, BorderStyle,
} = require('docx');

const NAVY = '232B50', WIZARD = '0073D9', GREEN = '2E8C57', ORANGE = 'F57D21';
const INK = '2F3542', MUTED = '5B6472';
const FONT = 'Arial';                       // brand system font for Word
const COLOURS = { navy: NAVY, blue: WIZARD, green: GREEN, orange: ORANGE };

const [, , contentPath, outPath] = process.argv;
if (!contentPath || !outPath) {
  console.error('usage: build_docx.js <content.js> <output.docx>');
  process.exit(1);
}
const content = require(path.resolve(contentPath));
const ASSETS = content.assetsDir || path.join(__dirname, '..', 'assets');

/* ---------- building blocks ---------- */
const P = (text, o = {}) => new Paragraph({
  spacing: { after: o.after ?? 90, before: o.before ?? 0, line: 264 },
  alignment: o.align,
  border: o.border,
  children: [new TextRun({
    text, bold: o.bold, italics: o.italics,
    color: o.color ?? INK, size: o.size ?? 21, font: FONT,
  })],
});

const T = (text, o = {}) => new TextRun({
  text, bold: o.bold, italics: o.italics,
  color: o.color ?? INK, size: o.size ?? 21, font: FONT,
});

const LINK = (text, href) => new ExternalHyperlink({
  link: href,
  children: [new TextRun({ text, style: 'Hyperlink', size: 21, font: FONT })],
});

const RUNS = (children, o = {}) => new Paragraph({
  spacing: { after: o.after ?? 90, before: o.before ?? 0, line: 264 },
  alignment: o.align,
  children,
});

const H1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 220, after: 100 },
  children: [new TextRun({ text, bold: true, color: NAVY, size: 28, font: FONT })],
});

const H2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 150, after: 70 },
  children: [new TextRun({ text, bold: true, color: NAVY, size: 23, font: FONT })],
});

const BULLET = (text, ref) => new Paragraph({
  numbering: { reference: ref, level: 0 },
  spacing: { after: 40, line: 264 },
  children: [new TextRun({ text, size: 21, font: FONT, color: INK })],
});

// coloured left bar, standing in for the PDF's tinted panels
const CALLOUT = (lines, colour) => lines.map((line, i) => new Paragraph({
  spacing: { after: i === lines.length - 1 ? 140 : 50, before: i === 0 ? 50 : 0, line: 264 },
  indent: { left: 220 },
  border: { left: { style: BorderStyle.SINGLE, size: 18, color: colour, space: 8 } },
  children: [new TextRun({ text: line, size: 21, font: FONT, color: INK })],
}));

const IMG = (file, w, h, name, desc) => new Paragraph({
  spacing: { before: 60, after: 40 },
  alignment: AlignmentType.CENTER,
  children: [new ImageRun({
    type: 'png',
    data: fs.readFileSync(path.join(ASSETS, file)),
    transformation: { width: w, height: h },
    altText: { title: name, description: desc, name },
  })],
});

const CAPTION = (text) => P(text, {
  size: 18, color: MUTED, italics: true, align: AlignmentType.CENTER, after: 140,
});

/* ---------- numbering: one reference per list, or lists continue each other ---------- */
const listRefs = [];
(content.sections || []).forEach((s, si) =>
  (s.blocks || []).forEach((b, bi) => {
    if (b.type === 'bullets') { b._ref = `list_${si}_${bi}`; listRefs.push(b._ref); }
  }));

const numbering = {
  config: listRefs.map((reference) => ({
    reference,
    levels: [{
      level: 0,
      format: LevelFormat.BULLET,
      text: '\u2022',
      alignment: AlignmentType.LEFT,
      style: {
        paragraph: { indent: { left: convertInchesToTwip(0.3), hanging: convertInchesToTwip(0.18) } },
        run: { color: GREEN, font: FONT },
      },
    }],
  })),
};

/* ---------- assemble ---------- */
const body = [];

if (content.logo !== false) {
  body.push(IMG('logo_colour.png', 165, 36, 'CoreEd logo',
    'The CoreEd logo: the word CoreEd in dark blue, with a circular device in orange, blue and green forming the letter O.'));
}
body.push(new Paragraph({
  heading: HeadingLevel.TITLE,
  spacing: { before: 120, after: 60 },
  alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: content.title, bold: true, color: NAVY, size: 44, font: FONT })],
}));
if (content.issue) {
  body.push(P(content.issue, { align: AlignmentType.CENTER, bold: true, color: GREEN, size: 22, after: 60 }));
}
if (content.strapline) {
  body.push(P(content.strapline, { align: AlignmentType.CENTER, color: MUTED, after: 100 }));
}
body.push(P('Accessible version. Same content as the designed PDF, with written descriptions of the illustrations.',
  { align: AlignmentType.CENTER, italics: true, color: MUTED, size: 18, after: 200 }));

for (const section of content.sections || []) {
  if (section.heading) body.push(H1(section.heading));
  for (const b of section.blocks || []) {
    switch (b.type) {
      case 'h2':
        body.push(H2(b.text)); break;
      case 'p':
        body.push(P(b.text, { bold: b.bold })); break;
      case 'bullets':
        b.items.forEach((t) => body.push(BULLET(t, b._ref))); break;
      case 'callout':
        CALLOUT(Array.isArray(b.text) ? b.text : [b.text],
                COLOURS[b.colour] || NAVY).forEach((p) => body.push(p)); break;
      case 'link':
        body.push(RUNS([
          T(b.before || ''), LINK(b.text, b.href), T(b.after || ''),
        ])); break;
      case 'contact':
        body.push(H2(`${b.name}, ${b.role}`));
        body.push(RUNS([
          T(`Telephone: ${b.phone}   Email: `), LINK(b.email, `mailto:${b.email}`),
        ])); break;
      case 'image':
        body.push(IMG(b.file, b.width, b.height, b.name, b.description));
        if (b.caption) body.push(CAPTION(b.caption));
        break;
      default:
        console.warn(`unknown block type: ${b.type}`);
    }
  }
}

if (content.signoff) {
  body.push(new Paragraph({
    spacing: { before: 120, after: 80 },
    border: { top: { style: BorderStyle.SINGLE, size: 6, color: 'DFE3EA', space: 10 } },
    children: [new TextRun({ text: content.signoff.who, bold: true, color: NAVY, size: 23, font: FONT })],
  }));
  body.push(P(content.signoff.text, { color: MUTED }));
}

const doc = new Document({
  title: content.title,
  description: content.description || content.title,
  creator: 'CoreEd',
  numbering,
  styles: {
    default: {
      document: { run: { font: FONT, size: 21, color: INK, language: { value: 'en-GB' } } },
    },
    characterStyles: [{
      id: 'Hyperlink',
      name: 'Hyperlink',
      basedOn: 'DefaultParagraphFont',
      quickFormat: true,
      run: { color: WIZARD, underline: {} },
    }],
  },
  sections: [{
    properties: { page: { margin: { top: 850, bottom: 850, left: 1000, right: 1000 } } },
    children: body,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, buf);
  console.log(`Written ${outPath}`);
});
