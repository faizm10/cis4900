"""
Seed script: inserts 7 intro CS KCs, 7 prereq edges, and 28+ quiz items.
Idempotent — safe to run multiple times (skips existing records by name).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database import SessionLocal
from app.models.kc import KC
from app.models.prereq_edge import PrereqEdge
from app.models.item import Item


KCS = [
    {"name": "Variables", "description": "Variable assignment, data types, and value binding in Python.", "p_l0": 0.1, "p_t": 0.15, "p_g": 0.25, "p_s": 0.10},
    {"name": "Boolean Expressions", "description": "Boolean values, comparison operators, and logical operators.", "p_l0": 0.1, "p_t": 0.12, "p_g": 0.25, "p_s": 0.10},
    {"name": "Conditionals", "description": "if/elif/else branching logic and control flow.", "p_l0": 0.1, "p_t": 0.10, "p_g": 0.20, "p_s": 0.10},
    {"name": "Loops", "description": "for and while loops, iteration, break and continue.", "p_l0": 0.1, "p_t": 0.10, "p_g": 0.20, "p_s": 0.12},
    {"name": "Functions", "description": "Defining functions, parameters, return values, and scope.", "p_l0": 0.1, "p_t": 0.08, "p_g": 0.15, "p_s": 0.12},
    {"name": "Arrays / Lists", "description": "Python lists: indexing, slicing, mutation, and built-in methods.", "p_l0": 0.1, "p_t": 0.10, "p_g": 0.20, "p_s": 0.10},
    {"name": "Recursion", "description": "Recursive functions, base cases, and the call stack.", "p_l0": 0.1, "p_t": 0.07, "p_g": 0.15, "p_s": 0.15},
]

# (from_name, to_name) — from must be mastered before to
EDGES = [
    ("Variables", "Boolean Expressions"),
    ("Boolean Expressions", "Conditionals"),
    ("Conditionals", "Loops"),
    ("Loops", "Functions"),
    ("Loops", "Arrays / Lists"),
    ("Functions", "Recursion"),
    ("Arrays / Lists", "Recursion"),
]

ITEMS = [
    # --- Variables ---
    {
        "kc": "Variables",
        "prompt": "What is the value of x after the following code?\n\nx = 5\nx = x + 3",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "5"}, {"label": "B", "text": "8"}, {"label": "C", "text": "3"}, {"label": "D", "text": "Error"}],
        "answer": "B",
        "difficulty": 0.2,
    },
    {
        "kc": "Variables",
        "prompt": "Which statement correctly assigns the string 'hello' to a variable named name?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "name = 'hello'"}, {"label": "B", "text": "name == 'hello'"}, {"label": "C", "text": "'hello' = name"}, {"label": "D", "text": "var name = 'hello'"}],
        "answer": "A",
        "difficulty": 0.1,
    },
    {
        "kc": "Variables",
        "prompt": "What type is the value 3.14 in Python?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "int"}, {"label": "B", "text": "str"}, {"label": "C", "text": "float"}, {"label": "D", "text": "double"}],
        "answer": "C",
        "difficulty": 0.2,
    },
    {
        "kc": "Variables",
        "prompt": "After the following code, what is the value of b?\n\na = 10\nb = a\na = 20",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "10"}, {"label": "B", "text": "20"}, {"label": "C", "text": "0"}, {"label": "D", "text": "Error"}],
        "answer": "A",
        "difficulty": 0.4,
    },
    {
        "kc": "Variables",
        "prompt": "Which of the following is a valid Python variable name?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "2fast"}, {"label": "B", "text": "my_var"}, {"label": "C", "text": "my-var"}, {"label": "D", "text": "class"}],
        "answer": "B",
        "difficulty": 0.3,
    },
    # --- Boolean Expressions ---
    {
        "kc": "Boolean Expressions",
        "prompt": "Which expression evaluates to True?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "5 > 3"}, {"label": "B", "text": "5 < 3"}, {"label": "C", "text": "5 == 3"}, {"label": "D", "text": "5 != 5"}],
        "answer": "A",
        "difficulty": 0.1,
    },
    {
        "kc": "Boolean Expressions",
        "prompt": "What does `not True` evaluate to?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "True"}, {"label": "B", "text": "False"}, {"label": "C", "text": "None"}, {"label": "D", "text": "Error"}],
        "answer": "B",
        "difficulty": 0.2,
    },
    {
        "kc": "Boolean Expressions",
        "prompt": "What is the result of `True and False`?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "True"}, {"label": "B", "text": "False"}, {"label": "C", "text": "None"}, {"label": "D", "text": "1"}],
        "answer": "B",
        "difficulty": 0.2,
    },
    {
        "kc": "Boolean Expressions",
        "prompt": "What is the result of `True or False`?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "True"}, {"label": "B", "text": "False"}, {"label": "C", "text": "None"}, {"label": "D", "text": "0"}],
        "answer": "A",
        "difficulty": 0.2,
    },
    {
        "kc": "Boolean Expressions",
        "prompt": "Which operator checks if two values are NOT equal in Python?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "!="}, {"label": "B", "text": "<>"}, {"label": "C", "text": "=/="}, {"label": "D", "text": "not =="}],
        "answer": "A",
        "difficulty": 0.2,
    },
    # --- Conditionals ---
    {
        "kc": "Conditionals",
        "prompt": "What is printed?\n\nif 5 > 3:\n    print('yes')\nelse:\n    print('no')",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "yes"}, {"label": "B", "text": "no"}, {"label": "C", "text": "both"}, {"label": "D", "text": "nothing"}],
        "answer": "A",
        "difficulty": 0.1,
    },
    {
        "kc": "Conditionals",
        "prompt": "Which keyword starts a secondary condition check in Python?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "else if"}, {"label": "B", "text": "elif"}, {"label": "C", "text": "elseif"}, {"label": "D", "text": "otherwise"}],
        "answer": "B",
        "difficulty": 0.2,
    },
    {
        "kc": "Conditionals",
        "prompt": "When does an `else` block execute?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "Always"}, {"label": "B", "text": "When the if condition is True"}, {"label": "C", "text": "When the if condition is False"}, {"label": "D", "text": "Never"}],
        "answer": "C",
        "difficulty": 0.2,
    },
    {
        "kc": "Conditionals",
        "prompt": "How many times does the body of `if x > 0:` execute if x = -1?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "0 times"}, {"label": "B", "text": "1 time"}, {"label": "C", "text": "-1 times"}, {"label": "D", "text": "Error"}],
        "answer": "A",
        "difficulty": 0.2,
    },
    {
        "kc": "Conditionals",
        "prompt": "What is printed?\n\nx = 10\nif x > 5:\n    print('big')\nelif x > 2:\n    print('medium')\nelse:\n    print('small')",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "big"}, {"label": "B", "text": "medium"}, {"label": "C", "text": "small"}, {"label": "D", "text": "big medium"}],
        "answer": "A",
        "difficulty": 0.3,
    },
    # --- Loops ---
    {
        "kc": "Loops",
        "prompt": "How many times does the following code print?\n\nfor i in range(3):\n    print(i)",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "2"}, {"label": "B", "text": "4"}, {"label": "C", "text": "3"}, {"label": "D", "text": "1"}],
        "answer": "C",
        "difficulty": 0.2,
    },
    {
        "kc": "Loops",
        "prompt": "What does `while False:` do?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "Runs forever"}, {"label": "B", "text": "Never executes the body"}, {"label": "C", "text": "Runs once"}, {"label": "D", "text": "Error"}],
        "answer": "B",
        "difficulty": 0.3,
    },
    {
        "kc": "Loops",
        "prompt": "What is the last value printed by `for i in range(5): print(i)`?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "5"}, {"label": "B", "text": "1"}, {"label": "C", "text": "0"}, {"label": "D", "text": "4"}],
        "answer": "D",
        "difficulty": 0.3,
    },
    {
        "kc": "Loops",
        "prompt": "Which keyword exits a loop immediately?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "break"}, {"label": "B", "text": "continue"}, {"label": "C", "text": "stop"}, {"label": "D", "text": "exit"}],
        "answer": "A",
        "difficulty": 0.2,
    },
    {
        "kc": "Loops",
        "prompt": "Which keyword skips to the next iteration of a loop?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "break"}, {"label": "B", "text": "continue"}, {"label": "C", "text": "skip"}, {"label": "D", "text": "next"}],
        "answer": "B",
        "difficulty": 0.2,
    },
    # --- Functions ---
    {
        "kc": "Functions",
        "prompt": "What keyword defines a function in Python?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "def"}, {"label": "B", "text": "function"}, {"label": "C", "text": "func"}, {"label": "D", "text": "define"}],
        "answer": "A",
        "difficulty": 0.1,
    },
    {
        "kc": "Functions",
        "prompt": "What does a function without a `return` statement implicitly return?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "0"}, {"label": "B", "text": "False"}, {"label": "C", "text": "None"}, {"label": "D", "text": "Error"}],
        "answer": "C",
        "difficulty": 0.3,
    },
    {
        "kc": "Functions",
        "prompt": "How do you call a function named `greet` with the argument 'Alice'?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "greet 'Alice'"}, {"label": "B", "text": "greet('Alice')"}, {"label": "C", "text": "call greet('Alice')"}, {"label": "D", "text": "greet.call('Alice')"}],
        "answer": "B",
        "difficulty": 0.1,
    },
    {
        "kc": "Functions",
        "prompt": "What is the scope of a variable defined inside a function?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "Local (only inside the function)"}, {"label": "B", "text": "Global (everywhere in the program)"}, {"label": "C", "text": "Module level"}, {"label": "D", "text": "Depends on the type"}],
        "answer": "A",
        "difficulty": 0.4,
    },
    # --- Arrays / Lists ---
    {
        "kc": "Arrays / Lists",
        "prompt": "What is the index of the first element in a Python list?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "0"}, {"label": "B", "text": "1"}, {"label": "C", "text": "-1"}, {"label": "D", "text": "Depends on the list"}],
        "answer": "A",
        "difficulty": 0.1,
    },
    {
        "kc": "Arrays / Lists",
        "prompt": "What does `len([1, 2, 3])` return?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "2"}, {"label": "B", "text": "3"}, {"label": "C", "text": "4"}, {"label": "D", "text": "1"}],
        "answer": "B",
        "difficulty": 0.1,
    },
    {
        "kc": "Arrays / Lists",
        "prompt": "How do you add an element to the end of a list named arr?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "arr.add(x)"}, {"label": "B", "text": "arr.insert(x)"}, {"label": "C", "text": "arr.append(x)"}, {"label": "D", "text": "arr.push(x)"}],
        "answer": "C",
        "difficulty": 0.2,
    },
    {
        "kc": "Arrays / Lists",
        "prompt": "What does `arr[-1]` access?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "The first element"}, {"label": "B", "text": "An error"}, {"label": "C", "text": "The second-to-last element"}, {"label": "D", "text": "The last element"}],
        "answer": "D",
        "difficulty": 0.3,
    },
    {
        "kc": "Arrays / Lists",
        "prompt": "What is the result of `[1, 2, 3, 4, 5][1:3]`?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "[1, 2]"}, {"label": "B", "text": "[2, 3]"}, {"label": "C", "text": "[2, 3, 4]"}, {"label": "D", "text": "[1, 2, 3]"}],
        "answer": "B",
        "difficulty": 0.4,
    },
    # --- Recursion ---
    {
        "kc": "Recursion",
        "prompt": "What is a base case in recursion?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "The condition that stops recursion"}, {"label": "B", "text": "The first call to the function"}, {"label": "C", "text": "The deepest recursive call"}, {"label": "D", "text": "The return value"}],
        "answer": "A",
        "difficulty": 0.3,
    },
    {
        "kc": "Recursion",
        "prompt": "What happens if a recursive function has no base case?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "It returns None"}, {"label": "B", "text": "It runs once"}, {"label": "C", "text": "Infinite recursion / stack overflow"}, {"label": "D", "text": "It raises a syntax error"}],
        "answer": "C",
        "difficulty": 0.3,
    },
    {
        "kc": "Recursion",
        "prompt": "How many times is f called in total?\n\ndef f(n):\n    if n == 0:\n        return 0\n    return f(n - 1)\n\nf(3)",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "3"}, {"label": "B", "text": "2"}, {"label": "C", "text": "1"}, {"label": "D", "text": "4"}],
        "answer": "D",
        "difficulty": 0.5,
    },
    {
        "kc": "Recursion",
        "prompt": "Which data structure does Python use internally to manage recursive calls?",
        "type": "multiple_choice",
        "choices": [{"label": "A", "text": "Queue"}, {"label": "B", "text": "Call stack"}, {"label": "C", "text": "Heap"}, {"label": "D", "text": "Dictionary"}],
        "answer": "B",
        "difficulty": 0.4,
    },
]


def seed():
    db = SessionLocal()
    try:
        # Insert KCs
        kc_map: dict[str, int] = {}
        for kc_data in KCS:
            existing = db.query(KC).filter(KC.name == kc_data["name"]).first()
            if existing:
                kc_map[existing.name] = existing.kc_id
                continue
            kc = KC(**kc_data)
            db.add(kc)
            db.flush()
            kc_map[kc.name] = kc.kc_id

        db.commit()

        # Re-query to get all IDs after commit
        all_kcs = db.query(KC).all()
        kc_map = {kc.name: kc.kc_id for kc in all_kcs}

        # Insert edges
        for from_name, to_name in EDGES:
            from_id = kc_map[from_name]
            to_id = kc_map[to_name]
            existing = db.query(PrereqEdge).filter(
                PrereqEdge.from_kc_id == from_id,
                PrereqEdge.to_kc_id == to_id,
            ).first()
            if not existing:
                db.add(PrereqEdge(from_kc_id=from_id, to_kc_id=to_id))

        db.commit()

        # Insert items
        for item_data in ITEMS:
            kc_name = item_data["kc"]
            kc_id = kc_map[kc_name]
            existing = db.query(Item).filter(
                Item.kc_id == kc_id,
                Item.prompt == item_data["prompt"],
            ).first()
            if not existing:
                db.add(Item(
                    kc_id=kc_id,
                    prompt=item_data["prompt"],
                    type=item_data["type"],
                    choices=item_data.get("choices"),
                    answer=item_data["answer"],
                    difficulty=item_data["difficulty"],
                ))

        db.commit()
        print(f"Seeded {len(KCS)} KCs, {len(EDGES)} edges, {len(ITEMS)} items.")

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
