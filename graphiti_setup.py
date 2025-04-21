# graphiti_setup.py
import os
import json
from datetime import datetime, timezone
from pathlib import Path
from pydantic import BaseModel
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode
from watchdog import observers
from watchdog.events import FileSystemEventHandler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileEntity(BaseModel):
    path: str
    name: str
    size: int
    modification_time: datetime
    parent: str

class DirectoryEntity(BaseModel):
    path: str
    name: str
    parent: str | None = None

async def setup_graphiti():
    try:
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        graphiti = Graphiti(
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password,
            openai_api_key=openai_api_key
        )
        await graphiti.initialize()
        logger.info("Graphiti initialized with Neo4j")
        return graphiti
    except Exception as e:
        logger.error(f"Failed to initialize Graphiti: {e}")
        raise

async def add_file_episode(graphiti: Graphiti, path: Path, parent: str):
    try:
        stat = path.stat()
        file_data = FileEntity(
            path=str(path),
            name=path.name,
            size=stat.st_size,
            modification_time=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            parent=parent
        )
        episode_body = json.dumps({"files": [file_data.dict()]})
        episode = RawEpisode(
            name=f"File_{path.name}",
            episode_body=episode_body,
            source=EpisodeType.json,
            source_description="file_metadata",
            reference_time=datetime.now(timezone.utc)
        )
        await graphiti.add_episode(episode)
        logger.info(f"Added episode for file: {path}")
    except Exception as e:
        logger.error(f"Error adding file episode {path}: {e}")

async def add_directory_episode(graphiti: Graphiti, path: Path, parent: str | None):
    try:
        dir_data = DirectoryEntity(
            path=str(path),
            name=path.name,
            parent=parent
        )
        episode_body = json.dumps({"directories": [dir_data.dict()]})
        episode = RawEpisode(
            name=f"Dir_{path.name}",
            episode_body=episode_body,
            source=EpisodeType.json,
            source_description="directory_metadata",
            reference_time=datetime.now(timezone.utc)
        )
        await graphiti.add_episode(episode)
        logger.info(f"Added episode for directory: {path}")
    except Exception as e:
        logger.error(f"Error adding directory episode {path}: {e}")

async def scan_initial_files(graphiti: Graphiti):
    allowed_paths = [Path(p) for p in os.getenv("ALLOWED_PATHS", "").split(",") if p]
    for base_path in allowed_paths:
        try:
            for path in base_path.rglob("*"):
                parent = str(path.parent)
                if path.is_file():
                    await add_file_episode(graphiti, path, parent)
                elif path.is_dir():
                    await add_directory_episode(graphiti, path, parent)
        except Exception as e:
            logger.error(f"Error scanning path {base_path}: {e}")

class FileSystemWatcher(FileSystemEventHandler):
    def __init__(self, graphiti: Graphiti):
        self.graphiti = graphiti

    async def add_or_update(self, path: str, is_dir: bool):
        path_obj = Path(path)
        parent = str(path_obj.parent)
        if is_dir:
            await add_directory_episode(self.graphiti, path_obj, parent)
        else:
            await add_file_episode(self.graphiti, path_obj, parent)

    async def delete(self, path: str):
        try:
            # Mark as deleted by updating episode with end time
            episode_body = json.dumps({"path": path, "deleted": True})
            episode = RawEpisode(
                name=f"Delete_{Path(path).name}",
                episode_body=episode_body,
                source=EpisodeType.json,
                source_description="deletion",
                reference_time=datetime.now(timezone.utc)
            )
            await self.graphiti.add_episode(episode)
            logger.info(f"Marked as deleted: {path}")
        except Exception as e:
            logger.error(f"Error marking deletion {path}: {e}")

    def on_created(self, event):
        if not any(Path(event.src_path).is_relative_to(p) for p in allowed_paths):
            return
        asyncio.run(self.add_or_update(event.src_path, event.is_directory))

    def on_modified(self, event):
        if not any(Path(event.src_path).is_relative_to(p) for p in allowed_paths):
            return
        if not event.is_directory:
            asyncio.run(self.add_or_update(event.src_path, False))

    def on_deleted(self, event):
        if not any(Path(event.src_path).is_relative_to(p) for p in allowed_paths):
            return
        asyncio.run(self.delete(event.src_path))

def start_watcher(graphiti: Graphiti):
    observer = Observer()
    watcher = FileSystemWatcher(graphiti)
    allowed_paths = [Path(p) for p in os.getenv("ALLOWED_PATHS", "").split(",") if p]
    for path in allowed_paths:
        observer.schedule(watcher, str(path), recursive=True)
    observer.start()
    logger.info("File system watcher started")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()