from tools.registry import registry_function

class FinalAnswer:
    
    def __init__(self):
        pass

    @registry_function
    def final_answer(*args) -> str:
        '''
        Name: final_answer

        Description:

        Arguments:
            response: str

        Return:
            {
            "thought": "I received the search results. Now I must present them to the user.",
            "tool_name": "final_answer",
            "parameters": {
            "response": "Here is the data I found on hospital infections..."}
            }
        '''
        return args

if __name__ == '__main__':
    #print(FinalAnswer.final_answer.__doc__)
    pass
