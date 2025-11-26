> [!TIP]
> Current version only includes backend code generation

> [!WARNING]
> Since the text output of jinja2 may have formatting problems when rendering templates, the `preview` interface may not be able to visually preview the code. This is a default for the front end.

## Introduction

The code generator is implemented using API calls and contains two modules. The design may have flaws. Please submit issues directly for related questions.

### 1. Code generation business

Contains configuration related to code generation, view details: `generator/model/gen_business.py`

### 2. Code generation model column

Contains model column information required for code generation, just like defining model columns normally. Currently, the supported functions are limited.

## Use (eat)

1. Start the backend service, open the swagger document and operate directly
2. Send interface requests through third-party api debugging tools
3. Start the front and back ends at the same time and operate from the page

The interface parameters are basically explained, please check carefully.

### F. Pure manual mode

Not recommended (manually creating business interfaces is marked as "deprecated")

1. Manually add a piece of business data by creating a business interface
2. Manually add model columns through the model creation interface
3. Access the `preview` (preview), `generate` (disk writing), `download` (download) interface and perform the corresponding work of back-end code generation

### S. Automatic mode

Recommended

1. Access the `tables` interface to obtain a list of database table names
2. Import existing database table data into the database through the `import` interface, and business table data and model table data will be automatically created.
3. Access the `preview` (preview), `generate` (disk writing), `download` (download) interface and perform the corresponding work of back-end code generation