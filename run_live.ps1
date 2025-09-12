param(
  [Parameter(ValueFromRemainingArguments=$true)]
  [string[]]$ArgsRest
)
Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONUTF8 = 1
$py = Join-Path $PSScriptRoot 'venv\Scripts\python.exe'
if (Test-Path $py) {
  & $py -u test.py live @ArgsRest
} else {
  & python -u test.py live @ArgsRest
}
