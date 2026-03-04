# Project Story JSON Import Schema

Use this schema when importing stories into a project.

Each story is created as a `Story` and attached to either a `ProjectCapitalIn` or `ProjectCapitalOut` relationship based on:

- `capital_direction`: `"in"` or `"out"`
- `capital_title`: exact capital title match (case-insensitive)

## JSON shape

```json
{
  "schema_version": 1,
  "dry_run": false,
  "upsert_by_title": true,
  "create_missing_project_capital_links": false,
  "capital_title_reference": {
    "for_capital_direction_in_use_exactly": ["Financial Capital", "Natural Capital"],
    "for_capital_direction_out_use_exactly": ["Financial Capital", "Natural Capital"],
    "all_available_capitals_in_system": ["Financial Capital", "Material Capital", "Natural Capital"]
  },
  "import_guidance": {
    "capital_title_matching": "Use exact titles from capital_title_reference. Matching is case-insensitive and whitespace-normalized.",
    "story_deduplication": "With upsert_by_title=true, importer updates existing story for same project capital + direction + title instead of creating duplicate.",
    "capital_direction_rules": {
      "in": "Story attaches to Project Capital In relationship for that capital title.",
      "out": "Story attaches to Project Capital Out relationship for that capital title."
    }
  },
  "default_visibility": {
    "view_members": true,
    "view_public": false
  },
  "stories": [
    {
      "title": "Learning to regenerate soil fertility",
      "text_content": "Narrative content for this project capital story.",
      "capital_direction": "in",
      "capital_title": "Natural Capital",
      "attachment_context": "regeneration_example",
      "youtube_url": "",
      "view_members": true,
      "view_public": false
    },
    {
      "title": "Training loop outputs stronger facilitation",
      "text_content": "What this project produces as social capacity.",
      "capital_direction": "out",
      "capital_title": "Social Capital",
      "attachment_context": "capacity_output"
    }
  ]
}
```

## Required fields

Per story object:

- `title` (string)
- `text_content` (string)
- `capital_direction` (`"in"` or `"out"`)
- `capital_title` (string)

Top-level:

- `stories` (non-empty array)

## Optional fields

Top-level:

- `schema_version` (number; currently `1`)
- `dry_run` (boolean; default `false`; validates and reports without creating data)
- `upsert_by_title` (boolean; default `true`; updates matching stories instead of duplicating)
- `create_missing_project_capital_links` (boolean; default `false`)
- `capital_title_reference` (object; provided by the project detail UI schema output)
- `import_guidance` (object; provided by the project detail UI schema output)
- `default_visibility.view_members` (boolean; default `true`)
- `default_visibility.view_public` (boolean; default `false`)

Per story:

- `attachment_context` (string)
- `youtube_url` (string URL)
- `view_members` (boolean; falls back to `default_visibility.view_members`)
- `view_public` (boolean; falls back to `default_visibility.view_public`)

## Behavior notes

- Import is all-or-nothing (transactional). If one story fails, none are created.
- Dry run can be enabled by JSON (`dry_run: true`) or by the UI preview checkbox.
- With `upsert_by_title=true`, duplicates are prevented per `(capital_direction, capital_title, story.title)` and matching existing stories are updated.
- If `create_missing_project_capital_links` is `false`, the project must already be linked to each capital in the specified direction.
- If `create_missing_project_capital_links` is `true`, missing project-capital links are auto-created if the capital already exists in the Capitals table.
- Capital matching is case-insensitive and whitespace-normalized by title.

## AI packaging rule of thumb

- Pick `capital_direction` first (`in` or `out`).
- Choose `capital_title` from the matching direction list in `capital_title_reference`.
- Keep one story per intended direction/title pair when possible.
