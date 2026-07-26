from groq import Groq


class Explanation:

    def __init__(self, client: Groq, model: str):
        self.client = client
        self.model = model

    def explain(self, quiz_data):

        question_type = quiz_data["question_type"]

        if question_type == "MCQ":

            prompt = f"""
Question:
{quiz_data["question"]}

Options:
{"\n".join(quiz_data["options"])}

Correct Option:
{quiz_data["correct_answer"]}

Explain:

1. Why the correct option is correct.
2. Why the other options are incorrect.
3. Keep the explanation under 120 words.

Return only plain text.
"""

        elif question_type == "True/False":

            prompt = f"""
Statement:

{quiz_data["question"]}

Correct Answer:

{quiz_data["correct_answer"]}

Explain why this statement is
True or False.

Maximum 100 words.
"""

        elif question_type == "Fill in the Blanks":

            prompt = f"""
Question:

{quiz_data["question"]}

Correct Answer:

{quiz_data["correct_answer"]}

Explain why this word completes the sentence.

Maximum 100 words.
"""

        elif question_type == "One Word":

            prompt = f"""
Question:

{quiz_data["question"]}

Correct Answer:

{quiz_data["correct_answer"]}

Explain this concept in simple language.

Maximum 100 words.
"""

        else:

            prompt = f"""
Question:

{quiz_data["question"]}

Model Answer:

{quiz_data["model_answer"]}

Explain the answer in an easy way.

Mention the important points the student should remember.

Maximum 150 words.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content":
                    "You are an expert teacher who explains concepts in simple language."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content