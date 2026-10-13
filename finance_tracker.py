# SMART SPENDING TRACKER
# A text menu program. The user types in what they spend, and the program:
#   - shows their expenses, sorted
#   - lets them delete or undo mistakes
#   - searches their expenses
#   - warns them when they spend more than usual in a category
#   - tells them how many weeks until they reach a savings goal
# Everything is saved in two text files (expenses.txt and settings.txt), so nothing is lost when it closes.
#
# HOW TO RUN:  py finance_tracker.py

# PART 1: SETUP

from datetime import date, timedelta #Loads two tools from Python's built in datetime library: date (a day) and timedelta (a length of time, like 7 days)

EXPENSES_FILE = "expenses.txt" #The name of the file where expenses are saved. Written in CAPITALS because it never changes
SETTINGS_FILE = "settings.txt" #The name of the file where the weekly budget and savings goal are saved
SEPARATOR = "|" #In the file, the parts of each expense are separated by this symbol, e.g. 4.5|Food|Coffee|2026-10-12|Want
OVERSPEND_LIMIT = 0.20 #0.20 means 20%. The program warns the user if they spend 20% more than normal


# PART 2: THE EXPENSE CLASSES
# Expense is the PARENT. Need and Want are CHILDREN: they get everything from Expense,

class Expense: #Starts the blueprint for an expense
    CATEGORIES = ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"] #The categories the user can choose from. This list belongs to the CLASS, so all expenses share one copy (a static variable)

    def __init__(self, amount, category, description, spent_on): #The CONSTRUCTOR. It runs automatically every time a new expense is made. "self" means "this expense"
        self.__amount = amount #Saves the amount inside this expense. The two underscores make it PRIVATE: other code cannot change it directly
        self.__category = category #Saves the category, e.g. "Food" (private)
        self.__description = description #Saves the description, e.g. "Coffee" (private)
        self.__spent_on = spent_on #Saves the date it was bought (private)

    def get_amount(self): #A GETTER: because the amount is private, other code reads it by calling this
        return self.__amount #Gives back the amount

    def get_category(self): #Getter for the category
        return self.__category #Gives back the category

    def get_description(self): #Getter for the description
        return self.__description #Gives back the description

    def get_date(self): #Getter for the date
        return self.__spent_on #Gives back the date

    def kind(self): #Says what type of expense this is. Need and Want replace this with their own version
        return "Expense" #The parent just says "Expense"

    def tip(self): #Gives a money saving tip. Need and Want replace this with their own version
        return "" #The parent gives no tip (an empty piece of text)

    def to_line(self): #Turns this expense into ONE line of text so it can be saved in the file
        return (str(self.__amount) + SEPARATOR + self.__category + SEPARATOR + self.__description
                + SEPARATOR + self.__spent_on.isoformat() + SEPARATOR + self.kind() + "\n") 


class Need(Expense): #A NEED is something essential, like groceries. (Expense) means Need gets everything from Expense (inheritance)
    def kind(self): #Replaces the parent's kind() (this is called overriding)
        return "Need" #A Need says "Need"

    def tip(self): #Replaces the parent's tip()
        return "Essential, no problem." #Needs are necessary, so no warning


class Want(Expense): #A WANT is something extra, like takeaway or games. Also gets everything from Expense
    def kind(self): #Replaces the parent's kind()
        return "Want" #A Want says "Want"

    def tip(self): #Replaces the parent's tip() with a useful warning
        yearly = self.get_amount() * 52 #There are 52 weeks in a year, so this is the cost if bought every week.
        return "If this is weekly, it costs " + money(yearly) + " a year." #Builds the tip, e.g. "If this is weekly, it costs EUR 182.00 a year."


def money(amount): #e.g. 3.5 becomes "EUR 3.50"
    return "EUR " + format(amount, ".2f") #format(amount, ".2f") always shows exactly 2 decimal places


