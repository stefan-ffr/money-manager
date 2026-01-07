# PWA Icon Generation

## Benötigte Icons

Für die vollständige PWA-Funktionalität werden folgende Icons benötigt:

- `icon-192.png` (192x192px)
- `icon-512.png` (512x512px)

## Icon Generation mit ImageMagick

```bash
# 1. Erstelle ein Basis-Icon (kann auch mit Figma/Inkscape erstellt werden)
# oder verwende das Money Manager Logo

# 2. Generiere alle erforderlichen Größen
convert icon-source.png -resize 192x192 frontend/public/icon-192.png
convert icon-source.png -resize 512x512 frontend/public/icon-512.png
```

## Einfaches Placeholder Icon erstellen

Wenn du schnell ein Placeholder Icon erstellen möchtest:

```bash
# Mit ImageMagick
convert -size 512x512 xc:#2563eb \
  -gravity center \
  -pointsize 200 \
  -fill white \
  -annotate +0+0 "💰" \
  frontend/public/icon-512.png

convert -size 192x192 xc:#2563eb \
  -gravity center \
  -pointsize 80 \
  -fill white \
  -annotate +0+0 "💰" \
  frontend/public/icon-192.png
```

## Online Tools

Alternativ können Icons auch mit folgenden Online-Tools generiert werden:

- [PWA Asset Generator](https://github.com/onderceylan/pwa-asset-generator)
- [RealFaviconGenerator](https://realfavicongenerator.net/)
- [PWA Builder](https://www.pwabuilder.com/imageGenerator)

## Empfohlenes Design

- **Hintergrundfarbe**: #2563eb (Blue-600 aus Tailwind)
- **Icon-Farbe**: Weiß (#FFFFFF)
- **Symbol**: 💰 (Money Bag Emoji) oder Custom Logo
- **Stil**: Minimalistisch, gut lesbar auf kleinen Bildschirmen

## Screenshots (Optional)

Für den App Store Preview können Screenshots hinzugefügt werden:

- `screenshot-desktop.png` (1280x720px)
- `screenshot-mobile.png` (750x1334px)

Diese werden in `manifest.json` referenziert und verbessern die Installation Experience.
