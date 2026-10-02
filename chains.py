
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from schemas import AnswerEvaluation

# Initialize the language model
llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0.3
)


# 1. Generate interview questions
question_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a technical interviewer.
        Generate exactly ONE interview question.
        Topic: {topic}
        Difficulty: {difficulty}
        Ask a clear, relevant technical question.
        Do not provide the answer."""
    ),
    (
        "human",
        "Previous interview context:\n{history}\n\nGenerate the next question."
    )
])

question_chain = question_prompt | llm | StrOutputParser()


# 2. Evaluate the candidate's answer
evaluation_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a fair and technically accurate interviewer.
        Evaluate the candidate's answer based on the question.
        Give an integer score from 0 to 10.
        Be specific about technical mistakes and missing concepts.
        Accept alternative correct approaches.
        Provide a correct model answer and one useful follow-up question.
        Return the requested structured output."""
    ),
    (
        "human",
        """Topic: {topic}

        Question: {question}

        Candidate's answer: {answer}"""
    )
])

evaluation_model = llm.with_structured_output(AnswerEvaluation)

evaluation_chain = evaluation_prompt | evaluation_model


# 3. Demonstrate RunnableParallel and RunnablePassthrough
# Both branches receive the same input dictionary.
analysis_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Explain the key technical concept tested by this interview question in 2-3 sentences."
    ),
    (
        "human",
        "Question: {question}\nCandidate answer: {answer}"
    )
])

parallel_analysis_chain = RunnableParallel(
    candidate_input=RunnablePassthrough(),
    concept_explanation=analysis_prompt | llm | StrOutputParser()
)


# 4. Combine reusable chains using LCEL
# The evaluation and concept explanation run in parallel.
full_evaluation_chain = RunnableParallel(
    evaluation=evaluation_chain,
    analysis=parallel_analysis_chain
)