def make_expense(kind, amount, category, description, spent_on): #Builds a Need or a Want, depending on the kind. A function that decides which object to build is called a FACTORY
    if kind == "Need": #If the user said it was a Need
        return Need(amount, category, description, spent_on) #build a Need object and give it back
    return Want(amount, category, description, spent_on) #Otherwise build a Want object


# PART 3: THE STACK (used for Undo)
# Every new expense is put on the stack, so Undo always removes the newest one.

class Stack: #Starts the blueprint for a stack
    def __init__(self): #Constructor: runs when a new stack is made
        self.__items = [] #An empty list that holds the items. The end of the list is the TOP of the stack. Private, so only the methods below can touch it

    def push(self, item): #Puts an item on top of the stack
        self.__items.append(item) #append() adds it to the end of the list (the top)

    def pop(self): #Takes the top item off the stack and gives it back
        if self.is_empty(): #If there is nothing in the stack
            return None #give back None (nothing) instead of crashing
        return self.__items.pop() #pop() removes the LAST item of the list and gives it back

    def peek(self): #Looks at the top item WITHOUT taking it off
        if self.is_empty(): #If there is nothing in the stack
            return None #there is nothing to look at
        return self.__items[len(self.__items) - 1] #The last position in a list is its length minus 1 (positions start at 0)

    def is_empty(self): #Checks if the stack has nothing in it
        return len(self.__items) == 0 #len() counts the items. Gives True if the count is 0, otherwise False


# PART 4: SAVING AND LOADING FILES

def load_expenses(): #Reads expenses.txt and turns every line back into an expense object
    expenses = [] #An empty list to put the expenses in
    file = None #No file is open yet. finally checks this before closing
    try: 
        file = open(EXPENSES_FILE, "r") 
        line = file.readline() 
        while line != "": #readline() gives back empty text "" when there are no more lines, so this repeats until the end of the file
            parts = line.strip().split(SEPARATOR) #e.g. ["4.5", "Food", "Coffee", "2026-10-12", "Want"]
            if len(parts) == 5: #Only use the line if it has all 5 pieces (a broken line is skipped instead of crashing the program)
                expenses.append(make_expense(parts[4], float(parts[0]), parts[1], parts[2], #Builds the expense: parts[4] is the kind, float() turns "4.5" back into the number 4.5
                                             date.fromisoformat(parts[3]))) 
            line = file.readline() #Reads the next line, then the loop checks again
    except FileNotFoundError: #This error happens the first time the program runs, because the file does not exist yet
        expenses = [] #So just start with no expenses
    finally: 
        if file is not None: 
            file.close() #close it, so it is not left open
    return expenses #Gives back the list of expenses


def save_expenses(expenses): #Writes every expense into expenses.txt, one per line
    file = open(EXPENSES_FILE, "w") #This creates the file if it does not exist and wipes the old contents
    try: 
        for expense in expenses: #Goes through every expense in the list, one at a time
            file.write(expense.to_line()) #Writes that expense as one line of text
    finally: #Always runs, even if writing failed
        file.close() #Closes the file. This is what actually finishes saving it


def load_settings(): #Reads settings.txt: the first line is the weekly budget, the second line is the savings goal
    settings = {"weekly_budget": 100.0, "goal": 500.0} #default values, used if there is no file yet
    file = None #No file open yet
    try: 
        file = open(SETTINGS_FILE, "r") 
        settings["weekly_budget"] = float(file.readline()) #Reads line 1 and turns it into a number
        settings["goal"] = float(file.readline()) #Reads line 2 and turns it into a number
    except (FileNotFoundError, ValueError): #If there is no file yet, OR a line is not a number
        settings = {"weekly_budget": 100.0, "goal": 500.0} #use the default values instead
    finally: 
        if file is not None: #If a file was opened
            file.close() #close it
    return settings #Gives back the settings


def save_settings(settings): #Writes the weekly budget and goal into settings.txt
    file = open(SETTINGS_FILE, "w") #Opens the file to write
    try: #Attempt to write
        file.write(str(settings["weekly_budget"]) + "\n") #Line 1: the budget 
        file.write(str(settings["goal"]) + "\n") #Line 2: the goal
    finally: #Always runs
        file.close() #Closes the file

