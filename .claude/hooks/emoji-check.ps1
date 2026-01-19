# emoji-check.ps1 - Hook to prevent emoji in Python files
# Triggers when editing *.py files
# Exit code 0 = allow, Exit code 1 = block

$ErrorActionPreference = "Stop"

# Read tool input from stdin
$stdin_content = ""
try {
    while ($line = [Console]::In.ReadLine()) {
        $stdin_content += $line
    }
} catch {
    # End of input
}

# Parse JSON to get the new_string content
try {
    $json = $stdin_content | ConvertFrom-Json
    $new_string = $json.tool_input.new_string

    if (-not $new_string) {
        # No new_string means this might be a different operation, allow it
        exit 0
    }

    # Common emoji ranges (simplified check)
    # Emoticons: U+1F600-U+1F64F
    # Dingbats: U+2700-U+27BF
    # Symbols: U+2600-U+26FF
    # Misc Symbols: U+1F300-U+1F5FF
    # Transport: U+1F680-U+1F6FF

    $emoji_pattern = '[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{FE00}-\u{FE0F}]|[\u{1F000}-\u{1FFFF}]'

    if ($new_string -match $emoji_pattern) {
        Write-Host ""
        Write-Host "========================================"
        Write-Host "[BLOCKED] Emoji detected in Python code!"
        Write-Host "========================================"
        Write-Host ""
        Write-Host "Emoji is FORBIDDEN in .py files."
        Write-Host "Reason: Windows cp950 encoding errors"
        Write-Host ""
        Write-Host "Incorrect: print('Success!')"
        Write-Host "Correct:   print('[SUCCESS] Operation completed')"
        Write-Host ""
        Write-Host "Reference: CLAUDE.md - Code Standards"
        Write-Host "========================================"
        Write-Host ""
        exit 1
    }
} catch {
    # If JSON parsing fails, allow the operation
    # This ensures we don't block legitimate operations
}

exit 0
