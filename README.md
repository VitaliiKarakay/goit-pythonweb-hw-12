# goit-pythonweb-hw-08
## How to Use

### **1️⃣ Start PostgreSQL using Docker**

Ensure you have **Docker** installed and run the following command to start a **PostgreSQL container**:

```sh
docker run --name contacts-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=postgres -p 5432:5432 -d postgres
```

> **This will:**
> - Start a **PostgreSQL** container with the database named **contacts**
> - Expose it on **port 5432**

### **2️⃣ Set up Environment Variables**

Create a `.env` file in the project root with the following content:

```ini
DATABASE_URL = postgresql+asyncpg://postgres:password@localhost:5432/postgres
```

### **3️⃣ Install Dependencies**

Set up a Python virtual environment and install dependencies using Poetry:

```sh
python3 -m venv venv
source venv/bin/activate

curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"

poetry install
```

> **This will:**
> - Create and activate a Python virtual environment
> - Install dependencies listed in `pyproject.toml`

### **4️⃣ Apply Migrations with Alembic**

Run the following command to apply database migrations:

```sh
alembic upgrade head
```

> **This will:**
> - Apply all database migrations defined in Alembic.

### **5️⃣ Run the FastAPI Application**

Start the application with **Uvicorn**:

```sh
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

> **Now, the API will be running on:**
> - `http://127.0.0.1:8000/`

---

## **API Overview**

### **Endpoints**

| Method     | Endpoint               | Description                                        |
|------------|------------------------|----------------------------------------------------|
| **POST**   | `/contacts/`           | Create a new contact                               |
| **GET**    | `/contacts/`           | Get all contacts (with pagination & filtering)     |
| **GET**    | `/contacts/{id}`       | Get a specific contact by ID                       |
| **PATCH**  | `/contacts/{id}`       | Update an existing contact                         |
| **DELETE** | `/contacts/{id}`       | Delete a contact                                   |
| **GET**    | `/contacts/search/`    | Search contacts by first name, last name, or email |
| **GET**    | `/contacts/birthdays/` | Get upcoming birthdays in the next N days          |

### **Query Parameters for Searching**

You can filter contacts by:

```sh
GET /contacts/?first_name=Valera&last_name=Valer&email=Valera@example.com
```

### **Get Upcoming Birthdays**

Fetch contacts whose birthdays are in the next 7 days:

```sh
GET /contacts/birthdays/?days=7
```

### **API Documentation**

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc UI:** `http://127.0.0.1:8000/redoc`

---