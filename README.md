# steam-library

A GitHub Action exports my Steam library once a day to `library.json`. A daily Claude scheduled task copies it into the Steam DLC Watch page, and the twice-monthly DLC check uses it.

- `scripts/export_library.py` calls `IPlayerService/GetOwnedGames` and keeps every game played for more than an hour, plus library totals.
- The Steam Web API key lives in the `STEAM_API_KEY` Actions secret. It is never written to the repo.
- Run it by hand from the Actions tab with "Run workflow".
- cron-job.org triggers the workflow once a day through the GitHub API (`workflow_dispatch`). The workflow has no schedule of its own.
