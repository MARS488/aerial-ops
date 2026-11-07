# Dependencies

| Piece | Required | Source |
| --- | --- | --- |
| Python | 3.9+ | Already installed on the computer. VM run used 3.12.3. |
| `sqlite3`, `http.server`, `json`, `hashlib`, `hmac`, `pathlib` | yes | Python standard library |
| Third-party Python packages | no | `requirements.txt` is empty on purpose |
| Node, containers, database server | no | Not used |
| Chrome or Chromium | no | The shell scenario does not start a browser. |
| Network during a normal run | loopback only | No package download and no API account |

Do not run `pip install`. Do not add a CDN script to the pages.
