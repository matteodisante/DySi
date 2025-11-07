# Update Documentation URLs

After deploying to GitHub Pages, replace `TUO-USERNAME` with your actual GitHub username.

## Files to update:

1. **README.md** (lines 3 and 83)
   - Replace: `https://TUO-USERNAME.github.io/rocket-sim/`
   - With: `https://YOUR-GITHUB-USERNAME.github.io/rocket-sim/`

## Quick replace command:

```bash
# Replace TUO-USERNAME with your actual GitHub username
sed -i '' 's/TUO-USERNAME/your-actual-username/g' README.md
```

Or use find & replace in your editor:
- Find: `TUO-USERNAME`
- Replace with: your actual GitHub username

Then commit:
```bash
git add README.md
git commit -m "Update documentation URLs with GitHub username"
git push origin main
```

## Your documentation will be available at:
`https://YOUR-GITHUB-USERNAME.github.io/rocket-sim/`
