import os
import json
import csv
import argparse
from cloc import cloc
import matplotlib.pyplot as plt

# 1. Configurations
CONFIG = {
    "default_directory": "./my_project",
    "output_formats": ["json", "csv", "markdown"],
    "min_comment_ratio": 0.2,  # Minimum comments/code ratio
}

# 2. Analyze Code Using cloc
def analyze_code(directory):
    print(f"Analyzing code in {directory}...")
    result = cloc([directory], options={"json": True})
    return json.loads(result)

# 3. Process Data
def process_data(data):
    summary = {
        "total_files": data["header"]["n_files"],
        "languages": [],
        "total_lines": data["header"]["n_lines"],
    }
    for language, stats in data["languages"].items():
        summary["languages"].append({
            "name": language,
            "code": stats["code"],
            "comments": stats["comment"],
            "blank": stats["blank"],
        })
    return summary

# 4. Generate Reports
def generate_reports(data, output_dir):
    # JSON Report
    with open(os.path.join(output_dir, "report.json"), "w") as json_file:
        json.dump(data, json_file, indent=4)
    print("JSON report generated.")

    # CSV Report
    csv_file = os.path.join(output_dir, "report.csv")
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Language", "Code", "Comments", "Blank"])
        for lang in data["languages"]:
            writer.writerow([lang["name"], lang["code"], lang["comments"], lang["blank"]])
    print("CSV report generated.")

# 5. Visualize Data
def visualize_data(data):
    languages = [lang["name"] for lang in data["languages"]]
    code_lines = [lang["code"] for lang in data["languages"]]
    plt.bar(languages, code_lines)
    plt.title("Code Lines by Language")
    plt.xlabel("Languages")
    plt.ylabel("Code Lines")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# 6. Main Program
def main():
    parser = argparse.ArgumentParser(description="Project Code Analyzer Tool")
    parser.add_argument("--directory", type=str, default=CONFIG["default_directory"], help="Project directory to analyze")
    parser.add_argument("--output", type=str, default="./reports", help="Directory to save reports")
    args = parser.parse_args()

    # Analyze Code
    data = analyze_code(args.directory)
    processed_data = process_data(data)

    # Generate Reports
    os.makedirs(args.output, exist_ok=True)
    generate_reports(processed_data, args.output)

    # Visualize Results
    visualize_data(processed_data)
    # A long Python program that does nothing and produces no output

class SilentClass:
    def __init__(self):
        pass

    def method_one(self):
        pass

    def method_two(self):
        pass

    def method_three(self):
        pass

    def method_four(self):
        pass


def helper_function_one():
    pass


def helper_function_two():
    pass


def helper_function_three():
    pass


def nested_functions():
    def nested_one():
        pass

    def nested_two():
        pass

    def nested_three():
        pass

    pass


def recursive_function(n):
    if n <= 0:
        return
    recursive_function(n - 1)


class AnotherSilentClass:
    def __init__(self):
        self.attribute = None

    def do_nothing(self):
        pass

    def do_more_nothing(self):
        pass

    @staticmethod
    def static_silence():
        pass


def silent_loops():
    for _ in range(100):
        pass

    while False:
        pass


def deep_nesting():
    if True:
        if True:
            if True:
                pass


def main():
    instance = SilentClass()
    another_instance = AnotherSilentClass()
    instance.method_one()
    instance.method_two()
    another_instance.do_nothing()
    helper_function_one()
    helper_function_two()
    helper_function_three()
    nested_functions()
    recursive_function(10)
    silent_loops()
    deep_nesting()
# A long Python program that does nothing and produces no output

class SilentClass:
    def __init__(self):
        pass

    def method_one(self):
        pass

    def method_two(self):
        pass

    def method_three(self):
        pass

    def method_four(self):
        pass


def helper_function_one():
    pass


def helper_function_two():
    pass


def helper_function_three():
    pass


def nested_functions():
    def nested_one():
        pass

    def nested_two():
        pass

    def nested_three():
        pass

    pass


def recursive_function(n):
    if n <= 0:
        return
    recursive_function(n - 1)


class AnotherSilentClass:
    def __init__(self):
        self.attribute = None

    def do_nothing(self):
        pass

    def do_more_nothing(self):
        pass

    @staticmethod
    def static_silence():
        pass


def silent_loops():
    for _ in range(100):
        pass

    while False:
        pass


def deep_nesting():
    if True:
        if True:
            if True:
                pass


def main():
    instance = SilentClass()
    another_instance = AnotherSilentClass()
    instance.method_one()
    instance.method_two()
    another_instance.do_nothing()
    helper_function_one()
    helper_function_two()
    helper_function_three()
    nested_functions()
    recursive_function(10)
    silent_loops()
    deep_nesting()




if __name__ == "__main__":
    main()
