from constants import bot, db, cursor
from study_buddy.notes import receive_file


# Function to check if the user entered "create course"
def create_courses_request(message):
    query = message.text.lower().split()
    # Ensure the message starts with "create course"
    if query[0] == "create" and query[1] == "course":
        return True
    else:
        return False


# Command to create a course
@bot.message_handler(func=create_courses_request)
def create_course(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     "Please send the name of the course you want to create:")
    bot.register_next_step_handler(message, save_course_name)


def save_course_name(message):
    chat_id = message.chat.id
    course_name = message.text

    # Check if the course already exists for this user
    cursor.execute(
        "SELECT * FROM courses WHERE chat_id = ? AND course_name = ?",
        (chat_id, course_name))
    if cursor.fetchone():
        bot.send_message(chat_id,
                         "Course already exists. Please choose another name.")
        bot.register_next_step_handler(message, save_course_name)
    else:
        # Insert the new course into the database
        cursor.execute(
            "INSERT INTO courses (chat_id, course_name) VALUES (?, ?)",
            (chat_id, course_name))
        db.commit()
        bot.send_message(
            chat_id,
            f"Course '{course_name}' created! Now you can upload notes (PDF, images, etc.) for this course."
        )
        # Now ask if they want to add notes
        bot.send_message(chat_id, "Would you like to add notes to this course? Reply with 'yes' or 'no'.")
        bot.register_next_step_handler(message, ask_to_add_notes, course_name)


def ask_to_add_notes(message, course_name):
    chat_id = message.chat.id
    response = message.text.strip().lower()

    if response == "yes":
        bot.send_message(
            chat_id,
            f"Great! Now send the file (image, PDF, etc.) for '{course_name}'."
        )
        cursor.execute(
            "SELECT id FROM courses WHERE chat_id = ? AND course_name = ?",
            (chat_id, course_name))
        course = cursor.fetchone()
        course_id = course[0]
        # Call the create_notes function from notes.py
        bot.register_next_step_handler(message, receive_file, course_id)
    elif response == "no":
        bot.send_message(chat_id, "Okay, no notes added. You can add notes later using the \'create note\' command.")
    else:
        bot.send_message(chat_id, "Please reply with 'yes' or 'no'.")
        bot.register_next_step_handler(message, ask_to_add_notes, course_name)


def get_course_list_request(message):
    query = message.text.lower().split()
    if (query[0] == "get" and query[1] == "courses"):
        return True
    else:
        return False


# Command to list courses
@bot.message_handler(func=get_course_list_request)
def get_course_list(message):
    chat_id = message.chat.id
    cursor.execute("SELECT course_name FROM courses WHERE chat_id = ?",
                   (chat_id, ))
    courses = cursor.fetchall()

    if courses:
        course_list = "\n".join([course[0] for course in courses])
        bot.send_message(chat_id, f"Here are your courses:\n{course_list}")
    else:
        bot.send_message(
            chat_id,
            "You haven't created any courses yet. Use /createcourse to get started."
        )


def delete_course_request(message):
    query = message.text.lower().split()
    if (query[0] == "delete" and query[1] == "course"):
        return True
    else:
        return False


# Command to list courses
@bot.message_handler(func=delete_course_request)
def delete_course_prompt(message):
    chat_id = message.chat.id

    cursor.execute("SELECT course_name FROM courses WHERE chat_id = ?",
                   (chat_id, ))
    courses = cursor.fetchall()

    if courses:
        course_list = "\n".join([course[0] for course in courses])
        bot.send_message(
            chat_id,
            f"Please specify the course name to delete:\n{course_list}")
        bot.register_next_step_handler(message, delete_course)
    else:
        bot.send_message(chat_id, "You don't have any courses to delete.")


def delete_course(message):
    chat_id = message.chat.id
    course_name = message.text  #.title()  # The course name to be deleted

    # Check if the course exists
    cursor.execute(
        "SELECT id FROM courses WHERE chat_id = ? AND course_name = ?",
        (chat_id, course_name))
    course = cursor.fetchone()

    if course:
        course_id = course[0]

        # Delete the notes associated with the course
        cursor.execute("DELETE FROM notes WHERE course_id = ?", (course_id, ))

        # Delete the course itself
        cursor.execute("DELETE FROM courses WHERE id = ?", (course_id, ))
        db.commit()

        bot.send_message(
            chat_id,
            f"Course '{course_name}' and its associated notes have been deleted."
        )
    else:
        bot.send_message(
            chat_id,
            f"Course '{course_name}' not found. Please check the name and try again."
        )
