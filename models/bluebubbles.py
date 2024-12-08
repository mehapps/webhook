from pydantic import BaseModel
from typing import List, Optional, Dict


class Handle(BaseModel):
    originalROWID: Optional[int] = None
    address: Optional[str] = None
    service: Optional[str] = None
    uncanonicalizedId: Optional[str] = None
    country: Optional[str] = None


class Chats(BaseModel):
    originalROWID: Optional[int] = None
    guid: Optional[str] = None
    style: Optional[int] = None
    chatIdentifier: Optional[str] = None
    isArchived: Optional[bool] = None
    displayName: Optional[str] = None


class Data(BaseModel):
    originalROWID: Optional[int] = None
    guid: Optional[str] = None
    text: Optional[str] = None
    attributedBody: Optional[str] = None
    handle: Optional[Handle] = None
    handleId: Optional[int] = None
    otherHandle: Optional[int] = None
    attachments: Optional[List[Dict]] = None
    subject: Optional[str] = None
    error: Optional[int] = None
    dateCreated: Optional[int] = None
    dateRead: Optional[int] = None
    dateDelivered: Optional[int] = None
    isDelivered: Optional[bool] = None
    isFromMe: Optional[bool] = None
    hasDdResults: Optional[bool] = None
    isArchived: Optional[bool] = None
    itemType: Optional[int] = None
    groupTitle: Optional[str] = None
    groupActionType: Optional[int] = None
    balloonBundleId: Optional[str] = None
    associatedMessageGuid: Optional[str] = None
    associatedMessageType: Optional[int] = None
    expressiveSendStyleId: Optional[str] = None
    threadOriginatorGuid: Optional[str] = None
    hasPayloadData: Optional[bool] = None
    chats: Optional[List[Chats]] = None
    messageSummaryInfo: Optional[Dict] = None
    payloadData: Optional[Dict] = None
    dateEdited: Optional[int] = None
    dateRetracted: Optional[int] = None
    partCount: Optional[int] = None


class BluebubblesData(BaseModel):
    type: Optional[str] = None
    data: Optional[Data] = None