# PART 5: ASKING THE USER FOR INPUT (with checks)
# Each of these keeps asking again until the answer is valid, so a typing mistake never crashes the program.

def ask_number(question): #Asks for a number and keeps asking until it is a number bigger than 0
    while True: #Repeats forever. The "return" inside is the only way out, and it only happens when the answer is valid
        try: #Attempt the next lines
            number = float(input(question)) 
            if number > 0: #Checks the number is more than 0
                return number #Valid, so give it back. This ends the loop and the function
            print("  Please enter a number bigger than 0.") #The number was 0 or negative, so the loop asks again
        except ValueError: #float() causes a ValueError if the text is not a number, e.g. "abc"
            print("  That is not a number, try again.") #Tells the user, then the loop asks again


def ask_choice(question, options): #Shows a numbered list of options and keeps asking until a valid number is typed
    for i in range(len(options)): #A counted loop: i goes 0, 1, 2 ... up to the number of options minus 1
        print("  " + str(i + 1) + ". " + options[i]) #Prints e.g. "  1. Food". We show i + 1 because people count from 1, not 0
    while True: #Keeps asking until the answer is valid
        answer = input(question).strip() #Reads what the user typed. 
        if answer.isdigit() and 1 <= int(answer) <= len(options): #isdigit() is True only for whole numbers. Then check the number is between 1 and the number of options
            return options[int(answer) - 1] #Gives back the chosen option. Minus 1 because the list starts at position 0
        print("  Please type a number from 1 to " + str(len(options)) + ".") #Not valid, so ask again


def ask_text(question): #Asks for some text and keeps asking until it is not empty and has no "|"
    while True: #Keeps asking until the answer is valid
        text = input(question).strip() #Reads what was typed, without spaces at the ends
        if text == "": #Nothing was typed
            print("  Please type something.") #Ask again
        elif SEPARATOR in text: #"in" checks if the "|" symbol is somewhere in the text. It would break the save file
            print("  Please do not use the | character.") #Ask again
        else: #The text is fine
            return text #Give it back


def ask_date(question): #Asks for a date. Pressing Enter without typing anything means today
    while True: #Keeps asking until the answer is valid
        answer = input(question).strip() #Reads what was typed
        if answer == "": #The user just pressed Enter
            return date.today() #so use today's date
        try: #Attempt to read the date
            day = date.fromisoformat(answer) #Turns "2026-10-12" into a date. Causes a ValueError if it is not a real date, e.g. "2026-13-40"
            if day <= date.today(): #Checks the date is today or earlier
                return day #Valid, give it back
            print("  The date cannot be in the future.") #A future date, so ask again
        except ValueError: #The text was not a real date
            print("  Use the format YYYY-MM-DD, e.g. 2026-10-12.") #Shows the correct format, then asks again

# PART 6: THE FEATURES (one function for each menu option)

def add_expense(expenses, undo_stack): #MENU OPTION 1: asks for a new expense and adds it
    description = ask_text("What did you buy? ") #e.g. "Coffee"
    amount = ask_number("How much was it (EUR)? ") #e.g. 3.5
    category = ask_choice("Category number: ", Expense.CATEGORIES) #Shows the categories list from the Expense class
    kind = ask_choice("Was it a Need or a Want? ", ["Need", "Want"]) #Need or Want
    spent_on = ask_date("Date (YYYY-MM-DD, press Enter for today): ") #The date
    expense = make_expense(kind, amount, category, description, spent_on) #Builds a Need or Want object with those answers
    expenses.append(expense) #Adds it to the list of all expenses
    undo_stack.push(expense) #Also puts it on the undo stack, so it can be undone
    print("Saved! " + expense.tip()) #Shows the tip. A Need and a Want give different tips 


