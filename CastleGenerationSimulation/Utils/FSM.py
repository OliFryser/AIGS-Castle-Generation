from enum import Enum

class State(Enum):
    STOP = 0
    MOVETO = 1
    UNDER = 2
    PLANPATH = 3
    WAIT = 4

class FSM:
    def __init__(self, defaultState, defaultExit = None) -> None:
        self.defaultState = defaultState
        if defaultExit is None:
            self.defaultExit = self.onExitPrint
        else:
            self.defaultExit = defaultExit
        self.currentState = defaultState
        self.onExit = self.defaultExit
        self.transitions = {}

    def addTransition(self, state0, state1, transition, onEnter = None, onExit = None):
        if state0 in self.transitions.keys():
            self.transitions[state0].update({transition: (state1, onEnter, onExit)})
        else:
            self.transitions[state0] = {transition: (state1, onEnter, onExit)}
    """
    def setState(self, state, onExit):
        if state not in self.transitions:
            print("forced into non-existant state")
        self.currentState = state
        self.onExit = onExit
    """    

    def resetState(self):
        self.currentState = self.defaultState
        self.onExit = self.defaultExit

    def updateState(self):
        if self.currentState not in self.transitions: 
            print("current state does not exist in state machine")
            return
    
        for transition, stateTuple in self.transitions[self.currentState].items():
            if not transition():
                return
            if self.onExit is not None:
                self.onExit()
            state, onEnter, onExit = stateTuple
            self.currentState = state
            if onEnter is not None:
                onEnter()
            self.onExit = onExit

    def getState(self):
        if self.currentState is not None:    
            if isinstance(self.currentState, State):
                return self.currentState
            return self.currentState.getState()

    #These two on exit and on enter conditions are mostly meant for debugging
    def onExitPrint(self, result = ""):
        for n in range(result.count("\n")):
            result = result + "  "
        if self.currentState is not None:
            if isinstance(self.currentState, State):
                result = result + f"exiting {self.currentState}"
                print(result)
            else:
                result = result + f"exiting sub fsm: {self.currentState}, \n"
                self.currentState.onEnterPrint(result)

    def onEnterPrint(self, result = ""):
        for n in range(result.count("\n")):
            result = result + "  "
        if self.currentState is not None:
            if isinstance(self.currentState, State):
                result = result + f"entering {self.currentState}"
                print(result)
            else:
                result = result + f"entering sub fsm: {self.currentState}, \n"
                self.currentState.onEnterPrint(result)