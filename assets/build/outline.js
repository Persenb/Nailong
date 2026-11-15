// Convert the SVG stroke on each frame into filled outlines so the paths
// can become font glyphs. Requires `npm install svg-outline-stroke`.
const fs = require('fs');
const path = require('path');
const outlineStroke = require('svg-outline-stroke');

const root = path.resolve(__dirname, '..', '..');
const inDir = path.join(root, 'assets', 'build', 'thick');
const outDir = path.join(root, 'assets', 'src');

(async () => {
  for (const name of ['idle', 'left-down', 'right-down']) {
    const svg = fs.readFileSync(path.join(inDir, name + '.svg'));
    const out = await outlineStroke(svg);
    fs.writeFileSync(path.join(outDir, name + '.svg'), out);
    console.log('outlined', name, out.length, 'bytes');
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
