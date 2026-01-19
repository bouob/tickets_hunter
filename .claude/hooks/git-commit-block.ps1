# git-commit-block.ps1 - Hook to block direct git commit
# Requires using /gsave skill instead
# Exit code 1 = block the command

Write-Host ""
Write-Host "========================================"
Write-Host "[BLOCKED] Direct git commit is forbidden!"
Write-Host "========================================"
Write-Host ""
Write-Host "This project uses dual-repo workflow."
Write-Host "Direct 'git commit' bypasses security filters."
Write-Host ""
Write-Host "REQUIRED: Use /gsave instead"
Write-Host ""
Write-Host "Standard workflow:"
Write-Host "  /gsave     - Commit changes (auto-filters sensitive files)"
Write-Host "  /gpush     - Push to private repo"
Write-Host "  /publicpr  - Create PR to public repo"
Write-Host ""
Write-Host "Reference: docs/12-git-workflow/dual-repo-workflow.md"
Write-Host "========================================"
Write-Host ""

exit 1
