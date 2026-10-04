from math import ceil
from typing import Annotated, Any, Generic, TypeVar

from fastapi import Depends, Query
from pydantic import BaseModel, Field

from backend.core.conf import settings

SchemaT = TypeVar('SchemaT')


class PageParams(BaseModel):
    """Page and size, validated once instead of clamped in every service."""

    page: int = Field(1, ge=1, description='Page number, 1-based')
    size: int = Field(settings.PAGINATION_DEFAULT_SIZE, ge=1, description='Items per page')

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PageData(BaseModel, Generic[SchemaT]):
    """One page of results, the shape every list endpoint returns as its ``data``."""

    items: list[SchemaT] = Field([], description='Items on this page')
    total: int = Field(0, description='Total number of matching items')
    page: int = Field(1, description='Page number')
    size: int = Field(settings.PAGINATION_DEFAULT_SIZE, description='Items per page')
    total_pages: int = Field(0, description='Total number of pages')


async def pagination_params(
    page: Annotated[int, Query(ge=1, description='Page number, 1-based')] = 1,
    size: Annotated[
        int,
        Query(ge=1, le=settings.PAGINATION_MAX_SIZE, description='Items per page'),
    ] = settings.PAGINATION_DEFAULT_SIZE,
) -> PageParams:
    """Pagination query parameters, as a route dependency."""
    return PageParams(page=page, size=size)


# Declare on a route to receive validated pagination parameters.
DependsPagination = Annotated[PageParams, Depends(pagination_params)]


def paginate(query: Any, params: PageParams) -> PageData[Any]:
    """Execute a PostgREST query as one page of results.

    ``query`` must be a builder selected with ``count='exact'``; the range is applied
    here so callers never compute offsets themselves.

    :param query: a PostgREST query builder, ready except for its range
    :param params: the requested page and size
    """
    result = query.range(params.offset, params.offset + params.size - 1).execute()
    total = result.count or 0
    return PageData[Any](
        items=result.data or [],
        total=total,
        page=params.page,
        size=params.size,
        total_pages=ceil(total / params.size) if params.size else 0,
    )


def page_of(items: list[Any], params: PageParams, total: int | None = None) -> PageData[Any]:
    """Wrap an already-fetched list in the page envelope.

    For the few endpoints whose rows do not come from a single PostgREST query.
    """
    count = len(items) if total is None else total
    return PageData[Any](
        items=items,
        total=count,
        page=params.page,
        size=params.size,
        total_pages=ceil(count / params.size) if params.size else 0,
    )
