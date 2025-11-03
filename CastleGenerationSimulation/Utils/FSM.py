from enum import Enum

class State(Enum):
    STOP = 0
    MOVETO = 1
    UNDER = 2
    PLANPATH = 3
    WAIT = 4
    ATTACK = 5
    DEMOLISH = 6

class FSM:
    def __init__(self, name, defaultState, defaultExit = None, show = False) -> None:
        self.name = name
        self.defaultState = defaultState
        if defaultExit is None:
            self.defaultExit = self.onExitPrint
        else:
            self.defaultExit = defaultExit
        self.currentState = defaultState
        self.onExit = self.defaultExit
        self.transitions = {}
        self.show = show

    def addTransition(self, state0, state1, transition, onEnter = None, onExit = None):
        if state0 in self.transitions.keys():
            self.transitions[state0].update({transition: (state1, onEnter, onExit)})
        else:
            self.transitions[state0] = {transition: (state1, onEnter, onExit)}

    def resetState(self):
        self.currentState = self.defaultState
        self.onExit = self.defaultExit

    def updateState(self):
        if self.currentState not in self.transitions: 
            print("current state does not exist in state machine")
            return
    
        for transition, stateTuple in self.transitions[self.currentState].items():
            if not transition():
                continue
            
            if self.onExit is not None:
                self.onExit()
            self.onExitPrint()
            state, onEnter, onExit = stateTuple
            self.currentState = state
            if onEnter is not None:
                onEnter()
            self.onEnterPrint()
            self.onExit = onExit
        
        
        if isinstance(self.currentState, FSM):
            self.currentState.updateState()
    

    def getState(self):
        if self.currentState is not None:
            #print(self.currentState)
            if isinstance(self.currentState, State):
                return self.currentState
            return self.currentState.getState()

    #These two on exit and on enter conditions are mostly meant for debugging
    def onExitPrint(self, result = ""):
        if not self.show:
            return
        for n in range(result.count("\n")):
            result = result + "  "
        if self.currentState is not None:
            if isinstance(self.currentState, State):
                result = result + f"exiting {self.currentState}"
                print(result)
            else:
                result = result + f"exiting sub fsm: {self.currentState.name}, \n"
                self.currentState.onExitPrint(result)

    def onEnterPrint(self, result = ""):
        if not self.show:
            return
        for n in range(result.count("\n")):
            result = result + "  "
        if self.currentState is not None:
            if isinstance(self.currentState, State):
                result = result + f"entering {self.currentState}"
                print(result)
            else:
                result = result + f"entering sub fsm: {self.currentState.name}, \n"
                self.currentState.onEnterPrint(result)

    def printState(self, result = ""):
        for n in range(result.count("\n")):
            result = result + "  "
        if self.currentState is not None:
            if isinstance(self.currentState, State):
                result = result + f"{self.currentState}"
                print(result)
            else:
                result = result + f"Sub fsm: {self.currentState.name}, \n"
                self.currentState.printState(result)