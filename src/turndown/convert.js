/**
 * Turndown converter with pre/post-processing.
 *
 * Pre-processes HTML:
 * - Strips <style>/<script> tags
 * - Converts internal docs.crpt.ru links to #anchor links
 * - Builds heading text -> id map
 *
 * Conversion rules:
 * - Complex tables (cells with multiple block elements) kept as raw HTML
 * - Simple table cells: <p> wrappers stripped so rows stay on one line
 * - GFM plugin for tables/strikethrough
 *
 * Post-processes markdown:
 * - Inserts <a id="..."> anchors before headings
 *
 * Usage: node convert.js <input.htm> <output_dir>
 */
const TurndownService = require('turndown');
const { gfm } = require('turndown-plugin-gfm');
const fs = require('fs');
const path = require('path');

const inputFile = process.argv[2];
const outputDir = process.argv[3];

fs.mkdirSync(outputDir, { recursive: true });

let html = fs.readFileSync(inputFile, 'utf8');

// Strip style/script
html = html.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');
html = html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');

// Internal links
html = html.replace(/https:\/\/docs\.crpt\.ru\/gismt\/True_API\/#/g, '#');

// Build heading text -> id map
const headingIds = {};
const hRe = /<h[1-6]\s+id="([^"]*)"[^>]*>([\s\S]*?)<\/h[1-6]>/gi;
let hm;
while ((hm = hRe.exec(html)) !== null) {
  headingIds[hm[2].replace(/<[^>]*>/g, '').trim()] = hm[1];
}

const td = new TurndownService({ headingStyle: 'atx', codeBlockStyle: 'fenced' });
td.use(gfm);

// Keep complex tables as raw HTML
td.addRule('complexTable', {
  filter: function (node) {
    if (node.nodeName !== 'TABLE') return false;
    var cells = node.querySelectorAll('td, th');
    for (var i = 0; i < cells.length; i++) {
      var blocks = cells[i].querySelectorAll('p, ul, ol, pre');
      if (blocks.length > 1) return true;
    }
    return false;
  },
  replacement: function (content, node) {
    return '\n\n' + node.outerHTML + '\n\n';
  }
});

// Simple tables: strip <p> inside cells
td.addRule('tableCellParagraph', {
  filter: function (node) {
    if (node.nodeName !== 'P' || !node.parentNode) return false;
    if (node.parentNode.nodeName !== 'TD' && node.parentNode.nodeName !== 'TH') return false;
    var table = node.closest('table');
    if (!table) return false;
    var cells = table.querySelectorAll('td, th');
    for (var i = 0; i < cells.length; i++) {
      if (cells[i].querySelectorAll('p, ul, ol, pre').length > 1) return false;
    }
    return true;
  },
  replacement: function (content) {
    return content.trim();
  }
});

let md = td.turndown(html);

// Insert anchor IDs before headings
md = md.replace(/^(#{1,6}) (.+)$/gm, function (match, hashes, text) {
  const clean = text.replace(/\\\*/g, '*').replace(/\\\[/g, '[').replace(/\\\]/g, ']').trim();
  const hid = headingIds[clean] || headingIds[text.trim()];
  if (hid) return '<a id="' + hid + '"></a>\n\n' + hashes + ' ' + text;
  return match;
});

const outputFile = path.join(outputDir, 'README.md');
fs.writeFileSync(outputFile, md, 'utf8');

console.log(`Turndown: ${inputFile} -> ${outputFile}`);
