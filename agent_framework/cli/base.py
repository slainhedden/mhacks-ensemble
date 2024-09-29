import blessed
from queue import Queue
from threading import Thread, Event

class BasicCLI:
    def __init__(self):
        self.term = blessed.Terminal()
        self.update_queue = Queue()
        self.should_exit = Event()
        self.current_goal = ""
        self.tasks = []
        self.current_task = ""
        self.last_output = ""
        self.goal_input_event = Event()
        self.user_goal = ""
        self.input_lock = Event()

    def start(self):
        with self.term.fullscreen(), self.term.cbreak():
            self.render_thread = Thread(target=self.render_loop)
            self.render_thread.start()
            self.input_loop()

    def stop(self):
        self.should_exit.set()
        self.render_thread.join()

    def render_loop(self):
        while not self.should_exit.is_set():
            if not self.input_lock.is_set():
                self.render_screen()
            self.process_updates()
            self.should_exit.wait(timeout=0.1)

    def input_loop(self):
        while not self.should_exit.is_set():
            if not self.goal_input_event.is_set():
                self.get_user_goal()
            else:
                command = self.get_user_input("Enter command (q to quit): ")
                if command.lower() == 'q':
                    self.should_exit.set()

    def get_user_input(self, prompt):
        self.input_lock.set()
        with self.term.location(0, self.term.height - 1):
            print(self.term.clear_eol + self.term.white_on_black(prompt), end='', flush=True)
            user_input = input()
        self.input_lock.clear()
        return user_input

    def render_screen(self):
        print(self.term.home + self.term.clear)
        self.render_header()
        self.render_main_content()
        self.render_footer()

    def render_header(self):
        print(self.term.black_on_white(self.term.center("Multi-Agent Framework CLI")))
        print(self.term.black_on_white(self.term.center(f"Current Goal: {self.current_goal[:50]}...")))

    def render_main_content(self):
        print(self.term.move_y(3) + self.term.bold("Tasks:"))
        for i, task in enumerate(self.tasks[-5:], 1):  # Show last 5 tasks
            print(f"{i}. {task[:50]}...")
        
        print("\n" + self.term.bold("Current Task:"))
        print(self.current_task[:50] + "...")
        
        print("\n" + self.term.bold("Last Output:"))
        print(self.last_output[:100] + "...")

    def render_footer(self):
        print(self.term.move_y(self.term.height - 2) + self.term.center("Press 'q' to quit"))

    def process_updates(self):
        while not self.update_queue.empty():
            update = self.update_queue.get()
            if update['type'] == 'goal':
                self.current_goal = update['content']
            elif update['type'] == 'task':
                self.tasks.append(update['content'])
                self.current_task = update['content']
            elif update['type'] == 'output':
                self.last_output = update['content']

    def update(self, update_type, content):
        self.update_queue.put({'type': update_type, 'content': content})

    def get_user_goal(self):
        self.input_lock.set()
        with self.term.location(0, self.term.height - 1):
            print(self.term.clear_eol + self.term.white_on_black("Enter your goal: "), end='', flush=True)
            self.user_goal = input()
        self.input_lock.clear()
        self.goal_input_event.set()
        return self.user_goal

def main():
    cli = BasicCLI()
    cli.start()

if __name__ == "__main__":
    main()