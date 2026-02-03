# Project Preview: Spotify Clone Server - Authentication System

This document provides a comprehensive overview of the Spotify Clone server project, focusing on the authentication system. It explains the sign up and sign in routes, the packages used, and provides a detailed plan for implementing email verification.

## Overview

The project is a FastAPI-based backend for a music streaming application (Spotify clone). It includes user authentication with sign up and sign in functionality. The system uses PostgreSQL as the database, SQLAlchemy for ORM, and bcrypt for password hashing.

## Sign Up Route Explanation

The sign up route is defined in `routes/auth.py` as a POST endpoint at `/auth/signup`.

### Functionality:
- **Endpoint**: `POST /auth/signup`
- **Status Code**: 201 (Created)
- **Input**: JSON payload with `name`, `email`, and `password` (validated using Pydantic `UserCreate` model)
- **Process**:
  1. Checks if a user with the provided email already exists in the database.
  2. If user exists, raises HTTP 400 error with message "User with same email already exists".
  3. Hashes the password using bcrypt with 16 rounds of salt.
  4. Creates a new user with a unique UUID, email, hashed password, and name.
  5. Adds the user to the database, commits the transaction, and refreshes the user object.
  6. Returns the newly created user object (excluding password for security).

### Code Snippet:
```python
@router.post("/signup", status_code=201)
def signup_user(user:UserCreate, db:Session = Depends(get_db)):
    user_db = db.query(User).filter(User.email == user.email).first()
    if user_db:
        raise HTTPException(400,'User with same email already exists')
    hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt(16))
    new_user = User(id=str(uuid.uuid4()),email=user.email,password=hashed_pw,name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
```

## Sign In Route Explanation

The sign in route is defined in `routes/auth.py` as a POST endpoint at `/auth/login`.

### Functionality:
- **Endpoint**: `POST /auth/login`
- **Input**: JSON payload with `email` and `password` (validated using Pydantic `UserLogin` model)
- **Process**:
  1. Queries the database for a user with the provided email.
  2. If no user is found, raises HTTP 404 error with message "User not found!".
  3. Compares the provided password with the stored hashed password using bcrypt.
  4. If passwords don't match, raises HTTP 400 error with message "Invalid credentials!".
  5. If authentication succeeds, returns the user object (excluding password).

### Code Snippet:
```python
@router.post("/login")
def signin_user(user:UserLogin,db:Session = Depends(get_db)):
    user_db = db.query(User).filter(User.email == user.email).first()
    if not user_db:
        raise HTTPException(404,"User not found!")
    compare_pass = bcrypt.checkpw(user.password.encode(), user_db.password)
    if not compare_pass:
        raise HTTPException(400,"Invalid credentials!")
    return user_db
```

## Packages Used

The project uses the following Python packages:

1. **FastAPI**: Web framework for building APIs with automatic OpenAPI documentation.
2. **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library for database operations.
3. **Pydantic**: Data validation and parsing library, used for request/response models.
4. **bcrypt**: Password hashing library for secure password storage.
5. **psycopg2-binary**: PostgreSQL adapter for Python (inferred from database URL).
6. **uuid**: Standard library module for generating unique identifiers.

### Installation:
To install these packages, create a `requirements.txt` file with:
```
fastapi
sqlalchemy
pydantic
bcrypt
psycopg2-binary
```

Then run: `pip install -r requirements.txt`

## Email Verification Implementation

To add email verification, we need to enhance the user model and authentication flow. Here's a step-by-step implementation plan:

### 1. Update User Model
Add fields for email verification:
- `email_verified: bool` (default False)
- `verification_token: str` (optional, for token-based verification)

### 2. Install Additional Packages
Add `fastapi-mail` for sending emails:
```
pip install fastapi-mail
```

### 3. Update Pydantic Schemas
Add a new schema for email verification requests.

### 4. Modify Sign Up Route
- Generate a verification token upon sign up
- Send verification email
- Set `email_verified` to False initially

### 5. Add Verification Endpoint
Create a new route `/auth/verify-email` that:
- Takes a token as parameter
- Verifies the token
- Sets `email_verified` to True

### 6. Update Sign In Route
- Check if `email_verified` is True before allowing login

### Detailed Implementation Steps:

1. **Update `models/user.py`**:
```python
class User(Base):
    __tablename__ = 'users'
    
    id = Column(TEXT, primary_key=True)
    name = Column(VARCHAR(100))
    email = Column(VARCHAR(100))
    password = Column(LargeBinary)
    email_verified = Column(Boolean, default=False)
    verification_token = Column(TEXT, nullable=True)
```

2. **Configure Email Settings** in `main.py` or a separate config file:
```python
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME="your_email@example.com",
    MAIL_PASSWORD="your_password",
    MAIL_FROM="your_email@example.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False
)
```

3. **Modify Sign Up Route**:
```python
@router.post("/signup", status_code=201)
def signup_user(user:UserCreate, db:Session = Depends(get_db)):
    # ... existing code ...
    verification_token = str(uuid.uuid4())
    new_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        password=hashed_pw,
        name=user.name,
        email_verified=False,
        verification_token=verification_token
    )
    # ... save to db ...
    
    # Send verification email
    message = MessageSchema(
        subject="Verify your email",
        recipients=[user.email],
        body=f"Click this link to verify: http://localhost:8000/auth/verify-email?token={verification_token}",
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    
    return new_user
```

4. **Add Verification Route**:
```python
@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(400, "Invalid token")
    user.email_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified successfully"}
```

5. **Update Sign In Route**:
```python
@router.post("/login")
def signin_user(user:UserLogin, db:Session = Depends(get_db)):
    # ... existing code ...
    if not user_db.email_verified:
        raise HTTPException(400, "Email not verified")
    return user_db
```

This implementation provides a secure email verification system. Remember to handle async operations properly and add proper error handling for email sending failures.