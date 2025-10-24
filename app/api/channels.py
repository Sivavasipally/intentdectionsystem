"""Channel management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db_session
from app.models.database import Channel, ChannelDetail
from app.models.schemas import ChannelResponse

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: str,
    db: Session = Depends(get_db_session),
) -> ChannelResponse:
    """Get channel details by ID."""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel {channel_id} not found",
        )

    # Get channel details
    details = db.query(ChannelDetail).filter(
        ChannelDetail.channel_id == channel_id
    ).all()

    detail_list = [
        {
            "key": d.key,
            "value": d.value,
            "source_doc": d.source_doc,
            "citation": d.citation,
        }
        for d in details
    ]

    return ChannelResponse(
        id=channel.id,
        name=channel.name,
        channel_type=channel.channel_type,
        department=channel.department,
        status=channel.status,
        created_at=channel.created_at,
        tenant=channel.tenant,
        details=detail_list,
    )


@router.get("/", response_model=list[ChannelResponse])
async def list_channels(
    tenant: str | None = None,
    status: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db_session),
) -> list[ChannelResponse]:
    """List channels with optional filters."""
    query = db.query(Channel)

    if tenant:
        query = query.filter(Channel.tenant == tenant)

    if status:
        query = query.filter(Channel.status == status)

    channels = query.limit(limit).all()

    results = []
    for channel in channels:
        details = db.query(ChannelDetail).filter(
            ChannelDetail.channel_id == channel.id
        ).all()

        detail_list = [
            {
                "key": d.key,
                "value": d.value,
                "source_doc": d.source_doc,
                "citation": d.citation,
            }
            for d in details
        ]

        results.append(
            ChannelResponse(
                id=channel.id,
                name=channel.name,
                channel_type=channel.channel_type,
                department=channel.department,
                status=channel.status,
                created_at=channel.created_at,
                tenant=channel.tenant,
                details=detail_list,
            )
        )

    return results
