import graphene
from celery.result import AsyncResult
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from .models import AsyncHeimdallGeneration, License
from .tasks import generate_bridge_drop_task
from .types import GenerationStatus


class RequestBridgeDrop(graphene.Mutation):
    taskId = graphene.String()

    class Arguments:
        introspection_data = graphene.JSONString(required=True)
        license_key = graphene.String(required=True)

    @login_required
    def mutate(self, info, introspection_data, license_key):
        info.context.user

        validity_check = License.validate(license_key=license_key)

        if not validity_check:
            raise GraphQLError(
                "This license is invalid. This could be due to expiration or has already been used."
            )

        async_gen = AsyncHeimdallGeneration.objects.create(
            introspection=introspection_data
        )

        task = generate_bridge_drop_task.delay(async_gen.id)

        # Deactivate licence
        license = License.objects.get(key=license_key)
        license.is_active = False
        license.save()

        return RequestBridgeDrop(taskId=task.id)


class Mutation(graphene.ObjectType):
    request_bridge_drop = RequestBridgeDrop.Field()


class Query(graphene.ObjectType):
    get_bridge_drop = graphene.Field(
        GenerationStatus, task_id=graphene.ID(required=True)
    )

    @login_required
    def resolve_get_bridge_drop(root, info, task_id):
        task = AsyncResult(task_id)
        file_url = None

        if task.ready():
            async_gen_id = task.get()
            async_gen = AsyncHeimdallGeneration.objects.get(id=async_gen_id)

            file_url = async_gen.save_bridge_drop()

        return {"status": GenerationStatus.Status.get(task.state), "url": file_url}
