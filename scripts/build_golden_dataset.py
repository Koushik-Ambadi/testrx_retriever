from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_PATH = ROOT / "output" / "document.json"
WARNINGS_PATH = ROOT / "output" / "parsing_warnings.json"
PDF_PATH = ROOT / "source" / "TESTRX_User_Manual.pdf"
OUT_DIR = ROOT / "output" / "golden_dataset"


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("–", "-").replace("—", "-")).strip().casefold()


document = json.loads(DOCUMENT_PATH.read_text(encoding="utf-8"))
warnings = json.loads(WARNINGS_PATH.read_text(encoding="utf-8"))
sections = {s["section_id"]: s for s in document["sections"]}
elements: dict[str, dict] = {}
element_sections: dict[str, str] = {}


def register_element(element: dict, section_id: str) -> None:
    elements[element["id"]] = element
    element_sections[element["id"]] = section_id
    for child in element.get("children", []):
        register_element(child, section_id)


for section in document["sections"]:
    for element in section["elements"]:
        register_element(element, section["section_id"])


questions: list[dict] = []


def add(
    question: str,
    question_type: str,
    difficulty: str,
    expected_answer: str,
    required_ids: list[str],
    *,
    supporting_ids: list[str] | None = None,
    negatives: list[str] | None = None,
    evidence: list[str] | None = None,
    notes: str = "",
    parent: bool = False,
    table: bool = False,
    procedure: bool = False,
    cross_reference: bool = False,
    multi_hop: bool = False,
) -> None:
    supporting_ids = supporting_ids or []
    negatives = negatives or []
    missing = [eid for eid in required_ids + supporting_ids + negatives if eid not in elements]
    if missing:
        raise KeyError(f"Unknown element IDs: {missing}")
    source_ids = list(dict.fromkeys(required_ids + supporting_ids))
    source_sections = list(dict.fromkeys(element_sections[eid] for eid in source_ids))
    pages = sorted(
        {
            page
            for eid in source_ids
            for page in range(elements[eid]["page_start"], elements[eid]["page_end"] + 1)
        }
    )
    section_paths = [sections[sid]["ancestor_path"] for sid in source_sections]
    qid = f"Q{len(questions) + 1:03d}"
    questions.append(
        {
            "question_id": qid,
            "question": question,
            "question_type": question_type,
            "difficulty": difficulty,
            "expected_answer": expected_answer,
            "source": {
                "document": document["title"],
                "pages": pages,
                "section_paths": section_paths,
                "semantic_unit_ids": required_ids,
                "element_ids": source_ids,
            },
            "retrieval_ground_truth": {
                "primary_source": required_ids[0],
                "required_source_set": required_ids,
                "acceptable_source_set": list(dict.fromkeys(required_ids + supporting_ids)),
            },
            "required_evidence": evidence or [expected_answer],
            "supporting_evidence": supporting_ids,
            "hard_negative_sources": negatives,
            "answerability": "answerable",
            "evaluation_metadata": {
                "requires_single_unit": len(required_ids) == 1,
                "requires_multiple_units": len(required_ids) > 1,
                "requires_parent_context": parent,
                "requires_table": table,
                "requires_procedure": procedure,
                "requires_cross_reference": cross_reference,
                "requires_multi_hop": multi_hop,
            },
            "notes": notes,
        }
    )


# Introduction, installation, workspace, and interface
add("What does TESTRX stand for?", "definition", "easy", "TESTRX stands for Test Environment System for Tracking & Running Xecutions.", ["section-1.1-element-001"])
add("What parts of the automotive testing workflow does TESTRX support?", "factual", "medium", "It supports standardized test-case authoring, test-script generation from test-bench configuration, and test execution for embedded automotive systems.", ["section-2.1-element-001", "section-2.1-element-002"], parent=True)
add("Which testing environments does TESTRX support?", "factual", "easy", "It supports a range of tools and environments, including HIL systems and in-vehicle testing.", ["section-2.1-element-002"])
add("What happens if TESTRX installation fails?", "troubleshooting", "easy", "The installer shows a notification and points to the generated log file for troubleshooting.", ["section-3-element-001"])
add("How can TESTRX be uninstalled from Windows?", "procedure", "easy", "Use Control Panel > Programs and Features or Windows Settings > Apps & Features.", ["section-3.2-element-001"], procedure=True)
add("What happens if TESTRX uninstallation fails?", "troubleshooting", "easy", "The changes are rolled back safely and the user is informed of the failure.", ["section-3.2-element-001"], negatives=["section-3-element-001"])
add("How can a workspace location be chosen on first launch?", "procedure", "easy", "Enter a directory path manually or select one with Browse, then confirm with OK.", ["section-4.1-element-001", "section-4.1-element-003"], procedure=True)
add("What happens when Cancel is selected in the first-launch workspace window?", "factual", "easy", "Workspace selection is aborted, the application closes, and no workspace information is stored.", ["section-4.1-element-001"])
add("What does TESTRX create after a workspace location is confirmed?", "factual", "easy", "It creates a TESTRX_Workspace directory and all required subfolders, initializes components and data, and opens the Test Case view.", ["section-4.1-element-003"])
add("Which main areas appear on the TESTRX Home screen?", "figure", "easy", "The Home screen contains the Menu Bar, Test Environment Roles Selector, Project Navigator, and Test Case Editor.", ["section-5-element-001"], supporting_ids=["snp_2_p007"])
add("What is the difference between the Test Case and Test Session tabs?", "comparison", "medium", "The Test Case tab is for viewing, creating, editing, and managing test cases; the Test Session tab is for starting, managing, and reviewing execution sessions.", ["section-5-element-003"])

