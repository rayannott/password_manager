from dataclasses import dataclass
import pickle
import glob
from datetime import datetime

from rich.console import Console

from src.crypt_tools import VigenereKeySplitCifer
from src.utils import generate_password, hashf, check_reliable, SYM_forw
import src.rich_utils as ru

cifer = VigenereKeySplitCifer(iterations=100)

HELP_STR = [
    'save    # save all folders to a local storage',
    'close    # close the program',
    'help    # print this message',
    'folder <folder_name>    # create a folder',
    'folder <folder_name> list    # list all entries in the folder',
    'folder <folder_name> add <ent_name> <login> <password> [<notes>*]    # add a new entry to the folder; the folder must be unlocked',
    'folder <folder_name> lock <key>    # encrypt a folder with a key; the folder must be unlocked',
    'folder <folder_name> unlock <key>    # decrypt a folder with a key; executes successfully only if the key is correct; the folder must be locked',
    'folder <folder_name> drop    # delete the folder; a folder must be unlocked',
    'folder <folder_name> drop <index>    # delete the entry with a given index from the folder; the folder must be unlocked; the entries are enumerated starting at 0',
    'folder <folder_name> export    # write all entries of a folder into a file',
    'folder <folder_name> info    # print log history of a folder; the folder must me unlocked',
    'list    # list all folders in this storage',
    'listv    # list all folders with their contents',
    'lock <key>    # try to apply lock command to all folders',
    'lock     # try to apply lock commands to all folders using the last key used with the "unlock <key>" command',
    'unlock <key>    # try to apply unlock command to all folders',
    'gen [<length>]    # generate a password string; default length is 15',
    'allowed     # show all allowed charachters for the entries'
]
HELP_LIST = [
    el.split('    # ') for el in HELP_STR
]


@dataclass
class Entry:
    name: str
    login: str
    password: str
    note: str = ''
    def __str__(self) -> str:
        note = ' | ' + self.note if self.note else ''
        return f'{self.name} | {self.login} | {self.password}{note}'


class LogEntry:
    def __init__(self, action: str) -> None:
        self.date = datetime.now()
        self.action = action
    
    def __str__(self):
        return f'{self.date} - {self.action}'
    
    def to_rich(self):
        return f'[blue]{self.date}[/]: [cyan]{self.action}[/]'


class Folder:
    # core database class - holds a list of Entries and performs logical operations on them
    def __init__(self, name) -> None:
        self.name = name
        self.entries: list[Entry] = []
        self.key_hash: int | None = None # storing hash of a key
        self.unlocked = True
        self.log_history: list[LogEntry] = []
        self.log('created')
    
    def log(self, action: str) -> None:
        self.log_history.append(LogEntry(action))
    
    def get_info(self) -> list[str]:
        return [log_ent.to_rich() for log_ent in self.log_history]
    
    def get_name(self) -> str:
        return self.name
    
    def get_unlocked(self) -> bool:
        return self.unlocked

    def encrypt(self, key) -> None:
        self.key_hash = hashf(key) # type: ignore
        self.unlocked = False
        for e in self.entries:
            e.password = cifer.encrypt(e.password, key)
            e.note = cifer.encrypt(e.note, key)
            e.login = cifer.encrypt(e.login, key)
        self.log('encrypted')

    def decrypt(self, key: str) -> None:
        self.key_hash = None
        self.unlocked = True
        for e in self.entries:
            e.password = cifer.decrypt(e.password, key)
            e.note = cifer.decrypt(e.note, key)
            e.login = cifer.decrypt(e.login, key)
        self.log('decrypted')
    
    def is_decryptable(self, key: str) -> bool:
        return hashf(key) == self.key_hash
    
    def add_entry(self, entry: Entry) -> str:
        if not self.get_unlocked():
            return '[red]Cannot add entry to locked folder'
        self.entries.append(entry)
        self.log(f'added entry {entry.name}')
        return f'[green]Added entry [white]{entry.name}[/] to folder [cyan]{self.name}'
    
    def delete_entry(self, entry_index: int) -> str:
        if 0 <= entry_index < len(self.entries):
            ent_name = self.entries[entry_index].name
            del self.entries[entry_index]
            self.log(f'deleted entry {ent_name}')
            return f'[green]Deleted entry [white]{ent_name}[/] from folder [cyan]{self.name}'
        else:
            return f'[red]Invalid index: {entry_index}; must be in 0..{len(self.entries)-1}'

    def __str__(self) -> str:
        unlocked_indicator = 'LOCKED ' if not self.get_unlocked() else ''
        return f'{unlocked_indicator}Folder [{self.name}] with {len(self.entries)} entries'
    
    def to_rich(self) -> str:
        unlocked_indicator = '[yellow]LOCKED[/]' if not self.get_unlocked() else '[green]OPEN[/]'
        return f'{unlocked_indicator} folder [cyan]{self.name}[/] with {len(self.entries)} entr{"y" if len(self.entries) == 1 else "ies"}'


