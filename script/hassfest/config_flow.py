"""Generate config flow file."""
import json
from typing import Dict

from .model import Integration, Config

BASE = """
\"\"\"Automatically generated by hassfest.

To update, run python3 -m script.hassfest
\"\"\"


FLOWS = {}
""".strip()


def validate_integration(integration: Integration):
    """Validate we can load config flow without installing requirements."""
    if not (integration.path / "config_flow.py").is_file():
        integration.add_error(
            "config_flow", "Config flows need to be defined in the file config_flow.py"
        )

    # Currently not require being able to load config flow without
    # installing requirements.
    # try:
    #     integration.import_pkg('config_flow')
    # except ImportError as err:
    #     integration.add_error(
    #         'config_flow',
    #         "Unable to import config flow: {}. Config flows should be able "
    #         "to be imported without installing requirements.".format(err))
    #     return

    # if integration.domain not in config_entries.HANDLERS:
    #     integration.add_error(
    #         'config_flow',
    #         "Importing the config flow platform did not register a config "
    #         "flow handler.")


def generate_and_validate(integrations: Dict[str, Integration]):
    """Validate and generate config flow data."""
    domains = []

    for domain in sorted(integrations):
        integration = integrations[domain]

        if not integration.manifest:
            continue

        config_flow = integration.manifest.get("config_flow")

        if not config_flow:
            continue

        validate_integration(integration)

        domains.append(domain)

    return BASE.format(json.dumps(domains, indent=4))


def validate(integrations: Dict[str, Integration], config: Config):
    """Validate config flow file."""
    config_flow_path = config.root / "homeassistant/generated/config_flows.py"
    config.cache["config_flow"] = content = generate_and_validate(integrations)

    with open(str(config_flow_path), "r") as fp:
        if fp.read().strip() != content:
            config.add_error(
                "config_flow",
                "File config_flows.py is not up to date. "
                "Run python3 -m script.hassfest",
                fixable=True,
            )
        return


def generate(integrations: Dict[str, Integration], config: Config):
    """Generate config flow file."""
    config_flow_path = config.root / "homeassistant/generated/config_flows.py"
    with open(str(config_flow_path), "w") as fp:
        fp.write(config.cache["config_flow"] + "\n")