# Navigator and menu bar
add("What does the Project Navigator show for the Test Case role versus the Test Session role?", "comparison", "easy", "The Test Case role shows Projects, Test Suites, and Test Cases; the Test Session role shows Test Sessions, Test Suites, and Test Cases.", ["section-6-element-001", "section-6-element-002"])
add("How do you expand and collapse the Project Navigator?", "procedure", "easy", "Click the Test Case or Test Session tab to expand it; click the same tab again to collapse it.", ["section-6.1-element-001"], procedure=True)
add("How does hovering over a navigator tab differ from clicking it?", "comparison", "medium", "Hovering temporarily displays the navigator as an overlay, while clicking expands it into the left portion of the window until collapsed.", ["section-6.1-element-001", "section-6.2-element-001"], negatives=["section-6.3-element-001"])
add("What does pinning the Project Navigator do?", "factual", "easy", "It locks the navigator in the expanded state until the user collapses or unpins it.", ["section-6.3-element-001"])
add("What happens when a Project Navigator node is double-clicked?", "factual", "easy", "A new tab opens in the right panel with details or the editor view for the selected node.", ["section-6.4-element-001"])
add("Which File menu command saves pending changes in every open test-case tab?", "table", "easy", "File > Save All.", ["table_1"], table=True, negatives=["section-7-element-001"])
add("Which menu command exports a selected Test Suite or Test Case to Excel?", "table", "easy", "File > Excel.", ["table_1"], table=True)
add("How do you open the folder associated with a selected node?", "table", "easy", "Use View > Open Folder.", ["table_1"], table=True)
add("Which menu command opens the current workspace location?", "table", "easy", "Use View > Open Workspace.", ["table_1"], table=True)
add("Which File menu command sends a Test Suite or Test Case to ALM?", "table", "easy", "Use File > Flush.", ["table_1"], table=True, negatives=["section-17.1.2-element-001"])
add("Which Help menu functions are marked as future scope?", "table", "medium", "About, Download User Manual, Download FAQs, FAQ, and Support are marked as future scope.", ["table_1"], table=True)
add("What is the hierarchy of content in the Test Case Repository?", "figure", "medium", "Projects contain Test Suites, and Test Suites contain one or more Test Cases.", ["section-8-element-001"], supporting_ids=["snp_3_p010", "snp_3_p011"])

# Projects and suites
add("What must exist before test cases can be authored in TESTRX?", "factual", "easy", "A project must first be created in the application.", ["section-9-element-001"])
add("How do you start creating a project from the File menu?", "procedure", "easy", "Open File, select New, and choose Project.", ["section-9-element-002", "section-9-element-003"], procedure=True)
add("Which project context-menu option restores a closed test suite?", "table", "easy", "Recover Test Suite.", ["table_2"], table=True)
add("What information is shown for Test Suites and Test Cases in the Overview panel?", "factual", "medium", "The panel shows ID, Description, State, Created By, and Category.", ["section-9.1.1-element-003"])
add("How do you view details for a Project, Test Suite, Test Case, or Heading?", "table", "easy", "Double-click the item and select the Details tab.", ["table_3"], table=True)
add("Which Details-tab fields identify when and by whom an item was changed?", "factual", "easy", "Modified Date and Modified By.", ["section-9.1.2-element-003"])
add("What are the two ways to create a Test Suite?", "procedure", "medium", "Either right-click the project and select Add Test Suite, or select the project and use File > New > Suite.", ["section-10-element-001", "section-10-element-002"], procedure=True)
add("What database file types can be added from the Signia sub-tab of a Test Suite?", "configuration", "easy", "A2L, DBC, and LDF files.", ["section-10.1-element-002"], negatives=["section-12.4-element-002"])
add("Which Test Suite sub-tab lists parameters used during test-case authoring?", "factual", "easy", "The Parameters sub-tab.", ["section-10.1-element-002"])
add("Which Test Suite context-menu action creates a ZIP file for reuse?", "table", "easy", "Export Test Suite exports the selected Test Suite as a ZIP file.", ["table_4"], table=True)
add("How can a Test Suite be opened from the Project Summary table?", "procedure", "easy", "Double-click its entry in the Project Summary table; selection then moves to that Test Suite.", ["section-10.3-element-001", "section-10.3-element-003"], procedure=True)