def sort_value(expense, field): #Gives back the value an expense should be sorted by
    if field == "date": #If sorting by date
        return expense.get_date() #give back its date (dates can be compared: an earlier date counts as smaller)
    return expense.get_amount() #Otherwise give back its amount


def bubble_sort(items, field): #BUBBLE SORT: puts a copy of the list in order, biggest first
    #How it works: go along the list comparing each pair of neighbours, and swap them if they are in the wrong order.
    #After one full pass the smallest item has "bubbled" to the end. Repeat until a pass makes no swaps.
    items = items.copy() #Makes a copy, so the original list keeps its order
    n = len(items) #How many items there are
    for i in range(n - 1): #The outer loop: at most n - 1 passes are needed
        swapped = False #Remembers if anything was swapped in this pass
        for j in range(n - 1 - i): #The inner loop: compares item j with item j + 1. The last i items are already in place, so they are skipped
            if sort_value(items[j], field) < sort_value(items[j + 1], field): #If the left one is SMALLER than the right one, they are in the wrong order (we want biggest first)
                temp = items[j] #Keep the left item safe in a temporary variable
                items[j] = items[j + 1] #Copy the right item into the left spot
                items[j + 1] = temp #Put the saved left item into the right spot. The two are now swapped
                swapped = True #Remember that a swap happened
        if not swapped: #If a whole pass had no swaps, everything is already in order
            break #so stop early (saves time)
    return items #Gives back the sorted list


def print_expenses(expenses): #Prints a numbered list of expenses, lined up in columns
    for i in range(len(expenses)): #Goes through every position in the list
        e = expenses[i] #The expense at that position
        print("  " + str(i + 1) + ". " + e.get_date().isoformat() + "  " + e.get_description().ljust(18) #ljust(18) adds spaces to make the text 18 characters long, so the columns line up
              + e.get_category().ljust(14) + e.kind().ljust(6) + money(e.get_amount())) #The rest of the columns: category, Need/Want, amount


def show_expenses(expenses): #MENU OPTION 2: shows all expenses, sorted the way the user picks
    if len(expenses) == 0: #If the list is empty
        print("No expenses yet.") #Tell the user
        return [] #Give back an empty list
    order = ask_choice("Sort by: ", ["Newest first", "Highest amount"]) #Ask how to sort
    if order == "Newest first": #Sort by date
        shown = bubble_sort(expenses, "date") #Newest date first
    else: #Sort by amount
        shown = bubble_sort(expenses, "amount") #Biggest amount first
    print_expenses(shown) #Print the sorted list
    return shown #Give back the sorted list, so Delete can use the same numbers the user saw


def delete_expense(expenses): #MENU OPTION 3: deletes an expense the user typed wrong
    shown = show_expenses(expenses) #First show the numbered list
    if len(shown) == 0: #Nothing to delete
        return #Stop here
    answer = input("Number to delete (press Enter to cancel): ").strip() #Ask which number to delete
    if answer.isdigit() and 1 <= int(answer) <= len(shown): #Check it is a whole number in the right range
        expense = shown[int(answer) - 1] #Find that expense (minus 1 because lists start at 0)
        expenses.remove(expense) #Remove it from the list of all expenses
        print("Deleted " + expense.get_description() + ".") #Confirm it was deleted
    else: #Enter was pressed, or the number was wrong
        print("Nothing deleted.") #Nothing happens


def undo_last(expenses, undo_stack): #MENU OPTION 4: removes the expense that was added most recently
    if undo_stack.is_empty(): #Nothing has been added since the program opened
        print("Nothing to undo.") #Tell the user
        return #Stop here
    print("Undoing: " + undo_stack.peek().get_description()) #peek() looks at the top of the stack to show which one will be removed
    expense = undo_stack.pop() #pop() takes the top (newest) expense off the stack
    if expense in expenses: #Checks it is still in the list (it might have been deleted already)
        expenses.remove(expense) #Removes it


