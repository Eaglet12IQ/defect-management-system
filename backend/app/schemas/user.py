from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

# Базовая схема для пользователя
class UserBase(BaseModel):
    email: EmailStr
    username: str

# Схема для создания пользователя (регистрация)
class UserCreate(UserBase):
    password: str
    re_password: str
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    role: int

# Схема для аутентификации
class UserLogin(BaseModel):
    username: str  # Может быть email или username
    password: str

# Схема для возврата информации о пользователе
class User(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True  # Replaces orm_mode
    )

class UserCreateWithPasswordValidation(UserCreate):
    @field_validator('password')
    def validate_password_length(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен содержать не менее 8 символов!')
        return v

class UserLoginWithPasswordValidation(UserLogin):
    @field_validator('password')
    def validate_password_length(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен содержать не менее 8 символов!')
        return v
    
    @field_validator('username')
    def username_not_empty(cls, v):
        if not v.strip():
            raise ValueError("field required")
        return v