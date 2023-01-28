from dataclasses import dataclass
import pickle
import glob
from datetime import datetime

from crypt_tools import VigenereKeySplitCifer
from utils import generate_password

cifer = VigenereKeySplitCifer(iterations=100)

HELP_STR = '''
    save    # save all folders to a local storage
    close    # close the program
    help    # print this message
    folder <folder_name>    # create a folder
    folder <folder_name> list    # list all entries in the folder
    folder <folder_name> add <ent_name> <login> <password> [<notes>*]    # add a new entry to the folder; the folder must be unlocked
    folder <folder_name> lock <key>    # encrypt a folder with a key; the folder must be unlocked
    folder <folder_name> unlock <key>    # decrypt a folder with a key; executes successfully only if the key is correct; the folder must be locked
    folder <folder_name> drop    # delete the folder; a folder must be unlocked
    folder <folder_name> drop <index>   # delete the entry with a given index from the folder; the folder must be unlocked
    folder <folder_name> export [<out_filename>]   # write all entries of a folder into a file
	folder <folder_name> info    # print log history of a folder; the folder must me unlocked
    list    # list all folders in this storage
    listv    # list all folders with their contents
    lock <key>    # try to apply lock command to all folders
    unlock <key>    # try to apply unlock command to all folders
    gen    # generate a password string

Note: some commands have a short form: folder = f, lock = l, unlock = ul.
'''

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
    def __init__(self, name) -> None:
        self.name = name
        self.entries: list[Entry] = []
        self.name_for_check = name
        self.unlocked = True
        self.log_history: list[LogEntry] = []
        self.log('created')
    
    def log(self, action: str) -> None:
        self.log_history.append(LogEntry(action))
    
    def display_info(self) -> None:
        for log_ent in self.log_history:
            print(log_ent)
    
    def get_name(self) -> str:
        return self.name
    
    def get_unlocked(self) -> bool:
        self.unlocked = self.name == self.name_for_check
        return self.unlocked

    def encrypt(self, key) -> None:
        self.name_for_check = cifer.encrypt(self.name_for_check, key) # this string gets transformed along with the data
        for e in self.entries:
            e.password = cifer.encrypt(e.password, key)
            e.note = cifer.encrypt(e.note, key)
            e.login = cifer.encrypt(e.login, key)
        self.log('encrypted')

    def decrypt(self, key: str) -> None:
        self.name_for_check = cifer.decrypt(self.name_for_check, key)
        for e in self.entries:
            e.password = cifer.decrypt(e.password, key)
            e.note = cifer.decrypt(e.note, key)
            e.login = cifer.decrypt(e.login, key)
        self.log('decrypted')
    
    def is_decryptable(self, key: str) -> bool:
        return cifer.decrypt(self.name_for_check, key) == self.name 
    
    def add_entry(self, entry: Entry) -> None:
        if not self.get_unlocked():
            print('FAIL: cannot add entry to locked folder')
            return
        self.entries.append(entry)
        print(f'Added entry {entry.name} to folder {self.name}')
        self.log(f'added entry {entry.name}')
    
    def delete_entry(self, entry_index: int) -> None:
        if 0 <= entry_index < len(self.entries):
            ent_name = self.entries[entry_index].name
            del self.entries[entry_index]
            print(f'Deleted entry {ent_name} from folder {self.name}')
            self.log(f'deleted entry {ent_name}')
        else:
            print(f'ERROR: invalid index: {entry_index}; must be in [0, {len(self.entries)})')
    
    def list(self) -> None:
        if self.entries:
            for ent in self.entries:
                print(ent)
        else:
            print('no entries')

    def __str__(self) -> str:
        unlocked_indicator = 'LOCKED ' if not self.get_unlocked() else ''
        return f'{unlocked_indicator}Folder [{self.name}] with {len(self.entries)} entries'


