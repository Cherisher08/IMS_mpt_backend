from typing import Any, Dict, Optional
from datetime import datetime


class SortBuilder:
    """
    Build MongoDB sort queries from query parameters.
    Supports: asc (ascending) and desc (descending)
    """

    @staticmethod
    def parse_sort_param(sort_str: str) -> Optional[tuple]:
        """
        Parse sort string format: "field:direction" or "field" (defaults to asc)
        Examples:
            - "created_at:asc" -> ("created_at", 1)
            - "created_at:desc" -> ("created_at", -1)
            - "amount" -> ("amount", 1)
        
        Returns: (field_name, direction) tuple where direction is 1 (asc) or -1 (desc)
        """
        if not sort_str:
            return None

        parts = sort_str.split(":", 1)

        if len(parts) == 1:
            # Format: field (defaults to asc)
            field = parts[0].strip()
            direction = 1
        else:
            # Format: field:direction
            field, direction_str = parts
            field = field.strip()
            direction_str = direction_str.strip().lower()

            if direction_str in ["asc", "ascending", "1"]:
                direction = 1
            elif direction_str in ["desc", "descending", "-1"]:
                direction = -1
            else:
                return None

        if field == "":
            return None

        return (field, direction)

    @staticmethod
    def build_sort(sort_params: Optional[list] = None) -> Optional[list]:
        """
        Build MongoDB sort specification from list of sort parameters.
        Returns list of (field, direction) tuples.
        
        Example:
            sort_params = ["created_at:desc", "order_id:asc"]
            -> [("created_at", -1), ("order_id", 1)]
        """
        if not sort_params:
            return None

        sort_spec = []
        for sort_param in sort_params:
            parsed_sort = SortBuilder.parse_sort_param(sort_param)
            if parsed_sort:
                sort_spec.append(parsed_sort)

        return sort_spec if sort_spec else None


