# 🚀 Glassmorphic Order App: Full-Stack E-Commerce System

An elegant, modern full-stack web application designed for browsing products, managing a shopping cart in real-time, and checking out orders. Built with an **Angular** frontend featuring glassmorphic UI principles and reactive streams, and a robust **FastAPI (Python)** backend leveraging relational databases and schema validation.

---

## 🗺️ Architectural Overview & System Flow

```mermaid
graph TD
    %% Frontend Components
    subgraph Frontend [Angular Frontend - Port 4200]
        UI[Glassmorphic UI Views]
        RF[Reactive Forms]
        CS[RxJS Cart Service]
        OS[Order Service]
        AI[Auth Interceptor]
        EI[HTTP Error Interceptor]
    end

    %% Backend Components
    subgraph Backend [FastAPI Backend - Port 8000]
        API[FastAPI App & Routers]
        PV[Pydantic Schema Validation]
        AM[Auth Handler & Hashing]
        DB_Dep[get_db Session Dependency]
    end

    %% Storage Layer
    subgraph Database [Storage Layer]
        SQLite[(SQLite DB: order_app.db)]
        ORM[SQLAlchemy ORM Models]
    end

    %% User Interactions
    User((User)) -->|Interacts| UI
    UI -->|Triggers| RF
    UI -->|Updates| CS
    UI -->|Requests| OS

    %% Client Services to Interceptors
    OS -->|HTTP Requests| AI
    AI -->|Injects Bearer Token| EI
    EI -->|Forwards Clean Call| API

    %% Backend Processing
    API -->|Validates Input| PV
    API -->|Authenticates Token| AM
    API -->|Requests session| DB_Dep
    DB_Dep -->|Manages transaction| ORM
    ORM -->|Reads / Writes| SQLite

    %% Error Flows
    API -.->|Throws HTTP Exception| EI
    EI -.->|Spawns Toast Notification| UI
```

---

## 🛠️ Technology Stack

### 💻 Frontend (Angular)
- **Framework:** Angular 19+ (Standalone Components, Functional Interceptors, Route-based views).
- **State Management:** Reactive RxJS streams utilizing `BehaviorSubject` for client-side shopping cart memory.
- **Styling:** Custom Vanilla CSS featuring CSS Custom Variables, background radial gradients, and modern frosted glass elements (`backdrop-filter`).
- **HTTP Client:** Angular `HttpClient` configured with functional interceptors for authentication propagation and automated error handling.

### 🐍 Backend (FastAPI)
- **Framework:** FastAPI (Python) - High performance, automatic Swagger/OpenAPI docs generation, and context-based lifespan handling.
- **Database ORM:** SQLAlchemy declarative mapping with relational structures and cascading deletions.
- **Database Engine:** SQLite (Embedded single-file SQL database).
- **Data Validation:** Pydantic schemas validating email syntax, phone regex pattern structures, string lengths, and numeric bounds.
- **Security:** SHA-256 password hashing and token-based header verification.

---

## 📁 Project Folder Structure

Below is an annotated overview of the file organization, illustrating where components reside:

```text
order-app-workspace/
├── backend/
│   ├── main.py              # FastAPI main application config, lifespan setup, and CORS configuration
│   ├── database.py          # SQLAlchemy SQLite connection setup, SessionLocal provider, and get_db dependency
│   ├── models.py            # Relational database models (User, Product, Order, OrderItem, OrderStatus enum)
│   ├── schemas.py           # Pydantic schemas for data serialization and API input validations
│   ├── order_app.db         # SQLite database file (created automatically on startup)
│   └── routers/
│       ├── auth.py          # Register, Login (mock token generator), and /me profile endpoints
│       ├── products.py      # Product catalog fetching and initial seeding logic
│       └── orders.py        # Order creation, order history retrieval, and status modification routers
│
└── order-app/
    ├── src/
    │   ├── main.ts          # Angular application bootstrapper
    │   ├── index.html       # Single HTML entry point containing the global layout structure
    │   ├── styles.css       # Global styles, layout utilities, toast notifications, and dark themes
    │   └── app/
    │       ├── app.ts       # Root component supervising the application shell and Navbar display
    │       ├── app.config.ts# Configures Zone.js detection, Routing, and HttpClient Interceptors
    │       ├── app.routes.ts# Maps paths (/login, /products, /cart, /place-order, /orders) to components
    │       ├── login/       # Login and Registration views, styling, and reactive validation forms
    │       ├── products/    # Product list grid component displaying item stock status
    │       ├── cart/        # Shopping cart view handling quantity operations and checkout links
    │       ├── orders/      # Checkout forms and history components
    │       │   ├── place-order/ # Order placement form (phone validation, automated user email matching)
    │       │   └── order-list/  # Collapsible order history list mapping items and details
    │       ├── services/    # Client side services:
    │       │   ├── cart.ts   # RxJS-powered local cart storage and item modifiers
    │       │   └── order.ts  # Angular HTTP client connection wrappers for order operations
    │       ├── shared/      # Common assets:
    │       │   └── navbar/   # Navigational headers visible inside the main platform
    │       └── interceptors/# Functional interceptor modules:
    │           ├── auth-interceptor.ts      # Automatic injection of Bearer token into HTTP headers
    │           └── http-error-interceptor.ts# Error-catching service triggering pop-up Toast displays
    └── package.json         # Frontend configuration, tasks, and dependency packages
```

