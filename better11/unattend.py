"""Utilities for generating Windows unattend (answer) files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom

NS = "urn:schemas-microsoft-com:unattend"
ET.register_namespace("", NS)


@dataclass
class LocaleProfile:
    """Regional settings for an answer file."""

    language: str
    keyboard: str
    timezone: str


@dataclass
class UserAccount:
    """Represents a local account to create during OOBE."""

    username: str
    password: Optional[str] = None
    display_name: Optional[str] = None
    groups: List[str] = field(default_factory=lambda: ["Administrators"])


@dataclass
class FirstLogonCommand:
    """Commands to run at first logon."""

    command: str
    description: Optional[str] = None
    order: int = 1


@dataclass
class OobeOptions:
    """Configuration for the OOBE experience."""

    hide_eula: bool = True
    hide_wireless_setup: bool = False
    network_location: str = "Work"
    protect_your_pc: str = "3"  # 1 = recommended, 2 = updates only, 3 = off


class UnattendBuilder:
    """Builds unattend.xml files for Windows deployments."""

    def __init__(
        self,
        *,
        product_key: Optional[str] = None,
        locale: Optional[LocaleProfile] = None,
        computer_name: str = "Better11",
        administrator: str = "Administrator",
        administrator_password: Optional[str] = None,
        autologon_count: int = 1,
        oobe_options: Optional[OobeOptions] = None,
        registered_owner: Optional[str] = None,
        registered_organization: Optional[str] = None,
    ) -> None:
        self.product_key = product_key
        self.locale = locale or LocaleProfile(language="en-US", keyboard="en-US", timezone="UTC")
        self.computer_name = computer_name
        self.administrator = administrator
        self.administrator_password = administrator_password
        self.autologon_count = autologon_count
        self.oobe_options = oobe_options or OobeOptions()
        self.registered_owner = registered_owner
        self.registered_organization = registered_organization
        self.local_accounts: List[UserAccount] = []
        self.first_logon_commands: List[FirstLogonCommand] = []
        self.run_synchronous_commands: List[str] = []

    # Fluent configuration helpers
    def with_product_key(self, key: str) -> "UnattendBuilder":
        self.product_key = key
        return self

    def with_locale(self, language: str, *, keyboard: Optional[str] = None, timezone: Optional[str] = None) -> "UnattendBuilder":
        self.locale = LocaleProfile(language=language, keyboard=keyboard or language, timezone=timezone or self.locale.timezone)
        return self

    def with_computer_name(self, name: str) -> "UnattendBuilder":
        self.computer_name = name
        return self

    def with_administrator(self, username: str, *, password: Optional[str] = None) -> "UnattendBuilder":
        self.administrator = username
        self.administrator_password = password
        return self

    def with_autologon_count(self, count: int) -> "UnattendBuilder":
        self.autologon_count = count
        return self

    def with_oobe_options(
        self,
        *,
        hide_eula: Optional[bool] = None,
        hide_wireless_setup: Optional[bool] = None,
        network_location: Optional[str] = None,
        protect_your_pc: Optional[str] = None,
    ) -> "UnattendBuilder":
        self.oobe_options = OobeOptions(
            hide_eula=hide_eula if hide_eula is not None else self.oobe_options.hide_eula,
            hide_wireless_setup=hide_wireless_setup if hide_wireless_setup is not None else self.oobe_options.hide_wireless_setup,
            network_location=network_location or self.oobe_options.network_location,
            protect_your_pc=protect_your_pc or self.oobe_options.protect_your_pc,
        )
        return self

    def with_registration(self, *, owner: Optional[str] = None, organization: Optional[str] = None) -> "UnattendBuilder":
        self.registered_owner = owner or self.registered_owner
        self.registered_organization = organization or self.registered_organization
        return self

    def add_user(self, username: str, *, password: Optional[str] = None, display_name: Optional[str] = None, groups: Optional[Iterable[str]] = None) -> "UnattendBuilder":
        self.local_accounts.append(
            UserAccount(
                username=username,
                password=password,
                display_name=display_name,
                groups=list(groups) if groups is not None else ["Users"],
            )
        )
        return self

    def add_first_logon_command(self, command: str, *, description: Optional[str] = None) -> "UnattendBuilder":
        order = len(self.first_logon_commands) + 1
        self.first_logon_commands.append(FirstLogonCommand(command=command, description=description, order=order))
        return self

    def add_post_setup_command(self, command: str) -> "UnattendBuilder":
        self.run_synchronous_commands.append(command)
        return self

    # Templates
    @classmethod
    def english_workstation(
        cls, *,
        admin_password: Optional[str],
        product_key: Optional[str] = None,
        first_logon_commands: Optional[Iterable[str]] = None,
    ) -> "UnattendBuilder":
        builder = cls(product_key=product_key, administrator="Administrator", administrator_password=admin_password)
        builder.with_locale("en-US", keyboard="en-US", timezone="Pacific Standard Time")
        if first_logon_commands:
            for cmd in first_logon_commands:
                builder.add_first_logon_command(cmd)
        return builder

    @classmethod
    def lab_template(
        cls,
        *,
        admin_password: Optional[str],
        timezone: str = "UTC",
        product_key: Optional[str] = None,
    ) -> "UnattendBuilder":
        builder = cls(product_key=product_key, administrator="lab-admin", administrator_password=admin_password)
        builder.with_locale("en-US", keyboard="en-US", timezone=timezone)
        builder.add_first_logon_command("powershell -ExecutionPolicy Bypass -File C:\\Scripts\\setup.ps1", description="Lab bootstrap")
        builder.add_post_setup_command("wpeutil reboot")
        return builder

    @classmethod
    def kiosk_template(
        cls,
        *,
        kiosk_user: str = "kiosk",
        kiosk_password: str = "P@ssw0rd!",
        shell_command: Optional[str] = None,
        timezone: str = "UTC",
    ) -> "UnattendBuilder":
        builder = cls(administrator=kiosk_user, administrator_password=kiosk_password, autologon_count=999)
        builder.with_locale("en-US", timezone=timezone)
        builder.with_oobe_options(hide_eula=True, hide_wireless_setup=True, network_location="Other", protect_your_pc="3")
        builder.add_first_logon_command(
            shell_command or "explorer.exe",
            description="Launch kiosk shell",
        )
        return builder

    def _validate(self) -> None:
        missing: List[str] = []
        if not self.locale.language:
            missing.append("locale language")
        if not self.locale.timezone:
            missing.append("timezone")
        if not self.administrator:
            missing.append("administrator username")
        if self.autologon_count < 1:
            raise ValueError("autologon count must be at least 1")
        if self.oobe_options.network_location not in {"Home", "Work", "Other"}:
            raise ValueError("network location must be one of Home, Work, Other")
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

    def build_tree(self) -> ET.Element:
        self._validate()

        root = ET.Element(ET.QName(NS, "unattend"))

        # windowsPE pass for setup and localization
        settings_pe = ET.SubElement(root, "settings", {"pass": "windowsPE"})
        intl_component = self._intl_component()
        settings_pe.append(intl_component)
        if self.product_key:
            settings_pe.append(self._setup_component())

        # specialize pass for machine identity
        settings_specialize = ET.SubElement(root, "settings", {"pass": "specialize"})
        settings_specialize.append(self._shell_setup_component(include_accounts=False))

        # oobeSystem pass for accounts and first logon actions
        settings_oobe = ET.SubElement(root, "settings", {"pass": "oobeSystem"})
        settings_oobe.append(self._shell_setup_component(include_accounts=True))

        return root

    def _intl_component(self) -> ET.Element:
        component = ET.Element(
            "component",
            {
                "name": "Microsoft-Windows-International-Core-WinPE",
                "processorArchitecture": "amd64",
                "publicKeyToken": "31bf3856ad364e35",
                "language": "neutral",
                "versionScope": "nonSxS",
            },
        )
        ET.SubElement(component, "SetupUILanguage").append(self._simple_element("UILanguage", self.locale.language))
        ET.SubElement(component, "InputLocale").text = self.locale.keyboard
        ET.SubElement(component, "SystemLocale").text = self.locale.language
        ET.SubElement(component, "UILanguage").text = self.locale.language
        ET.SubElement(component, "UserLocale").text = self.locale.language
        return component

    def _setup_component(self) -> ET.Element:
        component = ET.Element(
            "component",
            {
                "name": "Microsoft-Windows-Setup",
                "processorArchitecture": "amd64",
                "publicKeyToken": "31bf3856ad364e35",
                "language": "neutral",
                "versionScope": "nonSxS",
            },
        )
        user_data = ET.SubElement(component, "UserData")
        ET.SubElement(user_data, "ProductKey").append(self._simple_element("Key", self.product_key or ""))
        ET.SubElement(user_data, "AcceptEula").text = "true"
        return component

    def _shell_setup_component(self, *, include_accounts: bool) -> ET.Element:
        component = ET.Element(
            "component",
            {
                "name": "Microsoft-Windows-Shell-Setup",
                "processorArchitecture": "amd64",
                "publicKeyToken": "31bf3856ad364e35",
                "language": "neutral",
                "versionScope": "nonSxS",
            },
        )
        ET.SubElement(component, "TimeZone").text = self.locale.timezone
        ET.SubElement(component, "ComputerName").text = self.computer_name

        if self.registered_owner:
            ET.SubElement(component, "RegisteredOwner").text = self.registered_owner
        if self.registered_organization:
            ET.SubElement(component, "RegisteredOrganization").text = self.registered_organization

        if include_accounts:
            self._append_accounts(component)
            self._append_first_logon_commands(component)
            self._append_oobe(component)

        if self.run_synchronous_commands:
            run_sync = ET.SubElement(component, "RunSynchronous")
            for order, command in enumerate(self.run_synchronous_commands, start=1):
                item = ET.SubElement(run_sync, "RunSynchronousCommand")
                ET.SubElement(item, "Order").text = str(order)
                ET.SubElement(item, "Path").text = command
                ET.SubElement(item, "Description").text = f"Setup command {order}"

        return component

    def _append_accounts(self, component: ET.Element) -> None:
        auto_logon = ET.SubElement(component, "AutoLogon")
        ET.SubElement(auto_logon, "Enabled").text = "true"
        ET.SubElement(auto_logon, "LogonCount").text = str(self.autologon_count)
        ET.SubElement(auto_logon, "Username").text = self.administrator
        if self.administrator_password:
            password_elem = ET.SubElement(auto_logon, "Password")
            ET.SubElement(password_elem, "Value").text = self.administrator_password

        user_accounts = ET.SubElement(component, "UserAccounts")
        local_accounts_elem = ET.SubElement(user_accounts, "LocalAccounts")

        admin_account = ET.SubElement(local_accounts_elem, "LocalAccount")
        ET.SubElement(admin_account, "Name").text = self.administrator
        ET.SubElement(admin_account, "Group").text = "Administrators"
        if self.administrator_password:
            admin_password = ET.SubElement(admin_account, "Password")
            ET.SubElement(admin_password, "Value").text = self.administrator_password

        for account in self.local_accounts:
            elem = ET.SubElement(local_accounts_elem, "LocalAccount")
            ET.SubElement(elem, "Name").text = account.username
            ET.SubElement(elem, "Group").text = ",".join(account.groups)
            if account.display_name:
                ET.SubElement(elem, "DisplayName").text = account.display_name
            if account.password:
                pwd = ET.SubElement(elem, "Password")
                ET.SubElement(pwd, "Value").text = account.password

    def _append_first_logon_commands(self, component: ET.Element) -> None:
        if not self.first_logon_commands:
            return

        first_logon = ET.SubElement(component, "FirstLogonCommands")
        for item in self.first_logon_commands:
            cmd_elem = ET.SubElement(first_logon, "SynchronousCommand")
            ET.SubElement(cmd_elem, "Order").text = str(item.order)
            if item.description:
                ET.SubElement(cmd_elem, "Description").text = item.description
            ET.SubElement(cmd_elem, "CommandLine").text = item.command

    def _append_oobe(self, component: ET.Element) -> None:
        oobe = ET.SubElement(component, "OOBE")
        ET.SubElement(oobe, "HideEULAPage").text = str(self.oobe_options.hide_eula).lower()
        ET.SubElement(oobe, "HideWirelessSetupInOOBE").text = str(self.oobe_options.hide_wireless_setup).lower()
        ET.SubElement(oobe, "NetworkLocation").text = self.oobe_options.network_location
        ET.SubElement(oobe, "ProtectYourPC").text = self.oobe_options.protect_your_pc

    @staticmethod
    def _simple_element(name: str, value: str) -> ET.Element:
        elem = ET.Element(name)
        elem.text = value
        return elem

    def to_xml_string(self) -> str:
        tree = self.build_tree()
        xml_bytes = ET.tostring(tree, encoding="utf-8")
        parsed = minidom.parseString(xml_bytes)
        return parsed.toprettyxml(indent="  ")

    def export(self, path: Path | str, *, writer: Optional[Callable[[Path, str], None]] = None) -> Path:
        """Write the unattend XML to ``path``.

        The ``writer`` callback can be injected by tests to avoid touching disk.
        """
        output_path = Path(path)
        xml_text = self.to_xml_string()
        if writer is None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(xml_text, encoding="utf-8")
        else:
            writer(output_path, xml_text)
        return output_path
