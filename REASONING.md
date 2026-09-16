FairShare --- Group Contribution & Settlement
A simple contribution manager that turns messy payment records into
clear, fair settlements.

1. Problem Statement
When a group buys a shared gift, everyone is expected to contribute an
equal amount.

In reality, payment records are rarely clean:

One person may pay the full amount.

Someone may pay only part of their share.

A person may cover another participant.

The same payment may appear more than once.

The same person may appear with different capitalization or spacing.

Names may contain small spelling variations.

Amounts may appear as 1000, ₹1,000, Rs. 1000, etc.

Some rows may be incomplete or invalid.

The difficult part is not simply adding the payments. The system must
first determine which records are valid, who they belong to, and
whether duplicate records should be ignored.

FairShare solves this in two stages:

Clean the contribution data → calculate fair balances → generate
settlements.

2. Goal
Given:

A total gift budget

A list of participants

Existing contributions

Optionally, a messy CSV containing past contributions

the application answers:

How much has been collected?

How much remains?

What is each person's fair share?

Who still owes money?

Who has paid extra?

Who should pay whom?

Which imported records were accepted, merged, duplicated, or
rejected?

The system is designed for an arbitrary group, not for one fixed
example.

3. Core Idea
The most important calculation is the balance of each participant.

Fair share
If:

Total budget = ₹6,000
Participants = 6
then:

Fair share = ₹6,000 / 6
           = ₹1,000 per person
Balance
For every participant:

Balance = Amount Paid - Fair Share
Therefore:

Balance = 0 → settled

Balance < 0 → participant still owes money

Balance > 0 → participant should receive money

Example:

Participant Paid Fair Share Balance

Ayushi ₹1,000 ₹1,000 ₹0
Riya ₹500 ₹1,000 -₹500
Rahul ₹1,500 ₹1,000 +₹500

Rahul has paid ₹500 extra, while Riya owes ₹500.

The application then converts these balances into a simple settlement
such as:

Riya → Rahul ₹500
4. Handling the CSV Twist
The CSV importer is a major part of the project.

Instead of trusting imported data blindly, FairShare processes each row
before it affects the final balances.

The pipeline is:

Messy CSV
   ↓
Read rows
   ↓
Validate required fields
   ↓
Normalize names
   ↓
Normalize amounts
   ↓
Detect duplicate records
   ↓
Detect close name variations
   ↓
Accept / Reject
   ↓
Store valid contributions
   ↓
Recalculate balances
   ↓
Generate settlements
This makes the system more reliable than simply importing every row
as-is.

5. Name Normalization
People can appear in a CSV in multiple forms:

Ayushi Gupta
ayushi gupta
 AYUSHI GUPTA
Ayushi   Gupta
These should represent the same participant.

The importer therefore normalizes basic formatting differences such as:

Leading/trailing spaces

Repeated spaces

Capitalization

Example:

"  ayushi   gupta "
        ↓
"Ayushi Gupta"
The system also detects close spelling variations when appropriate.

Example:

Aman Sing
Aman Singh
can be identified as a close name variation and mapped to the canonical
participant name.

Why this matters
Without normalization, the application could incorrectly treat one
person as multiple people and calculate the wrong fair share.

6. Amount Normalization
Contribution amounts may use different formats:

1000
₹1000
₹1,000
Rs. 1000
Rs 1,000
The importer converts supported formats into a consistent numeric value.

For example:

"₹1,000" → 1000
"Rs. 500" → 500
"500"     → 500
Invalid amounts are not silently accepted.

7. Duplicate Detection
Duplicate contributions are dangerous because they can artificially
increase the collected amount.

For example:

Ayushi Gupta, ₹1000
Ayushi Gupta, ₹1000
If the second row is the same transaction recorded twice, counting both
would incorrectly produce:

₹2,000
instead of:

₹1,000
FairShare detects duplicate rows before adding them to the final
contribution data.

The import report records how many duplicates were removed.

8. Invalid Data Handling
The importer does not allow bad rows to silently affect the calculation.

Examples of rows that can be rejected:

,1000
Ayushi Gupta,
Ayushi Gupta,-500
Ayushi Gupta,abc
Instead of crashing the entire import, the system keeps processing valid
rows and reports rejected records separately.

This follows an important design principle:

One bad row should not make the whole import unusable.

9. Import Report
After processing a CSV, the application shows an import summary.

Example:

13 data rows checked

5 Imported
5 Duplicates removed
6 Name variants merged
3 Rejected
The report gives the organiser visibility into what happened to the
input data.

Detailed sections can show:

Merged name variants

Duplicate rows

Rejected rows

This is useful because the user can verify the cleaning process instead
of trusting a hidden transformation.

10. Settlement Algorithm
Once the contribution data is clean, the application calculates
participant balances.

There are two groups:

Debtors
Participants whose balance is negative.

Riya  -₹500
Aman  -₹300
Creditors
Participants whose balance is positive.

Rahul +₹500
Neha  +₹300
The settlement process matches debtors with creditors.

Conceptually:

Debtors                    Creditors

Riya  owes ₹500    →       Rahul receives ₹500
Aman  owes ₹300    →       Neha receives ₹300
The result is a short list of payments rather than asking everyone to
pay everyone else.

Why this approach?
The organiser does not need to manually reason through every
contribution.

The system converts:

Individual payments
        ↓
Net balances
        ↓
Minimal/simple payment instructions
11. Preventing Double Counting
A particularly important design consideration is the difference between:

money paid into the group pool

and

money one participant covered for another person.

These should not automatically be treated as two separate contributions.

For example, if Rahul pays ₹2,000 and says that ₹1,000 was also covering
Aman, the system should not accidentally count:

