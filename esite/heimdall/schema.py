import channels_graphql_ws
import graphene
from celery.result import AsyncResult
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from .models import AsyncHeimdallGeneration, License
from .tasks import generate_bridge_drop_task
from .types import GenerationTypes


class HeimdallGeneration(graphene.Mutation):
    task_id = graphene.String()
    remaining_uses = graphene.Int()

    class Arguments:
        introspection_data = graphene.JSONString(required=True)
        license_key = graphene.String(required=True)

    @login_required
    def mutate(self, info, introspection_data, license_key):
        license = License.use(license_key=license_key)

        if not license:
            """If license is False then the license is invalid."""
            raise GraphQLError(
                "This license is invalid. This could be due to expiration or has already been used."
            )

        async_gen = AsyncHeimdallGeneration.objects.create(
            introspection=introspection_data
        )

        task = generate_bridge_drop_task.delay(async_gen.id, license_key=license_key)
        task_id = task.id
        task_state = task.state

        OnNewHeimdallGeneration.new_heimdall_generation(
            license_key=license_key, state=task_state, task_id=task_id, url=None
        )

        return HeimdallGeneration(
            task_id=task_id, remaining_uses=license.remaining_uses
        )


class Mutation(graphene.ObjectType):
    heimdall_generation = HeimdallGeneration.Field()


class OnNewHeimdallGeneration(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Subscription payload.
    state = GenerationTypes.State(required=True)
    task_id = graphene.ID(required=True)
    access_token = graphene.String()
    url = graphene.String()
    secure_url = graphene.String()

    class Arguments:
        """That is how subscription arguments are defined."""

        license_key = graphene.ID(required=True)

    @staticmethod
    def subscribe(root, info, license_key):
        """Called when user subscribes."""

        if not License.validate(license_key):
            raise GraphQLError(
                "This license is invalid. This could be due to expiration or has already been used."
            )

        # Return the list of subscription group names.
        return [license_key]

    @staticmethod
    def publish(payload, info, license_key):
        """Called to notify the client."""

        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the notification to a particular
        # client. For example, this allows to avoid notifications for
        # the actions made by this particular client.

        assert License.validate(license_key)

        state = payload["state"]
        task_id = payload["task_id"]
        access_token = payload["access_token"]
        secure_url = payload["secure_url"]
        url = payload["url"]

        task = AsyncResult(task_id)

        if task.ready():
            async_gen = AsyncHeimdallGeneration.objects.get(id=task.get())
            file = async_gen.save_bridge_drop()
            access_token = file.access_token
            secure_url = file.secure_url
            url = file.url

        return OnNewHeimdallGeneration(
            state=GenerationTypes.State.get(state),
            task_id=task_id,
            access_token=access_token,
            secure_url=secure_url,
            url=url,
        )

    @classmethod
    def new_heimdall_generation(
        cls, license_key, state, task_id, access_token=None, secure_url=None, url=None
    ):
        """Auxiliary function to send subscription notifications.
        It is generally a good idea to encapsulate broadcast invocation
        inside auxiliary class methods inside the subscription class.
        That allows to consider a structure of the `payload` as an
        implementation details.
        """

        cls.broadcast(
            group=license_key,
            payload={
                "state": state,
                "task_id": task_id,
                "access_token": access_token,
                "secure_url": secure_url,
                "url": url,
            },
        )


class Subscription(graphene.ObjectType):
    """Root GraphQL subscription."""

    on_new_heimdall_generation = OnNewHeimdallGeneration.Field()
