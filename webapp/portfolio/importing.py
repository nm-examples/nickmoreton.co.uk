import hashlib
import io

import requests
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from PIL import Image as PillowImage
from wagtail.images import get_image_model

from .models import PortfolioProject, PortfolioSourceRecord
from .source import RAW_ROOT, TIMEOUT, SourceError


def download_image(record):
    url = record.data["image_url"]
    if not url.startswith(f"{RAW_ROOT}/{record.commit_sha}/"):
        raise SourceError("The screenshot URL does not belong to the source snapshot.")
    try:
        with requests.get(
            url, timeout=TIMEOUT, stream=True, allow_redirects=False
        ) as response:
            response.raise_for_status()
            if response.status_code != 200:
                raise SourceError("The source screenshot could not be downloaded.")
            content = bytearray()
            for chunk in response.iter_content(64 * 1024):
                content.extend(chunk)
                if len(content) > 8 * 1024 * 1024:
                    raise SourceError("The source screenshot exceeds 8 MB.")
        image_bytes = bytes(content)
        with PillowImage.open(io.BytesIO(image_bytes)) as image:
            if image.format != "WEBP":
                raise SourceError("The source screenshot must be a WebP image.")
            image.verify()
        return image_bytes
    except (
        requests.RequestException,
        OSError,
        PillowImage.DecompressionBombError,
    ) as error:
        raise SourceError(
            "Could not import the source screenshot. No snippet was changed."
        ) from error


def save_import(record_id, data, user):
    # Fetch before opening the transaction, then reject any intervening changes.
    record = PortfolioSourceRecord.objects.get(pk=record_id)
    if record.missing_upstream or record.fingerprint != data["source_fingerprint"]:
        raise SourceError(
            "The source changed during review. Reload and review it again."
        )
    image_bytes = download_image(record) if data["import_image"] else None
    saved_file = None
    try:
        with transaction.atomic():
            record = PortfolioSourceRecord.objects.select_for_update().get(pk=record_id)
            if (
                record.missing_upstream
                or record.fingerprint != data["source_fingerprint"]
            ):
                raise SourceError(
                    "The source changed during review. Reload and review it again."
                )
            if record.project_id:
                project = PortfolioProject.objects.select_for_update().get(
                    pk=record.project_id
                )
                if str(project.latest_revision_id or "") != data["project_revision"]:
                    raise SourceError(
                        "The project changed during review. Reload and review it again."
                    )
                project = project.get_latest_revision_as_object()
            else:
                if data["project_revision"]:
                    raise SourceError(
                        "The linked project changed. Reload and review it again."
                    )
                project = PortfolioProject(live=False)
            for field in data["apply_fields"]:
                setattr(project, field, data[field])
            if image_bytes is not None:
                image_model = get_image_model()
                image = image_model.objects.filter(
                    file_hash=hashlib.sha1(image_bytes).hexdigest()
                ).first()
                if image is None:
                    image = image_model(
                        title=project.title or record.title,
                        file_hash=hashlib.sha1(image_bytes).hexdigest(),
                        file=ContentFile(
                            image_bytes,
                            name=record.data["image_url"].rsplit("/", 1)[-1],
                        ),
                        uploaded_by_user=user,
                    )
                    image.full_clean()
                    image.save()
                    saved_file = (image.file.storage, image.file.name)
                project.image = image
            project.full_clean()
            if not project.pk:
                project.save()
            project.save_revision(user=user, log_action=True)
            record.project = project
            record.last_applied_data = record.data
            record.last_applied_fingerprint = record.fingerprint
            record.applied_at = timezone.now()
            record.save(
                update_fields=[
                    "project",
                    "last_applied_data",
                    "last_applied_fingerprint",
                    "applied_at",
                ]
            )
        return project
    except Exception:
        # File storage does not participate in database rollbacks.
        if saved_file:
            storage, name = saved_file
            storage.delete(name)
        raise
