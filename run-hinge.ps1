param(
    [switch]$Install,        # open Play Store to Hinge for a one-tap install
    [switch]$Capture,        # start the screenshot->comment hotkey against the emulator window
    [switch]$Once,           # single capture, then exit
    [string]$Avd = "Medium_Phone_API_35",
    [string]$Window = "Medium_Phone",
    [string]$Hotkey = "<ctrl>+<alt>+h",
    [string]$SdkRoot = $env:LOCALAPPDATA + "\Android\Sdk"
)

$ErrorActionPreference = "Stop"
$adb = Join-Path $SdkRoot "platform-tools\adb.exe"
$emulator = Join-Path $SdkRoot "emulator\emulator.exe"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $root ".venv\Scripts\python.exe"

function Fail([string]$msg) { Write-Host "ERROR: $msg" -ForegroundColor Red; exit 1 }
foreach ($p in @($adb, $emulator)) {
    if (-not (Test-Path $p)) { Fail "not found: $p (set -SdkRoot to your Android SDK)" }
}

cmd /c "`"$adb`" start-server >nul 2>&1"

function Emulator-Running {
    $state = (& $adb devices 2>$null) | Select-String "emulator-\d+\s+device"
    return [bool]$state
}

function Wait-Boot {
    Write-Host "waiting for the emulator to boot (first boot can take a few minutes)..." -ForegroundColor Cyan
    & $adb wait-for-device 2>$null
    for ($i = 0; $i -lt 180; $i++) {
        $b = ((& $adb shell getprop sys.boot_completed 2>$null) -join "").Trim()
        if ($b -eq "1") { Write-Host "booted." -ForegroundColor Green; return }
        Start-Sleep 5
    }
    Fail "emulator did not finish booting"
}

if (-not (Emulator-Running)) {
    $avdFile = Get-ChildItem "$env:USERPROFILE\.android\avd\*.ini" -ErrorAction SilentlyContinue |
        Where-Object { $_.BaseName -eq $Avd } | Select-Object -First 1
    if (-not $avdFile) {
        Write-Host "AVD '$Avd' not found. Available:"
        Get-ChildItem "$env:USERPROFILE\.android\avd\*.ini" -ErrorAction SilentlyContinue | ForEach-Object { "  " + $_.BaseName }
        exit 1
    }
    Write-Host "starting emulator '$Avd'..." -ForegroundColor Cyan
    Start-Process -FilePath $emulator -ArgumentList "-avd",$Avd,"-gpu","swiftshader_indirect","-no-snapshot-save","-no-boot-anim"
    Wait-Boot
} else {
    Write-Host "emulator already running." -ForegroundColor Green
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type @'
using System; using System.Runtime.InteropServices;
public struct RECT { public int L, T, R, B; }
public static class Win {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int w, int hh, uint f);
}
'@
$hwnd = (Get-Process qemu-system-x86_64* | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1).MainWindowHandle
if ($hwnd) {
    $r = New-Object RECT; [Win]::GetWindowRect($hwnd, [ref]$r) | Out-Null
    $area = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
    $h = $area.Height - 40; $w = [int](($r.R - $r.L) * $h / ($r.B - $r.T))
    [Win]::SetWindowPos($hwnd, [IntPtr]::Zero, [int](($area.Width - $w) / 2), [int](($area.Height - $h) / 2), $w, $h, 0x0044) | Out-Null
}

function Ensure-Venv {
    if (-not (Test-Path $py)) {
        if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { Fail "uv not found. Install it with: pip install uv" }
        Write-Host "creating python environment with uv (one time)..." -ForegroundColor Cyan
        uv sync --quiet --project $root
    }
}

if ($Install) {
    $hinge = (& $adb shell pm list packages 2>$null) | Select-String "co.hinge.app"
    if ($hinge) {
        Write-Host "Hinge is already installed." -ForegroundColor Green
    } else {
        Write-Host "opening the Play Store page for Hinge. Sign in once if asked, then tap Install." -ForegroundColor Cyan
        & $adb shell am start -a android.intent.action.VIEW -d "market://details?id=co.hinge.app" 2>$null
        Write-Host "once it's installed, run this script with -Capture"
    }
    exit 0
}

if ($Capture -or $Once) {
    Ensure-Venv
    if (-not $env:ANTHROPIC_API_KEY -and -not $env:OPENAI_API_KEY) {
        if (Get-Command claude -ErrorAction SilentlyContinue) {
            Write-Host "no API key set - using the claude CLI (your Claude Code login). Slower, ~5-10s per capture." -ForegroundColor Cyan
        } else {
            Write-Host "WARNING: no ANTHROPIC_API_KEY or OPENAI_API_KEY set and no claude CLI found. The capture call will fail." -ForegroundColor Yellow
        }
    }
    $cap = Join-Path $root "capture\hinge_capture.py"
    if ($Once) {
        & $py $cap --once --window $Window
    } else {
        Write-Host "listening for $Hotkey - capturing the '$Window' emulator window. Ctrl+C to stop." -ForegroundColor Cyan
        & $py $cap --window $Window --hotkey $Hotkey
    }
    exit $LASTEXITCODE
}

Write-Host @"

Hinge is running inside the emulator on this laptop - no phone, no USB debugging.

Next steps:
  - first time:  .\run-hinge.ps1 -Install     (sign in once, tap Install)
  - then open Hinge in the emulator, get a profile on screen
  - capture:     .\run-hinge.ps1 -Capture     (hotkey $Hotkey -> comment on clipboard)
  - one shot:    .\run-hinge.ps1 -Once
"@
