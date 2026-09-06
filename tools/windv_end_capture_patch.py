#!/usr/bin/env python3
"""Patch Wachhund/WinDV v1.6.0/main with an explicit End Capture control."""
from pathlib import Path
import sys


def replace_once(root: Path, rel: str, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{rel}: expected exactly one match, found {count}\n--- needle ---\n{old}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="")
    print(f"patched {rel}")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: windv_end_capture_patch.py <WinDV source root>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()

    replace_once(root, "Resource.h",
        "#define IDC_CHK_SHA256                  1074\n",
        "#define IDC_CHK_SHA256                  1074\n#define IDC_END_CAPTURE                 1075\n")
    replace_once(root, "Resource.h",
        "#define _APS_NEXT_CONTROL_VALUE         1075\n",
        "#define _APS_NEXT_CONTROL_VALUE         1076\n")
    replace_once(root, "WinDV.rc",
        '    PUSHBUTTON      "Record",IDC_RECORD,259,130,50,14,WS_GROUP\n    PUSHBUTTON      "Cancel",IDCANCEL,259,145,50,14,WS_GROUP\n',
        '    PUSHBUTTON      "Record",IDC_RECORD,259,130,50,14,WS_GROUP\n    PUSHBUTTON      "End Capture",IDC_END_CAPTURE,259,145,50,14,WS_GROUP\n    PUSHBUTTON      "Cancel",IDCANCEL,259,145,50,14,WS_GROUP\n')
    replace_once(root, "DVToolsDlg.h",
        "\tafx_msg void OnCapture();\n\tafx_msg void OnRecord();\n",
        "\tafx_msg void OnCapture();\n\tafx_msg void OnEndCapture();\n\tafx_msg void OnRecord();\n")
    replace_once(root, "DVToolsDlg.cpp",
        "\t// Action buttons: each visible on its own tab only.\n"
        "\t{IDC_CAPTURE,\t XR, XR,100,100,\tTAB_CAPTURE},\n"
        "\t{IDC_RECORD,\t XR, XR,100,100,\tTAB_RECORD},\n"
        "\t// Cancel button: visible on both active tabs.\n"
        "\t{IDCANCEL,\t\t XR, XR,100,100,\tTAB_CAPTURE | TAB_RECORD},\n",
        "\t// Action buttons: each visible on its own tab only.\n"
        "\t{IDC_CAPTURE,\t XR, XR,100,100,\tTAB_CAPTURE},\n"
        "\t{IDC_RECORD,\t XR, XR,100,100,\tTAB_RECORD},\n"
        "\t// Explicit capture finalization button; shares the lower-right slot\n"
        "\t// with Cancel, which remains visible only on the Record tab.\n"
        "\t{IDC_END_CAPTURE, XR, XR,100,100,\tTAB_CAPTURE},\n"
        "\t{IDCANCEL,\t\t XR, XR,100,100,\tTAB_RECORD},\n")
    replace_once(root, "DVToolsDlg.cpp",
        "\tON_BN_CLICKED(IDC_CAPTURE, OnCapture)\n\tON_BN_CLICKED(IDC_RECORD, OnRecord)\n",
        "\tON_BN_CLICKED(IDC_CAPTURE, OnCapture)\n\tON_BN_CLICKED(IDC_END_CAPTURE, OnEndCapture)\n\tON_BN_CLICKED(IDC_RECORD, OnRecord)\n")
    replace_once(root, "DVToolsDlg.cpp",
        "/* OnCancel -- suppress the default Escape/Cancel behaviour that would close the\n"
        " * dialog.  Instead, reinitialise the pipeline to the idle state for the active tab.\n"
        " */\nvoid CDVToolsDlg::OnCancel()\n{\n\tInitVideo();\n}\n",
        "/* OnCancel -- suppress the default Escape/Cancel behaviour that would close the\n"
        " * dialog.  On Capture, route through End Capture so the AVI is finalized first.\n"
        " */\nvoid CDVToolsDlg::OnCancel()\n{\n"
        "\tif (m_toolTab.GetCurSel() == 0 &&\n"
        "\t\t(m_video.GetState() == CDV::Capturing || m_video.GetState() == CDV::CapturePaused)) {\n"
        "\t\tOnEndCapture();\n\t\treturn;\n\t}\n\tInitVideo();\n}\n")
    replace_once(root, "DVToolsDlg.cpp",
        " *   Capturing      -> StopCapturing()   (pause; output file is flushed/closed)\n",
        " *   Capturing      -> StopCapturing()   (pause; End Capture performs guaranteed finalization)\n")
    replace_once(root, "DVToolsDlg.cpp",
        '"Capturing...  Press <Capture> for pause."',
        '"Capturing... <Capture>=Pause, <End Capture>=Finalize."')
    replace_once(root, "DVToolsDlg.cpp",
        '"Paused... Press <Capture> for Capturing."',
        '"Paused... <Capture>=Resume, <End Capture>=Finalize."')

    marker = "\n/* OnRecord -- toggle button handler for the Record tab.\n"
    handler = r'''

/* OnEndCapture -- explicitly finish the current capture session.
 * Destroy() stops input, wakes and joins CapturingThread, and destroys
 * CAVIWriter. CAVIWriter sends EndOfStream to the AVI mux and waits for
 * graph completion so the AVI index is committed before this call returns.
 */
void CDVToolsDlg::OnEndCapture()
{
	if (m_toolTab.GetCurSel() != 0) return;

	int state = m_video.GetState();
	if (state != CDV::Capturing && state != CDV::CapturePaused) {
		InitVideo();
		return;
	}

	KillTimer(1);
	CWnd *captureButton = GetDlgItem(IDC_CAPTURE);
	CWnd *endButton = GetDlgItem(IDC_END_CAPTURE);
	if (captureButton) captureButton->EnableWindow(FALSE);
	if (endButton) endButton->EnableWindow(FALSE);

	m_status.SetWindowText("Finalizing AVI and writing index...");
	UpdateWindow();

	TRY {
		m_video.Destroy();
		InitVideo();
		m_status.SetWindowText("Capture ended. AVI finalized; ready for next capture.");
	}
	CATCH_ALL(e) {
		Exception2Status(e);
	}
	END_CATCH_ALL;

	if (captureButton) captureButton->EnableWindow(TRUE);
	if (endButton) endButton->EnableWindow(TRUE);
}
'''
    replace_once(root, "DVToolsDlg.cpp", marker, handler + marker)
    print("WinDV End Capture patch applied successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
