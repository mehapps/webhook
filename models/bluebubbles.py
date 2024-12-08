from pydantic import BaseModel

class Handle(BaseModel):
    originalROWID: int | None = None
    address: str | None = None
    service: str | None = None
    uncanonicalizedId: str | None = None
    country: str | None = None

class Chats(BaseModel):
    originalROWID: int | None = None
    guid: str | None = None
    style: int | None = None
    chatIdentifier: str | None = None
    isArchived: bool | None = None
    displayName: str | None = None

class Data(BaseModel):
    guid: str | None = None
    text: str | None = None
    dateCreated: int | None = None
    dateEdited: int | None = None
    isFromMe: bool | None = None
    handle: Handle | None = None
    originalROWID: int | None = None
    attributedBody: str | None = None
    handleId: int | None = None
    otherHandle: int | None = None
    attachments: list | None = None
    subject: str | None = None
    error: int | None = None
    dateRead: int | None = None
    dateDelivered: int | None = None
    isDelivered: bool | None = None
    hasDdResults: bool | None = None
    isArchived: bool | None = None
    itemType: int | None = None
    groupTitle: str | None = None
    groupActionType: int | None = None
    balloonBundleId: str | None = None
    associatedMessageGuid: str | None = None
    associatedMessageType: int | None = None
    expressiveSendStyleId: str | None = None
    threadOriginatorGuid: str | None = None
    hasPayloadData: bool | None = None
    chats: list[Chats] | None = None
    messageSummaryInfo: dict | None = None
    payloadData: dict | None = None
    dateRetracted: int | None = None
    partCount: int | None = None

class BluebubblesData(BaseModel):
    type: str | None = None
    data: Data | None = None