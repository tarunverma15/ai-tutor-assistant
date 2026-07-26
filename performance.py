from collections import defaultdict


class PerformanceAnalyzer:

    def __init__(self):
        self.total_questions = 0
        self.correct = 0
        self.wrong = 0

        self.topic_stats = defaultdict(lambda: {"correct": 0, "wrong": 0})
        self.difficulty_stats = defaultdict(lambda: {"correct": 0, "wrong": 0})
        self.question_type_stats = defaultdict(lambda: {"correct": 0, "wrong": 0})

    def update(self, quiz_data, result, difficulty):

        self.total_questions += 1

        topic = quiz_data.get("topic", "General")
        question_type = quiz_data["question_type"]

        is_correct = False

        if result.get("correct") is True:
            is_correct = True

        elif result.get("marks") is not None:

            if result["marks"] >= result.get("max_marks", 1) / 2:
                is_correct = True

        if is_correct:

            self.correct += 1

            self.topic_stats[topic]["correct"] += 1
            self.difficulty_stats[difficulty]["correct"] += 1
            self.question_type_stats[question_type]["correct"] += 1

        else:

            self.wrong += 1

            self.topic_stats[topic]["wrong"] += 1
            self.difficulty_stats[difficulty]["wrong"] += 1
            self.question_type_stats[question_type]["wrong"] += 1

    def show_report(self):

        print("\n")
        print("=" * 60)
        print("           PERFORMANCE REPORT")
        print("=" * 60)

        print(f"Total Questions : {self.total_questions}")
        print(f"Correct         : {self.correct}")
        print(f"Wrong           : {self.wrong}")

        accuracy = (self.correct / self.total_questions) * 100

        print(f"Accuracy        : {accuracy:.2f}%")

        if accuracy >= 90:
            grade = "A+"

        elif accuracy >= 80:
            grade = "A"

        elif accuracy >= 70:
            grade = "B"

        elif accuracy >= 60:
            grade = "C"

        else:
            grade = "Needs Improvement"

        print(f"Grade           : {grade}")

        print("\nTopic Analysis")

        for topic, stat in self.topic_stats.items():

            total = stat["correct"] + stat["wrong"]

            percent = (stat["correct"] / total) * 100

            print(f"{topic:25} {percent:.1f}%")

        print("\nDifficulty Analysis")

        for diff, stat in self.difficulty_stats.items():

            total = stat["correct"] + stat["wrong"]

            percent = (stat["correct"] / total) * 100

            print(f"{diff:15} {percent:.1f}%")

        print("\nQuestion Type Analysis")

        for qtype, stat in self.question_type_stats.items():

            total = stat["correct"] + stat["wrong"]

            percent = (stat["correct"] / total) * 100

            print(f"{qtype:20} {percent:.1f}%")

        print("=" * 60)