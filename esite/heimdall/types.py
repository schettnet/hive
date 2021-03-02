import graphene


class GenerationTypes:
    class State(graphene.Enum):
        PENDING = "PENDING"
        STARTED = "STARTED"
        RETRY = "RETRY"
        FAILURE = "FAILURE"
        SUCCESS = "SUCCESS"
