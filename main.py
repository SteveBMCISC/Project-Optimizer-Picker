from bakery import assert_equal
from drafter import *
from drafter import Content
from dataclasses import dataclass

set_website_title("Project Optimizer")
set_site_information(
    author="Steve Baltazar-Mendez",
    description="Put projects in, constraints, desires, and rate them in order to come out with the best one",
    sources="AI Conversation CISC-106 - Steve BM.pdf",
    planning=["Project-Optimizer Brainstorm.docx", "Project-Optimizer Design.docx"],
    links=["https://drive.google.com/file/d/1Ri0wL1esSdOMELb7tIEyM9B16pxzSHGx/view?usp=sharing"]
)
hide_debug_information()

# =========================================
# DATACLASSES
# =========================================

@dataclass
class Project:
    """
    The dataclass that holds all of the aspects to Project
    
    name (str): Name of the project or idea
    score (int): The score to determine whether or not it is the maximum or best project"
    best (bool): Whether or not it is the current maximum
    description (str): A small description on the project to remember what it is about
    eligible (bool): Whether or not an instant of project fails a constraint will change this to False
    met_desires (list[str]): A list of strings that contains the desires the project met
    failed_constraints (list[str]): A list of strings that contains the constraints the project failed
    """
    name: str
    score: int
    best: bool
    description: str
    eligible: bool
    met_desires: list[str]
    failed_constraints: list[str]


@dataclass
class State:
    """
    The state dataclass that saves the data of all the user inputs
    
    projects (list[Project): Holds all the projects the user inputs into the organizer
    compared_project (str): Holds the name of the project the rest are being compared to
    constraints (list[str]): A list of string that contains multiple constraints
    desires (list[str])?: A list of string that contains multiple desires for points for projects to earn
    best_project (str): Name of the best project that comes from projects after a max loop
    """
    projects: list[Project]
    compared_project: str
    constraints: list[str]
    desires: list[str]
    best_project: str


# ==========================================
# HELPER FUNCTION
# ==========================================

def update_best_project(state: State):
    """
    Helper Function:
    state (State): Modifies the state.best via whichever has the highest points
    """
    highest_score = -1
    state.best_project = ""

    for project in state.projects:
        project.best = False
        if project.eligible:
            if project.score > highest_score:
                highest_score = project.score
                state.best_project = project.name
    for project in state.projects:
        if project.name == state.best_project:
            project.best = True


# ==========================================
# MAIN PAGE
# ==========================================

@route
def index(state: State) -> Page:
    """
    The true index to display all aspects of the projects that the user inputs
    
    Div(): Special calling that I saw on drafter and on the to-do list project example
           Gives a table appearance to the information displayed on the website
           Offers special margins and borders via pixel measurements
           
    Buttons/Route Functions:
    add_project: To the Add project page to all user inputs for new ideas
    compared_to: To the comparison page to pick a project to base and review others off of
    constraints: To the constraints page to add what parts are necessary for the project
    desires: To the desires page to add criteria that will give the project a higher score
    project_rater: The page to give points to projects and determines which is the best
    best_project: The page to officially display the best project
    
    returns:
    Page (Page): A new website page with all the buttons present for a selection for the user to use
    """
    project_content = []
    constraint_content = []
    desire_content = []
    for project in state.projects:
        project_content.append(
            Div(
                Header(project.name, 3),
                "Description: " + project.description,
                "Score: " + str(project.score),
                "Status: " + (
                    "Eligible" if project.eligible
                    else "Disqualified"
                ),
                style_border="1px solid gray",
                style_padding="10px",
                style_margin="5px"
            )
        )
    for constraint in state.constraints:
        constraint_content.append(
            Div(constraint)
        )
    for desire in state.desires:
        desire_content.append(
            Div(desire)
        )
    if not project_content:
        project_content.append(Div("No projects added yet."))
    if not constraint_content:
        constraint_content.append(Div("No constraints added yet."))
    if not desire_content:
        desire_content.append(Div("No desires added yet."))
    best = state.best_project
    if not best:
        best = "No eligible project yet."
    return Page(state, [
        Header("Project Optimizer"),
        Div(
            Header("All Projects", 2),
            *project_content
        ),
        Div(
            Header("Constraints", 2),
            *constraint_content
        ),
        Div(
            Header("Desires", 2),
            *desire_content
        ),
        Div(
            Header("Best Project", 2),
            best
        ),
        Button("Add Project", "add_project"),
        Button("Compare Projects", "compared_to"),
        Button("Manage Constraints", "constraints"),
        Button("Manage Desires", "desires"),
        Button("Rate Projects", "project_rater"),
        Button("View Results", "best_project")
    ])