def search_expenses(expenses): #MENU OPTION 5: finds every expense whose description contains a word (LINEAR SEARCH)
    word = ask_text("Search for: ").lower() #The word to look for. lower() makes it lowercase so "COFFEE" and "coffee" both match
    found = [] #An empty list for the matches
    for e in expenses: #Checks EVERY expense, one by one, from start to end. That is what makes it a linear search
        if word in e.get_description().lower(): #"in" checks if the word appears anywhere inside the description
            found.append(e) #It matches, so add it to the results
    if len(found) == 0: #Nothing matched
        print("No matches.") #Tell the user
    else: #At least one match
        print_expenses(found) #Show the matches
        total = 0 #Start a running total at 0
        for e in found: #Goes through every match
            total = total + e.get_amount() #and adds its amount to the total
        print("  " + str(len(found)) + " matches, " + money(total) + " in total.") #e.g. "3 matches, EUR 10.50 in total."


def week_start(day): #Finds the Monday of the week that a date is in, so expenses can be grouped by week
    return day - timedelta(days=day.weekday()) #weekday() gives 0 for Monday up to 6 for Sunday, so going back that many days always lands on Monday


def check_overspending(expenses): #MENU OPTION 6: compares this week's spending with the user's normal spending
    this_week = week_start(date.today()) #The Monday of this week
    four_weeks_ago = this_week - timedelta(weeks=4) #The Monday 4 weeks before that
    this_week_totals = {} #Dictionary: category -> how much was spent THIS week
    past_totals = {} #Dictionary: category -> how much was spent in the 4 weeks BEFORE
    for e in expenses: #Goes through every expense once
        category = e.get_category() #Which category it is in
        if e.get_date() >= this_week: #If it was bought this week
            if category not in this_week_totals: #If this category is not in the dictionary yet
                this_week_totals[category] = 0 #add it with a total of 0
            this_week_totals[category] = this_week_totals[category] + e.get_amount() #Add this expense to the category's total
        elif e.get_date() >= four_weeks_ago: #Otherwise, if it was bought in the 4 weeks before
            if category not in past_totals: #If this category is not in the dictionary yet
                past_totals[category] = 0 #add it with a total of 0
            past_totals[category] = past_totals[category] + e.get_amount() #Add this expense to the category's total
    found = False #Remembers if any warning was shown
    for category in this_week_totals: #Goes through every category spent on this week
        spent = this_week_totals[category] #How much was spent on it this week
        average = 0 #The normal weekly amount, 0 if there is no history
        if category in past_totals: #If the user spent on this category in the past 4 weeks
            average = past_totals[category] / 4 #The normal weekly amount = 4 weeks total divided by 4
        if average > 0 and spent > average * (1 + OVERSPEND_LIMIT): #If there is a normal amount AND this week is more than 1.2 times it (20% more)
            percent = (spent - average) / average * 100 #How many percent more: (new - normal) / normal x 100
            print("  ! " + category + ": " + money(spent) + " this week, usually " #The warning, first half
                  + money(average) + " (" + str(round(percent)) + "% more)") #Second half. round() makes the percent a whole number
            found = True #A warning was shown
    if not found: #If no warning was shown at all
        print("  No overspending this week. Nice!") #Good news message


def weeks_to_goal(saved, goal, per_week, weeks): #Counts how many weeks until the goal is reached
    if saved >= goal: #STOPPING CASE 1: the goal has been reached
        return weeks #so give back how many weeks it took
    if weeks >= 520: #STOPPING CASE 2: after 520 weeks (10 years), give up. This stops the function calling itself forever
        return -1 #-1 is a signal meaning "more than 10 years"
    return weeks_to_goal(saved + per_week, goal, per_week, weeks + 1) #Not there yet: add one more week of saving and call itself again


