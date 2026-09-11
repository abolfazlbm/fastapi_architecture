# Code Generator

Code-generator plugin for producing general business code

- Supports maintaining code-generation business settings and model-column information
- Supports manual and automatic table-import modes for generating general business code
- Supports previewing, writing to disk, and downloading generated output

## plugin type

- Application-level plugin

## Configuration instructions

The `[settings]` section of `plugin.toml` in the plugin directory contains:

```toml
[settings]
CODE_GENERATOR_DOWNLOAD_ZIP_FILENAME = 'fba_generator'
```

The current project's `backend/core/conf.py` already contains these fields:

```python
##################################################
# [ Plugin ] code_generator
##################################################
CODE_GENERATOR_DOWNLOAD_ZIP_FILENAME: str
```

## Setting descriptions

- `CODE_GENERATOR_DOWNLOAD_ZIP_FILENAME`:Controls the filename of the downloaded code-generation archive

## Usage

1. Install and enable the plugin, then restart the backend
2. Maintain business settings and model-column information
3. Run the preview, generation, and download workflow
4. Generated code is written directly to disk; use this only in development

## Uninstall instructions

- After uninstalling, remove related plugin settings and its configuration from `backend/core/conf.py`
- If the project integrates code-generation pages or automation, remove the corresponding integration

## Contact information

- author:`wu-clan`
- Feedback: submit an issue or pull request
