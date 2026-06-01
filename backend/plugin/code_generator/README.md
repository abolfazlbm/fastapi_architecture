#CodeGenerator

Code generator plug-in to generate general business code

- Support maintenance of code generation business configuration and model column information
- Supports manual mode and automatic table guide mode to generate general business code
- Supports previewing, writing to disk and downloading generated results

## Plug-in type

- Application-level plug-ins

## Configuration instructions

The `[settings]` of `plugin.toml` in the plugin directory contains the following content:

```toml
[settings]
CODE_GENERATOR_DOWNLOAD_ZIP_FILENAME = 'fba_generator'
```

Add the following content to `backend/core/conf.py`:

```python
################################################
# [Plugin] code_generator
################################################
CODE_GENERATOR_DOWNLOAD_ZIP_FILENAME: str
```

## Usage

1. After installing and enabling the plug-in, restart the backend service
2. Maintain business configuration and model column information
3. Execute the preview, generation and download process
4. The generated code will be written directly to disk and must only be used in the development environment.

## Uninstall instructions

- After uninstalling the plug-in, it is recommended to simultaneously remove the relevant plug-in basic configuration and the plug-in configuration in `backend/core/conf.py`
- If the project has been connected to code generation related pages or automated processes, please clean up the corresponding integration simultaneously.

## Contact information

- Author: `wu-clan`
- Feedback method: Submit an Issue or PR