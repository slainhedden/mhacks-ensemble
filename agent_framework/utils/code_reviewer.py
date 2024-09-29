import os
from typing import Dict, Any, List
from difflib import unified_diff

class CodeReviewer:
    def review_changes(self, task_description: str, new_content: Dict[str, Any], file_history: List[str], sandbox_result: str = None) -> Dict[str, Any]:
        try:
            if not file_history:
                return {"approved": True, "comments": "New file created."}

            old_content = file_history[-1]
            new_content_str = new_content.get("content", "")
            
            if not new_content_str:
                return {"approved": False, "comments": "No new content provided for review."}

            diff = list(unified_diff(
                old_content.splitlines(keepends=True),
                new_content_str.splitlines(keepends=True),
                fromfile="previous_version",
                tofile="new_version",
                n=3
            ))

            if not diff:
                return {"approved": True, "comments": "No changes detected."}

            # Implement more sophisticated review logic here
            # For now, we'll just check if the changes align with the task description
            changes_align_with_task = all(line.lower() in task_description.lower() for line in diff if line.startswith('+'))

            if changes_align_with_task:
                return {"approved": True, "comments": "Changes align with the task description."}
            else:
                return {"approved": False, "comments": "Changes do not seem to align with the task description. Please review and adjust."}

            # Consider sandbox results in the review
            if sandbox_result:
                sandbox_success = "All tests passed" in sandbox_result
                if sandbox_success:
                    return {"approved": True, "comments": f"Changes align with the task description and pass all tests. Sandbox result: {sandbox_result}"}
                else:
                    return {"approved": False, "comments": f"Changes do not pass all tests. Please review and fix. Sandbox result: {sandbox_result}"}
        except Exception as e:
            return {"approved": False, "comments": f"Error during code review: {str(e)}"}

