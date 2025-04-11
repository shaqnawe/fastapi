from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.oauth import get_current_user
from app.database import SessionDep
from sqlmodel import select, func
from app.models import Post, User, Vote
from app.schemas import PostCreate, PostResponse, PostVote
from datetime import datetime, timezone


router = APIRouter(prefix="/posts", tags=["Posts"])


# @router.get("/", response_model=list[PostResponse])
@router.get("/", response_model=list[PostVote])
def get_posts(
    db: SessionDep,
    current_user: User = Depends(get_current_user),
    limit: int = 5,
    skip: int = 0,
    search: Optional[str] = "",
):
    # with conn.cursor() as cursor:
    #     cursor.execute("SELECT * FROM posts")
    #     posts = cursor.fetchall()
    #     return {"data": posts}
    print(f"LIMIT: {limit}")
    # posts = db.exec(
    #     select(Post).filter(Post.title.contains(search)).offset(skip).limit(limit)
    # ).all()
    posts = db.exec(
        select(Post, func.count(Vote.post_id).label("votes"))
        .outerjoin(Vote)
        .group_by(Post.id)
        .filter(Post.title.contains(search))
        .offset(skip)
        .limit(limit)
    ).all()
    # print(posts)
    # Get posts owned by specifc user
    # posts = db.exec(select(Post).where(Post.user_id == current_user.id)).all()
    return [PostVote(post=post, votes=votes) for post, votes in posts]


@router.get("/{id}", response_model=PostVote)
def get_post(id: int, db: SessionDep, current_user: User = Depends(get_current_user)):
    # with conn.cursor() as cursor:
    #     cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
    #     post = cursor.fetchone()
    # post = db.get(Post, id)
    post = db.exec(
        select(Post, func.count(Vote.post_id).label("votes"))
        .outerjoin(Vote)
        .group_by(Post.id)
        .filter(Post.id == id)
    ).first()
    # Get specific post only if the user created it
    # post = db.exec(
    #     select(Post).where(Post.id == id, Post.user_id == current_user.id)
    # ).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found or not authorized.",
        )
    post, votes = post
    return PostVote(post=post, votes=votes)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(
    post: PostCreate,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    # with conn.cursor() as cursor:
    #     cursor.execute(
    #         "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING*",
    #         (post.title, post.content, post.published),
    #     )
    #     new_post = cursor.fetchone()
    print("🟢 create_post route hit")
    # print("👤 Current user:", current_user.email)
    print("👤 Current user:", current_user.id)
    new_post = Post(user_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int, db: SessionDep, current_user: User = Depends(get_current_user)
):
    # with conn.cursor() as cursor:
    #     cursor.execute("DELETE FROM posts WHERE id = %s RETURNING*", (id,))
    #     deleted_post = cursor.fetchone()
    #     conn.commit()
    print(current_user.id)
    post = db.get(Post, id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist.",
        )
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform the requested action.",
        )
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=PostResponse)
def update_post(
    id: int,
    post: Post,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    # with conn.cursor() as cursor:
    #     cursor.execute(
    #         "UPDATE posts SET title = %s, content = %s WHERE id = %s RETURNING *",
    #         (post.title, post.content, id),
    #     )
    #     updated_post = cursor.fetchone()
    #     conn.commit()
    print(current_user.id)
    old_post = db.get(Post, id)
    if old_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist.",
        )
    if old_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform the requested action.",
        )
    post_data = post.model_dump(exclude_unset=True)
    for key, value in post_data.items():
        setattr(old_post, key, value)

    old_post.updated_at = datetime.now(timezone.utc)
    db.add(old_post)
    db.commit()
    db.refresh(old_post)

    return old_post
