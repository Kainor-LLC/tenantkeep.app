#Requires -Version 7.4
# Copyright (c) 2026 Kainor LLC.
# Re-renders Posture's pages from the posture repository beside this one: guide, licensing, how-it-works, architecture
# and the catalog. -Sample also rebuilds the sample report from the made-up demo tenant (build.ps1 -Task Demo),
# publishes the whole report at /posture/sample-report/ and writes the pictures of it to docs/assets/posture/. The
# sample and every picture come from that demo tenant only, never from a real one.
param([switch] $Sample)
$ErrorActionPreference = 'Stop'
$site = $PSScriptRoot
$posture = Join-Path $site '..' 'tenantkeep-posture'
if (-not (Test-Path $posture)) { throw "Posture repository not found at $posture" }
& (Join-Path $posture 'build.ps1') -Task Catalog -SkipInstall | Out-Null
New-Item -ItemType Directory -Path (Join-Path $site '.work') -Force | Out-Null
foreach ($n in 'guide', 'licensing', 'architecture', 'footprint') { [System.IO.File]::WriteAllText((Join-Path $site '.work' "$n.fragment.html"), (ConvertFrom-Markdown -Path (Join-Path $posture 'docs' "$n.md")).Html) }
if ($Sample) {
    & (Join-Path $posture 'build.ps1') -Task Demo -SkipInstall | Out-Null
    $demo = Join-Path $posture 'out' 'demo'
    $shots = @(Get-ChildItem -LiteralPath (Join-Path $demo 'screens') -Filter '*.png' -ErrorAction SilentlyContinue)
    if ($shots.Count -eq 0) { throw "No pictures in $(Join-Path $demo 'screens'): build.ps1 -Task Demo needs Edge or Chrome (TENANTKEEP_BROWSER)." }

    # Pictures of the report: 1400 pixels wide, JPEG, like the site's others. Resized with sips, which macOS has.
    if (-not (Get-Command sips -ErrorAction SilentlyContinue)) { throw 'The pictures are resized with sips, which this machine does not have. Run -Sample on a Mac.' }
    $pictures = Join-Path $site 'docs' 'assets' 'posture'
    New-Item -ItemType Directory -Path $pictures -Force | Out-Null
    foreach ($png in $shots) {
        $jpg = Join-Path $pictures "report-$($png.BaseName).jpg"
        & sips -s format jpeg -s formatOptions 72 --resampleWidth 1400 $png.FullName --out $jpg | Out-Null
        if (-not (Test-Path -LiteralPath $jpg)) { throw "sips wrote no picture for $($png.Name)." }
    }

    # The whole report at /posture/sample-report/. It is the file the module wrote, with two additions: a bar at the
    # top that says what it is and leads back to the site (not printed), and a tag that keeps a page of made-up
    # names out of search results. The build has already refused a report holding a path from this machine.
    $report = [System.IO.File]::ReadAllText((Join-Path $demo 'fernquill' 'report.html'))
    $bar = '<style>.tk-sample-bar{display:flex;gap:6px 18px;justify-content:space-between;align-items:center;flex-wrap:wrap;padding:10px 24px;background:#131E2E;color:#F4F7FB;font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}.tk-sample-bar b{color:#fff}.tk-sample-bar a{color:#F4F7FB;font-weight:600;margin-right:14px}.tk-sample-bar a:last-child{margin-right:0}@media print{.tk-sample-bar{display:none}}</style><div class="tk-sample-bar"><span><b>Sample report.</b> Fernquill Engineering is a made-up tenant and every value here is invented.</span><span><a href="/posture/">TenantKeep Posture</a><a href="/guide/">Guide</a><a href="/trial/">Free trial</a></span></div>'
    $head = [regex]::Match($report, '<head[^>]*>')
    if (-not $head.Success) { throw 'The sample report has no <head> tag.' }
    $report = $report.Insert($head.Index + $head.Length, '<meta name="robots" content="noindex">')
    $body = [regex]::Match($report, '<body[^>]*>')
    if (-not $body.Success) { throw 'The sample report has no <body> tag to put the bar after.' }
    $report = $report.Insert($body.Index + $body.Length, $bar)
    foreach ($leak in @($HOME, (Resolve-Path -LiteralPath $posture).Path, $site) | Where-Object { $_ }) { if ($report.Contains([string]$leak)) { throw "The sample report holds a path from this machine ($leak); not published." } }
    $sampleFolder = Join-Path $site 'docs' 'posture' 'sample-report'
    New-Item -ItemType Directory -Path $sampleFolder -Force | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $sampleFolder 'index.html'), $report, [System.Text.UTF8Encoding]::new($false))
    Write-Host "Sample report and $($shots.Count) pictures written."
}
& python3 (Join-Path $site 'render-pages.py')
Write-Host 'Pages rendered. Review the diff, then commit.'
