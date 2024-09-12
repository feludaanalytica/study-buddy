import os
from constants import bot, db, cursor
from study_buddy.vectordb import RAG


def check_course_notes(message):
    query = message.text.lower().split()
    if (query[0] == "get" and query[1] == "notes"):
        return True
    else:
        return False


# Command to list courses
@bot.message_handler(func=check_course_notes)
def get_notes_prompt(message):
    chat_id = message.chat.id
    cursor.execute("SELECT course_name FROM courses WHERE chat_id = ?",
                   (chat_id, ))
    courses = cursor.fetchall()

    if courses:
        course_list = "\n".join([course[0] for course in courses])
        bot.send_message(
            chat_id,
            f"Please specify the course name to retrieve notes from:\n{course_list}"
        )
        bot.register_next_step_handler(message, retrieve_notes)
    else:
        bot.send_message(
            chat_id,
            "You don't have any courses yet. Create one using create course first."
        )


def retrieve_notes(message):
    chat_id = message.chat.id
    course_name = message.text

    # Get the course ID from the database
    cursor.execute(
        "SELECT id FROM courses WHERE chat_id = ? AND course_name = ?",
        (chat_id, course_name))
    course = cursor.fetchone()

    if course:
        course_id = course[0]

        # Fetch all notes associated with the course
        cursor.execute(
            "SELECT file_name, file_path FROM notes WHERE course_id = ?",
            (course_id, ))
        notes = cursor.fetchall()

        if notes:
            bot.send_message(chat_id,
                             f"Here are the notes for '{course_name}':")
            for note in notes:
                file_name, file_path = note

                # Send each file back to the user
                with open(file_path, 'rb') as file:
                    bot.send_document(chat_id, file)
        else:
            bot.send_message(
                chat_id, f"No notes found for the course '{course_name}'.")
    else:
        bot.send_message(
            chat_id,
            "Course not found. Please check the course name and try again.")


# Function to check if the user entered "create course notes"
def create_notes_request(message):
    query = message.text.split()
    # Ensure the message starts with "create course"
    if query[0].lower() == "create" and query[1].lower() == "note":
        return True
    else:
        return False


# Command to upload files (notes)
@bot.message_handler(func=create_notes_request)
def create_notes(message):
    chat_id = message.chat.id
    cursor.execute("SELECT course_name FROM courses WHERE chat_id = ?",
                   (chat_id, ))
    courses = cursor.fetchall()

    if courses:
        course_list = "\n".join([course[0] for course in courses])
        bot.send_message(
            chat_id,
            f"Please specify the course name for which you'd like to upload a note:\n{course_list}"
        )
        bot.register_next_step_handler(message, ask_for_file)
    else:
        bot.send_message(
            chat_id,
            "You don't have any courses yet. Create one using create course first."
        )


def ask_for_file(message):
    chat_id = message.chat.id
    course_name = message.text

    cursor.execute(
        "SELECT id FROM courses WHERE chat_id = ? AND course_name = ?",
        (chat_id, course_name))
    course = cursor.fetchone()

    if course:
        course_id = course[0]
        bot.send_message(
            chat_id,
            f"Great! Now send the file (image, PDF, etc.) for '{course_name}'."
        )
        # bot.register_next_step_handler(message, receive_file, course_id)
        # Use a lambda to pass course_id along with message to receive_file
        bot.register_next_step_handler(
            message, lambda msg: receive_file(msg, course_id))
    else:
        bot.send_message(
            chat_id,
            "Course not found. Please check the course name and try again.")


