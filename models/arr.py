from pydantic import BaseModel

class SonarrData(BaseModel):
    class Config:
        extra = 'allow'
    
class Media(BaseModel):
    media_type: str
    tmbdId: str | None = None
    tvdb: str | None = None
    status: str
    status4k: str
    
class Request(BaseModel):
    request_id: str
    requestedBy_email: str | None = None
    requestedBy_username: str | None = None
    requestedBy_avatar: str | None = None
    requestedBy_settings_discordId: str | None = None
    requestedBy_settings_telegramChatId: str | None = None
    
class JellyseerrData(BaseModel):
    notification_type: str
    event: str
    subject: str
    message: str
    media: Media | None = None
    request: Request | None = None
    issue: dict | None = None
    comment: dict | None = None
        
class ProwlarrData(BaseModel):
    level: str
    message: str
    type: str
    wikiUrl: str
    eventType: str
    instanceName: str
    applicationUrl: str | None = None

class Image(BaseModel):
    coverType: str
    url: str
    remoteUrl: str

class MediaInfo(BaseModel):
    audioChannels: float | None = None
    audioCodec: str | None = None
    audioLanguages: list[str] | None = None
    height: int | None = None
    width: int | None = None
    subtitles: list[str] | None = None
    videoCodec: str | None = None
    videoDynamicRange: str | None = None
    videoDynamicRangeType: str | None = None

class MovieFile(BaseModel):
    id: int
    relativePath: str
    path: str
    quality: str
    qualityVersion: int
    releaseGroup: str
    sceneName: str
    indexerFlags: str | None = None
    size: int
    dateAdded: str
    mediaInfo: MediaInfo
    sourcePath: str

class Movie(BaseModel):
    id: int
    title: str
    year: int
    releaseDate: str | None = None
    folderPath: str
    tmdbId: int
    imdbId: str | None = None
    overview: str
    genres: list[str]
    images: list[Image]
    tags: list[str]

class RemoteMovie(BaseModel):
    tmdbId: int
    imdbId: str | None = None
    title: str
    year: int

class Release(BaseModel):
    releaseTitle: str
    indexer: str
    size: int
    quality: str | None = None

class CustomFormatInfo(BaseModel):
    customFormats: list[str]
    customFormatScore: int

class RadarrData(BaseModel):
    eventType: str
    movie: Movie
    remoteMovie: RemoteMovie
    release: Release
    movieFile: MovieFile
    isUpgrade: bool
    downloadClient: str
    downloadClientType: str
    downloadId: str
    customFormatInfo: CustomFormatInfo
    instanceName: str
    applicationUrl: str | None = None