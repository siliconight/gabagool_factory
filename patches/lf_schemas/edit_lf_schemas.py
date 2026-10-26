"""Level Factory 0.252.0 on a clone: the authoring loop's records as data schemas, checked by every reader and writer
(the factory's roadmap 310-317's records; `docs/AUTHORING_LOOP.md`). Anchored; refuses on a miss.

    python edit_lf_schemas.py <clone>

Copies schemas/authoring/*.schema.json (eight), packages/service/schemas.py, tests/service/test_schemas.py and its
real records (tests/service/fixtures/authoring/, eight) from `src/`. The worker checks the request it reads and every event and result it writes; the design is checked when read
and written, a template when loaded; the build, walk and export records before they reach disk.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
NEW = sorted(str(p.relative_to(HERE / "src")).replace("\\", "/") for p in (HERE / "src").rglob("*") if p.is_file())
assert len(NEW) == 18, NEW          # 8 schemas, the check, its test, 8 real records
for rel in NEW:
    dst = C / rel
    assert not dst.exists(), rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / "src" / rel, dst)
    print("wrote", rel)


def edit(rel, edits):
    p = C / rel
    t = p.read_bytes().decode("utf-8")
    assert "\r\n" not in t
    for old, new in edits:
        assert t.count(old) == 1, (rel, t.count(old), old[:80])
        t = t.replace(old, new)
    p.write_bytes(t.encode("utf-8"))
    print("edited", rel, len(edits))


edit("packages/service/worker.py", [
    ('''from pathlib import Path

REQUEST_SCHEMA''', '''from pathlib import Path

from packages.service import schemas

REQUEST_SCHEMA'''),
    ('''REQUEST_KEYS = {"schema", "request_id", "operation", "arguments", "design_revision"}
''', '''#: The request's fields, read off its schema (schemas/authoring/gabagool.service.request.v1.schema.json).
REQUEST_KEYS = set(schemas.load(REQUEST_SCHEMA)["properties"])
'''),
    ('''    def emit(self, stage: str, status: str, message: str = "", progress: float | None = None,
             **extra) -> None:
        self.seq += 1
        event = {"schema": EVENT_SCHEMA, "request_id": self.request_id, "operation": self.operation,
                 "seq": self.seq, "time": _now(), "stage": stage, "status": status, "message": message}
        if progress is not None:
            event["progress"] = max(0.0, min(1.0, float(progress)))
        event.update(extra)
''', '''    def emit(self, stage: str, status: str, message: str = "", progress: float | None = None) -> None:
        self.seq += 1
        event = {"schema": EVENT_SCHEMA, "request_id": self.request_id, "operation": self.operation,
                 "seq": self.seq, "time": _now(), "stage": stage, "status": status, "message": message}
        if progress is not None:
            event["progress"] = max(0.0, min(1.0, float(progress)))
        schemas.require(event, EVENT_SCHEMA)        # an event the panel could not read is never written
'''),
    ('''    """Write ``result.json`` atomically: the whole file or none of it."""
    path = run_dir / "result.json"
''', '''    """Write ``result.json`` atomically: the whole file or none of it. A result that is not a valid
    ``gabagool.service.result.v1`` raises `schemas.SchemaError` and is not written."""
    schemas.require(result, RESULT_SCHEMA)
    path = run_dir / "result.json"
'''),
    ('''    unknown = sorted(set(req) - REQUEST_KEYS)
    if unknown:
        raise RequestError("request_unknown_keys", "unknown keys: %s" % ", ".join(unknown))
    if not isinstance(req.get("request_id"), str) or not req["request_id"]:
        raise RequestError("request_malformed", "request_id must be a non-empty string")
    if not isinstance(req.get("operation"), str) or not req["operation"]:
        raise RequestError("request_malformed", "operation must be a non-empty string")
    args = req.get("arguments", {})
    if not isinstance(args, dict):
        raise RequestError("request_malformed", "arguments must be an object")
    rev = req.get("design_revision")
    if rev is not None and (isinstance(rev, bool) or not isinstance(rev, int) or rev < 0):
        raise RequestError("request_malformed", "design_revision must be a non-negative integer")
    req["arguments"] = args
    return req
''', '''    unknown = sorted(set(req) - REQUEST_KEYS)
    if unknown:
        raise RequestError("request_unknown_keys", "unknown keys: %s" % ", ".join(unknown))
    # every other rule is the schema's (0.252.0): one statement of the request, read by the worker and the panel
    problems = schemas.check(req, REQUEST_SCHEMA)
    if problems:
        raise RequestError("request_malformed", "request.json is not a valid %s: %s"
                           % (REQUEST_SCHEMA, "; ".join(problems)))
    req["arguments"] = req.get("arguments", {})
    return req
'''),
    ('''    except Exception as exc:  # the result must say so, whatever broke
''', '''    except Exception as exc:  # the result must say so, whatever broke -- an answer the schema refuses included
'''),
])

edit("packages/service/design.py", [
    ('''from pathlib import Path

DESIGN_SCHEMA''', '''from pathlib import Path

from packages.service import schemas

DESIGN_SCHEMA'''),
    ('''        if t.get("schema") != TEMPLATE_SCHEMA:
            raise DesignError("template_unreadable", "%s is not a %s" % (p.name, TEMPLATE_SCHEMA))
''', '''        if t.get("schema") != TEMPLATE_SCHEMA:
            raise DesignError("template_unreadable", "%s is not a %s" % (p.name, TEMPLATE_SCHEMA))
        problems = schemas.check(t, TEMPLATE_SCHEMA)
        if problems or t["template_id"] != p.stem:
            raise DesignError("template_unreadable", "%s: %s" % (
                p.name, "; ".join(problems) or "template_id %r is not the file's name" % t["template_id"]))
'''),
    ('''    unknown = sorted(set(doc) - DESIGN_KEYS)
    rev = doc.get("revision")
    if isinstance(rev, bool) or not isinstance(rev, int) or rev < 1:
        problems.append("revision must be a whole number of at least 1")
    try:
''', '''    unknown = sorted(set(doc) - DESIGN_KEYS)
    # the document's shape is the schema's (0.252.0); the values under choices and intent are the catalog's, below
    problems += schemas.check(doc, DESIGN_SCHEMA)
    try:
'''),
    ('''    for part in ("choices", "intent"):
        if not isinstance(doc.get(part), dict):
            problems.append("%s must be an object" % part)
            continue
''', '''    for part in ("choices", "intent"):
        if not isinstance(doc.get(part), dict):
            continue                                 # the schema has said so
'''),
    ('''            except DesignError as exc:
                problems.append(str(exc))
    if not isinstance(doc.get("name"), str) or not doc["name"].strip():
        problems.append("a level needs a name")
    return problems, unknown
''', '''            except DesignError as exc:
                problems.append(str(exc))
    return problems, unknown
'''),
    ('''    """Save ``doc`` as ``folder/design.json``, atomically: the whole file or the previous one."""
    folder.mkdir(parents=True, exist_ok=True)
''', '''    """Save ``doc`` as ``folder/design.json``, atomically: the whole file or the previous one. A document that is
    not a valid ``gabagool.design.v1`` raises `schemas.SchemaError` and nothing is written."""
    schemas.require(doc, DESIGN_SCHEMA)
    folder.mkdir(parents=True, exist_ok=True)
'''),
])

edit("packages/service/layouts.py", [
    ('''    record = _write_json(folder / "builds" / ("revision_%d.json" % doc["revision"]),
                         {"schema": "gabagool.build_record.v1", "design_id": doc["design_id"],
''', '''    from packages.service import schemas
    record = _write_json(folder / "builds" / ("revision_%d.json" % doc["revision"]), schemas.require(
                         {"schema": "gabagool.build_record.v1", "design_id": doc["design_id"],
'''),
    ('''                          "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())})
    events.emit("layouts", "ok"''', '''                          "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())},
                         "gabagool.build_record.v1"))
    events.emit("layouts", "ok"'''),
])

edit("packages/service/walking.py", [
    ('''from packages.service import layouts
''', '''from packages.service import layouts, schemas
'''),
    ('''    layouts._write_json(folder / "builds" / ("revision_%d.walk.json" % doc["revision"]),
                        dict(out, schema="gabagool.walk_record.v1", design_id=doc["design_id"],
                             recorded_at=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())))
''', '''    layouts._write_json(folder / "builds" / ("revision_%d.walk.json" % doc["revision"]), schemas.require(
                        dict(out, schema="gabagool.walk_record.v1", design_id=doc["design_id"],
                             recorded_at=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())),
                        "gabagool.walk_record.v1"))
'''),
])

edit("packages/service/exporting.py", [
    ('''from packages.service import layouts
''', '''from packages.service import layouts, schemas
'''),
    ('''                "exported_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())}
    staging = dest.with_name(".%s.partial" % dest.name)
''', '''                "exported_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())}
    schemas.require(manifest, "gabagool.snapshot.v1")          # before anything is copied
    staging = dest.with_name(".%s.partial" % dest.name)
'''),
    ('''    layouts._write_json(folder / "builds" / ("revision_%d.export.json" % doc["revision"]),
                        dict(manifest, snapshot=str(dest)))
''', '''    layouts._write_json(folder / "builds" / ("revision_%d.export.json" % doc["revision"]),
                        schemas.require(dict(manifest, snapshot=str(dest)), "gabagool.snapshot.v1"))
'''),
])
