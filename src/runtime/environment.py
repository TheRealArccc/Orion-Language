class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.scopes = [{}]

    def enter_scope(self):
        self.scopes.append({})
    
    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(self, identifier, value):
        current_scope = self.scopes[-1]
        if str(identifier) in current_scope:
            raise Exception(f"'{identifier}' already exists")
        current_scope[str(identifier)] = value

    def assign(self, identifier, value):
        for scope in reversed(self.scopes):
            if identifier in scope:
                scope[identifier] = value
                return
            
        if self.parent:
            self.parent.assign(identifier, value)
            return

        raise Exception(f"'{identifier}' is not declared")
    
    def get(self, identifier):
        for scope in reversed(self.scopes):
            if identifier in scope:
                value = scope.get(identifier)
                return value
            
        if self.parent:
            return self.parent.get(identifier)
        raise Exception(f"'{identifier}' does not exist")
    
    def debug(self):
        print("SCOPE: ", self.scopes)
        if self.parent:
            print("Parent →")
            self.parent.debug()