class App:
    def __init__(self) -> None:
        self.running = True
        self.app_files = glob.glob('./*.pass')
        self.default_key = None
        self.cns = Console()
        
        self.cns.print('[magenta underline]CL Password Manager[/] [green]v0.4[/] (from [cyan]10.03.23[/])')
        print()
        if self.app_files:
            cols = ['[blue]ID', '[magenta]STORAGE']
            rows = []
            for i, af in enumerate(self.app_files):
                rows.append([str(i), af[2:]])
            self.cns.print(ru.get_rich_table(cols, rows, 'Existing Storages'))
            ind = int(ru.input(self.cns, prompt_text='Choose a [magenta]storage[/] by [blue]ID[/] or type "-1" to create a new storage: '))
            if ind != -1:
                self.DBFILE = self.app_files[ind][2:]
                self.loading_existing_storage(self.DBFILE)
            else:
                self.creating_new_storage()
        else:
            self.creating_new_storage()

    def loading_existing_storage(self, storage_name: str):
        with open(storage_name, 'rb') as f:
            try:
                self.databases: dict[str, Folder] = pickle.load(f)
            except Exception as e:
                self.cns.print(f'[red]Error occured when reading the storage file: [red]{e}[/]')
                self.close()
            else:
                self.cns.print(ru.get_rich_panel(f'STORAGE [magenta]{storage_name[:-5]}'))
    
    def creating_new_storage(self) -> None:
        name = ru.input(self.cns, 'Input a name for a new storage: ')
        self.DBFILE = f'{name}.pass'
        if '.\\' + self.DBFILE in self.app_files:
            self.cns.print('[yellow]A storage with this name already exists')
            if not ru.input(self.cns, '[yellow]Are you sure that you want to rewrite it? ([green]y[/]/[red]n[/]) ') == 'y':
                self.close()
                return
        self.databases = dict()
        self.cns.print(f'[green]Created new storage [magenta]{name}')
        self.cns.print(ru.get_rich_panel(f'STORAGE [magenta]{name}'))

    def encrypt_db(self, db_name, key) -> None:
        thisdb = self.databases[db_name]
        if not thisdb.get_unlocked():
            self.cns.print(f'[red]Folder [cyan]{db_name}[/] is already locked')
            return

        thisdb.encrypt(key)
        self.cns.print(f'[green]Folder [cyan]{db_name}[/] encrypted successfully')
    
    def decrypt_db(self, db_name, key) -> None:
        thisdb = self.databases[db_name]
        if thisdb.get_unlocked():
            self.cns.print(f'[red]Folder [cyan]{db_name}[/] is already unlocked')
            return
        if not thisdb.is_decryptable(key):
            self.cns.print(f'[red]Invalid key for folder [cyan]{db_name}')
            thisdb.log(f'decrypting unsuccessfull')
            return

        thisdb.decrypt(key)
        self.cns.print(f'[green]Folder [cyan]{db_name}[/] decrypted successfully')
        
    def save(self) -> None:
        if not self.databases:
            self.cns.print('[red]Empty list of folders')
            return
        with open(self.DBFILE, 'wb') as f:
            pickle.dump(self.databases, f)
        self.cns.print('[green]Saved all folders')

    def close(self) -> None:
        self.running = False
        self.cns.print('[green]Closed successfully')

    def display_db_as_table(self, db: Folder):
        rich_folder_table = ru.get_rich_db_table(
            [[ent.name, ent.login, ent.password, ent.note] for ent in db.entries], 
            db.to_rich()
        )
        self.cns.print(rich_folder_table)
    
    def execute(self, cmd: str) -> None:
        if not cmd:
            return
        match cmd.split(): # TODO: make this better
            case ['save']:
                self.save()
            case ['close']:
                self.close()
            case ['sc']:
                self.save()
                self.close()
            case ['help']:
                help_rich_table = ru.get_rich_table(
                    ['COMMAND PATTERN', 'DESCRIPTION'],
                    HELP_LIST,
                    ''
                )
                self.cns.print(help_rich_table)
                self.cns.print('[yellow]Note[/]: some commands have a short form: folder = f, lock = l, unlock = ul.')
            case ['listv']:
                if not self.databases:
                    self.cns.print('[red]Empty list of folders')
                    return
                for db_name, db in self.databases.items():
                    self.display_db_as_table(db)
            case ['list']:
                if self.databases:
                    table = ru.get_rich_dbs_short_table(self.databases.values())
                    self.cns.print(table)
                else:
                    self.cns.print('[red]Empty list of folders')
            case ['lock' | 'l', key]:
                for foldername in self.databases:
                    self.encrypt_db(foldername, key)
            case ['lock' | 'l']:
                if self.default_key is None:
                    self.cns.print('[red]"unlock <key>" command was not used')
                    return
                for foldername in self.databases:
                    self.encrypt_db(foldername, self.default_key)
                self.cns.print('[green]Locked everything with the key used in the last "unlock <key>"')
            case ['unlock' | 'ul', key]:
                for foldername in self.databases:
                    self.decrypt_db(foldername, key)
                self.default_key = key
            case ['folder' | 'f', db_name, *rest]:
                if db_name in self.databases:
                    match rest:
                        case ['add' | '+', *entry_data]:
                            if len(entry_data) >= 3:
                                feedback = self.databases[db_name].add_entry(Entry(*entry_data[:3], ' '.join(entry_data[3:]))) # type: ignore
                                self.cns.print(feedback)
                            else:
                                self.cns.print('[red]Not enough arguments for an entry')
                        case ['list' | 'l']:
                            self.display_db_as_table(self.databases[db_name])
                        case ['drop']:
                            if self.databases[db_name].get_unlocked():
                                if ru.input(self.cns, '[yellow]Are you sure ([green]y[/]/[red]n[/])? ') == 'y':
                                    del self.databases[db_name]
                                    self.cns.print(f'[green]Deleted folder [cyan]{db_name}')
                            else:
                                self.cns.print('[red]Cannot delete a locked folder')
                        case ['drop', entry_index]:
                            try:
                                entry_index_int = int(entry_index)
                            except ValueError:
                                self.cns.print(f'[red]{entry_index} is not an integer')
                                return
                            if self.databases[db_name].get_unlocked():
                                feedback = self.databases[db_name].delete_entry(entry_index_int)
                                self.cns.print(feedback)
                            else:
                                self.cns.print('[red]Cannot delete an entry from a locked folder')
                        case ['lock' | 'l' | '<<', pin]:
                            self.encrypt_db(db_name, pin)
                        case ['unlock' | 'ul' | '>>', pin]:
                            self.decrypt_db(db_name, pin)
                        case ['export']:
                            filename = f'{db_name}.txt'
                            with open(filename, 'w') as fexport:
                                for ent in self.databases[db_name].entries:
                                    print(ent, file=fexport)
                        case ['info']:
                            if self.databases[db_name].get_unlocked():
                                for msg in self.databases[db_name].get_info():
                                    self.cns.print(msg)
                            else:
                                self.cns.print('[red]Cannot display info about a locked folder')
                        case _:
                            self.cns.print('[red]Folder already exists')
                else:
                    if len(rest):
                        self.cns.print('[red]No such folder')
                        return
                    self.databases[db_name] = Folder(db_name)
                    self.cns.print('[green]Created new folder')
            case ['gen']:
                self.cns.print(f'Generated password: {generate_password(15)}')
            case ['gen', pass_len]:
                try:
                    pass_len_int = int(pass_len)
                except:
                    self.cns.print(f'[red]{pass_len} is not a number')
                else:
                    if pass_len_int <= 0:
                        self.cns.print('[red]Password length must be positive')
                        return
                    if pass_len_int <= 4:
                        additional_str = ' (a very short one)'
                    elif 4 < pass_len_int < 16:
                        additional_str = ''
                    else:
                        additional_str = ' (a huge one)'

                    self.cns.print(f'Generated password: {generate_password(pass_len_int)}[blue]{additional_str}')
            case ['allowed']:
                print(''.join(SYM_forw))
            case ['check', key]:
                try:
                    get_reliability_score = check_reliable(key)
                except KeyError as e:
                    self.cns.print(f'[red]{e}')
                    return
                self.cns.print(f'[white]The key [magenta]{key}[/] is {get_reliability_score:.0%} reliable')
            case _:
                self.cns.print('[red]Unknown command. Try <help>')

    def run(self) -> None:
        while self.running:
            cmd = ru.input(self.cns, '>>> ')
            self.execute(cmd)
