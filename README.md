# md-checklist-generator

**Transform your Markdown checklists into professional PDF documents with one command.**

Stop manually formatting checklists for printing. This tool takes your simple Markdown file with checkboxes and converts it into a beautifully styled PDF ready for distribution, printing, or digital signing.

## Why use this?

- **No more manual formatting** — Write checklists in Markdown, get polished PDFs
- **Professional appearance** — Clean design with PT Sans fonts and colored accents
- **Visual checkboxes** — Graphical checkmarks (not just "x" characters)
- **Ready to print** — Optimized layout with proper margins and signature lines
- **Open source** — MIT license, free to use and modify

## Installation

### Dependencies

First, install the required Python package:

```bash
pip install reportlab
```

### Run

```bash
python checklist_generator.py checklist.md
```

## Perfect for:

- Daily task checklists
- Quality assurance checklists  
- Pre-flight inspection sheets
- Delivery acceptance forms
- Testing checklists
- Any process that needs a printable checklist

## How it works:

1. Write your checklist in Markdown
2. Run one command
3. Get a professional PDF ready to use

## Example:

**Input (Markdown):**
```markdown
# Server Maintenance Checklist

## Pre-check
- [ ] Verify backup completed
- [ ] Check disk space
- [x] Notify users about downtime

## During maintenance  
- [ ] Update kernel
- [x] Clear old logs
- [ ] Reboot server
```

## License

MIT License

Copyright (c) 2026 Andrey Kalinin

This license allows you to freely use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of this software, provided that the copyright notice is retained.

Mandatory condition: When using this library, you must retain the author's information in the source code.
