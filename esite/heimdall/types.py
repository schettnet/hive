import graphene


class GenerationStatus(graphene.ObjectType):
    class Status(graphene.Enum):
        PENDING = "PENDING"
        STARTED = "STARTED"
        RETRY = "RETRY"
        FAILURE = "FAILURE"
        SUCCESS = "SUCCESS"

    status = Status(required=True)
    url = graphene.String()
