from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, StringConstraints

NormalizedEmail = Annotated[EmailStr, AfterValidator(str.lower)]
Password = Annotated[str, Field(min_length=8, max_length=128)]
FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PageQuery(InputModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class Page[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int
