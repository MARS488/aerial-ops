# Dependencies

| Piece | Required | Source |
| --- | --- | --- |
| Python | 3.9+ | Already installed on the computer. VM run used 3.12.3. |
| `sqlite3`, `http.server`, `json`, `hashlib`, `hmac`, `pathlib` | yes | Python standard library |
| Third-party Python packages | no | `requirements.txt` is empty on purpose |
| Node, containers, database server | no | Not used |
| Chrome or Chromium | only for screenshots | `tests/browser_capture.py`. The scenario's API stages do not need it. The VM had `google-chrome`. |
| Network during a normal run | loopback only | No package download and no API account |

Do not run `pip install`. Do not add a CDN script to the pages.
