from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown

from mkdocs_obsidian.common.config import Configuration


def git_pull(configuration: Configuration, git=True):
    """
    Command to pull the repository
        If true, pull the repo
    """
    console = Console()
    if git:
        try:
            import git

            BASEDIR = configuration.output
            try:
                repo = git.Repo(BASEDIR)
                update = repo.remotes.origin
                update.pull()
                return True
            except git.GitCommandError as exc:
                console.print(f"Unexpected error : {exc}", style="bold white on red")
                return False
        except ImportError:
            return False


def git_push(
    commit: str,
    configuration: Configuration,
    obsidian=False,
    add_info="",
    rmv_info="",
    add_msg="",
    remove_msg="",
):
    """
    git push the modified files and print a message result
    """
    console = Console()
    try:
        import git

        BASEDIR = configuration.output
        try:
            repo = git.Repo(Path(BASEDIR, ".git"))
            repo.git.add(".")
            repo.git.commit("-m", f"{commit}")
            origin = repo.remote("origin")
            origin.push()
            if not obsidian:
                console.print(
                    f"[[i not bold sky_blue2]{datetime.now().strftime('%H:%M:%S')}][/]"
                    f" {add_info}",
                    Markdown(add_msg),
                    rmv_info,
                    Markdown(remove_msg),
                    Markdown("---"),
                    "🎉 Successful 🎉",
                    end=" ",
                )
            else:
                if add_msg != "":
                    add_msg = ": " + add_msg
                if remove_msg != "":
                    remove_msg = ": " + remove_msg
                print(
                    f"🎉 Successful 🎉",
                    f"[{datetime.now().strftime('%H:%M:%S')}]\n",
                    f"{add_info}{add_msg}",
                    f"{rmv_info}{remove_msg}",
                )
        except git.GitCommandError:
            if not obsidian:
                console.print(
                    f"❌ Nothing to Push ❌",
                    "[[i not bold"
                    f" sky_blue2]{datetime.now().strftime('%H:%M:%S')}][/]\n",
                    "💡 Converted 💡",
                    f" {add_info}",
                    Markdown(add_msg),
                    rmv_info,
                    Markdown(remove_msg),
                    end=" ",
                )
            else:
                if remove_msg != "":
                    remove_msg = ": " + remove_msg
                print(
                    f"❌ Nothing to Push ❌\n",
                    f"[{datetime.now().strftime('%H:%M:%S')}]",
                    "💡 Converted 💡\n",
                    f"{add_msg}",
                    f"{rmv_info}{remove_msg}",
                )
    except ImportError:
        if not obsidian:
            console.print(
                f"[{datetime.now().strftime('%H:%M:%S')}]",
                Markdown(commit),
                "changed\nPlease, use another way to push your change 😶",
                end=" ",
            )
        else:
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] {commit} changed\n Please use"
                " another way to push your change 😶"
            )
