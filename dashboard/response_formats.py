from pydantic import BaseModel, Field
from typing import Optional, List

class ListData(BaseModel):
    header_text: str = Field(..., description="The header text for the list of options, must not exceed 20 characters.")
    data: List[str] = Field(..., description="A list of up to 10 options for the user to choose from, each option can have a maximum of 24 characters.")

class ResponseSchema(BaseModel):
    text: str = Field(..., description="The main text content of the response. If image, list_data, or cta_button is present, the length of the text should be less than 1024 characters, otherwise it should be less than 4096 characters.")
    image: Optional[str] = Field(None, description="An optional image URL associated with the response, or null.")
    list_data: Optional[ListData] = Field(None, description="List data containing a header and options, or null.")
    cta_button: Optional[List[str]] = Field(None, description="A list of buttons (strings) or null, with each button having a maximum of 20 characters.")