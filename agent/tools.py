def calc(a : int ,b : int , operation : str):
    """
    Perform a bsic arithematic operation
    
    Args : 
    operation : calculation to be performed
    a : 1st no.
    b : 2nd no.
    
    returns : result of calculation
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        raise ValueError("Unsupported operation")
