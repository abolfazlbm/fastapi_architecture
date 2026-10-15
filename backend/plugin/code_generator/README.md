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

The following fields are already included in `backend/core/conf.py`:

```python
##################################################
# [ Plugin ] code_generator
##################################################
CODE_GENERATOR_DOWNLOAD_ZIP_FILENAME: str
```

## Configuration options

- `CODE_GENERATOR_DOWNLOAD_ZIP_FILENAME`: Name of the ZIP archive downloaded for generated code

## Usage

1. After installing and enabling the plug-in, restart the backend service
2. Maintain business configuration and model column information
3. Execute the preview, generation and download process
4. The generated code will be written directly to disk and must only be used in the development environment.

## Uninstall instructions

- After uninstalling, remove related plugin settings and its configuration from `backend/core/conf.py`
- If the project integrates code-generation pages or automation, remove the corresponding integration

## Contact information

- author:`wu-clan`
- Feedback: submit an issue or pull request
