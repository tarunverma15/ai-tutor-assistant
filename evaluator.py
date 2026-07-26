from groq import Groq
import json


class Evaluator:

    def __init__(self, client: Groq, model: str):
        self.client = client
        self.model = model

    def evaluate(self, quiz_data, user_answer):

        question_type = quiz_data["question_type"]

        # ---------------- MCQ ---------------- #

        if question_type == "MCQ":

            correct = quiz_data["correct_answer"].strip().upper()

            # st.radio returns the FULL option text (e.g. "B) Some option"),
            # not just the letter, so extract the leading letter before comparing.
            user_choice = user_answer.strip()
            user_letter = user_choice[0].upper() if user_choice else ""

            if user_letter == correct:

                return {
                    "correct": True,
                    "marks": 1,
                    "feedback": "Correct!",
                    "explanation": quiz_data.get("model_answer", "No explanation available.")
                }

            # Show the full correct option text in feedback, not just the letter
            correct_option_text = next(
                (
                    opt for opt in quiz_data.get("options", [])
                    if opt.strip().upper().startswith(correct)
                ),
                correct
            )

            return {
                "correct": False,
                "marks": 0,
                "feedback": f"Wrong! Correct Answer: {correct_option_text}",
                "explanation": quiz_data.get("model_answer", "No explanation available.")
            }

        # -------- True / False -------- #

        elif question_type == "True/False":

            correct = quiz_data["correct_answer"].strip().lower()

            if user_answer.strip().lower() == correct:

                return {
                    "correct": True,
                    "marks": 1,
                    "feedback": "Correct!",
                    "explanation": quiz_data.get("model_answer", "No explanation available.")
                }

            return {
                "correct": False,
                "marks": 0,
                "feedback": f"Correct Answer: {correct}",
                "explanation": quiz_data.get("model_answer", "No explanation available.")
            }

        # -------- Fill in the Blank -------- #

        elif question_type == "Fill in the Blanks":

            correct = quiz_data["correct_answer"].strip().lower()

            if user_answer.strip().lower() == correct:

                return {
                    "correct": True,
                    "marks": 1,
                    "feedback": "Correct!",
                    "explanation": quiz_data.get("model_answer", "No explanation available.")
                }

            return {
                "correct": False,
                "marks": 0,
                "feedback": f"Correct Answer: {quiz_data['correct_answer']}",
                "explanation": quiz_data.get("model_answer", "No explanation available.")
            }

        # -------- One Word -------- #

        elif question_type == "One Word":

            correct = quiz_data["correct_answer"].strip().lower()

            if user_answer.strip().lower() == correct:

                return {
                    "correct": True,
                    "marks": 2,
                    "feedback": "Correct!",
                    "explanation": quiz_data.get("model_answer", "No explanation available.")
                }

            return {
                "correct": False,
                "marks": 0,
                "feedback": f"Correct Answer: {quiz_data['correct_answer']}",
                "explanation": quiz_data.get("model_answer", "No explanation available.")
            }

        # -------- Short & Long Answer -------- #

        elif question_type in ["Short Answer", "Long Answer"]:

            system_prompt = """
You are an expert examiner.

Evaluate the student's answer.

Return ONLY this JSON.

{
    "marks":4,
    "max_marks":5,
    "feedback":"...",
    "missing_points":"...",
    "ideal_answer":"..."
}
"""

            if question_type == "Short Answer":
                max_marks = 5
            else:
                max_marks = 10

            user_prompt = f"""
Question:

{quiz_data["question"]}

Ideal Answer:

{quiz_data.get("model_answer", "No explanation available.")}

Student Answer:

{user_answer}

Maximum Marks:

{max_marks}

Evaluate fairly.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            

            result = json.loads(response.choices[0].message.content)

            result["correct"] = None

            return result