import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
import os
import random


# Flashcard object with question and answer
class Flashcard:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer


class Quiz:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz")
        self.root.geometry("800x600")

        # Flashcard data
        self.deck = []
        self.last_deleted_card = None
        self.last_deleted_index = None
        self.current_card = 0
        self.score = 0

        self.build_home_screen()

        self.load_flashcards()
        self.build_input_screen()
        self.build_quiz_screen()
        self.build_list_screen()
        self.build_tips_screen()

        self.show_home_frame()

    # =========================== UI CONSTRUCTION ===========================
    def build_home_screen(self):
        self.home_frame = ctk.CTkFrame(self.root, fg_color="transparent", corner_radius=0)
        self.home_inner = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        self.home_inner.pack(expand=True)

        ctk.CTkLabel(self.home_inner, text="Welcome to Flashcard Quiz!", font=("Calibri", 24)).pack(pady=30)
        ctk.CTkButton(self.home_inner, text="Create Flashcards", font=("Calibri", 16),
                      command=self.show_input_frame).pack(pady=10)

        self.home_start_button = ctk.CTkButton(self.home_inner, text="Start Quiz", font=("Calibri", 16),
                                               command=self.start_quiz)
        self.home_start_button.pack(pady=10)
        self.home_start_button.configure(state=ctk.DISABLED)

        ctk.CTkButton(self.home_inner, text="View Flashcards", font=("Calibri", 16),
                      command=self.show_flashcard_list).pack(pady=10)
        ctk.CTkButton(self.home_inner, text="Studying Tips", font=("Calibri", 16),
                      command=self.show_studying_tips).pack(pady=10)
        ctk.CTkButton(self.home_inner, text="Save Flashcards", font=("Calibri", 16), command=self.save_flashcards).pack(
            pady=10)

    def build_input_screen(self):
        self.input_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.input_inner = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.input_inner.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.input_inner, text="Add a Flashcard", font=("Calibri", 18)).pack(pady=10)
        ctk.CTkLabel(self.input_inner, text="Question", font=("Calibri", 14)).pack()
        self.question_entry = ctk.CTkEntry(self.input_inner, font=("Calibri", 14))
        self.question_entry.pack(pady=5)

        ctk.CTkLabel(self.input_inner, text="Answer", font=("Calibri", 14)).pack()
        self.answer_entry = ctk.CTkEntry(self.input_inner, font=("Calibri", 14))
        self.answer_entry.pack(pady=5)

        ctk.CTkButton(self.input_inner, text="Add Flashcard", font=("Calibri", 14), command=self.add_flashcard).pack(
            pady=10)
        ctk.CTkButton(self.input_inner, text="Back to Home", font=("Calibri", 14), command=self.show_home_frame).pack(
            pady=10)

    def build_quiz_screen(self):
        self.quiz_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.quiz_inner = ctk.CTkFrame(self.quiz_frame, fg_color="transparent")
        self.quiz_inner.place(relx=0.5, rely=0.5, anchor="center")

        self.quiz_question_label = ctk.CTkLabel(self.quiz_inner, text="", font=("Calibri", 16))
        self.quiz_question_label.pack(pady=20)

        self.quiz_answer_entry = ctk.CTkEntry(self.quiz_inner, font=("Calibri", 14))
        self.quiz_answer_entry.pack(pady=10)

        ctk.CTkButton(self.quiz_inner, text="Submit Answer", font=("Calibri", 14), command=self.check_answer).pack(
            pady=10)
        ctk.CTkButton(self.quiz_inner, text="Back to Home", font=("Calibri", 14), command=self.restart_quiz).pack(
            pady=10)

    def build_list_screen(self):
        self.timer_seconds = 0
        self.timer_running = False
        self.list_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.flashcard_index = 0
        self.flipped = False

        self.flashcard_label = ctk.CTkLabel(self.list_frame, text="", font=("Calibri", 36), wraplength=700,
                                            justify="center")
        self.flashcard_label.pack(pady=30)

        # Timer UI moved to bottom — will reinsert after buttons

        nav_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        nav_frame.pack(pady=10)

        ctk.CTkButton(nav_frame, text="Previous", font=("Calibri", 14), command=self.prev_flashcard).pack(side="left",
                                                                                                          padx=10)
        ctk.CTkButton(nav_frame, text="Flip", font=("Calibri", 14), command=self.flip_flashcard).pack(side="left",
                                                                                                      padx=10)
        ctk.CTkButton(nav_frame, text="Next", font=("Calibri", 14), command=self.next_flashcard).pack(side="left",
                                                                                                      padx=10)

        ctk.CTkButton(self.list_frame, text="Delete This Flashcard", font=("Calibri", 14),
                      command=self.delete_flashcard).pack(pady=5)
        ctk.CTkButton(self.list_frame, text="Undo Delete", font=("Calibri", 14), command=self.undo_delete).pack(pady=5)
        ctk.CTkButton(self.list_frame, text="Back to Home", font=("Calibri", 14), command=self.show_home_frame).pack(
            pady=10)

        # Timer label and controls at the bottom
        self.timer_label = ctk.CTkLabel(self.list_frame, text="Timer: 00:00", font=("Calibri", 18))
        self.timer_label.pack(pady=5)

        timer_buttons = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        timer_buttons.pack(pady=5)
        ctk.CTkButton(timer_buttons, text="Start", font=("Calibri", 12), command=self.start_timer).pack(side="left",
                                                                                                        padx=5)
        ctk.CTkButton(timer_buttons, text="Pause", font=("Calibri", 12), command=self.pause_timer).pack(side="left",
                                                                                                        padx=5)
        ctk.CTkButton(timer_buttons, text="Reset", font=("Calibri", 12), command=self.reset_timer).pack(side="left",
                                                                                                        padx=5)

    def update_flashcard_view(self):
        if not self.deck:
            self.flashcard_label.configure(text="No flashcards available.")
            return

        card = self.deck[self.flashcard_index]
        if self.flipped:
            self.flashcard_label.configure(text=f"A: {card.answer}")
        else:
            self.flashcard_label.configure(text=f"Q: {card.question}")

    def flip_flashcard(self):
        if not self.deck:
            return

        # Animate shrink
        for size in range(36, 10, -2):
            self.flashcard_label.configure(font=("Calibri", size))
            self.flashcard_label.update()
            self.flashcard_label.after(10)

        self.flipped = not self.flipped
        self.update_flashcard_view()

        # Animate grow
        for size in range(10, 37, 2):
            self.flashcard_label.configure(font=("Calibri", size))
            self.flashcard_label.update()
            self.flashcard_label.after(10)

    def next_flashcard(self):
        if self.deck:
            self.flashcard_index = (self.flashcard_index + 1) % len(self.deck)
            self.flipped = False
            self.update_flashcard_view()

    def prev_flashcard(self):
        if self.deck:
            self.flashcard_index = (self.flashcard_index - 1) % len(self.deck)
            self.flipped = False
            self.update_flashcard_view()

    def show_flashcard_list(self):
        self.hide_all_frames()
        self.list_frame.pack(expand=True, fill="both")
        self.update_flashcard_view()

    def build_tips_screen(self):
        self.tips_frame = ctk.CTkFrame(self.root, corner_radius=0)
        ctk.CTkLabel(self.tips_frame, text="Studying Tips", font=("Calibri", 20)).pack(pady=10)

        self.tips_container = ctk.CTkFrame(self.tips_frame, fg_color="#f5f5dc", corner_radius=15)
        self.tips_container.pack(padx=20, pady=10, fill="both", expand=False)

        self.tips_scroll = tk.Scrollbar(self.tips_container)
        self.tips_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tips_textbox = tk.Text(self.tips_container, font=("Calibri", 24), wrap="word",
                                    yscrollcommand=self.tips_scroll.set, height=20, width=80, borderwidth=0,
                                    highlightthickness=0)
        self.tips_textbox.insert(tk.END, (
            "\n- Space out your study sessions instead of cramming."
            "\n- Use active recall (like flashcards!) to reinforce memory."
            "\n- Teach the content to someone else."
            "\n- Take breaks using the Pomodoro technique."
            "\n- Get enough sleep to help your brain consolidate learning."
        ))
        self.tips_textbox.config(state=tk.DISABLED)
        self.tips_textbox.pack(padx=10, pady=10, fill="both", expand=True)
        self.tips_scroll.config(command=self.tips_textbox.yview)

        ctk.CTkButton(self.tips_frame, text="Back to Home", font=("Calibri", 14), command=self.show_home_frame).pack(
            pady=10)

    # =========================== NAVIGATION ===========================
    def show_input_frame(self):
        self.hide_all_frames()
        self.input_frame.pack(expand=True, fill="both")

    def show_home_frame(self):
        self.hide_all_frames()
        self.home_frame.pack(expand=True, fill="both")

    def show_studying_tips(self):
        self.hide_all_frames()
        self.tips_frame.pack(expand=True, fill="both")

    def hide_all_frames(self):
        for frame in [self.home_frame, self.input_frame, self.quiz_frame, self.list_frame, self.tips_frame]:
            frame.pack_forget()

    # =========================== FLASHCARD LOGIC ===========================
    def add_flashcard(self):
        question = self.question_entry.get().strip()
        answer = self.answer_entry.get().strip()
        if question and answer:
            self.deck.append(Flashcard(question, answer))
            self.save_flashcards()
            messagebox.showinfo("Flashcard Added", "Flashcard has been added successfully!")
            self.question_entry.delete(0, tk.END)
            self.answer_entry.delete(0, tk.END)
            self.home_start_button.configure(state=ctk.NORMAL)
        else:
            messagebox.showwarning("Input Error", "Please enter both a question and an answer.")

    def delete_flashcard(self):
        index = self.flashcard_index if self.deck else None
        if index is not None and 0 <= index < len(self.deck):
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this flashcard?")
            if confirm:
                self.last_deleted_card = self.deck[index]
                self.last_deleted_index = index
                del self.deck[index]
                self.save_flashcards()
                self.show_flashcard_list()
                if not self.deck:
                    self.home_start_button.configure(state=ctk.DISABLED)

    def undo_delete(self):
        if self.last_deleted_card is not None and self.last_deleted_index is not None:
            self.deck.insert(self.last_deleted_index, self.last_deleted_card)
            self.last_deleted_card = None
            self.last_deleted_index = None
            self.save_flashcards()
            self.home_start_button.configure(state=ctk.NORMAL)
            self.update_flashcard_view()

    def save_flashcards(self):
        try:
            data = [{"question": card.question, "answer": card.answer} for card in self.deck]
            with open("flashcards.json", "w") as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving: {e}")

    def load_flashcards(self):
        if os.path.exists("flashcards.json"):
            try:
                with open("flashcards.json", "r") as file:
                    data = json.load(file)
                self.deck = [Flashcard(item["question"], item["answer"]) for item in data]
                if self.deck:
                    self.home_start_button.configure(state=ctk.NORMAL)
            except Exception as e:
                messagebox.showerror("Load Error", f"An error occurred while loading: {e}")

    def start_quiz(self):
        if not self.deck:
            messagebox.showwarning("No Flashcards", "Please add flashcards before starting the quiz.")
            return
        self.current_card = 0
        self.score = 0
        random.shuffle(self.deck)
        self.hide_all_frames()
        self.quiz_frame.pack(expand=True, fill="both")
        self.update_flashcard()

    def update_flashcard(self):
        self.quiz_question_label.configure(text=self.deck[self.current_card].question)
        self.quiz_answer_entry.delete(0, tk.END)

    def check_answer(self):
        user_answer = self.quiz_answer_entry.get().strip()
        correct_answer = self.deck[self.current_card].answer

        if user_answer.lower() == correct_answer.lower():
            self.score += 1
            messagebox.showinfo("Correct!", "That's right!")
        else:
            messagebox.showinfo("Try Again", f"The correct answer was: {correct_answer}")

        self.current_card += 1
        if self.current_card < len(self.deck):
            self.update_flashcard()
        else:
            messagebox.showinfo("Quiz Completed", f"You got {self.score} out of {len(self.deck)} correct.")
            self.show_home_frame()

    def update_timer(self):
        if self.timer_running:
            self.timer_seconds += 1
            minutes = self.timer_seconds // 60
            seconds = self.timer_seconds % 60
            self.timer_label.configure(text=f"Timer: {minutes:02}:{seconds:02}")
            self.root.after(1000, self.update_timer)

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def pause_timer(self):
        self.timer_running = False

    def reset_timer(self):
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_label.configure(text="Timer: 00:00")

    def restart_quiz(self):
        self.quiz_frame.pack_forget()
        self.show_home_frame()


# Run the app
if __name__ == '__main__':
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    quiz = Quiz(root)
    root.mainloop()
