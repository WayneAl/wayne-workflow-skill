#!/bin/zsh
# Memory gardener for wayne-workflow. Run manually from a terminal:
#   zsh gardener/run.sh
# (Not scheduled: a launchd LaunchAgent can't read ~/Documents without Full Disk
# Access for /bin/zsh. The .last-scan marker makes each run cover everything since
# the previous one, however long ago.)
set -u
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
REPO="${0:A:h:h}"
LOGDIR="$REPO/gardener/logs"; mkdir -p "$LOGDIR"
LOG="$LOGDIR/$(date +%Y-%m-%d).log"

cd "$REPO" || exit 1
# hard cap: a run must never exceed 15 min (macOS has no `timeout`)
perl -e 'alarm shift @ARGV; exec @ARGV' 900 \
claude -p "$(cat "$REPO/gardener/prompt.md")" \
  --permission-mode acceptEdits \
  --allowedTools Read Glob Grep LS Write Edit 'Bash(git:*)' 'Bash(ls:*)' 'Bash(find:*)' 'Bash(date:*)' \
  --add-dir "$HOME/.claude/projects" \
  >"$LOG" 2>&1
echo "exit=$?" >>"$LOG"

# mark scan horizon so a skipped week is covered by the next run
touch "$REPO/gardener/.last-scan"

# surface new proposals via macOS notification
n=$(ls "$REPO/gardener/inbox" 2>/dev/null | grep -c '\.md$')
if [ "${n:-0}" -gt 0 ]; then
  osascript -e "display notification \"$n proposal file(s) pending review — gardener/inbox/\" with title \"wayne-workflow gardener\"" 2>/dev/null
fi
