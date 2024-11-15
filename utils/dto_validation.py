from typing import Union, Tuple, Type, Dict
import schemas

schema_mapping: Dict[str, Type[schemas.ResponseCover]] = {
    "add_points": schemas.SingleFramePointPromptInputCover,
    "run_inference": schemas.RunInferenceInputCover,
    "remove_object": schemas.RemoveObjectInputCover,
    "error": schemas.ErrorResponseCover,
    "reset": schemas.ResetTaskInputCover
}


def validate_request(request: dict) -> Tuple[schemas.ResponseCover, bool]:

    if request.get("msg_type") is None:
        return schemas.ErrorResponseCover(message="msg_type is required"), False

    validation_schema: Type[schemas.ResponseCover] = schema_mapping.get(
        request["msg_type"], schemas.ErrorResponseCover
    )
    if validation_schema is schemas.ErrorResponseCover:
        return validation_schema(message="Unknown msg_type"), False

    try:
        validated_request = validation_schema.model_validate(request)
        return validated_request, True
    except Exception as e:
        return schemas.ErrorResponseCover(message=str(e)), False

    return schemas.ErrorResponseCover(message="unknown error occured"), False
