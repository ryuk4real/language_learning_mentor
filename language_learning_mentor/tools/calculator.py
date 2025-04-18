from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class ScoreInput(BaseModel):
    correct: int = Field(..., description="Numero di risposte corrette")
    wrong: int = Field(..., description="Numero di risposte sbagliate")

class QuizCalculator(BaseTool):
    name: str = "Quiz Score Calculator"
    description: str = "Calcola il punteggio finale del quiz"
    args_schema: Type[BaseModel] = ScoreInput
    
    def _run(self, correct: int, wrong: int) -> str:
        score = correct - wrong
        return f"Punteggio finale: {score}"