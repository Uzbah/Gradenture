from typing import Any, Generic, TypeVar, overload

from pydantic import BaseModel, Field

from backend.common.response.response_code import CustomResponse, CustomResponseCode

SchemaT = TypeVar('SchemaT')


class ResponseModel(BaseModel):
    """Unified response envelope without a typed data schema.

    Example::

        @router.get('/ping')
        async def ping() -> ResponseModel:
            return response_base.success(data={'pong': True})
    """

    code: int = Field(CustomResponseCode.HTTP_200.code, description='Response code')
    msg: str = Field(CustomResponseCode.HTTP_200.msg, description='Response message')
    data: Any | None = Field(None, description='Response data')


class ResponseSchemaModel(ResponseModel, Generic[SchemaT]):
    """Unified response envelope with a typed data schema.

    Example::

        @router.get('/{pk}')
        async def get_question(pk: str) -> ResponseSchemaModel[GetQuestionDetail]:
            return response_base.success(data=await question_service.get(pk=pk))
    """

    data: SchemaT


class ResponseBase:
    """Builders for the unified response envelope."""

    @staticmethod
    def __response(
        *,
        res: CustomResponseCode | CustomResponse,
        data: Any | None,
    ) -> ResponseModel | ResponseSchemaModel[Any]:
        if data is None:
            return ResponseModel(code=res.code, msg=res.msg, data=data)
        return ResponseSchemaModel[Any](code=res.code, msg=res.msg, data=data)

    @overload
    def success(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: None = None,
    ) -> ResponseModel: ...

    @overload
    def success(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: SchemaT,
    ) -> ResponseSchemaModel[SchemaT]: ...

    def success(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: Any | None = None,
    ) -> ResponseModel | ResponseSchemaModel[Any]:
        """Successful response.

        :param res: code and message to report
        :param data: response payload
        """
        return self.__response(res=res, data=data)

    @overload
    def fail(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_400,
        data: None = None,
    ) -> ResponseModel: ...

    @overload
    def fail(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_400,
        data: SchemaT,
    ) -> ResponseSchemaModel[SchemaT]: ...

    def fail(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_400,
        data: Any = None,
    ) -> ResponseModel | ResponseSchemaModel[Any]:
        """Failure response that still carries an HTTP 200.

        Prefer raising one of the errors in ``backend.common.exception.errors``; this
        is for the handful of cases where the request was understood but the write
        affected no rows.

        :param res: code and message to report
        :param data: response payload
        """
        return self.__response(res=res, data=data)


response_base: ResponseBase = ResponseBase()