def savings_progress(expenses, settings): #MENU OPTION 7: shows how much has been saved and when the goal will be reached
    budget = settings["weekly_budget"] #How much the user allows themselves to spend each week
    goal = settings["goal"] #How much they want to save
    if len(expenses) == 0: #No expenses yet
        print("Add some expenses first.") #Nothing to work out
        return #Stop here
    first_day = expenses[0].get_date() #Start by guessing the first expense is the earliest...
    for e in expenses: #...then check every expense
        if e.get_date() < first_day: #If one is earlier than the earliest so far
            first_day = e.get_date() #it becomes the new earliest
    this_week = week_start(date.today()) #Monday of this week. This week is not over yet, so it is not counted
    weeks = (this_week - week_start(first_day)).days // 7 #Number of FULL weeks since the first expense. Days between the two Mondays, divided by 7. // gives a whole number
    if weeks == 0: #Not even one full week yet
        print("Come back after your first full week.") #Not enough data
        return #Stop here
    spent = 0 #Running total of money spent in those full weeks
    for e in expenses: #Goes through every expense
        if e.get_date() < this_week: #Only count expenses from finished weeks
            spent = spent + e.get_amount() #Add it to the total
    saved = budget * weeks - spent #Money saved = what they were allowed to spend minus what they actually spent
    print("  Saved so far: " + money(saved) + " of " + money(goal)) #Shows the progress
    per_week = saved / weeks #Average amount saved each week
    if saved >= goal: #Already saved enough
        print("  Goal reached!") #Congratulations
    elif per_week <= 0: #Saving nothing, or spending more than the budget
        print("  You are not saving at the moment. Try to spend less than your budget.") #Advice
    else: #Saving something each week
        weeks_left = weeks_to_goal(saved, goal, per_week, 0) #Calls the recursive function above, starting at 0 weeks
        if weeks_left == -1: #The signal for "more than 10 years"
            print("  At this pace it would take more than 10 years.") 
        else: #A normal number of weeks
            print("  At " + money(per_week) + " a week you will reach your goal in " + str(weeks_left) + " weeks.") #The prediction


def change_settings(settings): #MENU OPTION 8: lets the user change their weekly budget and savings goal
    settings["weekly_budget"] = ask_number("Weekly budget (EUR): ") #New budget
    settings["goal"] = ask_number("Savings goal (EUR): ") #New goal
    print("Settings saved.") #Confirm

# PART 7: THE MAIN MENU 

def main(): #Runs the whole program
    expenses = load_expenses() #Loads the expenses saved last time (an empty list the first time)
    settings = load_settings() #Loads the budget and goal (default values the first time)
    undo_stack = Stack() #Makes a new, empty stack for Undo
    menu = ["Add expense", "Show expenses", "Delete an expense", "Undo last", "Search expenses", #The menu options, in order
            "Check overspending", "Savings progress", "Change budget and goal", "Quit"] #(the list carries on onto this line)
    running = True #While this is True the program keeps going
    while running: #Shows the menu again and again until running becomes False
        print("\n=== SMART SPENDING TRACKER ===") #The title. "\n" adds an empty line above it
        choice = ask_choice("Choose an option: ", menu) #Shows the menu and gets the user's valid choice
        if choice == "Add expense": #Option 1
            add_expense(expenses, undo_stack) #runs the add function
        elif choice == "Show expenses": #Option 2. elif means "else if": only checked if the ones above were False
            show_expenses(expenses) #runs the show function
        elif choice == "Delete an expense": #Option 3
            delete_expense(expenses) #runs the delete function
        elif choice == "Undo last": #Option 4
            undo_last(expenses, undo_stack) #runs the undo function
        elif choice == "Search expenses": #Option 5
            search_expenses(expenses) #runs the search function
        elif choice == "Check overspending": #Option 6
            check_overspending(expenses) #runs the overspending check
        elif choice == "Savings progress": #Option 7
            savings_progress(expenses, settings) #runs the savings function
        elif choice == "Change budget and goal": #Option 8
            change_settings(settings) #runs the settings function
        else: #The only option left is Quit
            print("Bye!") #Goodbye message
            running = False #Makes the while loop stop, so the program ends
        save_expenses(expenses) #Saves the expenses after EVERY option, so nothing is lost if the program closes suddenly
        save_settings(settings) #Saves the settings too


main() 
