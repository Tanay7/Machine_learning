now in the legacy code: If I have to remove the data volume , what should I do? what date filetrs can I change?


To reduce the data volume in the **legacy code** (the original scripts provided), you should focus on the **`WHERE` clauses** that filter by `TERMINATION_DATE` or `INCEPTION_DATE`.

The legacy pipeline has two main "gates" where data enters the system. Tightening the dates at these points is the most effective way to reduce volume without breaking the logic.

Here are the specific locations and changes you should make:

### 1\. The Main Extraction Gate (Source 1 & 2)

This is the very first step where data is pulled from the `GENERAL_POLICY` table into the staging table `alterian_monthly_extract_churn`.

  * **Location:** Source 2
  * **Current Code:**
    ```sql
    WHERE (A.EFF_MKR in ('A','B') or A.TERMINATION_DATE >= date '2019-01-01')
    ```
    [cite\_start][cite: 2]
  * **What to change:** Change `2019-01-01` to a more recent date (e.g., `2023-01-01`).
  * **Effect:** This filters out older "Lapsed" policies. It will drastically reduce the number of inactive customers entering the matching algorithm.
  * **Warning:** Do **not** remove `A.EFF_MKR in ('A','B')` or change the `OR` to `AND` here, as that ensures you still capture all currently **Active** policies regardless of dates.

### 2\. The Policy Processing Gate (Source 132)

Later in the pipeline, the script repopulates a table called `gi_general_policy_churn`. This has a separate, stricter filter.

  * **Location:** Source 132
  * **Current Code:**
    ```sql
    WHERE (EFF_MKR in ('A','B')  and TERMINATION_DATE >= date '2021-01-01')
    ```
    [cite\_start][cite: 132]
  * **What to change:** Update `2021-01-01` to match the date you chose in Step 1 (e.g., `2023-01-01`).
  * **Effect:** This ensures the churn calculation logic (Phase 4) doesn't process policies that you already filtered out in Step 1, or further restricts the set used for the final churn join.

### 3\. The Qlik Load Script (Source 156)

If you are also running the Qlik/Reporting layer (the final step of the legacy text file), there is a load filter there as well.

  * **Location:** Source 156
  * **Current Code:**
    ```qlik
    where Date(Floor(inception_date)) > '31/12/2018';
    ```
    [cite\_start][cite: 156]
  * **What to change:** Update `'31/12/2018'` to a more recent date.
  * **Effect:** This restricts the final report to show only recent policy inceptions.

-----

### Summary of Recommended Changes

To significantly reduce volume while keeping the pipeline functional for testing, change these lines:

| Source | Original Date | Recommended Test Date |
| :--- | :--- | :--- |
| [cite\_start]**[cite: 2]** | `'2019-01-01'` | `'2024-01-01'` |
| [cite\_start]**[cite: 132]** | `'2021-01-01'` | `'2024-01-01'` |
| [cite\_start]**[cite: 156]** | `'31/12/2018'` | `'31/12/2023'` |

**Note on "Diff" Logic:**
Do **not** change the logic `where diff < 3 and diff > -21` in Source 147 and 151. This defines *what a churn is* (the gap between policies). [cite\_start]Changing this won't reduce input volume; it will just break the business definition of churn[cite: 147, 151].
