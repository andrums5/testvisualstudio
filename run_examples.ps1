param(
  [Parameter(ValueFromRemainingArguments=$true)]
  [string[]]$ArgsRest
)

# Cambia al directorio donde está este script
Set-Location -LiteralPath $PSScriptRoot

# Intenta usar venv si existe, si no usa python del sistema
$venvPy = Join-Path $PSScriptRoot 'venv\Scripts\python.exe'
if (Test-Path $venvPy) {
  & $venvPy -X utf8 scripts\run_examples.py @ArgsRest
} else {
  & python -X utf8 scripts\run_examples.py @ArgsRest
}
