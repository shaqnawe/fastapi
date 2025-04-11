from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from app.models import Vote, User, Post
from app.database import SessionDep
from app.oauth import get_current_user

router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post("/{post_id}", status_code=status.HTTP_201_CREATED)
def toggle_vote(
    post_id: int,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    # Check if the post exists
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )

    # Check if the vote already exists
    vote = db.exec(
        select(Vote).where(Vote.post_id == post_id, Vote.user_id == current_user.id)
    ).first()

    if vote:
        # Vote exists: remove it (unvote)
        db.delete(vote)
        db.commit()
        return {"message": "Successfully unvoted the post."}
    else:
        # Vote doesn't exist: add it (vote)
        new_vote = Vote(post_id=post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully voted for the post."}
