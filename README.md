# OpenKamer for TWIN4DEM

This project is a fork of the original OpenKamer project, adapted for data scraping and analysis within the TWIN4DEM project. It gives insight into the Dutch parliament by gathering, organizing, and visualizing parliamentary data from sources like the Tweede Kamer API, WikiData, and overheid.nl.

This project is based on Python 3.8 and Django 2.2.

### Project Context

This guide provides an updated and reliable installation process for modern operating systems (macOS and Windows). The original project's dependencies require a specific **Python 3.8** environment to function correctly. Following these instructions is crucial for a successful setup.

-----

## 1\. Prerequisites

Before starting, ensure you have the required tools for your operating system.

#### **macOS**

1.  **Homebrew:** If not installed, get it from [brew.sh](https://brew.sh).
2.  **Install Tools:** Open Terminal and run:
    ```bash
    brew install git pyenv postgresql
    ```

#### **Windows**

1.  **Git:** Download and install from [git-scm.com](https://git-scm.com/download/win).
2.  **Python 3.8:** Download and install the "Windows installer (64-bit)" for Python 3.8.10 from [python.org](https://www.python.org/downloads/release/python-3810/). **Important:** During installation, check the box that says **"Add Python 3.8 to PATH"**.
3.  **PostgreSQL:** Download and install from [postgresql.org](https://www.postgresql.org/download/windows/). This is required for a project dependency and does not need to be configured further.

-----

## 2\. Installation and Setup

Follow these steps in your terminal (macOS) or Command Prompt/PowerShell (Windows).

#### Step 2.1: Get Project Code

```bash
git clone https://github.com/openkamer/openkamer.git
cd openkamer
```

#### Step 2.2: Create and Activate Virtual Environment

**macOS:**

```bash
# Install Python 3.8.18 and set it for this directory
pyenv install 3.8.18
pyenv local 3.8.18

# Create virtual environment using the direct pyenv path
~/.pyenv/versions/3.8.18/bin/python -m venv env

# Activate the environment
source env/bin/activate
```

**Windows:**

```bash
# Create virtual environment using the py.exe launcher for Python 3.8
py -3.8 -m venv env

# Activate the environment
.\env\Scripts\activate
```

> **Verification:** After activating, run `python --version`. The output must be `Python 3.8.x`.

#### Step 2.3: Install Dependencies

With the environment active, install the required packages.

```bash
python -m pip install -r requirements.txt
```

#### Step 2.4: Initialize Database

This command creates the tables in the local `db.sqlite3` database file.

```bash
python manage.py migrate
```

#### Step 2.5: Create Local Settings

This generates the required local configuration file.

```bash
python create_local_settings.py
```

-----

## 3\. Runtime Fix for Wikidata Scraper

A mandatory fix is required to handle changes in the live Wikidata API.

1.  **Open the file:** `wikidata/government.py`.
2.  **Replace** the entire `get_government_members` function with the code below to prevent crashes from empty API responses.

\<details\>
\<summary\>Click to expand code for the corrected function.\</summary\>

```python
def get_government_members(government_wikidata_id, max_members=None) -> List[GovernmentMemberData]:
    logger.info('BEGIN')
    language = 'nl'
    parts = wikidata.WikidataItem(government_wikidata_id).get_parts()
    members = []
    if parts:  # This check prevents the script from crashing
        for part in parts:
            member = create_government_member(part, language)
            logger.info(member.name)
            logger.info(json.dumps(member.__dict__, sort_keys=True, default=str))
            members.append(member)
            if max_members and len(members) >= max_members:
                break
    logger.info('END')
    return members
```

\</details\>

-----

## 4\. Data Scraping

This project is configured to use a custom, resilient scraper that targets a specific date range. *(Note: This assumes the `scrape_range.py` script from our session is saved in `openkamer/management/commands/`)*.

#### Step 4.1: Run the Scraper

This long-running process scrapes data and saves it to the `db.sqlite3` database. To run it for 2010-2024:

```bash
python manage.py scrape_range --start-year 2010 --end-year 2024
```

You can monitor progress via the messages printed in the terminal.

-----

## 5\. Running the Web Application

#### Step 5.1: Run the Development Server

**Note:** It is highly recommended to wait for the scraping process to complete. Running the web server and scraper at the same time will cause `database is locked` errors.

To run the server, open a **new terminal**, navigate to the project folder, activate the virtual environment, and run:

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000`.

-----

## 6\. Accessing the Data

The scraped data is stored in the **`db.sqlite3`** file in the project's root directory.

#### **Viewing the Data**

A graphical tool like [DB Browser for SQLite](https://sqlitebrowser.org/) can be used to open the `db.sqlite3` file and browse the tables and data.

#### **Accessing with Code**

**Python (with Pandas):**

```python
import sqlite3
import pandas as pd
conn = sqlite3.connect('db.sqlite3')
df = pd.read_sql_query("SELECT * FROM document_kamervraag", conn)
conn.close()
print(df.head())
```

**R (with RSQLite):**

```r
library(RSQLite)
con <- dbConnect(RSQLite::SQLite(), "db.sqlite3")
data_df <- dbGetQuery(con, "SELECT * FROM document_kamervraag")
dbDisconnect(con)
head(data_df)
```

-----

\<details\>
\<summary\>\<b\>Advanced Development (Original README Sections)\</b\>\</summary\>

### Search

This project can be configured to use Apache Solr for search. Instructions are based on [https://github.com/dekanayake/haystack\_solr6](https://github.com/dekanayake/haystack_solr6).

### Testing

To run the full test suite:

```bash
$ python manage.py test
```

To run specific tests:

```bash
$ python manage.py test website.test.TestCreateParliament
```

\</details\>
