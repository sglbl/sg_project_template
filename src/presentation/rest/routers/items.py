from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError
from src.presentation.dependencies import *
from src.presentation.rest.schemas import *

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_token)],
    responses=response_examples
)


@router.get("/", response_model=ResponseMessage)
async def read_items():
    return ResponseMessage(detail="Items retrieved successfully", data=items_db)


@router.post("/{item_name}", response_model=ResponseMessage)
async def add_item(item_name: str):
    if item_name != "sightjump":
        raise HTTPException(status_code=400, detail="You can only add this item: sightjump")
    items_db.update({"project3": {"name": item_name}})

    try:
        return ResponseMessage(detail="Item added successfully", data=items_db)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
   
    
@router.get("/gpt", response_model=ResponseMessage)
async def use_gpt_dependency(llm_service: LLMPipeline = Depends(get_llm_service)):
    items_db.update({"using_dependency_inversion": {"name": f"{llm_service.llmmodel.name}"}})
    return ResponseMessage(detail="GPT dependency used and llm model is added to the db successfully", data=items_db)
