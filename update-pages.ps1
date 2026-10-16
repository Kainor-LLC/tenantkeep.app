#Requires -Version 7.4
# Copyright (c) 2026 Kainor LLC.
# Re-renders guide, licensing, how-it-works and the catalog from the posture repository beside this one.
$ErrorActionPreference = 'Stop'
$site = $PSScriptRoot
$posture = Join-Path $site '..' 'tenantkeep-posture'
if (-not (Test-Path $posture)) { throw "Posture repository not found at $posture" }
& (Join-Path $posture 'build.ps1') -Task Catalog -SkipInstall | Out-Null
New-Item -ItemType Directory -Path (Join-Path $site '.work') -Force | Out-Null
foreach ($n in 'guide', 'licensing', 'architecture', 'footprint') { [System.IO.File]::WriteAllText((Join-Path $site '.work' "$n.fragment.html"), (ConvertFrom-Markdown -Path (Join-Path $posture 'docs' "$n.md")).Html) }
& python3 (Join-Path $site 'render-pages.py')
Write-Host 'Pages rendered. Review the diff, then commit and push.'
