param(
    [string]$WorkDir = "$PSScriptRoot\..\build",
    [switch]$SkipNativeDeps
)

$ErrorActionPreference = "Stop"
$Commit = "55204c94bb6c8bc1684ada3d712a61f73f324067"
$GraphBLASVersion = "v10.5.0"
$LAGraphVersion = "v1.3.x"

function Need([string]$Cmd) {
    if (-not (Get-Command $Cmd -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Cmd"
    }
}

Need git
Need cargo
Need rustc
Need cmake
Need python

function Get-CMakeVSGenerator {
    $Help = (cmake --help | Out-String)
    foreach ($Generator in @("Visual Studio 18 2026", "Visual Studio 17 2022")) {
        if ($Help.Contains($Generator)) {
            return $Generator
        }
    }
    throw "No supported Visual Studio CMake generator found. Available generators:`n$Help"
}

$VSGenerator = Get-CMakeVSGenerator
Write-Host "Using CMake generator: $VSGenerator"

$WorkDir = [IO.Path]::GetFullPath($WorkDir)
$Src = Join-Path $WorkDir "src"
$Prefix = Join-Path $WorkDir "native-prefix"
$ShimDir = Join-Path $WorkDir "redisearch-shim"
New-Item -ItemType Directory -Force -Path $Src, $Prefix, $ShimDir | Out-Null

$Falkor = Join-Path $Src "FalkorDB"
if (-not (Test-Path $Falkor)) {
    git clone https://github.com/FalkorDB/FalkorDB.git $Falkor
}
Push-Location $Falkor
git fetch origin
git checkout $Commit
Pop-Location

python "$PSScriptRoot\apply_windows_foundation.py" $Falkor

if (-not $SkipNativeDeps) {
    $GB = Join-Path $Src "GraphBLAS"
    if (-not (Test-Path $GB)) {
        git clone --branch $GraphBLASVersion --single-branch --depth 1 `
            https://github.com/DrTimothyAldenDavis/GraphBLAS.git $GB
    }

    $GBBuild = Join-Path $WorkDir "graphblas-build"
    cmake -S $GB -B $GBBuild -G "$VSGenerator" -A x64 `
        -DCMAKE_INSTALL_PREFIX="$Prefix" `
        -DSUITESPARSE_USE_FORTRAN=OFF `
        -DBUILD_STATIC_LIBS=ON `
        -DBUILD_SHARED_LIBS=OFF `
        -DGRAPHBLAS_BUILD_STATIC_LIBS=ON `
        -DGRAPHBLAS_COMPACT=OFF `
        -DGRAPHBLAS_USE_OPENMP=OFF `
        -DBUILD_TESTING=OFF
    cmake --build $GBBuild --config Release --target GraphBLAS_static
    cmake --install $GBBuild --config Release

    $GBStatic = Join-Path $Prefix "lib\graphblas_static.lib"
    $GBAlias = Join-Path $Prefix "lib\graphblas.lib"
    if (-not (Test-Path $GBStatic)) {
        throw "Expected GraphBLAS static library not found: $GBStatic"
    }
    Copy-Item -Force $GBStatic $GBAlias

    $LA = Join-Path $Src "LAGraph"
    if (-not (Test-Path $LA)) {
        git clone --branch $LAGraphVersion --single-branch --depth 1 `
            https://github.com/GraphBLAS/LAGraph.git $LA
    }

    $LABuild = Join-Path $WorkDir "lagraph-build"
    cmake -S $LA -B $LABuild -G "$VSGenerator" -A x64 `
        -DCMAKE_INSTALL_PREFIX="$Prefix" `
        -DBUILD_STATIC_LIBS=ON `
        -DBUILD_SHARED_LIBS=OFF `
        -DLIBRARY_ONLY=ON `
        -DBUILD_TESTING=OFF `
        -DLAGRAPH_USE_OPENMP=OFF `
        -DNO_LIBM=ON `
        -DSUITESPARSE_USE_FORTRAN=OFF `
        -DGraphBLAS_DIR="$Prefix\lib\cmake\GraphBLAS" `
        -DCMAKE_PREFIX_PATH="$Prefix"
    cmake --build $LABuild --config Release --target LAGraph_static LAGraphX_static
    cmake --install $LABuild --config Release

    foreach ($Pair in @(
        @("lagraph_static.lib", "lagraph.lib"),
        @("lagraphx_static.lib", "lagraphx.lib")
    )) {
        $From = Join-Path $Prefix ("lib\" + $Pair[0])
        $To = Join-Path $Prefix ("lib\" + $Pair[1])
        if (-not (Test-Path $From)) {
            throw "Expected LAGraph static library not found: $From"
        }
        Copy-Item -Force $From $To
    }
}

& "$PSScriptRoot\generate_graphblas_bindings.ps1" -FalkorRoot $Falkor -Prefix $Prefix
& "$PSScriptRoot\build_redisearch_shim.ps1" -OutDir $ShimDir -VSGenerator $VSGenerator

Write-Host ""
Write-Host "Prepared source:       $Falkor"
Write-Host "Native prefix:         $Prefix"
Write-Host "RediSearch shim dir:   $ShimDir"
Write-Host "Next: .\scripts\diagnose.ps1"