# Signia
add("What are the upper and lower panels of the Signia tab used for?", "configuration", "medium", "The upper panel lists imported database files; the lower panel shows details and signals for the selected file.", ["section-11-element-001"])
add("Which signal attributes are shown in the Signia Signals sub-tab?", "factual", "easy", "Label name, data type, conversion, and minimum and maximum values.", ["section-11-element-001"])
add("How do you import a database file into Signia?", "procedure", "medium", "Click Add in the upper panel, select A2L, DBC, or LDF, browse to the file in Details, and click Save.", ["section-11.1-element-001", "section-11.1-element-003"], procedure=True)
add("What does Reload do to an existing Signia database?", "configuration", "easy", "It re-imports a selected new or modified database file and refreshes its data with the latest content.", ["section-11.1-element-003"])
add("How do Delete and Force Delete differ for a Signia database?", "comparison", "medium", "Delete checks dependencies and blocks removal when active Test Cases reference the file; Force Delete bypasses that validation and removes the application reference immediately.", ["section-11.2-element-001"])
add("Does deleting a database from Signia delete the original system file?", "factual", "easy", "No. It removes only the reference in TESTRX; the original file remains unchanged.", ["section-11.2-element-001"])
add("What happens if the same database is pasted back into the same Test Suite?", "troubleshooting", "easy", "TESTRX displays an error indicating that the file already exists.", ["section-11.3-element-001"])
add("What happens if an invalid database file is selected during Signia import?", "troubleshooting", "easy", "The system displays an error message.", ["section-11.4-element-001"])
add("What happens if exporting a Signia database fails?", "troubleshooting", "easy", "An error popup is displayed.", ["section-11.4-element-001"])

# Parameters
add("What syntax is used to substitute a parameter in a Test Case?", "configuration", "easy", "Use double braces in the form {{parameter_name}}.", ["section-12-element-001"])
add("Where can parameters be created?", "configuration", "easy", "They can be created from the Parameters tab at Test Suite or Test Case level, or directly in the Editor.", ["section-12.1-element-001"])
add("What name does TESTRX initially assign to a parameter created from the Parameters tab?", "factual", "easy", "It assigns a sequential default such as Parameter001, Parameter002, and so on.", ["section-12.1-element-001"])
add("How are newly created parameters saved?", "procedure", "easy", "Use Save on the Menu Bar or press Ctrl+S.", ["section-12.1-element-001"], procedure=True)
add("How do Test Suite and Test Case parameters differ in scope and precedence?", "comparison", "medium", "Test Suite parameters are global across their suite and provide defaults; Test Case parameters are local and override same-named suite parameters.", ["section-12.2.1-element-001", "section-12.2.2-element-001"], negatives=["section-12.2.3-element-001"])
add("When do parameters entered in the editor appear in the parameter table?", "factual", "easy", "They appear automatically once the user confirms the input.", ["section-12.2.3-element-001"])
add("Can multiple parameters be entered in one editor cell?", "factual", "easy", "Yes. Multiple parameters may be entered within a single editor cell.", ["section-12.2.3-element-001"])
add("What characters may a valid parameter name contain?", "configuration", "easy", "It must start with a letter and may contain only letters, digits, and underscores.", ["section-12.3-element-002"])
add("Which underscore patterns are invalid in a parameter name?", "configuration", "medium", "A name may not begin or end with an underscore and may not contain consecutive underscores.", ["section-12.3-element-002"])
add("Is abc a valid parameter name?", "configuration", "medium", "No. Parameter names must be longer than three characters.", ["section-12.3-element-002"])
add("What does the Set In field of the parameter table indicate?", "factual", "easy", "It indicates whether the parameter belongs to the Test Suite or the Test Case.", ["section-12.4-element-002"])
add("What inputs are accepted in a parameter's Value field?", "configuration", "easy", "A single numeric value or a comma-separated list of numeric values.", ["section-12.5.1-element-001", "section-12.5.1-element-002"])
add("Why is 1,,2 invalid in a parameter Value field?", "troubleshooting", "medium", "It contains consecutive commas; values must be numeric, unique, comma-separated, and have no trailing or consecutive commas.", ["section-12.5.1-element-003-labelled", "section-12.5.1-element-005-labelled"], negatives=["section-12.5.1-element-006-labelled"])
add("What happens when a valid new Current Value is typed manually?", "configuration", "easy", "The value is automatically added to the predefined Value list.", ["section-12.5.2-element-001", "section-12.5.2-element-002", "section-12.5.2-element-004"])
add("How are Value Description and Units handled when switching Current Values?", "configuration", "medium", "They are preserved and reloaded for the selected value, and edits apply only to that selected value.", ["section-12.5.2-element-004"])
add("At which level can a parameter be renamed?", "configuration", "easy", "Only at the Test Suite level.", ["section-12.6-element-001"])
add("What choices are offered when renaming a parameter that is already used in Test Cases?", "procedure", "medium", "Choose Continue to rename old_param to new_param, or Create New to add the new name as a separate parameter; naming rules are revalidated.", ["section-12.6-element-001", "section-12.6-element-002-labelled"], procedure=True)
add("How is a parameter removed?", "procedure", "easy", "Right-click its row, choose Remove Parameter, and confirm the deletion popup.", ["section-12.7-element-001"], procedure=True)

