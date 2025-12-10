from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET
from xml.dom import minidom


UNATTEND_NS = "urn:schemas-microsoft-com:unattend"
WCM_NS = "http://schemas.microsoft.com/WMIConfig/2002/State"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"

ET.register_namespace("", UNATTEND_NS)
ET.register_namespace("wcm", WCM_NS)
ET.register_namespace("xsi", XSI_NS)


@dataclass
class LocalAccount:
    """Represents a local account configured during setup."""

    name: str
    password: str | None = None
    display_name: str | None = None
    groups: list[str] = field(default_factory=lambda: ["Administrators"])
    auto_logon: bool = False

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Local account name is required")
        if any(not group for group in self.groups):
            raise ValueError("Group names must be non-empty")


@dataclass
class FirstLogonCommand:
    """Represents a synchronous first-logon command."""

    order: int
    command: str
    description: str | None = None

    def __post_init__(self) -> None:
        if self.order < 1:
            raise ValueError("Command order must be 1 or greater")
        if not self.command:
            raise ValueError("Command text is required")


class UnattendBuilder:
    """Builds a Windows unattend XML document."""

    def __init__(
        self,
        *,
        language: str = "en-US",
        input_locale: str = "en-US",
        time_zone: str = "Pacific Standard Time",
        computer_name: str | None = None,
    ) -> None:
        self.language = language
        self.input_locale = input_locale
        self.time_zone = time_zone
        self.computer_name = computer_name
        self._product_key: str | None = None
        self._accept_eula: bool = True
        self._admin_password: str | None = None
        self._accounts: list[LocalAccount] = []
        self._first_logon: list[FirstLogonCommand] = []

    @classmethod
    def workstation_template(
        cls,
        *,
        product_key: str,
        admin_user: str = "Administrator",
        admin_password: str | None = None,
        language: str = "en-US",
        time_zone: str = "Pacific Standard Time",
    ) -> "UnattendBuilder":
        builder = cls(language=language, time_zone=time_zone)
        builder.set_product_key(product_key)
        builder.set_admin_password(admin_password)
        builder.add_local_account(admin_user, password=admin_password, auto_logon=True)
        builder.add_first_logon_command(
            order=1,
            command="PowerShell -ExecutionPolicy Bypass -Command \"Write-Host 'Deployment ready'\"",
            description="Confirm deployment readiness",
        )
        return builder

    @classmethod
    def lab_template(
        cls,
        *,
        product_key: str,
        language: str = "en-US",
        time_zone: str = "UTC",
    ) -> "UnattendBuilder":
        builder = cls(language=language, time_zone=time_zone)
        builder.set_product_key(product_key)
        builder.add_local_account("LabAdmin", password="P@ssw0rd!", auto_logon=True)
        builder.add_first_logon_command(
            order=1,
            command="PowerShell -Command \"Get-ComputerInfo | Out-File C:\\setup.log\"",
            description="Capture baseline inventory",
        )
        return builder

    def set_product_key(self, product_key: str) -> "UnattendBuilder":
        if not product_key:
            raise ValueError("Product key is required")
        self._product_key = product_key
        return self

    def set_admin_password(self, password: str | None) -> "UnattendBuilder":
        if password is not None and not password:
            raise ValueError("Administrator password cannot be an empty string")
        self._admin_password = password
        return self

    def add_local_account(
        self,
        name: str,
        *,
        password: str | None = None,
        display_name: str | None = None,
        groups: Iterable[str] | None = None,
        auto_logon: bool = False,
    ) -> "UnattendBuilder":
        account = LocalAccount(
            name=name,
            password=password,
            display_name=display_name,
            groups=list(groups) if groups is not None else ["Administrators"],
            auto_logon=auto_logon,
        )
        self._accounts.append(account)
        return self

    def add_first_logon_command(
        self, *, order: int, command: str, description: str | None = None
    ) -> "UnattendBuilder":
        command_obj = FirstLogonCommand(order=order, command=command, description=description)
        self._first_logon.append(command_obj)
        return self

    def _validate(self) -> None:
        if not self._product_key:
            raise ValueError("Product key must be provided before building unattend.xml")
        if not self.language:
            raise ValueError("Language must be specified")
        if not self.time_zone:
            raise ValueError("Time zone must be specified")
        if not self._accounts:
            raise ValueError("At least one local account is required")

    def _create_component(self, settings: ET.Element, name: str) -> ET.Element:
        return ET.SubElement(
            settings,
            "{urn:schemas-microsoft-com:unattend}component",
            {
                "name": name,
                "processorArchitecture": "amd64",
                "publicKeyToken": "31bf3856ad364e35",
                "language": "neutral",
                "versionScope": "nonSxS",
            },
        )

    def _append_windows_pe(self, root: ET.Element) -> None:
        settings = ET.SubElement(root, "{urn:schemas-microsoft-com:unattend}settings", {"pass": "windowsPE"})

        international = self._create_component(settings, "Microsoft-Windows-International-Core-WinPE")
        ET.SubElement(international, "{urn:schemas-microsoft-com:unattend}InputLocale").text = self.input_locale
        ET.SubElement(international, "{urn:schemas-microsoft-com:unattend}SystemLocale").text = self.language
        ET.SubElement(international, "{urn:schemas-microsoft-com:unattend}UILanguage").text = self.language
        ET.SubElement(international, "{urn:schemas-microsoft-com:unattend}UserLocale").text = self.language

        setup = self._create_component(settings, "Microsoft-Windows-Setup")
        user_data = ET.SubElement(setup, "{urn:schemas-microsoft-com:unattend}UserData")
        ET.SubElement(user_data, "{urn:schemas-microsoft-com:unattend}AcceptEula").text = str(self._accept_eula).lower()
        product_key = ET.SubElement(user_data, "{urn:schemas-microsoft-com:unattend}ProductKey")
        ET.SubElement(product_key, "{urn:schemas-microsoft-com:unattend}Key").text = self._product_key

    def _append_specialize(self, root: ET.Element) -> None:
        settings = ET.SubElement(root, "{urn:schemas-microsoft-com:unattend}settings", {"pass": "specialize"})
        shell_setup = self._create_component(settings, "Microsoft-Windows-Shell-Setup")
        if self.computer_name:
            ET.SubElement(shell_setup, "{urn:schemas-microsoft-com:unattend}ComputerName").text = self.computer_name
        ET.SubElement(shell_setup, "{urn:schemas-microsoft-com:unattend}TimeZone").text = self.time_zone

    def _append_oobe_system(self, root: ET.Element) -> None:
        settings = ET.SubElement(root, "{urn:schemas-microsoft-com:unattend}settings", {"pass": "oobeSystem"})
        shell_setup = self._create_component(settings, "Microsoft-Windows-Shell-Setup")

        oobe = ET.SubElement(shell_setup, "{urn:schemas-microsoft-com:unattend}OOBE")
        ET.SubElement(oobe, "{urn:schemas-microsoft-com:unattend}HideEULAPage").text = "true"
        ET.SubElement(oobe, "{urn:schemas-microsoft-com:unattend}NetworkLocation").text = "Work"
        ET.SubElement(oobe, "{urn:schemas-microsoft-com:unattend}ProtectYourPC").text = "3"

        user_accounts = ET.SubElement(shell_setup, "{urn:schemas-microsoft-com:unattend}UserAccounts")
        if self._admin_password:
            admin_pw = ET.SubElement(user_accounts, "{urn:schemas-microsoft-com:unattend}AdministratorPassword")
            ET.SubElement(admin_pw, "{urn:schemas-microsoft-com:unattend}Value").text = self._admin_password
            ET.SubElement(admin_pw, "{urn:schemas-microsoft-com:unattend}PlainText").text = "true"

        local_accounts = ET.SubElement(user_accounts, "{urn:schemas-microsoft-com:unattend}LocalAccounts")
        for account in self._accounts:
            local_account = ET.SubElement(
                local_accounts,
                "{urn:schemas-microsoft-com:unattend}LocalAccount",
                {"{http://schemas.microsoft.com/WMIConfig/2002/State}action": "add"},
            )
            ET.SubElement(local_account, "{urn:schemas-microsoft-com:unattend}Name").text = account.name
            ET.SubElement(local_account, "{urn:schemas-microsoft-com:unattend}Group").text = ";".join(account.groups)
            if account.display_name:
                ET.SubElement(local_account, "{urn:schemas-microsoft-com:unattend}DisplayName").text = account.display_name
            if account.password:
                password_node = ET.SubElement(local_account, "{urn:schemas-microsoft-com:unattend}Password")
                ET.SubElement(password_node, "{urn:schemas-microsoft-com:unattend}Value").text = account.password
                ET.SubElement(password_node, "{urn:schemas-microsoft-com:unattend}PlainText").text = "true"

            if account.auto_logon:
                auto_logon = ET.SubElement(shell_setup, "{urn:schemas-microsoft-com:unattend}AutoLogon")
                ET.SubElement(auto_logon, "{urn:schemas-microsoft-com:unattend}Username").text = account.name
                ET.SubElement(auto_logon, "{urn:schemas-microsoft-com:unattend}Enabled").text = "true"
                ET.SubElement(auto_logon, "{urn:schemas-microsoft-com:unattend}LogonCount").text = "5"
                if account.password:
                    password_node = ET.SubElement(auto_logon, "{urn:schemas-microsoft-com:unattend}Password")
                    ET.SubElement(password_node, "{urn:schemas-microsoft-com:unattend}Value").text = account.password
                    ET.SubElement(password_node, "{urn:schemas-microsoft-com:unattend}PlainText").text = "true"

        if self._first_logon:
            commands = ET.SubElement(shell_setup, "{urn:schemas-microsoft-com:unattend}FirstLogonCommands")
            for command in sorted(self._first_logon, key=lambda c: c.order):
                sync_cmd = ET.SubElement(
                    commands,
                    "{urn:schemas-microsoft-com:unattend}SynchronousCommand",
                    {"{http://schemas.microsoft.com/WMIConfig/2002/State}action": "add"},
                )
                ET.SubElement(sync_cmd, "{urn:schemas-microsoft-com:unattend}Order").text = str(command.order)
                ET.SubElement(sync_cmd, "{urn:schemas-microsoft-com:unattend}CommandLine").text = command.command
                if command.description:
                    ET.SubElement(sync_cmd, "{urn:schemas-microsoft-com:unattend}Description").text = command.description

    def build_tree(self) -> ET.ElementTree:
        self._validate()
        root = ET.Element("{urn:schemas-microsoft-com:unattend}unattend")
        self._append_windows_pe(root)
        self._append_specialize(root)
        self._append_oobe_system(root)
        return ET.ElementTree(root)

    def to_xml_string(self) -> str:
        tree = self.build_tree()
        rough_string = ET.tostring(tree.getroot(), encoding="utf-8")
        return minidom.parseString(rough_string).toprettyxml(indent="  ")

    def export(self, output_path: Path) -> Path:
        xml_content = self.to_xml_string()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(xml_content, encoding="utf-8")
        return output_path
