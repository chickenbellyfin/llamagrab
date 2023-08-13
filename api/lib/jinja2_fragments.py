from typing import Any, Dict, Optional
from jinja2 import Environment

from sanic import Request, Sanic, SanicException
from sanic_ext.extensions.templating import render as sanic_render
from sanic_ext.exceptions import ExtensionNotFound

import jinja2_fragments


async def render(
    template_name: str = "",
    status: int = 200,
    headers: Optional[Dict[str, str]] = None,
    content_type: str = "text/html; charset=utf-8",
    app: Optional[Sanic] = None,
    environment: Optional[Environment] = None,
    context: Optional[Dict[str, Any]] = None,
    *,
    # template_source: str = "", # TODO: add support for template_source in jinja2_fragments
    block: Optional[str] = None
) -> sanic_render.TemplateResponse:
    if block is None or block == "":
        return await sanic_render.render(
          template_name=template_name,
          status=status,
          headers=headers,
          content_type=content_type,
          app=app,
          environment=environment,
          context=context
        )
    if app is None:
        try:
            app = Sanic.get_app()
        except SanicException as e:
            raise SanicException(
                "Cannot render template beause locating the Sanic application "
                "was ambiguous. Please return  render(..., app=some_app)."
            ) from e

    if environment is None:
        try:
            environment = app.ext.environment
        except AttributeError:
            raise ExtensionNotFound(
                "The Templating extension does not appear to be enabled. "
                "Perhaps jinja2 is not installed."
            )

    kwargs = context if context else {}

    kwargs["request"] = Request.get_current()

    if template_name:
        
        if app.config.TEMPLATING_ENABLE_ASYNC:
          content = await jinja2_fragments.render_block_async(
            environment = environment,
            template_name = template_name,
            block_name = block,
            **kwargs
          )
        else:
          content = jinja2_fragments.render_block(
            environment = environment,
            template_name = template_name,
            block_name = block,
            **kwargs 
          )

        return sanic_render.TemplateResponse(  # type: ignore
            content, status=status, headers=headers, content_type=content_type
        )
    else:
        return sanic_render.LazyResponse(
            kwargs, status=status, headers=headers, content_type=content_type
        )