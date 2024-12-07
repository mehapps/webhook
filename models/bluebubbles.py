from pydantic import BaseModel

class Handle(BaseModel):
    originalROWID: int
    address: str
    service: str
    uncanonicalizedId: str
    country: str

class Chats(BaseModel):
    originalROWID: int
    guid: str
    style: int
    chatIdentifier: str
    isArchived: bool
    displayName: str | None = None

class Data(BaseModel):
    guid: str
    text: str | None = None
    dateCreated: int | None = None
    dateEdited: int | None = None
    isFromMe: bool
    handle: Handle
    originalROWID: int
    attributedBody: str | None = None
    handleId: int
    otherHandle: int
    attachments: list | None = None
    subject: str | None = None
    error: int
    dateRead: int | None = None
    dateDelivered: int | None = None
    isDelivered: bool
    hasDdResults: bool
    isArchived: bool
    itemType: int
    groupTitle: str | None = None
    groupActionType: int
    balloonBundleId: str | None = None
    associatedMessageGuid: str | None = None
    associatedMessageType: int | None = None
    expressiveSendStyleId: str | None = None
    threadOriginatorGuid: str | None = None
    hasPayloadData: bool
    chats: list[Chats] | None = None
    messageSummaryInfo: dict | None = None
    payloadData: dict | None = None
    dateRetracted: int | None = None
    partCount: int
