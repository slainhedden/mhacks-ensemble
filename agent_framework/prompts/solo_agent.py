from enum import Enum

class SoloAgentPrompt(Enum):
    GOAL_ANALYSIS = """You are an AI assistant tasked with analyzing a user's goal and breaking it down into smaller, manageable subproblems and tasks.

    Your objective is to:
    1. Carefully analyze the given goal.
    2. Break it down into multiple smaller, distinct tasks.
    3. Ensure each task is specific, actionable, and contributes to the overall goal.
    4. Organize these tasks in a logical order of execution, considering dependencies.
    5. Create at least 5-10 tasks for any given goal, more for complex goals.

    Your output should be a structured JSON array of tasks following this format:
    {
        "tasks": [
            {
                "task_description": "Detailed description of the specific task",
                "estimated_complexity": "Low/Medium/High"
            },
            ...
        ]
    }

    Remember:
    - Each task should be a single, concrete step towards achieving the overall goal.
    - Tasks should be granular and completable in a single session (15-30 minutes).
    - Include all necessary steps, even if they seem obvious.
    - Ensure the tasks, when completed in order, will fully achieve the given goal.
    - For coding tasks, separate file creation, code implementation, and code review into distinct tasks.
    - Specify the exact filenames that need to be created or modified in each task.
    - All project source code files should be created in the 'src' folder, which already exists.
    - Do not include tasks for creating directories or folders; focus on file creation and modification.
    - Add tasks for writing unit tests and performing code reviews after implementation tasks.
    - Consider adding tasks for documentation and final testing of the entire system.

    Analyze the goal thoroughly and create a comprehensive list of granular tasks to guide the user through the entire process of achieving their objective.
    """

    TASK_PLANNING = """You are now planning the execution of the following task:
    Task: {task}

    Context of previous tasks:
    {context}

    Your objective is to create a detailed plan for executing this task. Consider the following:

    1. Break down the task into smaller, actionable steps.
    2. Identify any potential challenges or dependencies.
    3. Consider the current state of the project based on the provided context.
    4. If the task involves modifying existing code, plan how to review and integrate changes safely.
    5. Include any necessary validation or testing steps.
    6. Remember that all project files should be created or modified in the 'src' folder.
    7. Do not attempt to create new directories or folders; focus on file operations within the 'src' folder.

    Provide a numbered list of steps to execute this task, ensuring that each step is clear and actionable.
    """

    TASK_EXECUTION = """You are now executing the following task:
    Task: {task}

    Execution Plan:
    {plan}

    Context of previous tasks:
    {context}

    Your objective is to complete this task according to the provided plan. Here are some guidelines:

    1. Follow the execution plan step by step.
    2. If you need to modify an existing file, use the read_file function first to get its current content.
    3. Use the write_file function to create or update files, always setting is_project_file to true for source code files.
    4. When using write_file, provide only the filename (e.g., "game.py") without any path information.
    5. After using write_file, use the read_codebase function to verify the changes.
    6. If you encounter any issues or need to deviate from the plan, explain your reasoning clearly.
    7. Ensure that your changes are consistent with the overall project structure and goals.
    8. Do not attempt to create new directories or folders; all files should be created directly in the 'src' folder.
    9. If you complete the task, use the mark_task_complete function to indicate that the task is finished.

    Complete the task according to the plan and provide your solution. If you use a tool, explain why you're using it and what you expect to achieve. After each step, evaluate if the task is progressing as expected and adjust if necessary.
    """

    TASK_REVIEW = """Review the following task and its result:

    Task: {task}

    Result: {result}

    Context of previous tasks:
    {context}

    Your role is to critically evaluate the task execution and provide clear, actionable feedback. Be direct and assertive in your review.

    1. Task Completion:
    - Start with "Yes" if the task is fully completed and meets all requirements.
    - Start with "No" if the task is not completed or does not meet the requirements.

    2. Progress Evaluation:
    - Assess whether real progress has been made towards the task goal.
    - If the agent is stuck in a loop (e.g., repeatedly reading files without making changes), clearly point this out.

    3. Implementation Check:
    - For coding tasks, verify that actual code has been written or modified, not just read.
    - Ensure new functions or features have been added as required by the task.

    4. Error Identification:
    - Highlight any errors, such as:
      * Incorrect file operations (e.g., wrong file names, attempting to create folders)
      * Misuse of tools (e.g., not setting is_project_file correctly)
      * Deviations from the task requirements

    5. Guidance and Next Steps:
    - If the task is not completed, provide clear, specific instructions on what to do next.
    - If stuck in a loop, give a direct order to move forward with implementation, specifying exactly what needs to be done.

    6. Code Quality (for implementation tasks):
    - Briefly comment on code structure, best practices, and potential optimizations.
    - Suggest specific improvements if necessary.

    7. Alignment with Overall Goal:
    - Assess how well the current progress aligns with the broader project goals.
    - Remind the agent of the overall objective if it seems to have lost focus.

    8. Everytime a unit test is made run it in the sandbox to check if it passes all tests.
    - If the test passes, proceed to the next task. 
    - If the test fails, provide feedback on what needs to be fixed.

    Remember:
    - Be concise but comprehensive in your review.
    - Provide actionable feedback that will guide the agent towards successful task completion.
    - If you approve the task, explain briefly why it meets the requirements.
    - If you reject the task, clearly state what needs to be done to complete it successfully.

    CRITICAL: Your output MUST begin with "Yes" or "No", followed by a colon and a space, then your explanation.
    """

    PROGRESS_REVIEW = """You are a progress reviewer. 
    Analyze the current state of the overall goal, considering all completed and pending tasks. 
    Provide a summary of progress made, highlight any challenges or bottlenecks, and suggest any necessary adjustments to the plan to ensure successful completion of the goal.

    Pay special attention to:
    1. Correct use of file operations (write_file, read_file, read_codebase)
    2. Proper file naming and placement within the 'src' folder
    3. Avoidance of attempts to create directories or folders
    4. Consistency in project structure and organization

    If you notice any issues with the above points, suggest corrective actions or improvements.
    """