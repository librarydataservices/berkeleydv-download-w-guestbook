# berkeleydv-download-w-guestbook
Jupyter Notebook walking through steps to download dataverse file with a guestbook via API.
Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

## Features
- Bulk upload entire directories to Dataverse datasets
- Configurable via TOML file
- Secure API token management via environment variable
- Support for dependency management with [uv](https://github.com/astral-sh/uv)

## Installation

### Using uv (Recommended)
[uv](https://docs.astral.sh/uv/) is an extremely fast Python and project manager. This is the recommended approach for the fastest setup experience. See [Installing uv](https://docs.astral.sh/uv/getting-started/installation/).

#### 1. Clone the repository
``` bash
git clone https://github.com/librarydataservices/berkeley-dataverse-upload.git
cd berkeley-dataverse-upload
```

#### 2. Sync dependencies
uv will read from `pyproject.toml` and `uv.lock` to create a virtual environment and install all dependencies.

```
uv sync
```

---

### Using `pip`
If you prefer traditional Python tooling:

#### 1. Clone the repository
``` bash
git clone https://github.com/librarydataservices/berkeley-dataverse-upload.git
cd berkeley-dataverse-upload
```

#### 2. Create and activate a virtual environment
``` bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 3. Install dependencies
Install dependencies using `pyproject.toml`.

``` bash
pip install .
```

## Configuration

### Environment Variables

1. Copy the example environment file (`.env.example`):

```bash
cp .env.example .env
```

2. Edit `.env` and add your [UC Berkeley Library Dataverse API Token](https://guides.dataverse.org/en/latest/user/account.html#api-token).

```bash
API_TOKEN="REPLACE WITH TOKEN"
```

#### Obtaining an API Token
1. Log in to [UC Berkeley Library Dataverse](https://datasets.lib.berkeley.edu/).
2. Click your account name in the navbar, then select "API Token" from the dropdown.
3. Click "Create Token."

> **Security Note:** Never commit your `.env` file or share your API token publicly. The `.env` file is included in the `.gitignore` by default.

## Usage

### Running with uv
uv provides the `uv run` command which automatically uses the project's virtual environment. 

``` bash
# Basic usage
uv run jupyterlab
```

Once the Jupyter environment is running, open `guestbook_download.ipynb`, follow instructions, and step through the environment.

### Running with Python directly

1. Activate your virtual environment.

``` bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

2. Run the Jupyter Lab.

``` bash
python -m jupyter lab
```

Once the Jupyter environment is running, open `guestbook_download.ipynb`, follow instructions, and step through the environment.

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/librarydataservices/berkeley-dataverse-upload/blob/main/LICENSE) file for details.

## Acknowledgements
- GPT 5.4 used in development

## Contact
UC Berkeley Library Data Services
- Email: [librarydataservices@berkeley.edu]( mailto:librarydataservices@berkeley.edu)
- GitHub: [@librarydataservices](https://github.com/librarydataservices)