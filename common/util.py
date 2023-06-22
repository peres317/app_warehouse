import re
from termcolor import colored
from os import system
system('color')


class Util:
    @staticmethod
    def get_tag_containing(substring, string_iterator) -> str:
        """Finds first string in string_iterator that match regex ".*substring"

        Args:
            substring (str): Substring to find.
            string_iterator (list[str]): String iterator.

        Returns:
            str: String from string iterator that matches. None if not found.
        """
        for s in string_iterator:
            search = re.search(r'.*' + substring, s)
            if search:
                return search.string
        return None
    
    @staticmethod
    def read_list(filename: str) -> list[str]:
        """Read strings from file one by line.

        Args:
            filename (str): File path.

        Returns:
            list[str]: List of strings readed.
        """
        list = []
        with open(filename, 'r', encoding="utf8") as f:
            for item in f:
                list.append(item[:-1]) # Remove \n
        return list
    
    @staticmethod
    def write_list(filename: str, list: list[str]) -> None:
        """Write strings to file one by line.

        Args:
            filename (str): File path.
            list (list[str]): List of strings.
        """
        with open(filename, 'w', encoding="utf8") as f:
            f.write('\n'.join(list) + '\n')
    
    @staticmethod
    def log_normal(msg: str) -> None:
        """Logs a normal priority message.

        Args:
            msg (str): Message.
        """
        print("[i] " + msg)
    
    @staticmethod        
    def log_error(error: str, msg: str) -> None:
        """Logs a error priority message.

        Args:
            error (str): Error name.
            msg (str): Error description.
        """
        print(colored("[!] Error: " + error, "red") + " " + msg)
    
    @staticmethod    
    def log_warning(warning: str, msg: str) -> None:
        """Logs a warning priority message.

        Args:
            warning (str): Warning name.
            msg (str): Warning description.
        """
        print(colored("[i] Warning: " + warning, "yellow") + " " + msg)
    
    @staticmethod    
    def log_result(msg: str) -> None:
        """Logs a result priority message.

        Args:
            msg (str): Message.
        """
        print(colored("[+] " + msg, "green"))