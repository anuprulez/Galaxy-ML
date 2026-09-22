"""Register the installed source environment for local Planemo tool tests."""

import os
from importlib.metadata import version
from pathlib import Path
import shlex
import sys
from xml.etree import ElementTree as ET


def main():
    root = Path(__file__).resolve().parents[1]
    macros = ET.parse(root / 'galaxy_ml/tools/main_macros.xml')
    package_version = macros.find("token[@name='@GALAXY_ML_VERSION@']").text
    python_version = macros.find(
        "xml[@name='python_requirements']/requirements/"
        "requirement[.='python']").get('version')
    actual_python = f'{sys.version_info.major}.{sys.version_info.minor}'
    if actual_python != python_version:
        raise SystemExit(f'Use Python {python_version}, not {actual_python}.')
    if version('Galaxy-ML') != package_version:
        raise SystemExit(
            'Install this checkout with python -m pip install -e .')

    directory = root / '.planemo-local'
    packages = directory / 'dependencies'
    # Explicit PATH resolution also works when Galaxy runs in its own venv.
    executable_dir = shlex.quote(str(Path(sys.executable).parent))
    environment = f'export PATH={executable_dir}:"$PATH"\n'
    for name, required_version in (
            ('python', python_version), ('Galaxy-ML', package_version)):
        destination = packages / name / required_version
        destination.mkdir(parents=True, exist_ok=True)
        (destination / 'env.sh').write_text(environment)

    resolvers = ET.Element('dependency_resolvers')
    ET.SubElement(resolvers, 'galaxy_packages', base_path=os.fspath(packages))
    config = directory / 'dependency_resolvers.xml'
    ET.ElementTree(resolvers).write(config, encoding='unicode')
    print(config)


if __name__ == '__main__':
    main()
