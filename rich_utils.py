from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel

def input(console, prompt_text='>>> '):
    return Prompt.get_input(console, prompt_text, False)


def get_rich_db_table(rows: list[list[str]], title: str) -> Table:
    table = Table(title=title, show_lines=True)

    table.add_column("Name", justify="right", style="white bold", no_wrap=True)
    table.add_column("Login", justify="right", style="green")
    table.add_column("Password", justify="right", style="green")
    table.add_column("Notes", justify="left", style="blue")

    for row in rows:
        table.add_row(*row)
    
    return table

def get_rich_table(cols: list[str], rows: list[list[str]], title):
    table = Table(title=title)
    for col in cols:
        table.add_column(col)
    for row in rows:
        table.add_row(*row)
    return table

def get_rich_panel(text: str) -> Panel:
    return Panel(text)