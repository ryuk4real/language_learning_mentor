from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class EmailInput(BaseModel):
    recipient: str = Field(..., description="Indirizzo email del destinatario")
    subject: str = Field(..., description="Oggetto dell'email")
    body: str = Field(..., description="Corpo dell'email")

class EmailSender(BaseTool):
    name: str = "Email Sender"
    description: str = "Invia un'email all'utente"
    args_schema: Type[BaseModel] = EmailInput
    
    def _run(self, recipient: str, subject: str, body: str) -> str:
        # In un'applicazione reale, qui ci sarebbe la logica per inviare l'email
        print(f"Email simulata inviata a {recipient}")
        print(f"Oggetto: {subject}")
        print(f"Corpo: {body}")
        return f"Email inviata con successo a {recipient}"