#!/usr/bin/env node

import { readFileSync, writeFileSync } from 'fs';
import juice from 'juice';

const src = process.argv[2];
if (!src) {
  console.error('Usage: node inline.js <html_path>');
  console.error('Converts <style> blocks to inline style="" attributes in place.');
  process.exit(1);
}

try {
  const html = readFileSync(src, 'utf8');
  const inlined = juice(html);
  writeFileSync(src, inlined, 'utf8');
  process.exit(0);
} catch (err) {
  console.error(`inline.js: error processing ${src}`);
  console.error(err.message);
  process.exit(1);
}