# ==========================================
# ADD PROJECT
# ==========================================

@route
def add_project(state: State) -> Page:
    """
    Route function that adds projects to the state so the index can then display them
    
    state (State): Changes the state to move to a new page with new infomation allowing 3 different input types
    """
    return Page(state, [
        Header("Add a Project"),
        "Project Name:",
        TextBox("name"),
        "Project Description:",
        TextArea("description"),
        Button("Submit Project", "save_project"),
        Button("Home", "index")
    ])


@route
def save_project(state: State,
                 name: str,
                 description: str) -> Page:
    """
    Saves a project and moves it to the state dataclass in State.projects
    
    args:
    state (State): Saves info to the state dataclass
    name (str): Takes in a string to name an instance of project
    description (str): Takes in a string to give a description to an instance of a project
    
    returns:
    index(state): Accepts the information if not a duplicate or empty into the state
    """
    name = name.strip()
    if not name:
        return Page(state, [
            Header("Add a Project"),
            "Error: A project must have a name.",
            Button("Try Again", "add_project")
        ])
    duplicate = False
    for project in state.projects:
        if project.name.lower() == name.lower():
            duplicate = True
    if duplicate:
        return Page(state, [
            Header("Add a Project"),
            "Error: This project already exists.",
            Button("Try Again", "add_project")
        ])

    new_project = Project(
        name,
        0,
        False,
        description,
        True,
        [],
        []
    )
    state.projects.append(new_project)
    return index(state)


# ==========================================
# COMPARE PROJECTS
# ==========================================

@route
def compared_to(state: State) -> Page:
    """
    Opens a page to select one project to compare to however many others
    
    args:
    state (State): Utilizes the state to select one of the user's projects to use to compare others to 
    """
    project_names = []
    project_content = []
    for project in state.projects:
        project_names.append(project.name)
        project_content.append(
            Div(
                Header(project.name, 3),
                project.description,
                "Score: " + str(project.score),
                style_border="1px solid gray",
                style_padding="10px",
                style_margin="5px"
            )
        )
    if not project_content:
        return Page(state, [
            Header("Compare Projects"),
            "You must add a project first.",
            Button("Add Project", "add_project"),
            Button("Home", "index")
        ])
    return Page(state, [
        Header("Compare Projects"),
        Div(
            Header("Available Projects", 2),
            *project_content
        ),
        Div(
            Header("Current Baseline", 2),
            state.compared_project
        ),

        Div(
            Header("Choose a Baseline", 2),
            SelectBox("selected_project", project_names),
            Button("Save Comparison", "save_comparison")
        ),
        Button("Home", "index")
    ])

@route
def save_comparison(state: State,
                    selected_project: str) -> Page:
    """
    Saves the selected project to the state
    
    arg:
    state (State): The dataclass to extract the information from and return it
    selected_project (str): The name of the project chosen from user input
    
    returns:
    compared_to (state): Calls the compared_to page to accept the user_input as the comparison
    """
    valid_project = False
    for project in state.projects:
        if project.name == selected_project:
            valid_project = True
    if valid_project:
        state.compared_project = selected_project
    return compared_to(state)


# ==========================================
# CONSTRAINTS
# ==========================================

@route
def constraints(state: State) -> Page:
    """
    Takes in user inputs of constraint to be a guide to determine whether or not a project fills the goal of an assignment
    
    args:
    state (State): The state is taken in to open a new page and recieve user input
    
    returns:
    Page: The function will be called to be saved into the state
    """
    constraint_content = []
    for constraint in state.constraints:
        constraint_content.append(
            Div(
                constraint,
                style_border="1px solid gray",
                style_padding="8px",
                style_margin="5px"
            )
        )
    if not constraint_content:
        constraint_content.append(
            Div("No constraints added yet.")
        )
    return Page(state, [
        Header("Project Constraints"),
        Div(
            Header("Current Constraints", 2),
            *constraint_content
        ),
        Div(
            Header("Add a Constraint", 2),
            TextBox("new_constraint"),
            Button("Submit", "save_constraint")
        ),
        Button("Home", "index")
    ])


