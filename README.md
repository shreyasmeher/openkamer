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


```mermaid
graph TD
    A[Start: OpenKamer for TWIN4DEM Project] --> B(Project Context: Dutch Parliament Data, Python 3.8, Django 2.2);

    B --> C{1. Prerequisites};
    C --> C1[macOS Prerequisites];
    C --> C2[Windows Prerequisites];

    subgraph macOS Setup
        C1a[Homebrew] --> C1b[Install Tools: git, pyenv, postgresql];
    end

    subgraph Windows Setup
        C2a[Install Git] --> C2b[Install Python 3.8.10 (Add to PATH)];
        C2b --> C2c[Install PostgreSQL];
    end

    C1b & C2c --> D{2. Installation and Setup};
    D --> D1[2.1 Get Project Code];
    D1 --> D2{2.2 Create & Activate Virtual Environment};

    subgraph Virtual Environment Setup
        D2_mac_a[macOS: pyenv install 3.8.18 & pyenv local] --> D2_mac_b[macOS: python -m venv env & source activate];
        D2_win_a[Windows: py -3.8 -m venv env] --> D2_win_b[Windows: .\env\Scripts\activate];
        D2_mac_b & D2_win_b --> D2_verify(Verification: python --version == Python 3.8.x);
    end

    D2_verify --> D3[2.3 Install Dependencies];
    D3 --> D4[2.4 Initialize Database (db.sqlite3)];
    D4 --> D5[2.5 Create Local Settings];

    D5 --> E{3. Runtime Fix for Wikidata Scraper};
    E --> E1[Open wikidata/government.py];
    E1 --> E2[Replace get_government_members function];

    E2 --> F{4. Data Scraping};
    F --> F1[Run Scraper: scrape_range 2010-2024];
    F1 --> F2(Scraping in progress...);

    F2 --> G{5. Running Web Application};
    G --> G1(Note: Wait for Scraping to Complete);
    G1 --> G2[Open New Terminal & Activate Env];
    G2 --> G3[Run Server: python manage.py runserver];
    G3 --> G4(App available at [http://127.0.0.1:8000](http://127.0.0.1:8000));

    G4 --> H{6. Accessing the Data};
    H --> H1[Data in db.sqlite3 file];
    H1 --> H2a[Viewing: DB Browser for SQLite];
    H1 --> H2b[Accessing with Code: Python/Pandas or R/RSQLite];

    H --> I[End: Project Setup & Data Available];

    subgraph Additional Capabilities
        J[Search (Apache Solr)]
        K[Testing (python manage.py test)]
    end

    I --> J;
    I --> K;

    %% Styling for better readability and visual distinction
    style A fill:#D0F0C0,stroke:#3C803C,stroke-width:2px,color:#000
    style B fill:#E0E0FF,stroke:#6A5ACD,stroke-width:1px,color:#000

    style C fill:#F9E79F,stroke:#D35400,stroke-width:2px,color:#000
    style C1 fill:#D6EAF8,stroke:#2874A6,stroke-width:1px,color:#000
    style C2 fill:#D6EAF8,stroke:#2874A6,stroke-width:1px,color:#000
    style C1a fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style C1b fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style C2a fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style C2b fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style C2c fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000

    style D fill:#F9E79F,stroke:#D35400,stroke-width:2px,color:#000
    style D1 fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style D2 fill:#D6EAF8,stroke:#2874A6,stroke-width:1px,color:#000
    style D2_mac_a fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style D2_mac_b fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style D2_win_a fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style D2_win_b fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style D2_verify fill:#FFFFCC,stroke:#DAA520,stroke-width:1px,color:#000
    style D3 fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style D4 fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style D5 fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000

    style E fill:#F9E79F,stroke:#D35400,stroke-width:2px,color:#000
    style E1 fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style E2 fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000

    style F fill:#F9E79F,stroke:#D35400,stroke-width:2px,color:#000
    style F1 fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style F2 fill:#FFFFCC,stroke:#DAA520,stroke-width:1px,color:#000

    style G fill:#F9E79F,stroke:#D35400,stroke-width:2px,color:#000
    style G1 fill:#FFFFCC,stroke:#DAA520,stroke-width:1px,color:#000
    style G2 fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style G3 fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style G4 fill:#FFFFCC,stroke:#DAA520,stroke-width:1px,color:#000

    style H fill:#F9E79F,stroke:#D35400,stroke-width:2px,color:#000
    style H1 fill:#D6EAF8,stroke:#2874A6,stroke-width:1px,color:#000
    style H2a fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000
    style H2b fill:#E8F8F5,stroke:#1ABC9C,stroke-width:1px,color:#000

    style I fill:#D0F0C0,stroke:#3C803C,stroke-width:2px,color:#000
    style J fill:#C9E3F3,stroke:#1C6EA4,stroke-width:1px,color:#000
    style K fill:#C9E3F3,stroke:#1C6EA4,stroke-width:1px,color:#000
