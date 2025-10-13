from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError
from src.presentation.dependencies import *
from src.domain.schemas.pydantic_schemas import *

router_name = __name__.split(".")[-1] # get the name of the file to use it in the router

router = APIRouter(
    prefix=f'/{router_name}',
    tags=[router_name],
    dependencies=[Depends(get_token)],
    responses=response_examples
)

items_db = {
    "project1": {"name": "sightjump"},
    "project2": {"name": "hefesto"}
}

@router.get("/", response_model=ResponseMessage)
async def read_items():
    """ Retrieves all items from the database  

    ## Returns:  
    **ResponseMessage**: A message indicating the success of the operation and the data retrieved.  
    """
    return ResponseMessage(detail="Items retrieved successfully", data=items_db)


@router.post("/{item_name}", response_model=ResponseMessage)
async def add_item(item_name: str):
    """ Adds an item to the database  

    ## Args:  
    **item_name (str):** Name of the item to be added. (Example: `sightjump`)

    ## Returns:  
    **ResponseMessage**: A message indicating the success of the operation and the data retrieved.

    ## Raises:  
    **HTTPException:** In case of an invalid item name, a 400 error is raised with a message indicating the allowed item name.
    """
    if item_name != "sightjump":
        raise HTTPException(status_code=400, detail="You can only add this item: sightjump")
    items_db.update({"project3": {"name": item_name}})

    try:
        return ResponseMessage(detail="Item added successfully", data=items_db)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
   
    
# @router.get("/gpt", response_model=ResponseMessage)
# async def use_gpt_dependency(llm_service: LLMService = Depends(get_llm_service)):
#     items_db.update({"using_dependency_inversion": {"name": f"{llm_service.llmmodel.name}"}})
#     return ResponseMessage(detail="GPT dependency used and llm model is added to the db successfully", data=items_db)
