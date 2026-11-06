# Structured LLM Prompt Pipeline & JSON Extractor

A Python application that converts unstructured invoice and resume text into structured JSON using Google's Gemini API, few-shot prompting, and strict Pydantic validation.

The project demonstrates prompt engineering, LLM API integration, structured output generation, data validation, error handling, retry logic, command-line development, and automated testing.

For a concise Windows setup, activation, testing, and custom `.txt` walkthrough,
see [Getting Started](START_GUIDE.md).

## 1. Project objectives

The application accepts unstructured text from an invoice or resume and extracts relevant information into a predefined JSON structure.

The extraction pipeline is:

```text
Input text file
      |
      v
Command-line interface
      |
      v
Document-specific prompt + Pydantic schema
      |
      v
Google Gemini API
      |
      v
JSON parsing
      |
      v
Pydantic validation
      |
      v
Validated JSON output
```

The application supports two document types:

- **Invoice:** vendor, invoice number, dates, currency, totals, customer details, line items, payment terms, and notes.
- **Resume:** contact details, headline, skills, work experience, education, certifications, and languages.

## 2. Features

- Google Gemini API integration using the `google-genai` SDK.
- Parameterized prompts for invoice and resume extraction.
- Few-shot examples containing sample documents and expected JSON outputs.
- Structured JSON generation.
- Independent Pydantic validation after the model responds.
- Strict schema handling that rejects unexpected fields.
- Validation for dates, amounts, currencies, and other defined constraints.
- Configurable Gemini model through environment variables.
- Bounded retry attempts with exponential delays for selected failures.
- Command-line interface for processing text files.
- JSON output to the terminal or a specified file.
- Automated tests that mock the Gemini client and do not require API calls.

## 3. Technology stack

| Technology | Purpose |
|---|---|
| Python | Application implementation |
| Google GenAI SDK | Gemini API integration |
| Pydantic v2 | Schema definition and validation |
| python-dotenv | Loading environment variables from `.env` |
| pytest | Automated testing |
| setuptools | Project packaging and installation |

## 4. Requirements

- Python 3.11 or newer is recommended.
- A Google AI Studio API key.
- Internet access when making Gemini API requests.

The project metadata currently declares Python 3.10 or newer. Python 3.11+ is recommended for a fresh setup, but compatibility should be confirmed in the target environment.

## 5. Installation

### Windows PowerShell

Open a terminal in the project directory.

Create a virtual environment:

```powershell
py -3 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install the project and development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

If the `py` launcher is unavailable, use the appropriate Python executable to create the virtual environment.

## 6. Configure Gemini

Create a `.env` file from the supplied example:

```powershell
Copy-Item .env.example .env
```

Open `.env` and set your API key:

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Replace the placeholder with your own key. The example above shows the configuration format; model availability depends on your Google AI Studio/API account.

Obtain an API key through Google AI Studio.

**Security requirements:**

- Never commit `.env` to Git.
- Never hard-code your API key in Python source files.
- Never share API keys in screenshots, logs, or public repositories.
- Do not send private documents to an external API unless you have permission to do so.

## 7. Run the application

Run commands from the project root, with the virtual environment activated.

### Extract invoice information

```powershell
python -m src.cli --type invoice --input examples/invoice.txt
```

To save the output to a JSON file:

```powershell
python -m src.cli --type invoice --input examples/invoice.txt --output output/invoice.json
```

### Extract resume information

```powershell
python -m src.cli --type resume --input examples/resume.txt
```

To save the output to a JSON file:

```powershell
python -m src.cli --type resume --input examples/resume.txt --output output/resume.json
```

The application creates the output directory if necessary.

When `--output` is omitted, the validated JSON is printed to the terminal.

### Command-line arguments

| Argument | Required | Description |
|---|---|---|
| `--type` | Yes | Document type: `invoice` or `resume` |
| `--input` | Yes | Path to the source text file |
| `--output` | No | Destination path for the JSON result |

Example with a different input file:

```powershell
python -m src.cli --type invoice --input path\to\invoice.txt --output output\result.json
```

## 8. Run the tests

Run the full automated test suite:

```powershell
python -m pytest -v
```

The tests cover:

- Prompt construction.
- Schema validation.
- Currency normalization.
- Rejection of negative amounts and invalid experience values.
- Rejection of unexpected fields.
- Successful extraction using a mocked Gemini response.
- Empty input and unsupported document types.
- Invalid JSON and invalid model data.
- Simulated API failures.
- Retry and non-retryable error behavior.

The extraction unit tests mock the Gemini client. They do not require a live API request or consume Gemini API quota.

A successful test run means the tested behaviors passed. It does not guarantee that every real document will be extracted perfectly.

## 9. Project structure

```text
structured_llm_json_extractor/
|
|-- examples/
|   |-- invoice.txt
|   `-- resume.txt
|
|-- src/
|   |-- __init__.py
|   |-- cli.py
|   |-- extractor.py
|   |-- prompts.py
|   `-- schemas.py
|
|-- tests/
|   |-- test_extractor.py
|   |-- test_prompts.py
|   `-- test_schemas.py
|
|-- .env.example
|-- .gitignore
|-- pyproject.toml
`-- README.md
```

Generated JSON files and local virtual-environment files may also be present during development.

## 10. Error handling and validation

The application rejects empty document text and unsupported document types before calling Gemini.

After the model responds, the application:

1. Checks that a response exists.
2. Parses the response as JSON.
3. Validates the resulting data against the appropriate Pydantic model.
4. Returns validated data or raises an extraction error.

Selected failures may be retried with a bounded number of attempts.

Schema validation confirms that the returned data meets the defined structural and validation rules. It does not independently prove that the extracted information is factually correct.

## 11. Limitations

- **Text input only:** PDF extraction, image OCR, and scanned-document processing are not implemented.
- **Extraction accuracy:** Results depend on source quality and model behavior.
- **Field-level evidence:** The application does not currently attach source quotations or page references to each extracted field.
- **Privacy:** Input documents are sent to the configured Gemini API.
- **API availability:** Requests may fail because of quotas, permissions, service outages, or model availability.
- **Financial correctness:** The application validates extracted data but does not provide a complete accounting reconciliation system.
- **Human review:** Important financial information and employment-related information should be checked against the original document.

## 12. Troubleshooting

### Missing API key

Confirm that `.env` exists in the project root and contains a valid `GEMINI_API_KEY` value.

### Gemini API errors

Check your API key, model availability, API access, quota, and network connection.

### Invalid JSON or schema errors

Inspect the source document and extraction error. The model may have returned malformed JSON or data that does not satisfy the schema.

### Module not found

Activate the project's virtual environment and install the package:

```powershell
python -m pip install -e ".[dev]"
```

Run the CLI from the project root.

### Test failures

Run:

```powershell
python -m pytest -v
```

Use the failure details to identify which prompt, schema, or extraction behavior needs attention.

## 13. Possible future improvements

Potential extensions include:

- FastAPI endpoint.
- Streamlit user interface.
- PDF and image OCR ingestion.
- Field-level source evidence.
- A labeled evaluation dataset with extraction accuracy metrics.
- Structured logging and API usage monitoring.
- Provider-specific retry handling.
- Additional document types.
- Human review workflow for low-confidence results.

These are optional extensions, not requirements for the current project.

## 14. Project summary

This project demonstrates an end-to-end structured extraction pipeline built with Python, Google Gemini, prompt engineering, and Pydantic.

It converts unstructured invoice and resume text into schema-validated JSON and includes a command-line interface, configurable API settings, error handling, and automated tests.