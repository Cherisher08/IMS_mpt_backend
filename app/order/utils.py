from fastapi import HTTPException
from app.order.schema import PatchOperation


def apply_patch_operation(doc: dict, operation: PatchOperation):
    path_parts = [p for p in operation.path.strip("/").split("/") if p]

    def traverse(target, parts):
        """Navigate to the parent of the last key."""
        for i, part in enumerate(parts[:-1]):
            if isinstance(target, list):
                part = int(part)
            target = target[part]
        return target, parts[-1]

    try:
        parent, final_key = traverse(doc, path_parts)

        # Convert to int if the parent is a list
        if isinstance(parent, list):
            final_key = int(final_key)

            # Handle add operation
        if operation.op == "add":
            # Case: Adding to a list directly
            if isinstance(parent, list):
                if isinstance(final_key, int) and final_key <= len(parent):
                    parent.insert(final_key, operation.value)
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid index '{final_key}' for list at path '{operation.path}'",
                    )

            # Case: Appending to list if path is e.g., /list and list exists
            elif isinstance(parent.get(final_key), list):
                parent[final_key].append(operation.value)

            # Case: Normal add to dict
            else:
                parent[final_key] = operation.value

        if operation.op == "replace":
            parent[final_key] = operation.value

        elif operation.op == "remove":
            if isinstance(parent, list):
                parent.pop(final_key)
            else:
                parent.pop(final_key, None)

    except (KeyError, IndexError, ValueError, TypeError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error applying patch at path '{operation.path}': {str(e)}",
        )
