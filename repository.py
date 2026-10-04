"""
repository.py
--------------
Generic JSON-file-backed repository implementing simple CRUD operations.
This is the same proven Repository-pattern design used across the other
internship projects, adapted for the Expense & Budget Tracker.

Why JSON instead of a real database?
  - The brief calls for CSV/JSON based storage (no SQL requirement).
  - JSON preserves native Python types (lists, dicts, nested ints/floats)
    without the type-coercion headaches of CSV.
  - A single generic class means Expense and Budget storage share one
    well-tested implementation instead of duplicating file I/O logic.
"""

import json
import os
import threading


class RecordNotFoundError(Exception):
    """Raised when a record lookup/update/delete targets a missing id."""
    pass


class JSONRepository:
    """A tiny generic repository that persists a list of dict records
    to a JSON file on disk, keyed by an auto-incrementing integer id.
    """

    def __init__(self, filepath: str, id_field: str = "id"):
        self.filepath = filepath
        self.id_field = id_field
        self._lock = threading.Lock()
        self._ensure_file_exists()

    # ------------------------------------------------------------------
    # low level file helpers
    # ------------------------------------------------------------------
    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _read(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return []
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write(self, records):
        tmp_path = self.filepath + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, self.filepath)

    # ------------------------------------------------------------------
    # public CRUD api
    # ------------------------------------------------------------------
    def all(self):
        return self._read()

    def get(self, record_id):
        for rec in self._read():
            if rec.get(self.id_field) == record_id:
                return rec
        return None

    def get_or_raise(self, record_id):
        rec = self.get(record_id)
        if rec is None:
            raise RecordNotFoundError(f"Record {record_id} not found")
        return rec

    def _next_id(self, records):
        if not records:
            return 1
        return max(rec.get(self.id_field, 0) for rec in records) + 1

    def add(self, data: dict):
        with self._lock:
            records = self._read()
            new_id = self._next_id(records)
            data = dict(data)
            data[self.id_field] = new_id
            records.append(data)
            self._write(records)
            return data

    def update(self, record_id, updates: dict):
        with self._lock:
            records = self._read()
            for idx, rec in enumerate(records):
                if rec.get(self.id_field) == record_id:
                    merged = dict(rec)
                    merged.update(updates)
                    merged[self.id_field] = record_id
                    records[idx] = merged
                    self._write(records)
                    return merged
            raise RecordNotFoundError(f"Record {record_id} not found")

    def delete(self, record_id):
        with self._lock:
            records = self._read()
            new_records = [r for r in records if r.get(self.id_field) != record_id]
            if len(new_records) == len(records):
                raise RecordNotFoundError(f"Record {record_id} not found")
            self._write(new_records)
            return True

    def search(self, predicate):
        """predicate: a function(record) -> bool"""
        return [r for r in self._read() if predicate(r)]

    def count(self):
        return len(self._read())