@route
def save_constraint(state: State,
                    new_constraint: str) -> Page:
    """
    The function that allows the state to be saved to the state
    
    arg:
    state (State): The argument that will receive the information through state.constraints
    new_constraint (str): A new constraint that will be compared to an old one to verify that it is new
    
    returns
    Page: Calls constraints on the state to return the information to the state
    """
    new_constraint_list = new_constraint.strip()
    if new_constraint_list and new_constraint not in state.constraints:
        state.constraints.append(new_constraint)
    return constraints(state)


# ==========================================
# DESIRES
# ==========================================

@route
def desires(state: State) -> Page:
    """
    Opens the page for the state to be called and recieve a user inputed desire
    
    args:
    state (State): The state awaits a user input to recieve inside the state.desires
    
    returns:
    Page: A website page to recieve the information
    """
    desire_content = []
    for desire in state.desires:
        desire_content.append(
            Div(
                desire,
                style_border="1px solid gray",
                style_padding="8px",
                style_margin="5px"
            )
        )
    if not desire_content:
        desire_content.append(
            Div("No desires added yet.")
        )
    return Page(state, [
        Header("Project Desires"),
        Div(
            Header("Current Desires", 2),
            *desire_content
        ),
        Div(
            Header("Add a Desire", 2),
            TextBox("new_desire"),
            Button("Submit", "save_desire")
        ),
        Button("Home", "index")
    ])

@route
def save_desire(state: State,
                new_desire: str) -> Page:
    """
    Takes in the user input as a new list to verify whether or not it is a repeat
    
    args:
    state (State): Takes the data from the state and confirms whether or not it is in the state
    new_desire: The possible new desire to add to the state
    
    returns:
    Page: Updates the page and the state to recieve the new info via calling desires
    """
    new_desire_list = new_desire.strip()
    if new_desire_list and new_desire not in state.desires:
        state.desires.append(new_desire)
    return desires(state)


# ==========================================
# PROJECT RATER
# ==========================================

@route
def project_rater(state: State) -> Page:
    """
    Makes a page to start the rating process, will not appear if desires and constraints are filled out
    
    args:
    state (State): Takes in the info from State to determine whether or not to allow the ratings to start
    
    returns:
    Page: Determines whther or not to continue with the rating process
    """
    if not state.projects:
        return Page(state, [
            Header("Project Rater"),
            "Add projects before rating them.",
            Button("Add Project", "add_project")
        ])

    if not state.constraints or not state.desires:
        return Page(state, [
            Header("Project Rater"),
            "Add at least one constraint and one desire first.",
            Button("Constraints", "constraints"),
            Button("Desires", "desires")
        ])
    project_names = []
    for project in state.projects:
        project_names.append(project.name)
        
    return Page(state, [
        Header("Project Rater"),
        "Choose a project:",
        SelectBox("project_name", project_names),
        "Choose a constraint:",
        SelectBox("selected_constraint", state.constraints),
        "Does the project satisfy the constraint?",
        SelectBox("constraint_result", ["Yes", "No"]),
        "Choose a desire:",
        SelectBox("selected_desire", state.desires),
        "Does the project satisfy the desire?",
        SelectBox("desire_result", ["Yes", "No"]),
        Button("Submit Rating", "save_rating"),
        Button("Home", "index")
    ])


@route
def save_rating(state: State,
                project_name: str,
                selected_constraint: str,
                constraint_result: str,
                selected_desire: str,
                desire_result: str) -> Page:
    """
    Saves the ratings of every project while the user compares it to another
    
    args:
    state (State): Takes in the list of projects from the state to iterate over the non compared
    project_name (str): The project iterated name
    selected_constraint (str): The iterated constraint that has been chosen, fails a project if one is not met
    selected_desire (str): The iterated desire that has been chosen, rewards points for best_project
    desire_result (str): Checks if selected "Yes" or "No" to give points to benefit the selected project
    
    returns:
    Page: A page to input/select all the buttons to rate the user's projects themselves
    """
    for project in state.projects:
        if project.name == project_name:
            if selected_constraint not in state.constraints:
                return Page(state, [
                    "Invalid constraint selection.",
                    Button("Try Again", "project_rater")
                ])
            if selected_desire not in state.desires:
                return Page(state, [
                    "Invalid desire selection.",
                    Button("Try Again", "project_rater")
                ])
            if constraint_result == "No":
                if selected_constraint not in project.failed_constraints:
                    project.failed_constraints.append(
                        selected_constraint
                    )
                project.eligible = False
            if desire_result == "Yes":
                if selected_desire not in project.met_desires:
                    project.met_desires.append(
                        selected_desire
                    )
            project.score = len(project.met_desires)
            update_best_project(state)
            return Page(state, [
                Header("Rating Submitted"),
                "Project: " + project.name,
                "Score: " + str(project.score),
                "Eligible: " + str(project.eligible),
                Button("Rate Another", "project_rater"),
                Button("View Results", "best_project")
            ])
    return Page(state, [
        "Project not found.",
        Button("Try Again", "project_rater")
    ])


