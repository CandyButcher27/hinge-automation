# emulator — running Hinge on the laptop

## Purpose
Hinge only ships a phone app. It runs inside an Android emulator on this laptop; everything else
(capture, adb driving) targets that emulator.

## Location
- `run-hinge.ps1` — boots the emulator, `-Install` opens the Play Store page, `-Capture` / `-Once` start the capture tool.
- SDK: `%LOCALAPPDATA%\Android\Sdk` (`platform-tools\adb.exe`, `emulator\emulator.exe`).
- AVD: `Medium_Phone_API_35`. Emulator window title: `Android Emulator - Medium_Phone_API_35:5554`. Device serial `emulator-5554`.
- Device screen: 1080x2400.

## Configuration / launch
- Normal launch: `.\run-hinge.ps1 -Capture`. Runs the hotkey listener until Ctrl+C.
- The script starts the emulator with `-gpu swiftshader_indirect -no-snapshot-save -no-boot-anim`.
- Boot takes ~25s after a cold start.
- Hinge is installed and the account is signed in (verified 2026-09-26).

## Important constraints (learned 2026-09-26)
- **adb daemon must be up before the script queries it.** Windows PowerShell 5.1 with
  `$ErrorActionPreference = "Stop"` turns adb's stderr line `* daemon not running; starting now`
  into a fatal NativeCommandError. The script now runs `adb start-server` through `cmd /c` first.
  The daemon also dies when a background shell that started it exits, so the fix has to live in the script.
- **Host GPU mode renders Hinge black.** With the default GPU mode, the screen went fully black
  whenever the keyboard opened (verification-code screen). A screenshot taken on the device was black too, and the window had
  no FLAG_SECURE. Hinge was alive, with a looping background video decoding. `-gpu swiftshader_indirect` fixed it,
  and sign-in completed.
- **Cost of swiftshader:** in-app videos (e.g. video prompt answers) render as black boxes.
- **Window can open off-screen** (top edge at y=-659). `run-hinge.ps1` now resizes the qemu window with Win32
  `SetWindowPos` to the primary work-area height minus 40, keeping aspect, and centres it. The work area is
  1536x816 logical (125% scaling) and the default window is 394x881, so it cannot fit unscaled. Result:
  346x776 at 595,20, verified 2026-09-28. The emulator side toolbar is a separate window and follows it.
  The second monitor is at x=1920 (1920x1080).
- Hinge may detect emulators and block features; not observed so far.

## Change History
- 2026-09-26: added `adb start-server` preamble and `-gpu swiftshader_indirect` to `run-hinge.ps1`.