---

## 🔒 Authentication Flow (How it Works)

The system enforces authentication to protect operations such as creating orders or viewing history.

```text
[ Register User ] ──> Stores Hashed Password (SHA-256) inside DB
                                │
[ Login Request ] ──> Verifies Credentials ──> Returns custom "mock_token_username"
                                │
[ Local Storage ] <── Caches access_token, username, and email in browser
                                │
[ HTTP Request  ] ──> Angular Interceptor reads local cache ──> Adds Authorization Header
                                │
[ FastAPI Guard ] <── Parses token header ──> Resolves active User ORM entity
```

### 1. Registration
- The user inputs a username, email, and password.
- **Backend checks:** Ensures both username and email are unique across the database.
- **Security:** The backend hashes the password using SHA-256 before writing it to the SQLite database.

### 2. Login
- The user provides their username and password.
- The backend matches the SHA-256 hash of the submitted password against the hashed record in the database.
- **Token Generation:** On success, the backend returns a mock OAuth2 Token format:
  ```json
  {
    "access_token": "mock_token_developer123",
    "token_type": "bearer",
    "username": "developer123",
    "email": "dev@example.com"
  }
  ```
- **Caching:** The Angular application caches `auth_token`, `username`, and `email` inside browser `localStorage`.

### 3. Session Middleware Injection
- When Angular sends an API request, the **Auth Interceptor** extracts the token from `localStorage` and appends it to the headers:
  ```http
  Authorization: Bearer mock_token_developer123
  ```
- The backend dependency `get_current_user` decodes the token, extracts the username (`developer123`), queries the database for this user record, and injects the corresponding ORM `User` object directly into the router endpoint.

---

## 📋 API Documentation & Specifications

The FastAPI application mounts three main routers. You can view, test, and interact with all endpoints directly through the auto-generated **Swagger UI** page by navigating to `http://localhost:8000/docs` in your browser.

### 🔑 Authentication Routes (Prefix: `/auth`)

| Method | Endpoint | Description | Auth Required | Payload Format | Key Returns |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Register a new user | ❌ No | `RegisterRequest` (JSON) | `{"message": "User registered successfully"}` |
| `POST` | `/auth/login` | Sign-in endpoint | ❌ No | JSON or UrlEncoded Form | `access_token`, `token_type`, `username`, `email` |
| `GET` | `/auth/me` | Fetch active user credentials | `Yes` | Headers | `id`, `username`, `email` |

### 📦 Product Routes (Prefix: `/api/products`)

| Method | Endpoint | Description | Auth Required | Payload Format | Key Returns |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/products` | Get catalog of products | ❌ No | None | Array of `ProductResponse` objects |

### 🛒 Order & Cart Routes (Prefix: `/api/orders`)

| Method | Endpoint | Description | Auth Required | Payload Format | Key Returns |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/orders` | Checkout cart & save order | `Yes` | `OrderCreate` (JSON) | Created `OrderResponse` (Order items, values, ID) |
| `GET` | `/api/orders` | Fetch orders for active user | `Yes` | None | Array of `OrderResponse` items |
| `PATCH`| `/api/orders/{id}` | Modify status of an order | `Yes` | `OrderStatusUpdate` (JSON) | Modified `OrderResponse` |

---

## 🔄 Dynamic End-to-End Workflow

Here is how all pages, components, and backend entities coordinate to handle a typical user flow:

