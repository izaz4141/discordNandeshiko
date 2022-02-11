from chatterbot import ChatBot
from chatterbot.response_selection import get_random_response

cbot = ChatBot( name= "Nadeshiko",
                read_only= True,
                storage_adapter='chatterbot.storage.SQLStorageAdapter',
                logic_adapters= [
                    {
                        "import_path": "chatterbot.logic.BestMatch",
                        "response_selection_method": get_random_response,
                        "default_response": "Maaf kak, Nadeshiko tidak paham...",
                        "maximum_similarity_threshold": 0.60
                    }
                  ],
                database_uri='sqlite:///database.sqlite3'
                )

