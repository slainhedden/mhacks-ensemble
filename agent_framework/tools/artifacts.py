import os
from typing import Dict, Any

def run_artifact_review(project_dir: str, html_content: str, css_content: str, js_content: str) -> Dict[str, Any]:
    print("\n--- Human Review Required ---")
    print("Please review the following artifact contents:")
    
    print("\nHTML Content:")
    print(html_content)
    
    print("\nCSS Content:")
    print(css_content)
    
    print("\nJavaScript Content:")
    print(js_content)
    
    print("\nConsider the following aspects:")
    print("1. Functionality")
    print("2. Appearance")
    print("3. Code quality")
    print("4. Any issues or improvements needed")
    
    feedback = input("\nEnter your feedback: ")
    
    while True:
        try:
            rating = int(input("Rate the artifact from 1-5 (1 being poor, 5 being excellent): "))
            if 1 <= rating <= 5:
                break
            else:
                print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 5.")
    
    return {
        "feedback": feedback,
        "rating": rating,
        "reviewed_by": "Human"
    }

if __name__ == "__main__":
    # Example usage
    project_dir = os.path.join(os.getcwd(), "src")
    html_content = "<h1>Hello, World!</h1>"
    css_content = "h1 { color: blue; text-align: center; }"
    js_content = "console.log('JavaScript is running');"
    
    result = run_artifact_review(project_dir, html_content, css_content, js_content)
    print(result)