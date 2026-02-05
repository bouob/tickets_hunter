# PostToolUse hook: Verify Python syntax after Edit
# Runs py_compile on edited .py files to catch syntax errors early

$input = $env:CLAUDE_TOOL_INPUT | ConvertFrom-Json
$filePath = $input.file_path

if ($filePath -match '\.py$') {
    $result = python -m py_compile $filePath 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Syntax error in $filePath"
        Write-Host $result
        exit 1
    }
}

exit 0
