from __future__ import annotations

from pathlib import Path

import pytest

from better11.unattend import FirstLogonCommand, UnattendBuilder


def test_unattend_builder_validates_required_fields() -> None:
    builder = UnattendBuilder()
    builder.add_local_account("Deployer")
    with pytest.raises(ValueError):
        builder.to_xml_string()


def test_unattend_builder_exports_expected_elements(tmp_path: Path) -> None:
    builder = UnattendBuilder(language="en-GB", time_zone="GMT Standard Time", computer_name="B11-DEPLOY")
    builder.set_product_key("AAAAA-BBBBB-CCCCC-DDDDD-EEEEE")
    builder.add_local_account(
        "DeployAdmin",
        password="Sup3rS3cret!",
        groups=["Administrators", "Users"],
        auto_logon=True,
    )
    builder.add_first_logon_command(
        order=2,
        command="cmd /c echo ready",
        description="Signal readiness",
    )

    output = builder.export(tmp_path / "unattend.xml")
    content = output.read_text()

    assert "DeployAdmin" in content
    assert "AAAAA-BBBBB-CCCCC-DDDDD-EEEEE" in content
    assert "GMT Standard Time" in content
    assert "B11-DEPLOY" in content
    assert "Signal readiness" in content


def test_templates_populate_defaults() -> None:
    builder = UnattendBuilder.workstation_template(product_key="AAAAA-BBBBB-CCCCC-DDDDD-EEEEE")
    xml = builder.to_xml_string()

    assert "Deployment ready" in xml
    assert "Administrator" in xml
    assert "Pacific Standard Time" in xml

    lab_builder = UnattendBuilder.lab_template(product_key="AAAAA-BBBBB-CCCCC-DDDDD-EEEEE")
    lab_xml = lab_builder.to_xml_string()

    assert "LabAdmin" in lab_xml
    assert "Get-ComputerInfo" in lab_xml
    assert "UTC" in lab_xml


def test_first_logon_command_validation() -> None:
    with pytest.raises(ValueError):
        FirstLogonCommand(order=0, command="cmd /c echo bad order")
    with pytest.raises(ValueError):
        FirstLogonCommand(order=1, command="")
