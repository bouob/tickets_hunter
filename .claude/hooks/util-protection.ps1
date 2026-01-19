# util-protection.ps1 - Hook for util.py cross-platform analysis protection
# Triggers when editing util.py or nodriver_util.py
# Exit code 0 = allow (with warning), Exit code non-zero = block

$ErrorActionPreference = "Stop"

# Read stdin for tool input (JSON format from Claude Code)
$input_json = $input | Out-String

# Output warning message
Write-Host ""
Write-Host "========================================"
Write-Host "[UTIL.PY PROTECTION] Cross-Platform Analysis Required"
Write-Host "========================================"
Write-Host ""
Write-Host "You are modifying a shared utility file."
Write-Host "This file is used by ALL platforms."
Write-Host ""
Write-Host "MANDATORY BEFORE EDIT:"
Write-Host "  1. Use Task tool (subagent_type=Explore) to search all call sites"
Write-Host "  2. Verify compatibility with ALL platforms:"
Write-Host "     - TixCraft"
Write-Host "     - iBon (Shadow DOM)"
Write-Host "     - KKTIX"
Write-Host "     - TicketPlus"
Write-Host "     - KHAM"
Write-Host "     - FamiTicket"
Write-Host "     - Cityline"
Write-Host "     - UDN"
Write-Host "     - FunOne"
Write-Host "  3. Document impact analysis"
Write-Host ""
Write-Host "Key shared functions:"
Write-Host "  - get_target_index_by_mode()"
Write-Host "  - get_target_item_from_matched_list()"
Write-Host "  - get_debug_mode()"
Write-Host "  - parse_keyword_string_to_array()"
Write-Host ""
Write-Host "Reference: .specify/memory/constitution.md (Article II)"
Write-Host "========================================"
Write-Host ""

# Allow the edit but show warning (exit 0)
# Change to exit 1 to block completely
exit 0
