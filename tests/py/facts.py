"""Facts for the logic tier, built as crew's readers return them, so a case reads as its scenario."""
import hashlib

ALICE = ("Alice", "alice@example.com")


def commit(subject, author=ALICE, body="", sha=None):
    """A commit as plan.commits_beyond reads it: sha, short sha, subject, and who (author name, email, message).
    Two commits with the same subject, author and body are the same commit replayed; give each its own sha."""
    message = subject + ("\n\n" + body if body else "") + "\n"
    sha = sha or hashlib.sha1(f"{subject}{author}{body}{id(message)}".encode()).hexdigest()
    return {"sha": sha, "short": sha[:7], "subject": subject, "who": (author[0], author[1], message)}


def replayed(c, subject=None, author=None):
    """The commit replayed with a new sha: the same message and author unless reworded or re-authored."""
    return commit(subject or c["subject"], author or c["who"][:2])
