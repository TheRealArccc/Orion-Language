class Environment:
    def __init__(self):
        self.scopes = [{}]

    def enter_scope(self):
        self.scopes.append({})
    
    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare_var(self, identifier, value):
        current_scope = self.scopes[-1]
        if identifier in current_scope:
            raise Exception(f"'{identifier}' already exists")
        current_scope[identifier] = value

    def assign_var(self, identifier, value):
        for scope in reversed(self.scopes):
            if identifier in scope:
                scope[identifier] = value
                return
        raise Exception(f"'{identifier}' is not declared")
    
    def get_var(self, identifier):
        for scope in reversed(self.scopes):
            if identifier in scope:
                value = scope.get(identifier)
                return value
        raise Exception(f"'{identifier}' does not exist")