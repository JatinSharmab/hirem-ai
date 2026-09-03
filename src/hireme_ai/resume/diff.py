from difflib import unified_diff


def text_diff(before: str, after: str) -> str:
    return "\n".join(
        unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile="master",
            tofile="tailored",
            lineterm="",
        )
    )
