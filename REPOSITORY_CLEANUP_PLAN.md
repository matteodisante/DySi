# Repository Cleanup and Reorganization Plan

**Date:** 2024-11-12  
**Status:** PROPOSED - Ready for execution

---

## Issues Identified

### 1. **Duplicate and Backup Files (REMOVE)**

Root directory contains many backup/old files:

```
❌ CHANGELOG.md.backup (6.6K) - duplicate of CHANGELOG.md
❌ README.md.backup (19K) - old version
❌ README.md.old (19K) - very old version
❌ CLEANUP_2025-11-12.md (5.9K) - temporary cleanup notes
```

**Action:** DELETE all `.backup` and `.old` files

---

### 2. **Documentation Phase Reports (ARCHIVE)**

Root directory has temporary documentation tracking files:

```
📄 DOCUMENTATION_PHASE1_COMPLETE.md (8.6K)
📄 DOCUMENTATION_PHASE2_COMPLETE.md (13K)
📄 DOCUMENTATION_PHASE3_COMPLETE.md (10K)
📄 DOCUMENTATION_RESTRUCTURING_PROMPT.md (20K)
```

**Total:** 51.6K of temporary docs

**Action:** Move to `docs/development/documentation_history/`

---

### 3. **Mixed Documentation Formats (MIGRATE)**

`docs/` contains both `.md` (Markdown) and `.rst` (reStructuredText):

**Old Markdown docs (obsolete, replaced by Sphinx .rst):**
```
❌ docs/user/CONFIGURATION_REFERENCE.md
❌ docs/user/MOTOR_STATE_EXPORT_GUIDE.md
❌ docs/user/PLOTS_AND_OUTPUT_REFERENCE.md
❌ docs/user/TROUBLESHOOTING.md
❌ docs/user/README.md
```

**Developer docs (still useful, keep as .md):**
```
✅ docs/developer/ARCHITECTURE.md
✅ docs/developer/API_REFERENCE.md
✅ docs/developer/MODULE_REFERENCE.md
✅ docs/developer/CONTRIBUTING.md
```

**Implementation notes (archive):**
```
📦 docs/implementation/IMPLEMENTATION_SUMMARY.md
📦 docs/implementation/IMPLEMENTATION_COMPLETE_SUMMARY.md
📦 docs/implementation/REPORT_GENERATOR_SPEC.md
📦 docs/implementation/ROCKET_STATE_EXPORT_IMPLEMENTATION_PLAN.md
```

**Action:**
- DELETE obsolete user .md docs (replaced by Sphinx .rst)
- KEEP developer .md docs (GitHub-friendly)
- MOVE implementation docs to archive

---

### 4. **Sphinx Build Output (CLEAN)**

```
❌ docs/_build/ - 50+ MB of generated HTML
```

**Action:** Add to `.gitignore` (should not be in git)

---

### 5. **Output Files (ORGANIZE)**

```
outputs/artemis/
outputs/artemis2/
outputs/zeus/
outputs/my_first_rocket/
```

All contain simulation results (plots, CSV, JSON, txt).

**Action:** Add `.gitignore` rule for `outputs/*/` (user-generated data)

---

## Proposed New Structure

```
rocket-sim/
├── .github/                    # GitHub Actions, templates
├── configs/                    # Configuration files
│   ├── single_sim/
│   ├── templates/
│   └── README.md
├── data/                       # Reference data
│   ├── motors/
│   └── drag_curves/
├── docs/                       # Documentation (Sphinx)
│   ├── source/                 # .rst files
│   │   ├── getting_started/
│   │   ├── user/
│   │   ├── api/
│   │   └── ...
│   ├── developer/              # Developer .md docs (keep)
│   │   ├── ARCHITECTURE.md
│   │   ├── API_REFERENCE.md
│   │   ├── MODULE_REFERENCE.md
│   │   └── CONTRIBUTING.md
│   ├── _archive/               # OLD/OBSOLETE docs
│   │   ├── implementation/
│   │   ├── documentation_history/
│   │   └── obsolete_user_docs/
│   └── Makefile
├── examples/                   # Example scripts
├── notebooks/                  # Jupyter notebooks
├── scripts/                    # CLI scripts
├── src/                        # Source code
├── tests/                      # Test suite
├── outputs/                    # Simulation outputs (gitignored)
├── CHANGELOG.md
├── README.md
├── requirements.txt
├── requirements-docs.txt
├── setup.py
└── .gitignore
```

---

## Detailed Actions

### Phase 1: Remove Obsolete Files ❌

