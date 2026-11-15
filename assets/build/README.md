# 素材构建流程

最终字体是项目根目录的 `bongocat.woff`。所有素材都在 `assets/` 下。

## 目录

- `../src/idle.svg`、`left-down.svg`、`right-down.svg` —— 最终用于预览和生成字体的三帧
- `../src/source/` —— 修正过动作线、但还没加粗的中间版本
- `build/thick/` —— 加了描边的中间版本
- `../original/bongocat.woff` —— 原版 Bongo Cat 字体备份
- `../preview.html` —— 浏览器预览页

## 依赖

- Python + `fonttools`（生成字体）
- Node.js
- 矢量化描边工具（只在改素材时需要）：

```bash
npm install --no-save @resvg/resvg-js svg-outline-stroke
```

## 完整流程

```bash
# 1. 修正 left-down 的动作线位置
python assets/build/prepare_frames.py

# 2. 给线条加粗（改 STROKE_WIDTH 即可调整粗细）
python assets/build/thicken.py

# 3. 描边转填充路径（potrace）
node assets/build/outline.js

# 4. 给两只眼睛挖出空心（环形眼睛）
python assets/build/hollow_eyes.py

# 5. 裁剪成统一 viewBox，保证三帧对齐
python assets/build/crop_frames.py

# 6. 生成字体
python assets/build/build_font.py

# 7. 安装到插件
cp assets/build/bongocat.woff bongocat.woff
```

## 可调参数

- `thicken.py` 的 `STROKE_WIDTH`：线条粗细。当前 15；改大更粗，改小更细。
- `build_font.py` 的 `TARGET_H`：字形在 em 里占的高度，当前 920（1024 em）。
- `build_font.py` 的 `SIDE_PAD` / `BOTTOM_PAD`：字形四周留白。
- `hollow_eyes.py` 的 `EYES`：左右眼的中心与椭圆半径；改大半径眼睛更空，改小则环更粗。
- `prepare_frames.py` 的 `MOUTH_D`：面部嘴巴路径，当前为笑弧 `M538 414 Q563 436 588 414`。`Q` 的控制点越往下（y 越大）笑弧越深，放到端点上方会变成撇嘴；改端点可调长度和位置。
- 码位在 `build_font.py` 的 `FRAMES` 列表里，需与 `bongocat-theme.json` 保持一致。

## 预览

直接用浏览器打开 `assets/preview.html`，可以看到 16px 实际大小、深浅色和动画效果。
