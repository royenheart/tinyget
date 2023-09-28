class Buffer(object):
    def __init__(self):
        """
        Initializes a new instance of the class. This function does not take any parameters.
        """
        self.data = ""

    def __len__(self) -> int:
        """
        Returns the length of the object.

        :return: An integer representing the length of the object.
        :rtype: int
        """
        return len(self.data)

    def __nonzero__(self) -> bool:
        """
        A function comment for the __nonzero__ method.

        :return: A boolean value indicating whether the length of the object is greater than zero.
        :rtype: bool
        """
        return len(self) > 0

    def __contains__(self, x: str) -> bool:
        """
        Check if the given value is contained within the data.

        Parameters:
            x (str): The value to check for containment.

        Returns:
            bool: True if the value is contained within the data, False otherwise.
        """
        return x in self.data

    def add(self, other):
        """
        Adds the given input to the current buffer.

        Parameters:
            other (Buffer or str): The input to be added to the buffer.

        Raises:
            TypeError: If the input is neither a Buffer nor a str.

        Returns:
            None
        """
        if isinstance(other, Buffer):
            self.data += other.data
        elif isinstance(other, str):
            self.data += other
        else:
            raise TypeError

    def get(self, want: int = -1) -> str:
        """
        Retrieves a substring from the data stored in the object.

        Args:
            want (int): The length of the substring to be retrieved. Defaults to -1,
                which retrieves the entire data stored in the object.

        Returns:
            str: The retrieved substring from the data stored in the object.
        """
        if want < 0:
            to_ret = self.data
            self.data = ""
            return to_ret
        else:
            to_ret = self.data[:want]
            self.data = self.data[want:]
            return to_ret

    def peek(self, want: int = -1) -> str:
        """
        Return the top element(s) of the stack without removing them.

        Parameters:
            want (int): The number of elements to return from the top of the stack. Defaults to -1 which returns the entire stack.

        Returns:
            str: The top element(s) of the stack as a string.

        """
        if want < 0:
            to_ret = self.data
            return to_ret
        else:
            to_ret = self.data[:want]
            return to_ret