# ==========================================
# BEST PROJECT
# ==========================================

@route
def best_project(state: State) -> Page:
    """
    Uses a loop to check each project in the state for the best project
    
    args:
    state (State): Takes in the state to check for the best project
    
    returns:
    Page(state, content): The page is updated with the best project and populated with Div()
    """
    update_best_project(state)
    if not state.best_project:
        return Page(state, [
            Header("Best Project"),
            "There are currently no eligible projects.",
            Button("Rate Projects", "project_rater"),
            Button("Home", "index")
        ])
    content: list[Content] = [
        Header("Most Optimal Project")
    ]
    for project in state.projects:
        if project.best:
            content.append(
                Div(
                    Header(project.name, 2),
                    project.description,
                    "Score: " + str(project.score),
                    "Met desires: " + str(project.met_desires),
                    style_border="1px solid gray",
                    style_padding="12px"
                )
            )
    content.extend([
        Button("View All Projects", "most_optimal"),
        Button("Home", "index")
    ])
    return Page(state, content)


# ==========================================
# ALL PROJECT RESULTS
# ==========================================

@route
def most_optimal(state: State) -> Page:
    """
    After all the program is ran fully, the most optimal project is chosen
    
    args:
    state (State): Populates the page with state info after rewarding or failing projects
    
    returns
    Page: A page with organized info via div() with the best project
    """
    project_content = []
    for project in state.projects:
        status = "Eligible"
        if not project.eligible:
            status = "Disqualified"
        project_content.append(
            Div(
                Header(project.name, 3),
                project.description,
                "Score: " + str(project.score),
                "Status: " + status,
                "Best Project: " + str(project.best),
                style_border="1px solid gray",
                style_padding="10px",
                style_margin="5px"
            )
        )
    if not project_content:
        project_content.append(
            Div("No projects have been added yet.")
        )
    return Page(state, [
        Header("All Project Results"),
        Div(
            Header("Baseline Project", 2),
            state.compared_project
        ),
        Div(
            Header("Project Rankings", 2),
            *project_content
        ),
        Button("View Best Project", "best_project"),
        Button("Home", "index")
    ])

# ==========================================
# BAKERY UNIT TESTS
# ==========================================
def sample_state():
    return State(
        projects=[
            Project(
                "Planner",
                0,
                False,
                "A simple planning application.",
                True,
                [],
                []
            )
        ],
        compared_project="None selected",
        constraints=["Must work offline"],
        desires=["Export PDF"],
        best_project=""
    )
# ------------------------------------------
# 1. INDEX
# ------------------------------------------

empty = State([], "None selected", [], [], "")

assert_equal(
    index(empty).content[0],
    Header("Project Optimizer")
)


# ------------------------------------------
# 2. ADD PROJECT
# ------------------------------------------

assert_equal(
    add_project(empty).content[0],
    Header("Add a Project")
)


# ------------------------------------------
# 3. SAVE PROJECT
# ------------------------------------------

# Empty name should not add a project

test = State([], "None selected", [], [], "")

save_project(test, "", "A description")

assert_equal(len(test.projects), 0)


# Valid project should be added

test = State([], "None selected", [], [], "")

save_project(test, "Planner", "Planning application")

assert_equal(
    test.projects,
    [
        Project(
            "Planner", 0, False,
            "Planning application",
            True, [], []
        )
    ]
)


# Duplicate project should not be added

save_project(test, "planner", "Another description")

assert_equal(len(test.projects), 1)


# ------------------------------------------
# 4. COMPARED TO
# ------------------------------------------

# Empty project list

test = State([], "None selected", [], [], "")

assert_equal(
    compared_to(test).content[0],
    Header("Compare Projects")
)


# Projects available

test = sample_state()

assert_equal(
    compared_to(test).content[0],
    Header("Compare Projects")
)


