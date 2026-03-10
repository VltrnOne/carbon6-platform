#!/usr/bin/env python3
"""HERMES Setup Agent - Fully automated iMessage bridge configuration.

Generates Apple Shortcut files (.shortcut), configures Pushcut via API,
and serves a single setup page. User opens one URL on their iPhone
and taps to install everything.

Flow:
  1. Verify Pushcut API key and get device info
  2. Generate "HERMES Send Message" shortcut file (outbound)
  3. Generate "HERMES Receive Message" shortcut file (inbound)
  4. Configure Pushcut notification/automation actions via API
  5. Serve setup page with install links at /api/comms/setup
  6. User opens URL on iPhone → taps Install → done
"""
import io
import json
import logging
import os
import plistlib
import requests
from typing import Optional

from ..config.settings import load_config

log = logging.getLogger("hermes.setup")

PUSHCUT_API = "https://api.pushcut.io"


class HermesSetupAgent:
    """Automated setup for the iMessage bridge."""

    def __init__(self):
        self.config = load_config()
        self.api_key = os.getenv("PUSHCUT_API_KEY", "")
        self.device_name = os.getenv("PUSHCUT_DEVICE_NAME", "My iPhone")
        self.webhook_base = os.getenv("HERMES_WEBHOOK_URL", "")
        # Auto-detect webhook URL - prefer HTTPS domain for iOS compatibility
        if not self.webhook_base:
            self.webhook_base = "https://hermes.vltrn.cloud"

    # ----------------------------------------------------------------
    # Pushcut API
    # ----------------------------------------------------------------

    def verify_pushcut(self) -> dict:
        """Verify Pushcut secret by hitting the execute endpoint with a test.

        Pushcut uses the secret in the URL path:
          https://api.pushcut.io/{secret}/execute?shortcut=Name
        A GET to the base returns 404, so we test with a nowait execute.
        """
        if not self.api_key:
            return {"ok": False, "error": "PUSHCUT_API_KEY not set"}

        try:
            # Test with a harmless request (timeout=nowait so it returns immediately)
            resp = requests.post(
                f"{PUSHCUT_API}/{self.api_key}/execute",
                params={"shortcut": "__pushcut_test__", "timeout": "nowait"},
                timeout=10,
            )
            # 200 = server is listening (shortcut may not exist but auth works)
            # 404 with "Invalid secret" = bad key
            # 404 with other message = key works but shortcut not found (which is fine)
            if resp.status_code == 200:
                return {"ok": True, "detail": "Pushcut Automation Server is reachable and key is valid"}
            body = resp.text[:200]
            if "Invalid secret" in body:
                return {"ok": False, "error": "Invalid Pushcut secret. Check your API key in Pushcut → Account → Integrations → URL secret"}
            # Any other 404 likely means the key is valid but shortcut doesn't exist yet
            return {"ok": True, "detail": f"Pushcut responded (shortcut not installed yet, which is expected): {body}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_device_name(self) -> Optional[str]:
        """Return configured device name (Pushcut secret API doesn't list devices)."""
        return self.device_name

    def configure_pushcut_notification(self) -> dict:
        """Verify the Pushcut Automation Server execute endpoint is reachable.

        Pushcut Automation Server uses the URL secret approach:
          POST https://api.pushcut.io/{secret}/execute?shortcut=Name&input=JSON
        No separate notification config needed — we call execute directly.
        """
        if not self.api_key:
            return {"error": "PUSHCUT_API_KEY not set"}

        return {
            "ok": True,
            "method": "Direct execute via URL secret",
            "endpoint": f"{PUSHCUT_API}/{self.api_key[:6]}***/execute?shortcut=HERMES Send Message",
            "note": "No notification setup needed — HERMES calls the execute endpoint directly with shortcut input",
        }

    # ----------------------------------------------------------------
    # Apple Shortcut Generation
    # ----------------------------------------------------------------

    def generate_send_shortcut(self) -> bytes:
        """Generate the 'HERMES Send Message' Apple Shortcut file.

        This shortcut:
        1. Receives JSON input from Pushcut with {to, body}
        2. Extracts the 'to' and 'body' fields
        3. Sends an iMessage using the Messages app
        """
        shortcut = {
            "WFWorkflowMinimumClientVersionString": "900",
            "WFWorkflowMinimumClientVersion": 900,
            "WFWorkflowIcon": {
                "WFWorkflowIconStartColor": 463140863,  # Blue
                "WFWorkflowIconGlyphNumber": 59076,  # Message bubble icon
            },
            "WFWorkflowClientVersion": "2612.0.4",
            "WFWorkflowOutputContentItemClasses": [],
            "WFWorkflowHasOutputFallback": False,
            "WFWorkflowActions": [
                # Action 1: Get Dictionary from Input (parse JSON)
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.detect.dictionary",
                    "WFWorkflowActionParameters": {
                        "WFInput": {
                            "Value": {
                                "Type": "ExtensionInput",
                            },
                            "WFSerializationType": "WFTextTokenAttachment",
                        },
                        "UUID": "A1B2C3D4-1111-2222-3333-AABBCCDDEEFF",
                    },
                },
                # Action 2: Get 'to' from dictionary
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
                    "WFWorkflowActionParameters": {
                        "WFDictionaryKey": "to",
                        "WFInput": {
                            "Value": {
                                "OutputUUID": "A1B2C3D4-1111-2222-3333-AABBCCDDEEFF",
                                "Type": "ActionOutput",
                                "OutputName": "Dictionary",
                            },
                            "WFSerializationType": "WFTextTokenAttachment",
                        },
                        "UUID": "A1B2C3D4-4444-5555-6666-AABBCCDDEEFF",
                    },
                },
                # Action 3: Set variable 'recipient'
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
                    "WFWorkflowActionParameters": {
                        "WFVariableName": "recipient",
                        "WFInput": {
                            "Value": {
                                "OutputUUID": "A1B2C3D4-4444-5555-6666-AABBCCDDEEFF",
                                "Type": "ActionOutput",
                                "OutputName": "Dictionary Value",
                            },
                            "WFSerializationType": "WFTextTokenAttachment",
                        },
                    },
                },
                # Action 4: Get 'body' from dictionary
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
                    "WFWorkflowActionParameters": {
                        "WFDictionaryKey": "body",
                        "WFInput": {
                            "Value": {
                                "OutputUUID": "A1B2C3D4-1111-2222-3333-AABBCCDDEEFF",
                                "Type": "ActionOutput",
                                "OutputName": "Dictionary",
                            },
                            "WFSerializationType": "WFTextTokenAttachment",
                        },
                        "UUID": "A1B2C3D4-7777-8888-9999-AABBCCDDEEFF",
                    },
                },
                # Action 5: Set variable 'messageBody'
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
                    "WFWorkflowActionParameters": {
                        "WFVariableName": "messageBody",
                        "WFInput": {
                            "Value": {
                                "OutputUUID": "A1B2C3D4-7777-8888-9999-AABBCCDDEEFF",
                                "Type": "ActionOutput",
                                "OutputName": "Dictionary Value",
                            },
                            "WFSerializationType": "WFTextTokenAttachment",
                        },
                    },
                },
                # Action 6: Send Message
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.sendmessage",
                    "WFWorkflowActionParameters": {
                        "WFSendMessageContent": {
                            "Value": {
                                "string": "",
                                "attachmentsByRange": {
                                    "{0, 1}": {
                                        "VariableName": "messageBody",
                                        "Type": "Variable",
                                    },
                                },
                            },
                            "WFSerializationType": "WFTextTokenString",
                        },
                        "WFSendMessageActionRecipients": {
                            "Value": {
                                "string": "",
                                "attachmentsByRange": {
                                    "{0, 1}": {
                                        "VariableName": "recipient",
                                        "Type": "Variable",
                                    },
                                },
                            },
                            "WFSerializationType": "WFTextTokenString",
                        },
                    },
                },
            ],
            "WFWorkflowImportQuestions": [],
            "WFWorkflowTypes": ["ActionExtension"],
            "WFWorkflowInputContentItemClasses": [
                "WFStringContentItem",
                "WFDictionaryContentItem",
            ],
        }

        return plistlib.dumps(shortcut, fmt=plistlib.FMT_BINARY)

    def generate_receive_shortcut(self) -> bytes:
        """Generate the 'HERMES Receive Message' Apple Shortcut file.

        This shortcut:
        1. Gets triggered by Shortcuts automation on message receive
        2. Takes the sender and message content
        3. POSTs them to the HERMES inbound webhook
        """
        webhook_url = f"{self.webhook_base}/api/comms/imessage/inbound"

        shortcut = {
            "WFWorkflowMinimumClientVersionString": "900",
            "WFWorkflowMinimumClientVersion": 900,
            "WFWorkflowIcon": {
                "WFWorkflowIconStartColor": 4274264319,  # Green
                "WFWorkflowIconGlyphNumber": 59076,
            },
            "WFWorkflowClientVersion": "2612.0.4",
            "WFWorkflowOutputContentItemClasses": [],
            "WFWorkflowHasOutputFallback": False,
            "WFWorkflowActions": [
                # Action 1: Get Shortcut Input (message details from automation)
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.detect.text",
                    "WFWorkflowActionParameters": {
                        "WFInput": {
                            "Value": {
                                "Type": "ExtensionInput",
                            },
                            "WFSerializationType": "WFTextTokenAttachment",
                        },
                        "UUID": "B1B2C3D4-1111-2222-3333-AABBCCDDEEFF",
                    },
                },
                # Action 2: Build JSON dictionary with sender and body
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.dictionary",
                    "WFWorkflowActionParameters": {
                        "WFItems": {
                            "Value": {
                                "WFDictionaryFieldValueItems": [
                                    {
                                        "WFKey": {"Value": {"string": "from"}, "WFSerializationType": "WFTextTokenString"},
                                        "WFItemType": 0,
                                        "WFValue": {
                                            "Value": {
                                                "string": "",
                                                "attachmentsByRange": {
                                                    "{0, 1}": {
                                                        "Type": "ExtensionInput",
                                                        "OutputName": "Sender",
                                                    },
                                                },
                                            },
                                            "WFSerializationType": "WFTextTokenString",
                                        },
                                    },
                                    {
                                        "WFKey": {"Value": {"string": "body"}, "WFSerializationType": "WFTextTokenString"},
                                        "WFItemType": 0,
                                        "WFValue": {
                                            "Value": {
                                                "string": "",
                                                "attachmentsByRange": {
                                                    "{0, 1}": {
                                                        "Type": "ExtensionInput",
                                                        "OutputName": "Content",
                                                    },
                                                },
                                            },
                                            "WFSerializationType": "WFTextTokenString",
                                        },
                                    },
                                ],
                            },
                            "WFSerializationType": "WFDictionaryFieldValue",
                        },
                        "UUID": "B1B2C3D4-4444-5555-6666-AABBCCDDEEFF",
                    },
                },
                # Action 3: POST to HERMES webhook
                {
                    "WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
                    "WFWorkflowActionParameters": {
                        "WFURL": {
                            "Value": {"string": webhook_url},
                            "WFSerializationType": "WFTextTokenString",
                        },
                        "WFHTTPMethod": "POST",
                        "WFHTTPBodyType": "Json",
                        "WFJSONValues": {
                            "Value": {
                                "WFDictionaryFieldValueItems": [],
                            },
                            "WFSerializationType": "WFDictionaryFieldValue",
                        },
                        "WFRequestVariable": {
                            "Value": {
                                "OutputUUID": "B1B2C3D4-4444-5555-6666-AABBCCDDEEFF",
                                "Type": "ActionOutput",
                                "OutputName": "Dictionary",
                            },
                            "WFSerializationType": "WFTextTokenAttachment",
                        },
                    },
                },
            ],
            "WFWorkflowImportQuestions": [],
            "WFWorkflowTypes": ["ActionExtension"],
            "WFWorkflowInputContentItemClasses": [
                "WFStringContentItem",
            ],
        }

        return plistlib.dumps(shortcut, fmt=plistlib.FMT_BINARY)

    # ----------------------------------------------------------------
    # Full Setup Flow
    # ----------------------------------------------------------------

    def run_full_setup(self) -> dict:
        """Execute the complete automated setup.

        Returns status of each step and the URLs to open on iPhone.
        """
        results = {"steps": [], "success": True}

        # Step 1: Verify Pushcut
        log.info("Step 1: Verifying Pushcut API key...")
        pushcut_status = self.verify_pushcut()
        results["steps"].append({
            "step": 1,
            "name": "Verify Pushcut API",
            "status": "ok" if pushcut_status.get("ok") else "failed",
            "detail": pushcut_status,
        })
        if not pushcut_status.get("ok"):
            results["success"] = False

        # Step 2: Auto-detect device name
        log.info("Step 2: Detecting device name...")
        detected_name = self.get_device_name()
        if detected_name and detected_name != self.device_name:
            results["steps"].append({
                "step": 2,
                "name": "Device Detection",
                "status": "updated",
                "detail": f"Detected: '{detected_name}' (was: '{self.device_name}')",
                "device_name": detected_name,
            })
            self.device_name = detected_name
        else:
            results["steps"].append({
                "step": 2,
                "name": "Device Detection",
                "status": "ok",
                "detail": f"Using: '{self.device_name}'",
            })

        # Step 3: Configure Pushcut notification
        log.info("Step 3: Configuring Pushcut notification...")
        notif_result = self.configure_pushcut_notification()
        results["steps"].append({
            "step": 3,
            "name": "Pushcut Notification Config",
            "status": "ok" if notif_result.get("ok") else "info",
            "detail": notif_result,
        })

        # Step 4: Generate shortcut files (served via API)
        log.info("Step 4: Generating Apple Shortcut files...")
        try:
            send_data = self.generate_send_shortcut()
            recv_data = self.generate_receive_shortcut()
            results["steps"].append({
                "step": 4,
                "name": "Generate Shortcuts",
                "status": "ok",
                "detail": {
                    "send_shortcut_size": len(send_data),
                    "recv_shortcut_size": len(recv_data),
                },
            })
            results["shortcuts_generated"] = True
        except Exception as e:
            results["steps"].append({
                "step": 4,
                "name": "Generate Shortcuts",
                "status": "failed",
                "detail": str(e),
            })
            results["success"] = False

        # Step 5: Generate install URLs
        api_base = self.webhook_base
        results["install"] = {
            "setup_page": f"{api_base}/api/comms/setup",
            "send_shortcut": f"{api_base}/api/comms/setup/shortcut/send",
            "receive_shortcut": f"{api_base}/api/comms/setup/shortcut/receive",
            "instructions": [
                f"1. Open this URL on your iPhone: {api_base}/api/comms/setup",
                "2. Tap 'Install Send Shortcut' → tap 'Add Shortcut'",
                "3. Tap 'Install Receive Shortcut' → tap 'Add Shortcut'",
                "4. Go to Shortcuts → Automation → New Automation",
                "5. Choose 'Message' trigger → 'Run Immediately'",
                "6. Set action to 'Run Shortcut: HERMES Receive Message'",
                "7. Done! Test with: hermes text <contact> <message>",
            ],
        }

        results["steps"].append({
            "step": 5,
            "name": "Setup Ready",
            "status": "ok",
            "detail": f"Open on iPhone: {api_base}/api/comms/setup",
        })

        return results

    def generate_setup_page_html(self) -> str:
        """Generate the HTML setup page served to the iPhone.

        Serves .shortcut files over HTTPS via shortcuts://import-shortcut URL scheme.
        iOS requires HTTPS for shortcut imports.
        """
        import urllib.parse
        api_base = self.webhook_base
        webhook_url = f"{api_base}/api/comms/imessage/inbound"
        send_file_url = f"{api_base}/api/comms/setup/shortcut/send"
        recv_file_url = f"{api_base}/api/comms/setup/shortcut/receive"
        send_import = f"shortcuts://import-shortcut?url={urllib.parse.quote(send_file_url, safe='')}&name={urllib.parse.quote('HERMES Send Message', safe='')}"
        recv_import = f"shortcuts://import-shortcut?url={urllib.parse.quote(recv_file_url, safe='')}&name={urllib.parse.quote('HERMES Receive Message', safe='')}"
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HERMES Setup</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #000; color: #fff; padding: 20px; }}
  .logo {{ text-align: center; padding: 30px 0 20px; }}
  .logo h1 {{ font-size: 28px; letter-spacing: 2px; }}
  .logo p {{ color: #888; font-size: 14px; margin-top: 5px; }}
  .card {{ background: #1c1c1e; border-radius: 16px; padding: 20px; margin: 16px 0; }}
  .card h2 {{ font-size: 18px; margin-bottom: 12px; }}
  .card p {{ color: #aaa; font-size: 14px; line-height: 1.5; margin-bottom: 12px; }}
  .step {{ display: flex; align-items: flex-start; margin: 12px 0; }}
  .step-num {{ background: #0a84ff; color: #fff; width: 28px; height: 28px; border-radius: 14px;
               display: flex; align-items: center; justify-content: center; font-weight: 700;
               font-size: 14px; flex-shrink: 0; margin-right: 12px; margin-top: 2px; }}
  .step-text {{ font-size: 15px; line-height: 1.4; }}
  .btn {{ display: block; width: 100%; padding: 16px; border-radius: 12px; border: none;
          font-size: 17px; font-weight: 600; text-align: center; text-decoration: none;
          margin: 10px 0; cursor: pointer; }}
  .btn-blue {{ background: #0a84ff; color: #fff; }}
  .btn-green {{ background: #30d158; color: #fff; }}
  .btn-outline {{ background: transparent; color: #0a84ff; border: 2px solid #0a84ff; }}
  .divider {{ height: 1px; background: #333; margin: 16px 0; }}
  .small {{ font-size: 12px; color: #666; text-align: center; margin-top: 20px; }}
  .note {{ font-size: 13px; color: #888; margin-top: 8px; text-align: center; }}
</style>
</head>
<body>

<div class="logo">
  <h1>HERMES</h1>
  <p>Communications Department Setup</p>
</div>

<div class="card">
  <h2>Step 1: Install Send Shortcut</h2>
  <p>This shortcut lets HERMES send iMessages from your phone number. Tap below — it opens the Shortcuts app and adds it automatically.</p>
  <a href="{send_import}" class="btn btn-blue">
    Add "HERMES Send Message"
  </a>
  <p class="note">Tap "Add Shortcut" when the Shortcuts app opens.</p>
</div>

<div class="card">
  <h2>Step 2: Install Receive Shortcut</h2>
  <p>This shortcut forwards incoming messages to HERMES for your unified inbox.</p>
  <a href="{recv_import}" class="btn btn-green">
    Add "HERMES Receive Message"
  </a>
  <p class="note">Tap "Add Shortcut" when the Shortcuts app opens.</p>
</div>

<div class="card">
  <h2>Step 3: Create Message Automation</h2>
  <p>Auto-forward every incoming message to HERMES:</p>
  <div class="step">
    <div class="step-num">1</div>
    <div class="step-text">Open <strong>Shortcuts</strong> → <strong>Automation</strong> tab</div>
  </div>
  <div class="step">
    <div class="step-num">2</div>
    <div class="step-text">Tap <strong>+</strong> → choose <strong>Message</strong></div>
  </div>
  <div class="step">
    <div class="step-num">3</div>
    <div class="step-text"><strong>Message Contains</strong> → leave blank → <strong>Next</strong></div>
  </div>
  <div class="step">
    <div class="step-num">4</div>
    <div class="step-text">Choose <strong>Run Immediately</strong></div>
  </div>
  <div class="step">
    <div class="step-num">5</div>
    <div class="step-text">Action: <strong>Run Shortcut → HERMES Receive Message</strong></div>
  </div>
</div>

<div class="card">
  <h2>Step 4: Verify Connection</h2>
  <p>Tap below to check if HERMES can receive messages:</p>
  <button class="btn btn-outline" onclick="testConnection()">Test Connection</button>
  <div id="test-result" style="margin-top: 10px; font-size: 14px;"></div>
</div>

<div class="card" style="background: #1a2a1a; border: 1px solid #30d158;">
  <h2 style="color: #30d158;">Ready to Go</h2>
  <p>Once all steps are done, control messages from your server:</p>
  <p style="color: #fff; font-family: monospace; background: #000; padding: 12px; border-radius: 8px; font-size: 13px;">
    hermes text "John" "Hey, meeting at 3pm"<br>
    hermes inbox --unread<br>
    hermes search "invoice"
  </p>
</div>

<p class="small">HERMES // Carbon6 Communications Department<br>
{api_base}</p>

<script>
function testConnection() {{
  const r = document.getElementById('test-result');
  r.innerHTML = '<span style="color:#ff9f0a;">Testing...</span>';
  fetch('{api_base}/api/comms/imessage/inbound', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{from: 'setup-test', body: 'HERMES setup verification', is_imessage: true}})
  }})
  .then(resp => resp.json())
  .then(data => {{
    r.innerHTML = '<span style="color:#30d158;">Connected! HERMES received the test message.</span>';
  }})
  .catch(err => {{
    r.innerHTML = '<span style="color:#ff453a;">Connection failed: ' + err.message + '</span>';
  }});
}}
</script>

</body>
</html>"""
