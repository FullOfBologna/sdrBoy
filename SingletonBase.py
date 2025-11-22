class SingletonBase:
    _instances = {}

    # Accept *args and **kwargs here for when children class have specific input arguments. Don't do anything with them
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # print(f"Creating new instance for {cls.__name__}")
            instance = super().__new__(cls)
            cls._instances[cls] = instance
        
        return cls._instances[cls]
    
    @classmethod
    def reset(cls):
        """
        Explicitly remove the instance of this specific subclass
        from the registry, allowing a new one to be created on next call.
        Useful for testing.
        """
        if cls in cls._instances:
            print(f"--- Resetting singleton instance for {cls.__name__} ---")
            del cls._instances[cls]
        else:
            print(f"--- No singleton instance for {cls.__name__} to reset ---")

    # Note: No base __init__. Subclasses MUST implement their own
    # __init__ if needed AND include a guard to prevent re-initialization.

