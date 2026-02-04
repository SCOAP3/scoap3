# import re

# from gitlint.rules import CommitRule, RuleViolation

# EXAMPLE GITLINT CONFIGURATION

# class SignedOffBy(CommitRule):
#     """This rule will enforce that each commit contains a "Signed-off-by" line."""

#     name = "body-requires-signed-off-by"
#     id = "Workflows1"

#     def validate(self, commit):
#         for line in commit.message.body:
#             if line.startswith("Signed-off-by"):
#                 return

#         msg = "Body does not contain a 'Signed-Off-By' line"
#         return [RuleViolation(self.id, msg, line_nr=1)]


# class ApprovedSubject(CommitRule):
#     """Validate subject of each commit.

#     This rule will enforce that each commit starts with a "module: text" format.
#     The 'module' can be any alphanumeric word, and the message must start with a
#     colon followed by a space.
#     """

#     name = "approved-subject-in-title"
#     id = "Workflows2"

#     MODULE_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+: .+")

#     def validate(self, commit):
#         title = commit.message.title

#         if not self.MODULE_PATTERN.match(title):
#             msg = "Subject does not follow 'module: text' format"
#             return [RuleViolation(self.id, msg, line_nr=1)]

#         return