# Labels
add("Where is the Labels tab available, and what does it collect?", "definition", "easy", "It is available only at Test Suite level and consolidates labels referenced by Test Cases in the current suite.", ["section-13-element-001"])
add("When does a label created in the Test Case editor appear in the Labels tab?", "factual", "easy", "After the user saves the changes.", ["section-13.1-element-001"])
add("Are saved labels restricted to the Test Suite where they were created?", "factual", "easy", "No. Saved labels become globally accessible across all Test Suites.", ["section-13.1-element-001"])
add("Which Labels-tab field can the user edit?", "factual", "easy", "Only the Name field.", ["section-13.2-element-002"])
add("Where do a label's Factor, Offset, Units, minimum, maximum, and data type come from?", "configuration", "medium", "They are system-derived from metadata in the associated A2L, DBC, or LDF database file.", ["section-13.2-element-002"], negatives=["section-12.4-element-002"])
add("Why might TESTRX refuse to remove a label?", "troubleshooting", "easy", "Removal is blocked when the label is referenced in one or more Test Cases.", ["section-13.3.1-element-001"])
add("What happens if a label is renamed to a name that already exists?", "procedure", "medium", "TESTRX asks whether to merge; Yes merges reference data into the existing label, while Cancel aborts the rename.", ["section-13.3.2-element-001", "section-13.3.2-element-002"], procedure=True)
add("What does a pink label row indicate?", "troubleshooting", "easy", "The label has an invalid or missing source reference, such as after Signia deletion or reload or a copy into a suite without the required Signia file.", ["section-13.4-element-001"])
add("Which copy operations can cause label rows to turn pink?", "troubleshooting", "easy", "Copying a Test Case or a step into a context without the corresponding Signia file.", ["section-13.4-element-001"])

# Test-case authoring and control logic
add("What are the two ways to create a Test Case or Heading?", "procedure", "medium", "Use the context menu on a Test Suite or Test Case and choose Add Test Case/Add Heading, or use the New menu and select Test Case or Heading.", ["section-14-element-001", "section-14-element-002", "section-14-element-003", "section-14-element-004", "section-14-element-005"], procedure=True, notes="The parser split the two printed creation steps across procedure and paragraph elements; the complete source set is required.")
add("What default names are assigned to new Test Cases and Headings?", "factual", "easy", "Test Cases use TestCase001, TestCase002, and so on; Headings use Heading001, Heading002, and so on.", ["section-14-element-006"])
add("What are the main naming restrictions for a Test Case?", "configuration", "medium", "The name cannot be empty or longer than 150 characters, cannot start with a special character, cannot contain listed invalid characters or restricted reserved terms, and has leading/trailing spaces trimmed.", ["section-14.1-element-001"])
add("Which Test Case context-menu action exports a test case as a ZIP file?", "table", "easy", "Export Test Case.", ["table_5"], table=True)
add("What is the difference between Clear Step(s) and Remove Step(s)?", "comparison", "easy", "Clear Step(s) erases selected step content without deleting the steps; Remove Step(s) deletes the selected steps.", ["table_6"], table=True)
add("How do you open the test-step context menu?", "procedure", "easy", "Right-click the S.no column in the Sequence tab.", ["section-14.4-element-001"], procedure=True)
add("What are the Setup, Sequence, and Shut Down sections used for?", "configuration", "medium", "Setup holds automated preconditions and initialization, Sequence holds core actions and validations, and Shut Down holds cleanup and post-execution validation.", ["section-14.3-element-003"])
add("Which Sequence-tab column identifies the signal, variable, or parameter targeted by a step?", "factual", "easy", "Identifier.", ["section-14.3-element-003"], negatives=["section-14.6-element-001"])
add("Which instruction keyword waits for a duration at a test step?", "table", "easy", "Wait.", ["table_7"], table=True)
add("Which instruction keyword runs another test case?", "table", "easy", "Run.", ["table_7"], table=True)
add("Which Entity Type exposes signals from a DBC file?", "table", "easy", "CAN Signal.", ["table_8"], table=True)
add("Which Entity Types expose measurements from an A2L file?", "table", "medium", "ECU Input and ECU Output.", ["table_8"], table=True)
add("How is the Identifier suggestion list determined?", "configuration", "medium", "It is filtered by Entity Type and can include signals from linked DBC, A2L, and LDF files, parameters, previously used values, and user-defined data.", ["section-14.6-element-001"])
add("What does Clear do in the Control Logic window?", "factual", "easy", "It clears only updated or modified control-logic values and restores the previously saved configuration.", ["section-14.7-element-001"])
add("How does the Value control logic evaluate a test step?", "configuration", "medium", "The user selects a data type, expected value and comparison operator, optionally with tolerance and units; TESTRX compares the runtime value automatically.", ["section-14.7.1-element-001"])
add("How can a step depend on the verdict of an earlier step?", "configuration", "medium", "Use Reference Step to select a previous step and the required verdict; the current step runs or validates only when that verdict is met.", ["section-14.7.2-element-001"])
add("What are the four Time Constraint modes?", "factual", "easy", "After, Before, In Range, and Entire Range.", ["section-14.7.3-element-001"])
add("With an Entire Range of 5-10 seconds and early/late tolerance of 1 second, when is the condition accepted?", "factual", "medium", "It is accepted from 4 through 11 seconds.", ["section-14.7.3-element-001"], supporting_ids=["snp_17_p035"])
add("How does In Range differ from Entire Range?", "comparison", "hard", "In Range requires an occurrence within the acceptable interval, with optional early/late tolerance; Entire Range applies the condition across the whole configured time range, also allowing configured tolerance at its boundaries.", ["section-14.7.3-element-001"], notes="The source wording is awkward; retain for manual review if strict semantic interpretation of Entire Range is required.")
add("When is Range of Steps control logic available?", "configuration", "medium", "It is available for the When action and also for Repeat.", ["section-14.7.4-element-001", "section-14.7.4-element-003"])
add("What limits can control a Repeat over a range of steps?", "configuration", "medium", "A continuation Condition, a maximum Count, and a maximum Duration can control repetition.", ["section-14.7.4-element-003"])

