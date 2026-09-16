#!/bin/zsh
# SessionStart hook: surface pending gardener proposals at the start of every
# Claude session until the user reviews them. Silence when the inbox is empty.
INBOX="${0:A:h:h}/gardener/inbox"
n=$(ls "$INBOX" 2>/dev/null | grep -c '\.md$')
if [ "${n:-0}" -gt 0 ]; then
  files=$(ls "$INBOX" 2>/dev/null | grep '\.md$' | tr '\n' ' ')
  printf '{"systemMessage":"wayne-workflow gardener: %s proposal file(s) pending review (gardener/inbox/ %s)","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"Pending wayne-workflow gardener proposals await the user'"'"'s review: %sin %s/. When the user accepts an item (accept / 收), fold it into the skill (always-on.md, SKILL.md, or the right references/ file), commit the fold, then delete the inbox file; when they drop it (drop / 砍), delete the inbox file. gardener/inbox/ is gitignored, so the inbox file itself is never committed. Do not fold anything without their verdict."}}\n' "$n" "$files" "$files" "$INBOX"
fi
exit 0
