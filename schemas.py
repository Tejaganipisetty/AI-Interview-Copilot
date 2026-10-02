from pydantic import BaseModel, Field


class AnswerEvaluation(BaseModel):
    score: int = Field(
        description="Score from 0 to 10"
    )
    correctness: str = Field(
        description="Explain whether the answer is technically correct"
    )
    strengths: list[str] = Field(
        description="What the candidate explained correctly"
    )
    improvements: list[str] = Field(
        description="What is missing or incorrect"
    )
    ideal_answer: str = Field(
        description="A clear, technically accurate model answer"
    )
    follow_up_question: str = Field(
        description="One relevant, more challenging follow-up question"
    )