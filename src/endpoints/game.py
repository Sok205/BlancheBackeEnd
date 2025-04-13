from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth.db import get_db
from ..auth.models import Game
from pydantic import BaseModel, Field

router = APIRouter()

@router.get("/games/{game_id}")
def get_game(game_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a game by its ID.
    """
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"id": game.id, "game": game.game}



class GameCreate(BaseModel):
    game: dict = Field(..., description="The JSON object representing the game")  # Require a JSON object

@router.post("/games")
def create_game(game_data: GameCreate, db: Session = Depends(get_db)):
    """
    Insert a new game into the database.
    """
    if not isinstance(game_data.game, dict):
        raise HTTPException(status_code=400, detail="The 'game' field must be a valid JSON object")

    new_game = Game(game=game_data.game)
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    return {"message": "Game created successfully", "game_id": new_game.id}