Rahul = ₹2,000
Aman  = ₹1,000
as ₹3,000 collected unless the underlying transaction actually
represents that additional money.

The safest approach is to treat the actual payment as the contribution
and use the participant relationship/note only to explain who the
payment was intended to cover.

This keeps the financial calculation consistent.

12. Application Architecture
The project uses a lightweight architecture:

                 ┌──────────────────────┐
                 │      Web Browser      │
                 │   HTML / CSS / JS     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │      Flask App       │
                 │   Routes / Logic     │
                 └───────┬───────┬──────┘
                         │       │
              ┌──────────┘       └───────────┐
              ▼                              ▼
     ┌─────────────────┐            ┌─────────────────┐
     │  CSV Importer   │            │   Settlement    │
     │ Clean & Validate│            │ Balance & Match │
     └────────┬────────┘            └────────┬────────┘
              │                              │
              └──────────────┬───────────────┘
                             ▼
                    ┌─────────────────┐
                    │  SQLite Database│
                    └─────────────────┘
13. Technology Stack
Backend
Python

Flask

SQLite

Frontend
HTML

CSS

JavaScript

Data Processing
Python CSV/data-cleaning logic

Name normalization

Amount parsing

Duplicate detection

Validation

The stack was intentionally kept lightweight so the application can run
easily in a development environment such as GitHub Codespaces.

14. Why SQLite?
The project does not require a large database system.

SQLite is sufficient because:

The application is lightweight.

Data is stored locally.

Setup is simple.

No separate database server is required.

It works well for a small group contribution application.

This keeps the build focused on the actual problem rather than
infrastructure.

15. Why Deterministic Cleaning Instead of AI?
The CSV cleaning rules are intentionally deterministic.

For example:

" ayushi gupta "
        ↓
trim spaces
        ↓
normalize case
        ↓
"Ayushi Gupta"
Financial data should not depend on unpredictable decisions.

For important operations such as:

duplicate detection

amount parsing

validation

balance calculation

the application uses explicit rules.

Fuzzy matching can assist with close name variations, but the final
result is still reported transparently.

The principle is:

Use automation for repetitive work, but keep financial calculations
explainable.

16. Example End-to-End Flow
Suppose the budget is:

₹6,000
and there are:

6 participants
FairShare calculates:

₹6,000 ÷ 6 = ₹1,000 per person
The imported data may contain:

Ayushi Gupta, ₹1000
ayushi gupta, ₹1000
Riya Sharma, Rs. 500
RAHUL MEENA, ₹1500
Aman Sing, ₹1000
Aman Singh, ₹1000
The importer first cleans the records.

It then:

Normalizes name formatting.

Detects close name variations.

Removes duplicate transactions.

Rejects invalid rows.

Stores valid contributions.

Recalculates participant totals.

Calculates balances against the fair share.

Generates the required payment instructions.

The organiser sees the final financial state, along with an
explanation of how the messy input was processed.

17. Design Decisions
Simple before clever
The application starts with the easiest understandable model:

Equal share
    ↓
Paid amount
    ↓
Balance
    ↓
Settlement
This makes the system easy to explain and test.

Transparent processing
Imported data is not silently changed.

The import report tells the user:

What was imported

What was duplicated

What was merged

What was rejected

Local-first
The application can run locally without requiring external services.

Arbitrary groups
The logic is based on participant data rather than hard-coded names or
amounts.

Practical UI
The interface is designed like a financial ledger so that the important
numbers --- collected amount, remaining amount, participant balances,
and settlements --- are easy to find.

18. Edge Cases Considered
The application should handle situations such as:

No participants

One participant

Participant has paid exactly their share

Participant has paid more than their share

Participant has paid less than their share

Nobody has paid yet

Budget has already been reached

Duplicate CSV records

Different name capitalization

Extra spaces in names

Close spelling variations

Currency symbols in amounts

Invalid amounts

Missing names

Missing amounts

Negative contributions

Empty CSV rows

The goal is graceful handling rather than unexpected application
failure.

19. Testing Strategy
The data-cleaning logic is separated into its own importer module so it
can be tested independently.

Important test cases include:

✓ Normal name formatting
✓ Case/spacing normalization
✓ Amount parsing
✓ Duplicate detection
✓ Close name matching
✓ Invalid row rejection
✓ Valid rows being imported
Separating the importer from the UI also makes debugging easier.

20. What Makes This Project Different
At first glance, this looks like a simple expense-sharing application.

The actual challenge is the data quality problem.

A normal implementation might assume:

Name + Amount = clean data
FairShare instead handles:

Messy real-world data
        ↓
Data quality checks
        ↓
Reliable contribution records
        ↓
Fair-share calculation
        ↓
Actionable settlements
So the project demonstrates more than CRUD operations. It demonstrates:

Data cleaning

Validation

Entity/name normalization

Duplicate detection

Financial calculations

Algorithmic settlement generation

Database persistence

Frontend-backend integration

Explainable processing

21. Future Improvements
Possible extensions include:

Login and multiple groups

Export settlement summary as PDF/CSV

WhatsApp/shareable settlement messages

Manual correction of rejected CSV rows

Better duplicate detection using transaction IDs

Support for unequal shares

Partial ownership of expenses

Payment status tracking

Multiple currencies

Audit history for imported files

These are intentionally outside the core implementation so that the
current application remains simple and reliable.

22. Final Outcome
FairShare turns a messy contribution sheet into a clear answer:

How much has been collected?
How much does each person owe?
Who has paid extra?
Who should receive money?
What happened to the imported data?
The core philosophy is:

Clean the data first. Calculate fairly. Explain the result.

That makes the application useful not only for the farewell-gift
scenario, but for any small group that needs to collect money fairly and
settle contributions without manual calculation.