# Function to handle file uploads
@bot.message_handler(content_types=['document', 'photo'])
def receive_file(message, course_id):
    chat_id = message.chat.id

    # Handle document (PDF, etc.)
    if message.content_type == 'document':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_name = message.document.file_name
        course_path = f"courses/{chat_id}/{course_id}/"
        os.makedirs(course_path, exist_ok=True)

        file_path = os.path.join(course_path, file_name)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Save the file information in the database
        cursor.execute(
            "INSERT INTO notes (course_id, file_name, file_path) VALUES (?, ?, ?)",
            (course_id, file_name, file_path))
        db.commit()

        # Store pdf embeddings in Qdrant
        collection_name = f"note_{chat_id}_{course_id}"
        rag = RAG()
        rag.vector_store(collection_name, file_path)

        bot.send_message(
            chat_id, f"File '{file_name}' has been uploaded to the course.")

    # Handle photo
    elif message.content_type == 'photo':
        file_info = bot.get_file(
            message.photo[-1].file_id)  # Get highest resolution
        downloaded_file = bot.download_file(file_info.file_path)

        file_name = f"image_{message.message_id}.jpg"
        course_path = f"courses/{chat_id}/{course_id}/"
        os.makedirs(course_path, exist_ok=True)

        file_path = os.path.join(course_path, file_name)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Save the image information in the database
        cursor.execute(
            "INSERT INTO notes (course_id, file_name, file_path) VALUES (?, ?, ?)",
            (course_id, file_name, file_path))
        db.commit()

        bot.send_message(chat_id, "Image has been uploaded to the course.")
        bot.send_message(
            chat_id,
            "Would you like to add more notes to this course? Reply with 'yes' or 'no'."
        )
        bot.register_next_step_handler(message, add_more_notes, course_id)


def add_more_notes(message, course_id):
    chat_id = message.chat.id
    if message.content_type in ['document', 'photo']:
        bot.send_message(chat_id, "Please reply with 'yes' or 'no'.")
        bot.register_next_step_handler(message, add_more_notes, course_id)
        return
    yes_no_response = message.text.strip().lower()

    if yes_no_response == "yes":
        bot.register_next_step_handler(message, receive_file, course_id)
    elif yes_no_response == "no":
        bot.send_message(
            chat_id,
            "Okay, no notes added. You can add notes later using the \'create note\' command."
        )
    else:
        bot.send_message(chat_id, "Please reply with 'yes' or 'no'.")
        bot.register_next_step_handler(message, add_more_notes, course_id)


def delete_note_request(message):
    query = message.text.lower().split()
    if (query[0] == "delete" and query[1] == "note"):
        return True
    else:
        return False


@bot.message_handler(func=delete_note_request)
def delete_note_prompt(message):
    chat_id = message.chat.id

    # Fetch and show all courses for the user to choose from
    cursor.execute("SELECT course_name FROM courses WHERE chat_id = ?",
                   (chat_id, ))
    courses = cursor.fetchall()

    if courses:
        course_list = "\n".join([course[0] for course in courses])
        bot.send_message(
            chat_id,
            f"Please specify the course name to delete a note from:\n{course_list}"
        )
        bot.register_next_step_handler(message, select_note_to_delete)
    else:
        bot.send_message(chat_id,
                         "You don't have any courses to delete notes from.")


def select_note_to_delete(message):
    chat_id = message.chat.id
    course_name = message.text

    # Check if the course exists
    cursor.execute(
        "SELECT id FROM courses WHERE chat_id = ? AND course_name = ?",
        (chat_id, course_name))
    course = cursor.fetchone()

    if course:
        course_id = course[0]

        # Fetch notes for the selected course
        cursor.execute("SELECT id, file_name FROM notes WHERE course_id = ?",
                       (course_id, ))
        notes = cursor.fetchall()

        if notes:
            note_list = "\n".join([f"{note[0]}: {note[1]}" for note in notes])
            bot.send_message(
                chat_id, f"Please specify the note ID to delete:\n{note_list}")
            bot.register_next_step_handler(message, delete_selected_note,
                                           course_id)
        else:
            bot.send_message(chat_id,
                             f"No notes found for course '{course_name}'.")
    else:
        bot.send_message(
            chat_id,
            f"Course '{course_name}' not found. Please check the name and try again."
        )


def delete_selected_note(message, course_id):
    note_id = message.text  # User specifies the note ID to delete

    # Check if the note exists
    cursor.execute(
        "SELECT file_name FROM notes WHERE id = ? AND course_id = ?",
        (note_id, course_id))
    note = cursor.fetchone()

    if note:
        # Delete the note from the database
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id, ))
        db.commit()

        bot.send_message(message.chat.id,
                         f"Note '{note[0]}' has been deleted.")
    else:
        bot.send_message(message.chat.id, "Invalid note ID. Please try again.")
