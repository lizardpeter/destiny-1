param(
    [Parameter(Mandatory=$true)][string]$FalkorRoot,
    [Parameter(Mandatory=$true)][string]$Prefix
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command bindgen -ErrorAction SilentlyContinue)) {
    cargo install bindgen-cli --version 0.72.1
}

$candidates = @(
    (Join-Path $Prefix "include\suitesparse\GraphBLAS.h"),
    (Join-Path $Prefix "include\GraphBLAS.h"),
    (Join-Path $Prefix "include\SuiteSparse\GraphBLAS.h")
)
$Header = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Header) {
    throw "GraphBLAS.h was not found under $Prefix"
}

$Out = Join-Path $env:TEMP "falkordb_graphblas_windows.rs"

bindgen $Header `
    --default-enum-style rust `
    --opaque-type "GB_Iterator_opaque" `
    --blocklist-type "FILE" `
    --raw-line "pub enum FILE {}" `
    --allowlist-type "^(GrB|GxB|GB)_.*" `
    --allowlist-function "^(GrB|GxB|GB)_.*" `
    --allowlist-var "^(GrB|GxB|GB)_.*" `
    -- `
    -target x86_64-pc-windows-msvc `
    "-I$(Split-Path $Header -Parent)" `
    > $Out

if (-not (Test-Path $Out) -or (Get-Item $Out).Length -lt 10000) {
    throw "Generated GraphBLAS binding file is unexpectedly small"
}

python "$PSScriptRoot\splice_graphblas_bindings.py" $FalkorRoot $Out
Write-Host "Windows GraphBLAS bindings regenerated."