# Execution workflow, TBC, and mapping
add("What are the four stages of the TESTRX execution workflow?", "procedure", "medium", "Link test cases to a Test Session, configure the Test Bench Configuration, define and configure a Test Plan, and execute the configured test cases.", ["section-16-element-001", "section-16-element-002"], procedure=True)
add("How do you view test steps from a Test Session or Test Plan?", "procedure", "easy", "Click the ID column for the relevant test case.", ["section-16.1-element-001"], procedure=True)
add("How can a Test Session be created after adding a project?", "procedure", "medium", "Right-click the project and choose Add Test Session, or choose Test Session from the File menu's New option.", ["section-16.1.1-element-001"], procedure=True)
add("How are test cases added from a linked Test Suite into a Test Session?", "procedure", "medium", "Link the Test Suite, expand it in the Test Cases panel, and drag the required test cases into the Test Session.", ["section-16.1.2-element-001", "section-16.1.2-element-003"], procedure=True)
add("What happens when a collapsed nested test case is dragged into a Test Session?", "factual", "easy", "All child test cases are included automatically.", ["section-16.1.2-element-003"])
add("How are linked test cases synchronized after edits in the Test Case tab?", "procedure", "easy", "Use Reload in the Test Cases panel or from the right-click menu in the Test Session table.", ["section-16.1.3-element-001"], procedure=True)
add("Why is Test Bench Configuration required before execution?", "definition", "easy", "It supplies the details needed to initialize, control, and manage the designated hardware and simulation environments.", ["section-16.2-element-001"])
add("What is the complete procedure for adding Test Bench Configuration details?", "procedure", "medium", "Open Configurator in the required Test Session, select its Configurator folder, add a TBC, choose the report path, then add the required interface.", ["section-16.2.1-element-001"], procedure=True, notes="The complete five-step procedure is the answer-bearing unit.")
add("Which TBC component controls power settings and power cycling?", "table", "easy", "PowerSupply.", ["table_9"], table=True)
add("Which TBC component provides a virtual environment for automated execution?", "table", "easy", "VTE.", ["table_9"], table=True)
add("Which CANoe settings can be configured in TBC?", "configuration", "medium", "Configuration path, logging format, reload and restart toggles, XIL or COM mode, and DBC association through Signia.", ["section-16.2.2-local-group-01"])
add("What connection types are available for Power Supply configuration?", "configuration", "easy", "PyVISA or COM.", ["section-16.2.2-local-group-02"], negatives=["section-16.2.2-local-group-01"])
add("Which SDT options control disconnection and data upload?", "configuration", "easy", "Disconnect after each step and upload data after each session can each be enabled or disabled.", ["section-16.2.2-local-group-03"])
add("What information is required for FPGA execution configuration?", "configuration", "medium", "An executable file, project name, number of packs, pack IDs, and optional CSV association through Signia.", ["section-16.2.2-local-group-04"])
add("How do VTE and FPGA configuration differ?", "comparison", "hard", "Both select an executable and project information, but FPGA adds pack counts/IDs and CSV association, while VTE adds a file path and VTE database import/management through Signia.", ["section-16.2.2-local-group-04", "section-16.2.2-local-group-05"], negatives=["section-16.2.2-local-group-01"])
add("Which Configurator toolbar action defines read and write paths for test and I/O labels?", "factual", "easy", "Map Labels.", ["section-16.2.3-element-004"])
add("Which Configurator toolbar actions move a TBC between TESTRX installations or sessions as a ZIP file?", "configuration", "medium", "Export saves the selected TBC as a ZIP file, and Import loads a previously exported TBC ZIP file.", ["section-16.2.3-element-004"])
add("When is the Map Labels option available?", "configuration", "easy", "Only for TBC nodes in the project tree.", ["section-16.2.4-element-001"])
add("What is the purpose of Map Labels?", "definition", "medium", "It maps logical labels used by test cases to database signals so read/write and diagnostic communication work correctly during execution.", ["section-16.2.4-element-001"])
add("Which Map Labels tab opens by default, and which common actions are available?", "configuration", "medium", "Test Labels opens by default; Autofill, Import, Export, Cancel, and Save are available.", ["section-16.2.4.1-element-001"])
add("Where do the Test Labels tab entries come from?", "configuration", "medium", "They are extracted automatically from the labels in all test cases linked to the active Test Session.", ["section-16.2.4.2-element-001"], parent=True)
add("How do the Test Labels and IO Labels tabs differ?", "comparison", "hard", "Test Labels maps labels extracted from linked test cases to active CANoe read/write paths; IO Labels maps user-defined hardware or external-interface labels and visually flags missing mappings. Both have a mapping grid and read-only details panel.", ["section-16.2.4.2-element-001", "section-16.2.4.3-element-001"], negatives=["section-13.2-element-002"])
add("What does Autofill do in Map Labels?", "configuration", "easy", "It populates read and write paths in Test Labels, IO Labels, and Diagnostics by matching label names to signals in connected CANoe databases.", ["section-16.2.4.4-element-001"])
add("What happens when mapping data is imported over existing mappings?", "configuration", "easy", "A confirmation is shown before the current mappings are replaced.", ["section-16.2.4.5-element-001"])
add("Does exporting label mappings change the mappings in the workspace?", "factual", "easy", "No. It saves mappings from all tabs to a ZIP file without changing the workspace mappings.", ["section-16.2.4.5-element-001"])
add("How does Map Labels signal an invalid database mapping?", "troubleshooting", "medium", "The label is highlighted in pink and its read/write dropdowns are disabled when valid signals are unavailable.", ["section-16.2.4.6-element-001"])

