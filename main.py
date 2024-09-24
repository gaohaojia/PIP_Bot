import threading
import fs_schedule
import fs_flask

if __name__ == "__main__":
    print("Starting PIP Bot")
    schedule_thread = threading.Thread(target=fs_schedule.start_schedule)
    flask_thread = threading.Thread(target=fs_flask.start_flask)
    schedule_thread.start()
    flask_thread.start()
