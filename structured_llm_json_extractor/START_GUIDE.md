# Getting Started

This guide covers setting up the project on Windows, running it, testing it, and
processing your own `.txt` file. Run the commands from the project root folder.

## 1. Create and activate the environment

Open PowerShell in the project folder:

```powershell
cd D:\structured_llm_json_extractor
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, allow scripts for this terminal session only,
then activate the environment:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Install the project and its development/test dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

When activation succeeds, the prompt normally shows `(.venv)`. To leave the
environment later, run `deactivate`.

## 2. Configure Gemini

The automated tests use a mocked Gemini client and do not need an API key.
Running an actual extraction does need a valid Google Gemini API key.

Create your local settings file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder with your own key:

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Keep `.env` private; it is excluded from Git. Do not commit or share your key.
Your input text will be sent to the configured Gemini API, so only process
documents you are authorized to share with that service.

## 3. Run the project with included examples

Extract an invoice and print the validated JSON in the terminal:

```powershell
python -m src.cli --type invoice --input examples\invoice.txt
```

Save the invoice result to a JSON file instead:

```powershell
python -m src.cli --type invoice --input examples\invoice.txt --output output\invoice.json
```

Extract a resume:

```powershell
python -m src.cli --type resume --input examples\resume.txt --output output\resume.json
```

The supported document types are `invoice` and `resume`. If `--output` is
omitted, JSON is printed to the terminal. The program creates the output
directory if needed.

## 4. Run automated tests

With the virtual environment active, run:

```powershell
python -m pytest -v
```

These tests check prompts, schema validation, and extraction behavior using a
mocked Gemini response. They do not make real API calls or consume API quota.

## 5. Process another `.txt` file

Put your UTF-8 plain-text document anywhere you can reference, for example
`test_inputs\my_invoice.txt`. Choose `invoice` or `resume` to match the
document, then provide the file path with `--input`.

```powershell
python -m src.cli --type invoice --input test_inputs\my_invoice.txt --output output\my_invoice.json
```

For a resume:

```powershell
python -m src.cli --type resume --input test_inputs\my_resume.txt --output output\my_resume.json
```

You can use an absolute path or a path relative to the project root. Quote paths
that contain spaces:

```powershell
python -m src.cli --type invoice --input "C:\Users\YourName\Documents\new invoice.txt" --output output\new_invoice.json
```

This project reads text files only; it does not convert PDFs, images, or
scanned documents to text. Check the generated JSON against the original
document, especially amounts, dates, and contact details.

## Troubleshooting

- **`GEMINI_API_KEY is missing`:** Make sure `.env` is in the project root and
  contains a valid key.
- **Module or dependency errors:** Activate `.venv`, then rerun
  `python -m pip install -e ".[dev]"`.
- **File not found:** Check the input path and run the command from the project
  root, or provide an absolute path.
- **API, quota, or model errors:** Check your key, model access, network, and
  account quota. Automated tests can still run without API access.
