from dataclasses import dataclass
import pickle
import glob
from datetime import datetime

from crypt_tools import VigenereKeySplitCifer
from utils import generate_password, Message, MessagesList, MsgType, hashf, SYM_forw

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
    'folder <folder_name> drop <index>   # delete the entry with a given index from the folder; the folder must be unlocked; the entries are enumerated starting at 0',
    'folder <folder_name> export   # write all entries of a folder into a file',
    'folder <folder_name> info    # print log history of a folder; the folder must me unlocked',
    'list    # list all folders in this storage',
    'listv    # list all folders with their contents',
    'lock <key>    # try to apply lock command to all folders',
    'lock     # try to apply lock commands to all folders using the last key used with the "unlock <key>" command',
    'unlock <key>    # try to apply unlock command to all folders',
    'gen [<length>]   # generate a password string; default length is 15',
    'allowed     # show all allowed charachters for the entries'
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
    
    def display_info(self) -> MessagesList:
        return [Message(str(log_ent)) for log_ent in self.log_history]
    
    def get_name(self) -> str:
        return self.name
    
    def get_unlocked(self) -> bool:
        return self.unlocked

    def encrypt(self, key) -> None:
        self.key_hash = hashf(key)
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
    
    def add_entry(self, entry: Entry) -> MessagesList:
        if not self.get_unlocked():
            return [Message('Cannot add entry to locked folder', MsgType.ERROR)]
        self.entries.append(entry)
        self.log(f'added entry {entry.name}')
        return [Message(f'Added entry {entry.name} to folder {self.name}')]
    
    def delete_entry(self, entry_index: int) -> MessagesList:
        if 0 <= entry_index < len(self.entries):
            ent_name = self.entries[entry_index].name
            del self.entries[entry_index]
            self.log(f'deleted entry {ent_name}')
            return [Message(f'Deleted entry {ent_name} from folder {self.name}')]
        else:
            return [Message(f'ERROR: invalid index: {entry_index}; must be in [0, {len(self.entries)})', MsgType.ERROR)]
    
    def list(self) -> MessagesList:
        if self.entries:
            return [Message(str(ent)) for ent in self.entries]
        else:
            return [Message('No entries', MsgType.ERROR)]

    def __str__(self) -> str:
        unlocked_indicator = 'LOCKED ' if not self.get_unlocked() else ''
        return f'{unlocked_indicator}Folder [{self.name}] with {len(self.entries)} entries'


