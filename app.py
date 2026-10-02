import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from chains import question_chain, full_evaluation_chain



st.set_page_config(
    page_title="AI Interview Copilot",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 AI Interview Copilot")
st.caption("Practice technical interviews with an AI interviewer.")


defaults = {
    "history": [],
    "question": None,
    "last_result": None,
    "topic": "LangChain",
    "difficulty": "Intermediate",
    "total_questions": 10,
    "question_number": 1,
    "interview_complete": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value



with st.sidebar:
    st.header("Interview Settings")

    topic = st.text_input(
        "Enter interview topic",
        value="LangChain"
    )

    difficulty = st.selectbox(
        "Difficulty",
        ["Beginner", "Intermediate", "Advanced"]
    )

    total_questions = st.selectbox(
        "Number of questions",
        [10, 15, 20],
        index=0
    )

    if st.button("Start / Restart Interview", type="primary"):
        if not topic.strip():
            st.warning("Please enter an interview topic.")

        else:
            st.session_state.history = []
            st.session_state.last_result = None
            st.session_state.question = None
            st.session_state.topic = topic.strip()
            st.session_state.difficulty = difficulty
            st.session_state.total_questions = total_questions
            st.session_state.question_number = 1
            st.session_state.interview_complete = False

            with st.spinner("Generating your first question..."):
                try:
                    question = question_chain.invoke({
                        "topic": st.session_state.topic,
                        "difficulty": st.session_state.difficulty,
                        "history": (
                            "This is the beginning of the interview."
                        )
                    })

                    st.session_state.question = question
                    st.rerun()

                except Exception as e:
                    st.error(f"Could not generate question: {e}")



if (
    st.session_state.question
    and not st.session_state.interview_complete
):
    st.subheader(
        f"Topic: {st.session_state.topic} "
        f"• Difficulty: {st.session_state.difficulty}"
    )

    answered = len(st.session_state.history)
    total = st.session_state.total_questions

    st.progress(min(answered / total, 1.0))

    st.caption(
        f"Question {st.session_state.question_number} "
        f"of {total}"
    )

    st.markdown("### 📝 Interview Question")
    st.info(st.session_state.question)

    # Show the answer form only if the current question
    # has not already been evaluated.
    if st.session_state.last_result is None:

        with st.form("answer_form"):
            answer = st.text_area(
                "Your answer",
                placeholder="Explain your answer here...",
                height=180
            )

            submitted = st.form_submit_button("Submit Answer")

        if submitted:
            if not answer.strip():
                st.warning("Please enter your answer first.")

            else:
                with st.spinner("Evaluating your answer..."):
                    try:
                        result = full_evaluation_chain.invoke({
                            "topic": st.session_state.topic,
                            "question": st.session_state.question,
                            "answer": answer.strip()
                        })

                        evaluation = result["evaluation"]
                        explanation = (
                            result["analysis"]["concept_explanation"]
                        )

                        st.session_state.last_result = {
                            "question": st.session_state.question,
                            "answer": answer.strip(),
                            "evaluation": evaluation,
                            "explanation": explanation
                        }

                        st.session_state.history.append({
                            "question": st.session_state.question,
                            "answer": answer.strip(),
                            "score": evaluation.score
                        })

                        st.rerun()

                    except Exception as e:
                        st.error(f"Evaluation failed: {e}")



if st.session_state.last_result:
    result = st.session_state.last_result
    evaluation = result["evaluation"]

    st.divider()
    st.header("📊 Your Evaluation")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Score",
            f"{evaluation.score}/10"
        )

    with col2:
        st.metric(
            "Questions answered",
            len(st.session_state.history)
        )

    st.subheader("Correctness")
    st.write(evaluation.correctness)

    st.subheader("✅ Strengths")
    for item in evaluation.strengths:
        st.markdown(f"- {item}")

    st.subheader("📌 Areas to Improve")
    for item in evaluation.improvements:
        st.markdown(f"- {item}")

    st.subheader("💡 Ideal Answer")
    st.write(evaluation.ideal_answer)

    st.subheader("🧠 Key Concept Explained")
    st.write(result["explanation"])

    # NEXT QUESTION BUTTON
    if len(st.session_state.history) < st.session_state.total_questions:

        if st.button("Next Question ➡️", type="primary"):
            with st.spinner("Generating the next question..."):
                try:
                    history_text = "\n".join(
                        [
                            f"Question: {item['question']}\n"
                            f"Candidate answer: {item['answer']}\n"
                            f"Score: {item['score']}/10"
                            for item in st.session_state.history
                        ]
                    )

                    next_question = question_chain.invoke({
                        "topic": st.session_state.topic,
                        "difficulty": st.session_state.difficulty,
                        "history": history_text
                    })

                    st.session_state.question = next_question
                    st.session_state.question_number += 1
                    st.session_state.last_result = None

                    st.rerun()

                except Exception as e:
                    st.error(f"Could not generate next question: {e}")

    else:
        st.success("You have answered all the selected questions!")

        if st.button("Finish Interview", type="primary"):
            st.session_state.interview_complete = True
            st.session_state.question = None
            st.rerun()

if st.session_state.interview_complete:
    st.divider()
    st.header("🎉 Interview Completed!")

    scores = [
        item["score"]
        for item in st.session_state.history
    ]

    if scores:
        average_score = sum(scores) / len(scores)

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Average Score",
                f"{average_score:.1f}/10"
            )

        with col2:
            st.metric(
                "Questions Completed",
                len(scores)
            )

    st.write(
        f"Topic: **{st.session_state.topic}**"
    )

    st.write(
        "Review your interview history below to identify "
        "topics that need more practice."
    )



if st.session_state.history:
    with st.expander("📚 View Interview History"):
        for i, item in enumerate(
            st.session_state.history,
            start=1
        ):
            st.markdown(
                f"**Question {i}:** {item['question']}"
            )

            st.markdown(
                f"**Your Answer:** {item['answer']}"
            )

            st.markdown(
                f"**Score:** {item['score']}/10"
            )

            st.divider()