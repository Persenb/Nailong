# 素材构建流程

最终字体是项目根目录的 `nailong.woff`。所有素材都在 `assets/` 下。

## 目录

- `../source/` —— 三张原始手绘 SVG（idle / left-down / right-down）
- `../frames/` —— 最终用于预览和生成字体的三帧
- `build/normalized/` —— 修正动作线、未加粗的中间版本（生成物，已忽略）
- `build/thick/` —— 加描边的中间版本（生成物，已忽略）
- `../preview.html` —— 浏览器预览页

## 依赖

- Python + `fonttools` + `Pillow`
- Node.js + `svg-outline-stroke`

```bash
npm install --no-save svg-outline-stroke
```

## 完整流程

```bash
python assets/build/prepare_frames.py
python assets/build/thicken.py
node assets/build/outline.js
python assets/build/hollow_eyes.py
python assets/build/crop_frames.py
python assets/build/build_font.py
cp assets/build/nailong.woff nailong.woff
python assets/build/make_gif.py
```

## 可调参数

- `thicken.py` 的 `STROKE_WIDTH`：线条粗细。当前 15；改大更粗，改小更细。
- `build_font.py` 的 `TARGET_H`：字形在 em 里占的高度，当前 1200（1024 em，允许少量上下溢出以匹配状态栏高度）。
- `build_font.py` 的 `SIDE_PAD` / `BOTTOM_PAD`：字形四周留白；当前 48 / -152。
- `hollow_eyes.py` 的 `EYES`：左右眼的中心与椭圆半径；改大半径眼睛更空，改小则环更粗。
- `prepare_frames.py` 的 `MOUTH_D`：面部嘴巴路径，当前为笑弧 `M538 414 Q563 436 588 414`。`Q` 的控制点越往下（y 越大）笑弧越深，放到端点上方会变成撇嘴；改端点可调长度和位置。
- 码位在 `build_font.py` 的 `FRAMES` 列表里，需与 `nailong-theme.json` 保持一致。

## 预览

直接用浏览器打开 `assets/preview.html`，可以看到 16px 实际大小、深浅色和动画效果。
