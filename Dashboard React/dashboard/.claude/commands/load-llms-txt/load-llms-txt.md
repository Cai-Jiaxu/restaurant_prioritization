---
description: Load llms.txt file from a remote URL
---

# How to load a remote context file

READ the llms.txt file for the URL provided in $ARGUMENTS via `curl`. Do nothing else and await further instructions.

Ensure the `curl` calls an actual URL if the provided argument is e.g. just a domain, call `curl` with:

```bash
curl -s https://$ARGUMENTS/llms.txt
```