# ------------------------------------------
# 5. SAVE COMPARISON
# ------------------------------------------

test = sample_state()

save_comparison(test, "Planner")

assert_equal(test.compared_project, "Planner")


# Invalid selection should not replace baseline

save_comparison(test, "Invalid Project")

assert_equal(test.compared_project, "Planner")


# ------------------------------------------
# 6. CONSTRAINTS
# ------------------------------------------

test = State([], "None selected", [], [], "")

assert_equal(
    constraints(test).content[0],
    Header("Project Constraints")
)


# ------------------------------------------
# 7. SAVE CONSTRAINT
# ------------------------------------------

test = State([], "None selected", [], [], "")

# Empty input

save_constraint(test, "")

assert_equal(test.constraints, [])


# Valid input

save_constraint(test, "Must be free")

assert_equal(test.constraints, ["Must be free"])


# Duplicate input

save_constraint(test, "Must be free")

assert_equal(len(test.constraints), 1)


# ------------------------------------------
# 8. DESIRES
# ------------------------------------------

test = State([], "None selected", [], [], "")

assert_equal(
    desires(test).content[0],
    Header("Project Desires")
)


# ------------------------------------------
# 9. SAVE DESIRE
# ------------------------------------------

# Empty input

save_desire(test, "")

assert_equal(test.desires, [])


# Valid input

save_desire(test, "Easy to use")

assert_equal(test.desires, ["Easy to use"])


# Duplicate input

save_desire(test, "Easy to use")

assert_equal(len(test.desires), 1)


# ------------------------------------------
# 10. PROJECT RATER
# ------------------------------------------

# No projects

test = State([], "None selected", [], [], "")

assert_equal(
    project_rater(test).content[0],
    Header("Project Rater")
)


# Projects but no criteria

test = State(
    [Project("Planner", 0, False, "", True, [], [])],
    "None selected",
    [],
    [],
    ""
)

assert_equal(
    project_rater(test).content[0],
    Header("Project Rater")
)


# Projects and criteria available

test = sample_state()

assert_equal(
    project_rater(test).content[0],
    Header("Project Rater")
)


# ------------------------------------------
# 11. SAVE RATING
# ------------------------------------------

# Project does not exist

test = sample_state()

save_rating(
    test,
    "Invalid Project",
    "Must work offline",
    "Yes",
    "Export PDF",
    "Yes"
)

assert_equal(test.projects[0].score, 0)


# Project meets a desire

test = sample_state()

save_rating(
    test,
    "Planner",
    "Must work offline",
    "Yes",
    "Export PDF",
    "Yes"
)

assert_equal(test.projects[0].score, 1)


# Repeating the same desire does not add another point

save_rating(
    test,
    "Planner",
    "Must work offline",
    "Yes",
    "Export PDF",
    "Yes"
)

assert_equal(test.projects[0].score, 1)


# Failing a constraint disqualifies the project

save_rating(
    test,
    "Planner",
    "Must work offline",
    "No",
    "Export PDF",
    "Yes"
)

assert_equal(test.projects[0].eligible, False)
assert_equal(test.best_project, "")


# Invalid constraint selection

test = sample_state()

save_rating(
    test,
    "Planner",
    "Invalid Constraint",
    "Yes",
    "Export PDF",
    "Yes"
)

assert_equal(test.projects[0].score, 0)


# ------------------------------------------
# 12. BEST PROJECT
# ------------------------------------------

# No eligible projects

test = State([], "None selected", [], [], "")

assert_equal(
    best_project(test).content[0],
    Header("Best Project")
)


# Find the highest-scoring eligible project

test = State(
    [
        Project("Planner", 2, False, "Planning", True, [], []),
        Project("Organizer", 5, False, "Organizing", True, [], [])
    ],
    "None selected",
    [],
    [],
    ""
)

best_project(test)

assert_equal(test.best_project, "Organizer")
assert_equal(test.projects[1].best, True)
assert_equal(test.projects[0].best, False)


# ------------------------------------------
# 13. MOST OPTIMAL
# ------------------------------------------

# Empty project list

test = State([], "None selected", [], [], "")

assert_equal(
    most_optimal(test).content[0],
    Header("All Project Results")
)


# Populated project list

test = sample_state()

assert_equal(
    most_optimal(test).content[0],
    Header("All Project Results")
)

start_server(
    State(
        projects=[],
        compared_project="None selected",
        constraints=[],
        desires=[],
        best_project=""
    )
)
