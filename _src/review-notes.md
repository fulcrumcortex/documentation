# Documentation review — 5 November 2026

Scope: expand the published GitHub Pages user guides, add privacy-safe screenshots and add Fulcrum Code documentation. Create a separate root GitHub homepage explaining Cortex and Sidekick skills and linking to these guides.

## Evidence and coverage

- Existing 33 guides retained and reviewed. The homepage was updated; the other 32 guides gained task-specific worked examples, result checks and troubleshooting.
- Eight new Code guides cover installation/sign-in, models, Plan/Build, review, tool families, worktrees, task tracking, scheduling, skills, agents, sessions, memory, usage, sharing, MCP, hooks/plugins, voice/images, themes/keybindings and VS Code. Checked against Code README, configuration reference and implementation of commands, skill discovery, CLI, TUI and tools at source revision 028c57c. Older command/MCP reference prose contains stale limitations; the current command implementation takes precedence.
- New Drive, Docs, Wallet and Cortex/Sessions guides cover workspace files, permissions, document editing/collaboration, credit/account context and orchestrated work.
- Five new CRM/Lyre guides cover resources/SMS/connections, reports/workflows, invoices/products, projects/issues and settings/integrations.
- Mail/Calendar/Drive/Docs/Wallet implementation and fixture references were reviewed in the current local Mail release checkout (HEAD 37c4d9059cadc102faaf5905570462ad46a57c52; local built release metadata a94fbb51f2a2bcedfa1ad85332e67a40a0acb4b6, marked dirty). Screenshots demonstrate the locally built UI, not a claim of exact production parity.
- CRM source reviewed at 4bf11224c. Lyre source reviewed at 309067d. Sessions README and orchestration context reviewed at bf9fabf.
- No real user data, payments, calls, campaigns or production writes were used for screenshots or guide validation.

## Limits

This is a user-guide expansion, not an audit proving that every enabled module, third-party integration, billing plan or production behaviour is working. API references remain in their product sources. Availability depends on role, workspace, account and release. Payment, phone and recording guides explain product operation without claiming legal compliance or running a paid action.

The Sidekick skills repository was empty at review time. The homepage and Code guide describe that accurately; they do not advertise an installable pack. Existing read-only access to that repository was not changed.

## Validation

Run the static site checker (including online external links), browser checks for all generated pages and screenshot loading, representative mobile layouts, screenshot OCR/visual inspection, metadata checks, and source-example validation before publication. Release revisions and live checks belong in the release record after the commits are known.
