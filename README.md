# Better11
An all around windows 11 system enhancer that includes live and offline image editing and application downloader/installer

## Unattend answer file generation
Better11 now ships a deployment helper that builds Windows answer files for unattended setup. The `deploy unattend` command renders `unattend.xml` using the `UnattendBuilder` defaults (English locale, UTC timezone, Better11 computer name) or the options you provide. When running from the repository, set `PYTHONPATH=src` so Python can locate the package.

Create a US workstation unattend with a specific timezone and administrator password:

```bash
PYTHONPATH=src python -m better11.cli deploy unattend ./out/unattend.xml \
  --language en-US \
  --timezone "Pacific Standard Time" \
  --admin-password "P@ssw0rd!" \
  --first-logon-command "powershell -ExecutionPolicy Bypass -File C:\\Scripts\\postinstall.ps1" \
  --setup-command "wpeutil reboot" \
  --user "it-support:Temp!234:Administrators,Remote Desktop Users"
```

To target a localized deployment you can override keyboard and language while reusing templates from Python code:

You can also shape the OOBE experience and networking posture directly from the CLI by adding options such as:

```bash
  --network-location Work \
  --hide-eula \
  --protect-pc 3 \
  --autologon-count 3
```

During testing, `--setup-command` injects run-synchronous steps into the specialize phase (for example to rearm imaging or drop tools), while `--user` lets you pre-provision local operators with group assignments.

```python
from better11.unattend import UnattendBuilder

builder = UnattendBuilder.english_workstation(
    admin_password="P@ssw0rd!",
    first_logon_commands=["Install-Choco.ps1", "Enable-RemoteDesktop.ps1"],
)
builder.with_locale("fr-FR", keyboard="fr-FR", timezone="Romance Standard Time")
builder.add_user("it-ops", password="Temporary!23", groups=["Administrators", "Remote Desktop Users"])
builder.export("./out/unattend-fr.xml")

# Build a kiosk-friendly profile that auto-logs on and launches a shell
kiosk_builder = UnattendBuilder.kiosk_template(shell_command="C:\\Apps\\KioskShell.exe")
kiosk_builder.export("./out/kiosk-unattend.xml")
```

The generated `unattend.xml` can be dropped alongside your boot media or injected during the capture/apply process when preparing offline WIM images. Pair the file with your existing Better11 capture/apply steps so that the image boots directly into the configured desktop with post-setup commands already queued.

## CLI help

```bash
PYTHONPATH=src python -m better11.cli deploy unattend --help
```
