# M7 build-exFAT + deploy — progress ledger

Branch: feat/m7-build-exfat-deploy
Plan A: ~/Documents/cv/mkpfs-tui/superpowers/plans/2026-06-20-m7-build-exfat.md (Tasks 1-7)
Plan B: ~/Documents/cv/mkpfs-tui/superpowers/plans/2026-06-23-m7b-deploy-ftp.md (Tasks B1-B8)

Task 1: complete (commits 27f06f2..ed6c804, review clean — Approved)
  Minor (deferred to final review): sizing.py "1M": 1024*_KB → could read _MB (same value); test comment 'spare=64MB(floor)' imprecise.
Task 2: complete (commits ed6c804..98e9de8, review clean — Approved; Minor: dup-key iter in _extract_title, plan-verbatim/harmless)
Task 3: complete (commits 98e9de8..3f475e2, review clean — Approved, no issues)
Task 4: complete (commits 3f475e2..9f50101, review clean — Approved; real mkfs/fsck smoke ran; Minor cosmetics only)
Task 5: complete (commits 9f50101..c7632f6, review clean — Approved; full suite 150/150; fixture annotations added for ruff ANN001)
Task 6: complete (commits c7632f6..3554f0d, review clean — Approved; full suite 152; .renderable→.content API fix)
Task 7: complete (docs + spec + full gate: 152 passed, ruff clean; mkpfs-tui.spec needed hiddenimports for mkpfs_tui.exfat.cli; both boundary greps empty)