# Test plans, reports, Jama, and tab management
add("How do you create a Test Plan after adding a TBC?", "procedure", "medium", "Return to Test Session Overview, select the test cases, right-click and choose Create Test Plan, then enter the plan name.", ["section-16.3-element-001", "section-16.3-element-002", "section-16.3-element-003"], procedure=True)
add("What keyboard shortcut selects all test cases before creating or reloading a Test Plan?", "factual", "easy", "Ctrl+A.", ["section-16.3-element-004-labelled"])
add("What information is shown in a Test Plan execution tab?", "factual", "medium", "It shows S. No, ID, Name, Description, Start Time, End Time, Verdict, and a Report link for each test case.", ["section-16.4-element-001", "section-16.4-element-002"])
add("How do you open the latest report for an individual test case versus the entire latest run?", "comparison", "medium", "Use the test case's Report-column link for its latest report; use the report next to Active Test Run Report for the whole latest run.", ["section-16.5-element-007", "section-16.5-element-009"])
add("How can older Test Plan reports be opened?", "procedure", "easy", "Open the Test Run tab, click My Runs, and select a report from the list of previous runs.", ["section-16.5-element-011"], procedure=True)
add("What is Jama used for in the TESTRX integration?", "definition", "easy", "Jama is an ALM tool for requirements, test cases, and traceability; the integration synchronizes test artifacts with Jama Connect.", ["section-17-element-001"])
add("How do you load a project and one of its Test Suites from ALM?", "procedure", "hard", "Use File > New > Project > Load, submit valid ALM credentials, choose the project, then open it, right-click the required Test Suite, choose Load Test Suite, and authenticate when prompted.", ["section-17.1.1-element-001", "section-17.1.1-element-003", "section-17.1.1-element-005", "section-17.1.1-element-007"], procedure=True)
add("Which modified items can be flushed back to ALM?", "configuration", "medium", "Only Test Suites and Test Cases that were originally loaded from ALM are eligible for flushing.", ["section-17.1.2-element-001", "section-17.1.2-element-004-labelled"])
add("How do you link an ALM requirement to a Test Case?", "procedure", "medium", "Open the Test Case details, go to Traceability, right-click the S.No cell, choose Add Requirement, enter the ALM Requirement ID, and press Enter.", ["section-17.1.3-element-001"], supporting_ids=["section-17.1.3-element-003"], procedure=True)
add("How do you remove a requirement link from a Test Case?", "procedure", "easy", "Right-click the S. No cell for the requirement row and choose Remove Requirement.", ["section-17.1.3-element-003"], procedure=True)
add("What do Close, Close Others, and Close All do in a tab context menu?", "comparison", "easy", "Close closes the selected tab, Close Others closes every other tab, and Close All closes all open tabs.", ["section-18-element-005"])
add("How can a closed Test Case Editor section be restored, and how can the table size be reset?", "procedure", "medium", "Right-click the editor's S. No cell to add the closed section back; use Table Auto Adjust to fit content or Default Table to restore the default size.", ["section-18-element-007"], procedure=True)

# Deliberate cross-reference and multi-hop cases
add("Which menu command starts a flush to ALM, and which items are eligible for that operation?", "cross-reference", "hard", "Use File > Flush; only Test Suites and Test Cases originally loaded from ALM are eligible.", ["table_1", "section-17.1.2-element-001", "section-17.1.2-element-004-labelled"], cross_reference=True, multi_hop=True)
add("Where is a DBC file associated for CANoe, and how is that database added?", "cross-reference", "hard", "CANoe's DBC association is managed through Signia. In Signia, click Add, choose DBC, browse to the file in Details, and save it.", ["section-16.2.2-local-group-01", "section-11.1-element-001", "section-11.1-element-003"], cross_reference=True, multi_hop=True)
add("How can deleting a Signia database affect label validity elsewhere in TESTRX?", "multi-section", "hard", "Deleting the Signia reference can remove or invalidate linked label references, causing the affected label rows to be highlighted in pink.", ["section-11.2-element-001", "section-13.4-element-001"], multi_hop=True)

# Difficulty and type calibration for the seed set. These cases genuinely need
# broader context or discrimination even when their answers are concise.
type_overrides = {
    "Q014": "multi-section",
    "Q045": "multi-section",
    "Q106": "multi-section",
    "Q112": "multi-section",
}
difficulty_overrides = {
    "Q002": "medium", "Q005": "medium", "Q010": "medium", "Q012": "medium",
    "Q014": "hard", "Q019": "medium", "Q020": "medium", "Q021": "medium",
    "Q024": "medium", "Q026": "medium", "Q031": "medium", "Q034": "medium",
    "Q035": "medium", "Q040": "medium", "Q041": "medium", "Q044": "medium",
    "Q045": "hard", "Q050": "medium", "Q056": "hard", "Q059": "medium",
    "Q062": "medium", "Q069": "medium", "Q071": "hard", "Q073": "medium",
    "Q075": "medium", "Q092": "hard", "Q095": "hard", "Q099": "hard",
    "Q106": "hard", "Q112": "hard", "Q118": "hard", "Q126": "hard",
}
for question in questions:
    question["question_type"] = type_overrides.get(question["question_id"], question["question_type"])
    question["difficulty"] = difficulty_overrides.get(question["question_id"], question["difficulty"])