class FilterBuilder:
    """
    Build MongoDB filter queries from query parameters.
    Supports operators: eq, in, gte, lte, gt, lt, ne, regex, exists
    """

    SUPPORTED_OPERATORS = {
        "eq": lambda field, value: {field: value},
        "in": lambda field, value: {field: {"$in": value if isinstance(value, list) else [value]}},
        "gte": lambda field, value: {field: {"$gte": value}},
        "lte": lambda field, value: {field: {"$lte": value}},
        "gt": lambda field, value: {field: {"$gt": value}},
        "lt": lambda field, value: {field: {"$lt": value}},
        "ne": lambda field, value: {field: {"$ne": value}},
        "regex": lambda field, value: {field: {"$regex": value, "$options": "i"}},
        "exists": lambda field, value: {field: {"$exists": value.lower() in ["true", "1", "yes"]}},
    }

    @staticmethod
    def parse_filter_param(filter_str: str) -> Optional[Dict[str, Any]]:
        """
        Parse filter string format: "field:operator:value" or "field:value" (defaults to eq)
        Examples:
            - "status:pending" -> {"status": "pending"}
            - "status:in:pending,paid" -> {"status": {"$in": ["pending", "paid"]}}
            - "created_at:gte:2025-01-01" -> {"created_at": {"$gte": "2025-01-01"}}
            - "amount:lte:1000" -> {"amount": {"$lte": 1000}}
        """
        if not filter_str or ":" not in filter_str:
            return None

        parts = filter_str.split(":", 2)

        if len(parts) == 2:
            # Format: field:value (defaults to eq)
            field, value = parts
            operator = "eq"
        elif len(parts) == 3:
            # Format: field:operator:value
            field, operator, value = parts
        else:
            return None

        if operator not in FilterBuilder.SUPPORTED_OPERATORS:
            return None

        if field.strip() == "" or value.strip() == "":
            return None

        field = field.strip()
        value = value.strip()

        # Convert value types
        if operator in ["in"]:
            value = [v.strip() for v in value.split(",")]
        elif operator in ["gte", "lte", "gt", "lt"]:
            # Try to convert to number, otherwise keep as string
            try:
                value = float(value) if "." in value else int(value)
            except ValueError:
                # Try to parse as datetime
                try:
                    value = datetime.fromisoformat(value)
                except ValueError:
                    pass

        return FilterBuilder.SUPPORTED_OPERATORS[operator](field, value)

    @staticmethod
    def build_filters(filter_params: Optional[list] = None) -> Dict[str, Any]:
        """
        Build combined MongoDB filter query from list of filter parameters.
        Supports multiple filters (AND logic by default).
        Handles multiple conditions on same field (e.g., out_date:gte:... and out_date:lte:...)
        Special handling for filters starting with 'or:' which are combined with $or logic.
        
        Examples:
            - ["status:pending", "amount:gte:100"] -> AND logic
            - ["out_date:gte:2025-01-01,out_date:lte:2025-01-31"] -> merges into single field
            - ["or:balance_paid_date:gte:2025-01-01", "or:repay_date:gte:2025-01-01"] -> OR logic
            - ["or:balance_paid_date:gte:2025-01-01", "or:balance_paid_date:lte:2025-01-31"] -> combines same field
        """
        if not filter_params:
            return {}

        filters = {}
        or_filters = []
        
        for filter_param in filter_params:
            # Handle comma-separated multiple conditions on same field
            # e.g., "out_date:gte:2025-01-01,out_date:lte:2025-01-31" or "or:balance_paid_date:gte:...,or:balance_paid_date:lte:..."
            if "," in filter_param and ":" in filter_param:
                # Split by comma to get individual conditions
                conditions = filter_param.split(",")
                for condition in conditions:
                    # Check if condition should use OR logic
                    if condition.startswith("or:"):
                        parsed_filter = FilterBuilder.parse_filter_param(condition[3:])
                        if parsed_filter:
                            # Merge conditions for same field in or_filters
                            field = list(parsed_filter.keys())[0]
                            existing_idx = next((i for i, f in enumerate(or_filters) if field in f), None)
                            if existing_idx is not None:
                                # Merge with existing field filter
                                or_filters[existing_idx][field].update(parsed_filter[field])
                            else:
                                or_filters.append(parsed_filter)
                    else:
                        parsed_filter = FilterBuilder.parse_filter_param(condition)
                        if parsed_filter:
                            # Merge conditions for same field
                            for field, value in parsed_filter.items():
                                if field in filters:
                                    # If field already exists, merge the operators
                                    if isinstance(filters[field], dict) and isinstance(value, dict):
                                        filters[field].update(value)
                                    else:
                                        filters[field] = value
                                else:
                                    filters[field] = value
            else:
                # Check if filter should use OR logic
                if filter_param.startswith("or:"):
                    parsed_filter = FilterBuilder.parse_filter_param(filter_param[3:])
                    if parsed_filter:
                        # Merge conditions for same field in or_filters
                        field = list(parsed_filter.keys())[0]
                        existing_idx = next((i for i, f in enumerate(or_filters) if field in f), None)
                        if existing_idx is not None:
                            # Merge with existing field filter
                            or_filters[existing_idx][field].update(parsed_filter[field])
                        else:
                            or_filters.append(parsed_filter)
                else:
                    parsed_filter = FilterBuilder.parse_filter_param(filter_param)
                    if parsed_filter:
                        filters.update(parsed_filter)
        
        # If there are OR filters, add them to the query
        if or_filters:
            filters["$or"] = or_filters

        return filters


class PaginationParams:
    """Handle pagination parameters. limit=0 means retrieve all documents."""

    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = max(0, skip)  # Ensure skip is not negative
        # limit=0 means unlimited, otherwise limit between 1 and 1000
        self.limit = limit if limit == 0 else max(1, min(limit, 1000))

    def get_skip_limit(self) -> tuple:
        """Return skip and limit values."""
        return self.skip, self.limit

    def to_dict(self) -> Dict[str, int]:
        """Return as dictionary."""
        return {"skip": self.skip, "limit": self.limit}
