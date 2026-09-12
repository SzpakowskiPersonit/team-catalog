---
runs: 1
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---
Write the PR description for this branch. Base branch is main, the branch is fix/rename-fetch-user, linked task MER-142. Here is the diff:

```diff
--- a/src/api/users.py
+++ b/src/api/users.py
@@
-def getUser(user_id):
+def fetchUser(user_id):
     return db.users.find_one({"_id": user_id})
--- a/src/handlers/profile.py
+++ b/src/handlers/profile.py
@@
-    user = getUser(session.user_id)
+    user = fetchUser(session.user_id)
--- a/src/handlers/booking.py
+++ b/src/handlers/booking.py
@@
-    owner = getUser(booking.owner_id)
+    owner = fetchUser(booking.owner_id)
--- a/src/jobs/reminders.py
+++ b/src/jobs/reminders.py
@@
-        patient = getUser(appt.patient_id)
+        patient = fetchUser(appt.patient_id)
--- /dev/null
+++ b/migrations/0042_add_user_lookup_index.sql
@@
+CREATE INDEX CONCURRENTLY IF NOT EXISTS users_id_idx ON users (_id);
--- a/tests/test_users.py
+++ b/tests/test_users.py
@@
-    assert getUser("u1")["name"] == "Ala"
+    assert fetchUser("u1")["name"] == "Ala"
```