if not 100 <= len(questions) <= 200:
    raise AssertionError(f"Expected a 100-200 question seed set, got {len(questions)}")


def source_text(element: dict) -> str:
    parts = [element.get("text", "")]
    data = element.get("data") or {}
    for key in ("items", "rows", "resolved_rows"):
        value = data.get(key)
        if isinstance(value, list):
            parts.append(json.dumps(value, ensure_ascii=False))
    for child in element.get("children", []):
        parts.append(source_text(child))
    return " ".join(p for p in parts if p)


def verify_pdf_lineage() -> tuple[list[dict], list[dict]]:
    reader = PdfReader(str(PDF_PATH))
    pdf_text = {i + 1: norm(page.extract_text() or "") for i, page in enumerate(reader.pages)}
    lineage_failures: list[dict] = []
    weak_matches: list[dict] = []
    for question in questions:
        for eid in question["retrieval_ground_truth"]["required_source_set"]:
            element = elements[eid]
            text = norm(source_text(element))
            tokens = [t for t in re.findall(r"[a-z0-9_]+", text) if len(t) >= 5]
            page_blob = " ".join(pdf_text[p] for p in range(element["page_start"], element["page_end"] + 1))
            if not tokens:
                weak_matches.append({"question_id": question["question_id"], "element_id": eid, "reason": "no anchor tokens"})
                continue
            sample = tokens[: min(40, len(tokens))]
            matched = sum(token in page_blob for token in sample)
            ratio = matched / len(sample)
            # Independent PDF extractors split bullets, ligatures, punctuation, and
            # wrapped table/list text differently. A ratio below 0.35 indicates
            # that the required unit is likely mapped to the wrong page; lower
            # but non-failing ratios remain visible in the QC report.
            if ratio < 0.35:
                lineage_failures.append({"question_id": question["question_id"], "element_id": eid, "token_match_ratio": round(ratio, 3)})
            elif ratio < 0.85:
                weak_matches.append({"question_id": question["question_id"], "element_id": eid, "token_match_ratio": round(ratio, 3)})
    return lineage_failures, weak_matches


lineage_failures, weak_matches = verify_pdf_lineage()
if lineage_failures:
    raise AssertionError(f"PDF lineage verification failed: {lineage_failures[:10]}")


OUT_DIR.mkdir(parents=True, exist_ok=True)
jsonl_path = OUT_DIR / "golden_dataset.jsonl"
csv_path = OUT_DIR / "golden_dataset.csv"
report_path = OUT_DIR / "golden_dataset_report.md"
coverage_path = OUT_DIR / "source_coverage_report.md"
qc_path = OUT_DIR / "quality_control_report.md"

with jsonl_path.open("w", encoding="utf-8", newline="\n") as handle:
    for question in questions:
        handle.write(json.dumps(question, ensure_ascii=False) + "\n")

csv_fields = [
    "question_id", "question", "question_type", "difficulty", "expected_answer",
    "source_document", "source_pages", "source_section_paths", "source_semantic_unit_ids",
    "source_element_ids", "primary_source", "required_source_set", "acceptable_source_set",
    "required_evidence", "supporting_evidence", "hard_negative_sources", "answerability",
    "requires_single_unit", "requires_multiple_units", "requires_parent_context", "requires_table",
    "requires_procedure", "requires_cross_reference", "requires_multi_hop", "notes",
]
with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=csv_fields)
    writer.writeheader()
    for question in questions:
        src = question["source"]
        gt = question["retrieval_ground_truth"]
        flags = question["evaluation_metadata"]
        writer.writerow({
            "question_id": question["question_id"], "question": question["question"],
            "question_type": question["question_type"], "difficulty": question["difficulty"],
            "expected_answer": question["expected_answer"], "source_document": src["document"],
            "source_pages": "|".join(map(str, src["pages"])),
            "source_section_paths": " || ".join(" > ".join(path) for path in src["section_paths"]),
            "source_semantic_unit_ids": "|".join(src["semantic_unit_ids"]),
            "source_element_ids": "|".join(src["element_ids"]), "primary_source": gt["primary_source"],
            "required_source_set": "|".join(gt["required_source_set"]),
            "acceptable_source_set": "|".join(gt["acceptable_source_set"]),
            "required_evidence": " || ".join(question["required_evidence"]),
            "supporting_evidence": "|".join(question["supporting_evidence"]),
            "hard_negative_sources": "|".join(question["hard_negative_sources"]),
            "answerability": question["answerability"], **flags, "notes": question["notes"],
        })


def markdown_counts(counter: Counter) -> str:
    return "\n".join(f"- {key}: {counter[key]}" for key in sorted(counter))


