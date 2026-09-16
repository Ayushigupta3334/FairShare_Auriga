ROUND 2  ·  BUILD ROUND
Chipping in for the farewell gift
The team is buying a farewell gift for their manager — budget ₹6,000. Everyone agreed to chip in equally, but in practice it’s chaos: some have paid their full share, a few paid only part, one generous soul paid extra to cover a friend, and two people haven’t paid at all. The organiser is constantly asked ‘how much do I still owe?’ and ‘have we collected enough yet?’ At the end the organiser just wants the simplest list of who should pay whom so everyone lands on their fair share.
Build something so the organiser can track the pool and settle up fairly.
(The questions the organiser keeps fielding are your clues — and build for any pool and organiser, not just this one. The easier you make it to see shares, balances and what’s left to collect, the better. Start with equal shares and simple balances, then settlements.)

this is one of the assignment i have given that you have to make think uniquely and creatively with these rules are given below with the idea of creating a simple ui that is easy to use and understand. And all the mention point must be come within.
The final solution must be a public GitHub repository, and its root folder must contain the following three files, which are required for evaluation:
- README.md — instructions for project setup, running, and debugging.
- REASONING.md — an explanation of the thought process behind the solution.
- AI_LOGS.md — a complete copy of the candidate's conversation with the AI tool (Copilot or any other). This log must be pasted as-is and not modified in any way; any alteration will lead to a deduction of marks

Perfect — that works just as well. Now let's get it running.

Step 1: Double-check the upload went cleanly
On your repo's GitHub page, confirm you see this exact structure (click into folders to check they're not empty):

.devcontainer/
  devcontainer.json
static/
  app.js
  style.css
templates/
  index.html
tests/
  test_settlement.py
.gitignore
AI_LOGS.md
README.md
REASONING.md
app.py
database.py
requirements.txt
settlement.py
If .devcontainer, static, templates, or tests are missing, or show up empty — go back and upload just that folder's contents again (drag the folder in, GitHub will recreate it). This matters: without .devcontainer/devcontainer.json, Codespaces won't auto-install dependencies, and without templates/+static/, the app has no page to show.

Step 2: Launch Codespaces
On the repo's main page → green Code button → Codespaces tab → Create codespace on main

