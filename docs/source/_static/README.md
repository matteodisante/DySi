# Static Files for Documentation

Place your logo and other static files in this directory.

## Required Files

### Logo Images

1. **`logo.png`** (Required)
   - Main logo for light mode
   - Recommended size: 200x50 px (or proportional)
   - Format: PNG with transparent background
   - This will appear in the sidebar and navbar

2. **`logo_dark.png`** (Optional)
   - Logo for dark mode (if different from light mode)
   - Same dimensions as logo.png
   - If not provided, logo.png will be used for both themes

### Favicon (Optional)

3. **`favicon.ico`** (Optional)
   - Browser tab icon
   - Size: 16x16 or 32x32 px
   - Format: .ico or .png

## How to Add Your Logo

### Option 1: Copy your existing logo
```bash
cp /path/to/your/logo.png docs/source/_static/logo.png
```

### Option 2: Create a simple text-based logo
If you don't have a logo yet, you can use a placeholder or create one online:
- [Canva](https://www.canva.com/) - Free logo maker
- [LogoMakr](https://logomakr.com/) - Simple online tool
- [Figma](https://www.figma.com/) - Professional design tool

### Option 3: Use emoji as placeholder
For a quick placeholder, you can use an emoji-based logo (will be converted to image).

## Logo Guidelines

- **Dimensions**: 200-400px wide, 50-100px tall recommended
- **Format**: PNG preferred (supports transparency)
- **File size**: < 100KB for fast loading
- **Background**: Transparent recommended
- **Colors**: Consider both light and dark mode visibility

## Example Logo Locations

After adding your logo files, the structure should be:
```
docs/source/_static/
├── logo.png          # Main logo (required)
├── logo_dark.png     # Dark mode logo (optional)
├── favicon.ico       # Browser icon (optional)
└── custom.css        # Custom styles (optional)
```

## Testing

After adding your logo, rebuild the documentation:
```bash
cd docs
make clean
make html
open _build/html/index.html
```

## Troubleshooting

If your logo doesn't appear:
1. Check file name matches exactly: `logo.png` (lowercase)
2. Check file is in `docs/source/_static/` directory
3. Run `make clean && make html` to rebuild
4. Check browser console for image loading errors
5. Verify image format is supported (PNG, SVG, JPG)
