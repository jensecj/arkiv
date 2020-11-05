import os
from urllib.parse import urlparse
import logging
import hashlib

import git
from git import Repo, Actor

from .modules.url2meta import gather_meta
from .modules.url2links import gather_links
from .modules.url2readable import generate_readable
from .modules.url2singlefile import generate_singlefile
from .modules.url2img import generate_screenshots
from .modules.url2archive import generate_archive
from .modules.url2warc import generate_warc

from .modules.links2repos import extract_repos
from .modules.links2videos import extract_videos
from .modules.links2images import extract_images
from .modules.links2pdfs import extract_pdfs


log = logging.getLogger(__name__)


def _build_archive_dir(url):
    link = urlparse(url)
    loc = link.netloc.strip("/")
    path = link.path.strip("/")

    archive_dir = f"{loc}--{path}"

    # replace common parts of the path
    archive_dir = (
        archive_dir.replace("www.", "")
        .replace(".html", "")
        .replace(".htm", "")
        .replace(".asp", "")
        .replace(".aspx", "")
        .replace(".php", "")
        .replace("/", "_")
    )

    # append fragment and query parts of the path
    if fragment := link.fragment:
        archive_dir = archive_dir + "#" + fragment
    if query := link.query:
        archive_dir = archive_dir + "?" + query

    # cap the length of the archives name
    archive_dir = archive_dir[:75]

    # add checksum, to ensure we dont overwrite archives from long urls
    hash = hashlib.md5(url.encode("utf-8")).hexdigest()[:4]
    archive_dir = f"{archive_dir}={hash}"

    return archive_dir


def _get_archive_repo(archive_path):
    try:
        repo = Repo(archive_path)
    except git.exc.InvalidGitRepositoryError:
        log.info("repo does not exist, creating...")
        repo = Repo.init(archive_path)

    # TODO: if dir is a git-repo, validate that it is a proper archive

    return repo


def _commit_archive(archive_path, repo):
    actor = Actor("Arkivist", "arkiv@arkiv.arkiv")

    if not repo.heads:  # archive has no commits yet
        repo.index.commit("created archive", author=actor, committer=actor)

    # add all archive changes to the index, not just checked in files
    repo.git.add(all=True)

    # NOTE: on prefixes: b is the `before' diff, a is `after'
    # even if the docs have it the other way around

    diff = repo.index.diff(repo.head.commit)
    changed_files = [d.a_path for d in diff]
    log.info("commiting: " + ", ".join(changed_files))

    for d in diff:
        if d.b_blob is None:  # new file
            log.debug(f"{d.a_path}: added")
        elif d.a_blob is None:  # deleted file
            log.debug(f"{d.b_path}: deleted")
        else:
            byte_diff = d.a_blob.size - d.b_blob.size
            diff_str = f"+{byte_diff}" if byte_diff >= 0 else f"{byte_diff}"
            log.debug(f"{d.b_path:<15}: {diff_str} bytes")

    repo.index.commit("update", author=actor, committer=actor)


def archive(config, url):
    log.info(f"archiving {url}")

    archive_dir = _build_archive_dir(url)
    log.debug(f"{archive_dir=}")

    if p := config.get("archive"):
        archive_path = os.path.join(os.path.expanduser(p), archive_dir)
    else:
        archive_path = os.path.abspath(archive_dir)

    log.debug(f"{archive_path=}")

    if not os.path.isdir(archive_path):
        os.mkdir(archive_path)

    repo = _get_archive_repo(archive_path)

    if repo.is_dirty(untracked_files=True):
        log.warning("git repo is dirty!")

    # we change the working dir, so relative outputs land in the correct location
    os.chdir(archive_path)

    # TODO: wrap each section in an error handler
    meta = gather_meta(url)
    links = gather_links(url)
    generate_readable(url)
    generate_screenshots(url)
    # generate_singlefile(url)

    if links:
        extract_pdfs(config, links)
        extract_images(links)
        extract_videos(links)
        extract_repos(links)

    # generate_warc(config, url)
    # generate_archive(config, url)

    _commit_archive(archive_path, repo)

    log.info("Archiving complete")
