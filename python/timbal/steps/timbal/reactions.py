from typing import Literal

from httpx import AsyncClient

from ...state.context import RunContext, run_context_var
from ...types.field import Field, resolve_default


async def post_reaction(
    sentiment: Literal["positive", "negative"] = Field(
        description="The sentiment of the reaction",
    ),
    feedback: str = Field(
        default=None, 
        description="Optional additional feedback",
    ),
    org_id: str = Field(
        default=None,
        description="The org_id to post the reaction for."
            "By default, it uses the org_id from the run_context.",
        private=True,
    ),
    app_id: str = Field(
        default=None,
        description="The app_id to post the reaction for."
            "By default, it uses the app_id from the run_context.",
        private=True,
    ),
    run_id: str = Field(
        default=None,
        description="The run_id to post the reaction for."
            "By default, it uses the run_id from the run_context.",
        private=True,
    ),
    run_context: RunContext = Field(
        default=None, 
        private=True,
    ), 
) -> None:

    sentiment = resolve_default("sentiment", sentiment)
    feedback = resolve_default("feedback", feedback)
    org_id = resolve_default("org_id", org_id)
    app_id = resolve_default("app_id", app_id)
    run_id = resolve_default("run_id", run_id)
    run_context = resolve_default("run_context", run_context)

    if not isinstance(run_context, RunContext):
        run_context = run_context_var.get(None)
        if run_context is None:
            raise ValueError(
                "RunContext not found. "
                "Please run this function as a timbal step or pass the run_context explicitly.")

    timbal_platform_config = run_context.timbal_platform_config
    if not timbal_platform_config:
        raise ValueError(
            "Missing Timbal Platform Config. "
            "Please specify it when running this function as a step or pass it explicitly as a function parameter.")

    org_id = org_id or timbal_platform_config.scope.org_id
    app_id = app_id or timbal_platform_config.scope.app_id
    run_id = run_id or run_context.id
    if org_id is None or app_id is None or run_id is None:
        raise ValueError(
            "Missing org_id or app_id or run_id. "
            "Please specify it when running this function as a step or pass it explicitly as a function parameter.")

    async with AsyncClient() as client:

        auth = timbal_platform_config.auth
        headers = {auth.header_key: auth.header_value}

        payload = {
            "sentiment": sentiment,
            "feedback": feedback,
        }

        res = await client.post(
            f"https://{timbal_platform_config.host}/orgs/{org_id}/apps/{app_id}/runs/{run_id}/reactions", 
            headers=headers,
            json=payload,
        )
        res.raise_for_status()