class App:
    def __init__(self) -> None:
        self.running = True
        app_files = glob.glob('./*.pass')

        if len(app_files):
            print('Existing storages found:')
            for i, af in enumerate(app_files):
                print(f'{i}. {af[2:]}')
            ind = int(input('Choose one by index or type "-1" to create a new storage: '))
            if ind != -1:
                self.DBFILE = app_files[ind][2:]
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
        name = input('No storage found. Input a name for a new one: ')
        self.DBFILE = f'{name}.pass'
        self.databases = dict()
        print('Created new storage')

    def display(self) -> None:
        if self.databases:
            for db in self.databases.values():
                print(db)
        else:
            print('Empty list of folders')

    def encrypt_db(self, db_name, key) -> None:
        thisdb = self.databases[db_name]
        if not thisdb.unlocked:
            print(f'FAIL: folder [{db_name}] is already locked')
            return

        thisdb.encrypt(key)
        thisdb.get_unlocked()
        print(f'Folder [{db_name}] encrypted successfully')
    
    def decrypt_db(self, db_name, key) -> None:
        thisdb = self.databases[db_name]
        if thisdb.unlocked:
            print(f'FAIL: folder [{db_name}] is already unlocked')
            return
        if not thisdb.is_decryptable(key):
            print(f'FAIL: invalid key for folder [{db_name}]')
            thisdb.log(f'decrypting unsuccessfull')
            return

        thisdb.decrypt(key)
        thisdb.get_unlocked()
        print(f'Folder [{db_name}] decrypted successfully')
        
    def save(self) -> None:
        if not self.databases:
            print('Empty list of folders')
            return
        with open(self.DBFILE, 'wb') as f:
            pickle.dump(self.databases, f)

    def close(self) -> None:
        self.running = False
    
    def execute(self, cmd: str) -> None:
        match cmd.split():
            case ['save']:
                self.save()
                print('Saved all folders')
            case ['close']:
                self.close()
                print('Closed successfully')
            case ['sc']:
                self.save()
                self.close()
                print('Saved and closed successfully')
            case ['help']:
                print(HELP_STR)
            case ['listv' | 'lv', *args]:
                print()
                for db_name, db in self.databases.items():
                    print('\t', db, ':', sep='')
                    db.list()
                    print()
            case ['list' | 'l']:
                self.display()
            case ['lock', key]:
                for foldername in self.databases:
                    self.encrypt_db(foldername, key)
            case ['unlock', key]:
                for foldername in self.databases:
                    self.decrypt_db(foldername, key)
            case ['folder' | 'f', db_name, *rest]:
                if db_name in self.databases:
                    match rest:
                        case ['add' | '+', *entry_data]:
                            if len(entry_data) >= 3:
                                self.databases[db_name].add_entry(Entry(*entry_data[:3], ' '.join(entry_data[3:])))
                            else:
                                print('Not enough arguments for an entry')
                        case ['list' | 'l']:
                            print('\t', self.databases[db_name], ':', sep='')
                            self.databases[db_name].list()
                        case ['drop']:
                            if self.databases[db_name].get_unlocked():
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
                                self.databases[db_name].delete_entry(entry_index_int)
                            else:
                                print('Cannot delete an entry from a locked folder')
                        case ['lock' | '<<', pin]:
                            self.encrypt_db(db_name, pin)
                        case ['unlock' | '>>', pin]:
                            self.decrypt_db(db_name, pin)
                        case ['export', *export_filename]:
                            filename = export_filename[0] if export_filename else 'exported_folder.txt'
                            with open(filename, 'w') as fexport:
                                for ent in self.databases[db_name].entries:
                                    print(ent, file=fexport)
                        case ['info']:
                            if self.databases[db_name].get_unlocked():
                                self.databases[db_name].display_info()
                            else:
                                print('Cannot display info about a locked folder')
                        case _:
                            print('Folder already exists')
                else:
                    self.databases[db_name] = Folder(db_name)
                    print('Created new folder')
            case ['gen']:
                print('Generated password:', generate_password())
            case _:
                print('Unknown command. Try <help>')

    def run(self) -> None:
        while self.running:
            cmd = input('>>> ')
            self.execute(cmd)
