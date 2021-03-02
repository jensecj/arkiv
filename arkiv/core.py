import os
import json
from urllib.parse import urlparse
import logging
import hashlib
import concurrent.futures

import git
from git import Repo, Actor

from .config import CONFIG
from . import extractors
from .extractors import meta, links, wayback, video
from . import generators
from .generators import readable, monolith, screenshots, tar, warc, pdfs, arxiv
from .utils import profile

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
        .replace(".gmi", "")
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
        return Repo(archive_path)
    except git.exc.InvalidGitRepositoryError:
        pass


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

    repo.index.commit("", author=actor, committer=actor)


def parallelize(tasks):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for fn, args in tasks:
            futures.append(executor.submit(fn, *args))

        results = []
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

        return results


@profile
def archive(url):
    log.info(f"archiving {url}")

    archive_dir = _build_archive_dir(url)
    log.debug(f"{archive_dir=}")

    if p := CONFIG.get("archive"):
        archive_path = os.path.join(os.path.expanduser(p), archive_dir)
    else:
        archive_path = os.path.abspath(archive_dir)

    log.debug(f"{archive_path=}")

    if not os.path.isdir(archive_path):
        os.mkdir(archive_path)

    # change the working dir, so relative outputs land in the correct location
    os.chdir(archive_path)

    if repo := _get_archive_repo(archive_path):
        if repo.is_dirty(untracked_files=True):
            log.warning("archive repository is dirty")

    results = parallelize(
        [
            (extractors.meta.extract, [url]),
            (extractors.wayback.extract, [url]),
            (extractors.video.extract, [url]),
            (extractors.links.extract, [url]),
        ]
    )

    data = {}

    # TODO: rework parsing parallel extraction results
    for r in results:
        if isinstance(r, dict):
            for k, v in r.items():
                e = data.get(k) or {}
                e.update(v)
                data[k] = e

    meta = data.get("meta") or {}
    links = data.get("links") or {}

    if CONFIG.get("json"):
        print(json.dumps(data, indent=4, sort_keys=True))

    should_generate = not CONFIG.get("dry-run") and not CONFIG.get("json")

    if should_generate:
        with open("meta.json", "w") as f:
            json.dump(meta, f, indent=4, sort_keys=True)

        with open("links.json", "w") as f:
            json.dump(links, f, indent=4, sort_keys=True)

        parallelize(
            [
                (generators.readable.generate, [url]),
                (generators.monolith.generate, [url]),
                (generators.screenshots.generate, [url]),
                (generators.tar.generate, [url]),
                (generators.warc.generate, [url]),
                (generators.pdfs.generate, [links]),
                (generators.arxiv.generate, [links]),
            ]
        )

        if not repo:
            log.info("repo does not exist, creating...")
            repo = Repo.init(archive_path)

        _commit_archive(archive_path, repo)

    log.info("Archiving complete")