### Step 1: Authentication View (`/login`)
The user is presented with a card that toggles between **Login** and **Register**. 
- **Validation:** On the frontend, Angular's `FormGroup` handles validation rules. For example, during registration, the email field must match email formatting, the username must be alphanumeric, and the password must be at least 8 characters. 
- **API Call:** On submit, Angular posts to `/auth/login` or `/auth/register`. On success, tokens are saved to local storage, and the app redirects to `/products`.

### Step 2: Catalog View (`/products`)
- Angular sends a request to `/api/products` to fetch all products.
- The UI lists all products inside a glassmorphic grid layout.
- **Stock Check:** The component checks the `stock_qty` property of each item. If the quantity is 0, the UI disables the "Add to Cart" button and displays an "Out of Stock" badge.
- Clicking "Add to Cart" passes the product model to the `CartService`.

### Step 3: Shopping Cart (`/cart`)
- `CartService` maintains an in-memory shopping list using an RxJS `BehaviorSubject`. This ensures that cart changes (such as total cost or item counts) update instantly across any listening component.
- Inside `/cart`, users can increase or decrease quantities. Reducing a quantity to 0 removes the item from the cart.
- Users can click "Proceed to Checkout" to move to `/place-order`.

### Step 4: Checkout Process (`/place-order`)
- The checkout form uses validation checks. It requires a `customer_name` (minimum 3 characters), `customer_email`, `delivery_address` (minimum 5 characters), and a 10-digit `phone` number.
- The email and name fields are pre-populated with details retrieved from `localStorage`.
- When the user clicks "Place Order", the frontend maps the items into an array of product IDs and quantities, sending it alongside the shipping details in a POST request to `/api/orders`.

### Step 5: Database Transactions on Checkout
Upon receiving the POST request:
1. **Stock Verification:** The backend queries each item's stock level in the database. If there is insufficient stock, it rejects the request with an error.
2. **Stock Update:** The backend decrements `stock_qty` for each ordered item in the database.
3. **Database Insertion:** The backend saves a new `Order` record, and inserts the individual items as relational `OrderItem` records.
4. **Clean up:** The backend commits the transaction to SQLite. The frontend then clears the client-side cart (`CartService.clearCart()`) and redirects the user to the orders page.

### Step 6: Order History (`/orders`)
- Angular calls the backend to retrieve all orders matching the authenticated user.
- The frontend displays the orders in a list. Users can click on an order card to expand it, revealing its shipping address, telephone number, and itemized subtotal costs.

---

## 🛡️ Input Validation Matrix

Data consistency is enforced on both the client (Angular) and the server (FastAPI/Pydantic) to protect the application from invalid inputs:

| Attribute | Frontend Validation (Angular) | Backend Validation (Pydantic) |
| :--- | :--- | :--- |
| **Username** | `Validators.required`<br>`Validators.minLength(3)` <br>Pattern: `^[a-zA-Z0-9_]+$` | String field: `min_length=3`, `max_length=30`<br>Pattern: `^[a-zA-Z0-9_]+$` |
| **Email** | `Validators.required`<br>`Validators.email` | Strict `EmailStr` formatting validation |
| **Password** | `Validators.required`<br>`Validators.minLength(8)` (Register)<br>`Validators.minLength(3)` (Login) | String field: `min_length=8`, `max_length=64` (Register) |
| **Customer Name** | `Validators.required`<br>`Validators.minLength(3)` | String field: `min_length=3` |
| **Address** | `Validators.required`<br>`Validators.minLength(5)` | String field: `min_length=5` |
| **Phone** | `Validators.required`<br>Pattern: `^[0-9]{10}$` | String field: Matching regex pattern `^\d{10}$` |
| **Order Items** | Evaluated on checkout button status | Required list: `min_length=1` item |
| **Item Qty** | Managed via UI counter bounds | Integer field: `Field(gt=0)` (quantity must be > 0) |

---

## 🗄️ Relational Database Schema (SQLite)

The application uses SQLAlchemy to model four primary tables in SQLite.

```mermaid
erDiagram
    USERS {
        int id PK
        string username UK
        string email UK
        string hashed_password
    }
    
    PRODUCTS {
        int id PK
        string name
        float price
        int stock_qty
    }
    
    ORDERS {
        int id PK
        int user_id FK
        string customer_name
        string customer_email
        string delivery_address
        string phone
        string status
        datetime created_at
    }
    
    ORDER_ITEMS {
        int id PK
        int order_id FK
        int product_id FK
        int qty
        float price_at_order
    }

    USERS ||--o{ ORDERS : "places"
    ORDERS ||--|{ ORDER_ITEMS : "contains"
    PRODUCTS ||--o{ ORDER_ITEMS : "references"
```