class App:
    def __init__(self) -> None:
        self.running = True
        self.app_files = glob.glob('./*.pass')
        self.default_key = None

        if self.app_files:
            print('Existing storages found:')
            for i, af in enumerate(self.app_files):
                print(f'{i}. {af[2:]}')
            ind = int(input('Choose one by index or type "-1" to create a new storage: '))
            if ind != -1:
                self.DBFILE = self.app_files[ind][2:]
                with open(self.DBFILE, 'rb') as f:
                    try:
                        self.databases: dict[str, Folder] = pickle.load(f)
                    except Exception as e:
                        print('Error occured when reading the storage file:', e)
                        self.close()
                    else:
                        print('Loaded existing storage:', self.DBFILE)
            else:
                self.creating_new_storage()
        else:
            self.creating_new_storage()
    
    def creating_new_storage(self) -> None:
        name = input('Input a name for a new storage: ')
        self.DBFILE = f'{name}.pass'
        if '.\\' + self.DBFILE in self.app_files:
            print('A storage with this name already exists.')
            if not input('Are you sure that you want to rewrite it? (y/n) ') == 'y':
                self.close()
                return
        self.databases = dict()
        print(f'Created new storage [{name}]')

    def display(self) -> None:
        if self.databases:
            for db in self.databases.values():
                print(db)
        else:
            print('Empty list of folders')

    def encrypt_db(self, db_name, key) -> None:
        thisdb = self.databases[db_name]
        if not thisdb.get_unlocked():
            print(f'FAIL: folder [{db_name}] is already locked')
            return

        thisdb.encrypt(key)
        print(f'Folder [{db_name}] encrypted successfully')
    
    def decrypt_db(self, db_name, key) -> None:
        thisdb = self.databases[db_name]
        if thisdb.get_unlocked():
            print(f'FAIL: folder [{db_name}] is already unlocked')
            return
        if not thisdb.is_decryptable(key):
            print(f'FAIL: invalid key for folder [{db_name}]')
            thisdb.log(f'decrypting unsuccessfull')
            return

        thisdb.decrypt(key)
        print(f'Folder [{db_name}] decrypted successfully')
        
    def save(self) -> None:
        if not self.databases:
            print('Empty list of folders')
            return
        with open(self.DBFILE, 'wb') as f:
            pickle.dump(self.databases, f)
        print('Saved all folders')

    def close(self) -> None:
        self.running = False
        print('Closed successfully')
    
    def execute(self, cmd: str) -> None:
        match cmd.split():
            case ['save']:
                self.save()
            case ['close']:
                self.close()
            case ['sc']:
                self.save()
                self.close()
            case ['help']:
                for i, hlp in enumerate(HELP_STR):
                    print(f'{i+1}. {hlp}')
                print('Note: some commands have a short form: folder = f, lock = l, unlock = ul.')
            case ['listv']:
                if not self.databases:
                    print('Empty list of folders')
                    return
                print()
                for db_name, db in self.databases.items():
                    print('\t', db, ':', sep='')
                    for msg in db.list():
                        print(msg)
                    print()
            case ['list']:
                self.display()
            case ['lock' | 'l', key]:
                for foldername in self.databases:
                    self.encrypt_db(foldername, key)
            case ['lock' | 'l']:
                if self.default_key is None:
                    print('"unlock <key>" command was not used')
                    return
                for foldername in self.databases:
                    self.encrypt_db(foldername, self.default_key)
                print('Locked everything with the key used in the last "unlock <key>"')
            case ['unlock' | 'ul', key]:
                for foldername in self.databases:
                    self.decrypt_db(foldername, key)
                self.default_key = key
            case ['folder' | 'f', db_name, *rest]:
                if db_name in self.databases:
                    match rest:
                        case ['add' | '+', *entry_data]:
                            if len(entry_data) >= 3:
                                for msg in self.databases[db_name].add_entry(Entry(*entry_data[:3], ' '.join(entry_data[3:]))):
                                    print(msg)
                            else:
                                print('Not enough arguments for an entry')
                        case ['list' | 'l']:
                            print('\t', self.databases[db_name], ':', sep='')
                            for msg in self.databases[db_name].list():
                                print(msg)
                        case ['drop']:
                            if self.databases[db_name].get_unlocked():
                                if input('Are you sure (y/n)? ') == 'y':
                                    del self.databases[db_name]
                                    print(f'Deleted folder [{db_name}]')
                            else:
                                print('Cannot delete a locked folder')
                        case ['drop', entry_index]:
                            try:
                                entry_index_int = int(entry_index)
                            except ValueError:
                                print(f'ERROR: {entry_index} is not an integer')
                                return
                            if self.databases[db_name].get_unlocked():
                                for msg in self.databases[db_name].delete_entry(entry_index_int):
                                    print(msg)
                            else:
                                print('Cannot delete an entry from a locked folder')
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
                            print(self.databases[db_name].key_hash)
                            if self.databases[db_name].get_unlocked():
                                for msg in self.databases[db_name].display_info():
                                    print(msg)
                            else:
                                print('Cannot display info about a locked folder')
                        case _:
                            print('Folder already exists')
                else:
                    if len(rest):
                        print('No such folder')
                        return
                    self.databases[db_name] = Folder(db_name)
                    print('Created new folder')
            case ['gen']:
                print('Generated password:', generate_password(15))
            case ['gen', pass_len]:
                try:
                    pass_len_int = int(pass_len)
                except:
                    print(f'{pass_len} is not a number')
                else:
                    if pass_len_int <= 0:
                        print('Password length must be positive')
                        return
                    if pass_len_int <= 4:
                        additional_str = ' (a very short one)'
                    elif 4 < pass_len_int < 16:
                        additional_str = ''
                    else:
                        additional_str = ' (a huge one)'

                    print('Generated password:', generate_password(pass_len_int), additional_str)
            case ['allowed']:
                print(''.join(SYM_forw))
            case _:
                print('Unknown command. Try <help>')

    def run(self) -> None:
        while self.running:
            cmd = input('>>> ')
            self.execute(cmd)
