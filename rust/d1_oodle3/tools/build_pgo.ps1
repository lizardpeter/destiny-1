# Build a CPU-specific, PGO-trained Rust Oodle 2.3 DLL on Windows.
# Fixtures: a directory containing matching <block>.bin and <block>.raw files.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $Fixtures,
    [int] $Iterations = 140
)

$ErrorActionPreference = "Stop"
if ($Iterations -lt 1) { throw "Iterations must be >= 1" }

$crate = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$manifest = Join-Path $crate "Cargo.toml"
$trainingScript = Join-Path $crate "tools\train_pgo.py"
$fixturesPath = (Resolve-Path $Fixtures).Path
$buildRoot = Join-Path $crate "target-pgo"
$raw = Join-Path $buildRoot "profiles"
$trainTarget = Join-Path $buildRoot "instrumented"
$useTarget = Join-Path $buildRoot "optimized"
$profileData = Join-Path $buildRoot "d1_oodle3.profdata"

New-Item -ItemType Directory -Force -Path $raw | Out-Null
# Never combine stale profiles from a previous compiler/build.
Get-ChildItem -Path $raw -Filter "*.profraw" -File | Remove-Item -Force

$before = @{}
foreach ($name in @("CARGO_ENCODED_RUSTFLAGS", "RUSTFLAGS", "CARGO_TARGET_DIR", "CARGO_PROFILE_RELEASE_LTO", "CARGO_PROFILE_RELEASE_CODEGEN_UNITS")) {
    $before[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}
try {
    # The ASCII unit separator preserves paths with spaces in rustc arguments.
    $sep = [char] 31
    $env:RUSTFLAGS = $null
    $env:CARGO_PROFILE_RELEASE_LTO = "fat"
    $env:CARGO_PROFILE_RELEASE_CODEGEN_UNITS = "1"

    & rustup component add llvm-tools-preview
    if ($LASTEXITCODE -ne 0) { throw "Failed to install LLVM profile tools" }

    $env:CARGO_TARGET_DIR = $trainTarget
    $env:CARGO_ENCODED_RUSTFLAGS = (@("-C", "target-cpu=native", "-C", "profile-generate=$raw") -join $sep)
    & cargo build --release --manifest-path $manifest
    if ($LASTEXITCODE -ne 0) { throw "Instrumented Rust codec did not compile" }
    $trainingDll = Join-Path $trainTarget "release\d1_oodle3.dll"
    if (-not (Test-Path $trainingDll)) { throw "Missing instrumented DLL: $trainingDll" }

    & python $trainingScript --dll $trainingDll --fixtures $fixturesPath --iterations $Iterations
    if ($LASTEXITCODE -ne 0) { throw "Profile training or byte-for-byte verification failed" }

    $sysroot = (& rustc --print sysroot | Select-Object -First 1).Trim()
    if ($LASTEXITCODE -ne 0) { throw "Failed to locate Rust sysroot" }
    $profileTool = Join-Path $sysroot "lib\rustlib\x86_64-pc-windows-msvc\bin\llvm-profdata.exe"
    if (-not (Test-Path $profileTool)) { throw "Missing llvm-profdata.exe: $profileTool" }
    $profiles = @(Get-ChildItem -Path $raw -Filter "*.profraw" -File | ForEach-Object { $_.FullName })
    if ($profiles.Count -eq 0) { throw "Instrumentation did not produce a .profraw file" }
    & $profileTool merge -o $profileData @profiles
    if ($LASTEXITCODE -ne 0) { throw "LLVM profile merge failed" }

    $env:CARGO_TARGET_DIR = $useTarget
    $env:CARGO_ENCODED_RUSTFLAGS = (@("-C", "target-cpu=native", "-C", "profile-use=$profileData") -join $sep)
    & cargo build --release --manifest-path $manifest
    if ($LASTEXITCODE -ne 0) { throw "PGO-optimized Rust codec did not compile" }

    $resultDll = Join-Path $useTarget "release\d1_oodle3.dll"
    if (-not (Test-Path $resultDll)) { throw "Missing optimized DLL: $resultDll" }
    Write-Host "PGO_NATIVE_DLL: $resultDll"
    Write-Host "PGO_PROFILE: $profileData"
    Write-Host "Built with native CPU features, fat LTO, and validated training input."
    Write-Host "CPU-specific DLL: benchmark before deploying, and do not distribute as generic x86-64."
}
finally {
    foreach ($name in $before.Keys) {
        [Environment]::SetEnvironmentVariable($name, $before[$name], "Process")
    }
}