### Table Relationships
1. **User (1) ── (N) Order:** A user can place multiple orders. An order is linked to a user via the foreign key `user_id`.
2. **Order (1) ── (N) OrderItem:** Each order consists of one or more line items. If an order is deleted, its associated line items are deleted automatically due to the database configuration:
   `relationship("OrderItem", cascade="all, delete-orphan")`
3. **OrderItem (N) ── (1) Product:** Each line item references a specific product in the database.
4. **Historical Price Consistency:** `OrderItem` stores the `price_at_order`. This preserves the historical price of the product at the time of purchase, even if the price of the product changes in the catalog later.

---

## ⚙️ Development Environment Setup

### 1. Backend Setup (FastAPI & SQLite)

#### Prerequisites
- Make sure Python 3.9 or higher is installed.

#### Setup Steps
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - **Windows PowerShell:**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux:**
     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic email-validator
   ```
5. Run the FastAPI development server:
   ```bash
   uvicorn main:app --reload
   ```
6. **Verify Server Running:** Open `http://127.0.0.1:8000/docs` in your browser. The application should load the interactive **Swagger UI** page.
   > **Note:** On server startup, the database is initialized and seeded with default products (e.g. Wireless Mouse, Mechanical Keyboard) if the tables are empty.

---

### 2. Frontend Setup (Angular)

#### Prerequisites
- Make sure Node.js (version 18 or higher) and npm are installed.

#### Setup Steps
1. Navigate to the frontend directory:
   ```bash
   cd order-app
   ```
2. Install the project dependencies:
   ```bash
   npm install
   ```
3. Start the Angular development server:
   ```bash
   npm run dev
   # OR
   npx ng serve
   ```
4. **Verify Application:** Open `http://localhost:4200/` in your browser.

---

## 🎓 Interview-Ready Q&A Reference

### Q1: What is a `BehaviorSubject` in RxJS, and why is it used in the `CartService`?
> **Answer:** A `BehaviorSubject` is a special type of RxJS Subject that stores the current state and emits it to new subscribers immediately. In the shopping cart service, it acts as a client-side state store. When components like the cart page or checkout page subscribe to `items$`, they instantly receive the latest list of cart items. Any changes made to the cart automatically update all subscribing components.

### Q2: What is the purpose of functional interceptors in Angular?
> **Answer:** Interceptors process outgoing HTTP requests and incoming HTTP responses globally.
> - **`authInterceptor`:** Inspects `localStorage` for a saved token and appends it to request headers automatically. This keeps components clean, as they don't have to manage authentication headers for every request.
> - **`httpErrorInterceptor`:** Catches failed network requests (like invalid validation or unauthorized access) and displays an error message on screen using toast notifications.

### Q3: Why does `OrderItem` store `price_at_order` rather than referencing `Product.price`?
> **Answer:** If we only refer to the product table to fetch prices, changing a product's price in the catalog will retroactively alter the total cost of all previously placed orders. Storing a snapshot of the price at checkout ensures that order histories remain accurate and unaffected by future catalog price changes.

### Q4: How is Database Seeding managed on Startup in FastAPI?
> **Answer:** FastAPI uses a `lifespan` context manager. This hook runs before the server starts accepting HTTP requests. Inside `lifespan`, the backend generates the database tables and checks if the product table is empty. If it is, the server seeds the table with default products.

### Q5: How do Pydantic (Backend) and Angular (Frontend) validations work together?
> **Answer:**
> - **Frontend validation** provides immediate feedback to the user, improving usability by preventing the submission of incomplete forms.
> - **Backend validation** acts as the system's primary security barrier. Since clients can bypass frontend checks by calling APIs directly (e.g. via Postman or curl), backend validation ensures that only valid data is written to the database.

### Q6: What is SQLite, and is it suitable for production environments?
> **Answer:** SQLite is a serverless, single-file relational database engine that does not run as a separate process. While ideal for development, testing, and low-traffic applications, high-concurrency production systems generally use database engines like PostgreSQL or MySQL to better handle concurrent write transactions.