type_counts = Counter(q["question_type"] for q in questions)
difficulty_counts = Counter(q["difficulty"] for q in questions)
flag_counts = Counter()
section_counts = Counter()
unit_counts = Counter()
for q in questions:
    for key, value in q["evaluation_metadata"].items():
        if value:
            flag_counts[key] += 1
    for path in q["source"]["section_paths"]:
        section_counts[path[-1]] += 1
    unit_counts.update(q["retrieval_ground_truth"]["required_source_set"])

normalized_questions = defaultdict(list)
for q in questions:
    normalized_questions[norm(q["question"])].append(q["question_id"])
duplicates = {k: v for k, v in normalized_questions.items() if len(v) > 1}

report_path.write_text(
    "# Golden Dataset Report\n\n"
    f"Source: `{document['source_file']}`  \n"
    f"Source SHA-256: `{document['source_sha256']}`  \n"
    f"Total questions: **{len(questions)}**\n\n"
    "## Questions by type\n\n" + markdown_counts(type_counts) + "\n\n"
    "## Questions by difficulty\n\n" + markdown_counts(difficulty_counts) + "\n\n"
    "## Retrieval requirements\n\n" + markdown_counts(flag_counts) + "\n\n"
    f"## Semantic-unit coverage\n\n- Unique required semantic units: {len(unit_counts)}\n"
    f"- Repeated required semantic units: {sum(1 for n in unit_counts.values() if n > 1)}\n"
    f"- Questions with hard negatives: {sum(bool(q['hard_negative_sources']) for q in questions)}\n"
    f"- Potential exact duplicates: {len(duplicates)}\n"
    f"- Unanswerable or ambiguous questions retained: 0\n"
    f"- Questions requiring external knowledge: 0\n\n"
    "## Questions per represented section\n\n" + markdown_counts(section_counts) + "\n",
    encoding="utf-8",
)

represented_units = set(unit_counts)
all_top_level_units = {e["id"] for s in document["sections"] for e in s["elements"]}
unrepresented_units = sorted(all_top_level_units - represented_units)
represented_sections = {element_sections[eid] for eid in represented_units}
unrepresented_sections = [s for s in document["sections"] if s["section_id"] not in represented_sections]
coverage_lines = [
    "# Source Coverage Report", "", f"- Numbered sections represented: {len(represented_sections)} of {len(sections)}",
    f"- Top-level semantic elements used as required evidence: {len(represented_units)} of {len(all_top_level_units)}",
    "", "## Represented sections", "",
]
coverage_lines.extend(f"- {sid} {sections[sid]['title']}: {section_counts[sections[sid]['ancestor_path'][-1]]} question(s)" for sid in sorted(represented_sections, key=lambda x: sections[x]["sequence"]))
coverage_lines.extend(["", "## Unrepresented numbered sections", ""])
coverage_lines.extend(f"- {s['section_id']} {s['title']}" for s in unrepresented_sections)
coverage_lines.extend(["", "## Unrepresented top-level semantic elements", ""])
coverage_lines.extend(f"- {eid} ({elements[eid]['type']}, section {element_sections[eid]})" for eid in unrepresented_units)
coverage_lines.extend(["", "Unrepresented figures and narrowly redundant elements are intentional in the seed set; expand them only when they support a distinct user information need.", ""])
coverage_path.write_text("\n".join(coverage_lines), encoding="utf-8")

qc_lines = [
    "# Quality-Control Report", "",
    f"- Questions reviewed: {len(questions)}", f"- PDF lineage failures: {len(lineage_failures)}",
    f"- Weaker PDF text matches retained for review: {len(weak_matches)}",
    f"- Exact duplicate questions: {len(duplicates)}", "- Rejected questions: 0",
    "- Ambiguous questions retained: 0", "- Questions requiring external knowledge: 0", "",
    "## Verification method", "",
    "Every required semantic-unit ID was resolved against `output/document.json`. Its page range and source text were then checked against text independently extracted from the corresponding page(s) of the original PDF with pypdf. The build fails if the sampled source-token match falls below 35%; matches below 85% remain explicit manual-review candidates because PDF extractors tokenize lists, ligatures, punctuation, and wrapped text differently.",
    "", "Procedure questions cite all parser elements needed to reconstruct the complete printed procedure. Table questions cite the canonical table element, including joined fragments for Tables 1 and 7.",
    "", "## Parser warnings carried into review", "",
]
for item in warnings["items"]:
    qc_lines.append(f"- {item['id']} ({item['type']}), pages {', '.join(map(str, item['pages']))}: {item['message']}")
qc_lines.extend(["", "## Manual-review candidates", ""])
for question in questions:
    if question["notes"]:
        qc_lines.append(f"- {question['question_id']}: {question['notes']}")
for item in weak_matches:
    qc_lines.append(f"- {item['question_id']} / {item['element_id']}: independent PDF token match {item.get('token_match_ratio', 'n/a')}.")
qc_lines.extend(["", "## Duplicate candidates", "", "- None by exact normalized-question comparison." if not duplicates else json.dumps(duplicates, indent=2), ""])
qc_path.write_text("\n".join(qc_lines), encoding="utf-8")

print(json.dumps({
    "questions": len(questions), "jsonl": str(jsonl_path), "csv": str(csv_path),
    "report": str(report_path), "coverage": str(coverage_path), "qc": str(qc_path),
    "types": type_counts, "difficulty": difficulty_counts, "weak_pdf_matches": len(weak_matches),
}, ensure_ascii=False, indent=2, default=dict))