Wait for it to finish building (you'll see a terminal open at the bottom, and setup logs scroll by — this takes 30–90 seconds the first time).

Step 3: Confirm dependencies installed
In the terminal that opens automatically:

bash
flask --version
Prints a version number → good, continue to Step 4.
Error → run pip install -r requirements.txt manually, then retry.
Step 4: Run the app
bash
python app.py
You should see Running on http://127.0.0.1:5000.

Step 5: Open it
A popup should appear in the bottom-right saying a port was forwarded — click Open in Browser.
If no popup appears: click the Ports tab (next to the Terminal tab) → find row 5000 → click the little globe/browser icon next to it.

Try it and tell me what you see at each step — especially Step 1, since that's the one most likely to have gone sideways with a manual upload.

okay ya so it is running now i want you to change some ui of it make it more flexible to the user and some images point i will give you images and the name will be fairshare i want

Ran a command
Let's start with the rename since that's unambiguous, and I'll ask about a couple of things before touching the UI further.

By "more flexible for the user," what matters most to you?
Better mobile/responsive layout & editing
Ran a command
Renaming to FairShare and improving mobile responsiveness + inline editing now. I'll also add a spot for your images once you upload them — go ahead and attach them whenever ready and I'll drop them in (logo/cover image, icons, etc.).

Ran a command
Good, still here. Let's make the changes: rename to FairShare, add inline editing (no more delete-and-retype for a payment or a name), and a proper mobile card layout for the ledger.

1. Database — add update queries for members/payments
Edited 7 files, ran 7 commands, shared files

Fairshare
ZIP 

App
PY 

App
JS 

Style
Code·CSS 

Index
Code·HTML 

Test settlement
PY 
I already have a working Flask + SQLite + HTML/CSS/JavaScript application called FairShare.

IMPORTANT:
Do NOT rebuild the application.
Do NOT change the existing visual design significantly.
Do NOT migrate to React.
Do NOT replace Flask or SQLite.
Do NOT rewrite settlement.py.

I need to add the BUILD ROUND TWIST:

"The solution must import a messy list of past contributions — with duplicate entries, the same person's name spelled differently, amounts written in inconsistent formats, and some invalid rows. Import it, produce correct balances from the cleaned data, and report what was imported, de-duplicated, merged, and rejected."

First inspect the existing project structure and preserve the current architecture.

CURRENT IMPORTANT FILES:
- app.py
- database.py
- settlement.py
- templates/index.html
- static/app.js
- static/style.css

IMPLEMENT THIS WITH MINIMAL CHANGES.

1. CREATE NEW FILE:
fairshare/importer.py

Keep all CSV cleaning/import logic here.

The importer must:

A. Read CSV files with columns:
name, amount, note

B. Normalize names:
- trim leading/trailing whitespace
- collapse multiple spaces
- case-insensitive comparison
- recognize obvious spelling/format variants
- use conservative fuzzy matching for close names
- NEVER merge two names when confidence is low
- if a name matches an existing participant, use the existing participant

Example:
"ayushi gupta" → "Ayushi Gupta"
"AYUSHI GUPTA" → "Ayushi Gupta"
"Riya  Sharma" → "Riya Sharma"

C. Normalize amounts:
Accept formats such as:
1000
1000.00
₹1000
₹ 1,000
1,000
Rs. 1000
Rs 1,000

Convert them to numeric rupee amounts.

D. Reject invalid rows:
- missing name
- missing amount
- non-numeric amount
- negative amount
- malformed row

E. Detect duplicate contribution rows.

For this application, an exact duplicate means the same normalized person + same amount + same note.

Do NOT treat two legitimate payments from the same person for the same amount as duplicates unless they are exact duplicate rows.

F. Produce an import report containing:
- total rows
- imported rows
- duplicate rows
- merged name rows
- rejected rows
- details of merged names
- details of rejected rows
- details of duplicates

2. MODIFY app.py

Add a new endpoint:

POST /api/import

It should accept a CSV file using multipart/form-data.

The endpoint should:
- receive the uploaded CSV
- call importer.py
- resolve cleaned names against existing members
- create a new member when an imported name does not already exist
- insert valid non-duplicate contributions into the existing payments table
- return the import report
- then return the updated state

Do NOT duplicate balance or settlement calculations.

Continue using the existing:
compute_balances()
pool_status()
settle()

3. MODIFY templates/index.html

Add a new section between "Pool status" and "Transactions".

Title:
"Import past contributions"

Subtitle:
"clean a messy CSV without losing the audit trail"

Include:
- CSV file input
- Import button
- small supported-format hint
- import report area

The report should clearly show:

ROWS FOUND
IMPORTED
DUPLICATES REMOVED
NAMES MERGED
REJECTED

Also show expandable/detail lists for:
- merged names
- duplicate rows
- rejected rows

4. MODIFY static/app.js

Add the import functionality using fetch() and FormData.

After successful import:
- refresh the existing dashboard
- show the import report
- ensure imported payments appear in Transactions
- ensure balances update
- ensure pool status updates
- ensure settlement updates

Do not duplicate business logic in JavaScript.

5. MODIFY static/style.css only as necessary.

Keep the existing ledger/passbook visual style.

Do NOT redesign the application.

6. Add a "Load Demo CSV" option if practical, but the main requirement is real CSV upload.

7. IMPORTANT EDGE CASES

Test:
- different capitalization of names
- extra spaces in names
- ₹1,000
- Rs. 1000
- 1000
- invalid amount
- negative amount
- missing name
- duplicate row
- same person making two legitimate payments
- imported name matching an existing participant
- imported new participant
- empty CSV
- malformed CSV

8. After implementation, explain exactly:
- which files were changed
- what importer.py does
- how duplicate detection works
- how name merging works
- how invalid rows are rejected
- how imported data reaches SQLite
- how the existing settlement algorithm uses the cleaned payments

Do not modify the existing settlement algorithm unless absolutely necessary.
Use the demo CSV that I included in the updated project.

📁 Location

Inside your project:

fairshare/
└── static/
    └── demo_contributions.csv

So in Codespaces, look for:

static → demo_contributions.csv

Then select that file in Import Past Contributions.

What is inside it?

It's intentionally messy to demonstrate the twist:

Different capitalization of names
Extra spaces in names
₹1000
₹ 1,000
Rs. 2,000
Duplicate contribution rows
Similar/spelled-differently names
Missing names
Invalid amounts
Negative amounts

So it lets you demonstrate the complete requirement:

Messy CSV
   ↓
Import
   ↓
✓ Imported
↻ Duplicates removed
≈ Names merged
✕ Invalid rows rejected
   ↓
Correct balances
   ↓
Settlement plan
If you don't see the file

In your Codespaces terminal, run:

find . -name "demo_contributions.csv"

It should return something like:

./static/demo_contributions.csv

Don't use your old CSV from another project. Use static/demo_contributions.csv for your demo.

do you think it get messy in seeing?

Yes — a little messy visually, especially because the “Merged names” section shows 6 individual rows immediately. The functionality is good, but for a build-round demo, you want the screen to look clean and intentional, not like a debugging log.

I’d change it like this:

What I would improve

1. Keep the summary exactly as it is
The top is excellent:

13 rows checked → 5 imported
5 duplicates → 6 names merged → 3 rejected

That immediately proves your CSV-cleaning feature works.

2. Collapse the details by default

Instead of showing:

Merged names (6)
Row 2 ...
Row 3 ...
Row 5 ...
Row 7 ...
Row 9 ...
Row 11 ...

show:

▸ Merged names (6)
▸ Duplicates removed (5)
▸ Rejected rows (3)

Then the judge can click one if they want to inspect the details.

3. Make the report hierarchy clearer

I'd aim for:

IMPORT REPORT                         5 imported
13 data rows checked

┌──────────┬──────────────┬────────────┬──────────┐
│ 5        │ 5            │ 6          │ 3        │
│ Imported │ Duplicates   │ Names      │ Rejected │
│          │ removed      │ merged     │          │
└──────────┴──────────────┴────────────┴──────────┘

▸ Merged names (6)
▸ Duplicates removed (5)
▸ Rejected rows (3)

This is much cleaner.

One more important thing

Your current wording:

Names merged: 6

could be slightly confusing because a judge might think 6 people were merged.

I'd use:

6 name variations merged

or:

6 name variants normalized

Then the details can show:

ayushi gupta → Ayushi Gupta
RAHUL MEENA → Rahul Meena
Aman Singhh → Aman Singh

That makes the twist of the problem immediately obvious.

Overall

Don't redesign the whole UI. Your dark ledger aesthetic is actually distinctive. Just make the detailed report collapsed by default. That one change will make it feel much more like a polished product and less like raw processing output.

If you want, I can also give you the 
exact HTML/CSS changes to make this report compact without touching the rest of your project.
