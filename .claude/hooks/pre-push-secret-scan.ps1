# Pre-push secret scanner hook.
# Reads the PreToolUse payload from stdin; only acts when the Bash command
# is a `git push`. Sets up mise-managed PATH so `gitleaks` resolves, then
# runs `gitleaks git` over the push range. Exits 2 (block) on findings,
# 0 on clean / non-push commands.

$payload = [Console]::In.ReadToEnd() | ConvertFrom-Json
if ($payload.tool_input.command -notmatch 'git\s+push') {
  exit 0
}

# `mise bin-paths` prints space-separated dirs on one line. Prepend each
# to PATH so PowerShell resolves gitleaks / git installed by mise.
$binPaths = ((mise bin-paths) -split '\s+') -join [IO.Path]::PathSeparator
$env:PATH = $binPaths + [IO.Path]::PathSeparator + $env:PATH

if (git rev-parse --verify '@{u}' 2>$null) {
  $range = '@{u}..HEAD'
} else {
  # Initial push: scan everything reachable from HEAD.
  $range = '--all'
}

gitleaks git . --log-opts $range --config .gitleaks.toml --redact --no-banner --exit-code 2
exit $LASTEXITCODE