**DELETE (7 files, ~70K):**
```bash
rm CHANGELOG.md.backup
rm README.md.backup
rm README.md.old
rm CLEANUP_2025-11-12.md
rm docs/user/CONFIGURATION_REFERENCE.md        # Replaced by .rst
rm docs/user/MOTOR_STATE_EXPORT_GUIDE.md       # Obsolete
rm docs/user/PLOTS_AND_OUTPUT_REFERENCE.md     # Obsolete
rm docs/user/TROUBLESHOOTING.md                # Will be in Sphinx
rm docs/user/README.md                         # Redundant
```

---

### Phase 2: Archive Documentation History 📦

**CREATE archive directory:**
```bash
mkdir -p docs/_archive/documentation_history
mkdir -p docs/_archive/implementation
mkdir -p docs/_archive/obsolete_user_docs
```

**MOVE phase reports:**
```bash
mv DOCUMENTATION_PHASE1_COMPLETE.md docs/_archive/documentation_history/
mv DOCUMENTATION_PHASE2_COMPLETE.md docs/_archive/documentation_history/
mv DOCUMENTATION_PHASE3_COMPLETE.md docs/_archive/documentation_history/
mv DOCUMENTATION_RESTRUCTURING_PROMPT.md docs/_archive/documentation_history/
```

**MOVE implementation docs:**
```bash
mv docs/implementation/* docs/_archive/implementation/
rmdir docs/implementation
```

---

### Phase 3: Update .gitignore 🚫

**ADD to `.gitignore`:**
```gitignore
# Sphinx build output
docs/_build/
docs/build/

# User-generated simulation outputs
outputs/*/
!outputs/.gitkeep

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# macOS
.DS_Store

# Jupyter
.ipynb_checkpoints/

# Temporary files
*.tmp
*.backup
*.old
~*
```

---

### Phase 4: Clean Build Artifacts 🧹

**REMOVE (if in git):**
```bash
git rm -r --cached docs/_build/
echo "docs/_build/" >> .gitignore
```

---

### Phase 5: Organize configs/ 📁

**Current structure is good, but add README:**

```
configs/
├── single_sim/
│   ├── 01_minimal.yaml
│   └── 02_complete.yaml
├── templates/
│   └── tutorial_rocket.yaml
└── README.md  (already exists, update if needed)
```

---

## File Count Summary

### Files to DELETE: 9 files (~75 KB)
- 3 backup files (README, CHANGELOG)
- 1 temporary cleanup file
- 5 obsolete user .md docs

### Files to ARCHIVE: 8 files (~90 KB)
- 4 documentation phase reports
- 4 implementation notes

### Directories to .gitignore: 2
- `docs/_build/` (~50+ MB)
- `outputs/*/` (variable size)

### **Total cleanup: ~125 KB + 50+ MB build artifacts**

---

## Execution Checklist

- [ ] **Phase 1:** Delete obsolete files (9 files)
- [ ] **Phase 2:** Create archive structure and move files (8 files)
- [ ] **Phase 3:** Update `.gitignore`
- [ ] **Phase 4:** Remove build artifacts from git
- [ ] **Phase 5:** Test that code still works (`pytest`, run simulation)
- [ ] **Phase 6:** Commit cleanup: "chore: Repository cleanup and reorganization"
- [ ] **Phase 7:** Update README if needed

---

## Safety Checks Before Execution

### 1. Verify no code imports obsolete docs
```bash
grep -r "CONFIGURATION_REFERENCE.md" src/ tests/ scripts/
grep -r "MOTOR_STATE_EXPORT_GUIDE" src/ tests/ scripts/
```

### 2. Verify docs still build
```bash
cd docs && make clean && make html
```

### 3. Verify tests pass
```bash
pytest tests/
```

### 4. Verify example script works
```bash
python examples/01_basic_simulation.py
```

---

## Impact Analysis

### ✅ No Breaking Changes
- All deletions are documentation files
- No source code affected
- No configuration files removed
- Archive preserves history

### ✅ Benefits
- Cleaner root directory
- Clear documentation structure
- Reduced repository size (~50+ MB)
- Better .gitignore practices
- Easier navigation

### ⚠️ Considerations
- Archive docs still accessible in `docs/_archive/`
- Git history preserves all deleted files
- Can restore any file if needed: `git checkout <commit> -- <file>`

---

## Recommendation

**EXECUTE cleanup** - Safe and beneficial:

1. All obsolete files clearly identified
2. Archive preserves documentation history
3. No code functionality affected
4. Significant reduction in clutter
5. Follows best practices (.gitignore for build outputs)

**Estimated time:** 15-20 minutes

**Risk level:** LOW (all reversible via git)

---

**Ready to proceed?** Execute phases 1-7 in order.
